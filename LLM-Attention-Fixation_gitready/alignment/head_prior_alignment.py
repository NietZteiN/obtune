#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import ModelRunner  # noqa: E402
from steering import SteeringConfig  # noqa: E402
from paths import (  # noqa: E402
    resolve_artifact_path,
    resolve_alignment_outputs_root,
    resolve_eyetracking_source_root,
    resolve_head_mask_root,
)


@dataclass
class ReferenceMask:
    snippet: str
    path: Path
    active_pairs: List[Tuple[int, int]]
    agree_mean: np.ndarray
    model_name: str


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
            raise ValueError(f"Invalid GPU id '{p}' in --gpu-ids={raw!r}")
        out.append(int(p))
    return out or None


def _latest_masks_by_snippet(mask_dir: Path, pattern: str) -> Dict[str, Path]:
    by_snippet: Dict[str, List[Path]] = {}
    for p in mask_dir.glob(pattern):
        if not p.is_file():
            continue
        name = p.stem
        # expected pattern examples:
        # step4-l2-ast-b0p1-Ackerman-20260214-182442
        # snippet sits before trailing date/time chunks.
        m = re.match(r".+-([A-Za-z0-9_]+)-\d{8}-\d{6}$", name)
        if not m:
            continue
        snippet = m.group(1)
        by_snippet.setdefault(snippet, []).append(p)

    out: Dict[str, Path] = {}
    for snippet, files in by_snippet.items():
        out[snippet] = sorted(files)[-1]
    return out


def _mask_pairs_from_payload(payload: dict) -> List[Tuple[int, int]]:
    if "active_heads" in payload and isinstance(payload["active_heads"], dict):
        pairs: List[Tuple[int, int]] = []
        for lk, heads in payload["active_heads"].items():
            li = int(lk)
            for h in heads:
                pairs.append((li, int(h)))
        return sorted(set(pairs))

    if "mask" in payload:
        mask = np.asarray(payload["mask"])
        if mask.ndim != 2:
            return []
        coords = np.argwhere(mask > 0)
        return sorted((int(i), int(j)) for i, j in coords)

    return []


def _load_reference_masks(mask_dir: Path, pattern: str) -> Dict[str, ReferenceMask]:
    selected = _latest_masks_by_snippet(mask_dir, pattern)
    out: Dict[str, ReferenceMask] = {}
    for snippet, path in sorted(selected.items()):
        payload = json.loads(path.read_text(encoding="utf-8"))
        pairs = _mask_pairs_from_payload(payload)
        if not pairs:
            continue
        agree = np.asarray(payload.get("agree_mean", []), dtype=np.float64)
        if agree.ndim != 2:
            continue
        meta = payload.get("meta", {})
        ref_model = str(meta.get("model_name", ""))
        out[snippet] = ReferenceMask(
            snippet=snippet,
            path=path,
            active_pairs=pairs,
            agree_mean=agree,
            model_name=ref_model,
        )
    return out


def _mean_on_pairs(matrix: np.ndarray, pairs: Sequence[Tuple[int, int]]) -> float:
    vals: List[float] = []
    n_layers, n_heads = matrix.shape
    for li, hi in pairs:
        if 0 <= li < n_layers and 0 <= hi < n_heads:
            vals.append(float(matrix[li, hi]))
    return float(np.mean(vals)) if vals else 0.0


