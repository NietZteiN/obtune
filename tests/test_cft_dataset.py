"""Dataset-contract tests for the CFT pools.

Two failures here would invalidate the whole replication and are invisible downstream:
an H1 instance reaching a training pool (CLAUDE.md §3.2), and a test-split program in a
training pool (which would make the "held-out" bidirectional eval a memorisation check).
"""
from __future__ import annotations

import json

import pytest

from obtune import paths
from obtune.cft import dataset as cft_data


def _inst(**kw):
    base = dict(
        instance_id="p::L1r::pos",
        task="pos",
        program_id="p",
        program_group_id="p",
        condition="L1r",
        language="python",
        code_a="def f():\n    return 1\n",
        code_b="def f_0001():\n    return 1\n",
        label="YES",
        split="train",
    )
    base.update(kw)
    return cft_data.CFTInstance(**base)


def test_h1_can_never_be_a_cft_instance():
    with pytest.raises(ValueError, match="not trainable"):
        _inst(condition="H1")


def test_pools_reject_a_test_split_program():
    with pytest.raises(cft_data.CFTDataError, match="test-split"):
        cft_data.validate_pools({"pos": [_inst(split="test")]}, {})


def test_pools_reject_split_leakage():
    rows = [_inst(instance_id="p::L1r::pos", split="train"),
            _inst(instance_id="p::L2::pos", condition="L2", split="val")]
    with pytest.raises(cft_data.CFTDataError, match="more than one split"):
        cft_data.validate_pools({"pos": rows}, {})


def test_pools_reject_duplicate_instance_ids():
    with pytest.raises(cft_data.CFTDataError, match="duplicate instance_id"):
        cft_data.validate_pools({"pos": [_inst(), _inst()]}, {})


def test_pools_reject_a_degenerate_pair():
    """An identity pair labelled NO would teach that identical programs differ."""
    code = "def f():\n    return 1\n"
    with pytest.raises(cft_data.CFTDataError, match="identical"):
        cft_data.validate_pools({"neg": [_inst(code_a=code, code_b=code, label="NO")]}, {})


def test_pool_paths_stay_inside_the_training_tree():
    """Anything else would be refused by the loader guard on read-back anyway; failing
    here names the reason instead of surfacing as a QuarantineViolation later."""
    p = cft_data.pool_path("python", "gen").resolve()
    assert paths.TRAIN_ROOT.resolve() in p.parents
    paths.assert_trainable_path(p.parent)


def test_load_mixture_rejects_the_reverse_task():
    with pytest.raises(ValueError, match="unknown task"):
        cft_data.load_mixture("python", ["deobf"])


def test_balanced_take_spreads_across_conditions():
    rows = [
        _inst(instance_id=f"p{i}::{c}::pos", program_id=f"p{i}", program_group_id=f"p{i}",
              condition=c)
        for c in ("L1r", "L2", "S1")
        for i in range(10)
    ]
    picked = cft_data._balanced_take(rows, 9, seed=17)
    counts = {}
    for r in picked:
        counts[r.condition] = counts.get(r.condition, 0) + 1
    assert len(picked) == 9
    assert set(counts.values()) == {3}, counts


def test_balanced_take_is_deterministic():
    rows = [_inst(instance_id=f"p{i}::L1r::pos", program_id=f"p{i}", program_group_id=f"p{i}")
            for i in range(20)]
    a = [r.instance_id for r in cft_data._balanced_take(rows, 5, seed=17)]
    b = [r.instance_id for r in cft_data._balanced_take(rows, 5, seed=17)]
    assert a == b


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_built_pools_satisfy_the_contract(language):
    """Runs against the real pools when they exist; skipped before they are built."""
    try:
        pools = {t: cft_data.load_pool(language, t) for t in ("gen", "pos", "neg")}
    except FileNotFoundError:
        pytest.skip(f"CFT pools for {language} not built yet")
    cft_data.validate_pools(pools, cft_data.load_splits(language))
    assert pools["gen"] and pools["pos"] and pools["neg"]
    for task, rows in pools.items():
        assert {r.task for r in rows} == {task}
        assert all(r.condition in paths.TRAINABLE_CONDITIONS for r in rows)
    assert {r.label for r in pools["pos"]} == {"YES"}
    assert {r.label for r in pools["neg"]} == {"NO"}
    # Every negative must carry the executed evidence that it differs from its parent.
    assert all(
        r.mutation and r.mutation.get("n_cases_differing", 0) >= 1 for r in pools["neg"]
    )


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_pool_report_records_prompt_provenance(language):
    p = cft_data.report_path(language)
    if not p.exists():
        pytest.skip(f"CFT pool report for {language} not built yet")
    report = json.loads(p.read_text())
    assert report["prompt_provenance"]["cft_prompt_version"] == "cft_v1"
    assert len(report["prompt_provenance"]["cft_prompt_template_sha256"]) == 64
    assert report["negative_style"] in cft_data.NEGATIVE_STYLES


