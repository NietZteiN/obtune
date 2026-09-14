# main.py

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
import re
import json
import copy
import shutil
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - optional dependency at runtime
    tqdm = None
from models import ModelRunner
from util import utity
from render.util import AttentionRenderer, RenderConfig
from steering import SteeringConfig
from counterfactual_eval import (
    build_case_pack,
    build_counterfactual_instruction,
    parse_predicted_labels,
    resolve_task_profile,
    score_case_predictions,
)
from paths import (
    model_dir_name,
    resolve_artifact_path,
    resolve_attn_root,
    resolve_dataset_source_root,
    resolve_eyetracking_source_root,
)


def _canonicalize_model_output(text: str) -> tuple[str, bool]:
    """
    Normalize model output to remove common formatting artifacts while preserving content.

    Returns a tuple of (normalized_output, format_found).
    """
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

    # Handle \begin{code} ... ``` or \end{code}
    code_match = re.search(r"\\begin\{code\}(.*?)(?:```|\\end\{code\}|$)", stripped, re.DOTALL)
    if code_match:
        cand = code_match.group(1).strip()
        if cand:
            return cand, True

    # Fallback: take everything after the last fence if present, else try trailing numeric block.
    if matches:
        last_end = matches[-1].end()
        tail = stripped[last_end:].strip()
        if tail:
            return tail, True

    # Trailing numeric/non-alpha block heuristic
    lines = stripped.splitlines()
    collected: List[str] = []
    for line in reversed(lines):
        if line.strip() == "":
            if collected:
                break
            continue
        if re.search(r"[A-Za-z]", line):
            if collected:
                break
            continue
        collected.append(line.strip())
    if collected:
        return "\n".join(reversed(collected)), True

    return stripped, False


def _compute_generated_token_spans(
    tokenizer,
    token_ids_all: Sequence[int],
    prompt_len: int,
) -> List[Tuple[int, int]]:
    generated_ids = token_ids_all[prompt_len:]
    spans: List[Tuple[int, int]] = []
    if not generated_ids:
        return spans

    decoded_prev = ""
    for idx in range(len(generated_ids)):
        current = tokenizer.decode(generated_ids[: idx + 1], skip_special_tokens=True)
        spans.append((len(decoded_prev), len(current)))
        decoded_prev = current
    return spans


def _classify_generation_phases(
    result: Dict[str, Any],
    tokenizer,
) -> Tuple[Dict[int, str], Dict[str, Tuple[int, int]]]:
    completion = result.get("generated_completion", "")
    lower = completion.lower()

    # Identify the likely answer as the *last* non-Java fenced block.
    answer_start = -1
    answer_end = -1
    search_pos = 0
    while True:
        idx = lower.find("```", search_pos)
        if idx == -1:
            break
        lang_token = lower[idx : idx + 8]
        if "```java" in lang_token:
            search_pos = idx + 3
            continue
        answer_start = idx
        end_idx = lower.find("```", idx + 3)
        if end_idx != -1:
            answer_end = end_idx + 3
        search_pos = idx + 3
    if answer_start == -1:
        answer_start = len(completion)
    if answer_end == -1:
        answer_end = len(completion)

    # Explanation flagged by keyword if present.
    expl_start = lower.find("explanation")
    if expl_start == -1 or expl_start >= answer_start:
        expl_start = answer_start

    reading_range = (0, max(0, expl_start))
    reasoning_range = (expl_start, max(expl_start, answer_start))
    answer_range = (answer_start, answer_end)

    token_spans = _compute_generated_token_spans(
        tokenizer,
        result.get("token_ids_all", []),
        result.get("prompt_length_tokens", 0),
    )

    phase_by_step: Dict[int, str] = {}
    for idx, (start_char, end_char) in enumerate(token_spans):
        phase = "reading"
        if answer_range[0] < answer_range[1] and answer_range[0] <= start_char < answer_range[1]:
            phase = "answering"
        elif reasoning_range[0] < reasoning_range[1] and reasoning_range[0] <= start_char < reasoning_range[1]:
            phase = "reasoning"
        phase_by_step[idx] = phase

    phase_ranges = {
        "reading": reading_range,
        "answering": answer_range,
        "reasoning": reasoning_range,
    }
    return phase_by_step, phase_ranges


