"""Transfer-matrix statistics: the denominator guard, clustering, and the index.

The numbers here are synthetic and known by construction, so every assertion is about
the *estimator*, not about any model. Three properties are load-bearing for RQ1 and are
each pinned by a test: TR is undefined when the self-training gain is too small or its
CI touches zero; the bootstrap clusters on program_id rather than item; and the
Invariance Index falls back to raw delta-H1 points when the monolithic normalizer fails
the guard.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from obtune import transfer  # noqa: E402

N_PROGRAMS = 120
CASES_PER_PROGRAM = 3
COND_SEED = {"L0": 11, "L1b": 22, "L2": 33, "S1": 44, "H1": 55}


def make_cell(
    arch: str, train_cond, eval_cond: str, acc: float, churn: int = 0,
    prompt_id: str = "base_v1",
) -> pd.DataFrame:
    """Program-clustered outcomes: a program is right or wrong for ALL of its cases.

    That is the real correlation structure (CLAUDE.md §4 — bootstrap by program, not by
    item) and it is what makes the item bootstrap visibly wrong.

    Systems share one per-condition difficulty ordering, so an easier system's correct
    set is nearly a superset of a harder one's — as in real data. `churn` swaps that
    many programs across the boundary, which is what creates McNemar discordance in the
    "wrong direction" without changing the accuracy.
    """
    rng = np.random.default_rng(COND_SEED[eval_cond])
    perm = rng.permutation(N_PROGRAMS).tolist()
    n_right = int(round(acc * N_PROGRAMS))
    right_l, wrong_l = perm[:n_right], perm[n_right:]
    for k in range(min(churn, len(right_l), len(wrong_l))):
        right_l[-1 - k], wrong_l[k] = wrong_l[k], right_l[-1 - k]
    right = set(right_l)
    rows = []
    for p in range(N_PROGRAMS):
        for c in range(CASES_PER_PROGRAM):
            rows.append(
                {
                    "run_id": f"{arch}-{train_cond}-{eval_cond}", "run_ts": "2026-08-04T00:00:00Z",
                    "seed": 17, "phase": "pilot", "experiment_id": "test",
                    "base_model": "Qwen/Qwen2.5-Coder-1.5B-Instruct", "model_family": "coder",
                    "adapter_id": None if arch == "none" else f"ad/{train_cond}",
                    "adapter_arch": arch, "train_cond": train_cond, "eval_cond": eval_cond,
                    "language": "python", "dataset": "A",
                    "snippet_id": f"p{p:03d}", "item_id": f"p{p:03d}::{eval_cond}::{c}",
                    "is_core": 1, "prompt_id": prompt_id,
                    "output_raw": "x", "output_parsed": "x",
                    "correct": int(p in right), "parse_ok": 1, "grade_method": "normalized",
                    "format_fail": 0, "raw_exact": 0, "n_gen_tokens": 3,
                }
            )
    return pd.DataFrame(rows)


# acc[system][eval_cond]. Chosen so that L1b/L2 have a large self gain (the guard
# passes) while S1's self gain is under 1 point (the guard must reject the whole S1
# column), and the monolithic adapter has a usable H1 gain to normalize against.
ACC = {
    ("none", None): {"L0": 0.60, "L1b": 0.30, "L2": 0.35, "S1": 0.25, "H1": 0.20},
    ("per_type", "L1b"): {"L0": 0.58, "L1b": 0.62, "L2": 0.47, "S1": 0.26, "H1": 0.25},
    ("per_type", "L2"): {"L0": 0.57, "L1b": 0.42, "L2": 0.67, "S1": 0.26, "H1": 0.23},
    ("per_type", "S1"): {"L0": 0.55, "L1b": 0.32, "L2": 0.36, "S1": 0.26, "H1": 0.21},
    ("mono", None): {"L0": 0.59, "L1b": 0.55, "L2": 0.60, "S1": 0.40, "H1": 0.32},
}
CHURN = {("none", None): 0, ("per_type", "L1b"): 2, ("per_type", "L2"): 3,
         ("per_type", "S1"): 1, ("mono", None): 2}


@pytest.fixture(scope="module")
def trials() -> pd.DataFrame:
    frames = []
    for (arch, tc), accs in ACC.items():
        for cond, acc in accs.items():
            frames.append(make_cell(arch, tc, cond, acc, churn=CHURN[(arch, tc)]))
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="module")
def matrix(trials) -> pd.DataFrame:
    return transfer.transfer_matrix(
        trials, ["L1b", "L2", "S1"], ["L0", "L1b", "L2", "S1", "H1"], n_resamples=400, seed=17
    )


# --------------------------------------------------------------------------- #

def test_wilson_ci_bounds_and_endpoints():
    lo, hi = transfer.wilson_ci(50, 100)
    # Known value: Wilson 95 % for 50/100 is 0.4038-0.5962 (symmetric at p=0.5).
    assert lo == pytest.approx(0.40383, abs=1e-4) and hi == pytest.approx(0.59617, abs=1e-4)
    lo0, hi0 = transfer.wilson_ci(0, 30)
    assert lo0 == 0.0 and hi0 > 0.0, "Wald would give a zero-width interval here"
    lo1, hi1 = transfer.wilson_ci(30, 30)
    assert hi1 == pytest.approx(1.0, abs=1e-12) and lo1 < 1.0
    assert all(np.isnan(x) for x in transfer.wilson_ci(0, 0))


def test_mcnemar_and_bh():
    assert transfer.mcnemar_exact(0, 0) == 1.0
    assert transfer.mcnemar_exact(20, 0) < 1e-4
    assert transfer.mcnemar_exact(10, 10) == 1.0
    adj = transfer.bh_fdr([0.001, 0.02, 0.5, 0.9])
    assert all(a <= 1.0 for a in adj)
    assert adj == sorted(adj), "BH must preserve the p-value ordering"
    assert all(a >= p for a, p in zip(adj, [0.001, 0.02, 0.5, 0.9]))
    assert np.isnan(transfer.bh_fdr([float("nan")])[0])


def test_self_cell_transfer_ratio_is_one(matrix):
    for cond in ("L1b", "L2"):
        row = matrix[(matrix["train_cond"] == cond) & (matrix["eval_cond"] == cond)].iloc[0]
        assert row["tr_defined"]
        assert row["tr"] == pytest.approx(1.0, abs=1e-9)


def test_denominator_guard_rejects_small_self_gain(matrix):
    """S1's self gain is 1 point (< 3), so the whole S1 COLUMN is undefined — including
    the S1->S1 diagonal. A TR of 3.0 built on a 1-point denominator is noise."""
    col = matrix[matrix["eval_cond"] == "S1"]
    assert len(col) == 3
    assert not col["tr_defined"].any()
    assert col["tr"].isna().all()
    assert 0 < col["den_pts"].iloc[0] < transfer.MIN_DENOMINATOR_PTS

    l1b_col = matrix[matrix["eval_cond"] == "L1b"]
    assert l1b_col["tr_defined"].all()
    assert l1b_col["den_pts"].iloc[0] == pytest.approx(32.0, abs=0.5)


def test_undefined_cells_excluded_from_averages(matrix):
    s = transfer.summarize(matrix)
    off = matrix[~matrix["is_self"]]
    defined = off[off["tr_defined"] & off["tr"].notna()]
    assert s["n_tr_undefined"] == len(off) - len(defined) > 0
    assert s["mean_tr_offdiagonal"] == pytest.approx(defined["tr"].mean())
    assert not np.isnan(s["mean_tr_offdiagonal"])


def test_transfer_ratio_matches_the_definition(matrix):
    row = matrix[(matrix["train_cond"] == "L2") & (matrix["eval_cond"] == "L1b")].iloc[0]
    num = ACC[("per_type", "L2")]["L1b"] - ACC[("none", None)]["L1b"]
    den = ACC[("per_type", "L1b")]["L1b"] - ACC[("none", None)]["L1b"]
    assert row["delta_pts"] == pytest.approx(num * 100, abs=0.6)
    assert row["tr"] == pytest.approx(num / den, abs=0.03)
    assert row["tr_ci_lo"] < row["tr"] < row["tr_ci_hi"]


def test_h1_denominator_falls_back_to_the_monolithic_adapter(matrix):
    """No tuned_H1 exists and never will (CLAUDE.md §3.2), so the H1 column is
    normalized by the monolithic adapter's H1 gain."""
    col = matrix[matrix["eval_cond"] == "H1"]
    assert set(col["den_source"]) == {"mono"}
    assert col["den_pts"].iloc[0] == pytest.approx(12.0, abs=0.6)


