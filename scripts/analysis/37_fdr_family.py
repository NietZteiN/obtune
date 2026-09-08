#!/usr/bin/env python
"""E7 — BH-FDR across the transfer matrix AS ONE FAMILY (CLAUDE.md §4), 7B. NO H1.

WHAT THIS IS NOT. The charter asks for item-level binomial GLMMs with crossed program × model
random effects. statsmodels is not in the env and the R `stats/` stack (lme4) did not survive
the migration, so this is the honest substitute: every contrast keeps the project's
program-clustered bootstrap (the same resampling the CIs use), a two-sided percentile-bootstrap
p is formed from the draws, and Benjamini-Hochberg is applied over the whole family at once.
The GLMM is a TODO for when R/lme4 is back; nothing here changes a headline direction, it
only says which cells survive family-wise correction.

Families (each corrected separately, as pre-registered 2026-09-07):
  transfer   6 specialists (s17) × 6 eval conditions vs tuned_L0_s17          (30 tests: 5 specialists × 6 conditions; the control is not tested against itself)
  arms       {mono_all, cons_lam3, cons_lam1, tuned_X1} × 7 conditions vs tuned_L0  (28 tests)
Rule: a cell is "survives FDR" iff q < 0.05. Reported; gates nothing.

--extended adds two MORE families, pre-registered 2026-09-08 (commit e5d08ab) as a CONSERVATIVE
robustness check after the pipeline campaign roughly tripled the number of arms. Enlarging a family
can only raise q, never lower it, so nothing can be upgraded by this — a claim either survives the
widest reasonable family or it does not. The two families above stay PRIMARY and are unchanged, and
membership below is discovered from the filesystem, never hand-picked, so no arm can enter because
of how its number came out:

  arms_all   every system holding all seven generic cells (L0 + 5 seen + X1) × 7 conditions vs tuned_L0
  composites {mono_all, cons_lam3} × the six depth-2 composites vs tuned_L0                 (12 tests)

--control-family <system> runs ONE family, mechanically discovered as above but controlled against
<system> instead of tuned_L0, and writes it alone. This exists because every family above uses the
clean-code arm as the control, which leaves RQ3's actual headline — cons_lam3 - mono_all @ X1 —
uncorrected. That gap was recorded on 2026-09-08 (E7b) and deliberately NOT closed in the same
breath: a family chosen after seeing that the headline was uncovered cannot be told apart, by a
reader, from a family chosen because the headline survives in it. The rule was frozen first
(pre-registration #2, commit 8da96b4) and only then run.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

SPEC = ["tuned_L0", "tuned_L1b", "tuned_L1r", "tuned_L2", "tuned_S1", "tuned_S2"]
GEN_PHASES = ["objectives_teacher", "x1_split", "saturation", "objectives_generic", "x1_generic", "rq1_generic"]
COMPOSITES = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]


def discover(model: str, phases, conds) -> list[str]:
    """Systems holding a cell for EVERY cond in `conds`, across `phases`. Mechanical: the family's
    membership must not depend on any result, so it is read off the directory tree."""
    have: dict[str, set[str]] = {}
    for ph in phases:
        d = ck.CELLS / ph / model / "python"
        if not d.exists():
            continue
        for c in d.iterdir():
            if "__" not in c.name or not (c / "trials.parquet").exists():
                continue
            sys_, cond = c.name.rsplit("__", 1)
            have.setdefault(sys_, set()).add(cond)
    return sorted(s for s, cs in have.items() if set(conds) <= cs)


def family(name: str, phases, model, systems, control, conds, alias, res):
    b = ck.load_block(phases, model, list(systems) + [control], conds, alias=alias)
    rows = []
    for s in systems:
        if s == control:
            continue
        for c in conds:
            if c in b.get(s, {}) and c in b.get(control, {}):
                point, draws = ck.bootstrap_draws(b[s][c], b[control][c])
                lo, hi = (float(x) for x in __import__("numpy").percentile(draws, [2.5, 97.5]))
                rows.append({"system": s, "cond": c, "delta_pts": round(point, 3),
                             "ci_lo": round(lo, 3), "ci_hi": round(hi, 3), "p_boot": ck.bootstrap_p(draws)})
    qs = ck.bh_fdr([r["p_boot"] for r in rows])
    for r, q in zip(rows, qs):
        r["q_bh"] = round(q, 4)
        r["survives_fdr"] = bool(q < 0.05)
    res.setdefault("families", {})[name] = {"control": control, "n_tests": len(rows),
                                             "n_survive": sum(r["survives_fdr"] for r in rows), "rows": rows}
    print(f"--- family {name}: {len(rows)} tests, {sum(r['survives_fdr'] for r in rows)} survive q<.05")
    for r in rows:
        flag = "✓" if r["survives_fdr"] else " "
        print(f"  {flag} {r['system']:<12} {r['cond']:<5} {r['delta_pts']:+7.2f} [{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}]  p={r['p_boot']:.4f} q={r['q_bh']:.4f}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extended", action="store_true",
                    help="also run the arms_all and composites families (2026-09-08 pre-registration)")
    ap.add_argument("--control-family", metavar="SYSTEM",
                    help="run ONE mechanically-discovered family controlled against SYSTEM (e.g. mono_all)")
    a = ap.parse_args()
    res = ck.new_result("RQ4' (support)", Path(__file__).name, [a.model])
    if a.control_family:
        conds7 = ck.SEEN + ["X1"]
        arms = discover(a.model, GEN_PHASES, conds7)
        if a.control_family not in arms:
            print(f"FATAL: control {a.control_family} has no complete 7-condition row", file=sys.stderr)
            return 1
        print(f"[control-family] {len(arms)} systems discovered, control = {a.control_family}: {arms}")
        family(f"arms_vs_{a.control_family}", GEN_PHASES, a.model, arms, a.control_family, conds7, {}, res)
        f = res["families"][f"arms_vs_{a.control_family}"]
        ck.hypothesis(res, f"FDR-arms_vs_{a.control_family}",
                      "q<0.05 after BH over the family (reported, gates nothing)", "REPORTED",
                      f"{f['n_survive']}/{f['n_tests']} cells survive")
        ck.write(res, a.out)
        print(f"wrote {a.out}")
        return 0
    alias = {s: f"{s}_s17" for s in SPEC}
    family("transfer", ["rq1_generic"], a.model, SPEC, "tuned_L0", ck.SEEN, alias, res)
    family("arms", ["objectives_generic", "x1_generic", "rq1_generic"], a.model,
           ["mono_all", "cons_lam3", "cons_lam1", "tuned_X1"], "tuned_L0", ck.SEEN + ["X1"], {}, res)
    if a.extended:
        conds7 = ck.SEEN + ["X1"]
        arms_all = discover(a.model, GEN_PHASES, conds7)
        print(f"[extended] arms_all discovered {len(arms_all)} systems with all 7 generic cells: {arms_all}")
        family("arms_all", GEN_PHASES, a.model, arms_all, "tuned_L0", conds7, {}, res)
        family("composites", ["composite_generic"], a.model, ["mono_all", "cons_lam3"], "tuned_L0",
               COMPOSITES, {}, res)
    for name, f in res["families"].items():
        ck.hypothesis(res, f"FDR-{name}", "q<0.05 after BH over the family (reported, gates nothing)", "REPORTED",
                      f"{f['n_survive']}/{f['n_tests']} cells survive")
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
