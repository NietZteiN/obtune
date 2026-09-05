#!/usr/bin/env python
"""What actually works best, per obfuscation condition and on the held-out obfuscator.

Every ranking table in this project has invited the same error: two systems "about a point"
apart get read as an ordering when only one of the two gaps is real (log/transfer 2026-09-03).
So this script ranks, and then immediately asks of each ranking whether it survives an
interval -- both against the LEADER of its own column and against `tuned_L0`, the clean-code
control the project reads everything against.

Scope: CodeLlama-7b, python, Grid A (`heldout`), greedy decoding. Phases pooled are the
greedy Grid A ones; `mole_generic_testset` is excluded because it is Grid B (a different
program set -- CLAUDE.md forbids pooling) and `selfcons_generic` because it is T=0.7 sampling
rather than greedy. Where a system exists in several phases the cell with the most items wins
and the spread across phases is reported, so a duplicate can never silently change a ranking.

Items are intersected across every system in a column before anything is compared, so each
column is one program set. H1 comes from `h1_codellama` (already-spent reads; no new budget).

Writes results/analysis/best_per_condition_2026-09-04.json.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.config import RESULTS_DIR  # noqa: E402
from obtune.control_relative import bootstrap_delta  # noqa: E402

CELLS = RESULTS_DIR / "cells"
MODEL = "codellama-7b"
GREEDY_GRID_A = ["rq1_generic", "rq2_generic", "loto_generic", "mole_generic",
                 "merge_sweep_generic", "rank_generic", "extra_generic", "baselines_generic"]
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
NBOOT, TOPK = 2000, 6


def collect(cond: str, phases: list[str], model: str = MODEL) -> dict[str, pd.DataFrame]:
    """One frame per system for this condition, deduped across phases by item count."""
    best: dict[str, tuple[int, str, pd.DataFrame]] = {}
    spread: dict[str, list] = defaultdict(list)
    for ph in phases:
        root = CELLS / ph / model / "python"
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if not d.name.endswith(f"__{cond}"):
                continue
            p = d / "trials.parquet"
            if not p.exists():
                continue
            name = d.name.rsplit("__", 1)[0]
            df = pd.read_parquet(p, columns=["item_id", "snippet_id", "correct"])
            spread[name].append((ph, round(float(df["correct"].mean()), 4)))
            if name not in best or len(df) > best[name][0]:
                best[name] = (len(df), ph, df)
    return {k: v[2] for k, v in best.items()}, {k: v[1] for k, v in best.items()}, dict(spread)


def rank(frames: dict[str, pd.DataFrame], control: str = "tuned_L0") -> dict:
    common = set.intersection(*[set(df["item_id"]) for df in frames.values()])
    sub = {k: df[df["item_id"].isin(common)].sort_values("item_id") for k, df in frames.items()}
    order = sorted(sub, key=lambda k: -float(sub[k]["correct"].mean()))
    out = {"n_items": len(common),
           "n_programs": int(next(iter(sub.values()))["snippet_id"].nunique()),
           "n_systems": len(sub),
           "acc": {k: round(float(sub[k]["correct"].mean()), 4) for k in order},
           "vs_leader": {}, "vs_control": {}}
    leader = order[0]
    out["leader"] = leader
    for k in order[:TOPK]:
        if k != leader:
            out["vs_leader"][k] = bootstrap_delta(sub[k], sub[leader], k, n_resamples=NBOOT).to_dict()
        if control in sub and k != control:
            out["vs_control"][k] = bootstrap_delta(sub[k], sub[control], k, n_resamples=NBOOT).to_dict()
    return out


def main() -> int:
    report = {"model": MODEL, "grid": "A/heldout", "decoding": "greedy",
              "phases": GREEDY_GRID_A, "n_boot": NBOOT, "conditions": {}, "H1": {}}

    for cond in CONDS:
        frames, src, spread = collect(cond, GREEDY_GRID_A)
        r = rank(frames)
        r["source_phase"] = src
        r["cross_phase_spread"] = {k: v for k, v in spread.items() if len(v) > 1}
        report["conditions"][cond] = r
        print(f"\n=== {cond}  ({r['n_systems']} systems, {r['n_items']} items, "
              f"{r['n_programs']} programs) ===")
        for i, (k, a) in enumerate(list(r["acc"].items())[:TOPK]):
            vl = r["vs_leader"].get(k)
            vc = r["vs_control"].get(k)
            tag = ""
            if vl:
                tag += f"  vs leader {vl['value_pts']:+.2f} [{vl['ci_lo']:+.2f}, {vl['ci_hi']:+.2f}]"
                tag += "*" if vl["excludes_zero"] else " "
            if vc:
                tag += f"   vs tuned_L0 {vc['value_pts']:+.2f}"
                tag += "*" if vc["excludes_zero"] else ""
            print(f"  {i+1}. {k:24s} {a:.4f}{tag}")

    # H1 -- one phase, one grid, already-spent reads.
    frames, src, _ = collect("H1", ["h1_codellama"])
    r = rank(frames)
    r["source_phase"] = src
    report["H1"] = r
    print(f"\n=== H1  ({r['n_systems']} systems, {r['n_items']} items, {r['n_programs']} programs) ===")
    for i, (k, a) in enumerate(r["acc"].items()):
        vl = r["vs_leader"].get(k)
        tag = ""
        if vl:
            tag = (f"  vs leader {vl['value_pts']:+.2f} [{vl['ci_lo']:+.2f}, {vl['ci_hi']:+.2f}]"
                   + ("*" if vl["excludes_zero"] else ""))
        print(f"  {i+1}. {k:24s} {a:.4f}{tag}")

    out = RESULTS_DIR / "analysis" / "best_per_condition_2026-09-04.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}   (* = interval excludes zero)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
