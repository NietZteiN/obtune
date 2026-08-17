"""A job that hangs after raising must not block the queue forever.

On 2026-08-11 two eval jobs raised `assert_adapters_effective` and then hung in
`multiprocessing.util._exit_function`, joining a vLLM `EngineCore` child that never
terminates. The traceback reached the job log; the process never exited; the worker never
recorded the failure. Both claims sat in `running/` for **18 hours** with the GPUs idle and
five jobs queued behind them, and the pipeline's `drain` loop waited on a queue that could
not empty.

Neither existing mechanism catches this: `is_orphaned` asks whether the owner is DEAD (it is
alive, just asleep), and `reap_stranded_engines` requires the parent to be gone first. CPU
time is the discriminator — a working job accumulates it, a wedged one does not.
"""
from __future__ import annotations

import json

import pytest

from obtune.sched import worker


@pytest.fixture()
def claim(tmp_path, monkeypatch):
    """A claim in running/gpu0/, owned by a live pid on this boot."""
    running = tmp_path / "running"
    failed = tmp_path / "failed"
    (running / "gpu0").mkdir(parents=True)
    failed.mkdir()
    monkeypatch.setattr(worker, "RUNNING", running)
    monkeypatch.setattr(worker, "FAILED", failed)

    path = running / "gpu0" / "job.json"

    def write(progress=None, pid=4242):
        payload = {"job_id": "job", "_owner": {"pid": pid, "tag": "gpu0",
                                               "boot_id": worker._boot_id()}}
        path.write_text(json.dumps(payload))
        # Progress lives in a SIDECAR, never in the claim: writing it back into the claim
        # could recreate a file the worker had already moved to done/.
        if progress is not None:
            worker._write_progress(path, progress)
        return path

    return write, path, failed


def test_stalled_claim_is_failed_and_process_killed(claim, monkeypatch) -> None:
    write, path, failed = claim
    killed: list[int] = []
    monkeypatch.setattr(worker, "_cpu_ticks", lambda pid: 1000)          # never moves
    # Patch the KILLER, not os.kill. `_kill_tree` polls until a wall-clock deadline, and
    # this test freezes time.time() — patching os.kill instead spins that loop forever.
    monkeypatch.setattr(worker, "_kill_tree", lambda pid, **kw: killed.append(pid))
    monkeypatch.setattr(worker.time, "time", lambda: 10_000.0)
    # Seen long ago, ticks unchanged since long ago.
    write({"ticks": 1000, "since": 0.0, "first_seen": 0.0})

    assert worker.kill_stalled(min_idle_s=1800, grace_s=900) == 1
    assert killed == [4242]
    assert not path.exists(), "claim must leave running/ or the queue stays blocked"
    moved = json.loads((failed / "job.json").read_text())
    assert moved["_stalled"]["pid"] == 4242
    assert "_owner" not in moved


