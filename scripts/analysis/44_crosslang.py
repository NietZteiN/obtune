#!/usr/bin/env python
"""E13 — does the campaign's story hold in a SECOND LANGUAGE? CodeLlama-7b, JavaScript. NO H1.

Every number in the paper is Python. The charter's cross-language hypothesis was written off as
unreachable because `node` is not installed on juno — but node blocks REGENERATING the corpus, not
using it, and the JS corpus transferred intact: 2,022 train pairs and 504 heldout items per
condition plus the six depth-2 composites, all passing `scripts/check_manifest.py` (SHA manifests
AND the H1-marker content scan, verified 2026-09-08 before anything was trained).

WHAT IS NOT HERE. No unseen-family column. X1 is Python-only by construction and no JS X1 generator
exists; H1's budget is spent. So this read covers RQ1's "buy" side (stacked-but-seen composites),
RQ3's seen-condition and clean-code claims, and breadth's L0 cost — and must not be quoted for the
"cost" side, which is the half that needs a held-out family.

Rules frozen in CLAUDE_SCRATCHPAD.md (pre-registration #2, commit 8da96b4) BEFORE submission:
  H-xlang-stack       mono_all - tuned_L0 pooled over the six JS composites:
                      ci_lo > 0 CONFIRMED / ci_hi < 0 REFUTED / else INCONCLUSIVE
  H-xlang-cons-seen   cons_lam3 - tuned_L0 pooled over the five obfuscated seen conditions, same rule
  H-xlang-cons-stack  cons_lam3 - mono_all on the six composites, same rule
  H-xlang-L0          mono_all - tuned_L0 @ L0: ci_hi < 0 CONFIRMED / inside +/-1.0 REFUTED / else INCONCLUSIVE
  H-xlang-volume      REPORTED, not verdicted: JS trains on ~12.1k rows against Python's ~26.8k and
                      E12 showed breadth's taxes grow with data volume, so the JS L0 cost should be
                      the smaller one (Python: -1.32). No verdict — a cross-language magnitude
                      comparison is confounded by the programs, the tokenizer and the ladder at once.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

PHASES = ["crosslang_js"]
SYSTEMS = ["base", "tuned_L0", "mono_all", "cons_lam3"]
COMPOSITES = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
PY_L0_COST = -1.32          # mono_all - tuned_L0 @ L0 on Python, for the H-xlang-volume comparison


def three_way(c: dict | None) -> str:
    if not c:
        return "UNAVAILABLE"
    if c["ci_lo"] > 0:
        return "CONFIRMED"
    if c["ci_hi"] < 0:
        return "REFUTED"
    return "INCONCLUSIVE"


def cost_rule(c: dict | None) -> str:
    if not c:
        return "UNAVAILABLE"
    if c["ci_hi"] < 0:
        return "CONFIRMED"
    if c.get("equivalent"):
        return "REFUTED"
    return "INCONCLUSIVE"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    conds = ck.SEEN + COMPOSITES
    b = ck.load_block(PHASES, a.model, SYSTEMS, conds, alias=None)
    res = ck.new_result("E13 (cross-language)", Path(__file__).name, [a.model])
    res["accuracy"][a.model], res["format_fail"][a.model] = ck.acc_table(b)
    print(f"=== {a.model} / JAVASCRIPT — seen singles ===")
    ck.print_acc(a.model, res["accuracy"][a.model], ck.SEEN)
    print(f"\n=== {a.model} / JAVASCRIPT — depth-2 composites ===")
    ck.print_acc(a.model, res["accuracy"][a.model], COMPOSITES)

    C = res["contrasts"].setdefault(a.model, {})

    def add(treat, control, cs, label, eq=None):
        r = ck.contrast(b, treat, control, cs, label=label, eq_margin=eq)
        if r:
            C[label] = r
            print(f"  {label:<42} {ck.fmt(r)}")
        return r

    print("\n=== contrasts (pts, program-clustered bootstrap) ===")
    stack = add("mono_all", "tuned_L0", COMPOSITES, "mono_all - tuned_L0 @ composites")
    cons_stack = add("cons_lam3", "mono_all", COMPOSITES, "cons_lam3 - mono_all @ composites")
    add("cons_lam3", "tuned_L0", COMPOSITES, "cons_lam3 - tuned_L0 @ composites")
    cons_seen = add("cons_lam3", "tuned_L0", ck.OBF_SEEN, "cons_lam3 - tuned_L0 @ seen5")
    add("mono_all", "tuned_L0", ck.OBF_SEEN, "mono_all - tuned_L0 @ seen5")
    l0 = add("mono_all", "tuned_L0", ["L0"], "mono_all - tuned_L0 @ L0", eq=1.0)
    add("cons_lam3", "tuned_L0", ["L0"], "cons_lam3 - tuned_L0 @ L0", eq=1.0)
    add("tuned_L0", "base", ck.OBF_SEEN, "tuned_L0 - base @ seen5")

    print("\n=== per-composite detail ===")
    for c in COMPOSITES:
        for t, ctl in (("mono_all", "tuned_L0"), ("cons_lam3", "mono_all")):
            r = ck.contrast(b, t, ctl, [c], label=f"{t} - {ctl} @ {c}")
            if r:
                C[f"{t} - {ctl} @ {c}"] = r
        m = C.get(f"mono_all - tuned_L0 @ {c}")
        k = C.get(f"cons_lam3 - mono_all @ {c}")
        if m and k:
            print(f"  {c:<10} mono-L0 {m['value_pts']:+6.2f}{'*' if m['excludes_zero'] else ' '}"
                  f"   cons-mono {k['value_pts']:+6.2f}{'*' if k['excludes_zero'] else ' '}")

    ck.hypothesis(res, "H-xlang-stack", "mono_all - tuned_L0 @ composites: ci_lo>0 CONFIRMED / ci_hi<0 REFUTED",
                  three_way(stack), ck.fmt(stack))
    ck.hypothesis(res, "H-xlang-cons-seen", "cons_lam3 - tuned_L0 @ seen5: ci_lo>0 CONFIRMED / ci_hi<0 REFUTED",
                  three_way(cons_seen), ck.fmt(cons_seen))
    ck.hypothesis(res, "H-xlang-cons-stack", "cons_lam3 - mono_all @ composites: ci_lo>0 CONFIRMED / ci_hi<0 REFUTED",
                  three_way(cons_stack), ck.fmt(cons_stack))
    ck.hypothesis(res, "H-xlang-L0", "mono_all - tuned_L0 @ L0: ci_hi<0 CONFIRMED / inside +/-1.0 REFUTED",
                  cost_rule(l0), ck.fmt(l0))
    ck.hypothesis(res, "H-xlang-volume",
                  "REPORTED, not verdicted: JS trains on ~12.1k rows vs Python's ~26.8k, so E12 predicts "
                  "the JS L0 cost is the smaller one", "REPORTED",
                  f"JS {l0['value_pts']:+.2f} vs Python {PY_L0_COST:+.2f}" if l0 else "unavailable")
    print()
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
