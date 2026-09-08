#!/usr/bin/env python
"""Stacked-obfuscation (composite) contrasts — RQ-A / RQ-B, and the paper's RQ1'.

Reads the `composite_generic` cells for one model, pools the six composites and
reports every pre-registered contrast with a program-clustered bootstrap. The
decision rules live in CLAUDE_SCRATCHPAD.md (2026-09-07 pre-registration) and
are applied verbatim here so a re-run cannot drift from them:

  RQ-A  CONFIRM iff  mono_all - tuned_L0  pooled > 0 (interval excludes zero above)
  RQ-B  CONFIRM iff  cons_lam3 - tuned_L0 pooled > 0  AND
                     cons_lam3 - mono_all pooled does NOT exclude zero from below

Never reads an H1 cell. `--out` is required so a dated artifact is never
overwritten by accident.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.control_relative import bootstrap_delta  # noqa: E402

COMPOSITES = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
SYSTEMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_S2"]
PAIRS = [("mono_all", "tuned_L0"), ("cons_lam3", "tuned_L0"), ("cons_lam3", "mono_all"),
         ("tuned_S2", "tuned_L0"), ("tuned_L0", "base")]


def load(cells: Path, system: str, cond: str) -> pd.DataFrame | None:
    p = cells / f"{system}__{cond}" / "trials.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    df["condition"] = cond
    # clusters are PROGRAMS (raw snippet_id): the same program under two
    # composites is one correlated cluster, so pooling resamples it as one unit.
    # Qualifying the id by composite would narrow the pooled interval.
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--phase", default="composite_generic")
    ap.add_argument("--out", required=True)
    ap.add_argument("--systems", nargs="*", default=SYSTEMS)
    ap.add_argument("--alias", nargs="*", default=[],
                    help="canonical=on_disk, e.g. tuned_L0=tuned_L0_s17 for the Qwen grid")
    ap.add_argument("--composites", nargs="*", default=None,
                    help="override the composite list (RQ-C depth leg: the C3_/C4_ codes)")
    ap.add_argument("--common", action="store_true",
                    help="restrict every cell to programs present in ALL composites (coverage honesty)")
    ap.add_argument("--ref-json", default=None,
                    help="depth-2 composites json; RQ-C compares the pooled breadth gain against its value")
    a = ap.parse_args()
    alias = dict(kv.split("=", 1) for kv in a.alias)
    global COMPOSITES
    if a.composites:
        COMPOSITES = list(a.composites)

    cells = ROOT / "results" / "cells" / a.phase / a.model / "python"
    data: dict[str, dict[str, pd.DataFrame]] = {}
    for s in a.systems:
        for c in COMPOSITES:
            df = load(cells, alias.get(s, s), c)
            if df is not None:
                data.setdefault(s, {})[c] = df
    missing = [(s, c) for s in a.systems for c in COMPOSITES if c not in data.get(s, {})]
    if missing:
        print(f"[composites] MISSING cells: {missing}", file=sys.stderr)
    if a.common:
        # S1/S3/S4 bail on some programs by design; a depth-4 composite only exists where
        # every part succeeded. Pooling across depths without this would confound depth
        # with program difficulty (CLAUDE.md §4 "coverage honesty").
        keep = None
        for s in data.values():
            for df in s.values():
                keep = set(df["snippet_id"]) if keep is None else keep & set(df["snippet_id"])
        for s in data:
            for c in list(data[s]):
                data[s][c] = data[s][c][data[s][c]["snippet_id"].isin(keep)]
        print(f"[composites] --common: {len(keep or [])} programs present in every cell")

    out: dict = {"model": a.model, "phase": a.phase, "alias": alias, "n_cells": sum(len(v) for v in data.values()),
                 "accuracy": {}, "format_fail": {}, "per_composite": {}, "pooled": {}, "verdicts": {}}
    for s, d in data.items():
        out["accuracy"][s] = {c: round(float(df["correct"].mean()), 4) for c, df in d.items()}
        out["format_fail"][s] = {c: round(float(df["format_fail"].mean()), 4) for c, df in d.items()}
        pooled = pd.concat(d.values())
        out["accuracy"][s]["pooled"] = round(float(pooled["correct"].mean()), 4)

    def pool(s: str) -> pd.DataFrame:
        return pd.concat(data[s].values())

    for t, ctl in PAIRS:
        if t not in data or ctl not in data:
            continue
        lab = f"{t} - {ctl}"
        out["pooled"][lab] = bootstrap_delta(pool(t), pool(ctl), lab).to_dict()
        out["per_composite"][lab] = {
            c: bootstrap_delta(data[t][c], data[ctl][c], lab).to_dict()
            for c in COMPOSITES if c in data[t] and c in data[ctl]}

    # frozen rules — see module docstring
    A = out["pooled"].get("mono_all - tuned_L0")
    B1 = out["pooled"].get("cons_lam3 - tuned_L0")
    B2 = out["pooled"].get("cons_lam3 - mono_all")
    if not a.ref_json:  # the depth-2 run; RQ-A / RQ-B verdicts belong to it alone
        if A:
            out["verdicts"]["RQ-A"] = "CONFIRMED" if A["ci_lo"] > 0 else "REFUTED"
        if B1 and B2:
            out["verdicts"]["RQ-B"] = "CONFIRMED" if (B1["ci_lo"] > 0 and not B2["ci_hi"] < 0) else "REFUTED"

    # RQ-C (depth leg): does breadth's stacking gain persist / grow beyond depth 2?
    if a.ref_json and A:
        ref = json.loads(Path(a.ref_json).read_text())["pooled"].get("mono_all - tuned_L0", {})
        ref_pt = ref.get("value_pts")
        out["ref_depth2"] = {"mono_all - tuned_L0": ref}
        out["verdicts"]["RQ-C-persists"] = "CONFIRMED" if A["ci_lo"] > 0 else "REFUTED"
        if ref_pt is not None:
            out["verdicts"]["RQ-C-grows"] = ("CONFIRMED" if A["ci_lo"] > ref_pt else
                                            "REFUTED" if A["ci_hi"] < ref_pt else "INCONCLUSIVE")
        if B1:
            out["verdicts"]["RQ-C-cons-persists"] = "CONFIRMED" if B1["ci_lo"] > 0 else "REFUTED"

    # order pair, reported either way
    if "tuned_L0" in data:
        out["order_pair"] = {s: {"C_L1r_S1": out["accuracy"][s].get("C_L1r_S1"),
                                 "C_S1_L1r": out["accuracy"][s].get("C_S1_L1r")}
                             for s in data}

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))

    print(f"=== {a.model} composites ({out['n_cells']} cells) ===")
    print(f"{'system':<12}" + "".join(f"{c:>10}" for c in COMPOSITES) + f"{'pooled':>10}")
    for s in data:
        acc = out["accuracy"][s]
        print(f"{s:<12}" + "".join(f"{acc.get(c, float('nan')):>10.4f}" for c in COMPOSITES) + f"{acc['pooled']:>10.4f}")
    print()
    for lab, c in out["pooled"].items():
        star = "*" if c["excludes_zero"] else ""
        print(f"  {lab:<24} pooled {c['value_pts']:+6.2f} [{c["ci_lo"]:+.2f}, {c["ci_hi"]:+.2f}]{star}")
        per = out["per_composite"][lab]
        print("      " + "  ".join(f"{k}:{v['value_pts']:+.2f}" for k, v in per.items()))
    print()
    for k, v in out["verdicts"].items():
        print(f"  {k}: {v}")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
