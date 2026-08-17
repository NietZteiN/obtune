"""A claim must be distinguishable from an abandoned one, and ownership from a neighbour's.

Both properties failed simultaneously on 2026-08-09 and cost an RQ2 evaluation plus a
would-be-indefinite pipeline stall:

  * `gpu_alloc.survey` decided ownership from the command line alone. vLLM renames its
    engine-core process (`setproctitle` -> ``VLLM::EngineCore_DP0``), so the process
    holding the GPU during one of OUR evaluations carried no obtune marker and the card
    read as ``theirs``. The supervisor duly SIGTERMed the worker running it.
  * that worker's claim stayed in ``running/gpu0/``. The sweeper requeued only when NO
    worker held the tag, and a replacement worker had been started on gpu0 — so the claim
    was stranded, and ``drain`` (which waits on ``running/`` being empty) would have
    waited forever.

The tests below pin the repaired behaviour in both directions: an orphan must be
reclaimed, and a live claim must never be.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from obtune import gpu_alloc
from obtune.sched import worker


# --------------------------------------------------------------------------- #
# ownership


def test_ppid_matches_the_kernel() -> None:
    assert gpu_alloc._ppid(os.getpid()) == os.getppid()


def test_ppid_survives_a_comm_containing_spaces_and_parens(tmp_path: Path) -> None:
    """/proc/<pid>/stat field 2 is the executable name in parentheses and is NOT escaped.

    Splitting from the left puts ppid at a different index for a process named
    ``sh (2) x``. Parsing must key off the LAST ')'.
    """
    fake = "1234 (weird ) (name) S 4321 1234 1234 0 -1 4194304 0 0 0 0 0 0 0 0 20 0 1"
    data = fake
    assert int(data[data.rindex(")") + 1:].split()[1]) == 4321


def test_our_own_process_is_ours() -> None:
    assert gpu_alloc._is_ours(os.getpid())


def test_init_is_not_ours() -> None:
    assert not gpu_alloc._is_ours(1)


def test_a_renamed_child_is_ours_by_descent() -> None:
    """The vLLM case: the GPU-holding process carries no marker, its ancestor does.

    A plain `sleep` started from this (obtune) test process stands in for the renamed
    engine core — its own cmdline has no obtune marker at all.
    """
    proc = subprocess.Popen(["sleep", "30"])
    try:
        assert not any(m in gpu_alloc._cmdline(proc.pid) for m in gpu_alloc.OURS_MARKERS), \
            "the stand-in must not match on its own cmdline, or the test proves nothing"
        assert gpu_alloc._is_ours(proc.pid), "ancestry walk failed to find the obtune parent"
    finally:
        proc.kill()
        proc.wait()


def test_vllm_marker_is_scoped_to_our_uid() -> None:
    """A neighbour's vLLM is titled identically; claiming their card would be worse."""
    assert "VLLM::" in gpu_alloc.UID_SCOPED_MARKERS
    assert "VLLM::" not in gpu_alloc.OURS_MARKERS
    assert not gpu_alloc._same_uid(1)  # init is root, we are not


def test_is_ours_terminates_on_a_cycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """A /proc race must not spin forever."""
    monkeypatch.setattr(gpu_alloc, "_ppid", lambda pid: pid)
    monkeypatch.setattr(gpu_alloc, "_cmdline", lambda pid: "")
    assert gpu_alloc._is_ours(999_999) is False


# --------------------------------------------------------------------------- #
# claims


