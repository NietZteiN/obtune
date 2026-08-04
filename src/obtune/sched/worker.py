"""One-GPU worker for the file-queue scheduler (CLAUDE.md §1).

There is no scheduler on this host and the box is shared, so the discipline is:
claim a job only when the GPU is genuinely idle, pin ``CUDA_VISIBLE_DEVICES``
before any torch import, and make every job idempotent so a killed worker costs
one job rather than a run.

The queue is the filesystem — ``runs/manifest/{queued,running,done,failed}/`` — with
claiming done by ``os.rename``, which is atomic within a directory. That is all the
coordination several workers on one host need, and it survives a worker being killed
(its job is visible in ``running/<tag>/`` and can be requeued by moving the file back).

Launch one per idle GPU via scripts/launch_workers.sh, which sets
``CUDA_VISIBLE_DEVICES`` at tmux-spawn time — this module never imports torch itself,
so the pin is always in place before the job subprocess starts.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from obtune import gpu
from obtune.config import PROJECT_ROOT, RUNS_DIR, load_config

MANIFEST_DIR = RUNS_DIR / "manifest"
QUEUED = MANIFEST_DIR / "queued"
RUNNING = MANIFEST_DIR / "running"
DONE = MANIFEST_DIR / "done"
FAILED = MANIFEST_DIR / "failed"
LOGS = RUNS_DIR / "logs"


@dataclass
class Job:
    job_id: str
    kind: str  # train | ckpt-select | eval-cell | router | merge | forgetting | attn
    #: Arguments for the project interpreter — ``["-m", "obtune.train_sft", ...]`` or
    #: ``["scripts/05_build_variants.py", ...]``. Set ``raw=True`` to exec argv as a
    #: command instead (a shell script). Being explicit rather than inferring from a
    #: ``.py`` suffix matters: a mis-inferred ``-m`` job fails to spawn and is recorded
    #: as a job failure, which reads like the job itself broke.
    argv: list[str]
    raw: bool = False
    est_gpu_h: float = 1.0
    priority: int = 100  # lower runs first
    meta: dict[str, Any] | None = None

    @classmethod
    def load(cls, path: Path) -> "Job":
        d = json.loads(path.read_text())
        return cls(job_id=d["job_id"], kind=d["kind"], argv=list(d["argv"]),
                   raw=bool(d.get("raw", False)), est_gpu_h=float(d.get("est_gpu_h", 1.0)),
                   priority=int(d.get("priority", 100)), meta=d.get("meta"))

    def dump(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "job_id": self.job_id, "kind": self.kind, "argv": self.argv, "raw": self.raw,
            "est_gpu_h": self.est_gpu_h, "priority": self.priority, "meta": self.meta or {},
        }, indent=2))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _physical_gpu_index() -> int | None:
    """The physical index this worker was pinned to, for the idle check.

    Inside the worker CUDA_VISIBLE_DEVICES has already remapped device numbering, so
    NVML/nvidia-smi must be queried with the ORIGINAL index or we would happily check
    a GPU we are not using.
    """
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if not visible:
        return None
    first = visible.split(",")[0].strip()
    return int(first) if first.isdigit() else None


def gpu_is_idle(index: int | None, max_mem_used_mb: int, max_util_pct: int,
                own_pids: set[int] | None = None) -> bool:
    """Whether the pinned GPU is free for us to take work on.

    A job we launched ourselves occupies the GPU legitimately, so this is only ever
    consulted between jobs, never to preempt our own work.
    """
    if index is None:
        return True  # unpinned (CPU-only smoke runs) — nothing to protect
    for stat in gpu.query():
        if stat.index == index:
            return stat.is_idle(max_mem_used_mb, max_util_pct)
    return False


def _claim(tag: str) -> Path | None:
    """Atomically move the highest-priority queued job into running/<tag>/."""
    if not QUEUED.exists():
        return None
    candidates = sorted(QUEUED.glob("*.json"))
    if not candidates:
        return None

    def sort_key(p: Path) -> tuple[int, str]:
        try:
            return (Job.load(p).priority, p.name)
        except Exception:  # noqa: BLE001 — a malformed file must not wedge the queue
            return (10_000, p.name)

    dest_dir = RUNNING / tag
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(candidates, key=sort_key):
        dest = dest_dir / path.name
        try:
            os.rename(path, dest)  # atomic within the filesystem; loser gets FileNotFoundError
            return dest
        except (FileNotFoundError, OSError):
            continue  # another worker won the race
    return None


def _finish(path: Path, ok: bool, detail: dict[str, Any]) -> None:
    target_dir = DONE if ok else FAILED
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(path.read_text())
    payload["result"] = detail
    (target_dir / path.name).write_text(json.dumps(payload, indent=2))
    path.unlink(missing_ok=True)


def run_job(job: Job, tag: str) -> tuple[bool, dict[str, Any]]:
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{job.job_id}.log"
    started = time.time()
    argv = list(job.argv) if job.raw else [sys.executable, *job.argv]
    env = dict(os.environ)
    env.setdefault("PYTHONPATH", str(PROJECT_ROOT / "src"))

    with open(log_path, "w") as log:
        log.write(f"# {job.job_id} on {tag} at {_now()}\n# argv: {argv}\n\n")
        log.flush()
        try:
            proc = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT,
                                  cwd=PROJECT_ROOT, env=env)
            code = proc.returncode
        except Exception:  # noqa: BLE001 — a spawn failure is a job failure, not a worker crash
            log.write("\n" + traceback.format_exc())
            code = -1

    detail = {"returncode": code, "seconds": round(time.time() - started, 1),
              "log": str(log_path.relative_to(PROJECT_ROOT)), "worker": tag, "finished_utc": _now()}
    if code != 0:
        detail["tail"] = "".join(log_path.read_text().splitlines(keepends=True)[-20:])
    return code == 0, detail


def loop(tag: str, poll_seconds: int, max_mem_used_mb: int, max_util_pct: int,
         once: bool = False) -> int:
    index = _physical_gpu_index()
    print(f"[{tag}] worker up; CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')} "
          f"(physical gpu {index}); polling every {poll_seconds}s", flush=True)
    completed = 0
    while True:
        if not gpu_is_idle(index, max_mem_used_mb, max_util_pct):
            print(f"[{tag}] gpu{index} busy (someone else's job) — waiting {poll_seconds}s", flush=True)
            if once:
                return completed
            time.sleep(poll_seconds)
            continue

        claimed = _claim(tag)
        if claimed is None:
            print(f"[{tag}] queue empty", flush=True)
            if once:
                return completed
            time.sleep(poll_seconds)
            continue

        job = Job.load(claimed)
        print(f"[{tag}] running {job.job_id} ({job.kind})", flush=True)
        ok, detail = run_job(job, tag)
        _finish(claimed, ok, detail)
        completed += 1
        print(f"[{tag}] {'done' if ok else 'FAILED'} {job.job_id} in {detail['seconds']}s", flush=True)
        if once:
            return completed


def requeue_stale(tag: str | None = None) -> int:
    """Move jobs stranded in running/ back to queued/ (after a killed worker)."""
    moved = 0
    roots = [RUNNING / tag] if tag else (list(RUNNING.iterdir()) if RUNNING.exists() else [])
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("*.json"):
            shutil.move(str(path), str(QUEUED / path.name))
            moved += 1
    return moved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gpu-tag", required=True, help="worker name, e.g. gpu2")
    ap.add_argument("--once", action="store_true", help="run at most one job then exit")
    ap.add_argument("--requeue-stale", action="store_true",
                    help="return jobs stranded in running/ to the queue, then exit")
    args = ap.parse_args()

    for d in (QUEUED, RUNNING, DONE, FAILED, LOGS):
        d.mkdir(parents=True, exist_ok=True)

    if args.requeue_stale:
        print(f"requeued {requeue_stale()} stale job(s)")
        return 0

    policy = load_config("compute.yaml")["scheduler_policy"]
    return 0 if loop(
        args.gpu_tag,
        poll_seconds=int(policy.get("poll_seconds", 600)),
        max_mem_used_mb=int(policy.get("max_mem_used_mb", 2000)),
        max_util_pct=int(policy.get("max_util_pct", 5)),
        once=args.once,
    ) >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
