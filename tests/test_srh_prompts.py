"""Contracts for the SRH reverse-training task.

Two of these guard failures that would be invisible in a loss curve and fatal to the
experiment: the reverse training prompt drifting from the reverse eval prompt, and the
replication's "reverse is never supervised" guarantee being broken by a future edit.
"""
from __future__ import annotations

import pytest

from obtune.cft import prompts as cft_prompts
from obtune.srh import prompts as srh_prompts

PY_ORIG = "def add(a, b):\n    return a + b\n"
PY_OBF = "def f_1a2b(v_0011, v_0012):\n    return v_0011 + v_0012\n"


def _row(task, **kw):
    base = dict(
        task=task, code_a=PY_ORIG, code_b=PY_OBF, language="python", condition="L1r"
    )
    base.update(kw)
    return base


def test_reverse_training_prompt_is_byte_identical_to_the_eval_prompt():
    """CLAUDE.md §4.3. Training on a different reverse prompt than evaluation uses would
    make reverse accuracy a measurement of prompt mismatch rather than of capability."""
    train = srh_prompts.build_rev_messages(PY_OBF, "python")
    evalp = cft_prompts.build_deobf_messages(PY_OBF, "python", strategy="simple")
    assert train == evalp
    srh_prompts.assert_rev_matches_eval_prompt(PY_OBF, "python")  # no raise


def test_reverse_target_is_the_original_and_input_is_the_obfuscated_code():
    ex = srh_prompts.build_example(_row("rev"))
    assert ex["completion"][0]["content"] == PY_ORIG.rstrip("\n")
    assert PY_OBF.strip() in ex["prompt"][-1]["content"]
    assert PY_ORIG.strip() not in ex["prompt"][-1]["content"], "the answer leaked into the prompt"


def test_rev_does_not_swap_the_field_contract():
    """`code_a` stays the L0 original and `code_b` the transformed program, in every
    task. Swapping them would make pool rows direction-dependent and break every
    consumer that assumes otherwise (label_balance, pair_pos_neg, mutation metadata)."""
    from obtune.cft.dataset import CFTInstance
    from obtune.srh import dataset as srh_data

    inst = CFTInstance(
        instance_id="p::L1r::gen", task="gen", program_id="p", program_group_id="p",
        condition="L1r", language="python", code_a=PY_ORIG, code_b=PY_OBF, split="train",
    )
    (rev,) = srh_data.flip_to_reverse([inst])
    assert rev.task == "rev"
    assert rev.code_a == PY_ORIG and rev.code_b == PY_OBF
    assert rev.instance_id.endswith("::rev")


def test_forward_tasks_still_delegate_to_the_replication_builder():
    for task in ("gen", "pos", "neg"):
        assert srh_prompts.build_messages(_row(task)) == cft_prompts.build_messages(_row(task))
        assert srh_prompts.completion_for(_row(task)) == cft_prompts.completion_for(_row(task))


def test_the_replication_still_refuses_to_supervise_its_reverse_direction():
    """The guarantee `obtune.cft` is built on. If a future edit adds a trainable reverse
    task there, the replication silently stops answering the paper's question."""
    srh_prompts.assert_replication_untouched()  # no raise
    assert "rev" not in cft_prompts.TASKS
    with pytest.raises(ValueError, match="never supervised"):
        cft_prompts.completion_for({"task": "deobf", "code_a": "x", "code_b": "y"})


def test_symmetric_arm_shares_one_system_prompt_across_directions():
    """FLIP-sym's whole purpose: two personas must not be able to masquerade as two
    disjoint circuits when the probes look for shared representations."""
    fwd = srh_prompts.build_fwd_messages(PY_ORIG, "python", "L1r", symmetric=True)
    rev = srh_prompts.build_rev_messages(PY_OBF, "python", symmetric=True)
    assert fwd[0]["content"] == rev[0]["content"] == srh_prompts.SYMMETRIC_SYSTEM
    # ...and the direction still differs, carried by the user turn alone.
    assert fwd[-1]["content"] != rev[-1]["content"]


def test_asymmetric_is_the_default_and_uses_the_two_original_personas():
    fwd = srh_prompts.build_fwd_messages(PY_ORIG, "python", "L1r")
    rev = srh_prompts.build_rev_messages(PY_OBF, "python")
    assert fwd[0]["content"] == cft_prompts.GEN_SYSTEM
    assert rev[0]["content"] == cft_prompts.DEOBF_SYSTEM
    assert fwd[0]["content"] != rev[0]["content"]


def test_build_example_factory_binds_symmetry_without_touching_the_row():
    row = _row("rev")
    sym = srh_prompts.build_example_factory(True)(row)
    asym = srh_prompts.build_example_factory(False)(row)
    assert sym["prompt"][0]["content"] == srh_prompts.SYMMETRIC_SYSTEM
    assert asym["prompt"][0]["content"] == cft_prompts.DEOBF_SYSTEM
    assert "symmetric" not in row, "the factory must not mutate the caller's row"


def test_unknown_tasks_are_rejected():
    with pytest.raises(ValueError, match="unknown task"):
        srh_prompts.assert_tasks_known(["gen", "telepathy"])
    srh_prompts.assert_tasks_known(["gen", "rev", "pos", "neg"])  # no raise


def test_provenance_records_both_template_hashes():
    p = srh_prompts.provenance_block()
    assert len(p["srh_prompt_template_sha256"]) == 64
    assert p["cft_prompt_template_sha256"] == cft_prompts.template_sha256()


def test_cft_template_hash_is_unchanged_by_this_package():
    """The replication's pools on disk record this hash; it must not move."""
    assert cft_prompts.template_sha256() == (
        "101309399bb1223a7cb31bba4bfc493ee1c783057d68e944885fbe8526891862"
    )
