#!/usr/bin/env python
"""Rank every W6 campaign arm on the trainable grid, across models, to pick the H1 final batch.

`30_best_per_condition.py` ranks CodeLlama-7b's Grid A greedy phases. That is the right scope
for "what works best at 7B", but it cannot answer the question this campaign now has to answer:
**which arms are worth the single remaining H1 `final_eval` read** (CLAUDE.md 3.2 -- H1 is read
exactly twice and the pilot is spent). That question spans models (7b/13b/34b/llama31-8b) and
the new phases (`trace_generic`, `x1_generic`), so it gets its own script rather than a widened
scope on 30, whose docstring pins it to one model deliberately.

Method, and why: every arm is compared to `tuned_L0` **of its own model** on the intersected
item set, pooled over the six trainable conditions, with a bootstrap clustered by program.
Cross-model rows report the arm against **7b `tuned_L0`** as well, because "is 34b worth an H1
read" is a different question from "does breadth beat clean code at 34b". Ranking by raw
accuracy alone is exactly the error log/transfer 2026-09-03 corrected, so nothing here is
called an ordering unless its interval says so.

H1 cells are NEVER read here -- the arms are ranked entirely on the trainable grid, which is
the point: the H1 batch must be chosen without looking at H1.

Writes results/analysis/campaign_ranking_<date>.json.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.config import RESULTS_DIR  # noqa: E402

CELLS = RESULTS_DIR / "cells"
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
# Greedy, trainable-grid phases only. `selfcons_generic` is T=0.7 and `mole_generic_testset`
# is Grid B; both would pool incomparable program sets.
PHASES = ["rq1_generic", "rq2_generic", "loto_generic", "mole_generic", "merge_sweep_generic",
          "rank_generic", "extra_generic", "baselines_generic", "trace_generic", "x1_generic"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b"]
NBOOT = 2000


def load(model: str) -> dict[str, pd.DataFrame]:
    """One long frame per system: the largest cell per (system, condition), concatenated."""
    best: dict[tuple[str, str], tuple[int, pd.DataFrame]] = {}
    for ph in PHASES:
        root = CELLS / ph / model / "python"
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            name, _, cond = d.name.rpartition("__")
            if cond not in CONDS or not (d / "trials.parquet").exists():
                continue
            df = pd.read_parquet(d / "trials.parquet", columns=["item_id", "correct"])
            key = (name, cond)
            if key not in best or len(df) > best[key][0]:
                best[key] = (len(df), df)
    out: dict[str, list] = {}
    for (name, _cond), (_n, df) in best.items():
        out.setdefault(name, []).append(df)
    # Only keep systems present on all six conditions -- a system evaluated on a subset would
    # otherwise be ranked on an easier column mix than its rivals.
    return {k: pd.concat(v) for k, v in out.items() if len(v) == len(CONDS)}


def boot(m: pd.DataFrame, a: str, b: str, rng: np.random.Generator) -> dict:
    g = m.groupby("program_id").indices
    keys = np.array(list(g))
    vals = [
        (lambda s: (s[a].mean() - s[b].mean()) * 100)(
            m.iloc[np.concatenate([g[k] for k in rng.choice(keys, len(keys))])])
        for _ in range(NBOOT)
    ]
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"delta_pts": round(float((m[a].mean() - m[b].mean()) * 100), 2),
            "ci": [round(float(lo), 2), round(float(hi), 2)],
            "excludes_zero": bool(lo > 0 or hi < 0)}


def main() -> int:
    rng = np.random.default_rng(17)
    report: dict = {"generated": str(date.today()), "n_boot": NBOOT, "phases": PHASES,
                    "note": "trainable grid only; H1 never read", "models": {}}
    ref: pd.DataFrame | None = None

    for model in MODELS:
        sysframes = load(model)
        if "tuned_L0" not in sysframes:
            continue
        common = set.intersection(*[set(df.item_id) for df in sysframes.values()])
        wide = None
        for name, df in sysframes.items():
            d = (df[df.item_id.isin(common)].drop_duplicates("item_id")
                 .set_index("item_id")["correct"].astype(bool).rename(name))
            wide = d.to_frame() if wide is None else wide.join(d)
        wide["program_id"] = [i.split("::")[0] for i in wide.index]
        if model == "codellama-7b":
            ref = wide[["tuned_L0", "program_id"]].rename(columns={"tuned_L0": "ref7b"})

        rows = []
        for name in wide.columns.drop("program_id"):
            r = {"system": name, "acc": round(float(wide[name].mean()), 4)}
            if name != "tuned_L0":
                r["vs_own_tuned_L0"] = boot(wide, name, "tuned_L0", rng)
            if ref is not None and model != "codellama-7b":
                j = wide[[name, "program_id"]].join(ref["ref7b"], how="inner")
                r["vs_7b_tuned_L0"] = boot(j, name, "ref7b", rng)
            rows.append(r)
        rows.sort(key=lambda r: -r["acc"])
        report["models"][model] = {"n_items": len(common), "n_systems": len(sysframes),
                                  "systems": rows}

        print(f"\n=== {model}  ({len(sysframes)} systems, {len(common)} items) ===")
        for i, r in enumerate(rows, 1):
            t = ""
            if "vs_own_tuned_L0" in r:
                v = r["vs_own_tuned_L0"]
                t += f"  vs own tuned_L0 {v['delta_pts']:+6.2f} {v['ci']}" + ("*" if v["excludes_zero"] else "")
            if "vs_7b_tuned_L0" in r:
                v = r["vs_7b_tuned_L0"]
                t += f"   vs 7b {v['delta_pts']:+6.2f}" + ("*" if v["excludes_zero"] else "")
            print(f"  {i:2d}. {r['system']:22s} {r['acc']:.4f}{t}")

    out = RESULTS_DIR / "analysis" / f"campaign_ranking_{date.today()}.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"\nwrote {out}   (* = interval excludes zero)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
