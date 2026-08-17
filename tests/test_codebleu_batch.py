"""Parallel CodeBLEU must equal serial CodeBLEU, element for element.

This is the guard on a pure-performance change to the harness that produces the paper's
numbers. Profiled 2026-08-11 with py-spy on a live evaluation, the scoring tail is
`codebleu/parser/DFG.py::DFG_python` — single-threaded, GIL-bound data-flow-graph
construction. A 36 000-trial run makes 72 000 such calls and sat in that tail for 52 minutes
on ONE core while 95 were idle, longer than its own generation phase.

Distributing it is only legitimate because CodeBLEU is a pure deterministic function of
(prediction, reference, language) and `executor.map` preserves input order. That is exactly
what these tests assert. If any of them fails, the optimisation is silently rewriting results
and must be reverted rather than debugged in place.
"""
from __future__ import annotations

import pytest

from obtune.cft import metrics
from obtune.cft.evaluate import _codebleu_batch, _codebleu_one

PY_A = "def f(a, b):\n    if a < b:\n        return (b, a)\n    return (a, b)\n"
PY_B = "def f_2b71(v_9c04, v_31aa):\n    if v_9c04 < v_31aa:\n        return (v_31aa, v_9c04)\n    return (v_9c04, v_31aa)\n"
PY_C = "def g(xs):\n    t = 0\n    for x in xs:\n        t += x\n    return t\n"
PY_D = "def f(a, b):\n    return (a, b)\n"


def _pairs(n: int) -> list[tuple[str, str, str]]:
    """Enough pairs to cross the parallel threshold, with varied content."""
    srcs = [PY_A, PY_B, PY_C, PY_D]
    out: list[tuple[str, str, str]] = []
    for i in range(n):
        out.append((srcs[i % len(srcs)], srcs[(i + 1) % len(srcs)], "python"))
    return out


def test_single_call_matches_metrics_directly() -> None:
    assert _codebleu_one((PY_A, PY_B, "python")) == metrics.codebleu_score(PY_A, PY_B, "python")


def test_small_batch_stays_serial_and_is_correct() -> None:
    """Below the threshold the batch helper must still return the right answers."""
    pairs = _pairs(4)
    got = _codebleu_batch(pairs, workers=8)
    want = [metrics.codebleu_score(p, r, lang) for p, r, lang in pairs]
    assert got == want


@pytest.mark.parametrize("workers", [1, 4])
def test_parallel_equals_serial_elementwise(workers: int) -> None:
    """The load-bearing assertion. 128 pairs is above the parallel threshold."""
    pairs = _pairs(128)
    serial = [metrics.codebleu_score(p, r, lang) for p, r, lang in pairs]
    parallel = _codebleu_batch(pairs, workers=workers)
    assert len(parallel) == len(serial)
    for i, (a, b) in enumerate(zip(parallel, serial)):
        assert a == b, f"pair {i} differs: parallel={a} serial={b}"


def test_order_is_preserved_under_heterogeneous_cost() -> None:
    """A pair whose DFG is cheap must not overtake an expensive one in the output.

    `executor.map` guarantees this, but the guarantee is the whole reason the optimisation is
    safe — so it is asserted rather than assumed. The long source costs materially more to
    parse than the short one.
    """
    long_src = "def h(n):\n" + "".join(f"    x{i} = {i} + n\n" for i in range(60)) + "    return n\n"
    pairs: list[tuple[str, str, str]] = []
    for i in range(80):
        pairs.append((long_src, PY_A, "python") if i % 2 == 0 else (PY_D, PY_A, "python"))
    got = _codebleu_batch(pairs, workers=4)
    want = [metrics.codebleu_score(p, r, lang) for p, r, lang in pairs]
    assert got == want


def test_fallback_to_serial_on_pool_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A scoring speedup must never be able to fail a run that would have completed."""
    import concurrent.futures as cf

    class _Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("no workers available")

    monkeypatch.setattr(cf, "ProcessPoolExecutor", _Boom)
    pairs = _pairs(128)
    got = _codebleu_batch(pairs, workers=4)
    want = [metrics.codebleu_score(p, r, lang) for p, r, lang in pairs]
    assert got == want, "fallback path returned different values"
