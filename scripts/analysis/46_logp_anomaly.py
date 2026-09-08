#!/usr/bin/env python
"""E14 — is mono_all's log P(gold) deficit specific to the UNSEEN family, or global? NO H1.

`an_attention` (2026-09-08) refuted both RQ4' knockout hypotheses — the instrument moves gold
log-probability by < 0.5 % for every arm — but left one unplanned observation: on X1 the CLEAN
(un-knocked) mean log P(gold) is -11.42 for mono_all against -6.3 for tuned_L0 and cons_lam3, a gap
sitting exactly where the unseen-family tax is. One number from an instrument that turned out inert
is not a finding, so this read does two things and nothing more:

  1. establishes whether the gap is REAL — paired on the same items, bootstrapped by program, and
     checked against the two artifacts that could manufacture it: gold-token count (log P is a SUM,
     so a longer answer is mechanically more negative) and a heavy tail (a handful of catastrophic
     items rather than a shift);
  2. establishes whether it is SPECIFIC to the unseen family, using the L0 and S2 extractions
     submitted for this purpose (the pre-existing dumps carry all five arms on X1 only).

REPORTED, not verdicted (pre-registration #2, commit 8da96b4). Nothing here gates or ranks anything.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

KO = ck.ROOT / "results" / "attn" / "knockout"
CONDS = ["L0", "S2", "X1"]
SYSTEMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]
ACC_PHASES = ["objectives_generic", "x1_generic", "rq1_generic", "rq2_generic"]
N_BOOT, SEED = 2000, 17


def load(model: str, cond: str, system: str) -> pd.DataFrame | None:
    """Dump names differ by vintage: the X1 batch is <system>.json, the older per-condition
    batch is <system>__<model>_<system>_<cond>.json. Accept either."""
    d = KO / model / cond
    for p in (d / f"{system}.json", *sorted(d.glob(f"{system}__*.json"))):
        if p.exists():
            rows = json.load(p.open())["rows"]
            df = pd.DataFrame(rows)
            df["system"], df["cond"] = system, cond
            return df
    return None


def paired(a: pd.DataFrame, b: pd.DataFrame, col: str) -> dict:
    """Program-clustered bootstrap of mean(a - b) over the items both arms scored."""
    m = a.merge(b, on=["item_id", "program_id"], suffixes=("_a", "_b"))
    if m.empty:
        return {}
    d = (m[f"{col}_a"] - m[f"{col}_b"]).to_numpy()
    progs = m["program_id"].to_numpy()
    uniq = np.unique(progs)
    idx = {p: np.where(progs == p)[0] for p in uniq}
    rng = np.random.default_rng(SEED)
    draws = np.empty(N_BOOT)
    for i in range(N_BOOT):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        draws[i] = d[np.concatenate([idx[p] for p in pick])].mean()
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    trimmed = float(np.mean(np.sort(d)[int(0.1 * len(d)):len(d) - int(0.1 * len(d))]))
    return {"mean_delta": round(float(d.mean()), 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
            "median_delta": round(float(np.median(d)), 4), "trimmed10_mean": round(trimmed, 4),
            "frac_worse": round(float((d < 0).mean()), 4), "n_items": int(len(d)),
            "n_programs": int(len(uniq)), "excludes_zero": bool(lo > 0 or hi < 0)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ4' (support)", Path(__file__).name, [a.model])

    data: dict[tuple[str, str], pd.DataFrame] = {}
    for c in CONDS:
        for s in SYSTEMS:
            df = load(a.model, c, s)
            if df is not None:
                df["logp_per_gold"] = df["logp_clean"] / df["n_gold_tokens"].clip(lower=1)
                data[(c, s)] = df

    print(f"=== {a.model}: clean log P(gold), by condition and arm ===")
    print(f"{'cond':<5} {'system':<12} {'n':>5} {'mean logp':>11} {'median':>9} {'per gold tok':>13} {'gold toks':>10}")
    res["logp"] = {}
    for (c, s), df in sorted(data.items()):
        row = {"n_items": int(len(df)), "mean_logp_clean": round(float(df.logp_clean.mean()), 4),
               "median_logp_clean": round(float(df.logp_clean.median()), 4),
               "mean_logp_per_gold_token": round(float(df.logp_per_gold.mean()), 4),
               "mean_n_gold_tokens": round(float(df.n_gold_tokens.mean()), 2)}
        res["logp"].setdefault(c, {})[s] = row
        print(f"{c:<5} {s:<12} {row['n_items']:>5} {row['mean_logp_clean']:>11.3f} "
              f"{row['median_logp_clean']:>9.3f} {row['mean_logp_per_gold_token']:>13.3f} "
              f"{row['mean_n_gold_tokens']:>10.2f}")

    print("\n=== paired contrasts vs tuned_L0 (same items, bootstrap by program) ===")
    res["contrasts_logp"] = {}
    for c in CONDS:
        if (c, "tuned_L0") not in data:
            continue
        for s in ("mono_all", "cons_lam3", "tuned_X1", "base"):
            if (c, s) not in data:
                continue
            for col, tag in (("logp_clean", "sum"), ("logp_per_gold", "per-token")):
                r = paired(data[(c, s)], data[(c, "tuned_L0")], col)
                if not r:
                    continue
                res["contrasts_logp"][f"{s} - tuned_L0 @ {c} ({tag})"] = r
                star = "*" if r["excludes_zero"] else ""
                print(f"  {s + ' - tuned_L0 @ ' + c:<28} {tag:<9} {r['mean_delta']:+8.3f} "
                      f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]{star}  median {r['median_delta']:+7.3f}"
                      f"  trimmed10 {r['trimmed10_mean']:+7.3f}  worse on {r['frac_worse']:.0%} of items"
                      f"  n={r['n_items']}")

    # Does the deficit track being WRONG on the same items? Join the accuracy cells for the
    # 150 scored items. Descriptive: a within-arm point-biserial, never a test.
    print("\n=== does clean log P(gold) track correctness on the same items? ===")
    res["logp_vs_correct"] = {}
    for c in CONDS:
        block = ck.load_block(ACC_PHASES, a.model, [s for s in SYSTEMS if (c, s) in data], [c], quiet=True)
        for s, d in block.items():
            if c not in d or (c, s) not in data:
                continue
            acc = d[c].groupby("item_id")["correct"].mean().rename("acc")
            j = data[(c, s)].join(acc, on="item_id").dropna(subset=["acc"])
            if len(j) < 20:
                continue
            r = float(np.corrcoef(j.logp_clean, j.acc)[0, 1])
            hi = float(j.loc[j.acc >= 0.5, "logp_clean"].mean())
            lo = float(j.loc[j.acc < 0.5, "logp_clean"].mean())
            res["logp_vs_correct"].setdefault(c, {})[s] = {
                "pearson_r": round(r, 4), "mean_logp_correct": round(hi, 3),
                "mean_logp_wrong": round(lo, 3), "n_items": int(len(j))}
            print(f"  {c:<4} {s:<12} r={r:+.3f}  correct {hi:+8.3f} vs wrong {lo:+8.3f}  n={len(j)}")

    have = sorted({c for c, _ in data})
    x1 = res["contrasts_logp"].get("mono_all - tuned_L0 @ X1 (sum)", {})
    ev = (f"X1 {x1.get('mean_delta')} [{x1.get('ci_lo')}, {x1.get('ci_hi')}]"
          if x1 else "X1 contrast unavailable")
    others = "; ".join(f"{c} {res['contrasts_logp'].get(f'mono_all - tuned_L0 @ {c} (sum)', {}).get('mean_delta')}"
                       for c in have if c != "X1")
    ck.hypothesis(res, "E14-logp", "reported: is mono_all's clean log P(gold) deficit real and X1-specific?",
                  "REPORTED", f"conditions with all arms: {have}. mono_all - tuned_L0: {ev}; {others}")
    print()
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