def test_a_working_job_is_never_killed(claim, monkeypatch) -> None:
    """The false positive that matters: killing a job that is doing real work."""
    write, path, failed = claim
    killed: list[int] = []
    monkeypatch.setattr(worker.os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr(worker.time, "time", lambda: 10_000.0)
    monkeypatch.setattr(worker, "_cpu_ticks", lambda pid: 2000)          # advanced
    write({"ticks": 1000, "since": 0.0, "first_seen": 0.0})

    assert worker.kill_stalled(min_idle_s=1800, grace_s=900) == 0
    assert killed == []
    assert path.exists()
    # ...and the new baseline is recorded in the sidecar, so the next pass compares to 2000.
    assert worker._read_progress(path)["ticks"] == 2000


def test_grace_period_protects_model_load(claim, monkeypatch) -> None:
    """Loading a 7B model is genuinely quiet; a young claim is never judged."""
    write, path, _ = claim
    killed: list[int] = []
    monkeypatch.setattr(worker.os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr(worker, "_cpu_ticks", lambda pid: 1000)
    monkeypatch.setattr(worker.time, "time", lambda: 1000.0)
    write({"ticks": 1000, "since": 0.0, "first_seen": 900.0})            # 100 s old

    assert worker.kill_stalled(min_idle_s=1800, grace_s=900) == 0
    assert killed == []


def test_idle_but_not_yet_long_enough_is_left_alone(claim, monkeypatch) -> None:
    write, path, _ = claim
    killed: list[int] = []
    monkeypatch.setattr(worker.os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr(worker, "_cpu_ticks", lambda pid: 1000)
    monkeypatch.setattr(worker.time, "time", lambda: 10_000.0)
    write({"ticks": 1000, "since": 9_000.0, "first_seen": 0.0})          # idle 1000 s < 1800
    assert worker.kill_stalled(min_idle_s=1800, grace_s=900) == 0
    assert killed == []


def test_dead_owner_is_left_to_the_orphan_sweep(claim, monkeypatch) -> None:
    """Two mechanisms, two signals: dead -> requeue (recoverable); wedged -> fail."""
    write, path, _ = claim
    monkeypatch.setattr(worker, "_cpu_ticks", lambda pid: None)          # process gone
    monkeypatch.setattr(worker.time, "time", lambda: 10_000.0)
    write({"ticks": 1000, "since": 0.0, "first_seen": 0.0})
    assert worker.kill_stalled() == 0
    assert path.exists(), "a dead owner is --sweep-orphans' job, not this one"


def test_cpu_ticks_parses_a_command_with_spaces_and_parens() -> None:
    """/proc/<pid>/stat's comm field can contain spaces and ')' — split on the LAST ')'."""
    import os

    assert worker._cpu_ticks(os.getpid()) is not None
    assert worker._cpu_ticks(2**30) is None


# --------------------------------------------------------------------------- #
# killing must actually work — SIGTERM alone did not, on 2026-08-12


def test_kill_tree_escalates_to_sigkill_when_term_is_ignored(monkeypatch) -> None:
    """A process wedged in interpreter shutdown ACCEPTS SIGTERM and never acts on it.
    `kill_stalled` reported success and both processes were alive two hours later."""
    sent: list[tuple[int, int]] = []
    monkeypatch.setattr(worker, "_children", lambda pid: [])
    monkeypatch.setattr(worker.os, "kill",
                        lambda pid, sig: sent.append((pid, sig)) if sig else None)
    monkeypatch.setattr(worker, "_alive", lambda pid: True)          # never dies on TERM
    monkeypatch.setattr(worker.time, "sleep", lambda s: None)
    t = [0.0]
    monkeypatch.setattr(worker.time, "time", lambda: t.__setitem__(0, t[0] + 5) or t[0])

    worker._kill_tree(4242, term_grace_s=10.0)
    sigs = [s for _, s in sent]
    import signal as _sig
    assert _sig.SIGTERM in sigs, "never tried the polite signal"
    assert _sig.SIGKILL in sigs, "never escalated — this is the bug that needed a human"
    assert sigs.index(_sig.SIGTERM) < sigs.index(_sig.SIGKILL)


def test_kill_tree_kills_the_children_that_hold_the_gpu(monkeypatch) -> None:
    """vLLM's EngineCore child holds the ~41 GB reservation. Killing only the parent leaves
    it alive with a LIVE parent — precisely the state reap_stranded_engines refuses to touch
    (it needs ppid == 1), so the GPU stayed occupied until a human intervened."""
    sent: list[int] = []
    monkeypatch.setattr(worker, "_children", lambda pid: [9001, 9002])
    monkeypatch.setattr(worker.os, "kill", lambda pid, sig: sent.append(pid))
    monkeypatch.setattr(worker, "_alive", lambda pid: False)          # dies on TERM
    worker._kill_tree(4242)
    assert 9001 in sent and 9002 in sent, "engine children were not signalled"
    assert 4242 in sent


def test_kill_tree_stops_early_when_term_succeeds(monkeypatch) -> None:
    """Do not SIGKILL a process that already exited cleanly."""
    sent: list[tuple[int, int]] = []
    monkeypatch.setattr(worker, "_children", lambda pid: [])
    monkeypatch.setattr(worker.os, "kill", lambda pid, sig: sent.append((pid, sig)))
    monkeypatch.setattr(worker, "_alive", lambda pid: False)
    worker._kill_tree(4242)
    import signal as _sig
    assert _sig.SIGKILL not in [s for _, s in sent]


def test_cpu_ticks_counts_the_whole_tree_not_just_the_worker() -> None:
    """`_owner.pid` is the WORKER, which blocks in subprocess.run() and burns no CPU of its
    own for the entire job. Measuring only that process reports every healthy long-running
    job as frozen — a blanket 30-minute timeout on all work. The two jobs killed on
    2026-08-12 were genuinely wedged, so the bug looked like correct behaviour; the next
    victim would have been a job generating at 99% GPU.
    """
    import os
    import subprocess
    import time

    child = subprocess.Popen(["python", "-c", "x=0\nwhile True: x+=1"])
    try:
        time.sleep(2.5)
        own = worker._own_ticks(os.getpid())
        tree = worker._cpu_ticks(os.getpid())
        assert own is not None and tree is not None
        assert tree > own, (
            f"tree total {tree} does not exceed the idle parent's {own} — a busy child is "
            f"not being counted, so healthy jobs will be stall-killed")
    finally:
        child.kill()
        child.wait()


def test_descendants_is_bounded_and_excludes_self() -> None:
    import os

    kids = worker._descendants(os.getpid())
    assert os.getpid() not in kids
    assert isinstance(kids, list)


def test_progress_never_resurrects_a_finished_claim(claim, monkeypatch, tmp_path) -> None:
    """The TOCTOU that made a sidecar necessary.

    Progress used to be written back into the claim file on every poll. The worker can move
    that same file to `done/` at any instant, so a write landing microseconds later would
    RECREATE it under `running/` — a claim whose job had already finished and which nothing
    clears. `drain` counts `running/`, so one zombie blocks the pipeline permanently.
    """
    write, path, _ = claim
    monkeypatch.setattr(worker, "RUNNING", path.parent.parent)
    write({"ticks": 1, "since": 0.0, "first_seen": 0.0})

    path.unlink()                      # the worker finished and moved the claim away
    worker._write_progress(path, {"ticks": 2, "since": 1.0, "first_seen": 0.0})
    assert not path.exists(), "writing progress recreated a claim the worker had moved"


def test_stale_sidecars_are_swept(claim, monkeypatch) -> None:
    write, path, _ = claim
    monkeypatch.setattr(worker, "RUNNING", path.parent.parent)
    write({"ticks": 1, "since": 0.0, "first_seen": 0.0})
    side = worker._progress_path(path)
    assert side.exists()
    path.unlink()                      # claim gone; sidecar is now orphaned
    worker._sweep_progress_sidecars()
    assert not side.exists(), "orphaned sidecar was not swept"
