#!/usr/bin/env python
"""E7d — the GLMM CLAUDE.md §4 actually asks for. 7B. NO H1.

Every interval in this project is a program-clustered bootstrap, and every report says so and calls
it a substitute: the charter specifies **item-level binomial GLMMs with crossed random effects**, and
the R stack (lme4) did not survive the migration while `statsmodels` was never in the pinned env.
`statsmodels` IS installable — the login node has network — so it goes in a SEPARATE venv
(`envs/obtune-stats`) and this script re-execs itself there. The training env is not touched: an
analysis convenience must not be able to move a torch/scipy pin under a queued training job.

MODEL. One fit per condition, which keeps each coefficient directly interpretable as the contrast at
that condition instead of an interaction sum:

    correct ~ C(system, Treatment(<control>))   +  (1 | program_id)  +  (1 | item_id)

fitted by `BinomialBayesMixedGLM` (variational Bayes). `program_id` is the cluster the bootstrap
resamples, so the two methods are answering the same question two ways; `item_id` adds the item
difficulty the bootstrap leaves in the residual. Reported on the LOGIT scale — a GLMM coefficient is
a log-odds ratio and converting it to "points" would invent a number the model never estimated.

RULE (pre-registration #2, commit 8da96b4, frozen before the fit): for each headline contrast the
GLMM **agrees** with the bootstrap iff its posterior mean has the same sign as the bootstrap point
estimate AND its 95 % credible interval excludes zero iff the bootstrap CI did. Disagreements are
reported as disagreements. REPORTED, gates nothing, and it replaces no existing number.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

STATS_PY = Path("/work/jvl210002/migration/envs/obtune-stats/bin/python")
if "statsmodels" not in sys.modules:
    try:
        import statsmodels  # noqa: F401
    except ModuleNotFoundError:
        if STATS_PY.exists() and os.environ.get("_OBTUNE_GLMM_REEXEC") != "1":
            os.environ["_OBTUNE_GLMM_REEXEC"] = "1"
            os.execv(str(STATS_PY), [str(STATS_PY), *sys.argv])
        raise

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

PHASES = ["objectives_generic", "x1_generic", "rq1_generic", "rq2_generic"]
SYSTEMS = ["tuned_L0", "mono_all", "cons_lam3", "cons_lam1", "tuned_X1"]
CONDS = ck.SEEN + ["X1"]

# The four contrasts the paper rests on, with the bootstrap result each must be compared against
# (point estimate in pts and whether its 95 % CI excluded zero). Taken from fdr_codellama7b.json's
# `arms` family, which is the pre-registered primary family. The cons_lam3 - mono_all value comes from
# the mono_all-controlled family (an_fdr3, E7c), which is the only family that contains it.
HEADLINE = [
    ("mono_all", "tuned_L0", "X1", -3.79, True, "C1 — breadth loses on the unseen family"),
    ("cons_lam3", "mono_all", "X1", +4.86, True, "RQ3' — consistency beats breadth there"),
    ("mono_all", "tuned_L0", "L1b", +2.90, True, "breadth's seen-condition gain"),
    ("tuned_X1", "tuned_L0", "X1", +4.86, True, "the family result"),
]


def fit(df: pd.DataFrame, control: str, vc_item: bool = True) -> dict:
    """VB fit of correct ~ C(system) + (1|program_id) [+ (1|item_id)]."""
    d = df.copy()
    d["system"] = pd.Categorical(d["system"],
                                 categories=[control] + [s for s in sorted(d["system"].unique()) if s != control])
    vc = {"prog": "0 + C(program_id)"}
    if vc_item:
        vc["item"] = "0 + C(item_id)"
    m = BinomialBayesMixedGLM.from_formula("correct ~ C(system)", vc, d)
    r = m.fit_vb(verbose=False)
    out = {}
    for name, mean, sd in zip(r.model.exog_names, r.fe_mean, r.fe_sd):
        if not name.startswith("C(system)"):
            continue
        sysname = name.split("T.")[-1].rstrip("]")
        lo, hi = mean - 1.96 * sd, mean + 1.96 * sd
        out[sysname] = {"logit_mean": round(float(mean), 4), "logit_sd": round(float(sd), 4),
                        "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
                        "excludes_zero": bool(lo > 0 or hi < 0)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-item-effect", action="store_true", help="drop the (1|item_id) term")
    a = ap.parse_args()

    print(f"[glmm] interpreter {sys.executable}")
    block = ck.load_block(PHASES, a.model, SYSTEMS, CONDS, quiet=True)
    frames = []
    for s, d in block.items():
        for c, df in d.items():
            frames.append(pd.DataFrame({"correct": df["correct"].astype(float),
                                        "program_id": df["snippet_id"], "item_id": df["item_id"],
                                        "system": s, "cond": c}))
    data = pd.concat(frames, ignore_index=True)
    print(f"[glmm] {len(data):,} item-level rows, {data.program_id.nunique()} programs, "
          f"{data.system.nunique()} systems, {data.cond.nunique()} conditions")

    res = ck.new_result("RQ4' (support)", Path(__file__).name, [a.model])
    res["glmm"] = {"formula": "correct ~ C(system) + (1|program_id)" +
                   ("" if a.no_item_effect else " + (1|item_id)"),
                   "estimator": "BinomialBayesMixedGLM.fit_vb", "scale": "logit (log-odds ratio)",
                   "n_rows": int(len(data))}
    fits: dict[tuple[str, str], dict] = {}
    for cond in CONDS:
        sub = data[data.cond == cond]
        for control in ("tuned_L0", "mono_all"):
            if control not in set(sub.system):
                continue
            try:
                fits[(cond, control)] = fit(sub, control, vc_item=not a.no_item_effect)
            except Exception as e:                      # a VB failure is a result, not a crash
                print(f"[glmm] FAILED {cond} vs {control}: {type(e).__name__}: {e}", file=sys.stderr)
                fits[(cond, control)] = {}
        res["glmm"].setdefault("fits", {})[cond] = {
            f"vs_{c}": v for (cc, c), v in fits.items() if cc == cond}
        row = fits.get((cond, "tuned_L0"), {})
        print(f"\n--- {cond}  (vs tuned_L0, logit)")
        for s, v in sorted(row.items()):
            star = "*" if v["excludes_zero"] else " "
            print(f"   {star} {s:<12} {v['logit_mean']:+7.3f} [{v['ci_lo']:+.3f}, {v['ci_hi']:+.3f}]")

    print("\n=== agreement with the program-clustered bootstrap (the pre-registered rule) ===")
    agree = []
    for treat, control, cond, boot_pts, boot_sig, label in HEADLINE:
        v = fits.get((cond, control), {}).get(treat)
        if not v:
            print(f"  {treat} - {control} @ {cond:<4} GLMM UNAVAILABLE")
            continue
        same_sign = (v["logit_mean"] > 0) == (boot_pts > 0)
        same_sig = v["excludes_zero"] == boot_sig
        ok = same_sign and same_sig
        agree.append(ok)
        print(f"  {treat + ' - ' + control + ' @ ' + cond:<32} bootstrap {boot_pts:+6.2f} pts"
              f"{'*' if boot_sig else ' '}   GLMM {v['logit_mean']:+7.3f} "
              f"[{v['ci_lo']:+.3f}, {v['ci_hi']:+.3f}]{'*' if v['excludes_zero'] else ' '}"
              f"   -> {'AGREES' if ok else 'DISAGREES'}   ({label})")
        res["glmm"].setdefault("headline_agreement", {})[f"{treat} - {control} @ {cond}"] = {
            "bootstrap_pts": boot_pts, "bootstrap_excludes_zero": boot_sig,
            "glmm_logit": v["logit_mean"], "glmm_ci": [v["ci_lo"], v["ci_hi"]],
            "glmm_excludes_zero": v["excludes_zero"], "agrees": ok, "label": label}
    ck.hypothesis(res, "E7d-glmm",
                  "agrees iff same sign as the bootstrap AND same exclusion of zero (reported)",
                  "REPORTED", f"{sum(agree)}/{len(agree)} headline contrasts agree with the bootstrap")
    print()
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
