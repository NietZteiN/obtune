"""Anchor tests for the CFT metrics.

These pin the *direction* and the *endpoints* of each metric, not its exact values —
CodeBLEU is an external implementation and the readability proxy is explicitly a
substitute (see metrics.py). What must never silently change is which way each metric
points when code is obfuscated, because every conclusion in the replication is a
comparison of those directions.
"""
from __future__ import annotations

import math

import pytest

from obtune.cft import metrics

ORIG = """def running_total(numbers, start):
    total = start
    output = []
    for number in numbers:
        total = total + number
        output.append(total)
    return output
"""

HEX_RENAMED = """def f_2b71(v_9c04, v_31aa):
    v_c7e2 = v_31aa
    v_0f13 = []
    for v_88ac in v_9c04:
        v_c7e2 = v_c7e2 + v_88ac
        v_0f13.append(v_c7e2)
    return v_0f13
"""

MINIFIED = """def a(b, c):
    d = c
    e = []
    for f in b:
        d = d + f
        e.append(d)
    return e
"""

UNRELATED = """class Widget:
    def render(self, template):
        return template.format(width=self.width)
"""

CASES = [
    {"args_repr": "([1, 2, 3], 10,)", "output_canon": "[11,13,16]"},
    {"args_repr": "([], 0,)", "output_canon": "[]"},
]


# --------------------------------------------------------------------------- #
# CodeBLEU

def test_codebleu_is_one_for_identical_code():
    assert metrics.codebleu_score(ORIG, ORIG, "python")["codebleu"] == pytest.approx(1.0)


def test_codebleu_ranks_renamed_above_unrelated():
    renamed = metrics.codebleu_score(HEX_RENAMED, ORIG, "python")["codebleu"]
    unrelated = metrics.codebleu_score(UNRELATED, ORIG, "python")["codebleu"]
    assert renamed > unrelated


def test_codebleu_of_empty_prediction_is_zero_not_an_error():
    """A model that answered with nothing must score, not crash — dropping those rows
    would flatter whichever arm fails most often."""
    res = metrics.codebleu_score("", ORIG, "python")
    assert res["codebleu"] == 0.0
    assert set(metrics.CODEBLEU_COMPONENTS) <= set(res)


def test_codebleu_survives_unparseable_predictions():
    assert metrics.codebleu_score("}}} not code {{{", ORIG, "python")["codebleu"] >= 0.0


