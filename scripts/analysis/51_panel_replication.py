#!/usr/bin/env python
"""Read R1-R4 for every panel model that has a complete panel_core grid.

    python scripts/analysis/51_panel_replication.py [--json OUT]

The rules are the ones frozen in CLAUDE_SCRATCHPAD.md (commit d63340c) BEFORE any panel cell
existed, reproduced here verbatim so the script cannot drift from them:

  R1  mono_all  - tuned_L0 @ X1   REPLICATED iff ci_hi < 0   REFUTED iff ci_lo > 0
  R2  cons_lam3 - mono_all  @ X1   REPLICATED iff ci_lo > 0   REFUTED iff ci_hi < 0
  R3  cons_lam3 - tuned_L0  @ L0   REPLICATED iff ci_hi >= 0
  R4  mono_all  - tuned_L0 pooled over the five obfuscated ladder conditions -- REPORTED only

A model missing an arm is SKIPPED with its missing arms named, never silently partially read.
Contrasts are program-clustered bootstraps (2,000 resamples, seed 17) on intersected items, the
same estimator as every other contrast in this project. Cells are filtered to the FORWARD task by
prompt_id: the inverse cells share (system, condition) names and would otherwise collide.
"""
from __future__ import annotations

import argparse, glob, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

PUBLISHED = {"R1": "-3.79 / -4.28 / -2.64 (CodeLlama 7/13/34B), -2.88 (Llama-3.1-8B)",
             "R2": "+4.59 / +3.95 / +3.38, +3.46",
             "R3": "-0.30 / -0.60 / +0.42, +0.00 (never significantly negative)"}
ARMS = ["base", "tuned_L0", "tuned_X1", "mono_all", "cons_lam3"]
OBF = ["L1b", "L1r", "L2", "S1", "S2"]


def cell(model, system, cond):
    import pandas as pd
    p = f"results/cells/panel_core/{model}/python/{system}__{cond}/trials.parquet"
    if not os.path.exists(p):
        return None
    df = pd.read_parquet(p)
    if df.empty or str(df["prompt_id"].iloc[0]).startswith("inverse"):
        return None
    return df


def boot(a, b, n=2000, seed=17):
    import numpy as np
    a = a.set_index("item_id"); b = b.set_index("item_id")
    k = a.index.intersection(b.index)
    if len(k) == 0:
        return None
    a, b = a.loc[k], b.loc[k]
    g = {}
    for i, p in enumerate(a["snippet_id"].values):
        g.setdefault(p, []).append(i)
    ca = a["correct"].values.astype(float); cb = b["correct"].values.astype(float)
    ks = list(g); rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        idx = np.concatenate([g[ks[j]] for j in rng.choice(len(ks), len(ks), replace=True)])
        out.append(ca[idx].mean() - cb[idx].mean())
    lo, hi = np.percentile(out, [2.5, 97.5])
    return {"delta_pts": (ca.mean() - cb.mean()) * 100, "ci_lo": lo * 100, "ci_hi": hi * 100,
            "n_items": int(len(k)), "n_programs": len(ks)}


def pooled(model, a_sys, b_sys):
    """Concatenate the obfuscated conditions, then bootstrap once over the union."""
    import pandas as pd
    A = [cell(model, a_sys, c) for c in OBF]; B = [cell(model, b_sys, c) for c in OBF]
    if any(x is None for x in A + B):
        return None
    def tag(frames):
        out = []
        for c, d in zip(OBF, frames):
            d = d.copy(); d["item_id"] = c + "::" + d["item_id"].astype(str); out.append(d)
        return pd.concat(out, ignore_index=True)
    return boot(tag(A), tag(B))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    models = sorted({p.split("/")[3] for p in glob.glob("results/cells/panel_core/*/python/*/trials.parquet")})
    report = {}
    for m in models:
        have = {s: {c: cell(m, s, c) is not None for c in ["L0", "X1"] + OBF} for s in ARMS}
        missing = [s for s in ARMS if not have[s]["X1"] or not have[s]["L0"]]
        print(f"\n=== {m} ===")
        if missing:
            print(f"  SKIPPED — incomplete grid, missing L0/X1 for: {missing}")
            report[m] = {"skipped": True, "missing": missing}
            continue
        r = {}
        for key, (x, y, cond, rule) in {
            "R1": ("mono_all", "tuned_L0", "X1", "ci_hi<0"),
            "R2": ("cons_lam3", "mono_all", "X1", "ci_lo>0"),
            "R3": ("cons_lam3", "tuned_L0", "L0", "ci_hi>=0"),
        }.items():
            res = boot(cell(m, x, cond), cell(m, y, cond))
            if res is None:
                continue
            lo, hi = res["ci_lo"], res["ci_hi"]
            v = ("REPLICATED" if (hi < 0 if key == "R1" else (lo > 0 if key == "R2" else hi >= 0))
                 else ("REFUTED" if (lo > 0 if key == "R1" else (hi < 0 if key in ("R2", "R3") else False))
                       else "INCONCLUSIVE"))
            res["verdict"] = v; r[key] = res
            print(f"  {key}  {x} - {y} @ {cond:3s}  {res['delta_pts']:+6.2f} "
                  f"[{lo:+6.2f}, {hi:+6.2f}]  -> {v}   (published {PUBLISHED[key]})")
        p4 = pooled(m, "mono_all", "tuned_L0")
        if p4:
            r["R4"] = p4
            print(f"  R4  mono_all - tuned_L0 pooled obf   {p4['delta_pts']:+6.2f} "
                  f"[{p4['ci_lo']:+6.2f}, {p4['ci_hi']:+6.2f}]  -> REPORTED (not verdicted)")
        report[m] = r

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(report, indent=2))
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
