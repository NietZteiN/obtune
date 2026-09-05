#!/usr/bin/env python
"""OBJECTIVES campaign read (2026-09-05) — four new fine-tuning objectives, CodeLlama-7b,
trainable grid + X1. NO H1 (budget spent); X1 is the held-out-family read.

Arms (configs/eval/objectives_codellama7b.yaml, phase objectives_generic) against the
x1_generic controls that share the same eval rows (tuned_L0, tuned_X1, mono_all):

  O1 consistency   cons_lam1 · cons_lam3 · cons_same_lam1 (teacher on the SAME obfuscated input)
  O2 negatives     neg_ul · neg_data (mutant positives, no unlikelihood)
  O3 resample      x1_resample (three X1 surfaces, compute-matched to tuned_X1)
  O4 curriculum    curr_sft · curr_kl (continued from tuned_L0 on the five transformed conds)

Pre-registered decision rules (CLAUDE_SCRATCHPAD.md, committed before submission):
  H-cons     cons_lam1 - mono_all on X1 > 0 excl. 0  AND  cons_lam1 - cons_same_lam1 > 0
  H-neg      neg_ul - neg_data on X1 > 0 excl. 0;  neg_data - mono_all is the data-only read
  H-resample x1_resample - tuned_X1 on X1 > 0 excl. 0
  H-curr     curr_kl - tuned_L0 on L0 >= 0 (no tax)  AND  curr_kl - mono_all pooled non-L0 > 0;
             curr_kl - curr_sft separates the objective from the order
Every contrast is a program-cluster bootstrap on shared items. Reports only; selects nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.config import RESULTS_DIR  # noqa: E402
from obtune.control_relative import bootstrap_delta  # noqa: E402

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1"]
ARMS = ["cons_lam1", "cons_lam3", "cons_same_lam1", "neg_ul", "neg_data", "x1_resample", "curr_sft", "curr_kl"]
CONTROLS = {"tuned_L0": "x1_generic", "tuned_X1": "x1_generic", "mono_all": "x1_generic",
            "tuned_S2": "x1_generic", "mono_allX": "x1_generic"}


def load_system(phase, model, lang, system):
    root = RESULTS_DIR / "cells" / phase / model / lang
    parts = [pd.read_parquet(p) for c in CONDS if (p := root / f"{system}__{c}" / "trials.parquet").exists()]
    if not parts:
        return None
    df = pd.concat(parts, ignore_index=True)
    df["correct"] = df["correct"].astype(bool)
    df["system"] = system
    return df


def contrast(t, k, label, nb, conds=CONDS):
    out = {"label": label, "pooled": bootstrap_delta(t, k, label, n_resamples=nb).to_dict(), "by_cond": {}}
    for c in conds:
        tt, kk = t[t.eval_cond == c], k[k.eval_cond == c]
        if len(tt) and len(kk):
            out["by_cond"][c] = bootstrap_delta(tt, kk, f"{label} [{c}]", n_resamples=nb).to_dict()
    non = t[t.eval_cond != "L0"], k[k.eval_cond != "L0"]
    if len(non[0]) and len(non[1]):
        out["pooled_nonL0"] = bootstrap_delta(non[0], non[1], f"{label} [non-L0]", n_resamples=nb).to_dict()
    return out


def fmt(c):
    star = "*" if (c["ci_lo"] > 0 or c["ci_hi"] < 0) else " "
    return (f"{c['value_pts']:+.2f} [{c['ci_lo']:+.2f}, {c['ci_hi']:+.2f}]{star} "
            f"(acc {c['acc_treatment']:.4f} vs {c['acc_control']:.4f}, {c['n_programs']} prog)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="codellama-7b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--out", default=str(RESULTS_DIR / "analysis" / "objectives_2026-09-05.json"))
    args = ap.parse_args()
    m, l, nb = args.model, args.language, args.n_boot

    S = {a: load_system("objectives_generic", m, l, a) for a in ARMS}
    S.update({k: load_system(ph, m, l, k) for k, ph in CONTROLS.items()})
    present = [a for a in ARMS if S[a] is not None]
    print(f"arms present: {present}")
    report = {"model": m, "language": l, "acc": {}, "contrasts": []}
    for s, df in S.items():
        if df is not None:
            report["acc"][s] = {c: round(float(df[df.eval_cond == c]["correct"].mean()), 4)
                                for c in CONDS if (df.eval_cond == c).any()}
            report["acc"][s]["pooled"] = round(float(df["correct"].mean()), 4)
            report["acc"][s]["format_fail"] = round(float(df["format_fail"].astype(bool).mean()), 4)

    def add(t, k):
        if S.get(t) is None or S.get(k) is None:
            print(f"  (skip {t} - {k}: missing)"); return
        r = contrast(S[t], S[k], f"{t} - {k}", nb)
        report["contrasts"].append(r)
        print(f"\n{r['label']}\n  pooled   {fmt(r['pooled'])}")
        if "pooled_nonL0" in r:
            print(f"  non-L0   {fmt(r['pooled_nonL0'])}")
        for c, v in r["by_cond"].items():
            print(f"  {c:<5}    {fmt(v)}")

    print("\n== accuracy table ==")
    hdr = ["system"] + CONDS + ["pooled"]
    print("  " + "  ".join(f"{h:>8}" for h in hdr))
    for s in ["tuned_L0", "mono_all", "tuned_X1", "mono_allX", *present]:
        if s in report["acc"]:
            a = report["acc"][s]
            print("  " + "  ".join([f"{s:>8}"[:16].rjust(14)] + [f"{a.get(c, float('nan')):8.4f}" for c in CONDS + ['pooled']]))

    print("\n== H-cons: consistency vs same-data control, and vs the same-input teacher control ==")
    for a in ["cons_lam1", "cons_lam3", "cons_same_lam1"]:
        add(a, "mono_all")
    add("cons_lam1", "cons_same_lam1"); add("cons_lam3", "cons_same_lam1")
    add("cons_lam1", "tuned_L0"); add("cons_lam3", "tuned_L0")
    print("\n== H-neg: unlikelihood vs data-only control; data-only vs mono_all ==")
    add("neg_ul", "neg_data"); add("neg_data", "mono_all"); add("neg_ul", "mono_all"); add("neg_ul", "tuned_L0")
    print("\n== H-resample: three X1 surfaces vs one, compute-matched ==")
    add("x1_resample", "tuned_X1"); add("x1_resample", "mono_allX")
    print("\n== H-curr: continued from tuned_L0 ==")
    add("curr_sft", "tuned_L0"); add("curr_kl", "tuned_L0")
    add("curr_sft", "mono_all"); add("curr_kl", "mono_all"); add("curr_kl", "curr_sft")

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}   (* = interval excludes zero)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
