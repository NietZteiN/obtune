"""Mixture-assembly contracts for the SRH arms.

The load-bearing one is `test_mix50_*`: MIX50 is the arm the whole experiment turns on,
and it is only meaningful if it is genuinely budget-matched to FWD. Partition it by row
instead of by program, or let `direction_mix` silently go missing from a config, and it
quietly becomes a different arm that still produces a plausible number.
"""
from __future__ import annotations

from collections import Counter

import pytest

from obtune.cft.dataset import CFTInstance, CFTDataError
from obtune.config import load_config
from obtune.srh import arms
from obtune.srh import dataset as srh_data


def _gen(pid, cond="L1r", split="train"):
    return CFTInstance(
        instance_id=f"{pid}::{cond}::gen", task="gen", program_id=pid,
        program_group_id=pid, condition=cond, language="python",
        code_a=f"def orig_{pid}():\n    return 1\n",
        code_b=f"def f_{pid}():\n    return 1\n", split=split,
    )


# --------------------------------------------------------------------------- #
# flip_to_reverse

def test_flip_to_reverse_preserves_count_and_relabels():
    rows = [_gen(f"p{i}") for i in range(10)]
    rev = srh_data.flip_to_reverse(rows)
    assert len(rev) == 10
    assert {r.task for r in rev} == {"rev"}
    assert [r.program_id for r in rev] == [r.program_id for r in rows]


def test_flip_to_reverse_ignores_non_gen_rows():
    pos = _gen("p1").model_copy(update={"task": "pos", "label": "YES"})
    assert srh_data.flip_to_reverse([pos]) == []


# --------------------------------------------------------------------------- #
# MIX50

def test_mix50_has_exactly_fwd_instance_count():
    """The point of the arm: matched to FWD on instances and therefore on steps."""
    rows = [_gen(f"p{i}") for i in range(100)]
    mix = srh_data.split_directions(rows, 0.5, seed=17)
    assert len(mix) == len(rows)


def test_mix50_partitions_by_program_not_by_row():
    """By row, one program could appear in both directions and the arm would silently
    become FLIP at half the data."""
    rows = [_gen(f"p{i}", cond=c) for i in range(20) for c in ("L1r", "S1")]
    mix = srh_data.split_directions(rows, 0.5, seed=17, disjoint_programs=True)
    by_program = {}
    for r in mix:
        by_program.setdefault(r.program_id, set()).add(r.task)
    assert all(len(t) == 1 for t in by_program.values())
    srh_data.assert_direction_disjoint(mix)  # no raise


def test_mix50_row_partition_is_detected_as_non_disjoint():
    rows = [_gen(f"p{i}", cond=c) for i in range(20) for c in ("L1r", "S1")]
    mix = srh_data.split_directions(rows, 0.5, seed=17, disjoint_programs=False)
    with pytest.raises(CFTDataError, match="BOTH directions"):
        srh_data.assert_direction_disjoint(mix)


def test_mix50_is_deterministic_under_a_seed():
    rows = [_gen(f"p{i}") for i in range(50)]
    a = [(r.instance_id, r.task) for r in srh_data.split_directions(rows, 0.5, seed=17)]
    b = [(r.instance_id, r.task) for r in srh_data.split_directions(rows, 0.5, seed=17)]
    c = [(r.instance_id, r.task) for r in srh_data.split_directions(rows, 0.5, seed=18)]
    assert a == b and a != c


@pytest.mark.parametrize("frac,expected", [(0.0, 0), (1.0, 50)])
def test_mix50_fraction_endpoints(frac, expected):
    rows = [_gen(f"p{i}") for i in range(50)]
    mix = srh_data.split_directions(rows, frac, seed=17)
    assert Counter(r.task for r in mix)["rev"] == expected


def test_mix50_rejects_an_out_of_range_fraction():
    with pytest.raises(ValueError):
        srh_data.split_directions([_gen("p0")], 1.5, seed=17)


# --------------------------------------------------------------------------- #
# load_mixture guards

