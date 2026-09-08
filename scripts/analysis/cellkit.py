"""Shared cell loading + reporting for the pipeline analysis scripts (35_-41_).

Every pipeline analysis script writes ONE json with the same top-level shape so
scripts/pipeline/report.py can assemble the paper report without knowing each
script's internals:

    {"rq": ..., "script": ..., "generated_utc": ..., "models": [...],
     "accuracy": {model: {system: {cond: acc}}},
     "format_fail": {model: {system: {cond: rate}}},
     "contrasts": {model: {label: Contrast.to_dict()}},
     "hypotheses": [{"id", "rule", "verdict", "evidence"}]}

Cells are read from results/cells/<phase>/<model>/python/<system>__<cond>/trials.parquet.
A system may be looked up across several phases IN ORDER (first hit wins), because a
re-evaluated arm (same-phase re-read) should beat an older read of the same adapter, and
because the standing arms were read under whichever phase their campaign used.

NEVER reads an H1 cell: `load_cell` refuses cond == "H1" outright (CLAUDE.md §3.2: the
H1 budget is spent; no H1 number may be used to select, tune or rank anything).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.control_relative import Contrast, bootstrap_delta  # noqa: E402

CELLS = ROOT / "results" / "cells"
SEEN = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
OBF_SEEN = ["L1b", "L1r", "L2", "S1", "S2"]


class H1Refused(RuntimeError):
    pass


def load_cell(phases: Iterable[str], model: str, system: str, cond: str,
              language: str = "python") -> Optional[pd.DataFrame]:
    if cond == "H1":
        raise H1Refused("H1 reads are forbidden in pipeline analyses (CLAUDE.md §3.2)")
    for ph in phases:
        p = CELLS / ph / model / language / f"{system}__{cond}" / "trials.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            df["condition"] = cond
            df["_phase"] = ph
            return df
    return None


def load_block(phases: Iterable[str], model: str, systems: Iterable[str], conds: Iterable[str],
               alias: Optional[dict[str, str]] = None, quiet: bool = False,
               language: str = "python") -> dict[str, dict[str, pd.DataFrame]]:
    """system -> cond -> trials. Missing cells are reported on stderr, not fatal.

    `language` defaults to python because every analysis until 2026-09-08 was Python-only; the
    cross-language grid (E13) must pass it explicitly, and a caller that forgets gets an empty
    block rather than wrong numbers, because the cell path itself carries the language."""
    alias = alias or {}
    phases = list(phases)
    out: dict[str, dict[str, pd.DataFrame]] = {}
    missing = []
    for s in systems:
        for c in conds:
            df = load_cell(phases, model, alias.get(s, s), c, language=language)
            if df is None:
                missing.append((s, c))
            else:
                out.setdefault(s, {})[c] = df
    if missing and not quiet:
        print(f"[cellkit] {model}: MISSING {len(missing)} cell(s): {missing}", file=sys.stderr)
    return out


def pooled(block: dict[str, dict[str, pd.DataFrame]], system: str,
           conds: Iterable[str]) -> Optional[pd.DataFrame]:
    parts = [block[system][c] for c in conds if c in block.get(system, {})]
    return pd.concat(parts) if parts else None


def contrast(block, treat: str, control: str, conds: Iterable[str], label: Optional[str] = None,
             eq_margin: Optional[float] = None) -> Optional[dict]:
    conds = list(conds)
    t, c = pooled(block, treat, conds), pooled(block, control, conds)
    if t is None or c is None:
        return None
    lab = label or f"{treat} - {control} @ {'+'.join(conds) if len(conds) > 1 else conds[0]}"
    return bootstrap_delta(t, c, lab, eq_margin=eq_margin).to_dict()


def bootstrap_draws(treat: pd.DataFrame, control: pd.DataFrame, n_resamples: int = 2000,
                    seed: int = 17) -> tuple[float, np.ndarray]:
    """Same program-clustered resampling as bootstrap_delta, but returns the draws so a
    two-sided bootstrap p-value can be formed (needed for BH-FDR across a family)."""
    progs = sorted(set(treat["snippet_id"]) & set(control["snippet_id"]))
    A = {p: g["correct"].to_numpy() for p, g in treat.groupby("snippet_id")}
    B = {p: g["correct"].to_numpy() for p, g in control.groupby("snippet_id")}
    rng = np.random.default_rng(seed)
    idx = np.arange(len(progs))
    draws = np.empty(n_resamples)
    for i in range(n_resamples):
        pick = rng.choice(idx, size=len(progs), replace=True)
        a = np.concatenate([A[progs[j]] for j in pick])
        b = np.concatenate([B[progs[j]] for j in pick])
        draws[i] = (a.mean() - b.mean()) * 100.0
    point = (np.concatenate([A[p] for p in progs]).mean() - np.concatenate([B[p] for p in progs]).mean()) * 100.0
    return float(point), draws


def bootstrap_p(draws: np.ndarray) -> float:
    """Two-sided percentile-bootstrap p: how far the null (0) sits in the resampling
    distribution. Floored at 1/n so a p of exactly 0 is never reported."""
    n = len(draws)
    lo = (np.sum(draws <= 0) + 1) / (n + 1)
    hi = (np.sum(draws >= 0) + 1) / (n + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def bh_fdr(pvals: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted q-values (monotone, capped at 1)."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return []
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(q, 1.0)
    return [float(x) for x in out]


def acc_table(block) -> tuple[dict, dict]:
    acc = {s: {c: round(float(df["correct"].mean()), 4) for c, df in d.items()} for s, d in block.items()}
    ff = {s: {c: round(float(df["format_fail"].mean()), 4) for c, df in d.items()} for s, d in block.items()}
    return acc, ff


def new_result(rq: str, script: str, models: list[str]) -> dict:
    return {"rq": rq, "script": script,
            "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "models": models, "accuracy": {}, "format_fail": {}, "contrasts": {}, "hypotheses": []}


def hypothesis(res: dict, hid: str, rule: str, verdict: str, evidence: str) -> None:
    res["hypotheses"].append({"id": hid, "rule": rule, "verdict": verdict, "evidence": evidence})


def write(res: dict, out: str | Path) -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1))


def fmt(c: Optional[dict]) -> str:
    if not c:
        return "n/a"
    star = "*" if c.get("excludes_zero") else ""
    eq = " (equiv)" if c.get("equivalent") else ""
    return f"{c['value_pts']:+.2f} [{c['ci_lo']:+.2f}, {c['ci_hi']:+.2f}]{star}{eq} n_prog={c['n_programs']}"


def print_acc(model: str, acc: dict, conds: list[str]) -> None:
    print(f"=== {model} ===")
    print(f"{'system':<18}" + "".join(f"{c:>12}" for c in conds))
    for s, row in acc.items():
        print(f"{s:<18}" + "".join(f"{row.get(c, float('nan')):>12.4f}" for c in conds))


def print_hyps(res: dict) -> None:
    for h in res["hypotheses"]:
        print(f"  [{h['verdict']:<11}] {h['id']}: {h['evidence']}")
