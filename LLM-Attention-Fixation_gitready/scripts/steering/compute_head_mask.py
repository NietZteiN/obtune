#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models import ModelRunner
from steering import SteeringConfig
from paths import (
    resolve_artifact_path,
    resolve_eyetracking_source_root,
    resolve_head_mask_root,
)


def _parse_gpu_ids(raw: Optional[str]) -> Optional[List[int]]:
    if not raw:
        return None
    parts = re.split(r"[+,]", raw.strip())
    ids: List[int] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if not p.isdigit():
            raise ValueError(f"Invalid GPU id '{p}' in --gpu-ids={raw!r}")
        ids.append(int(p))
    return ids or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute per-layer steerable head mask from agreement stats.")
    parser.add_argument("--snippet", required=True, help="Snippet name (without .java), e.g., Ackerman")
    parser.add_argument("--runs", type=int, default=50, help="Number of generations to aggregate")
    parser.add_argument("--topk-per-layer", type=int, default=4, help="Top-k heads selected per layer")
    parser.add_argument(
        "--prior",
        choices=["human", "ast", "lex", "rand", "uniform", "cfg", "slice"],
        default="uniform",
        help="Prior used to build p_all while collecting agreement stats.",
    )
    parser.add_argument("--human-file", type=Path, default=None)
    parser.add_argument("--lex-window", type=int, default=32)
    parser.add_argument("--rand-seed", type=int, default=None)
    parser.add_argument("--n-bins", type=int, default=12)
    parser.add_argument("--model-name", type=str, default="Qwen/Qwen2.5-Coder-7B-Instruct")
    parser.add_argument("--cache-dir", type=str, default=None)
    parser.add_argument("--gpus", type=int, default=None)
    parser.add_argument("--gpu-ids", type=str, default=None)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--beta-bias", type=float, default=0.0)
    parser.add_argument("--beta-post", type=float, default=0.0)
    parser.add_argument(
        "--collect-first-decode-only",
        choices=["on", "off"],
        default="on",
        help="Collect only first decode step (kv_len == prompt_len).",
    )
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
        "--output-mask",
        type=Path,
        default=None,
        help="Optional output JSON path. Relative paths are rooted under artifact root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gpu_ids = _parse_gpu_ids(args.gpu_ids)
    if gpu_ids is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in gpu_ids)

    source_root = resolve_eyetracking_source_root(PROJECT_ROOT)
    source_path = source_root / f"{args.snippet}.java"
    if not source_path.is_file():
        raise FileNotFoundError(f"Snippet not found: {source_path}")
    code = source_path.read_text(encoding="utf-8")

    steering_cfg = SteeringConfig(
        enabled_levels=[1],  # install steering hooks; stats collector is backend-side.
        prior=args.prior,
        n_bins=args.n_bins,
        beta_bias=args.beta_bias,
        beta_post=args.beta_post,
        human_file=args.human_file,
        lex_window=args.lex_window,
        rand_seed=args.rand_seed,
        decode_only=True,
        only_first_decode_step=False,
        recency_mix=True,
        collect_head_stats=True,
        collect_head_stats_first_decode_only=(args.collect_first_decode_only == "on"),
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
        model_name=args.model_name,
        cache_dir=args.cache_dir,
        key_scope="prompt",
        max_devices=max_devices,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
    )
    runner.build()

    agg_sum = None
    agg_count = None
    completed = 0

    try:
        for run_idx in range(1, max(1, args.runs) + 1):
            result = runner.run_llama(
                code,
                instruction=args.instruction,
                language="java",
                record_layers=False,
                record_attention=False,
            )
            hs = (result.get("steering_debug") or {}).get("head_stats")
            if not hs:
                print(f"[WARN] run={run_idx:03d}: missing head_stats; skipping")
                continue

            run_sum = np.asarray(hs.get("sum", []), dtype=np.float64)
            run_count = np.asarray(hs.get("count", []), dtype=np.float64)
            if run_sum.ndim != 2 or run_count.ndim != 2:
                print(f"[WARN] run={run_idx:03d}: invalid head_stats shape; skipping")
                continue

            if agg_sum is None:
                agg_sum = np.zeros_like(run_sum, dtype=np.float64)
                agg_count = np.zeros_like(run_count, dtype=np.float64)
            if agg_sum.shape != run_sum.shape:
                raise ValueError(
                    f"Inconsistent head stat shapes: aggregated={agg_sum.shape} run={run_sum.shape}"
                )

            agg_sum += run_sum
            agg_count += run_count
            completed += 1
            if run_idx % 5 == 0 or run_idx == args.runs:
                print(f"[INFO] completed {run_idx}/{args.runs} runs (valid={completed})")
    finally:
        runner.free()

    if agg_sum is None or agg_count is None or completed == 0:
        raise RuntimeError("No valid head statistics collected.")

    with np.errstate(divide="ignore", invalid="ignore"):
        mean = np.divide(agg_sum, np.maximum(agg_count, 1.0), where=np.maximum(agg_count, 1.0) > 0)

    num_layers, num_heads = mean.shape
    k = max(1, min(int(args.topk_per_layer), num_heads))
    mask = np.zeros((num_layers, num_heads), dtype=np.int32)
    active_heads: dict[str, list[int]] = {}

    for li in range(num_layers):
        layer_count = agg_count[li]
        candidates = np.where(layer_count > 0)[0]
        if candidates.size == 0:
            continue
        layer_scores = mean[li, candidates]
        order = np.argsort(-layer_scores)
        selected = candidates[order[: min(k, candidates.size)]].astype(int).tolist()
        if not selected:
            continue
        mask[li, selected] = 1
        active_heads[str(li)] = selected

    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.model_name)
    out_path = args.output_mask
    if out_path is None:
        out_dir = resolve_head_mask_root(PROJECT_ROOT)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_model}-{args.snippet}-topk{k}.json"
    else:
        out_path = resolve_artifact_path(PROJECT_ROOT, out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "snippet": args.snippet,
            "model_name": args.model_name,
            "prior": args.prior,
            "runs_requested": int(args.runs),
            "runs_valid": int(completed),
            "topk_per_layer": int(k),
            "collect_first_decode_only": bool(args.collect_first_decode_only == "on"),
            "beta_bias": float(args.beta_bias),
            "beta_post": float(args.beta_post),
        },
        "shape": [int(num_layers), int(num_heads)],
        "mask": mask.tolist(),
        "active_heads": active_heads,
        "agree_mean": mean.tolist(),
        "agree_sum": agg_sum.tolist(),
        "agree_count": agg_count.astype(np.int64).tolist(),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[DONE] Wrote head mask -> {out_path}")
    print(f"[DONE] active heads: {int(mask.sum())} / {int(mask.size)}")


if __name__ == "__main__":
    main()