def test_codebleu_works_for_javascript():
    js = "function f(a) { return a + 1; }"
    assert metrics.codebleu_score(js, js, "javascript")["codebleu"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Readability proxy

def test_readability_orders_original_above_both_identifier_obfuscations():
    r_orig = metrics.readability_proxy(ORIG, "python").score
    r_hex = metrics.readability_proxy(HEX_RENAMED, "python").score
    r_min = metrics.readability_proxy(MINIFIED, "python").score
    assert r_orig > r_hex
    assert r_orig > r_min


def test_minified_code_is_not_scored_as_idiomatic_short_names():
    """Single letters are idiom in a minority; when they are *every* binding they are
    minification. Without this distinction the proxy rates L2 as perfectly readable."""
    comps = metrics.readability_proxy(MINIFIED, "python").components
    assert comps["identifier_meaning"] < 0.5


def test_idiomatic_short_names_in_ordinary_code_are_not_penalised():
    src = (
        "def running_total(numbers, start):\n"
        "    total = start\n"
        "    for n in numbers:\n"
        "        total = total + n\n"
        "    return total\n"
    )
    assert metrics.readability_proxy(src, "python").components["identifier_meaning"] > 0.5


def test_readability_is_bounded_and_empty_code_scores_zero():
    for code in (ORIG, HEX_RENAMED, MINIFIED, UNRELATED):
        assert 0.0 <= metrics.readability_proxy(code, "python").score <= 1.0
    assert metrics.readability_proxy("", "python").score == 0.0


def test_readability_weights_sum_to_one():
    assert sum(metrics.READABILITY_WEIGHTS.values()) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Identifier recall

def test_identifier_recall_is_one_for_the_original_and_low_for_renamed():
    assert metrics.identifier_recall(ORIG, ORIG, "python") == pytest.approx(1.0)
    assert metrics.identifier_recall(HEX_RENAMED, ORIG, "python") < 0.5


def test_identifier_recall_is_nan_when_the_reference_has_no_meaningful_names():
    """No meaningful names to recover means the metric is undefined, not zero — a zero
    would drag the mean down for programs the metric cannot speak about."""
    nameless = "def f_2b71(v_9c04):\n    return v_9c04 + 1\n"
    assert math.isnan(metrics.identifier_recall(ORIG, nameless, "python"))


# --------------------------------------------------------------------------- #
# Entry-point resolution and execution

def test_resolve_entry_point_prefers_the_recovered_original_name():
    assert metrics.resolve_entry_point(ORIG, "python", "running_total") == "running_total"


def test_resolve_entry_point_falls_back_to_the_sole_function():
    assert metrics.resolve_entry_point(HEX_RENAMED, "python", "running_total") == "f_2b71"


def test_resolve_entry_point_takes_the_last_of_several():
    src = "def helper(x):\n    return x\n\ndef main(x):\n    return helper(x)\n"
    assert metrics.resolve_entry_point(src, "python", "absent") == "main"


def test_resolve_entry_point_is_none_when_nothing_is_defined():
    assert metrics.resolve_entry_point("x = 1", "python", "f") is None


def test_exec_equivalence_statuses():
    cands = [
        {"code": ORIG, "language": "python", "entry_point": "running_total", "cases": CASES},
        {"code": HEX_RENAMED, "language": "python", "entry_point": "running_total", "cases": CASES},
        {"code": ORIG.replace("total + number", "total - number"), "language": "python",
         "entry_point": "running_total", "cases": CASES},
        {"code": "def (((", "language": "python", "entry_point": "f", "cases": CASES},
        {"code": "x = 1", "language": "python", "entry_point": "f", "cases": CASES},
    ]
    got = [v.status for v in metrics.exec_equivalence(cands)]
    # renamed code is still semantically the original, which is the whole premise of the
    # identifier conditions — if this ever reports `mismatch`, the corpus gate is broken
    assert got[:2] == ["match", "match"]
    assert got[2] == "mismatch"
    assert got[3] == "parse_fail"
    assert got[4] == "no_entry_point"


def test_exec_equivalence_handles_javascript():
    js = "function f(a) { return a + 1; }"
    v = metrics.exec_equivalence(
        [{"code": js, "language": "javascript", "entry_point": "f",
          "cases": [{"args_repr": "(1,)", "output_canon": "2"}]}]
    )[0]
    assert v.status == "match"


# --------------------------------------------------------------------------- #
# Success criteria

def test_reverse_success_needs_both_halves_of_the_papers_criterion():
    # low similarity to the obfuscated input AND readability restored
    assert metrics.reverse_success_paper(0.2, 0.9, 0.9, parses=True)
    # still looks like the obfuscated input
    assert not metrics.reverse_success_paper(0.8, 0.9, 0.9, parses=True)
    # readability not recovered
    assert not metrics.reverse_success_paper(0.2, 0.3, 0.9, parses=True)


def test_reverse_success_requires_the_output_to_be_code():
    """As literally stated, the paper's criterion is two inequalities that ANY non-input
    reply satisfies. A stub run scored 17-25 % "reverse success" on the placeholder
    string `<stub:a1b2c3>` before this guard existed."""
    assert not metrics.reverse_success_paper(0.0, 1.0, 0.9, parses=False)


def test_non_code_scores_zero_readability():
    """tree-sitter is error-tolerant, so garbage yields identifier-ish tokens and would
    otherwise earn a middling readability that feeds straight into the success criterion."""
    assert metrics.readability_proxy("<stub:a1b2c3>", "python").score == 0.0
    assert metrics.readability_proxy("}}} not code {{{", "python").score == 0.0


def test_forward_success_requires_an_exact_execution_match():
    assert metrics.forward_success_exec(metrics.ExecVerdict("match", 3, 3))
    assert not metrics.forward_success_exec(metrics.ExecVerdict("mismatch", 3, 2))


# --------------------------------------------------------------------------- #
# Structural recovery — the reverse criterion for S1, where the paper's is vacuous

FLATTENED = """def running_total(numbers, start):
    _st = 39
    total = start
    output = []
    while _st != -1:
        if _st == 39:
            _it = iter(numbers)
            _st = 86
        elif _st == 86:
            _nx = next(_it, None)
            _st = 52 if _nx is None else 127
        elif _st == 127:
            total = total + _nx
            output.append(total)
            _st = 86
        elif _st == 52:
            _st = -1
    return output
"""


def test_dispatch_loop_detected_in_flattened_code_only():
    assert metrics.control_flow_signature(FLATTENED, "python")["dispatch_loop"] == 1.0
    assert metrics.control_flow_signature(ORIG, "python")["dispatch_loop"] == 0.0
    assert metrics.control_flow_signature(HEX_RENAMED, "python")["dispatch_loop"] == 0.0


def test_control_flow_signature_counts_branches_and_loops():
    sig = metrics.control_flow_signature(ORIG, "python")
    assert sig["n_loops"] == 1.0
    assert sig["max_depth"] >= 1.0
    assert metrics.control_flow_signature("", "python")["n_loops"] == 0.0


def test_structural_recovery_accepts_the_true_original():
    assert metrics.structural_recovery(ORIG, ORIG, FLATTENED, "python")


def test_structural_recovery_rejects_echoing_the_obfuscated_input():
    """The failure the paper reports for every SFT model in reverse (§4.3.3):
    "outputs nearly identical to the obfuscated input"."""
    assert not metrics.structural_recovery(FLATTENED, ORIG, FLATTENED, "python")


def test_structural_recovery_rejects_non_code():
    assert not metrics.structural_recovery("<stub:a1b2c3>", ORIG, FLATTENED, "python")
    assert not metrics.structural_recovery("", ORIG, FLATTENED, "python")


def test_structural_recovery_is_false_when_the_input_was_not_structural():
    """Nothing structural to recover means the metric has nothing to say — report it
    only for S1/S2, never as a general reverse criterion."""
    assert not metrics.structural_recovery(ORIG, ORIG, HEX_RENAMED, "python")
