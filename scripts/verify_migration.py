#!/usr/bin/env python3
"""Prove the data layer survived a move, by recomputing published numbers from cells.

continuation/02_ENVIRONMENT.md §6: after a migration, reproduce a known result from
results/cells/ before trusting anything downstream. A transfer can succeed at the
file level and still be wrong -- a truncated parquet, a dropped cell directory, a
resampling that silently changed -- and every number in every report is recomputed
from these files, so a corrupted cell tree invalidates the whole corpus of results
without any error being raised anywhere.

The checks below are read from result files, never from a report (the project's
standing rule; it has caught four report-vs-file discrepancies). Each expected value
is the published one, with the document that published it named alongside.

Grid identity is by ITEM COUNT, never by directory name -- Grid A H1 is n=1214,
Grid B H1 is n=115, and the two are disjoint in programs. This is the single easiest
way to produce a wrong number here, so it is asserted rather than assumed.

    python scripts/verify_migration.py
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import PROJECT_ROOT  # noqa: E402
from obtune.transfer import PairedCells, bootstrap_delta, ci_from_draws  # noqa: E402

GRID_A_N = 1214
TOL = 0.02  # points; §6 asks for reproduction to <=0.02


def load_cell(pattern: str, expect_n: int) -> pd.DataFrame:
    hits = sorted(glob.glob(str(PROJECT_ROOT / pattern)))
    frames = []
    for p in hits:
        d = pd.read_parquet(p, columns=["correct", "snippet_id"])
        if len(d) == expect_n:
            frames.append(d)
    if len(frames) != 1:
        raise SystemExit(f"expected exactly one n={expect_n} cell for {pattern}, found {len(frames)}")
    return frames[0]


def paired(a: pd.DataFrame, b: pd.DataFrame) -> PairedCells:
    """Group both systems by program. Requires identical item sets, which is the point:
    an unpaired comparison would still produce a plausible number."""
    if len(a) != len(b):
        raise SystemExit(f"unpaired cells: {len(a)} vs {len(b)} items")
    ga = a.groupby("snippet_id")["correct"].agg(["size", "sum"])
    gb = b.groupby("snippet_id")["correct"].agg(["size", "sum"])
    j = ga.join(gb, lsuffix="_a", rsuffix="_b", how="inner")
    if len(j) != len(ga) or not (j["size_a"] == j["size_b"]).all():
        raise SystemExit("cells do not cover the same programs/items")
    return PairedCells(j.index.to_numpy(), j["size_a"].to_numpy(float),
                       j["sum_a"].to_numpy(float), j["sum_b"].to_numpy(float))


CHECKS = [
    # (label, system A glob, system B glob, expected delta, expected CI, source)
    ("merge_dare_ties - tuned_L0, Grid A H1",
     "results/cells/final/qwen25c-1.5b/python/merge_dare_ties__H1/trials.parquet",
     "results/cells/main/qwen25c-1.5b/python/tuned_L0__H1/trials.parquet",
     -0.66, (-1.89, 0.66), "02_ENVIRONMENT.md §6 / MASTER_REPORT RQ2 table"),
    ("l0merge_dare_ties - tuned_L0, Grid A H1",
     "results/cells/final/qwen25c-1.5b/python/l0merge_dare_ties__H1/trials.parquet",
     "results/cells/main/qwen25c-1.5b/python/tuned_L0__H1/trials.parquet",
     -3.13, (-4.78, -1.40), "00_STATE.md RQ2 table"),
]

ACCURACIES = [
    ("tuned_L0   Grid A H1", "results/cells/main/qwen25c-1.5b/python/tuned_L0__H1/trials.parquet", 24.55),
    ("merge_dare_ties Grid A H1", "results/cells/final/qwen25c-1.5b/python/merge_dare_ties__H1/trials.parquet", 23.89),
    ("l0merge_dare_ties Grid A H1", "results/cells/final/qwen25c-1.5b/python/l0merge_dare_ties__H1/trials.parquet", 21.42),
]


def main() -> int:
    bad = 0
    print("Point accuracies (Grid A H1, n=1214)")
    for label, pat, want in ACCURACIES:
        d = load_cell(pat, GRID_A_N)
        got = d["correct"].mean() * 100
        ok = abs(got - want) <= TOL
        bad += not ok
        print(f"  {'OK ' if ok else 'BAD'}  {label:28s} {got:6.2f}  expected {want:6.2f}")

    print("\nPaired cluster bootstrap by program_id, 2000 resamples, seed 17")
    for label, pa, pb, want_d, want_ci, src in CHECKS:
        pc = paired(load_cell(pa, GRID_A_N), load_cell(pb, GRID_A_N))
        draws = bootstrap_delta(pc, n_resamples=2000, seed=17) * 100
        got_d = pc.delta() * 100
        lo, hi = ci_from_draws(draws)
        ok_d = abs(got_d - want_d) <= TOL
        # The CI is a quantile of a reseeded bootstrap; hold it to a looser bar than
        # the point estimate, which is deterministic given the same cells.
        ok_ci = abs(lo - want_ci[0]) <= 0.15 and abs(hi - want_ci[1]) <= 0.15
        bad += not (ok_d and ok_ci)
        print(f"  {'OK ' if ok_d and ok_ci else 'BAD'}  {label}")
        print(f"       got      {got_d:+6.2f}  [{lo:+6.2f}, {hi:+6.2f}]   ({pc.programs.size} programs, n={pc.n})")
        print(f"       expected {want_d:+6.2f}  [{want_ci[0]:+6.2f}, {want_ci[1]:+6.2f}]   -- {src}")

    print("\nMIGRATION VERIFY: " + ("OK — the cell tree reproduces published numbers"
                                    if not bad else f"FAILED — {bad} check(s) disagree"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
