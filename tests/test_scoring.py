"""Grader contract tests, built around the false-positive audit in ../LOG.md §2026-06-09.

Every accuracy number in the paper flows through `scoring.grade`. The cases below are
not illustrative: each one is a grading bug that was observed in the previous harness
and that would inflate or deflate the transfer matrix if it came back.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from obtune.scoring import (  # noqa: E402
    DEFAULT_FLOAT_TOL,
    Grade,
    deep_equal,
    error_category,
    grade,
    grade_batch,
    normalize,
    parse_literal,
    raw_exact_match,
)


# --------------------------------------------------------------------------- #
# The audit traps — these are the regressions we are actively defending against
# --------------------------------------------------------------------------- #

def test_trap_containment_substring_is_wrong():
    """LOG.md 2026-06-09: the deleted stage-4 containment check scored '927' correct
    inside '9273'. ~3 % false positives, larger than the effects we measure."""
    g = grade("9273", "927", "python")
    assert g.correct is False
    assert g.method == "none"
    # ... and the reverse direction, and the prompt-echo shape of the same bug.
    assert grade("927", "9273", "python").correct is False
    assert grade("The output is 927 for this call", "927", "python").correct is False


def test_trap_bracketless_sequence_is_wrong():
    """'[2,4,6,8]' vs '2, 4, 6, 8': literal_eval yields a tuple, not the gold list.
    Type discipline between list and tuple is what makes this fail."""
    g = grade("2, 4, 6, 8", "[2,4,6,8]", "python")
    assert g.correct is False
    assert g.parse_ok is True  # it parsed fine — it is simply a different value
    assert g.format_fail is False
    assert error_category(g, "python") == "wrong_type"


def test_trap_python_bool_case_ok_javascript_not():
    """'True' vs 'true' is correct for Python (literal_eval accepts the Python repr,
    json.loads accepts the canonical form) and WRONG for JavaScript, whose output
    vocabulary is JSON only."""
    g_py = grade("true", "True", "python")
    assert g_py.correct is True
    assert g_py.method == "structural"

    assert grade("True", "true", "python").correct is True

    g_js = grade("True", "true", "javascript")
    assert g_js.correct is False
    assert g_js.parse_ok is False
    assert g_js.format_fail is True


def test_trap_float_tolerance_nested_in_container():
    """Tolerance must recurse: a float three levels down still gets 1e-6 of slack."""
    g = grade('[1, {"k": [0.3333333333]}]', '[1,{"k":[0.33333333333333]}]', "python")
    assert g.correct is True
    assert g.method == "numeric"
    # ... and a difference above the tolerance is still wrong.
    assert grade("[0.3334]", "[0.33333333333333]", "python").correct is False


def test_trap_code_fenced_answer_is_correct_after_normalization():
    for fenced in ("```\n[1,2,3]\n```", "```python\n[1,2,3]\n```", "`[1,2,3]`", "[1,2,3]."):
        g = grade(fenced, "[1,2,3]", "python")
        assert g.correct is True, fenced
        assert g.method == "normalized", fenced
        assert g.raw_exact is False, fenced


def test_trap_case_sensitivity_of_string_contents():
    """The old normalize_for_compare lowercased. 'ABC' and 'abc' are different
    execution outputs and must grade as different."""
    assert grade('"abc"', '"ABC"', "python").correct is False
    assert grade('"ABC"', '"ABC"', "python").correct is True
    assert grade('["Ab","cD"]', '["ab","cd"]', "javascript").correct is False


def test_trap_bool_is_not_one():
    assert grade("1", "true", "python").correct is False
    assert grade("true", "1", "python").correct is False
    assert deep_equal(True, 1) is False


def test_trap_big_int_not_absorbed_by_relative_tolerance():
    gold = "1000000000000000000"
    assert grade("1000000000000000001", gold, "python").correct is False
    assert grade(gold, gold, "python").correct is True


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def test_normalize_rules():
    assert normalize("  [1,2]  \n") == "[1,2]"
    assert normalize("```json\n{\"a\":1}\n```") == '{"a":1}'
    assert normalize("`42`") == "42"
    assert normalize("42.") == "42"
    assert normalize("42..") == "42."  # only ONE trailing period is dropped
    assert normalize('"ends with period."') == '"ends with period."'
    assert normalize("```\n[1,2]\n```.") == "[1,2]"


def test_normalize_does_not_extract_answers():
    """Deliberately NOT repairing prose: format_fail_rate is a reported metric."""
    g = grade("The answer is: 42", "42", "python")
    assert g.correct is False
    assert g.format_fail is True
    assert error_category(g, "python") == "unparseable"


def test_no_lowercasing_in_normalize():
    assert normalize("True") == "True"


# --------------------------------------------------------------------------- #
# Stage attribution and the raw_exact appendix column
# --------------------------------------------------------------------------- #

def test_method_stage_order():
    assert grade("[1,2]", "[1,2]", "python").method == "exact"
    assert grade(" [1,2] ", "[1,2]", "python").method == "exact"  # strip only == raw
    assert grade("```\n[1,2]\n```", "[1,2]", "python").method == "normalized"
    assert grade("[1, 2]", "[1,2]", "python").method == "structural"
    assert grade("[1.0000001]", "[1]", "python").method == "numeric"
    assert grade("[9]", "[1]", "python").method == "none"


def test_raw_exact_is_stricter_than_correct():
    g = grade("[1, 2]", "[1,2]", "python")
    assert g.correct is True and g.raw_exact is False
    assert raw_exact_match(" [1,2]\n", "[1,2]") is True
    assert g.grade_method == "normalized"
    assert grade("[1,2]", "[1,2]", "python").grade_method == "exact"


def test_integral_float_collapses_like_canon():
    """canon prints 2.0 as 2 (JS has one number type); a model answering 2.0 is right."""
    assert grade("2.0", "2", "python").correct is True
    assert grade("[2.0,3.0]", "[2,3]", "javascript").correct is True


# --------------------------------------------------------------------------- #
# Parsing / structures
# --------------------------------------------------------------------------- #

def test_dict_key_order_irrelevant_after_parse():
    assert grade('{"b":2,"a":1}', '{"a":1,"b":2}', "python").correct is True
    assert grade('{"b":2,"a":1}', '{"a":1,"b":2}', "javascript").correct is True


def test_dict_key_mismatch_wrong():
    assert grade('{"a":1}', '{"a":1,"b":2}', "python").correct is False
    assert grade('{"a":1,"c":2}', '{"a":1,"b":2}', "python").correct is False


def test_python_repr_strings_accepted_javascript_strings_not():
    assert grade("'abc'", '"abc"', "python").correct is True
    assert grade("'abc'", '"abc"', "javascript").correct is False
    assert grade("None", "null", "python").correct is True
    assert grade("None", "null", "javascript").correct is False


def test_empty_and_whitespace_predictions():
    g = grade("", "[1]", "python")
    assert g.correct is False and g.format_fail is True
    assert error_category(g, "python") == "empty"
    assert error_category(grade("[1,\n2", "[1,2]", "python"), "python") == "multiline"


def test_parse_literal_rejects_unknown_language():
    with pytest.raises(ValueError):
        parse_literal("1", "ruby")


def test_nested_length_and_element_categories():
    assert error_category(grade("[1,2]", "[1,2,3]", "python"), "python") == "wrong_length"
    assert error_category(grade("[1,2,4]", "[1,2,3]", "python"), "python") == "wrong_elements"


def test_grade_batch_shapes():
    gs = grade_batch(["1", "2"], ["1", "3"], "python")
    assert [g.correct for g in gs] == [True, False]
    with pytest.raises(ValueError):
        grade_batch(["1"], ["1", "2"], "python")
    assert set(Grade(True, True, False, "exact", "1", "1").as_dict()) == {
        "correct", "parse_ok", "format_fail", "method", "pred_norm", "gold_norm", "raw_exact",
    }


def test_default_tolerance_is_the_configured_one():
    """configs/eval/_base_eval.yaml pins float_tol: 1.0e-6; keep the code default in sync."""
    assert DEFAULT_FLOAT_TOL == 1e-6