# --------------------------------------------------------------------------- #
# Label balance — the per-condition shortcut described in dataset.pair_pos_neg

def _pair(pid, cond, task):
    return _inst(
        instance_id=f"{pid}::{cond}::{task}",
        program_id=pid, program_group_id=pid, condition=cond, task=task,
        label="YES" if task == "pos" else "NO",
        code_b=f"def f_{pid}_{cond}_{task}():\n    return 1\n",
    )


def test_pairing_drops_positives_with_no_matching_negative():
    """Mutation coverage is uneven across conditions (S2 yields far fewer verified
    negatives, because most of what S2 inserts is inert). Unpaired, that makes the
    condition predictive of the label."""
    rows = [
        _pair("p1", "L1r", "pos"), _pair("p1", "L1r", "neg"),
        _pair("p2", "S2", "pos"),  # no negative for this key
        _pair("p3", "S2", "pos"), _pair("p3", "S2", "neg"),
    ]
    paired = cft_data.pair_pos_neg(rows)
    keys = {(r.program_id, r.condition) for r in paired}
    assert ("p2", "S2") not in keys
    assert keys == {("p1", "L1r"), ("p3", "S2")}


def test_pairing_makes_every_condition_exactly_balanced():
    rows = []
    for i in range(10):
        rows += [_pair(f"a{i}", "L1r", "pos"), _pair(f"a{i}", "L1r", "neg")]
    for i in range(10):
        rows.append(_pair(f"b{i}", "S2", "pos"))  # only 3 of them get a negative
        if i < 3:
            rows.append(_pair(f"b{i}", "S2", "neg"))
    unpaired = cft_data.label_balance(rows)
    assert unpaired["S2"]["p_yes"] > 0.6  # the shortcut, before the fix
    balance = cft_data.label_balance(cft_data.pair_pos_neg(rows))
    for cond in ("L1r", "S2", "ALL"):
        assert balance[cond]["p_yes"] == 0.5, (cond, balance[cond])


def test_pairing_leaves_the_generation_pool_untouched():
    rows = [_pair("p1", "L1r", "pos"), _inst(instance_id="p9::L1r::gen", task="gen",
                                             program_id="p9", program_group_id="p9", label=None)]
    out = cft_data.pair_pos_neg(rows)
    assert [r.instance_id for r in out] == ["p9::L1r::gen"]


def test_label_balance_reports_all_and_per_condition():
    rows = [_pair("p1", "L1r", "pos"), _pair("p1", "L1r", "neg")]
    b = cft_data.label_balance(rows)
    assert b["ALL"] == {"pos": 1, "neg": 1, "p_yes": 0.5}
    assert b["L1r"]["p_yes"] == 0.5


# --------------------------------------------------------------------------- #
# Eval common subset — the `limit: 300` bug

def test_common_subset_keeps_only_fully_covered_programs():
    """`limit` used to shuffle and truncate the full program list, so each condition was
    scored on a different set — and S1's programs are systematically longer, which
    confounds the transform with the program (CLAUDE.md §4 coverage honesty)."""
    from obtune.cft.evaluate import EvalProgram, common_subset

    def prog(pid, conds):
        return EvalProgram(
            program_id=pid, language="python", original_code="def f():\n    return 1\n",
            entry_point="f", cases=[{"args_repr": "()", "output_canon": "1"}],
            variants={c: {"code": "x", "entry_point": "f"} for c in conds},
        )

    progs = [
        prog("all", ["L1b", "L1r", "L2", "S1", "S2"]),
        prog("no_s1", ["L1b", "L1r", "L2", "S2"]),
        prog("only_l1r", ["L1r"]),
    ]
    kept = common_subset(progs, ["L1b", "L1r", "L2", "S1", "S2"])
    assert [p.program_id for p in kept] == ["all"]
    # L0 is the reference source, not an evaluated condition, so it is never required:
    # every program here carries L1r, so requiring {L0, L1r} keeps all three.
    assert len(common_subset(progs, ["L0", "L1r"])) == 3
    # ...and the filtering is still real for a condition some programs lack.
    assert [p.program_id for p in common_subset(progs, ["L0", "S2"])] == ["all", "no_s1"]
