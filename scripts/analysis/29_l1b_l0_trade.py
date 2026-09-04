#!/usr/bin/env python
"""H-L1b-L0-trade: is breadth's L0 cost the same event as its L1b gain?

Every six-condition adapter measured on CodeLlama shows one shape against the clean-code
control (master report 22.5): L0 -1.4...-2.6, L1b +1.4...+3.9, the rest null, pooled a tie.
The hypothesis that opened is MECHANISTIC: breadth teaches "distrust the identifiers", which
is exactly what L1b (adversarial renaming) rewards and what L0 (meaningful names) punishes.
If that is right the two are ONE effect seen twice, and it has an item-level signature.

The test pairs items ACROSS conditions. `L0` and `L1b` differ only by the renaming transform,
so `<program>::L0::<i>` and `<program>::L1b::<i>` are the same program on the same input with
the SAME correct answer -- the pairing is exact, not a matched-sample approximation.

For each breadth adapter B and the control C = tuned_L0:
    d_L0(item)  = correct(B, L0, item)  - correct(C, L0, item)   in {-1, 0, +1}
    d_L1b(item) = correct(B, L1b, item) - correct(C, L1b, item)

  TRADE      predicts a NEGATIVE association: the items breadth loses on L0 are the items it
             wins on L1b.  corr(d_L0, d_L1b) < 0, and P(win L1b | lose L0) > P(win L1b).
  TWO EFFECTS predicts independence: corr ~ 0. Breadth would then be doing two unrelated
             things that happen to cancel, and "the trade" is a narrative laid over a tie.

Reported per adapter: the 3x3 flip contingency, the item-level correlation, the conditional
lift, and a PROGRAM-cluster bootstrap of the correlation (items within a program are
correlated; bootstrapping items would understate the interval -- CLAUDE.md 4).

THE CORRELATION ALONE CANNOT ANSWER IT, which is why `base` is in the arm list as a negative
control. Two systems compared on paired items share the items' difficulty, so d_L0 and d_L1b
are positively correlated for ANY pair -- and `base`, which is not a breadth adapter at all,
shows the strongest correlation of the lot. So the second test conditions on strata defined
ONLY by the control, which the treatment cannot influence:

    S_sensitive  control right on L0 and WRONG on L1b -- renaming alone broke it, so this is
                 where the identifiers are doing semantic work for the control
    S_robust     control right on both -- the identifiers are not load-bearing here

"Breadth distrusts identifiers" then predicts, sharply and without the difficulty confound:
  (a) breadth RECOVERS the renamed items: P(breadth right on L1b | S_sensitive) is high;
  (b) breadth PAYS for it on the clean parents of exactly those items:
      P(breadth wrong on L0 | S_sensitive) > P(breadth wrong on L0 | S_robust).
If (b) fails, the L0 cost is not the price of the L1b gain -- they are separate populations
of items and the "trade" is a story laid over a pooled tie.

Reads only existing cells. No GPU, no H1. Writes results/analysis/l1b_l0_trade_2026-09-04.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.config import RESULTS_DIR  # noqa: E402

CELLS = RESULTS_DIR / "cells"
NBOOT, SEED = 2000, 17

# (label, phase, model, system) for every six-condition adapter in the fingerprint, plus the
# control each is read against. 13B is read against the 13B control, not the 7B one.
ARMS = [
    ("mono_all s17",  "rq2_generic", "codellama-7b",  "mono_all",       "tuned_L0"),
    ("mono_all s42",  "rq2_generic", "codellama-7b",  "mono_all_s42",   "tuned_L0"),
    ("mono_all s101", "rq2_generic", "codellama-7b",  "mono_all_s101",  "tuned_L0"),
    ("mono_aug",      "rq2_generic", "codellama-7b",  "mono_aug",       "tuned_L0"),
    ("mono_scale",    "rq2_generic", "codellama-7b",  "mono_scale",     "tuned_L0"),
    ("mono_all 13B",  "rq2_generic", "codellama-13b", "mono_all",       "tuned_L0"),
    # THE DOSE LADDER, which is what separates the mechanism from item difficulty. Identifier-
    # sensitive items are simply harder, so EVERY system loses L0 on them more often -- `base`
    # posts a pay gap of the same size as the breadth adapters while being no kind of breadth
    # adapter at all. The question is therefore not "is there a gap" but "does the gap track
    # exposure to renaming". These specialists differ in exactly that and nothing else:
    #   tuned_L1b  trained ON adversarial renaming        -- maximum dose
    #   tuned_L1r / tuned_L2  trained on other renamings  -- partial dose
    #   tuned_S1 / tuned_S2   never saw a renaming        -- zero dose, pure difficulty baseline
    ("tuned_L1b",     "rq1_generic", "codellama-7b",  "tuned_L1b_s17",  "tuned_L0_s17"),
    ("tuned_L1r",     "rq1_generic", "codellama-7b",  "tuned_L1r_s17",  "tuned_L0_s17"),
    ("tuned_L2",      "rq1_generic", "codellama-7b",  "tuned_L2_s17",   "tuned_L0_s17"),
    ("tuned_S1",      "rq1_generic", "codellama-7b",  "tuned_S1_s17",   "tuned_L0_s17"),
    ("tuned_S2",      "rq1_generic", "codellama-7b",  "tuned_S2_s17",   "tuned_L0_s17"),
    # Negative control: a system that is NOT a breadth adapter. If the association turns up
    # here too it is a property of the item pairing, not of breadth training.
    ("base (control)", "rq2_generic", "codellama-7b", "base",           "tuned_L0"),
]


def load(phase: str, model: str, system: str, cond: str) -> pd.DataFrame | None:
    p = CELLS / phase / model / "python" / f"{system}__{cond}" / "trials.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p, columns=["item_id", "snippet_id", "correct"])
    # `<program>::<cond>::<i>` -> `<program>::<i>`, the condition-free identity of the case.
    d["case"] = d["item_id"].str.replace(f"::{cond}::", "::", regex=False)
    return d[["case", "snippet_id", "correct"]]


def deltas(phase, model, treat, ctrl):
    """One row per case present in all four cells, with d_L0 and d_L1b."""
    frames = {}
    for sysname, tag in ((treat, "t"), (ctrl, "c")):
        for cond in ("L0", "L1b"):
            d = load(phase, model, sysname, cond)
            if d is None:
                return None
            frames[(tag, cond)] = d.rename(columns={"correct": f"{tag}_{cond}"})
    m = frames[("t", "L0")]
    for k in [("c", "L0"), ("t", "L1b"), ("c", "L1b")]:
        m = m.merge(frames[k].drop(columns=["snippet_id"]), on="case", how="inner")
    m["d_L0"] = m["t_L0"].astype(int) - m["c_L0"].astype(int)
    m["d_L1b"] = m["t_L1b"].astype(int) - m["c_L1b"].astype(int)
    return m


def boot_stat(m: pd.DataFrame, fn) -> tuple[float, float, float]:
    """Program-cluster bootstrap of any statistic computed from the paired frame."""
    progs = m["snippet_id"].unique()
    by = {p: g for p, g in m.groupby("snippet_id")}
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(NBOOT):
        pick = rng.choice(len(progs), size=len(progs), replace=True)
        v = fn(pd.concat([by[progs[j]] for j in pick], ignore_index=True))
        if v is not None and np.isfinite(v):
            draws.append(v)
    d = np.asarray(draws)
    return float(fn(m)), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def _recover_sensitive(g):
    sel = (g["c_L0"] == 1) & (g["c_L1b"] == 0)
    return float(g.loc[sel, "t_L1b"].mean()) if sel.any() else None


def _pay_ratio(g):
    """L0 failure rate on identifier-sensitive items over the rate on robust ones.

    A RATIO, not a difference: `base` fails L0 on 46 % of robust items and every tuned system
    on 6-16 %, so a difference in points makes a weak system look mechanistically interesting
    when it is only bad everywhere. The ratio asks the mechanistic question -- is a system
    DISPROPORTIONATELY hurt on the clean parents of the items whose identifiers matter.
    """
    sens = (g["c_L0"] == 1) & (g["c_L1b"] == 0)
    rob = (g["c_L0"] == 1) & (g["c_L1b"] == 1)
    if not sens.any() or not rob.any():
        return None
    den = 1 - float(g.loc[rob, "t_L0"].mean())
    return (1 - float(g.loc[sens, "t_L0"].mean())) / den if den > 0 else None


def boot_corr(m: pd.DataFrame) -> tuple[float, float, float]:
    progs = m["snippet_id"].unique()
    by = {p: g[["d_L0", "d_L1b"]].to_numpy() for p, g in m.groupby("snippet_id")}
    rng = np.random.default_rng(SEED)
    draws = np.empty(NBOOT)
    for i in range(NBOOT):
        pick = rng.choice(len(progs), size=len(progs), replace=True)
        a = np.concatenate([by[progs[j]] for j in pick])
        # A resample can be constant in one column (all zeros); corrcoef is then undefined.
        draws[i] = 0.0 if a[:, 0].std() == 0 or a[:, 1].std() == 0 else float(
            np.corrcoef(a[:, 0], a[:, 1])[0, 1])
    point = float(np.corrcoef(m["d_L0"], m["d_L1b"])[0, 1])
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    return point, lo, hi


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(RESULTS_DIR / "analysis" / "l1b_l0_trade_2026-09-04.json"))
    args = ap.parse_args()

    report = {"n_boot": NBOOT, "seed": SEED, "arms": []}
    for label, phase, model, treat, ctrl in ARMS:
        m = deltas(phase, model, treat, ctrl)
        if m is None or not len(m):
            print(f"(skip {label}: cells missing)")
            continue
        r, lo, hi = boot_corr(m)
        lose_L0 = m["d_L0"] == -1
        win_L1b = m["d_L1b"] == 1
        p_win = float(win_L1b.mean())
        p_win_given_lose = float(win_L1b[lose_L0].mean()) if lose_L0.any() else float("nan")
        # Strata defined by the CONTROL alone -- the treatment cannot move them.
        sens = (m["c_L0"] == 1) & (m["c_L1b"] == 0)
        robust = (m["c_L0"] == 1) & (m["c_L1b"] == 1)
        strat = {
            "n_sensitive": int(sens.sum()), "n_robust": int(robust.sum()),
            # (a) does breadth recover the items renaming broke?
            "recover_L1b_given_sensitive": round(float(m.loc[sens, "t_L1b"].mean()), 4),
            "recover_L1b_given_robust": round(float(m.loc[robust, "t_L1b"].mean()), 4),
            # (b) does it pay for that on the clean parents of those same items?
            "lose_L0_given_sensitive": round(float(1 - m.loc[sens, "t_L0"].mean()), 4),
            "lose_L0_given_robust": round(float(1 - m.loc[robust, "t_L0"].mean()), 4),
        }
        strat["pay_gap_pts"] = round(
            (strat["lose_L0_given_sensitive"] - strat["lose_L0_given_robust"]) * 100, 2)
        rv, rlo, rhi = boot_stat(m, _recover_sensitive)
        pv, plo, phi = boot_stat(m, _pay_ratio)
        strat["recover_sensitive_ci"] = [round(rlo, 4), round(rhi, 4)]
        strat["pay_ratio"] = round(pv, 3)
        strat["pay_ratio_ci"] = [round(plo, 3), round(phi, 3)]

        cont = (m.groupby(["d_L0", "d_L1b"]).size()
                 .unstack(fill_value=0).reindex(index=[-1, 0, 1], columns=[-1, 0, 1],
                                                fill_value=0))
        arm = {
            "label": label, "model": model, "treat": treat, "control": ctrl,
            "n_cases": int(len(m)), "n_programs": int(m["snippet_id"].nunique()),
            "acc_L0_delta_pts": round(float(m["d_L0"].mean()) * 100, 2),
            "acc_L1b_delta_pts": round(float(m["d_L1b"].mean()) * 100, 2),
            "corr": round(r, 4), "ci": [round(lo, 4), round(hi, 4)],
            "excludes_zero": bool(lo > 0 or hi < 0),
            "p_win_L1b": round(p_win, 4),
            "p_win_L1b_given_lose_L0": round(p_win_given_lose, 4),
            "lift": round(p_win_given_lose / p_win, 3) if p_win else None,
            "n_lose_L0": int(lose_L0.sum()),
            **strat,
            "contingency": {f"d_L0={i}": {f"d_L1b={j}": int(cont.loc[i, j])
                                          for j in [-1, 0, 1]} for i in [-1, 0, 1]},
        }
        report["arms"].append(arm)
        print(f"\n{label}  ({arm['n_cases']} cases / {arm['n_programs']} programs)")
        print(f"  L0 {arm['acc_L0_delta_pts']:+.2f} pts   L1b {arm['acc_L1b_delta_pts']:+.2f} pts")
        print(f"  corr(d_L0, d_L1b) = {r:+.4f} [{lo:+.4f}, {hi:+.4f}]"
              f"{'  EXCLUDES 0' if arm['excludes_zero'] else ''}")
        print(f"  P(win L1b) = {p_win:.4f}   P(win L1b | lose L0) = {p_win_given_lose:.4f}"
              f"   lift {arm['lift']}   (n lose L0 = {arm['n_lose_L0']})")
        print(f"  (a) recovers L1b: {strat['recover_L1b_given_sensitive']:.4f} on sensitive"
              f" (n={strat['n_sensitive']}) vs {strat['recover_L1b_given_robust']:.4f} on robust"
              f" (n={strat['n_robust']})")
        print(f"  (a) recover CI    [{strat['recover_sensitive_ci'][0]:.4f},"
              f" {strat['recover_sensitive_ci'][1]:.4f}]")
        print(f"  (b) loses L0:     {strat['lose_L0_given_sensitive']:.4f} on sensitive"
              f" vs {strat['lose_L0_given_robust']:.4f} on robust"
              f"   -> gap {strat['pay_gap_pts']:+.2f} pts,"
              f" ratio {strat['pay_ratio']:.2f} [{strat['pay_ratio_ci'][0]:.2f},"
              f" {strat['pay_ratio_ci'][1]:.2f}]")

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