def _write_claim(d: Path, name: str, owner: dict | None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    payload = {"job_id": name, "kind": "train", "argv": ["-m", "obtune.train_sft"]}
    if owner is not None:
        payload["_owner"] = owner
    p = d / f"{name}.json"
    p.write_text(json.dumps(payload, indent=2))
    return p


@pytest.fixture()
def manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for attr, sub in (("QUEUED", "queued"), ("RUNNING", "running"),
                      ("DONE", "done"), ("FAILED", "failed")):
        d = tmp_path / sub
        d.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(worker, attr, d)
    return tmp_path


def test_claim_owned_by_a_dead_pid_is_orphaned(manifest: Path) -> None:
    dead = subprocess.Popen(["true"])
    dead.wait()
    p = _write_claim(manifest / "running" / "gpu0", "j", {
        "pid": dead.pid, "tag": "gpu0", "host": os.uname().nodename, "claimed_utc": "x"})
    assert worker.is_orphaned(p)


def test_claim_owned_by_a_live_pid_is_not_orphaned(manifest: Path) -> None:
    p = _write_claim(manifest / "running" / "gpu0", "j", {
        "pid": os.getpid(), "tag": "gpu0", "host": os.uname().nodename, "claimed_utc": "x"})
    assert not worker.is_orphaned(p)


def test_claim_from_a_previous_boot_is_orphaned(manifest: Path) -> None:
    """Pid numbers restart at reboot, so a live pid proves nothing about a pre-reboot claim.

    Without the boot_id comparison this claim looks alive forever (its pid is this very
    process), `running/` never empties, and `drain` waits indefinitely — a reboot being
    precisely the event most likely to leave claims behind.
    """
    p = _write_claim(manifest / "running" / "gpu0", "j", {
        "pid": os.getpid(), "tag": "gpu0", "host": os.uname().nodename,
        "boot_id": "0000-a-different-boot-0000", "claimed_utc": "x"})
    assert worker.is_orphaned(p)


def test_claim_from_this_boot_with_a_live_pid_is_kept(manifest: Path) -> None:
    p = _write_claim(manifest / "running" / "gpu0", "j", {
        "pid": os.getpid(), "tag": "gpu0", "host": os.uname().nodename,
        "boot_id": worker._boot_id(), "claimed_utc": "x"})
    assert not worker.is_orphaned(p)


def test_claim_from_another_host_is_left_alone(manifest: Path) -> None:
    """Its pid means nothing here; requeuing would double-launch it there."""
    p = _write_claim(manifest / "running" / "gpu0", "j", {
        "pid": os.getpid(), "tag": "gpu0", "host": "some-other-box", "claimed_utc": "x"})
    assert not worker.is_orphaned(p)


def test_unreadable_claim_is_not_orphaned(manifest: Path) -> None:
    d = manifest / "running" / "gpu0"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "broken.json"
    p.write_text("{not json")
    assert not worker.is_orphaned(p)


def test_sweep_requeues_only_the_orphan(manifest: Path) -> None:
    """The property the pipeline depends on: a live worker's job is never taken back."""
    dead = subprocess.Popen(["true"])
    dead.wait()
    host = os.uname().nodename
    _write_claim(manifest / "running" / "gpu0", "orphan",
                 {"pid": dead.pid, "tag": "gpu0", "host": host, "claimed_utc": "x"})
    _write_claim(manifest / "running" / "gpu1", "live",
                 {"pid": os.getpid(), "tag": "gpu1", "host": host, "claimed_utc": "x"})

    assert worker.requeue_stale(only_orphans=True) == 1
    assert (manifest / "queued" / "orphan.json").exists()
    assert (manifest / "running" / "gpu1" / "live.json").exists()
    assert not (manifest / "running" / "gpu0" / "orphan.json").exists()


def test_unconditional_requeue_is_scoped_by_tag(manifest: Path) -> None:
    """The supervisor retires one worker; it must not requeue the other three's jobs."""
    host = os.uname().nodename
    for tag in ("gpu0", "gpu1"):
        _write_claim(manifest / "running" / tag, f"job_{tag}",
                     {"pid": os.getpid(), "tag": tag, "host": host, "claimed_utc": "x"})

    assert worker.requeue_stale(tag="gpu0") == 1
    assert (manifest / "queued" / "job_gpu0.json").exists()
    assert (manifest / "running" / "gpu1" / "job_gpu1.json").exists()


def test_stamp_records_the_owning_process(manifest: Path) -> None:
    p = _write_claim(manifest / "running" / "gpu0", "j", None)
    worker._stamp_owner(p, "gpu0")
    owner = json.loads(p.read_text())["_owner"]
    assert owner["pid"] == os.getpid()
    assert owner["tag"] == "gpu0"
    assert owner["host"] == os.uname().nodename
    assert owner["boot_id"] == worker._boot_id()
    assert not worker.is_orphaned(p)


def test_finish_strips_the_owner_stamp(manifest: Path) -> None:
    p = _write_claim(manifest / "running" / "gpu0", "j", None)
    worker._stamp_owner(p, "gpu0")
    worker._finish(p, True, {"returncode": 0})
    payload = json.loads((manifest / "done" / "j.json").read_text())
    assert "_owner" not in payload
    assert payload["result"]["returncode"] == 0


def test_claim_is_stamped_end_to_end(manifest: Path) -> None:
    """_claim must stamp, or every claim it takes is indistinguishable from an orphan."""
    worker.Job(job_id="j", kind="train", argv=["-m", "obtune.train_sft"]).dump(
        manifest / "queued" / "001_j.json")
    claimed = worker._claim("gpu0")
    assert claimed is not None
    assert json.loads(claimed.read_text())["_owner"]["pid"] == os.getpid()
    assert not worker.is_orphaned(claimed)
