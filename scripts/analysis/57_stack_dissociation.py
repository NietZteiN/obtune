#!/usr/bin/env python
"""RQ1's headline, as a WITHIN-MODEL difference on ONE program set.

    python scripts/analysis/57_stack_dissociation.py

THE CLAIM. Breadth training composes on stacks built from transforms it has SEEN and fails on
stacks containing a family it has not. Until now that was two separate reads on two program sets,
and the natural summary -- "one interval is positive and the other is negative" -- is NOT a test of
the difference between them. On most models the unseen-side interval straddles zero on its own, so
stating the dissociation from the two levels separately would be stating something not measured.

WHAT THIS COMPUTES. Per model, on the programs common to EVERY cell of both groups:

    [ breadth - clean control on the six SEEN depth-2 composites ]
  - [ breadth - clean control on the three composites containing the unseen family ]

on one program-clustered bootstrap (2,000 resamples, seed 17), so the two halves are paired and the
difference has an interval of its own. That difference is the dissociation; the levels are context.

The seen composites cover more programs than the unseen-containing ones (X1 needs >= 3 sites), so
intersecting is what makes the comparison legitimate -- and it moves the level estimates, which is
reported rather than hidden.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402

SEEN = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
UNSEEN = ["C_L1r_X1", "C_X1_S1", "C_S2_X1"]
TREAT, CONTROL = "mono_all", "tuned_L0"
N_BOOT, SEED = 2000, 17
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]


def read(model):
    cells = {}
    for grp, conds, phases in (("seen", SEEN, ["composite_generic"]),
                               ("unseen", UNSEEN, ["f2_divergence"])):
        for c in conds:
            for s in (TREAT, CONTROL):
                d = load_cell(phases, model, s, c)
                if d is None:
                    return None
                cells[(grp, s, c)] = d
    return cells


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    out = {"script": "57_stack_dissociation.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "n_resamples": N_BOOT, "seed": SEED,
           "groups": {"seen": SEEN, "unseen_containing": UNSEEN},
           "models": {}}
    print("breadth - clean control: [SEEN stacks] - [stacks containing the UNSEEN family]")
    print(f"\n{'model':16s}{'seen':>21s}{'unseen-inside':>21s}{'DIFFERENCE':>21s}   n")
    sig = tot = 0
    for m in MODELS:
        cells = read(m)
        if cells is None:
            print(f"{m:16s}  (grid incomplete -- skipped)")
            continue
        progs = None
        for v in cells.values():
            s = set(v["snippet_id"])
            progs = s if progs is None else (progs & s)
        P = sorted(progs)
        by = {k: {p: g["correct"].to_numpy(dtype=float)
                  for p, g in v.groupby("snippet_id") if p in progs}
              for k, v in cells.items()}

        def grp(pick, g, conds):
            t = np.concatenate([np.concatenate([by[(g, TREAT, c)][P[j]] for j in pick]) for c in conds])
            b = np.concatenate([np.concatenate([by[(g, CONTROL, c)][P[j]] for j in pick]) for c in conds])
            return (t.mean() - b.mean()) * 100.0

        rng = np.random.default_rng(SEED)
        idx = np.arange(len(P))
        ds = np.empty(N_BOOT); du = np.empty(N_BOOT)
        for i in range(N_BOOT):
            pk = rng.choice(idx, len(P), True)
            ds[i] = grp(pk, "seen", SEEN); du[i] = grp(pk, "unseen", UNSEEN)
        dd = ds - du
        full = np.arange(len(P))
        ps, pu = grp(full, "seen", SEEN), grp(full, "unseen", UNSEEN)

        def ci(v, d):
            lo, hi = (float(x) for x in np.percentile(d, [2.5, 97.5]))
            return {"value_pts": float(v), "ci_lo": lo, "ci_hi": hi,
                    "excludes_zero": bool(lo > 0 or hi < 0)}

        rec = {"n_programs": len(P), "seen": ci(ps, ds), "unseen_containing": ci(pu, du),
               "difference": ci(ps - pu, dd)}
        out["models"][m] = rec
        tot += 1; sig += rec["difference"]["excludes_zero"]
        f = lambda c: f"{c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f},{c['ci_hi']:+6.2f}]{'*' if c['excludes_zero'] else ' '}"
        print(f"{m:16s}{f(rec['seen']):>21s}{f(rec['unseen_containing']):>21s}"
              f"{f(rec['difference']):>21s}   {len(P)}")
    out["tally"] = {"models_read": tot, "difference_significant": sig}
    print(f"\n  the dissociation is significant on {sig} of {tot} models read")
    dst = Path(a.out) if a.out else ROOT / "results/analysis/pipeline/stack_dissociation.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(f"  wrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
