"""A worker that is stopped must take its job with it.

Twice on 2026-08-11, signalling a process left its descendants running: 128 CodeBLEU pool
workers and 4 `VLLM::EngineCore` processes reparented to init, holding 164 GB across four
GPUs, reaped by hand. The scheduler consequence is worse than the wasted memory — a claim
in `running/<tag>/` is judged orphaned by the WORKER's pid (`is_orphaned`), so a worker
killed mid-job has its claim requeued while the job is still running, and a second copy of
it starts on another card. `supervise.sh` walks that exact path (kill worker, sleep 2,
requeue) whenever a neighbour takes a GPU.
"""
from __future__ import annotations

import os
import subprocess
import time

from obtune.sched import worker


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_terminate_group_kills_grandchildren() -> None:
    """The failure mode exactly: killing the job's pid alone leaves its children."""
    # `sh -c "sleep 300 & sleep 300"` gives us a child and a grandchild, the shape of an
    # eval process holding a vLLM engine and a process pool.
    proc = subprocess.Popen(["/bin/sh", "-c", "sleep 300 & sleep 300"],
                            start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pgid = os.getpgid(proc.pid)
    deadline = time.time() + 10
    kids: list[int] = []
    while time.time() < deadline:
        out = subprocess.run(["pgrep", "-g", str(pgid)], capture_output=True, text=True).stdout
        kids = [int(x) for x in out.split() if int(x) != proc.pid]
        if kids:
            break
        time.sleep(0.2)
    assert kids, "test setup: no descendants were spawned"

    worker._terminate_group(proc, grace_s=5.0)

    assert not _alive(proc.pid), "the job itself survived"
    time.sleep(1)
    survivors = [p for p in kids if _alive(p)]
    assert not survivors, f"descendants survived and would hold the GPU: {survivors}"


def test_termination_handler_raises_system_exit() -> None:
    """Default SIGTERM disposition kills the worker outright, skipping every teardown."""
    prev = worker.signal.getsignal(worker.signal.SIGTERM)
    try:
        worker._install_termination_handler()
        handler = worker.signal.getsignal(worker.signal.SIGTERM)
        assert callable(handler)
        try:
            handler(worker.signal.SIGTERM, None)
        except SystemExit as e:
            assert "15" in str(e)
        else:
            raise AssertionError("SIGTERM handler did not raise SystemExit")
    finally:
        worker.signal.signal(worker.signal.SIGTERM, prev)


def test_run_job_appends_so_a_retry_keeps_the_failed_log(tmp_path, monkeypatch) -> None:
    """Opening "w" made each retry destroy the evidence from the attempt that failed."""
    # PROJECT_ROOT too: run_job records the log path relative to it.
    monkeypatch.setattr(worker, "LOGS", tmp_path / "logs")
    monkeypatch.setattr(worker, "PROJECT_ROOT", tmp_path)
    job = worker.Job(job_id="probe", kind="eval-cell", raw=True,
                     argv=["/bin/sh", "-c", "echo attempt-marker"])

    ok, _ = worker.run_job(job, "smoketest")
    assert ok
    ok, _ = worker.run_job(job, "smoketest")
    assert ok

    text = (tmp_path / "logs" / "probe.log").read_text()
    # Count the job's OUTPUT lines, not every mention: the marker also appears in the
    # `# argv:` header this function writes for each attempt.
    produced = [ln for ln in text.splitlines() if ln.strip() == "attempt-marker"]
    assert len(produced) == 2, "the first attempt's output was truncated away"
    assert text.count("# ===== attempt:") == 2