def test_invariance_index_raw_is_primary_and_normalized_is_secondary(matrix):
    ii = transfer.invariance_index(matrix)
    expected_raw = np.mean(
        [ACC[("per_type", c)]["H1"] - ACC[("none", None)]["H1"] for c in ("L1b", "L2", "S1")]
    ) * 100
    assert ii["raw_delta_pts"] == pytest.approx(expected_raw, abs=0.6)
    assert ii["normalized_defined"] is True
    assert ii["normalizer"] == "mono"
    assert ii["normalized"] == pytest.approx(ii["raw_delta_pts"] / ii["normalizer_pts"], abs=0.03)
    assert set(ii["per_condition_delta_pts"]) == {"L1b", "L2", "S1"}


def test_invariance_index_raw_survives_a_failed_normalizer(trials):
    """Kill the monolithic H1 gain: the normalized index becomes undefined but the
    primary (raw points) number must still be reported."""
    weak = trials.copy()
    mask = (weak["adapter_arch"] == "mono") & (weak["eval_cond"] == "H1")
    weak.loc[mask, "correct"] = trials.loc[
        (trials["adapter_arch"] == "none") & (trials["eval_cond"] == "H1"), "correct"
    ].to_numpy()
    m = transfer.transfer_matrix(
        weak, ["L1b", "L2", "S1"], ["L1b", "H1"], n_resamples=300, seed=17
    )
    ii = transfer.invariance_index(m)
    assert ii["normalized_defined"] is False
    assert np.isnan(ii["normalized"])
    assert np.isfinite(ii["raw_delta_pts"])


