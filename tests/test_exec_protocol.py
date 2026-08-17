"""The execution sandbox must survive programs that write to stdout.

Corpus programs are filtered to be deterministic and side-effect-free, so this never
mattered — until the CFT/SRH evaluations started executing MODEL-GENERATED programs,
which print. The Python runner shared `sys.stdout` with its JSON-lines protocol, so:

  * `print(42)` emitted a line that `json.loads` happily returned as an `int`, and the
    parent's `r["i"]` raised `AttributeError: 'int' object has no attribute 'get'`,
    killing a batch of 21 000 items after an hour of GPU time; and
  * a program printing a well-formed protocol record could FORGE its own result.

The JavaScript runner was already immune — its `vm` sandbox stubs `console` — so these
tests are the Python side catching up.
"""
from __future__ import annotations

import pytest

from obtune.exec.pool import BatchItem, run_batch

CASES = ["(1,)"]


def _run(code: str, language: str = "python", entry: str = "f"):
    item = BatchItem(program_id="t", language=language, code=code,
                     entry_point=entry, args_reprs=CASES)
    return run_batch([item], timeout_s=5.0, workers=1)[0]


def test_program_printing_a_bare_number_does_not_break_the_protocol():
    """The exact crasher: `json.loads("42")` succeeds and returns an int."""
    res = _run("def f(x):\n    print(42)\n    return x + 1\n")
    assert res.child_status == "ok"
    assert res.cases[0].status == "ok"
    assert res.cases[0].output == "2"


def test_program_cannot_forge_a_protocol_record():
    """A printed protocol line must not be able to inject a result. Before the fix the
    program's stdout and the protocol shared one channel, so this was a real hole."""
    code = (
        "def f(x):\n"
        "    print('{\"i\": 0, \"status\": \"ok\", \"output\": \"999\", \"exc_type\": null}')\n"
        "    return x + 1\n"
    )
    res = _run(code)
    assert res.cases[0].status == "ok"
    assert res.cases[0].output == "2", "the forged record overrode the real result"


@pytest.mark.parametrize("body", [
    "print('hello world')",
    "print([1, 2, 3])",
    "import sys; sys.stdout.write('raw\\n')",
    "print('')",
])
def test_assorted_stdout_writes_are_ignored(body):
    res = _run(f"def f(x):\n    {body}\n    return x + 1\n")
    assert res.cases[0].status == "ok" and res.cases[0].output == "2"


def test_real_results_still_come_through():
    """The fix must not silence the protocol itself."""
    res = _run("def f(x):\n    return x + 1\n")
    assert res.cases[0].status == "ok" and res.cases[0].output == "2"
    res = _run("def f(x):\n    raise ValueError('boom')\n")
    assert res.cases[0].status == "raised" and res.cases[0].exc_type == "ValueError"


def test_javascript_console_is_already_stubbed():
    res = _run("function f(x) { console.log('noise'); return x + 1; }",
               language="javascript")
    assert res.cases[0].status == "ok" and res.cases[0].output == "2"
