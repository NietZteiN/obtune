#!/usr/bin/env python
"""B8: the seed noise floor on CodeLlama-7B.

    python scripts/analysis/83_seed_variance.py

The draft narrates several 1-2 point differences. This measures how far apart three independently
seeded runs of the SAME recipe land, so those differences can be read against the spread rather
than against zero.

Seeds 17 (the panel's own), 101 and 202, for the six specialists and for breadth. Seed 17 is read
from the phases it already lives in; 101 and 202 from `seedvar_generic`.

The headline is the per-arm RANGE across seeds on a condition group -- max minus min. A narrated
difference smaller than that range is not distinguishable from a re-roll of the seed.
"""
from __future__ import annotations
import sys, json, statistics as st
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

M = "codellama-7b"
S17 = ["panel_core", "merge_panel", "composite_generic", "f2_divergence", "rq2_generic"]
SV = ["seedvar_generic"]
GROUPS = [("L0", ["L0"]), ("singles", ["L1b", "L1r", "L2", "S1", "S2"]), ("unseen", ["X1"])]
# (label, s17 system name, seedvar system template)
ARMS = [("L0", "tuned_L0", "tuned_L0_s{s}"), ("L1b", "tuned_L1b", "tuned_L1b_s{s}"),
        ("L1r", "tuned_L1r", "tuned_L1r_s{s}"), ("L2", "tuned_L2", "tuned_L2_s{s}"),
        ("S1", "tuned_S1", "tuned_S1_s{s}"), ("S2", "tuned_S2", "tuned_S2_s{s}"),
        ("breadth", "mono_all", "mono_all_s{s}")]

def acc(ph, arm, cs):
    fr = [d for d in (load_cell(ph, M, arm, c) for c in cs)
          if d is not None and d.format_fail.mean() <= 0.25]
    return None if not fr else float(pd.concat(fr).correct.mean()) * 100

def main() -> int:
    out, ranges = {}, []
    for g, cs in GROUPS:
        print(f"\n{g}: accuracy (%) by seed\n")
        print(f"{'arm':9s} {'s17':>8s} {'s101':>8s} {'s202':>8s} {'range':>8s} {'sd':>7s}")
        for lab, a17, tmpl in ARMS:
            vals = [acc(S17, a17, cs)] + [acc(SV, tmpl.format(s=s), cs) for s in (101, 202)]
            got = [v for v in vals if v is not None]
            if len(got) < 2:
                print(f"{lab:9s} " + " ".join("      --" for _ in range(3)) + "      --      --")
                continue
            rng = max(got) - min(got)
            sd = st.stdev(got) if len(got) > 2 else float("nan")
            ranges.append(rng)
            out.setdefault(g, {})[lab] = dict(
                s17=vals[0] and round(vals[0], 2), s101=vals[1] and round(vals[1], 2),
                s202=vals[2] and round(vals[2], 2), range=round(rng, 2),
                sd=None if sd != sd else round(sd, 2), n_seeds=len(got))
            cells = " ".join("      --" if v is None else f"{v:8.2f}" for v in vals)
            print(f"{lab:9s} {cells} {rng:8.2f} " + ("     --" if sd != sd else f"{sd:7.2f}"))
    if ranges:
        print(f"\nNOISE FLOOR across {len(ranges)} arm x group combinations:")
        print(f"  median seed range {st.median(ranges):.2f} pts, max {max(ranges):.2f} pts")
        print("  A narrated difference below the median is not distinguishable from a re-rolled seed.")
        out["_summary"] = dict(n=len(ranges), median_range=round(st.median(ranges), 2),
                               max_range=round(max(ranges), 2))
    f = ROOT/"results/analysis/pipeline/seed_variance.json"
    f.write_text(json.dumps(out, indent=2)); print(f"\nwrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
