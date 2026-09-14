#!/usr/bin/env python3
"""
Baseline human–model alignment computed directly from attn_viz model_output.json files.

Walks:
  attn_viz/<snippet>/baseline/none/{EM,Mismatch}/*/model_output.json
and human timelines:
  fixation_dump/<snippet>/participant_*.json

For each participant/snippet/run:
  - Build human timeline matrix of shape [T, V] (T = frames, V = vocabulary length), normalized per frame.
  - Build model timeline matrices for pools: all_layers_mean, last_layer, binned into T intervals over generated steps.
  - Compute metrics (cosine, Spearman, JS divergence, dispersion) on flattened matrices (matrix) and on time-averaged vectors (vector).

Outputs:
  eval/baseline_attn_per_run.csv  (rows per run/participant/pool, for both matrix & vector)
  eval/baseline_attn_summary_matrix.csv
  eval/baseline_attn_summary_vector.csv
and prints summary tables. Config column shows the pool (all_layers_mean or last_layer).
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path
import argparse
from typing import Dict, List, Tuple

import numpy as np

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover
    def tqdm(x, **kwargs):
        return x

try:
    from scipy.stats import rankdata
except Exception:  # pragma: no cover
    rankdata = None


# ----------------- utilities -----------------

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if a.size != b.size or a.size == 0:
        return 0.0
    if rankdata is not None:
        ra = rankdata(a)
        rb = rankdata(b)
    else:
        ra = np.argsort(np.argsort(a))
        rb = np.argsort(np.argsort(b))
    return _cosine(ra - ra.mean(), rb - rb.mean())


def _js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = p.astype(float)
    q = q.astype(float)
    p = p / p.sum() if p.sum() > 0 else np.full_like(p, 1.0 / len(p))
    q = q / q.sum() if q.sum() > 0 else np.full_like(q, 1.0 / len(q))
    m = 0.5 * (p + q)

    def _kl(x, y):
        mask = (x > 0) & (y > 0)
        if not np.any(mask):
            return 0.0
        return float(np.sum(x[mask] * np.log2(x[mask] / y[mask])))

    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def _mean_std(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.pstdev(values)


# ----------------- data loaders -----------------

def load_human_timeline(participant_file: Path) -> Tuple[np.ndarray, List[str]]:
    data = json.loads(participant_file.read_text(encoding="utf-8"))
    vocab = [entry["Token"] for entry in data.get("vocabulary", [])]
    timeline = data.get("timeline", [])
    if not vocab or not timeline:
        return np.zeros((0, 0)), []
    T = len(timeline)
    V = len(vocab)
    mat = np.zeros((T, V), dtype=float)
    for t_idx, frame in enumerate(timeline):
        for i, entry in enumerate(frame):
            if i < V:
                mat[t_idx, i] = float(entry.get("score", 0.0))
        s = mat[t_idx].sum()
        if s > 0:
            mat[t_idx] /= s
    return mat, vocab


def build_model_matrix(model_output: dict, pool: str, vocab_len: int, num_bins: int) -> np.ndarray:
    steps = model_output.get("pooled_attention_by_generated_token", [])
    if not steps or num_bins <= 0 or vocab_len <= 0:
        return np.zeros((0, 0))
    # collect per-step prompt scores for the pool
    per_step = []
    for step in steps:
        scores = step.get("prompt_scores", {}).get(pool)
        if not scores:
            continue
        vec = np.asarray(scores, dtype=float)
        if vec.size < vocab_len:
            vec = np.pad(vec, (0, vocab_len - vec.size))
        elif vec.size > vocab_len:
            vec = vec[:vocab_len]
        s = vec.sum()
        if s > 0:
            vec = vec / s
        per_step.append(vec)
    if not per_step:
        return np.zeros((0, 0))
    per_step = np.stack(per_step, axis=0)  # [num_steps, vocab_len]
    num_steps = per_step.shape[0]
    bins = np.linspace(0, num_steps, num_bins + 1, dtype=int)
    mat = np.zeros((num_bins, vocab_len), dtype=float)
    for b in range(num_bins):
        start, end = bins[b], bins[b + 1]
        if end <= start:
            continue
        slice_vec = per_step[start:end].mean(axis=0)
        s = slice_vec.sum()
        if s > 0:
            slice_vec = slice_vec / s
        mat[b] = slice_vec
    return mat


# ----------------- aggregation & reporting -----------------

def summarize_rows(rows: List[Dict[str, str | float]], kind: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "phase",
        "config",
        "spearman_mean",
        "spearman_std",
        "cosine_mean",
        "cosine_std",
        "js_mean",
        "js_std",
        "dispersion_mean",
        "dispersion_std",
        "n",
    ]
    grouped: Dict[Tuple[str, str], List[Dict[str, str | float]]] = {}
    for r in rows:
        if r["kind"] != kind:
            continue
        key = (r["phase"], r["config"])
        grouped.setdefault(key, []).append(r)

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for (phase, config), items in sorted(grouped.items()):
            s_vals = [float(x["spearman"]) for x in items]
            c_vals = [float(x["cosine"]) for x in items]
            j_vals = [float(x["js"]) for x in items]
            d_vals = [float(x["dispersion"]) for x in items]
            s_mean, s_std = _mean_std(s_vals)
            c_mean, c_std = _mean_std(c_vals)
            j_mean, j_std = _mean_std(j_vals)
            d_mean, d_std = _mean_std(d_vals)
            n_snip = len(items)
            writer.writerow(
                {
                    "phase": phase,
                    "config": config,
                    "spearman_mean": f"{s_mean:.4f}",
                    "spearman_std": f"{s_std:.4f}",
                    "cosine_mean": f"{c_mean:.4f}",
                    "cosine_std": f"{c_std:.4f}",
                    "js_mean": f"{j_mean:.4f}",
                    "js_std": f"{j_std:.4f}",
                    "dispersion_mean": f"{d_mean:.4f}",
                    "dispersion_std": f"{d_std:.4f}",
                    "n": n_snip,
                }
            )


def print_table(path: Path, title: str) -> None:
    if not path.is_file():
        print(f"{title}: no data")
        return
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        print(f"{title}: no data")
        return
    print(f"\n{title}")
    print("Phase     | Config           | Spearman (mean±std) | Cosine (mean±std) | JS (mean±std) | Dispersion (mean±std) | n")
    print("-" * 118)
    for r in rows:
        print(
            f"{r['phase']:<9} | {r['config']:<15} | "
            f"{float(r['spearman_mean']):.2f} ± {float(r['spearman_std']):.2f} | "
            f"{float(r['cosine_mean']):.2f} ± {float(r['cosine_std']):.2f} | "
            f"{float(r['js_mean']):.2f} ± {float(r['js_std']):.2f} | "
            f"{float(r['dispersion_mean']):.2f} ± {float(r['dispersion_std']):.2f} | "
            f"{r['n']}"
        )


# ----------------- main pipeline -----------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline alignment from model_output.json.")
    parser.add_argument("--model-name", type=str, default=None, help="Model name for attn_viz/<model> lookup.")
    parser.add_argument("--model-dir", type=str, default=None, help="Explicit attn_viz/<model_dir> override.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    from paths import resolve_attn_root, model_dir_name, resolve_eval_root
    model_dir = args.model_dir or (model_dir_name(args.model_name) if args.model_name else None)
    attn_root = resolve_attn_root(project_root, model_dir)
    fixation_root = project_root / "fixation_dump"
    out_dir = resolve_eval_root(project_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    pools = ["all_layers_mean", "last_layer"]
    rows: List[Dict[str, str | float]] = []

    snippet_dirs = sorted([p for p in attn_root.iterdir() if p.is_dir()])
    for snippet_dir in tqdm(snippet_dirs, desc="Snippets", total=len(snippet_dirs)):
        snippet = snippet_dir.name
        human_dir = fixation_root / snippet
        if not human_dir.is_dir():
            continue
        participant_files = sorted(human_dir.glob("participant_*.json"))
        if not participant_files:
            continue

        # collect all baseline runs for this snippet
        run_paths: List[Path] = []
        base_dir = snippet_dir / "baseline" / "none"
        for status in ("EM", "Mismatch"):
            status_dir = base_dir / status
            if not status_dir.is_dir():
                continue
            for run_dir in status_dir.iterdir():
                mo_path = run_dir / "model_output.json"
                if mo_path.is_file():
                    run_paths.append(mo_path)
        if not run_paths:
            continue

        # preload model outputs with a per-snippet progress bar
        model_outputs = []
        for mo_path in tqdm(run_paths, desc=f"{snippet} runs", leave=False):
            try:
                model_outputs.append(json.loads(mo_path.read_text(encoding="utf-8")))
            except Exception:
                continue

        for participant_file in participant_files:
            human_mat, vocab_tokens = load_human_timeline(participant_file)
            if human_mat.size == 0:
                continue
            T, V = human_mat.shape
            human_flat = human_mat.flatten()
            human_vec = human_mat.mean(axis=0)

            for mo in model_outputs:
                for pool in pools:
                    model_mat = build_model_matrix(mo, pool, V, T)
                    if model_mat.size == 0:
                        continue
                    model_flat = model_mat.flatten()
                    model_vec = model_mat.mean(axis=0)
                    # matrix metrics
                    rows.append(
                        {
                            "participant": participant_file.stem,
                            "snippet": snippet,
                            "phase": "timeline",
                            "kind": "matrix",
                            "config": pool,
                            "spearman": _spearman(human_flat, model_flat),
                            "cosine": _cosine(human_flat, model_flat),
                            "js": _js_divergence(human_flat, model_flat),
                            "dispersion": float(model_flat.var()),
                        }
                    )
                    # vector metrics
                    rows.append(
                        {
                            "participant": participant_file.stem,
                            "snippet": snippet,
                            "phase": "timeline",
                            "kind": "vector",
                            "config": pool,
                            "spearman": _spearman(human_vec, model_vec),
                            "cosine": _cosine(human_vec, model_vec),
                            "js": _js_divergence(human_vec, model_vec),
                            "dispersion": float(model_vec.var()),
                        }
                    )

    if not rows:
        print("No alignment rows computed.")
        return

    per_run_path = out_dir / "baseline_attn_per_run.csv"
    fieldnames = ["participant", "snippet", "phase", "kind", "config", "spearman", "cosine", "js", "dispersion"]
    with per_run_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    summary_matrix = out_dir / "baseline_attn_summary_matrix.csv"
    summary_vector = out_dir / "baseline_attn_summary_vector.csv"
    summarize_rows(rows, kind="matrix", out_path=summary_matrix)
    summarize_rows(rows, kind="vector", out_path=summary_vector)

    print(f"Wrote per-run metrics to {per_run_path}")
    print_table(summary_matrix, "Matrix (time-dependent) – all_layers_mean vs last_layer")
    print_table(summary_vector, "Vector (time-independent) – all_layers_mean vs last_layer")


if __name__ == "__main__":
    main()
