"""The CodeBLEU wall-clock guard must actually bound a real `DFG_python` blow-up.

Incident of 2026-08-11 (`log/cft-replication/2026-08-11_codebleu-scoring-hang.md`): four
evaluation cells died twice without producing a verdict because
`codebleu/parser/DFG.py::DFG_python` does not terminate on a deeply-nested prediction.
Nine pool workers sat at 100 % CPU for 71-102 minutes each while four GPUs held 164 GB of
idle vLLM engine.

`NESTED_FOR_20` below is the reproduction: unguarded, `codebleu_score` on it does not
return. If these tests start failing, the guard is gone and an evaluation can hang again.
"""
from __future__ import annotations

import time

from obtune.cft import metrics

REF = "def f(a):\n    return a + 1\n"

#: 20 nested for-loops. Nesting DEPTH of compound statements is the trigger, not length:
#: nested `if`, chained assignment and deep parenthesised expressions all score in under
#: 0.03 s at depths up to 160.
NESTED_FOR_20 = (
    "def f(a):\n"
    + "".join("    " * (i + 1) + f"for v{i} in range(a):\n" for i in range(20))
    + "    " * 21
    + "a = a + 1\n    return a\n"
)

ORDINARY = "def f(a, b):\n    if a < b:\n        return (b, a)\n    return (a, b)\n"


def test_pathological_prediction_is_bounded(monkeypatch) -> None:
    """The call returns, inside the bound, flagged — instead of never returning."""
    monkeypatch.setattr(metrics, "_CODEBLEU_TIMEOUT_S", 2.0)
    t = time.perf_counter()
    res = metrics.codebleu_score(NESTED_FOR_20, REF, "python")
    elapsed = time.perf_counter() - t
    assert res["timeout"] == 1.0
    assert elapsed < 10.0, f"guard did not bound the call ({elapsed:.1f}s)"
    assert res["codebleu"] == 0.0


def test_timeout_does_not_leak_into_the_next_call(monkeypatch) -> None:
    """A pending itimer or a left-behind handler would corrupt every later score, which
    is far worse than the hang it replaced."""
    monkeypatch.setattr(metrics, "_CODEBLEU_TIMEOUT_S", 2.0)
    before = metrics.codebleu_score(ORDINARY, REF, "python")
    metrics.codebleu_score(NESTED_FOR_20, REF, "python")
    after = metrics.codebleu_score(ORDINARY, REF, "python")
    assert after == before


def test_ordinary_pair_is_untouched_by_the_guard() -> None:
    """The bound is ~450x the mean call, so a real score must be unflagged and non-zero."""
    res = metrics.codebleu_score(ORDINARY, REF, "python")
    assert res["timeout"] == 0.0
    assert res["codebleu"] > 0.0


def test_alarm_is_not_swallowed_by_except_exception() -> None:
    """`_CodeBleuTimeout` derives from BaseException on purpose: codebleu's own
    `except Exception` handlers would otherwise catch the alarm and resume the recursion."""
    raised = False
    try:
        with metrics._time_limit(1.0):
            try:
                while True:
                    pass
            except Exception:  # noqa: BLE001 — the point of the test
                raise AssertionError("alarm was swallowed by except Exception")
    except metrics._CodeBleuTimeout:
        raised = True
    assert raised


def test_oversize_prediction_is_skipped_without_parsing() -> None:
    res = metrics.codebleu_score("x = 1\n" * 20_000, REF, "python")
    assert res["timeout"] == 1.0


def test_timeout_key_is_always_present() -> None:
    """Fixed key set across every return path, so the trial rows are not ragged."""
    empty = metrics.codebleu_score("", REF, "python")
    scored = metrics.codebleu_score(ORDINARY, REF, "python")
    assert "timeout" in empty and "timeout" in scored
    assert set(empty) == set(scored)
