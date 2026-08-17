"""A tripped adapter guard must fail the run WITHOUT destroying the evidence.

On 2026-08-11 two runs tripped `assert_adapters_effective`. The guard ran before
`trials.jsonl` was written, so an hour of generation and scoring was discarded and the only
surviving evidence was a traceback in the job log — which is why the root cause could not be
determined afterwards. The guard must still fail the run (the cells are untrustworthy), but
the rows have to outlive it.
"""
from __future__ import annotations

import inspect

import pytest

from obtune.cft import evaluate


def _rows(identical: bool):
    """Minimal row set: one base + one tuned system over 3 keys."""
    out = []
    for i in range(3):
        out.append({"direction": "forward", "strategy": "simple", "program_id": f"p{i}",
                    "condition": "L1r", "system": "base", "output_raw": f"out{i}"})
        out.append({"direction": "forward", "strategy": "simple", "program_id": f"p{i}",
                    "condition": "L1r", "system": "cft",
                    "output_raw": f"out{i}" if identical else f"different{i}"})
    return out


def test_guard_still_raises_when_every_output_matches_base() -> None:
    with pytest.raises(RuntimeError, match="did not take effect"):
        evaluate.assert_adapters_effective(_rows(identical=True))


def test_guard_passes_when_outputs_differ() -> None:
    rep = evaluate.assert_adapters_effective(_rows(identical=False))
    assert rep["cft"]["identical_to_base"] == 0
    assert rep["cft"]["n_compared"] == 3


def test_report_helper_never_raises_and_matches_the_guard() -> None:
    """It is written beside trials.jsonl when the guard trips, so it must survive the very
    input that makes the guard raise."""
    rep = evaluate._adapter_effectiveness_report(_rows(identical=True))
    assert rep["cft"] == {"n_compared": 3, "identical_to_base": 3, "identical_rate": 1.0}


def test_rows_are_written_before_the_guard_runs() -> None:
    """Order is the whole point. Pinned against the source because the failure mode is an
    ORDERING bug: both calls exist either way, and any behavioural test would need a GPU."""
    src = inspect.getsource(evaluate.main)
    write_at = src.index('write_jsonl(out_dir / "trials.jsonl"')
    guard_at = src.index("assert_adapters_effective(rows)")
    assert write_at < guard_at, (
        "assert_adapters_effective runs before trials.jsonl is written — a tripped guard "
        "would again discard the whole run and leave the failure undiagnosable")


def test_main_module_hard_exits_rather_than_joining_children() -> None:
    """vLLM's EngineCore child can wedge `multiprocessing.util._exit_function` in join().
    That cost 18 idle GPU-hours. The entry point must print and leave, not hang."""
    src = evaluate.__loader__.get_source("obtune.cft.evaluate")
    tail = src[src.index('if __name__ == "__main__":'):]
    # Strip comments: the rationale above the block MENTIONS os._exit, and matching that
    # instead of the call made this test pass on prose rather than on behaviour.
    code = "\n".join(l for l in tail.splitlines() if not l.lstrip().startswith("#"))
    assert "os._exit" in code, "entry point can still hang in multiprocessing atexit"
    assert "traceback.print_exc" in code, "hard exit must not swallow the traceback"
    assert code.index("traceback.print_exc") < code.index("os._exit"), (
        "traceback must be printed BEFORE the hard exit or the failure is invisible")


def test_every_row_keeps_its_own_generation() -> None:
    """The leaked-loop-variable bug that failed six runs.

    `score_trials` builds `prepared` in a pre-pass (so CodeBLEU can be batched), then walks
    it in a second loop. `"output_raw": raw` sat in that second loop while `raw` was NOT in
    the unpacked tuple — so it resolved to the enclosing scope, holding the LAST generation
    of the pre-pass. Every row stored the same string, and `assert_adapters_effective`
    compared a constant against itself and reported EVERY system as identical to base.

    The adapters were never at fault. This asserts the tuple still carries `raw`, checked
    against the source because a behavioural test would need a GPU.
    """
    import inspect

    src = inspect.getsource(evaluate.score_trials)
    assert "prepared.append((req, raw, pred" in src, (
        "`raw` is no longer carried in the prepared tuple — output_raw will silently "
        "collapse to the last generation again")
    assert "for i, ((req, raw, pred" in src, (
        "the consuming loop does not unpack `raw`; it will fall back to the enclosing "
        "scope and store one constant for every row")
