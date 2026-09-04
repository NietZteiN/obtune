#!/usr/bin/env python
"""Accuracy-campaign arms (2026-09-03) read against the L0-only control, on the trainable grid.

Arms (all CodeLlama-7b, python, `heldout` source, six trainable conditions, NO H1):
  * mono_all seed band       — s17 / s42 / s101, each vs tuned_L0 (phase rq2_generic)
  * mono_aug                 — variant augmentation (K=3 re-seeds), vs tuned_L0 and vs mono_all
  * mono_scale, tuned_L0_scale — split-frozen data scale, vs their canonical counterparts
  * self-consistency         — plurality vote over n=8 samples vs the greedy cell of the SAME
                               system (phase selfcons_generic vs rq2_generic); the any-of-8
                               rate is printed as a ceiling and never enters a contrast.

Every contrast is a cluster bootstrap over PROGRAMS (control_relative.bootstrap_delta), on
the items both cells share, pooled over the six conditions and per condition. Nothing
here selects anything: it is a report. Writes results/analysis/campaign_2026-09-03.json.
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

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]


def load_system(phase: str, model: str, lang: str, system: str) -> pd.DataFrame | None:
    root = RESULTS_DIR / "cells" / phase / model / lang
    parts = []
    for c in CONDS:
        p = root / f"{system}__{c}" / "trials.parquet"
        if p.exists():
            parts.append(pd.read_parquet(p))
    if not parts:
        return None
    df = pd.concat(parts, ignore_index=True)
    df["system"] = system
    return df


def contrast(treat: pd.DataFrame, control: pd.DataFrame, label: str, n_boot: int) -> dict:
    out = {"label": label,
           "pooled": bootstrap_delta(treat, control, label, n_resamples=n_boot).to_dict(),
           "by_cond": {}}
    for c in CONDS:
        t, k = treat[treat.eval_cond == c], control[control.eval_cond == c]
        if len(t) and len(k):
            out["by_cond"][c] = bootstrap_delta(t, k, f"{label}[{c}]", n_resamples=n_boot).to_dict()
    return out


def fmt(c: dict) -> str:
    return (f"{c['value_pts']:+.2f} [{c['ci_lo']:+.2f}, {c['ci_hi']:+.2f}]  "
            f"(acc {c['acc_treatment']:.4f} vs {c['acc_control']:.4f}, {c['n_programs']} programs)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="codellama-7b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--out", default=str(RESULTS_DIR / "analysis" / "campaign_2026-09-03.json"))
    args = ap.parse_args()
    m, l, nb = args.model, args.language, args.n_boot
    rq2 = lambda s: load_system("rq2_generic", m, l, s)  # noqa: E731

    report: dict = {"model": m, "language": l, "contrasts": [], "selfcons": []}
    control = rq2("tuned_L0")
    base = rq2("base")
    if control is None:
        raise SystemExit("no tuned_L0 cells in rq2_generic — nothing to read against")

    def add(treat_name, treat, ctrl_name, ctrl):
        if treat is None or ctrl is None:
            print(f"  (skip {treat_name} - {ctrl_name}: missing)")
            return
        r = contrast(treat, ctrl, f"{treat_name} - {ctrl_name}", nb)
        report["contrasts"].append(r)
        print(f"\n{r['label']}\n  pooled  {fmt(r['pooled'])}")
        for c, v in r["by_cond"].items():
            print(f"  {c:<4}   {fmt(v)}")

    print("== seed band: mono_all vs tuned_L0 ==")
    for s in ["mono_all", "mono_all_s42", "mono_all_s101"]:
        add(s, rq2(s), "tuned_L0", control)

    print("\n== transform diversity ==")
    aug = rq2("mono_aug")
    add("mono_aug", aug, "tuned_L0", control)
    add("mono_aug", aug, "mono_all", rq2("mono_all"))

    print("\n== data scale ==")
    add("tuned_L0_scale", rq2("tuned_L0_scale"), "tuned_L0", control)
    add("mono_scale", rq2("mono_scale"), "mono_all", rq2("mono_all"))
    add("mono_scale", rq2("mono_scale"), "tuned_L0", control)

    print("\n== self-consistency (vote vs greedy, same system) ==")
    for s in ["base", "tuned_L0", "mono_all"]:
        sc = load_system("selfcons_generic", m, l, s)
        greedy = rq2(s)
        if sc is None or greedy is None:
            print(f"  (skip {s}: missing)")
            continue
        r = contrast(sc, greedy, f"vote8({s}) - greedy({s})", nb)
        ceiling = {c: round(float(sc[sc.eval_cond == c]["sc_any_correct"].mean()), 4)
                   for c in CONDS if (sc.eval_cond == c).any()}
        agree = round(float(sc["sc_agree"].mean()), 4)
        r["any_of_8_ceiling"] = ceiling
        r["any_of_8_pooled"] = round(float(sc["sc_any_correct"].mean()), 4)
        r["mean_agree"] = agree
        report["selfcons"].append(r)
        print(f"\n{r['label']}\n  pooled  {fmt(r['pooled'])}   any-of-8 {r['any_of_8_pooled']:.4f}  agree {agree:.3f}")
        for c, v in r["by_cond"].items():
            print(f"  {c:<4}   {fmt(v)}   any-of-8 {ceiling.get(c, float('nan')):.4f}")

    if base is not None:
        report["base_acc"] = {c: round(float(base[base.eval_cond == c]["correct"].mean()), 4) for c in CONDS}
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