def _complement_pairs(shape: Tuple[int, int], pairs: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    s = set((int(i), int(j)) for i, j in pairs)
    n_layers, n_heads = shape
    out: List[Tuple[int, int]] = []
    for i in range(n_layers):
        for j in range(n_heads):
            if (i, j) not in s:
                out.append((i, j))
    return out


def _summary(values: Sequence[float]) -> Tuple[float, float]:
    vals = list(values)
    if not vals:
        return 0.0, 0.0
    if len(vals) == 1:
        return float(vals[0]), 0.0
    arr = np.asarray(vals, dtype=np.float64)
    return float(arr.mean()), float(arr.std(ddof=0))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare per-head prior agreement on Step-4 steered heads. "
            "Reference heads come from existing coder mask JSON files."
        )
    )
    parser.add_argument(
        "--target-model-name",
        type=str,
        default="Qwen/Qwen2.5-7B-Instruct",
        help="Model to evaluate on reference steered heads (e.g., plain Qwen2.5).",
    )
    parser.add_argument(
        "--mask-dir",
        type=Path,
        default=resolve_head_mask_root(PROJECT_ROOT),
        help="Directory with Step-4 mask files.",
    )
    parser.add_argument(
        "--mask-glob",
        type=str,
        default="step4-l2-ast-b0p1-*.json",
        help="Glob for selecting reference Step-4 mask files.",
    )
    parser.add_argument(
        "--prior",
        choices=["human", "ast", "lex", "rand", "uniform", "cfg", "slice"],
        default="ast",
        help="Prior used while collecting target model head agreement.",
    )
    parser.add_argument("--runs-per-snippet", type=int, default=1, help="Generations per snippet.")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--n-bins", type=int, default=12)
    parser.add_argument("--cache-dir", type=str, default=None)
    parser.add_argument("--gpus", type=int, default=None)
    parser.add_argument("--gpu-ids", type=str, default=None)
    parser.add_argument(
        "--instruction",
        type=str,
        default=(
            "You will analyze the Java program provided below. "
            "First, explain how you will predict the output for the code snippet. "
            "Then, simulate it as a compiler would and print the exact console output."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=resolve_alignment_outputs_root(PROJECT_ROOT),
    )
    args = parser.parse_args()

    mask_dir = args.mask_dir
    if not mask_dir.is_absolute():
        mask_dir = resolve_artifact_path(PROJECT_ROOT, mask_dir)
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = resolve_artifact_path(PROJECT_ROOT, output_dir)

    gpu_ids = _parse_gpu_ids(args.gpu_ids)
    if gpu_ids is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in gpu_ids)

    refs = _load_reference_masks(mask_dir, args.mask_glob)
    if not refs:
        raise RuntimeError(f"No reference masks found in {mask_dir} with glob '{args.mask_glob}'.")

    steering_cfg = SteeringConfig(
        enabled_levels=[1],
        prior=args.prior,
        n_bins=args.n_bins,
        beta_bias=0.0,
        beta_post=0.0,
        decode_only=True,
        only_first_decode_step=False,
        recency_mix=True,
        collect_head_stats=True,
        collect_head_stats_first_decode_only=True,
        split_prefill=True,
    )

    max_devices = None
    if gpu_ids is not None:
        if torch.cuda.is_available():
            max_devices = min(len(gpu_ids), torch.cuda.device_count())
    elif args.gpus is not None and torch.cuda.is_available():
        max_devices = min(max(1, args.gpus), torch.cuda.device_count())

    runner = ModelRunner()
    runner.set_steering_config(steering_cfg)
    runner.login_hf()
    runner.config(
        model_name=args.target_model_name,
        cache_dir=args.cache_dir,
        key_scope="prompt",
        max_devices=max_devices,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
    )
    runner.build()

    rows: List[dict] = []
    try:
        snippets = sorted(refs.keys())
        total_jobs = len(snippets) * max(1, args.runs_per_snippet)
        done = 0
        for snippet in snippets:
            ref = refs[snippet]
            source_root = resolve_eyetracking_source_root(PROJECT_ROOT)
            source_path = source_root / f"{snippet}.java"
            if not source_path.is_file():
                print(f"[WARN] missing source for snippet={snippet}, skipping")
                continue
            code = source_path.read_text(encoding="utf-8")

            agg_sum = None
            agg_count = None
            valid = 0
            for _ in range(max(1, args.runs_per_snippet)):
                result = runner.run_llama(
                    code,
                    instruction=args.instruction,
                    language="java",
                    record_layers=False,
                    record_attention=False,
                )
                hs = (result.get("steering_debug") or {}).get("head_stats")
                done += 1
                if done % 8 == 0 or done == total_jobs:
                    print(f"[progress] {done}/{total_jobs}")
                if not hs:
                    continue
                run_sum = np.asarray(hs.get("sum", []), dtype=np.float64)
                run_count = np.asarray(hs.get("count", []), dtype=np.float64)
                if run_sum.ndim != 2 or run_count.ndim != 2:
                    continue
                if agg_sum is None:
                    agg_sum = np.zeros_like(run_sum, dtype=np.float64)
                    agg_count = np.zeros_like(run_count, dtype=np.float64)
                if agg_sum.shape != run_sum.shape:
                    raise RuntimeError(
                        f"Head stats shape mismatch for snippet={snippet}: "
                        f"{agg_sum.shape} vs {run_sum.shape}"
                    )
                agg_sum += run_sum
                agg_count += run_count
                valid += 1

            if agg_sum is None or agg_count is None or valid == 0:
                print(f"[WARN] no valid head stats for snippet={snippet}")
                continue

            with np.errstate(divide="ignore", invalid="ignore"):
                target_mean = np.divide(
                    agg_sum, np.maximum(agg_count, 1.0), where=np.maximum(agg_count, 1.0) > 0
                )

            if ref.agree_mean.shape != target_mean.shape:
                print(
                    f"[WARN] shape mismatch snippet={snippet}: "
                    f"ref={ref.agree_mean.shape} target={target_mean.shape}; skipping"
                )
                continue

            active = ref.active_pairs
            inactive = _complement_pairs(ref.agree_mean.shape, active)

            ref_active = _mean_on_pairs(ref.agree_mean, active)
            tgt_active = _mean_on_pairs(target_mean, active)
            ref_inactive = _mean_on_pairs(ref.agree_mean, inactive)
            tgt_inactive = _mean_on_pairs(target_mean, inactive)

            rows.append(
                {
                    "snippet": snippet,
                    "reference_mask_file": str(ref.path),
                    "reference_model": ref.model_name,
                    "target_model": args.target_model_name,
                    "prior": args.prior,
                    "active_heads": len(active),
                    "inactive_heads": len(inactive),
                    "ref_active_mean": ref_active,
                    "target_active_mean": tgt_active,
                    "delta_active": tgt_active - ref_active,
                    "ref_inactive_mean": ref_inactive,
                    "target_inactive_mean": tgt_inactive,
                    "delta_inactive": tgt_inactive - ref_inactive,
                    "target_minus_ref_gap": (tgt_active - tgt_inactive) - (ref_active - ref_inactive),
                }
            )
    finally:
        runner.free()

    if not rows:
        raise RuntimeError("No per-snippet alignment rows computed.")

    out_dir = output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    micro_csv = out_dir / "head_prior_alignment_micro.csv"
    summary_csv = out_dir / "head_prior_alignment_summary.csv"

    with micro_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "snippet",
            "reference_mask_file",
            "reference_model",
            "target_model",
            "prior",
            "active_heads",
            "inactive_heads",
            "ref_active_mean",
            "target_active_mean",
            "delta_active",
            "ref_inactive_mean",
            "target_inactive_mean",
            "delta_inactive",
            "target_minus_ref_gap",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    da = [float(r["delta_active"]) for r in rows]
    di = [float(r["delta_inactive"]) for r in rows]
    dg = [float(r["target_minus_ref_gap"]) for r in rows]
    da_mean, da_std = _summary(da)
    di_mean, di_std = _summary(di)
    dg_mean, dg_std = _summary(dg)
    n = len(rows)
    t_like = 0.0
    if n > 1 and da_std > 0:
        t_like = da_mean / (da_std / math.sqrt(n))

    with summary_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "reference_model",
            "target_model",
            "prior",
            "mask_glob",
            "snippets",
            "delta_active_mean",
            "delta_active_std",
            "delta_inactive_mean",
            "delta_inactive_std",
            "gap_shift_mean",
            "gap_shift_std",
            "active_delta_t_like",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "reference_model": rows[0]["reference_model"],
                "target_model": args.target_model_name,
                "prior": args.prior,
                "mask_glob": args.mask_glob,
                "snippets": n,
                "delta_active_mean": f"{da_mean:.6f}",
                "delta_active_std": f"{da_std:.6f}",
                "delta_inactive_mean": f"{di_mean:.6f}",
                "delta_inactive_std": f"{di_std:.6f}",
                "gap_shift_mean": f"{dg_mean:.6f}",
                "gap_shift_std": f"{dg_std:.6f}",
                "active_delta_t_like": f"{t_like:.6f}",
            }
        )

    print("\n[Head Prior Alignment Summary]")
    print(f"reference_model : {rows[0]['reference_model']}")
    print(f"target_model    : {args.target_model_name}")
    print(f"prior           : {args.prior}")
    print(f"mask_glob       : {args.mask_glob}")
    print(f"snippets        : {n}")
    print(f"delta_active    : {da_mean:+.6f} ± {da_std:.6f}  (target - reference)")
    print(f"delta_inactive  : {di_mean:+.6f} ± {di_std:.6f}")
    print(f"gap_shift       : {dg_mean:+.6f} ± {dg_std:.6f}")
    print(f"t_like(active)  : {t_like:+.6f}")
    print(f"[INFO] micro csv   -> {micro_csv}")
    print(f"[INFO] summary csv -> {summary_csv}")


if __name__ == "__main__":
    main()
