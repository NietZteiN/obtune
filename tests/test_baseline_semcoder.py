"""SemCoder's prompt and answer contract, pinned.

A baseline is only meaningful if it is run the way its authors ran it. These tests
pin the two places that silently destroy the comparison: calling the wrong function,
and parsing the wrong side of the assertion.
"""
from __future__ import annotations

import pytest

from obtune.baselines.semcoder import (
    SemCoderSpec, cot_prompt, extract_answer, monologue_prompt,
)

CODE = 'def count_chars(s):\n    counts = {}\n    return counts\n'


def test_monologue_uses_the_real_entry_point():
    """CRUXEval always names the function `f`; our entry points are arbitrary AND the
    identifier conditions rename them. Hardcoding `f` would ask for a function the
    program does not define."""
    p = monologue_prompt(CODE, "count_chars", '("hi",)')
    assert 'assert count_chars("hi") == ??' in p
    assert "assert f(" not in p


def test_monologue_labels_lines_without_the_upstream_offset():
    """Upstream adds +4 because CRUXEval wraps code in a preamble; ours has none, so
    the same offset would mislabel every line."""
    p = monologue_prompt("def g(x):\n    return x\n", "g", "(1,)")
    assert "def g(x): # [L1]" in p
    assert "    return x # [L2]" in p


def test_single_argument_tuple_loses_its_trailing_comma():
    """`("hi",)` must become `f("hi")`, not `f(("hi",))` — the latter is a different
    call, with a tuple as its single argument."""
    assert 'assert g("hi") ==' in monologue_prompt("def g(s):\n    return s\n", "g", '("hi",)')
    assert 'assert g(1, 2) ==' in monologue_prompt("def g(a,b):\n    return a\n", "g", "(1, 2)")


def test_blank_lines_are_not_labelled():
    p = monologue_prompt("def g(x):\n\n    return x\n", "g", "(1,)")
    assert " # [L2]" not in p  # the blank line


@pytest.mark.parametrize("gen,expected", [
    ('[MONOLOGUE]\nreasoning\n[ANSWER]\nassert f("hi") == "bhihia"\n[/ANSWER]', '"bhihia"'),
    ('[ANSWER] assert g(1) == {"a":1} [/ANSWER]', '{"a":1}'),
    ('no tags at all, assert f(1) == 42', "42"),
    ('[ANSWER]\nassert f(1) == [1, 2]', "[1, 2]"),
])
def test_extract_answer_takes_the_right_hand_side(gen, expected):
    """Output prediction reads the RIGHT of `==`. The left is the answer to the
    *input*-prediction task — taking it is a silent way to score zero everywhere."""
    assert extract_answer(gen) == expected


def test_cot_prompt_keeps_the_upstream_worked_example():
    p = cot_prompt(CODE, "count_chars", '("hi",)')
    assert '"bhihia"' in p          # the upstream demonstration
    assert "[THOUGHT]" in p
    assert 'assert count_chars("hi") == ??' in p


def test_spec_selects_the_style():
    assert "[MONOLOGUE]" in SemCoderSpec(style="monologue").build(CODE, "count_chars", '("hi",)')
    assert "[THOUGHT]" in SemCoderSpec(style="cot").build(CODE, "count_chars", '("hi",)')
