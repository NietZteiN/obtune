#!/usr/bin/env python
"""`oracle_bestof8` — the upper bound on any hard router. ZERO GPU.

For each item, take the best of the eight per-condition experts. No router can beat this: it is
what a router with a perfect PER-ITEM oracle would score. The learned router is per-CONDITION and
already 100% accurate at that (master report §1.5.3), so the gap between the two is the entire
remaining headroom for routing — the quantity Part III's Gate 1 is defined against.

Computed from cells already on disk, so it costs nothing. It is labelled an ORACLE and is never a
deployable system: choosing per item requires knowing which expert was right, which requires the
answer. It bounds the achievable, which is what an upper bound is for.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
EXPERTS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"]


def main() -> int:
    import pandas as pd

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--grid", default="main")
    args = ap.parse_args()

    G = ROOT / "results" / "cells" / args.grid / args.model / args.language
    conds = sorted({p.name.rsplit("__", 1)[1] for p in G.glob("*__*") if p.is_dir()})
    out, skipped = {}, {}
    for cond in conds:
        frames = {}
        for e in EXPERTS:
            f = G / f"tuned_{e}__{cond}" / "trials.parquet"
            if f.exists():
                d = pd.read_parquet(f, columns=["item_id", "correct"])
                frames[e] = d.set_index("item_id")["correct"]
        if len(frames) < 2:
            skipped[cond] = f"only {len(frames)} expert cell(s): {sorted(frames)}"
            continue
        # Cells of DIFFERENT lengths mean the experts were scored on different grids
        # (Grid A `heldout` n=1670 vs Grid B `testset` n=176), which CLAUDE.md forbids
        # pooling. The inner join below would silently reduce to the intersection and
        # report a headroom computed on whatever programs happened to overlap.
        sizes = {e: int(len(s)) for e, s in frames.items()}
        if len(set(sizes.values())) > 1:
            skipped[cond] = f"expert cells span >1 grid, refusing to pool: {sizes}"
            continue
        df = pd.DataFrame(frames).dropna()
        if df.empty:
            skipped[cond] = f"no item_id shared by all {len(frames)} expert cells"
            continue
        if len(df) < min(sizes.values()):
            # Same length but different items — also a pooling hazard, just a subtler one.
            skipped[cond] = (f"experts agree on only {len(df)} of {min(sizes.values())} "
                             f"items; item sets differ")
            continue
        best = float(df.max(axis=1).mean())          # per ITEM: did ANY expert get it right?
        best_single = float(df.mean().max())         # the best single expert on this condition
        out[cond] = {"oracle_bestof8": best, "best_single_expert": best_single,
                     "headroom_pts": (best - best_single) * 100,
                     "n_items": int(len(df)), "n_experts": int(df.shape[1])}
    if not out:
        print("no condition produced a usable bound. Reasons:")
        for c, why in sorted(skipped.items()):
            print(f"  {c:12s} {why}")
        return 1
    dest = ROOT / "results" / "analysis" / f"oracle_bestof8_{args.model}_{args.language}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"bounds": out, "skipped": skipped}, indent=2))
    print(f"  {'condition':11s}{'best-of-8':>11s}{'best single':>13s}{'headroom':>11s}{'n':>7s}")
    for c, v in sorted(out.items()):
        print(f"  {c:11s}{v['oracle_bestof8']:>11.3f}{v['best_single_expert']:>13.3f}"
              f"{v['headroom_pts']:>10.1f}p{v['n_items']:>7d}")
    print(f"\nwrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
