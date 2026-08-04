"""Collate cell parquets into results/trials.parquet — the stats contract.

    python -m obtune.trial_table [--source results/cells] [--out results/trials.parquet]

Everything downstream (transfer.py, forgetting.py, stats/R/*.R) reads this one file, so
this is where the contract is enforced rather than assumed:

* every row is validated against `schema.TrialRow` (the same model
  stats/R/01_schema_validate.R mirrors) — a bad row fails here, not three days later
  inside a GLMM fit;
* stub cells (`STUB_DO_NOT_USE`) are refused outright;
* `is_core` is (re)computed here rather than at generation time, because the common
  subset is a property of the assembled grid: it is the set of programs present in
  EVERY eval condition for a given (base_model, language, phase). eval_vllm cannot know
  it while a cell is still running (CLAUDE.md §4, coverage honesty);
* duplicate trials — the same item evaluated twice by a re-run — are resolved by
  keeping the newest `run_ts`, so a partial re-run overwrites rather than double-counts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional, Sequence

import pandas as pd

from obtune.config import RESULTS_DIR
from obtune.schema import TrialRow

STUB_MARKER = "STUB_DO_NOT_USE"

# What makes two rows the same trial. Not run_id: a re-run gets a new run_id but is the
# same trial and must replace, not duplicate.
TRIAL_KEY = [
    "phase", "base_model", "language", "adapter_arch", "train_cond",
    "adapter_id", "prompt_id", "seed", "eval_cond", "item_id",
]

SCHEMA_COLUMNS = list(TrialRow.model_fields.keys())
EXTRA_COLUMNS = ["raw_exact", "format_fail"]  # grading-sensitivity appendix


def discover_cells(source: Path, allow_stub: bool = False) -> list[Path]:
    out = []
    for p in sorted(Path(source).rglob("trials.parquet")):
        if (p.parent / STUB_MARKER).exists() and not allow_stub:
            continue
        out.append(p)
    return out


def validate_rows(df: pd.DataFrame, sample: Optional[int] = None) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    missing = [c for c in SCHEMA_COLUMNS if c not in df.columns]
    if missing:
        return [f"missing required column(s): {missing}"]
    rows = df if sample is None else df.head(sample)
    records = rows[SCHEMA_COLUMNS].to_dict("records")
    for i, rec in enumerate(records):
        clean = {k: (None if pd.isna(v) else v) for k, v in rec.items()
                 if not isinstance(v, (list, dict))}
        clean.update({k: v for k, v in rec.items() if isinstance(v, (list, dict))})
        try:
            TrialRow(**clean)
        except Exception as e:  # pydantic ValidationError
            errors.append(f"row {i} ({rec.get('item_id')}): {e}")
            if len(errors) >= 20:
                errors.append("... (truncated)")
                break
    return errors


def compute_is_core(df: pd.DataFrame) -> pd.DataFrame:
    """is_core=1 iff the program appears in every eval condition of its own grid."""
    df = df.copy()
    df["is_core"] = 0
    for (_, _, _), sub in df.groupby(["phase", "base_model", "language"], dropna=False):
        per_cond = sub.groupby("eval_cond")["snippet_id"].apply(set)
        if per_cond.empty:
            continue
        common = set.intersection(*per_cond.tolist())
        df.loc[sub.index[sub["snippet_id"].isin(common)], "is_core"] = 1
    return df


def collate(
    source: Path,
    allow_stub: bool = False,
    validate_sample: Optional[int] = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cells = discover_cells(source, allow_stub)
    if not cells:
        raise FileNotFoundError(f"no cell parquets under {source}")
    frames = []
    for p in cells:
        d = pd.read_parquet(p)
        d["cell_path"] = str(p.parent)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)

    for col in EXTRA_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    n_raw = len(df)
    df = df.sort_values("run_ts").drop_duplicates(subset=TRIAL_KEY, keep="last")
    n_dupes = n_raw - len(df)

    df = compute_is_core(df).reset_index(drop=True)

    errors = validate_rows(df, sample=validate_sample)
    if errors:
        raise ValueError(
            "results/trials.parquet failed schema.TrialRow validation:\n  "
            + "\n  ".join(errors[:20])
        )

    report = {
        "n_cells": len(cells),
        "n_trials": int(len(df)),
        "n_duplicate_trials_dropped": int(n_dupes),
        "n_programs": int(df["snippet_id"].nunique()),
        "n_core_trials": int((df["is_core"] == 1).sum()),
        "phases": sorted(df["phase"].dropna().unique().tolist()),
        "models": sorted(df["base_model"].dropna().unique().tolist()),
        "languages": sorted(df["language"].dropna().unique().tolist()),
        "eval_conditions": sorted(df["eval_cond"].dropna().unique().tolist()),
        "systems": sorted(
            df[["adapter_arch", "train_cond"]].fillna("-").agg("|".join, axis=1).unique().tolist()
        ),
        "overall_accuracy": float(df["correct"].mean()),
        "overall_format_fail_rate": (
            float(pd.to_numeric(df["format_fail"], errors="coerce").mean())
            if df["format_fail"].notna().any() else None
        ),
        "h1_trials": int((df["eval_cond"] == "H1").sum()),
        "h1_access_purposes": sorted(
            df.loc[df["eval_cond"] == "H1", "h1_access_purpose"].dropna().unique().tolist()
        ),
    }
    return df, report


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="collate cell parquets into results/trials.parquet")
    ap.add_argument("--source", default=str(RESULTS_DIR / "cells"))
    ap.add_argument("--out", default=str(RESULTS_DIR / "trials.parquet"))
    ap.add_argument("--allow-stub", action="store_true", help="include --stub cells (never for a result)")
    ap.add_argument("--validate-sample", type=int, default=None, help="validate only the first N rows")
    args = ap.parse_args(argv)

    df, report = collate(Path(args.source), args.allow_stub, args.validate_sample)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    report["out"] = str(out)
    (out.parent / "trials_report.json").write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
