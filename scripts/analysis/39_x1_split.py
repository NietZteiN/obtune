#!/usr/bin/env python
"""RQ2' — is the unit of transfer the FAMILY or the MECHANISM? (E6, phase x1_split, NO H1)

X1 = string encoding + MBA arithmetic. X1m = MBA only, X1s = string encoding only. Specialists
on each are evaluated on the other. Rules (CLAUDE_SCRATCHPAD.md 2026-09-07, verbatim):

  H-family-unit  "a mechanism specialist helps on the OTHER mechanism of the same family":
                 CONFIRMED iff tuned_X1m − tuned_L0 @ X1s ci_lo>0 AND tuned_X1s − tuned_L0 @ X1m
                 ci_lo>0; PARTIAL iff exactly one; REFUTED otherwise.
  H-whole-ge-parts  "the family specialist is at least as good as either half on the full
                 family": CONFIRMED iff neither tuned_X1m − tuned_X1 @ X1 nor tuned_X1s −
                 tuned_X1 @ X1 has ci_lo>0.
  H-mech-dominance  which mechanism carries X1: reported, not gated — the larger of
                 tuned_X1m − tuned_L0 @ X1 and tuned_X1s − tuned_L0 @ X1.
  H-breadth-on-parts  mono_all − tuned_L0 on X1m and X1s: reported (does the unseen tax
                 fall on one mechanism?).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

CONDS = ["L0", "X1", "X1m", "X1s"]
SYSTEMS = ["base", "tuned_L0", "tuned_X1", "tuned_X1m", "tuned_X1s", "mono_all"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ2'", Path(__file__).name, [a.model])
    b = ck.load_block(["x1_split", "x1_generic"], a.model, SYSTEMS, CONDS)
    res["accuracy"][a.model], res["format_fail"][a.model] = ck.acc_table(b)
    C = res["contrasts"].setdefault(a.model, {})
    for t, c, cond in [("tuned_X1m", "tuned_L0", "X1s"), ("tuned_X1s", "tuned_L0", "X1m"),
                       ("tuned_X1m", "tuned_L0", "X1m"), ("tuned_X1s", "tuned_L0", "X1s"),
                       ("tuned_X1m", "tuned_L0", "X1"), ("tuned_X1s", "tuned_L0", "X1"),
                       ("tuned_X1", "tuned_L0", "X1"), ("tuned_X1m", "tuned_X1", "X1"), ("tuned_X1s", "tuned_X1", "X1"),
                       ("mono_all", "tuned_L0", "X1m"), ("mono_all", "tuned_L0", "X1s"), ("mono_all", "tuned_L0", "X1"),
                       ("tuned_X1", "tuned_L0", "L0"), ("tuned_X1m", "tuned_L0", "L0"), ("tuned_X1s", "tuned_L0", "L0")]:
        lab = f"{t} - {c} @ {cond}"
        r = ck.contrast(b, t, c, [cond], label=lab, eq_margin=1.0)
        if r:
            C[lab] = r
    ck.print_acc(a.model, res["accuracy"][a.model], CONDS)
    for lab, c in C.items():
        print(f"  {lab:<32} {ck.fmt(c)}")

    g = C.get
    x1, x2 = g("tuned_X1m - tuned_L0 @ X1s"), g("tuned_X1s - tuned_L0 @ X1m")
    if x1 and x2:
        n = int(x1["ci_lo"] > 0) + int(x2["ci_lo"] > 0)
        v = "CONFIRMED" if n == 2 else "PARTIAL" if n == 1 else "REFUTED"
    else:
        v = "PENDING"
    ck.hypothesis(res, "H-family-unit", "X1m→X1s and X1s→X1m both ci_lo>0 vs tuned_L0", v,
                  f"X1m→X1s {ck.fmt(x1)}; X1s→X1m {ck.fmt(x2)}")
    p1, p2 = g("tuned_X1m - tuned_X1 @ X1"), g("tuned_X1s - tuned_X1 @ X1")
    v = "PENDING" if not (p1 and p2) else "CONFIRMED" if not (p1["ci_lo"] > 0 or p2["ci_lo"] > 0) else "REFUTED"
    ck.hypothesis(res, "H-whole-ge-parts", "neither half beats tuned_X1 on X1 (ci_lo>0)", v,
                  f"X1m−X1 {ck.fmt(p1)}; X1s−X1 {ck.fmt(p2)}")
    d1, d2 = g("tuned_X1m - tuned_L0 @ X1"), g("tuned_X1s - tuned_L0 @ X1")
    if d1 and d2:
        dom = "MBA (X1m)" if d1["value_pts"] > d2["value_pts"] else "string encoding (X1s)"
        ck.hypothesis(res, "H-mech-dominance", "reported, not gated", "REPORTED",
                      f"{dom} carries more of X1: X1m {ck.fmt(d1)}; X1s {ck.fmt(d2)}")
    m1, m2 = g("mono_all - tuned_L0 @ X1m"), g("mono_all - tuned_L0 @ X1s")
    if m1 and m2:
        ck.hypothesis(res, "H-breadth-on-parts", "reported, not gated", "REPORTED",
                      f"breadth tax on X1m {ck.fmt(m1)}; on X1s {ck.fmt(m2)}")
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
