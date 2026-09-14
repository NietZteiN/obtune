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



# ---- AUTOMATIC PROMPT-CONSISTENCY REGISTRY ----------------------------------------------------
# check_one_prompt() below only fires for code that CALLS it, and on 2026-09-14 two scripts that
# needed it did not: 62_merge_backward.py has its own pooled(), and 67_backward_failure_modes.py
# computes its own aggregate. Both crossed the prompt boundary and both published a number before
# anyone noticed. A guard that works only on opt-in is not a guard, so this one fires from the read
# path itself: every cell a process opens registers its prompt_id against (model, system), and the
# second DISTINCT id for the same pair prints once. Scripts that compare prompts on purpose --
# 68_prompt_effect.py -- call allow_mixed_prompts() to silence it.
_SEEN_PROMPTS: dict = {}
_MIXED_OK = False


def allow_mixed_prompts(on: bool = True) -> None:
    """Silence the registry, for a script whose whole point is comparing two prompts."""
    global _MIXED_OK
    _MIXED_OK = bool(on)


def register_prompt(model: str, system: str, prompt_id: str, task: str = "output") -> None:
    """`task` is part of the key. Forward and backward cells for the same arm ALWAYS use different
    prompts -- that is what the two directions are -- so keying on (model, system) alone made every
    script that reads both directions warn on every arm. Keyed this way the warning means what it
    says: the same arm, asked the same question, two different ways."""
    if _MIXED_OK or not prompt_id or prompt_id == "?":
        return
    key = (model, system, task)
    seen = _SEEN_PROMPTS.setdefault(key, set())
    was = len(seen)
    seen.add(prompt_id)
    if was == 1 and len(seen) == 2:
        print(f"[cellkit] WARNING: {model}/{system} (task={task}) has cells under TWO prompts "
              f"{sorted(seen)}. Anything pooling or contrasting across them measures the prompt as "
              f"well as the arm (log/transfer/2026-09-14_two-prompts-one-phase.md). Call "
              f"cellkit.allow_mixed_prompts() if that is the intent.", file=sys.stderr)



# ---- GRADE VERSION FOR BACKWARD CELLS --------------------------------------------------------
# 72_regrade_inverse.py writes `trials_v2.parquet` / `cell_meta_v2.json` beside the originals for
# any backward cell that had multi-line replies: v2 grades the first line, which is exactly what
# the "\n" stop string the harness should have carried would have returned. v2 is the default
# read wherever it exists. OBTUNE_INVERSE_GRADE=v1 forces the originals, for before/after reads.
# Forward cells never have a v2 file, so the resolver is a no-op there.
import os as _os


def grade_version() -> str:
    return "v1" if _os.environ.get("OBTUNE_INVERSE_GRADE", "v2").lower() == "v1" else "v2"


def trials_path(cell_dir: Path) -> Path:
    v2 = cell_dir / "trials_v2.parquet"
    return v2 if grade_version() == "v2" and v2.exists() else cell_dir / "trials.parquet"


def meta_path(cell_dir: Path) -> Path:
    v2 = cell_dir / "cell_meta_v2.json"
    return v2 if grade_version() == "v2" and v2.exists() else cell_dir / "cell_meta.json"


def load_cell(phases: Iterable[str], model: str, system: str, cond: str,
              language: str = "python") -> Optional[pd.DataFrame]:
    if cond == "H1":
        raise H1Refused("H1 reads are forbidden in pipeline analyses (CLAUDE.md §3.2)")
    for ph in phases:
        cell_dir = CELLS / ph / model / language / f"{system}__{cond}"
        p = trials_path(cell_dir)
        if p.exists():
            df = pd.read_parquet(p)
            df["condition"] = cond
            df["_phase"] = ph
            # Carried so `pooled` can check that everything it averages was asked the same way.
            # See the 2026-09-14 fault below.
            pid, tsk = _prompt_id(p.parent)
            df["_prompt_id"] = pid
            register_prompt(model, system, pid, tsk)
            return df
    return None


def _prompt_id(cell: Path) -> tuple[str, str]:
    """(prompt_id, task) from the cell's manifest; ("?", "output") when it cannot be read."""
    meta = cell / "cell_meta.json"
    if not meta.exists():
        return "?", "output"
    try:
        d = json.loads(meta.read_text())
        return str(d.get("prompt_id", "?")), str(d.get("task", "output"))
    except Exception:
        return "?", "output"


_PROMPT_WARNED: set = set()


def check_one_prompt(frames, label: str = "") -> Optional[set]:
    """Warn once per (label, id-set) when a pooled read averages cells asked with DIFFERENT prompts.

    THE FAULT THIS EXISTS FOR (2026-09-14). Four configs wrote backward cells into the single phase
    `inverse_generic` over three days. `inverse_core.yaml` carried no one-shot demo and the other
    three did, so the backward LADDER was zero-shot on seven of eight models while every stack cell
    and every merge cell was one-shot. One column of the master table mixed the two, and one
    contrast compared zero-shot arms against one-shot merges. CodeGemma's `mono_all` sits at 0.882
    format-failure under the first prompt and 0.086 under the second, on a HARDER condition -- so
    the confound was larger than most effects being reported.

    `cell_meta.json` records `prompt_id` precisely so this is checkable, and nothing checked it.
    This is a warning rather than a refusal because several standing analyses legitimately pool
    across phases; the point is that it can no longer happen silently.
    """
    ids = {str(f["_prompt_id"].iloc[0]) for f in frames if f is not None and "_prompt_id" in f}
    if len(ids) <= 1:
        return ids
    key = (label, tuple(sorted(ids)))
    if key not in _PROMPT_WARNED:
        _PROMPT_WARNED.add(key)
        print(f"[cellkit] WARNING: pooling cells with DIFFERENT prompt_id{' for ' + label if label else ''}: "
              f"{sorted(ids)}. These were not asked the same question; the difference can exceed the "
              f"effect being measured (log/transfer/2026-09-14_two-prompts-one-phase.md).",
              file=sys.stderr)
    return ids


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
    if not parts:
        return None
    check_one_prompt(parts, label=system)
    return pd.concat(parts)


def contrast(block, treat: str, control: str, conds: Iterable[str], label: Optional[str] = None,
             eq_margin: Optional[float] = None) -> Optional[dict]:
    conds = list(conds)
    t, c = pooled(block, treat, conds), pooled(block, control, conds)
    if t is None or c is None:
        return None
    lab = label or f"{treat} - {control} @ {'+'.join(conds) if len(conds) > 1 else conds[0]}"
    # ACROSS systems, not only within one. The 2026-09-14 fault was exactly this shape:
    # 62_merge_backward.py contrasts one-shot merge cells against zero-shot base/breadth cells, and
    # each system's own cells are internally consistent, so a per-system check never fires. The
    # comparison is what crosses the boundary.
    check_one_prompt([t, c], label=lab)
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
