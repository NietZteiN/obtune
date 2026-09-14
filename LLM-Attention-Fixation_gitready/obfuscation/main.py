from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from tqdm.auto import tqdm

# Local runtime imports.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import ModelRunner
from paths import model_dir_name, resolve_artifact_path, resolve_obf_result_root
from steering import SteeringConfig
from util import utity
from counterfactual_eval import (
    build_case_pack,
    build_counterfactual_instruction,
    parse_predicted_labels,
    resolve_task_profile,
    score_case_predictions,
)



def _load_skip_models(base_dir: Path) -> tuple[set[str], list[Path]]:
    skipped: set[str] = set()
    sources: list[Path] = []
    env_models = os.environ.get("OBF_SKIP_MODELS", "").strip()
    if env_models:
        skipped.update(x.strip() for x in env_models.split(",") if x.strip())
    candidate_paths: List[Path] = []
    env_file = os.environ.get("OBF_SKIP_MODELS_FILE", "").strip()
    if env_file:
        candidate_paths.append(resolve_artifact_path(base_dir, env_file))
    candidate_paths.append(base_dir / "logs" / "obf_skip_models.txt")
    for path in candidate_paths:
        if not path.is_file():
            continue
        sources.append(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            skipped.update(x.strip() for x in line.split(",") if x.strip())
    return skipped, sources


def _canonicalize_model_output(text: str) -> tuple[str, bool]:
    if not text:
        return "", False
    stripped = text.strip()
    fence_pattern = re.compile(r"```(\w+)?\s*\n?(.*?)\n?```", re.DOTALL)
    matches = list(fence_pattern.finditer(stripped))
    for m in reversed(matches):
        candidate = (m.group(2) or "").strip()
        if not candidate:
            continue
        lowered = candidate.lower()
        if "<your answer>" in lowered:
            continue
        if lowered.startswith("class ") or lowered.startswith("import "):
            continue
        return candidate, True
    if matches:
        tail = stripped[matches[-1].end():].strip()
        if tail:
            return tail, True
    return stripped, bool(stripped)


def _parse_gpu_ids(raw: Optional[str]) -> Optional[List[int]]:
    if not raw:
        return None
    parts = re.split(r"[+,]", raw.strip())
    out: List[int] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if not p.isdigit():
            raise ValueError(f"Invalid GPU id '{p}' in --gpu-ids={raw!r}.")
        out.append(int(p))
    return out or None


def _parse_techniques(raw: Optional[str]) -> Optional[set[str]]:
    if not raw:
        return None
    vals = {x.strip() for x in raw.split(",") if x.strip()}
    return vals or None


def _assign_config_fields(target: SteeringConfig, source: SteeringConfig) -> None:
    for key, value in vars(source).items():
        setattr(target, key, copy.deepcopy(value))


def _build_steering_config(args: argparse.Namespace) -> Optional[SteeringConfig]:
    enabled = [2] if bool(args.steer) else []
    if not enabled:
        return None

    head_mask_path = (
        resolve_artifact_path(PROJECT_ROOT, args.head_mask_path)
        if args.head_mask_path
        else None
    )
    return SteeringConfig(
        enabled_levels=enabled,
        prior=args.prior,
        n_bins=max(1, int(args.n_bins)),
        binning=args.binning,
        beta_bias=float(args.beta_bias),
        beta_post=float(args.beta_post),
        lambda_attn=float(args.lambda_attn),
        lambda_mlp=float(args.lambda_mlp),
        head_subset_mode=args.head_subset_mode,
        head_mask_path=head_mask_path,
        head_mask_apply_to=args.head_mask_apply_to,
        head_subset_topk_per_layer=max(1, int(args.head_subset_topk_per_layer)),
        head_subset_calib_runs=max(1, int(args.head_subset_calib_runs)),
        head_subset_calib_max_new_tokens=max(1, int(args.head_subset_calib_max_new_tokens)),
        head_subset_calib_first_decode_only=(args.head_subset_calib_first_decode_only == "on"),
    )


def _collect_variants(
    source_root: Path,
    *,
    snippet_filter: Optional[str],
    techniques_filter: Optional[set[str]],
) -> List[Tuple[str, str, Path]]:
    variants: List[Tuple[str, str, Path]] = []
    if not source_root.is_dir():
        raise FileNotFoundError(f"Prepared obfuscated corpus root missing: {source_root}")
    for snippet_dir in sorted(p for p in source_root.iterdir() if p.is_dir()):
        snippet = snippet_dir.name
        if snippet_filter and snippet != snippet_filter:
            continue
        for technique_dir in sorted(p for p in snippet_dir.iterdir() if p.is_dir()):
            technique = technique_dir.name
            if techniques_filter and technique not in techniques_filter:
                continue
            direct_java_files = sorted(
                p for p in technique_dir.glob("*.java")
                if p.is_file() and not p.name.endswith(".meta.json")
            )
            if direct_java_files:
                for variant in direct_java_files:
                    variants.append((snippet, technique, variant))
                continue
            for tier_dir in sorted(p for p in technique_dir.iterdir() if p.is_dir()):
                java_files = sorted(
                    p for p in tier_dir.glob("*.java")
                    if p.is_file() and not p.name.endswith(".meta.json")
                )
                for variant in java_files:
                    variants.append((snippet, technique, variant))
    return variants


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Output prediction runner on a prepared obfuscated Java corpus.")
    ap.add_argument(
        "--dataset",
        choices=["eyetracking", "humaneval", "cruxeval"],
        default="eyetracking",
        help="Dataset selector used for evaluation profile and output organization.",
    )
    ap.add_argument(
        "--source-root",
        type=str,
        required=True,
        help="Path to a prepared obfuscated corpus laid out as snippet/technique/*.java or snippet/technique/<tier>/*.java.",
    )
    ap.add_argument(
        "--task-profile",
        choices=["auto", "stdout", "counterfactual_tf"],
        default="auto",
        help=(
            "Evaluation profile selector. humaneval/cruxeval are hard-switched to counterfactual_tf; "
            "eyetracking defaults to stdout."
        ),
    )
    ap.add_argument("--cf-min-cases", type=int, default=8, help="Minimum number of counterfactual T/F cases.")
    ap.add_argument("--cf-target-cases", type=int, default=16, help="Target number of counterfactual T/F cases.")
    ap.add_argument(
        "--cf-cache-dir",
        type=str,
        default="logs/eval_casepacks",
        help="Cache directory for generated counterfactual case packs.",
    )
    ap.add_argument(
        "--cf-rebuild",
        choices=["on", "off"],
        default="off",
        help="When on, ignore case-pack cache and rebuild.",
    )
    ap.add_argument(
        "--cf-strict-json",
        choices=["on", "off"],
        default="on",
        help="When on, enforce JSON-first parsing for counterfactual predictions (regex fallback still attempted).",
    )
    ap.add_argument(
        "--result-layout",
        choices=["auto", "grouped", "flat"],
        default="auto",
        help=(
            "Output directory layout. auto=flat for counterfactual_tf and grouped for stdout; "
            "grouped=EM/Mismatch folders; flat=run_XXXX folders."
        ),
    )
    ap.add_argument("--validation-mode", choices=["auto", "stdout", "assertion_verdict"], default="auto", help=argparse.SUPPRESS)
    ap.add_argument("--code-snippet", type=str, default=None, help="Single snippet folder name to run.")
    ap.add_argument("--techniques", type=str, default=None, help="Comma-separated technique folder names.")
    ap.add_argument("--runs-per-snippet", type=int, default=20)
    ap.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum number of generated tokens per run (default: 512).",
    )
    ap.add_argument("--gpu-ids", type=str, default=None, help="GPU IDs like 0,1 or 0+1+2+3")
    ap.add_argument("--model-name", type=str, default=None, help="HF model name override.")
    ap.add_argument("--cache-dir", type=str, default=None, help="HF cache directory override.")
    ap.add_argument("--record-layers", choices=["on", "off"], default="on")
    ap.add_argument("--record-bdv", choices=["on", "off"], default=None, help=argparse.SUPPRESS)
    ap.add_argument("--record-bdv-buckets", type=str, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--run-tag", type=str, default=None)
    ap.add_argument("--auto-run-tag", action="store_true")
    ap.add_argument("--gpus", type=int, default=None, help="Max number of visible GPUs to use.")
    ap.add_argument(
        "--steer",
        action="store_true",
        help="Enable the default steering path used in the paper.",
    )
    ap.add_argument(
        "--prior",
        choices=["human", "ast", "lex", "rand", "uniform", "cfg", "slice", "slice_hybrid"],
        default="human",
    )
    ap.add_argument("--n-bins", type=int, default=12)
    ap.add_argument("--binning", choices=["equal_count"], default="equal_count")
    ap.add_argument("--beta-bias", type=float, default=0.0)
    ap.add_argument("--beta-post", type=float, default=0.0)
    ap.add_argument("--lambda-attn", type=float, default=1.0)
    ap.add_argument("--lambda-mlp", type=float, default=1.0)
    ap.add_argument(
        "--head-subset-mode",
        choices=["none", "file", "auto"],
        default="none",
    )
    ap.add_argument("--head-mask-path", type=str, default=None)
    ap.add_argument(
        "--head-mask-apply-to",
        choices=["l1", "l2", "both"],
        default="both",
    )
    ap.add_argument("--head-subset-topk-per-layer", type=int, default=4)
    ap.add_argument("--head-subset-calib-runs", type=int, default=3)
    ap.add_argument("--head-subset-calib-max-new-tokens", type=int, default=64)
    ap.add_argument(
        "--head-subset-calib-first-decode-only",
        choices=["on", "off"],
        default="on",
    )
    ap.add_argument(
        "--steer-last-n-layers",
        type=int,
        default=None,
        help="Override the steering layer band to the last N transformer layers.",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    skipped_models, skip_sources = _load_skip_models(PROJECT_ROOT)
    if args.model_name and args.model_name in skipped_models:
        source_text = ", ".join(str(p) for p in skip_sources) if skip_sources else "OBF_SKIP_MODELS"
        print(f"[SKIP] model {args.model_name} skipped by active policy from {source_text}")
        return
    if args.record_bdv is not None:
        print("[WARN] --record-bdv is deprecated and ignored. Use --record-layers on/off only.")
    if args.record_bdv_buckets is not None:
        print("[WARN] --record-bdv-buckets is deprecated and ignored. Buckets b1+b3 are emitted automatically when --record-layers=on.")

    gpu_ids = _parse_gpu_ids(args.gpu_ids)
    if gpu_ids is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in gpu_ids)
    visible_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
    max_devices = None
    if gpu_ids is not None and visible_gpus > 0:
        max_devices = min(len(gpu_ids), visible_gpus)
    elif args.gpus is not None and visible_gpus > 0:
        max_devices = min(max(1, int(args.gpus)), visible_gpus)

    base_dir = Path(__file__).resolve().parents[1]
    source_root = resolve_artifact_path(base_dir, args.source_root)
    techniques_filter = _parse_techniques(args.techniques)
    variants = _collect_variants(
        source_root,
        snippet_filter=args.code_snippet.strip() if args.code_snippet else None,
        techniques_filter=techniques_filter,
    )
    if not variants:
        raise RuntimeError(
            f"No obfuscated variants matched the requested filters under source root: {source_root}"
        )

    run_tag = args.run_tag.strip() if args.run_tag else None
    if not run_tag and args.auto_run_tag:
        run_tag = f"{time.strftime('%Y%m%d-%H%M%S')}-{args.dataset}-pid{os.getpid()}"
    if run_tag:
        run_tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_tag)
    else:
        run_tag = "default"

    task_profile = resolve_task_profile(args.dataset, args.task_profile)
    result_layout = args.result_layout
    if result_layout == "auto":
        result_layout = "flat" if task_profile == "counterfactual_tf" else "grouped"
    stdout_instruction = (
        "You will analyze the Java program provided below. "
        "First, explain how you will predict the output for the code snippet. "
        "Then, simulate it as a compiler would and print the exact console output. \n"
    )
    cf_cache_dir = resolve_artifact_path(base_dir, args.cf_cache_dir)
    cf_strict_json = args.cf_strict_json == "on"
    cf_rebuild = args.cf_rebuild == "on"

    llama = ModelRunner()
    base_steering_config = _build_steering_config(args)
    active_steering_config: Optional[SteeringConfig] = None
    if base_steering_config is not None:
        active_steering_config = copy.deepcopy(base_steering_config)
        llama.set_steering_config(active_steering_config)
    llama.login_hf()
    llama.config(
        key_scope="prompt",
        max_devices=max_devices,
        model_name=args.model_name,
        cache_dir=args.cache_dir,
    )
    llama.build()
    if base_steering_config and args.steer_last_n_layers is not None:
        n = max(1, int(args.steer_last_n_layers))
        num_layers = getattr(getattr(llama.model, "config", None), "num_hidden_layers", None)
        if not isinstance(num_layers, int) or num_layers <= 0:
            layers_obj = getattr(getattr(llama.model, "model", None), "layers", None)
            num_layers = len(layers_obj) if layers_obj is not None else None
        if isinstance(num_layers, int) and num_layers > 0:
            start = max(0, num_layers - min(n, num_layers))
            end = max(0, num_layers - 1)
            base_steering_config.steer_layer_start = start
            base_steering_config.steer_layer_end = end
            if active_steering_config is not None:
                _assign_config_fields(active_steering_config, base_steering_config)
            print(
                f"[Steering] last-{n} layer override active: start={start}, end={end} (num_layers={num_layers})"
            )
        else:
            print(
                "[WARN] --steer-last-n-layers provided but failed to infer model layer count; "
                "using backend defaults."
            )

    model_label = model_dir_name(args.model_name or llama.model_name)
    output_root = resolve_obf_result_root(base_dir, model_label)
    output_root.mkdir(parents=True, exist_ok=True)

    runs_per_variant = max(1, int(args.runs_per_snippet))
    total_runs_expected = len(variants) * runs_per_variant
    record_layers = args.record_layers == "on"
    if base_steering_config is None:
        run_mode = "plain"
    else:
        run_mode = "steered"

    run_progress = tqdm(
        total=total_runs_expected,
        desc=f"{args.dataset}:{run_mode}",
        unit="run",
        dynamic_ncols=True,
        leave=True,
    )
    try:
        for snippet, technique, variant_path in variants:
            code = variant_path.read_text(encoding="utf-8")
            java_class_name = variant_path.stem
            instruction = stdout_instruction
            answer_prefix = ""
            case_pack = None
            case_ids: List[str] = []
            if task_profile == "counterfactual_tf":
                case_pack = build_case_pack(
                    java_code=code,
                    class_name=java_class_name,
                    dataset=args.dataset,
                    snippet=snippet,
                    min_cases=args.cf_min_cases,
                    target_cases=args.cf_target_cases,
                    cache_dir=cf_cache_dir,
                    rebuild=cf_rebuild,
                )
                instruction = build_counterfactual_instruction(case_pack)
                answer_prefix = "\n\nJSON answer:\n"
                case_ids = [str(c["case_id"]) for c in case_pack.get("cases", [])]
            if base_steering_config:
                current_cfg = copy.deepcopy(base_steering_config)
                if (
                    task_profile == "counterfactual_tf"
                    and args.dataset in {"humaneval", "cruxeval"}
                    and current_cfg.prior == "human"
                ):
                    current_cfg.prior = "slice_hybrid"
                if active_steering_config is None:
                    active_steering_config = current_cfg
                    llama.set_steering_config(active_steering_config)
                else:
                    _assign_config_fields(active_steering_config, current_cfg)
                if current_cfg.head_subset_mode == "auto":
                    llama.calibrate_head_subset(
                        code_snippet=code,
                        instruction=instruction,
                        language="java",
                        vocab_tokens=[],
                        snippet_name=snippet,
                    )
            exec_result = utity.run_java_program_with_result(code, java_class_name, enable_assertions=True)
            if not exec_result.get("compiled", False):
                raise RuntimeError(
                    f"Failed to compile obfuscated variant {variant_path}: {exec_result.get('compile_error', '')}"
                )
            if task_profile == "counterfactual_tf":
                oracle_labels = {
                    str(c["case_id"]): ("T" if bool(c["expected_bool"]) else "F")
                    for c in (case_pack or {}).get("cases", [])
                }
                actual_output_str = json.dumps(oracle_labels, sort_keys=True)
                actual_output_clean = actual_output_str
            else:
                if not exec_result.get("success", False):
                    raise RuntimeError(
                        f"Failed to execute obfuscated variant {variant_path}: {exec_result.get('runtime_error', '')}"
                    )
                actual_output_str = str(exec_result.get("stdout", ""))
                actual_output_clean = actual_output_str.strip()

            variant_root = output_root / snippet / technique / run_tag
            variant_root.mkdir(parents=True, exist_ok=True)
            if result_layout == "grouped":
                for outcome in ("EM", "Mismatch"):
                    out_dir = variant_root / outcome
                    if out_dir.exists():
                        for child in out_dir.iterdir():
                            if child.is_dir():
                                shutil.rmtree(child)
                            else:
                                child.unlink()
                    out_dir.mkdir(exist_ok=True)
            else:
                for run_child in variant_root.glob("run_*"):
                    if run_child.is_dir():
                        shutil.rmtree(run_child)
                    else:
                        run_child.unlink()

            run_idx = 1
            completed = 0
            while completed < runs_per_variant:
                result = llama.run_llama(
                    code,
                    instruction=instruction,
                    language="java",
                    answer_prefix=answer_prefix,
                    max_new_tokens=max(1, int(args.max_new_tokens)),
                    record_layers=record_layers,
                    record_attention=record_layers,
                    vocab_tokens=[],
                )
                predicted_output_raw = result.get("generated_text", "")
                if task_profile == "counterfactual_tf":
                    predicted_map, parse_meta = parse_predicted_labels(
                        predicted_output_raw,
                        case_ids,
                        strict_json=cf_strict_json,
                    )
                    parse_mode = str(parse_meta.get("parse_mode", "none"))
                    provided_case_count = int(parse_meta.get("provided_case_count", 0))
                    requested_case_count = int(parse_meta.get("requested_case_count", len(case_ids)))
                    if requested_case_count > 0 and provided_case_count < requested_case_count:
                        continue
                    score = score_case_predictions(case_pack or {}, predicted_map)
                    parse_coverage = (
                        float(provided_case_count) / float(requested_case_count)
                        if requested_case_count > 0
                        else 0.0
                    )
                    strict_pass = bool(score["all_cases_pass"])
                    if provided_case_count == 0:
                        match_label = "parse_fail"
                    elif strict_pass:
                        match_label = "all_pass"
                    else:
                        match_label = "partial"
                    predicted_output = json.dumps(score["predicted_labels"], sort_keys=True)
                    is_exact_match = strict_pass
                    result["counterfactual"] = {
                        "profile": "counterfactual_tf",
                        "case_total": int(score["case_total"]),
                        "case_correct": int(score["case_correct"]),
                        "case_accuracy": float(score["case_accuracy"]),
                        "all_cases_pass": strict_pass,
                        "strict_pass": strict_pass,
                        "match_label": match_label,
                        "parse_mode": parse_mode,
                        "provided_case_count": provided_case_count,
                        "requested_case_count": requested_case_count,
                        "parse_coverage": parse_coverage,
                        "parse_meta": parse_meta,
                    }
                    result["oracle_labels"] = score["oracle_labels"]
                    result["predicted_labels"] = score["predicted_labels"]
                    result["per_case_scores"] = score["per_case"]
                    result["case_total"] = int(score["case_total"])
                    result["case_correct"] = int(score["case_correct"])
                    result["case_accuracy"] = float(score["case_accuracy"])
                    result["all_cases_pass"] = strict_pass
                    result["strict_pass"] = strict_pass
                    result["match_label"] = match_label
                    result["parse_mode"] = parse_mode
                    result["provided_case_count"] = provided_case_count
                    result["requested_case_count"] = requested_case_count
                    result["parse_coverage"] = parse_coverage
                    result["exact_match"] = strict_pass
                else:
                    predicted_output, format_ok = _canonicalize_model_output(predicted_output_raw)
                    if not format_ok and not (actual_output_clean == "" and predicted_output == ""):
                        continue

                    is_exact_match = predicted_output == actual_output_clean
                if result_layout == "grouped":
                    run_dir = variant_root / ("EM" if is_exact_match else "Mismatch") / f"{run_idx}"
                else:
                    run_dir = variant_root / f"run_{run_idx:04d}"
                run_dir.mkdir(parents=True, exist_ok=True)

                result["actual_output"] = actual_output_str
                result["predicted_output"] = predicted_output
                result["predicted_output_raw"] = predicted_output_raw
                result["exact_match"] = is_exact_match
                result["task"] = "output_prediction"
                result["task_profile"] = task_profile
                result["eval_profile"] = task_profile
                result["dataset"] = args.dataset
                result["mode"] = run_mode
                result["actual_execution"] = exec_result
                result["obfuscation"] = {
                    "dataset": args.dataset,
                    "snippet": snippet,
                    "technique": technique,
                    "variant_file": variant_path.name,
                }

                if record_layers:
                    pair_id = f"{snippet}:{technique}:{run_idx:03d}"
                    artifact_paths = llama.write_recording_superset(
                        result=result,
                        run_dir=run_dir,
                        schema_dir=variant_root,
                        code_snippet=code,
                        instruction=instruction,
                        target_text=actual_output_clean,
                        language="java",
                        pair_id=pair_id,
                        variant_type="obf",
                        is_correct=is_exact_match,
                    )
                    result.update(artifact_paths)
                    result["recording_complete"] = True
                    result.pop("full_decode_head_tensors", None)
                    required = [
                        artifact_paths.get("record_layers_full_path"),
                        artifact_paths.get("bdv_features_b1_path"),
                        artifact_paths.get("bdv_features_b3_path"),
                        artifact_paths.get("bdv_schema_path"),
                    ]
                    if any(not p or not Path(p).is_file() for p in required):
                        raise RuntimeError(
                            f"Recorder failure for {snippet}/{technique} run {run_idx:03d}: missing required superset artifacts."
                        )
                else:
                    result["recording_complete"] = False
                    result.pop("full_decode_head_tensors", None)

                if task_profile == "counterfactual_tf":
                    score_payload = {
                        "eval_profile": "counterfactual_tf",
                        "case_total": int(result.get("case_total", 0)),
                        "case_correct": int(result.get("case_correct", 0)),
                        "case_accuracy": float(result.get("case_accuracy", 0.0)),
                        "all_cases_pass": bool(result.get("all_cases_pass", False)),
                        "strict_pass": bool(result.get("strict_pass", False)),
                        "match_label": str(result.get("match_label", "partial")),
                        "parse_mode": str(result.get("parse_mode", "none")),
                        "provided_case_count": int(result.get("provided_case_count", 0)),
                        "requested_case_count": int(result.get("requested_case_count", 0)),
                        "parse_coverage": float(result.get("parse_coverage", 0.0)),
                    }
                    if case_pack is not None:
                        (run_dir / "case_pack.json").write_text(
                            json.dumps(case_pack, indent=2),
                            encoding="utf-8",
                        )
                    (run_dir / "oracle_labels.json").write_text(
                        json.dumps(result.get("oracle_labels", {}), indent=2),
                        encoding="utf-8",
                    )
                    (run_dir / "predicted_labels.json").write_text(
                        json.dumps(result.get("predicted_labels", {}), indent=2),
                        encoding="utf-8",
                    )
                    (run_dir / "score.json").write_text(
                        json.dumps(score_payload, indent=2),
                        encoding="utf-8",
                    )
                llama.save_dump(result, str(run_dir / "model_output.json"))
                (run_dir / "actual_output.txt").write_text(actual_output_str + "\n", encoding="utf-8")
                (run_dir / "predicted_output.txt").write_text(predicted_output + "\n", encoding="utf-8")
                (run_dir / "predicted_output_raw.txt").write_text(predicted_output_raw + "\n", encoding="utf-8")
                run_progress.set_postfix_str(f"{snippet}/{technique} run {completed + 1}/{runs_per_variant}")
                run_progress.update(1)
                run_idx += 1
                completed += 1
    finally:
        run_progress.close()
        llama.free()


if __name__ == "__main__":
    main()
