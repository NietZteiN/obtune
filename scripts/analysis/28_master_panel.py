#!/usr/bin/env python
"""Master-report panel for the CodeLlama era (2026-09-04 revision).

`make_master_report.py` builds the Qwen-1.5B tables the 08-12/08-27 revisions rest on.
This script does the same job for everything trained since the juno migration: the
CodeLlama-7b replication, the 13B rung, the accuracy campaign, and the W5 alignment arms.
It recomputes from the per-cell parquets only -- nothing is copied from a log entry.

Outputs results/analysis/master_panel_2026-09-04.json:
  inventory   cells / trials / date span, by phase x model x language
  panel       system x eval_cond accuracy for every CodeLlama system, per phase, with n
  panel_common  the same accuracies on the ALL-CONDITIONS-SUCCEEDED common subset, which is
              what CLAUDE.md 4 requires of a headline transfer number: S1/S2 bail on some
              programs by design, so an unrestricted mean compares cells built on different
              program sets
  deltas      each system - tuned_L0 (same phase/model), program cluster bootstrap, pooled
              and per condition, on the items the pair shares
  scale       codellama-13b - codellama-7b for the systems present on both
H1 cells are READ ONLY where they already exist (phase h1_codellama); no stimulus is
touched and no new quarantine budget is spent -- CLAUDE.md 3.2 rule 3 counts reads of
`data/quarantine/`, not re-aggregation of results that a logged read already produced.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.control_relative import bootstrap_delta  # noqa: E402

CELLS = ROOT / "results" / "cells"
OUT = ROOT / "results" / "analysis" / "master_panel_2026-09-04.json"
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "H1"]
NBOOT = 2000
# Phases that make up the CodeLlama panel. `_contaminated_*` and `_misplaced_*` are
# quarantined directories and are deliberately not read.
PHASES = ["rq1_generic", "rq2_generic", "loto_generic", "mole_generic", "mole_generic_testset",
          "merge_sweep_generic", "rank_generic", "extra_generic", "baselines_generic",
          "basecheck", "selfcons_generic", "h1_codellama"]


def cell_frames(phase: str, model: str, lang: str):
    root = CELLS / phase / model / lang
    if not root.is_dir():
        return {}
    out: dict[str, list[pd.DataFrame]] = defaultdict(list)
    for d in sorted(root.iterdir()):
        p = d / "trials.parquet"
        if not p.exists() or "__" not in d.name:
            continue
        out[d.name.rsplit("__", 1)[0]].append(pd.read_parquet(p))
    return {k: pd.concat(v, ignore_index=True) for k, v in out.items()}


def main() -> int:
    report: dict = {"generated_for": "MASTER_REPORT_2026-09-04.md", "n_boot": NBOOT,
                    "inventory": {}, "panel": {}, "panel_common": {}, "deltas": {}, "scale": {}}

    # ---- inventory: every cell under results/cells, including the Qwen era ----
    inv: dict[str, dict] = {}
    total_cells = total_trials = 0
    for p in sorted(CELLS.rglob("trials.parquet")):
        rel = p.relative_to(CELLS).parts
        if rel[0].startswith("_"):
            key = f"[quarantined] {rel[0]}"
        else:
            key = "/".join(rel[:3])
        df = pd.read_parquet(p, columns=["correct"])
        e = inv.setdefault(key, {"cells": 0, "trials": 0})
        e["cells"] += 1
        e["trials"] += len(df)
        total_cells += 1
        total_trials += len(df)
    report["inventory"] = {"by_group": dict(sorted(inv.items())),
                           "total_cells": total_cells, "total_trials": total_trials}

    # ---- panel + deltas, per phase x model ----
    for model in ["codellama-7b", "codellama-13b"]:
        for phase in PHASES:
            frames = cell_frames(phase, model, "python")
            if not frames:
                continue
            key = f"{phase}/{model}/python"
            rows = {}
            for name, df in sorted(frames.items()):
                r = {c: round(float(df[df.eval_cond == c]["correct"].mean()), 4)
                     for c in CONDS if (df.eval_cond == c).any()}
                r["n_items"] = int(len(df))
                r["n_programs"] = int(df["snippet_id"].nunique())
                if "format_fail" in df:
                    r["format_fail"] = round(float(df["format_fail"].fillna(False).mean()), 4)
                rows[name] = r
            report["panel"][key] = rows

            # Common subset: programs covered in EVERY trainable condition, taken from the
            # reference system that has them all. Intersecting per system instead would let
            # a system with one thin cell shrink the subset for everybody.
            ref = frames.get("base", next(iter(frames.values())))
            sets = [set(ref[ref.eval_cond == c]["snippet_id"]) for c in CONDS
                    if (ref.eval_cond == c).any()]
            common = set.intersection(*sets) if sets else set()
            crows = {}
            for name, df in sorted(frames.items()):
                sub = df[df["snippet_id"].isin(common)]
                if not len(sub):
                    continue
                r = {c: round(float(sub[sub.eval_cond == c]["correct"].mean()), 4)
                     for c in CONDS if (sub.eval_cond == c).any()}
                present6 = [c for c in CONDS[:6] if c in r]
                if len(present6) == 6:
                    r["mean6"] = round(sum(r[c] for c in present6) / 6, 4)
                r["n_items"] = int(len(sub))
                r["n_programs"] = int(sub["snippet_id"].nunique())
                crows[name] = r
            report["panel_common"][key] = crows

            cname = "tuned_L0" if "tuned_L0" in frames else (
                "tuned_L0_s17" if "tuned_L0_s17" in frames else None)
            if cname is None:
                continue
            ctrl = frames[cname]
            ds = {}
            for name, df in sorted(frames.items()):
                if name == cname:
                    continue
                d = {"pooled": bootstrap_delta(df, ctrl, name, n_resamples=NBOOT).to_dict(),
                     "by_cond": {}}
                for c in CONDS:
                    t, k = df[df.eval_cond == c], ctrl[ctrl.eval_cond == c]
                    if len(t) and len(k):
                        d["by_cond"][c] = bootstrap_delta(t, k, f"{name}[{c}]",
                                                          n_resamples=NBOOT).to_dict()
                ds[name] = d
            report["deltas"][key] = ds

    # ---- model scale: 13B - 7B on the systems present on both, same items ----
    for phase in PHASES:
        a = cell_frames(phase, "codellama-13b", "python")
        b = cell_frames(phase, "codellama-7b", "python")
        shared = sorted(set(a) & set(b))
        if not shared:
            continue
        out = {}
        for name in shared:
            d = {"pooled": bootstrap_delta(a[name], b[name], f"13b-7b {name}",
                                           n_resamples=NBOOT).to_dict(), "by_cond": {}}
            for c in CONDS:
                t, k = a[name][a[name].eval_cond == c], b[name][b[name].eval_cond == c]
                if len(t) and len(k):
                    d["by_cond"][c] = bootstrap_delta(t, k, f"13b-7b {name}[{c}]",
                                                      n_resamples=NBOOT).to_dict()
            out[name] = d
        report["scale"][phase] = out

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1))
    print(f"wrote {OUT}")
    print(f"inventory: {total_cells} cells / {total_trials} trials")
    for k, v in report["panel"].items():
        print(f"  panel {k}: {len(v)} systems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
