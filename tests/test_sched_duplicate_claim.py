"""One job must never be claimed by two workers at once.

`os.rename` makes claiming atomic against a competing claim of the SAME queued file, but it
cannot see a job that is already RUNNING and got requeued underneath it. That is not
hypothetical: on 2026-08-13, restarting `pipeline.sh` mid-flight left the original
`eval_vllm` alive (killing the pipeline does not kill a worker's subprocess), the claim was
swept back to `queued/`, and a second worker took it on another GPU. Two processes then wrote
the SAME cell directories under `resume: true`. It was caught by eye, not by the scheduler.
"""
from __future__ import annotations

import json
import os

import pytest

from obtune.sched import worker


@pytest.fixture()
def queue(tmp_path, monkeypatch):
    q, r = tmp_path / "queued", tmp_path / "running"
    q.mkdir()
    (r / "gpu0").mkdir(parents=True)
    (r / "gpu1").mkdir(parents=True)
    monkeypatch.setattr(worker, "QUEUED", q)
    monkeypatch.setattr(worker, "RUNNING", r)
    monkeypatch.setattr(worker, "DONE", tmp_path / "done")
    (tmp_path / "done").mkdir()
    return q, r


def _job(path, job_id="j1", pid=None):
    payload = {"job_id": job_id, "kind": "eval-cell", "argv": ["-c", "pass"], "priority": 1}
    if pid is not None:
        payload["_owner"] = {"pid": pid, "tag": "gpu0", "boot_id": worker._boot_id()}
    path.write_text(json.dumps(payload))
    return path


def test_a_job_already_running_elsewhere_is_not_claimed_again(queue) -> None:
    q, r = queue
    # Same filename live under gpu0, owned by THIS process (definitely alive)...
    _job(r / "gpu0" / "job.json", pid=os.getpid())
    # ...and requeued underneath it, exactly as --sweep-orphans would leave it.
    _job(q / "job.json")

    assert worker._claim("gpu1") is None, "a second worker claimed a job already running"
    assert (q / "job.json").exists(), "the queued copy must be left alone, not consumed"


def test_a_normal_queued_job_is_still_claimed(queue) -> None:
    """The guard must not break the ordinary path."""
    q, r = queue
    _job(q / "job.json")
    claimed = worker._claim("gpu1")
    assert claimed is not None and claimed.parent.name == "gpu1"


def test_a_dead_owner_does_not_block_reclaiming(queue) -> None:
    """A crashed job's claim must not make the work unrunnable forever — that is
    --sweep-orphans' territory, and treating it as live would strand the queue."""
    q, r = queue
    _job(r / "gpu0" / "job.json", pid=2**30)      # pid that cannot exist
    _job(q / "job.json")
    assert worker._claim("gpu1") is not None


def test_the_same_tag_does_not_block_itself(queue) -> None:
    q, r = queue
    _job(r / "gpu1" / "job.json", pid=os.getpid())
    _job(q / "job.json")
    # gpu1 re-claiming its own tag is the resume path, not a duplicate.
    assert worker._claim("gpu1") is not None


def test_a_different_job_is_unaffected(queue) -> None:
    q, r = queue
    _job(r / "gpu0" / "other.json", pid=os.getpid())
    _job(q / "job.json")
    assert worker._claim("gpu1") is not None


def test_claim_drops_a_duplicate_whose_original_already_completed(tmp_path, monkeypatch):
    """A re-queued job whose job_id is in done/ must be dropped, not re-run.

    `_already_running` only sees a duplicate that is still IN FLIGHT. Restarting
    pipeline.sh mid-stage re-queues jobs a worker is holding; once such a job finishes its
    claim leaves running/ and the stale duplicate becomes claimable again. For a train job
    that is ~4.3 GPU-h of retraining plus an overwrite of a finished adapter directory.
    """
    import json

    from obtune.sched import worker as W

    root = tmp_path / "manifest"
    for sub in ("queued", "running", "done", "failed"):
        (root / sub).mkdir(parents=True)
    monkeypatch.setattr(W, "MANIFEST_DIR", root)
    monkeypatch.setattr(W, "QUEUED", root / "queued")
    monkeypatch.setattr(W, "RUNNING", root / "running")
    monkeypatch.setattr(W, "DONE", root / "done")

    job = {"job_id": "train__fold_a", "kind": "train", "argv": ["-m", "x"],
           "raw": False, "est_gpu_h": 1.0, "priority": 10}
    (root / "queued" / "010_train__fold_a.json").write_text(json.dumps(job))
    # the original completed earlier
    (root / "done" / "010_train__fold_a.json").write_text(json.dumps(job))

    assert W._claim("gpu0") is None, "a completed job must not be claimed again"
    assert not (root / "queued" / "010_train__fold_a.json").exists(), \
        "the stale duplicate should be dropped from the queue, not left to be re-examined"


def test_claim_still_takes_a_job_that_only_FAILED(tmp_path, monkeypatch):
    """Failure is not completion — a failed job stays claimable."""
    import json

    from obtune.sched import worker as W

    root = tmp_path / "manifest"
    for sub in ("queued", "running", "done", "failed"):
        (root / sub).mkdir(parents=True)
    monkeypatch.setattr(W, "MANIFEST_DIR", root)
    monkeypatch.setattr(W, "QUEUED", root / "queued")
    monkeypatch.setattr(W, "RUNNING", root / "running")
    monkeypatch.setattr(W, "DONE", root / "done")

    job = {"job_id": "train__fold_b", "kind": "train", "argv": ["-m", "x"],
           "raw": False, "est_gpu_h": 1.0, "priority": 10}
    (root / "queued" / "010_train__fold_b.json").write_text(json.dumps(job))
    (root / "failed" / "010_train__fold_b.json").write_text(json.dumps(job))

    claimed = W._claim("gpu0")
    assert claimed is not None and claimed.name == "010_train__fold_b.json"
