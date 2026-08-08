"""The negative pool's guarantee: every negative is EXECUTED and proven different.

If these tests pass but the guarantee is wrong, L_neg trains the model to call
semantically-equivalent programs inequivalent, and CFT's classification heads learn the
opposite of what they are for. That failure is invisible in the loss curve, so it is
checked here rather than assumed.
"""
from __future__ import annotations

import pytest

from obtune.cft import mutate

PY_SRC = """def clamp_sum(values, limit):
    total = 0
    for v in values:
        if v > 0 and v < limit:
            total = total + v
    return total
"""

JS_SRC = """function clampSum(values, limit) {
    let total = 0;
    for (const v of values) {
        if (v > 0 && v < limit) {
            total = total + v;
        }
    }
    return total;
}
"""

PY_CASES = [
    {"args_repr": "([1, 2, 3, 9], 5,)", "output_canon": "6"},
    {"args_repr": "([-1, 4, 4], 5,)", "output_canon": "8"},
    {"args_repr": "([], 3,)", "output_canon": "0"},
]

JS_CASES = list(PY_CASES)


def _program(language, code, entry, cases):
    return {
        "program_id": f"t_{language}",
        "language": language,
        "code": code,
        "entry_point": entry,
        "cases": cases,
        "gate_inputs": [],
    }


def test_candidates_cover_every_operator_family():
    families = {c.family for c in mutate.candidates("python", PY_SRC)}
    assert {"AOR", "ROR", "LCR", "ICR"} <= families


def test_candidates_never_touch_string_or_comment_content():
    """Operator swaps are found through the parse tree, so a `+` inside a literal is
    invisible to them. A regex-based implementation would corrupt the string."""
    src = 'def f():\n    return "a + b and c < d"\n'
    assert [c for c in mutate.candidates("python", src) if c.family != "ICR"] == []


def test_applying_a_candidate_changes_exactly_one_token():
    cands = mutate.candidates("python", PY_SRC)
    cand = next(c for c in cands if c.family == "ROR")
    out = mutate.apply_candidate(PY_SRC, cand)
    assert out != PY_SRC
    assert len(out.split()) == len(PY_SRC.split())


def test_proposals_are_deterministic_under_a_seed():
    a = mutate.propose("p", "python", PY_SRC, "clamp_sum", n=3, seed=17)
    b = mutate.propose("p", "python", PY_SRC, "clamp_sum", n=3, seed=17)
    c = mutate.propose("p", "python", PY_SRC, "clamp_sum", n=3, seed=18)
    assert [m.code for m in a] == [m.code for m in b]
    assert [m.code for m in a] != [m.code for m in c]


def test_proposals_spread_across_distinct_offsets():
    ms = mutate.propose("p", "python", PY_SRC, "clamp_sum", n=4, seed=17)
    offsets = [m.candidate.start_byte for m in ms]
    assert len(set(offsets)) == len(offsets)


@pytest.mark.parametrize(
    "language,src,entry,cases",
    [("python", PY_SRC, "clamp_sum", PY_CASES), ("javascript", JS_SRC, "clampSum", JS_CASES)],
)
def test_verified_mutants_really_differ_from_their_parent(language, src, entry, cases):
    kept, stats = mutate.verify(
        [_program(language, src, entry, cases)], n_per_program=8, seed=17, keep_per_program=8
    )
    assert kept, f"no verified mutant for {language}: {stats.as_dict()}"
    for m in kept:
        assert m.verified
        assert m.n_cases_differing >= 1
        assert m.code != m.parent_code


def test_equivalent_mutants_are_rejected():
    """The classic mutation-testing failure: a mutant the test inputs cannot tell apart.

    Both guards are satisfied by x = 5 with room to spare, so `and`->`or` leaves the
    observable behaviour unchanged. It must not be accepted as a negative — labelling it
    NO would train the model that semantically equivalent programs differ.
    """
    src = "def f(x):\n    if x > 0 and x > -1:\n        return 1\n    return 0\n"
    cases = [{"args_repr": "(5,)", "output_canon": "1"}]
    # LCR only: `and`->`or` on two guards that x = 5 already satisfies is the clean
    # equivalent-mutant case. The other families would genuinely change the output here
    # (`>`->`<`, `return 1`->`return 0`), which is a different test.
    kept, stats = mutate.verify(
        [_program("python", src, "f", cases)], n_per_program=8, seed=17,
        keep_per_program=8, families=["LCR"],
    )
    assert not kept, [m.candidate.note for m in kept]
    assert stats.reject_reasons.get("equivalent_mutant", 0) >= 1


def test_mutants_that_break_everywhere_are_rejected():
    """A negative that raises on every input is spottable from the traceback alone and
    teaches nothing about semantics — see the mutate.py module docstring."""
    src = "def f(s):\n    return s + '!'\n"
    cases = [
        {"args_repr": "('a',)", "output_canon": '"a!"'},
        {"args_repr": "('b',)", "output_canon": '"b!"'},
    ]
    kept, stats = mutate.verify(
        [_program("python", src, "f", cases)], n_per_program=8, seed=17,
        keep_per_program=8, min_ok_fraction=0.5,
    )
    # '+' -> '-' on a string raises TypeError on every case.
    assert all(m.n_cases_ok >= 1 for m in kept)
    assert stats.reject_reasons.get("mutant_mostly_broken", 0) >= 1


def test_program_that_never_runs_yields_no_negatives():
    """No clean parent run means no semantic reference, so nothing can be proven
    different. The `+ 1` is there only so the program HAS a mutation candidate; without
    one the program is skipped before execution and the check would pass vacuously."""
    kept, stats = mutate.verify(
        [_program("python", "def f(x):\n    return undefined_name(x) + 1\n", "f",
                  [{"args_repr": "(1,)", "output_canon": "1"}])],
        n_per_program=4, seed=17,
    )
    assert not kept
    assert stats.reject_reasons.get("parent_never_ok", 0) == 1


def test_unparseable_source_yields_no_candidates():
    assert mutate.candidates("python", "def (((") == []


def test_stats_report_program_coverage_not_just_proposal_rate():
    kept, stats = mutate.verify(
        [_program("python", PY_SRC, "clamp_sum", PY_CASES)],
        n_per_program=6, seed=17, keep_per_program=1,
    )
    d = stats.as_dict()
    assert d["program_coverage"] == len(kept) / 1
    assert d["verify_rate"] <= d["program_coverage"]
