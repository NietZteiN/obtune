#!/usr/bin/env python
"""Item-level agreement between systems on ONE condition. ZERO GPU.

Two systems can score the same accuracy in two very different ways: by succeeding on the same
items, or by succeeding on different ones. Only the second leaves headroom for any combination
method. `merge_dare_ties` (.348) and `tuned_L0_k0` (.339) tie on H1 (MASTER_REPORT §11.3), and
that tie is the sharpest statement of §5's negative result — but a tie in the MARGIN says nothing
about the OVERLAP, and the negative result is much stronger if the overlap is near-total than if
the two systems are solving disjoint halves of the problem.

This is the missing measurement. For every pair of systems it reports the 2x2 concordance table,
an exact McNemar test on the discordant pairs, Jaccard overlap of the correct-sets, and for the
whole system set the ORACLE-of-k (per item, did ANY system get it right) — the ceiling that no
selection rule can beat.

Distinct from `20_oracle_bestof8.py`, which bounds a *router* over the eight per-condition experts
and therefore hardcodes `tuned_{L0..S4}`. That script skips almost everything on H1 (only one
expert cell exists) and on the trainable conditions (the expert cells span two grids). This one
takes an arbitrary system list on one condition, which is what the H1 ladder needs.

    python scripts/analysis/24_item_agreement.py --condition H1
    python scripts/analysis/24_item_agreement.py --condition H1 --systems base tuned_L0_k0 merge_dare_ties

GRID SAFETY. Cells of different lengths mean the systems were scored on different grids (Grid A
`heldout` n=1214 vs Grid B `testset` n=115), which CLAUDE.md forbids pooling. Rather than joining
on item_id and silently reporting whatever overlapped, this refuses any system whose item set is
not identical to the modal one, and names it in `skipped`. The Grid A and Grid B H1 ladders are
therefore separate invocations, which is the point.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

#: The Grid B (testset) H1 ladder — every system whose H1 cell carries the same 115 item_ids.
#: MASTER_REPORT §11.3 verified the set equality; `--systems` overrides this default.
DEFAULT_SYSTEMS = [
    "base",
    "norm_full",
    "oracle_prompt_1shot",
    "icl_k1",
    "icl_k2",
    "merge_ties",
    "merge_dare_ties",
    "l0merge_ties",
    "l0merge_dare_ties",
    "mole_router",
    "mole_hardrouter",
    "tuned_L0_k0",
]


def load_cells(grid_root: Path, systems: list[str], cond: str):
    """system -> Series(item_id -> correct), plus a reason string for every system dropped."""
    import pandas as pd

    frames, skipped = {}, {}
    for s in systems:
        f = grid_root / f"{s}__{cond}" / "trials.parquet"
        if not f.exists():
            skipped[s] = "no cell"
            continue
        d = pd.read_parquet(f, columns=["item_id", "correct"])
        if d["item_id"].duplicated().any():
            # Would silently reindex to a cartesian product below.
            skipped[s] = f"duplicate item_ids ({int(d['item_id'].duplicated().sum())})"
            continue
        frames[s] = d.set_index("item_id")["correct"].astype(int)
    return frames, skipped


def enforce_one_grid(frames: dict, skipped: dict):
    """Drop any system whose item set differs from the modal one. See the GRID SAFETY note."""
    from collections import Counter

    if not frames:
        return frames
    sig = {s: frozenset(v.index) for s, v in frames.items()}
    modal, _ = Counter(sig.values()).most_common(1)[0]
    for s in list(frames):
        if sig[s] != modal:
            skipped[s] = (
                f"item set differs from the modal one (n={len(sig[s])} vs {len(modal)}) "
                f"- almost certainly the other grid; refusing to pool"
            )
            del frames[s]
    return frames


def main() -> int:
    import pandas as pd

    from obtune.transfer import mcnemar_exact

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--phase", default="main")
    ap.add_argument("--condition", default="H1")
    ap.add_argument("--systems", nargs="*", default=None)
    ap.add_argument("--n-null", type=int, default=2000,
                    help="permutation draws for the oracle independence null")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    grid_root = ROOT / "results" / "cells" / args.phase / args.model / args.language
    systems = args.systems or DEFAULT_SYSTEMS
    frames, skipped = load_cells(grid_root, systems, args.condition)
    frames = enforce_one_grid(frames, skipped)
    if len(frames) < 2:
        print(f"need >=2 comparable cells for {args.condition}; got {len(frames)}. Reasons:")
        for s, why in sorted(skipped.items()):
            print(f"  {s:24s} {why}")
        return 1

    df = pd.DataFrame(frames)
    n = len(df)
    acc = {s: float(df[s].mean()) for s in df.columns}

    pairs = []
    for a, b in combinations(sorted(df.columns), 2):
        x, y = df[a].values, df[b].values
        both = int(((x == 1) & (y == 1)).sum())
        a_only = int(((x == 1) & (y == 0)).sum())   # a right, b wrong
        b_only = int(((x == 0) & (y == 1)).sum())
        neither = int(((x == 0) & (y == 0)).sum())
        union = both + a_only + b_only
        pairs.append({
            "a": a, "b": b,
            "acc_a": acc[a], "acc_b": acc[b],
            "both": both, "a_only": a_only, "b_only": b_only, "neither": neither,
            # Jaccard over the CORRECT-sets: 1.0 = identical behaviour, 0.0 = disjoint.
            "jaccard": (both / union) if union else float("nan"),
            "oracle_of_2": union / n,
            # Headroom an oracle over just these two would buy over the better of them.
            "oracle_gain_pts": (union / n - max(acc[a], acc[b])) * 100,
            "mcnemar_p": mcnemar_exact(a_only, b_only),
        })

    # Per item: did ANY system get it right? No selection rule over this set can beat it.
    oracle_all = float(df.max(axis=1).mean())
    best_single = max(acc.values())

    # THE ORACLE NUMBER IS MEANINGLESS WITHOUT THIS NULL, so it is computed here rather than
    # left to the reader. An oracle-of-k rises mechanically with k even for systems that carry
    # no complementary skill at all: k independent coins each landing 1/3 cover 1-(2/3)^k of the
    # items. The null permutes each system's correct-vector independently, which preserves every
    # marginal accuracy exactly and destroys only the item-difficulty coupling. Real systems are
    # positively coupled (easy items are easy for everyone), so the observed oracle should sit
    # BELOW this null; how far below is the actual measure of redundancy. An observed oracle at
    # or above the null would be the complementarity finding. Reporting `oracle - best_single`
    # on its own invites exactly the wrong conclusion.
    import numpy as np

    rng = np.random.default_rng(17)
    cols = [df[s].values for s in df.columns]
    null = np.array([
        np.stack([rng.permutation(c) for c in cols], axis=1).max(axis=1).mean()
        for _ in range(args.n_null)
    ])
    solved_by_k = {int(k): int(v) for k, v in df.sum(axis=1).value_counts().sort_index().items()}
    phi = float(np.mean([df[a].corr(df[b]) for a, b in combinations(df.columns, 2)]))
    # A system is "load-bearing" if dropping it lowers the oracle — i.e. it is the sole
    # solver of at least one item. This is the cheapest test of "does it add anything".
    sole = {s: int(((df[s] == 1) & (df.drop(columns=[s]).max(axis=1) == 0)).sum())
            for s in df.columns}

    out = {
        "condition": args.condition, "phase": args.phase,
        "model": args.model, "language": args.language,
        "n_items": n, "n_systems": int(df.shape[1]),
        "accuracy": acc,
        "oracle_of_all": oracle_all,
        "best_single": best_single,
        "oracle_headroom_pts": (oracle_all - best_single) * 100,
        "oracle_independence_null": float(null.mean()),
        "oracle_null_ci": [float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))],
        "oracle_minus_null_pts": (oracle_all - float(null.mean())) * 100,
        "mean_pairwise_phi": phi,
        "items_solved_by_k_systems": solved_by_k,
        "sole_solver_items": sole,
        "pairs": pairs,
        "skipped": skipped,
    }
    dest = Path(args.out) if args.out else (
        ROOT / "results" / "analysis"
        / f"item_agreement_{args.phase}_{args.model}_{args.language}_{args.condition}.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))

    print(f"{args.condition} / {args.phase} / {args.language} - n={n} items, "
          f"{df.shape[1]} systems")
    if skipped:
        print("  skipped:")
        for s, why in sorted(skipped.items()):
            print(f"    {s:24s} {why}")
    print(f"\n  {'system':26s}{'acc':>8s}{'sole':>7s}")
    for s, a in sorted(acc.items(), key=lambda kv: -kv[1]):
        print(f"  {s:26s}{a*100:>7.1f}%{sole[s]:>7d}")
    print(f"\n  best single {best_single*100:.1f}%   oracle-of-{df.shape[1]} {oracle_all*100:.1f}%"
          f"   headroom {(oracle_all-best_single)*100:+.1f} pts")
    print(f"  independence null {null.mean()*100:.1f}% "
          f"[{np.percentile(null,2.5)*100:.1f}, {np.percentile(null,97.5)*100:.1f}]"
          f"   observed - null {(oracle_all-null.mean())*100:+.1f} pts"
          f"   mean pairwise phi {phi:+.3f}")
    print("  -> observed BELOW null = the systems are redundant, not complementary; "
          "the raw headroom is a k-artifact")
    print(f"  items solved by k of {df.shape[1]} systems: {solved_by_k}")
    print(f"\n  {'pair':52s}{'jacc':>7s}{'or2':>8s}{'gain':>8s}{'mcnemar':>10s}")
    for p in sorted(pairs, key=lambda r: -r["oracle_gain_pts"])[:15]:
        print(f"  {p['a']+' vs '+p['b']:52s}{p['jaccard']:>7.3f}{p['oracle_of_2']*100:>7.1f}%"
              f"{p['oracle_gain_pts']:>+8.1f}{p['mcnemar_p']:>10.3f}")
    print(f"\nwrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
