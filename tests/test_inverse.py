"""RQ5' inverse task: the call extractor, the execution grader, and the guarantee that
adding the inverse prompt changed nothing about the forward prompt."""
from __future__ import annotations

import pytest

from obtune import inverse, prompts
from obtune.schema import EvalItem

PROG = "def f(xs, k):\n    return [x * k for x in xs]\n"


def _item(i: int, args_repr: str, output_repr: str) -> EvalItem:
    return EvalItem(item_id=f"p::L0::{i}", program_id="p", dataset="A", condition="L0",
                    language="python", code=PROG, entry_point="f",
                    args_repr=args_repr, output_repr=output_repr)


@pytest.mark.parametrize(
    "text, ok, args",
    [
        ("f([1, 2], 3)", True, "([1, 2], 3,)"),
        ("f([1, 2], 3,)", True, "([1, 2], 3,)"),  # trailing comma from format_call
        ("f(3)", True, "(3,)"),  # one-tuple, not a parenthesised scalar
        ("f()", True, "()"),
        ("```python\nf([1], 2)\n```", True, "([1], 2,)"),
        ("`f((1, 2), {'a': None})`", True, "((1, 2), {'a': None},)"),
        ("g([1], 2)", True, "([1], 2,)"),  # wrong name is not a format failure
        ("f(range(3), 2)", False, None),  # expression
        ("f(x, 2)", False, None),  # variable
        ("The input is f([1], 2)", False, None),  # prose
        ("f([1], 2)\nf([2], 3)", False, None),  # multi-line
        ("[3, 6]", False, None),  # a forward-style literal, the tuned-arm failure mode
        ("", False, None),
    ],
)
def test_extract_call(text, ok, args):
    got_ok, got_args, _ = inverse.extract_call(text)
    assert got_ok is ok
    assert got_args == args


def test_grade_by_execution_not_by_gold_args():
    items = [_item(0, "([1, 2], 3)", "[3,6]")] * 4
    outs = ["f([1, 2], 3)",  # the gold call
            "f([3, 6], 1)",  # a different pre-image: correct, args_exact False
            "f([1, 2], 4)",  # wrong value
            "f(3, [1, 2])"]  # raises TypeError inside the program
    g = inverse.grade_batch(items, outs)
    assert [x.correct for x in g] == [True, True, False, False]
    assert [x.raw_exact for x in g] == [True, False, False, False]
    assert g[2].exec_status == "ok" and inverse.error_category(g[2]) == "wrong_value"
    assert g[3].exec_status == "raised" and inverse.error_category(g[3]) == "call_raised"
    assert all(not x.format_fail for x in g)


def test_format_failure_never_reaches_the_sandbox():
    items = [_item(0, "([1, 2], 3)", "[3,6]")] * 2
    g = inverse.grade_batch(items, ["[3, 6]", "f(range(2), 3)"])
    assert all(x.format_fail and x.exec_status == "not_run" and not x.correct for x in g)


def test_javascript_refused():
    it = _item(0, "([1], 1)", "[1]").model_copy(update={"language": "javascript"})
    with pytest.raises(NotImplementedError):
        inverse.grade_batch([it], ["f([1], 1)"])


def test_forward_prompt_untouched_by_inverse_task():
    fwd = prompts.build_prompt(PROG, "f", "([1, 2], 3)", "python", condition="L0")
    assert fwd == prompts.build_prompt(PROG, "f", "([1, 2], 3)", "python", condition="L0", task="output")
    assert prompts.template_sha256() == prompts.template_sha256(task="output")
    assert prompts.template_sha256() != prompts.template_sha256(task="input")
    assert prompts.prompt_id() == "base_v1"
    assert prompts.prompt_id(task="input", one_shot=True) == "inverse_1shot_v1"


def test_inverse_prompt_shape():
    msgs = prompts.build_prompt(PROG, "f", "([1, 2], 3)", "python", condition="L0",
                                one_shot=True, task="input", output_repr="[3,6]")
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]
    assert msgs[0]["content"] == prompts.SYSTEM_PROMPT_INVERSE
    d = prompts.ONE_SHOT_DEMOS["python"]
    assert msgs[2]["content"] == prompts.format_call(d.entry_point, d.args_repr)
    assert "Return value: [3,6]" in msgs[3]["content"] and "Entry point: f" in msgs[3]["content"]
    assert msgs[3]["content"].endswith("Call:")
    assert "([1, 2], 3)" not in msgs[3]["content"]  # the gold call is never shown
    with pytest.raises(ValueError):
        prompts.build_prompt(PROG, "f", "()", "python", task="input")  # output_repr required
    with pytest.raises(ValueError):
        prompts.build_prompt(PROG, "f", "()", "python", task="input", output_repr="1", trace=True)
