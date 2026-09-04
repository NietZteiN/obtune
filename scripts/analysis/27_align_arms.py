#!/usr/bin/env python
"""W5 — hidden-state alignment arms (2026-09-04) on the trainable grid, CodeLlama-7b.

Arms (`configs/eval/align_codellama7b.yaml`, phase rq2_generic, `heldout`, six conditions, NO H1):
  align_lam0 · align_lam0.3 · align_lam1 · align_lam1_mm (mismatched teacher) · align_lam3

Reads, in the order the decision rule needs them:
  1. PLUMBING  align_lam0 - mono_all        must sit inside the seed band (+0.01…+0.77 pooled;
                                            L0 -1.4…-2.6, L1b +1.4…+3.9 vs tuned_L0).
  2. OBJECTIVE align_lamX - mono_all        did adding L_align move anything at all?
  3. CONTROL   align_lam1 - align_lam1_mm   semantic (matched > mismatched) or regularizer (==)?
  4. HEADLINE  align_lamX - tuned_L0        is the L0 tax gone without giving back L1b?

Every contrast is a program-cluster bootstrap (control_relative.bootstrap_delta) on shared
items, pooled and per condition. Reuses 26_campaign_arms' loaders; reports only, selects
nothing. Writes results/analysis/align_2026-09-04.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from obtune.config import RESULTS_DIR  # noqa: E402

_spec = importlib.util.spec_from_file_location("campaign", HERE / "26_campaign_arms.py")
campaign = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(campaign)

ARMS = ["align_lam0", "align_lam0.3", "align_lam1", "align_lam1_mm", "align_lam3"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="codellama-7b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--out", default=str(RESULTS_DIR / "analysis" / "align_2026-09-04.json"))
    args = ap.parse_args()
    m, l, nb = args.model, args.language, args.n_boot
    rq2 = lambda s: campaign.load_system("rq2_generic", m, l, s)  # noqa: E731

    report: dict = {"model": m, "language": l, "contrasts": [], "acc": {}}
    sys_ = {s: rq2(s) for s in ["tuned_L0", "mono_all", *ARMS]}
    for s, df in sys_.items():
        if df is not None:
            report["acc"][s] = {c: round(float(df[df.eval_cond == c]["correct"].mean()), 4)
                                for c in campaign.CONDS if (df.eval_cond == c).any()}
            report["acc"][s]["pooled"] = round(float(df["correct"].mean()), 4)
    present = [a for a in ARMS if sys_[a] is not None]
    print(f"arms present: {present}")

    def add(t, k):
        if sys_[t] is None or sys_[k] is None:
            return
        r = campaign.contrast(sys_[t], sys_[k], f"{t} - {k}", nb)
        report["contrasts"].append(r)
        print(f"\n{r['label']}\n  pooled  {campaign.fmt(r['pooled'])}")
        for c, v in r["by_cond"].items():
            print(f"  {c:<4}   {campaign.fmt(v)}")

    print("\n== 1. plumbing: lambda=0 twin vs mono_all ==")
    add("align_lam0", "mono_all")
    print("\n== 2. objective: each arm vs mono_all ==")
    for a in ["align_lam0.3", "align_lam1", "align_lam1_mm", "align_lam3"]:
        add(a, "mono_all")
    print("\n== 3. control: matched vs mismatched teacher ==")
    add("align_lam1", "align_lam1_mm")
    print("\n== 4. headline: each arm vs tuned_L0 ==")
    for a in present:
        add(a, "tuned_L0")

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