def test_direction_mix_and_rev_task_together_are_refused():
    """One replaces forward rows, the other adds reverse rows alongside them. Together
    they build an arm that is neither FLIP nor MIX50."""
    with pytest.raises(ValueError, match="Pick one"):
        srh_data.load_mixture(
            "python", ["gen", "rev"], splits=("train",),
            direction_mix={"reverse_fraction": 0.5},
        )


def test_common_program_subset_requires_conditions():
    with pytest.raises(ValueError, match="requires an explicit condition list"):
        srh_data.load_mixture("python", ["gen"], program_subset="common")


def test_unknown_program_subset_is_rejected():
    with pytest.raises(ValueError, match="program_subset"):
        srh_data.load_mixture("python", ["gen"], program_subset="whatever")


def test_no_h1_can_enter_a_mixture():
    from obtune import paths

    with pytest.raises(paths.QuarantineViolation):
        srh_data.assert_no_h1([_gen("p0").model_copy(update={"condition": "H1"})])


def test_direction_balance_reports_reverse_share():
    rows = [_gen(f"p{i}") for i in range(6)] + srh_data.flip_to_reverse(
        [_gen(f"q{i}") for i in range(4)]
    )
    bal = srh_data.direction_balance(rows)
    assert bal["ALL"] == {"gen": 6, "rev": 4}
    assert bal["reverse_share"] == pytest.approx(0.4)


# --------------------------------------------------------------------------- #
# Config integrity — this class of bug already bit once

@pytest.mark.parametrize("model", ["qwen1.5b", "qwen7b"])
@pytest.mark.parametrize("arm", ["rev", "flip", "mix50", "fwd2x", "cftflip", "flipsym"])
def test_every_arm_config_matches_its_registry_spec(arm, model):
    """Guards a real failure already hit once: appending a second `train:` block to a
    YAML file is valid and silently drops the first, which turned `mix50_qwen7b` into
    plain FWD (no `direction_mix`) and `fwd2x_qwen7b` into FWD (no `epochs: 6`). Both
    would have trained without error and produced a null that looked like a finding.
    """
    cfg = load_config(f"srh/train/{arm}_{model}_py.yaml")
    spec = arms.resolve(arm)
    train = cfg.get("train", {}) or {}
    mix_kw = train.get("mixture_kwargs", {}) or {}

    assert cfg["arm"] == spec.name
    assert list(cfg["tasks"]) == list(spec.tasks)
    assert bool(cfg.get("symmetric", False)) is spec.symmetric
    if spec.epochs is not None:
        assert float(train["epochs"]) == spec.epochs
    if spec.direction_mix:
        assert mix_kw.get("direction_mix"), "direction_mix went missing — MIX50 would train as FWD"
        assert mix_kw["direction_mix"]["disjoint_programs"] is True
    else:
        assert "direction_mix" not in mix_kw


@pytest.mark.parametrize("model", ["qwen1.5b", "qwen7b"])
@pytest.mark.parametrize("arm", ["rev", "flip", "mix50", "fwd2x", "cftflip", "flipsym"])
def test_arm_configs_land_outside_the_replication_adapter_root(arm, model):
    """An eval config that picked up an SRH adapter as a replication arm would produce
    numbers that look like replication results and are not."""
    from obtune.cft import train as cft_train

    cfg = load_config(f"srh/train/{arm}_{model}_py.yaml")
    d = cft_train.adapter_dir(cfg)
    assert "adapters_srh" in d.parts
    assert "adapters_cft" not in d.parts
    assert d.name.startswith(f"{cfg['scope']}_{arm}")


def test_all_arm_configs_share_one_recipe():
    """Any FLIP-vs-CFT gap must come from the data, not from the learning rate."""
    recipes = {}
    for arm in ("rev", "flip", "mix50", "cftflip", "flipsym"):
        t = load_config(f"srh/train/{arm}_qwen7b_py.yaml")["train"]
        recipes[arm] = (t["lr"], t["epochs"], t["max_seq_len"], t["seed"],
                        t["per_device_batch"] * t["grad_accum"])
    assert len(set(recipes.values())) == 1, recipes
