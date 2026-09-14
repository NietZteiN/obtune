#!/usr/bin/env python
"""Master-table coverage: how many cells each model has, and what the gap actually is.

    python scripts/analysis/70_coverage.py [--md]

docs/MASTER_TABLE_COVERAGE.md was maintained by hand with an "inventory snippet at the end",
which means it is right on the day it is written and drifts after. This computes it, so the
question "is the master table complete" has an answer that cannot be stale.

The table wants, per model, 8 methods x 23 conditions forward and 7 x 23 backward -- in-context
learning has no backward run, because there is no adapter to ask backwards, so 161 rather than 184.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CELLS = ROOT / "results" / "cells"
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1",
         "C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3",
         "C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4",
         "C_L1r_X1", "C_X1_S1", "C_S2_X1", "C_L1r_X1m", "C_S1_X1s", "C3_L1r_S1_X1"]
FWD_DEFAULT = ["panel_core", "composite_generic", "composite_depth", "f2_divergence",
               "baselines_generic"]
SYSTEMS = [("untuned", "base", None),
           ("ICL", "base_1shot", ["basecheck_1shot"]),
           ("clean LoRA", "tuned_L0", None),
           ("breadth", "mono_all", None),
           ("anchored", "cons_lam3", None),
           ("family", "tuned_X1", None),
           ("mixture", "mole_router", ["mole_generic"]),
           ("merge", "merge_dare_ties", ["merge_panel", "rq2_generic", "composite_generic",
                                         "composite_depth", "f2_divergence"])]
BWD = ["inverse_1shot", "inverse_generic"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]


def have(model, sysn, cond, phases):
    return any((CELLS / p / model / "python" / f"{sysn}__{cond}" / "cell_meta.json").exists()
               for p in phases)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="emit a markdown table")
    a = ap.parse_args()

    n_fwd = len(SYSTEMS) * len(CONDS)
    n_bwd = (len(SYSTEMS) - 1) * len(CONDS)
    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "n_forward": n_fwd, "n_backward": n_bwd, "models": {}}
    rows = []
    for m in MODELS:
        f = b = 0
        fgap, bgap = {}, {}
        for label, sysn, ph in SYSTEMS:
            for c in CONDS:
                if have(m, sysn, c, ph or FWD_DEFAULT):
                    f += 1
                else:
                    fgap[label] = fgap.get(label, 0) + 1
                if label == "ICL":
                    continue
                if have(m, sysn, c, BWD):
                    b += 1
                else:
                    bgap[label] = bgap.get(label, 0) + 1
        out["models"][m] = {"forward": f, "backward": b,
                            "forward_gaps": fgap, "backward_gaps": bgap}
        rows.append((m, f, b, fgap, bgap))

    def gapstr(g):
        return ", ".join(f"{k} {v}" for k, v in sorted(g.items(), key=lambda kv: -kv[1])) or "none"

    if a.md:
        print(f"| model | forward | backward | forward gap | backward gap |")
        print("|---|---:|---:|---|---|")
        for m, f, b, fg, bg in rows:
            print(f"| {m} | {f}/{n_fwd} | {b}/{n_bwd} | {gapstr(fg)} | {gapstr(bg)} |")
    else:
        print(f"{'model':16s} {'forward':>10s} {'backward':>10s}   gaps")
        for m, f, b, fg, bg in rows:
            print(f"{m:16s} {f:5d}/{n_fwd:<4d} {b:5d}/{n_bwd:<4d}   fwd: {gapstr(fg)} | bwd: {gapstr(bg)}")
    p = ROOT / "results/analysis/pipeline/master_table_coverage.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
