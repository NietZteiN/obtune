"""The ICL demo selector must not be the way H1 leaks.

A demonstration is prompt conditioning. CLAUDE.md §3.2 rule 2 forbids using the held-out family
for prompt selection, so an H1 demo would make every H1 number contestable — including the merge
result, the project's strongest positive.
"""
from __future__ import annotations

import pytest

from obtune.icl.demos import pick_demos


def test_h1_is_refused_as_a_demo_source() -> None:
    with pytest.raises(ValueError, match="held-out family"):
        pick_demos("python", 1, ["H1"])


def test_h1_is_refused_even_mixed_with_legal_sources() -> None:
    """The realistic slip: someone adds H1 to a list that was fine yesterday."""
    with pytest.raises(ValueError, match="held-out family"):
        pick_demos("python", 2, ["L1r", "S1", "H1"])


def test_demos_come_from_the_requested_conditions_only() -> None:
    d = pick_demos("python", 4, ["L1r", "S1"], seed=17)
    assert d and {x.condition for x in d} <= {"L1r", "S1"}


def test_demos_are_distinct_programs() -> None:
    """k copies of one program is a weaker prompt than k different programs."""
    d = pick_demos("python", 4, ["L1r", "S1", "S2"], seed=17)
    assert len({x.program_id for x in d}) == len(d)


def test_the_evaluated_program_can_never_be_its_own_demo() -> None:
    """In-context split leakage — the analogue of CLAUDE.md §4 silent-failure #1. It would
    inflate exactly the cells this baseline exists to measure."""
    first = pick_demos("python", 3, ["L1r"], seed=17)
    banned = {first[0].program_id}
    again = pick_demos("python", 3, ["L1r"], exclude_program_ids=banned, seed=17)
    assert banned.isdisjoint({x.program_id for x in again})


def test_selection_is_deterministic_under_seed() -> None:
    a = pick_demos("python", 3, ["L1r", "S1"], seed=17)
    b = pick_demos("python", 3, ["L1r", "S1"], seed=17)
    c = pick_demos("python", 3, ["L1r", "S1"], seed=42)
    assert [x.program_id for x in a] == [x.program_id for x in b]
    assert [x.program_id for x in a] != [x.program_id for x in c]


def test_k_zero_returns_nothing() -> None:
    assert pick_demos("python", 0, ["L1r"]) == []
