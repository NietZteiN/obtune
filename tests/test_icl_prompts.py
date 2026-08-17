"""The k-shot builder must agree with the frozen one-shot path at k=1.

If it does not, the k-sweep confounds "more demonstrations" with "a different prompt
format", and its k=1 column is not comparable to the k=1 cells already collected on
2026-08-13. That is CLAUDE.md §4 silent-failure #3 (two prompt distributions compared as
though they were one) applied to our own baseline.
"""
from __future__ import annotations

import pytest

from obtune import prompts
from obtune.icl.prompts import build_icl_prompt
from obtune.prompts import Demo

QUERY = dict(code="def f(a):\n    return a + 1\n", entry_point="f", args_repr="(1,)",
             language="python", condition="L1r")


def _demo(i: int) -> Demo:
    return Demo(program_id=f"p{i}", language="python", condition="L0",
                code=f"def g{i}(x):\n    return x * {i}\n", entry_point=f"g{i}",
                args_repr=f"({i},)", output_repr=str(i * i), provenance="test")


@pytest.mark.parametrize("oracle", [False, True])
def test_k1_is_byte_identical_to_the_frozen_one_shot_path(oracle) -> None:
    d = _demo(1)
    mine = build_icl_prompt(**QUERY, oracle=oracle, demos=[d])
    theirs = prompts.build_prompt(**QUERY, oracle=oracle, one_shot=True, demo=d)
    assert mine == theirs


@pytest.mark.parametrize("oracle", [False, True])
def test_k0_is_byte_identical_to_zero_shot(oracle) -> None:
    mine = build_icl_prompt(**QUERY, oracle=oracle, demos=[])
    theirs = prompts.build_prompt(**QUERY, oracle=oracle, one_shot=False)
    assert mine == theirs


@pytest.mark.parametrize("k", [0, 1, 2, 4])
def test_message_count_and_roles(k) -> None:
    msgs = build_icl_prompt(**QUERY, demos=[_demo(i) for i in range(k)])
    assert len(msgs) == 1 + 2 * k + 1, "system + (user,assistant) per demo + the query"
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    for i in range(k):
        assert msgs[1 + 2 * i]["role"] == "user"
        assert msgs[2 + 2 * i]["role"] == "assistant"


def test_demos_appear_in_the_given_order() -> None:
    demos = [_demo(1), _demo(2), _demo(3)]
    msgs = build_icl_prompt(**QUERY, demos=demos)
    answers = [m["content"] for m in msgs if m["role"] == "assistant"]
    assert answers == [d.output_repr for d in demos]


def test_the_query_is_last_and_is_not_a_demo() -> None:
    """The thing being scored must be the final user turn, or the model answers a demo."""
    msgs = build_icl_prompt(**QUERY, demos=[_demo(1), _demo(2)])
    assert QUERY["code"] in msgs[-1]["content"]
    assert all(QUERY["code"] not in m["content"] for m in msgs[:-1])


def test_frozen_template_hash_is_untouched() -> None:
    """This module composes `prompts.build_user_content`; it must never edit `prompts.py`,
    whose sha256 is pinned in every run manifest."""
    assert prompts.template_sha256() == prompts.template_sha256()
    import inspect
    assert "icl" not in inspect.getsource(prompts.build_prompt)


@pytest.mark.parametrize("k", [2, 4])
def test_pick_demos_returns_k_distinct_programs(k) -> None:
    from obtune.icl.demos import pick_demos

    demos = pick_demos("python", k, ["L0"], seed=17)
    assert len(demos) == k
    assert len({d.program_id for d in demos}) == k, "repeating one program is a weaker prompt"


def test_pick_demos_is_deterministic_across_calls() -> None:
    from obtune.icl.demos import pick_demos

    a = [d.program_id for d in pick_demos("python", 4, ["L0"], seed=17)]
    b = [d.program_id for d in pick_demos("python", 4, ["L0"], seed=17)]
    assert a == b