def _aggregate_phase_prompt_scores(
    result: Dict[str, Any],
    phase_assignments: Dict[int, str],
    pool_name: str,
) -> Tuple[Dict[str, List[float]], Dict[str, int]]:
    prompt_len = result.get("prompt_length_tokens", 0)
    per_step = result.get("pooled_attention_by_generated_token", [])
    aggregators: Dict[str, np.ndarray] = {}
    counts: Dict[str, int] = {}

    for entry in per_step:
        step = entry.get("generated_step")
        if step is None:
            continue
        phase = phase_assignments.get(step)
        if not phase:
            continue
        prompt_scores = entry.get("prompt_scores", {}).get(pool_name)
        if not prompt_scores:
            continue
        if phase not in aggregators:
            aggregators[phase] = np.zeros(prompt_len, dtype=float)
            counts[phase] = 0
        aggregators[phase] += np.asarray(prompt_scores, dtype=float)
        counts[phase] += 1

    for phase in phase_assignments.values():
        aggregators.setdefault(phase, np.zeros(prompt_len, dtype=float))
        counts.setdefault(phase, 0)

    phase_scores: Dict[str, List[float]] = {}
    for phase, arr in aggregators.items():
        count = counts.get(phase, 0)
        if count > 0:
            phase_scores[phase] = (arr / count).tolist()
        else:
            phase_scores[phase] = [0.0] * prompt_len

    return phase_scores, counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Eyetracking collection with optional steering.")
    parser.add_argument(
        "--steer",
        action="store_true",
        help="Enable the default steering path used in the paper.",
    )
    parser.add_argument("--prior", choices=["human", "ast", "lex", "rand", "uniform", "cfg", "slice", "slice_hybrid"], default="human")
    parser.add_argument("--n-bins", type=int, default=8)
    parser.add_argument("--binning", choices=["equal_count"], default="equal_count")
    parser.add_argument("--beta-bias", type=float, default=0.0)
    parser.add_argument("--beta-post", type=float, default=0.0)
    parser.add_argument("--lambda-attn", type=float, default=1.0)
    parser.add_argument("--lambda-mlp", type=float, default=1.0)
    parser.add_argument(
        "--residual-scale",
        choices=["on", "off"],
        default="off",
        help="Enable residual scaling (decode-only, layer-banded).",
    )
    parser.add_argument(
        "--residual-scale-mode",
        choices=["static", "amplifier", "paired", "agreement_gate"],
        default="static",
        help="Residual scaling mode.",
    )
    parser.add_argument(
        "--lambda-attn-delta",
        type=float,
        default=0.0,
        help="Paired mode delta; lambdas become (1+delta, 1-delta) with clipping.",
    )
    parser.add_argument(
        "--residual-scale-layer-start",
        type=int,
        default=None,
        help="Optional override start layer index for residual scaling band.",
    )
    parser.add_argument(
        "--residual-scale-layer-end",
        type=int,
        default=None,
        help="Optional override end layer index for residual scaling band.",
    )
    parser.add_argument(
        "--residual-scale-debug",
        action="store_true",
        help="Print one-time residual scaling debug and collect per-step residual debug records.",
    )
    parser.add_argument(
        "--lambda-attn-alpha",
        type=float,
        default=0.05,
        help="Agreement-gate alpha: lambda_attn=1+alpha*clamp(agree_rel-1,0,cap).",
    )
    parser.add_argument(
        "--lambda-attn-cap",
        type=float,
        default=4.0,
        help="Agreement-gate cap in lambda_attn computation.",
    )
    parser.add_argument(
        "--agreement-scope",
        choices=["selected_heads", "all_heads"],
        default="selected_heads",
        help="Agreement-gate aggregation scope for per-head agreement signal.",
    )
    parser.add_argument("--alpha-k", type=float, default=0.0)
    parser.add_argument("--alpha-v", type=float, default=0.0)
    parser.add_argument("--beta-ptr", type=float, default=0.0)
    parser.add_argument("--bias-cap", type=float, default=None)
    parser.add_argument("--gamma-min", type=float, default=0.0)
    parser.add_argument("--gamma-max", type=float, default=5.0)
    parser.add_argument("--eta-min", type=float, default=0.0)
    parser.add_argument("--eta-max", type=float, default=5.0)
    parser.add_argument("--human-file", type=Path, default=None)
    parser.add_argument("--lex-window", type=int, default=32)
    parser.add_argument("--rand-seed", type=int, default=None)
    parser.add_argument("--schedule-json", type=Path, default=None)
    parser.add_argument(
        "--recency-mix",
        choices=["on", "off"],
        default="on",
        help="Enable Step-2 temporal prior mixing (prompt prior + recency prior).",
    )
    parser.add_argument(
        "--recency-rho",
        type=float,
        default=0.2,
        help="Recency mixing weight rho in p_all=(1-rho)*p_prompt + rho*p_recent.",
    )
    parser.add_argument(
        "--recency-window",
        type=int,
        default=64,
        help="Recency window size (last W keys).",
    )
    parser.add_argument(
        "--recency-apply-after-prompt",
        choices=["on", "off"],
        default="on",
        help="When on, first decode step uses only prompt prior (no recency dilution).",
    )
    parser.add_argument(
        "--recency-scope",
        choices=["prefer_generated", "last_w"],
        default="prefer_generated",
        help="Recency key range policy.",
    )
    parser.add_argument(
        "--only-first-decode-step",
        choices=["on", "off"],
        default=None,
        help="Override decode-step gating (default: off for Step-2 multi-step steering).",
    )
    parser.add_argument(
        "--head-subset-mode",
        choices=["none", "file", "auto"],
        default="none",
        help="Head subset steering mode: none (all heads), file, or auto calibration.",
    )
    parser.add_argument(
        "--head-mask-path",
        type=Path,
        default=None,
        help="Path to JSON head mask file with shape [num_layers, num_heads].",
    )
    parser.add_argument(
        "--head-mask-apply-to",
        choices=["l1", "l2", "both"],
        default="both",
        help="Which internal steering stage(s) should apply the head mask.",
    )
    parser.add_argument(
        "--head-mask-debug",
        action="store_true",
        help="Print head-mask loading details at runtime.",
    )
    parser.add_argument(
        "--head-subset-topk-per-layer",
        type=int,
        default=4,
        help="For auto mode, select top-k heads per layer by agreement.",
    )
    parser.add_argument(
        "--head-subset-calib-runs",
        type=int,
        default=3,
        help="Auto mode: number of calibration generations.",
    )
    parser.add_argument(
        "--head-subset-calib-max-new-tokens",
        type=int,
        default=64,
        help="Auto mode: max_new_tokens during calibration.",
    )
    parser.add_argument(
        "--head-subset-calib-first-decode-only",
        choices=["on", "off"],
        default="on",
        help="Auto mode: collect calibration stats only at first decode step.",
    )
    parser.add_argument(
        "--head-subset-auto-save",
        type=Path,
        default=None,
        help="Optional path to save auto-calibrated mask JSON (file or directory).",
    )
    parser.add_argument(
        "--collect-head-stats",
        choices=["on", "off"],
        default="off",
        help="Collect per-layer per-head agreement stats for offline mask building.",
    )
    parser.add_argument(
        "--collect-head-stats-first-decode-only",
        choices=["on", "off"],
        default="on",
        help="Collect head stats only at first decode step (kv_len==prompt_len).",
    )
    parser.add_argument(
        "--steer-last-n-layers",
        type=int,
        default=None,
        help=(
            "Override the steering layer band to the last N decoder layers "
            "(e.g., 8 means [num_layers-8, num_layers-1])."
        ),
    )
    parser.add_argument("--model-name", type=str, default=None, help="HF model name to load.")
    parser.add_argument("--cache-dir", type=str, default=None, help="HF cache directory for the model.")
    parser.add_argument(
        "--gpus",
        type=int,
        default=None,
        help="Number of GPUs to use (caps device_map). Defaults to auto (all visible).",
    )
    parser.add_argument(
        "--gpu-ids",
        type=str,
        default=None,
        help="Explicit GPU IDs to use (e.g., 0+1 or 0,1). Overrides --gpus.",
    )
    parser.add_argument("--runs-per-snippet", type=int, default=20, help="Number of generations per snippet.")
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum number of generated tokens per run.",
    )
    parser.add_argument("--skip-steering", action="store_true")
    parser.add_argument(
        "--record-layers",
        choices=["on", "off"],
        default="on",
        help="When off, disable all attention capture and visualization output.",
    )
    parser.add_argument(
        "--visual-dump",
        choices=["on", "off"],
        default="on",
        help="When off, skip all attention visualization/text dump artifacts while keeping recorder outputs.",
    )
    parser.add_argument(
        "--record-logits",
        choices=["on", "off"],
        default="off",
        help="When on, save full per-step generated-token logits to generated_logits_full.npz for each run.",
    )
    parser.add_argument(
        "--record-bdv",
        choices=["on", "off"],
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--record-bdv-buckets",
        type=str,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--run-tag",
        type=str,
        default=None,
        help="Optional output subfolder tag to avoid collisions across parallel runs.",
    )
    parser.add_argument(
        "--auto-run-tag",
        action="store_true",
        help="Auto-generate a run tag (timestamp+pid) when --run-tag is not provided.",
    )
    parser.add_argument("--snippet", type=str, default=None, help="Run only this snippet (single name without .java).")
    parser.add_argument(
        "--snippets",
        type=str,
        default=None,
        help="Comma-separated list of snippet names to run. Defaults to all when omitted.",
    )
    parser.add_argument(
        "--dataset",
        choices=["eyetracking", "humaneval", "cruxeval"],
        default="eyetracking",
        help="Source dataset selector: eyetracking -> Source/eyetracking, humaneval -> Source/Humaneval(/java), cruxeval -> Source/Cruxeval(/java).",
    )
    parser.add_argument(
        "--task-profile",
        choices=["auto", "stdout", "counterfactual_tf"],
        default="auto",
        help=(
            "Evaluation profile selector. humaneval/cruxeval are hard-switched to counterfactual_tf; "
            "eyetracking defaults to stdout."
        ),
    )
    parser.add_argument("--cf-min-cases", type=int, default=8, help="Minimum number of counterfactual T/F cases.")
    parser.add_argument("--cf-target-cases", type=int, default=16, help="Target number of counterfactual T/F cases.")
    parser.add_argument(
        "--cf-cache-dir",
        type=str,
        default="logs/eval_casepacks",
        help="Cache directory for generated counterfactual case packs.",
    )
    parser.add_argument(
        "--cf-rebuild",
        choices=["on", "off"],
        default="off",
        help="When on, ignore case-pack cache and rebuild.",
    )
    parser.add_argument(
        "--cf-strict-json",
        choices=["on", "off"],
        default="on",
        help="When on, enforce JSON-first parsing for counterfactual predictions (regex fallback still attempted).",
    )
    parser.add_argument(
        "--result-layout",
        choices=["auto", "grouped", "flat"],
        default="auto",
        help=(
            "Output directory layout. auto=flat for counterfactual_tf and grouped for stdout; "
            "grouped=EM/Mismatch folders; flat=run_XXXX folders."
        ),
    )
    parser.add_argument(
        "--validation-mode",
        choices=["auto", "stdout", "assertion_verdict"],
        default="auto",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def _parse_gpu_ids(raw: Optional[str]) -> Optional[List[int]]:
    if not raw:
        return None
    cleaned = raw.strip()
    if not cleaned:
        return None
    parts = re.split(r"[+,]", cleaned)
    ids: List[int] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise ValueError(f"Invalid GPU id '{part}' in --gpu-ids={raw!r}. Use digits separated by '+' or ','.")
        ids.append(int(part))
    if not ids:
        return None
    return ids


def build_steering_config(args: argparse.Namespace) -> Optional[SteeringConfig]:
    enabled = [2] if bool(args.steer) else []
    if not enabled or args.skip_steering:
        return None
    project_root = Path(__file__).resolve().parent
    head_mask_path = (
        resolve_artifact_path(project_root, args.head_mask_path)
        if args.head_mask_path is not None
        else None
    )
    head_subset_auto_save = (
        resolve_artifact_path(project_root, args.head_subset_auto_save)
        if args.head_subset_auto_save is not None
        else None
    )
    return SteeringConfig(
        enabled_levels=enabled,
        prior=args.prior,
        n_bins=args.n_bins,
        binning=args.binning,
        beta_bias=args.beta_bias,
        beta_post=args.beta_post,
        lambda_attn=args.lambda_attn,
        lambda_mlp=args.lambda_mlp,
        residual_scale=(args.residual_scale == "on"),
        residual_scale_mode=args.residual_scale_mode,
        lambda_attn_delta=args.lambda_attn_delta,
        residual_scale_layer_start=args.residual_scale_layer_start,
        residual_scale_layer_end=args.residual_scale_layer_end,
        residual_scale_debug=bool(args.residual_scale_debug),
        lambda_attn_alpha=args.lambda_attn_alpha,
        lambda_attn_cap=args.lambda_attn_cap,
        agreement_scope=args.agreement_scope,
        alpha_k=args.alpha_k,
        alpha_v=args.alpha_v,
        beta_ptr=args.beta_ptr,
        bias_cap=args.bias_cap,
        gamma_min=args.gamma_min,
        gamma_max=args.gamma_max,
        eta_min=args.eta_min,
        eta_max=args.eta_max,
        human_file=args.human_file,
        lex_window=args.lex_window,
        rand_seed=args.rand_seed,
        schedule_json=args.schedule_json,
        recency_mix=(args.recency_mix == "on"),
        recency_rho=args.recency_rho,
        recency_window=args.recency_window,
        recency_apply_after_prompt=(args.recency_apply_after_prompt == "on"),
        recency_scope=args.recency_scope,
        only_first_decode_step=(
            (args.only_first_decode_step == "on")
            if args.only_first_decode_step is not None
            else False
        ),
        head_subset_mode=args.head_subset_mode,
        head_mask_path=head_mask_path,
        head_mask_apply_to=args.head_mask_apply_to,
        head_mask_debug=bool(args.head_mask_debug),
        head_subset_topk_per_layer=max(1, int(args.head_subset_topk_per_layer)),
        head_subset_calib_runs=max(1, int(args.head_subset_calib_runs)),
        head_subset_calib_max_new_tokens=max(1, int(args.head_subset_calib_max_new_tokens)),
        head_subset_calib_first_decode_only=(args.head_subset_calib_first_decode_only == "on"),
        head_subset_auto_save=head_subset_auto_save,
        collect_head_stats=(args.collect_head_stats == "on"),
        collect_head_stats_first_decode_only=(args.collect_head_stats_first_decode_only == "on"),
    )


def _assign_config_fields(target: SteeringConfig, source: SteeringConfig) -> None:
    for key, value in vars(source).items():
        setattr(target, key, copy.deepcopy(value))


def main():
    args = parse_args()
    if args.record_bdv is not None:
        print("[WARN] --record-bdv is deprecated and ignored. Use --record-layers on/off only.")
    if args.record_bdv_buckets is not None:
        print("[WARN] --record-bdv-buckets is deprecated and ignored. Buckets b1+b3 are emitted automatically when --record-layers=on.")
    gpu_ids = _parse_gpu_ids(args.gpu_ids)
    if gpu_ids is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in gpu_ids)
    visible_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
    max_devices = None
    if gpu_ids is not None:
        if visible_gpus == 0:
            print("[WARN] --gpu-ids specified but no CUDA devices visible; falling back to CPU.")
        else:
            max_devices = min(len(gpu_ids), visible_gpus)
    elif args.gpus is not None:
        if visible_gpus == 0:
            print("[WARN] --gpus specified but no CUDA devices visible; falling back to CPU.")
        else:
            requested = max(1, args.gpus)
            max_devices = min(requested, visible_gpus)
            if requested > visible_gpus:
                print(f"[WARN] Requested {requested} GPUs but only {visible_gpus} visible; using {max_devices}.")

    # 1) Build/run the model (only HF token may come from env)
    llama = ModelRunner()
    base_steering_config = build_steering_config(args)
    human_prior_override = args.human_file
    active_steering_config: Optional[SteeringConfig] = None
    if base_steering_config:
        active_steering_config = copy.deepcopy(base_steering_config)
        llama.set_steering_config(active_steering_config)
    llama.login_hf()                  # optional; uses HUGGINGFACE_TOKEN if present
    llama.config(
        key_scope="prompt",
        max_devices=max_devices,
        model_name=args.model_name,
        cache_dir=args.cache_dir,
    )  # IMPORTANT for prompt-aligned attention
    llama.build()

    if base_steering_config and args.steer_last_n_layers is not None:
        n = max(1, int(args.steer_last_n_layers))
        num_layers = getattr(getattr(llama.model, "config", None), "num_hidden_layers", None)
        if not isinstance(num_layers, int) or num_layers <= 0:
            layers_obj = getattr(getattr(llama.model, "model", None), "layers", None)
            num_layers = len(layers_obj) if layers_obj is not None else None
        if not isinstance(num_layers, int) or num_layers <= 0:
            print(
                "[WARN] --steer-last-n-layers provided but failed to infer model layer count; "
                "falling back to backend defaults."
            )
        else:
            start = max(0, num_layers - min(n, num_layers))
            end = max(0, num_layers - 1)
            base_steering_config.steer_layer_start = start
            base_steering_config.steer_layer_end = end
            print(
                f"[Steering] Layer override via --steer-last-n-layers={n}: "
                f"start={start}, end={end} (num_layers={num_layers})"
            )

    level_label = "baseline"
    prior_label = "none"
    if base_steering_config:
        level_label = "steered"
        prior_label = base_steering_config.prior

    # 2) Build our image renderer
    renderer = AttentionRenderer(tokenizer=llama.tokenizer, config=RenderConfig(pool="all_layers_mean"))
    # code_set = []
    # for snippet in os.listdir("./Source"):
    #     code_set.append(open(f"./Source/{snippet}", 'r').read())
    # for code in code_set():

    model_label = model_dir_name(args.model_name or llama.model_name)
    base_dir = Path(__file__).resolve().parent
    output_root = resolve_attn_root(base_dir, model_label, for_write=True)
    output_root.mkdir(parents=True, exist_ok=True)
    run_tag = args.run_tag.strip() if args.run_tag else None
    if not run_tag and args.auto_run_tag:
        run_tag = f"{time.strftime('%Y%m%d-%H%M%S')}-pid{os.getpid()}"
    if run_tag:
        run_tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_tag)

    if args.dataset == "eyetracking":
        source_dir = resolve_eyetracking_source_root(base_dir)
    elif args.dataset == "humaneval":
        humaneval_candidates = [
            resolve_dataset_source_root(base_dir, "humaneval") / "java",
            resolve_dataset_source_root(base_dir, "humaneval"),
        ]
        source_dir = humaneval_candidates[0]
        for cand in humaneval_candidates:
            if cand.is_dir():
                source_dir = cand
                break
    else:
        cruxeval_candidates = [
            resolve_dataset_source_root(base_dir, "cruxeval") / "java",
            resolve_dataset_source_root(base_dir, "cruxeval"),
        ]
        source_dir = cruxeval_candidates[0]
        for cand in cruxeval_candidates:
            if cand.is_dir():
                source_dir = cand
                break
    fixation_root = base_dir / "fixation_dump"
    requires_fixation = args.dataset == "eyetracking"
    available_fixations = (
        {p.name for p in fixation_root.iterdir() if p.is_dir()}
        if (requires_fixation and fixation_root.is_dir())
        else set()
    )
    requested: set[str] = set()
    if args.snippet:
        requested.add(args.snippet.strip())
    if args.snippets:
        requested.update(s.strip() for s in args.snippets.split(",") if s.strip())

    if requested:
        snippet_paths = []
        for name in sorted(requested):
            candidate = source_dir / f"{name}.java"
            if not candidate.is_file():
                raise FileNotFoundError(f"Snippet '{name}' not found under {source_dir}.")
            if available_fixations and name not in available_fixations:
                print(f"[WARN] Fixation data not found for requested snippet '{name}'.")
            snippet_paths.append(candidate)
    else:
        snippet_paths = []
        for p in sorted(source_dir.iterdir()):
            if not p.is_file():
                continue
            if p.suffix.lower() != ".java":
                continue
            if available_fixations and p.stem not in available_fixations:
                print(f"[WARN] Skipping '{p.stem}' (no fixation data found).")
                continue
            snippet_paths.append(p)
    if not snippet_paths:
        print(f"No code snippets found under {source_dir.resolve()}")
        llama.free()
        return
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
    runs_per_snippet = max(1, args.runs_per_snippet)
    max_new_tokens = max(1, int(args.max_new_tokens))
    record_layers = args.record_layers != "off"
    record_attention = record_layers
    visual_dump = args.visual_dump != "off"
    record_logits = args.record_logits != "off"
    if base_steering_config is None:
        run_mode = "plain"
    else:
        run_mode = "steered"
    total_runs_target = len(snippet_paths) * runs_per_snippet
    progress = (
        tqdm(total=total_runs_target, desc="prediction", unit="run", dynamic_ncols=True)
        if tqdm is not None
        else None
    )
    try:
        for snippet_path in snippet_paths:
            code = snippet_path.read_text(encoding="utf-8")
            snippet_name = snippet_path.stem
            snippet_root = output_root / snippet_name / level_label / prior_label
            if run_tag:
                snippet_root = snippet_root / run_tag
            snippet_root.mkdir(parents=True, exist_ok=True)
            if result_layout == "grouped":
                for outcome in ("EM", "Mismatch"):
                    outcome_dir = snippet_root / outcome
                    if outcome_dir.exists():
                        for child in outcome_dir.iterdir():
                            if child.is_dir():
                                shutil.rmtree(child)
                            else:
                                child.unlink()
                    outcome_dir.mkdir(exist_ok=True)
            else:
                for run_child in snippet_root.glob("run_*"):
                    if run_child.is_dir():
                        shutil.rmtree(run_child)
                    else:
                        run_child.unlink()
            run_idx = 1
            runs_completed = 0
            instruction = stdout_instruction
            answer_prefix = ""
            case_pack = None
            case_ids: list[str] = []
            fixation_dir = fixation_root / snippet_name
            fixation_vocab: list[dict[str, object]] = [] # Type Hint
            vocab_path = fixation_dir / "vocabulary.json"
            if vocab_path.is_file():
                try:
                    fixation_vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
                except Exception as exc:
                    print(f"[{snippet_name}] Warning: failed to load fixation vocabulary ({exc}); continuing without it.")
            if task_profile == "counterfactual_tf":
                case_pack = build_case_pack(
                    java_code=code,
                    class_name=snippet_name,
                    dataset=args.dataset,
                    snippet=snippet_name,
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
                if current_cfg.prior == "human":
                    if human_prior_override:
                        current_cfg.human_file = human_prior_override
                    else:
                        snippet_fix_dir = fixation_dir
                        if not snippet_fix_dir.is_dir():
                            raise FileNotFoundError(
                                f"Human prior selected but no fixation directory found at {snippet_fix_dir} for snippet '{snippet_name}'."
                            )
                        current_cfg.human_file = snippet_fix_dir
                if active_steering_config is None:
                    active_steering_config = current_cfg
                    llama.set_steering_config(active_steering_config)
                else:
                    _assign_config_fields(active_steering_config, current_cfg)
                if current_cfg.head_subset_mode == "auto":
                    calib_info = llama.calibrate_head_subset(
                        code_snippet=code,
                        instruction=instruction,
                        language="java",
                        vocab_tokens=fixation_vocab,
                        snippet_name=snippet_name,
                    )
                    selected_heads = int(calib_info.get("active_total", 0))
                    layers_with_heads = int(calib_info.get("layers_with_heads", 0))
                    print(
                        f"[{snippet_name}] Auto head subset ready: "
                        f"active_heads={selected_heads}, layers_with_heads={layers_with_heads}"
                    )
                    if calib_info.get("auto_save_path"):
                        print(f"[{snippet_name}] Auto head subset mask: {calib_info['auto_save_path']}")
            exec_result = utity.run_java_program_with_result(code, snippet_name, enable_assertions=True)
            if not exec_result.get("compiled", False):
                llama.free()
                raise RuntimeError(
                    f"Failed to compile {snippet_path.name}: {exec_result.get('compile_error', '')}"
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
                    llama.free()
                    raise RuntimeError(
                        f"Failed to execute {snippet_path.name}: {exec_result.get('runtime_error', '')}"
                    )
                actual_output_str = str(exec_result.get("stdout", ""))
                actual_output_clean = actual_output_str.strip()
            while runs_completed < runs_per_snippet:
                result = llama.run_llama(
                    code,
                    instruction=instruction,
                    language="java",
                    answer_prefix=answer_prefix,
                    max_new_tokens=max_new_tokens,
                    record_layers=record_layers,
                    vocab_tokens=fixation_vocab,
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
                        print(
                            f"[{snippet_name}] Parse coverage {provided_case_count}/{requested_case_count} "
                            f"(mode={parse_mode}); retrying run {run_idx:03d}."
                        )
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

                attn_map = None
                phase_attention_maps = {}
                masked_attn_map = None
                if record_attention and visual_dump:
                    phase_assignments, phase_ranges = _classify_generation_phases(result, llama.tokenizer)
                    phase_prompt_scores, phase_counts = _aggregate_phase_prompt_scores(
                        result, phase_assignments, pool_name="all_layers_mean"
                    )
                    # TODO: Experiment with all 5 settings.
                    attn_map = renderer.map_attention_to_source(
                        code_snippet=code,
                        generation_result=result,
                        instruction=instruction,
                        pool="all_layers_mean",
                        human_vocabulary=fixation_vocab,
                    )
                    for phase, prompt_scores in phase_prompt_scores.items():
                        if phase_counts.get(phase, 0) == 0:
                            continue
                        phase_attention_maps[phase] = renderer.map_attention_from_prompt_scores(
                            code_snippet=code,
                            instruction=instruction,
                            prompt_scores=prompt_scores,
                            pool_name="all_layers_mean",
                            human_vocabulary=fixation_vocab,
                            metadata={
                                "phase": phase,
                                "phase_step_count": phase_counts.get(phase, 0),
                                "phase_char_range": phase_ranges.get(phase),
                            },
                        )
                    fixation_spans = [
                        (token["start"], token["end"])
                        for token in attn_map.get("fixation_tokens", [])
                        if not token.get("missing")
                        and token.get("start", -1) is not None
                        and int(token["start"]) >= 0
                        and int(token["end"]) > int(token["start"])
                    ]
                    if fixation_spans:
                        masked_attn_map = renderer.mask_attention_map(
                            code_snippet=code,
                            attn_map=attn_map,
                            spans=fixation_spans,
                            human_vocabulary=fixation_vocab,
                            note="fixation-aligned span",
                        )
                if result_layout == "grouped":
                    match_dir = snippet_root / ("EM" if is_exact_match else "Mismatch")
                    run_dir = match_dir / f"{run_idx}"
                else:
                    run_dir = snippet_root / f"run_{run_idx:04d}"
                run_dir.mkdir(parents=True, exist_ok=True)
                if record_attention and visual_dump and attn_map is not None:
                    renderer.save_text_dump(attn_map, str(run_dir / "attention.json"), str(run_dir / "attention.csv"))
                    renderer.render_html(code, attn_map, str(run_dir / "attention.html"))
                    renderer.render_png(code, attn_map, str(run_dir / "attention_char.png"), score_key="char_attention")
                    renderer.render_png(code, attn_map, str(run_dir / "attention_lexical.png"), score_key="lexical_tokens")
                    if attn_map.get("fixation_tokens"):
                        renderer.render_png(code, attn_map, str(run_dir / "attention_fixation.png"), score_key="fixation_tokens")
                    for phase, phase_map in phase_attention_maps.items():
                        phase_prefix = f"attention_phase_{phase}"
                        renderer.save_text_dump(
                            phase_map,
                            str(run_dir / f"{phase_prefix}.json"),
                            str(run_dir / f"{phase_prefix}.csv"),
                        )
                        renderer.render_html(code, phase_map, str(run_dir / f"{phase_prefix}.html"))
                        renderer.render_png(
                            code,
                            phase_map,
                            str(run_dir / f"{phase_prefix}_char.png"),
                            score_key="char_attention",
                        )
                        renderer.render_png(
                            code,
                            phase_map,
                            str(run_dir / f"{phase_prefix}_lexical.png"),
                            score_key="lexical_tokens",
                        )
                        if phase_map.get("fixation_tokens"):
                            renderer.render_png(
                                code,
                                phase_map,
                                str(run_dir / f"{phase_prefix}_fixation.png"),
                                score_key="fixation_tokens",
                            )
                    if masked_attn_map:
                        renderer.save_text_dump(masked_attn_map, str(run_dir / "attention_algorithm.json"), str(run_dir / "attention_algorithm.csv"))
                        renderer.render_html(code, masked_attn_map, str(run_dir / "attention_algorithm.html"))
                        renderer.render_png(code, masked_attn_map, str(run_dir / "attention_algorithm_char.png"), score_key="char_attention")
                        renderer.render_png(code, masked_attn_map, str(run_dir / "attention_algorithm_lexical.png"), score_key="lexical_tokens")
                        if masked_attn_map.get("fixation_tokens"):
                            renderer.render_png(code, masked_attn_map, str(run_dir / "attention_algorithm_fixation.png"), score_key="fixation_tokens")
                if record_layers:
                    pair_id = f"{snippet_name}:{run_idx:03d}"
                    variant_type = "plain" if level_label == "baseline" else "steered"
                    artifact_paths = llama.write_recording_superset(
                        result=result,
                        run_dir=run_dir,
                        schema_dir=snippet_root,
                        code_snippet=code,
                        instruction=instruction,
                        target_text=actual_output_clean,
                        language="java",
                        pair_id=pair_id,
                        variant_type=variant_type,
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
                            f"Recorder failure for {snippet_name} run {run_idx:03d}: missing required superset artifacts."
                        )
                else:
                    result["recording_complete"] = False
                    result.pop("full_decode_head_tensors", None)
                if record_logits:
                    logits_paths = llama.write_generated_logits_artifact(
                        result=result,
                        run_dir=run_dir,
                    )
                    result.update(logits_paths)
                else:
                    result["logits_recorded"] = False
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
                run_idx += 1
                runs_completed += 1
                if progress is not None:
                    progress.update(1)
    finally:
        if progress is not None:
            progress.close()
    llama.free()

if __name__ == "__main__":
    main()
