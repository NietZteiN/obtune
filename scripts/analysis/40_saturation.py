#!/usr/bin/env python
"""E12 — are the two standing SFT arms data-saturated? (phase saturation, 7B, NO H1)

Rules (CLAUDE_SCRATCHPAD.md 2026-09-07, verbatim; TOST margin ±1.0 pt, 90% interval):
  H-sat-L0    CONFIRMED iff tuned_L0_half − tuned_L0 pooled over the six seen conditions is
              EQUIVALENT at ±1.0 (then row count is not what separates tuned_L0 from mono_all).
  H-sat-mono  CONFIRMED iff mono_half − mono_all pooled over the six seen conditions is
              EQUIVALENT at ±1.0.
  H-tax-scales  "the unseen tax grows with breadth DATA, not breadth per se": CONFIRMED iff
              mono_all − tuned_L0 @ X1 is more negative than mono_quarter − tuned_L0 @ X1 AND
              the quarter arm's tax does not have ci_hi<0. REFUTED iff the quarter arm already
              pays a tax with ci_hi<0 (then breadth itself, at a quarter of the rows, hurts).
The quarter arms are reported alongside; they gate nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

CONDS = ck.SEEN + ["X1"]
SYSTEMS = ["tuned_L0", "tuned_L0_half", "tuned_L0_quarter", "mono_all", "mono_half", "mono_quarter"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ1' (support)", Path(__file__).name, [a.model])
    b = ck.load_block(["saturation"], a.model, SYSTEMS, CONDS)
    res["accuracy"][a.model], res["format_fail"][a.model] = ck.acc_table(b)
    C = res["contrasts"].setdefault(a.model, {})
    for t, c in [("tuned_L0_half", "tuned_L0"), ("tuned_L0_quarter", "tuned_L0"),
                 ("mono_half", "mono_all"), ("mono_quarter", "mono_all"),
                 ("mono_all", "tuned_L0"), ("mono_half", "tuned_L0"), ("mono_quarter", "tuned_L0"),
                 ("mono_half", "tuned_L0_half"), ("mono_quarter", "tuned_L0_quarter")]:
        for conds, tag in ((ck.SEEN, "seen6"), (ck.OBF_SEEN, "seen"), (["X1"], "X1"), (["L0"], "L0")):
            lab = f"{t} - {c} @ {tag}"
            r = ck.contrast(b, t, c, conds, label=lab, eq_margin=1.0)
            if r:
                C[lab] = r
    ck.print_acc(a.model, res["accuracy"][a.model], CONDS)
    for lab, c in C.items():
        print(f"  {lab:<36} {ck.fmt(c)}")
    g = C.get
    r = g("tuned_L0_half - tuned_L0 @ seen6")
    ck.hypothesis(res, "H-sat-L0", "tuned_L0_half − tuned_L0 @ seen6 equivalent at ±1.0",
                  "PENDING" if not r else "CONFIRMED" if r.get("equivalent") else "REFUTED", ck.fmt(r))
    r = g("mono_half - mono_all @ seen6")
    ck.hypothesis(res, "H-sat-mono", "mono_half − mono_all @ seen6 equivalent at ±1.0",
                  "PENDING" if not r else "CONFIRMED" if r.get("equivalent") else "REFUTED", ck.fmt(r))
    full, q = g("mono_all - tuned_L0 @ X1"), g("mono_quarter - tuned_L0 @ X1")
    if full and q:
        v = "REFUTED" if q["ci_hi"] < 0 else "CONFIRMED" if full["value_pts"] < q["value_pts"] else "INCONCLUSIVE"
    else:
        v = "PENDING"
    ck.hypothesis(res, "H-tax-scales", "quarter arm pays no tax (ci_hi≥0) and full tax is more negative",
                  v, f"full {ck.fmt(full)}; quarter {ck.fmt(q)}; half {ck.fmt(g('mono_half - tuned_L0 @ X1'))}")
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
