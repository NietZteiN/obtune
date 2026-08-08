"""Contracts for the CFT prompt builders (src/obtune/cft/prompts.py).

The one that matters most is `test_pos_and_neg_prompts_differ_only_in_the_code`: if the
positive and negative tasks ever render different wording, the YES/NO label leaks through
the template and L_pos/L_neg stop measuring anything semantic — the failure would look
like CFT working spectacularly well.
"""
from __future__ import annotations

import pytest

from obtune.cft import prompts

PY_A = "def add(a, b):\n    return a + b\n"
PY_B = "def f_1a2b(v_0011, v_0012):\n    return v_0011 + v_0012\n"


def _user_turns(messages):
    return [m["content"] for m in messages if m["role"] == "user"]


def test_pos_and_neg_prompts_differ_only_in_the_code():
    pos = prompts.build_messages(
        {"task": "pos", "code_a": PY_A, "code_b": PY_B, "language": "python"}
    )
    neg = prompts.build_messages(
        {"task": "neg", "code_a": PY_A, "code_b": PY_B, "language": "python"}
    )
    assert pos == neg, "pos and neg must render one identical prompt; only the label differs"
    assert prompts.completion_for({"task": "pos", "code_a": PY_A, "code_b": PY_B}) == "YES"
    assert prompts.completion_for({"task": "neg", "code_a": PY_A, "code_b": PY_B}) == "NO"


def test_equivalence_prompt_contains_both_programs_and_no_label_hint():
    msgs = prompts.build_equiv_messages(PY_A, PY_B, "python")
    text = "\n".join(_user_turns(msgs))
    assert PY_A.strip() in text and PY_B.strip() in text
    # "obfuscated"/"mutated" in the user turn would tell the model which pool the pair
    # came from, which is the label.
    for leak in ("obfuscat", "mutat", "equivalent to", "identical"):
        assert leak not in text.lower(), f"prompt leaks the label via {leak!r}"


def test_gen_prompt_matches_the_paper_wording():
    msgs = prompts.build_gen_messages(PY_A, "python", "L1r")
    user = _user_turns(msgs)[0]
    assert user.startswith("Obfuscate the following Python code by ")
    assert "while preserving its functionality." in user
    assert PY_A.strip() in user


def test_gen_target_is_the_obfuscated_program():
    row = {"task": "gen", "code_a": PY_A, "code_b": PY_B, "language": "python", "condition": "L1r"}
    assert prompts.completion_for(row) == PY_B.rstrip("\n")


def test_reverse_direction_has_no_training_target():
    """The reverse task is never supervised — that is the paper's entire test (§2.3)."""
    with pytest.raises(ValueError, match="never supervised"):
        prompts.completion_for({"task": "deobf", "code_b": PY_B, "language": "python"})


@pytest.mark.parametrize("strategy", prompts.DEOBF_STRATEGIES)
def test_every_reverse_strategy_builds_and_shows_the_obfuscated_code(strategy):
    msgs = prompts.build_deobf_messages(PY_B, "python", strategy)
    assert msgs[0]["role"] == "system"
    assert PY_B.strip() in _user_turns(msgs)[-1]
    if strategy in ("few_shot", "augmented"):
        assert any(m["role"] == "assistant" for m in msgs), "few-shot needs a demo answer"
    else:
        assert not any(m["role"] == "assistant" for m in msgs)


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError):
        prompts.build_deobf_messages(PY_B, "python", "telepathy")


def test_extract_code_prefers_the_last_fence():
    """Under CoT the recovered program is the last thing in the reply; a model that
    quotes the input first must not be graded on the input."""
    text = "Input was:\n```python\nJUNK\n```\nRecovered:\n```python\ndef g():\n    return 1\n```"
    code, fenced = prompts.extract_code(text)
    assert fenced and code == "def g():\n    return 1"


def test_extract_code_passes_through_unfenced_output():
    code, fenced = prompts.extract_code("def g():\n    return 1")
    assert not fenced and code == "def g():\n    return 1"


def test_extract_code_recovers_an_unterminated_fence():
    """A reply cut off at max_tokens still yields its body — truncation is recorded
    separately, and an empty string would misreport it as a refusal."""
    code, fenced = prompts.extract_code("```python\ndef g():\n    return 1")
    assert fenced and code.startswith("def g():")


@pytest.mark.parametrize(
    "text,expected",
    [
        ("YES", True),
        ("no", False),
        ("NO, they are not the same - yes, the names differ", False),
        ("Yes, both compute the same value", True),
        ("I cannot determine that", None),
        ("", None),
    ],
)
def test_parse_equivalence(text, expected):
    assert prompts.parse_equivalence(text) is expected


def test_template_hash_is_stable_and_content_addressed():
    first = prompts.template_sha256()
    assert first == prompts.template_sha256()
    assert len(first) == 64
    assert prompts.provenance_block()["cft_prompt_template_sha256"] == first


def test_demo_ids_are_namespaced_away_from_corpus_programs():
    ids = {d.program_id for d in prompts.DEOBF_DEMOS.values()}
    assert all(i.startswith("cft_demo_") for i in ids)
    with pytest.raises(ValueError):
        prompts.assert_demo_disjoint(list(ids))
    prompts.assert_demo_disjoint(["apps_122_0"])  # no clash -> no raise


def test_technique_names_cover_every_trainable_condition_and_exclude_h1():
    from obtune import paths

    assert set(prompts.TECHNIQUE_NAMES) == set(paths.TRAINABLE_CONDITIONS)
    assert "H1" not in prompts.TECHNIQUE_NAMES
