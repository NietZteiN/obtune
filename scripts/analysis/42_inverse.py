#!/usr/bin/env python
"""RQ5' — does output-prediction tuning also help INPUT prediction? (phase inverse_generic, NO H1)

Every adapter was trained on the forward task (program + call -> value). The inverse grid
asks the same items backwards (program + value -> call), graded by execution
(src/obtune/inverse.py). Forward numbers come from the existing Grid A cells.

Rules (CLAUDE_SCRATCHPAD.md 2026-09-08, verbatim; 95 % program-cluster bootstrap; TOST ±1.0
at 90 %; "seen6" = L0 L1b L1r L2 S1 S2, "obf" = L1b L1r L2 S1 S2):
  FORMAT GATE   an arm whose pooled seen6 format_fail_rate on the inverse task exceeds 0.25 is
                NOT INTERPRETABLE; every hypothesis that names it is INCONCLUSIVE. Reported first.
  H-inv-transfer  forward tuning transfers to the inverse task. CONFIRMED iff
                tuned_L0 − base @ seen6 has ci_lo > 0 AND tuned_L0 − formatonly @ seen6 has
                ci_lo > 0 (so the gain is not prompt/format adaptation). REFUTED iff
                tuned_L0 − base is equivalent at ±1.0 or has ci_hi < 0 — tuning is
                direction-specific, Nikiema et al.'s "cognitive specialization" on this axis.
  H-inv-breadth   CONFIRMED iff mono_all − tuned_L0 @ obf (inverse) has ci_lo > 0; REFUTED iff
                equivalent at ±1.0 or ci_hi < 0.
  H-inv-cons      CONFIRMED iff cons_lam3 − mono_all @ obf (inverse) has ci_lo > 0; REFUTED iff
                equivalent at ±1.0 or ci_hi < 0.
  H-inv-family    CONFIRMED iff tuned_X1 − tuned_L0 @ X1 (inverse) has ci_lo > 0; REFUTED iff
                equivalent at ±1.0 or ci_hi < 0.
  H-inv-diagonal  CONFIRMED iff ≥ 3 of the 5 specialists beat tuned_L0 on their own condition
                (ci_lo > 0); REFUTED iff 0 of 5; else PARTIAL.
  DIRECTION RATIO (reported, gates nothing): DR(arm) = (inv_arm − inv_base) / (fwd_arm − fwd_base)
                pooled over seen6; the forward gain is read from the existing Grid A cells.
  BH-FDR over the five primary contrasts is reported alongside; verdicts use the CIs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

CONDS = ck.SEEN + ["X1"]
SYSTEMS = ["base", "formatonly", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1",
           "tuned_L1b", "tuned_L1r", "tuned_L2", "tuned_S1", "tuned_S2"]
FWD_PHASES = ["x1_generic", "rq1_generic", "objectives_generic", "baselines_generic",
              "extra_generic", "rq2_generic", "formatonly_fix"]
GATE = 0.25


def verdict(r, need_ci_lo=True):
    if not r:
        return "PENDING"
    if r["ci_lo"] > 0:
        return "CONFIRMED"
    if r["ci_hi"] < 0 or r.get("equivalent"):
        return "REFUTED"
    return "INCONCLUSIVE"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ5'", Path(__file__).name, [a.model])
    inv = ck.load_block(["inverse_generic"], a.model, SYSTEMS, CONDS)
    fwd = ck.load_block(FWD_PHASES, a.model, SYSTEMS, CONDS, quiet=True)
    res["accuracy"][a.model], res["format_fail"][a.model] = ck.acc_table(inv)
    res["forward_accuracy"] = {a.model: ck.acc_table(fwd)[0]}

    # Format gate, pooled seen6.
    gate = {}
    for s in inv:
        p = ck.pooled(inv, s, ck.SEEN)
        if p is not None:
            gate[s] = round(float(p["format_fail"].mean()), 4)
    blocked = {s for s, ff in gate.items() if ff > GATE}
    res["format_gate"] = {"threshold": GATE, "pooled_seen6_format_fail": gate, "not_interpretable": sorted(blocked)}

    C = res["contrasts"].setdefault(a.model, {})
    pairs = [("tuned_L0", "base", ck.SEEN, "seen6"), ("tuned_L0", "formatonly", ck.SEEN, "seen6"),
             ("formatonly", "base", ck.SEEN, "seen6"),
             ("mono_all", "tuned_L0", ck.OBF_SEEN, "obf"), ("cons_lam3", "mono_all", ck.OBF_SEEN, "obf"),
             ("cons_lam3", "tuned_L0", ck.OBF_SEEN, "obf"), ("tuned_X1", "tuned_L0", ["X1"], "X1"),
             ("mono_all", "tuned_L0", ["X1"], "X1"), ("mono_all", "base", ck.SEEN, "seen6"),
             ("cons_lam3", "base", ck.SEEN, "seen6"), ("tuned_X1", "base", ["X1"], "X1")]
    for c in ck.OBF_SEEN:
        pairs.append((f"tuned_{c}", "tuned_L0", [c], c))
    for t, c, conds, tag in pairs:
        lab = f"{t} - {c} @ {tag} [inverse]"
        r = ck.contrast(inv, t, c, conds, label=lab, eq_margin=1.0)
        if r:
            C[lab] = r
    # Direction ratio (descriptive).
    DR = res.setdefault("direction_ratio", {}).setdefault(a.model, {})
    for s in ["formatonly", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]:
        ri = ck.contrast(inv, s, "base", ck.SEEN, label=f"{s} - base @ seen6 [inverse]")
        rf = ck.contrast(fwd, s, "base", ck.SEEN, label=f"{s} - base @ seen6 [forward]")
        if ri and rf:
            C[rf["label"] if "label" in rf else f"{s} - base @ seen6 [forward]"] = rf
            DR[s] = {"inverse_gain_pts": ri["value_pts"], "forward_gain_pts": rf["value_pts"],
                     "ratio": round(ri["value_pts"] / rf["value_pts"], 3) if abs(rf["value_pts"]) > 0.5 else None}

    ck.print_acc(a.model, res["accuracy"][a.model], CONDS)
    print("format_fail pooled seen6:", gate, "| NOT INTERPRETABLE:", sorted(blocked) or "none")
    for lab, c in C.items():
        print(f"  {lab:<44} {ck.fmt(c)}")
    for s, d in DR.items():
        print(f"  DR {s:<12} inverse {d['inverse_gain_pts']:+.2f} / forward {d['forward_gain_pts']:+.2f} = {d['ratio']}")

    g = C.get

    def gated(v, *arms):
        return "INCONCLUSIVE (format gate)" if any(s in blocked for s in arms) and v != "PENDING" else v

    r1, r2 = g("tuned_L0 - base @ seen6 [inverse]"), g("tuned_L0 - formatonly @ seen6 [inverse]")
    if not r1 or not r2:
        v = "PENDING"
    elif r1["ci_lo"] > 0 and r2["ci_lo"] > 0:
        v = "CONFIRMED"
    elif r1["ci_hi"] < 0 or r1.get("equivalent"):
        v = "REFUTED"
    else:
        v = "INCONCLUSIVE"
    ck.hypothesis(res, "H-inv-transfer", "tuned_L0 − base @ seen6 ci_lo>0 AND tuned_L0 − formatonly ci_lo>0",
                  gated(v, "tuned_L0", "base", "formatonly"), f"vs base {ck.fmt(r1)}; vs formatonly {ck.fmt(r2)}")
    r = g("mono_all - tuned_L0 @ obf [inverse]")
    ck.hypothesis(res, "H-inv-breadth", "mono_all − tuned_L0 @ obf (inverse) ci_lo>0",
                  gated(verdict(r), "mono_all", "tuned_L0"), ck.fmt(r))
    r = g("cons_lam3 - mono_all @ obf [inverse]")
    ck.hypothesis(res, "H-inv-cons", "cons_lam3 − mono_all @ obf (inverse) ci_lo>0",
                  gated(verdict(r), "cons_lam3", "mono_all"), ck.fmt(r))
    r = g("tuned_X1 - tuned_L0 @ X1 [inverse]")
    ck.hypothesis(res, "H-inv-family", "tuned_X1 − tuned_L0 @ X1 (inverse) ci_lo>0",
                  gated(verdict(r), "tuned_X1", "tuned_L0"), ck.fmt(r))
    diag = [g(f"tuned_{c} - tuned_L0 @ {c} [inverse]") for c in ck.OBF_SEEN]
    if any(d is None for d in diag):
        v = "PENDING"
    else:
        wins = sum(d["ci_lo"] > 0 for d in diag)
        v = "CONFIRMED" if wins >= 3 else "REFUTED" if wins == 0 else "PARTIAL"
    ck.hypothesis(res, "H-inv-diagonal", "≥3 of 5 specialists beat tuned_L0 on their own condition (inverse)",
                  gated(v, *[f"tuned_{c}" for c in ck.OBF_SEEN]),
                  "; ".join(f"{c} {ck.fmt(d)}" for c, d in zip(ck.OBF_SEEN, diag)))
    # FDR over the five primary contrasts (reported).
    prim = ["tuned_L0 - base @ seen6 [inverse]", "mono_all - tuned_L0 @ obf [inverse]",
            "cons_lam3 - mono_all @ obf [inverse]", "tuned_X1 - tuned_L0 @ X1 [inverse]",
            "tuned_L0 - formatonly @ seen6 [inverse]"]
    have = [(lab, C[lab]) for lab in prim if lab in C]
    if have:
        ps = []
        for lab, c in have:
            t, ctrl = lab.split(" - ")[0], lab.split(" - ")[1].split(" @ ")[0]
            conds = {"seen6": ck.SEEN, "obf": ck.OBF_SEEN, "X1": ["X1"]}[lab.split(" @ ")[1].split(" ")[0]]
            _, draws = ck.bootstrap_draws(ck.pooled(inv, t, conds), ck.pooled(inv, ctrl, conds))
            ps.append(ck.bootstrap_p(draws))
        qs = ck.bh_fdr(ps)
        res["fdr"] = {lab: {"p": round(p, 4), "q": round(q, 4)} for (lab, _), p, q in zip(have, ps, qs)}
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