# --------------------------------------------------------------------------- #
# Clustering
# --------------------------------------------------------------------------- #

def test_cluster_bootstrap_is_wider_than_an_item_bootstrap(trials):
    """The whole point of clustering by program_id: pretending the 3 cases of a program
    are independent shrinks the CI by roughly sqrt(cases-per-program)."""
    tuned = trials[(trials["adapter_arch"] == "per_type") & (trials["train_cond"] == "L1b")
                   & (trials["eval_cond"] == "L1b")]
    base = trials[(trials["adapter_arch"] == "none") & (trials["eval_cond"] == "L1b")]
    pc = transfer.pair_cells(tuned, base)
    clustered = transfer.bootstrap_delta(pc, 2000, seed=17)

    # Same data, but each ITEM treated as its own cluster.
    items = transfer.pair_items(tuned, base)
    item_pc = transfer.PairedCells(
        items["item_id"].to_numpy(), np.ones(len(items)),
        items["correct_a"].to_numpy(float), items["correct_b"].to_numpy(float),
    )
    per_item = transfer.bootstrap_delta(item_pc, 2000, seed=17)

    w_cluster = np.subtract(*reversed(transfer.ci_from_draws(clustered)))
    w_item = np.subtract(*reversed(transfer.ci_from_draws(per_item)))
    assert w_cluster > w_item * 1.4, (w_cluster, w_item)
    assert clustered.mean() == pytest.approx(pc.delta(), abs=0.02)


def test_pair_items_is_an_inner_join_not_index_alignment(trials):
    tuned = trials[(trials["adapter_arch"] == "per_type") & (trials["train_cond"] == "L1b")
                   & (trials["eval_cond"] == "L1b")]
    base = trials[(trials["adapter_arch"] == "none") & (trials["eval_cond"] == "L1b")]
    partial = base.iloc[: 30 * CASES_PER_PROGRAM]
    paired = transfer.pair_items(tuned, partial)
    assert len(paired) == 30 * CASES_PER_PROGRAM
    assert paired["correct_b"].notna().all()


def test_core_subset_keeps_only_programs_present_in_every_condition(trials):
    drop = trials[(trials["eval_cond"] == "H1") & (trials["snippet_id"] == "p000")].index
    thinned = trials.drop(index=drop)
    core = transfer.core_subset(thinned)
    assert "p000" not in set(core["snippet_id"])
    assert core["snippet_id"].nunique() == N_PROGRAMS - 1
    assert (core["is_core"] == 1).all()


def test_accuracy_table_separates_systems_that_differ_only_by_prompt(trials):
    extra = make_cell("oracle_prompt", None, "L1b", 0.44, churn=1, prompt_id="oracle_1shot_v1")
    base_oracle = make_cell("oracle_prompt", None, "L1b", 0.40, churn=2, prompt_id="oracle_v1")
    df = pd.concat([trials, extra, base_oracle], ignore_index=True)
    acc = transfer.accuracy_table(df)
    oracle = acc[(acc["adapter_arch"] == "oracle_prompt") & (acc["eval_cond"] == "L1b")]
    assert len(oracle) == 2, "the two oracle prompt systems must not be pooled"
    assert set(oracle["prompt_id"]) == {"oracle_v1", "oracle_1shot_v1"}
    assert (oracle["wilson_lo"] < oracle["acc"]).all()
    assert (oracle["acc"] < oracle["wilson_hi"]).all()
