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
import signal
import socket
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


def _done_job_ids() -> set[str]:
    """job_ids already completed successfully."""
    if not DONE.exists():
        return set()
    out: set[str] = set()
    for p in DONE.glob("*.json"):
        try:
            out.add(json.loads(p.read_text())["job_id"])
        except Exception:  # noqa: BLE001 — a malformed record must not wedge the queue
            continue
    return out


def dependencies_met(job: Job, done: set[str]) -> bool:
    """Whether every `meta.depends_on` job has finished.

    Priorities order the queue but do not sequence it: with several workers running
    concurrently, two jobs at the SAME priority start together, so `router_train` (p45)
    began before `router_features` (p45) had written its .npz and died on a missing file.
    Eight jobs failed that way — none of them a code fault, all of them a job that simply
    ran too early. `depends_on` was already recorded in job meta by build_manifest and
    read by nothing; this is what makes it load-bearing.

    A job whose dependency has not finished is left in the queue rather than failed, so
    it is retried on the next poll once its input exists.
    """
    meta = job.meta or {}
    dep = meta.get("depends_on")
    if not dep:
        return True
    deps = [dep] if isinstance(dep, str) else list(dep)
    return all(d in done for d in deps)


def _already_running(name: str, skip_tag: str) -> bool:
    """Is a claim with this filename live under some OTHER tag, owned by a live process?

    A claim whose owner is dead does not count: that is `--sweep-orphans`' job, and treating
    it as live here would make a crashed job unrunnable forever.
    """
    if not RUNNING.exists():
        return False
    for d in RUNNING.iterdir():
        if not d.is_dir() or d.name == skip_tag:
            continue
        p = d / name
        if not p.exists():
            continue
        try:
            if not is_orphaned(p):
                return True
        except Exception:  # noqa: BLE001 — an unreadable claim is treated as live (safe side)
            return True
    return False


def _claim(tag: str) -> Path | None:
    """Atomically move the highest-priority READY queued job into running/<tag>/."""
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

    done = _done_job_ids()
    dest_dir = RUNNING / tag
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(candidates, key=sort_key):
        try:
            job = Job.load(path)
        except Exception:  # noqa: BLE001
            job = None
        if job is not None and not dependencies_met(job, done):
            continue  # not ready yet — leave it queued for a later poll
        if job is not None and job.job_id in done:
            # ALREADY COMPLETED. `_already_running` covers a duplicate that is in flight; it
            # cannot see one whose original has since FINISHED, and the two arise from the
            # same event. Restarting pipeline.sh mid-stage re-queues every job of the running
            # stage, including the ones a worker currently holds; when such a job completes,
            # its claim leaves running/ and the stale duplicate becomes claimable again.
            #
            # For an eval that is a wasteful no-op (the cell parquet is resumed). For a TRAIN
            # job it is neither cheap nor safe: `train_sft` has no skip-if-finished check, so
            # it would retrain the adapter from scratch — ~4.3 GPU-h per LOTO fold — and
            # overwrite a completed adapter directory that ckpt-select may be reading.
            #
            # Dropped rather than left in place, so the queue does not accumulate corpses
            # that every future poll re-examines. A genuinely failed job is in failed/, not
            # done/, so it stays claimable.
            path.unlink(missing_ok=True)
            print(f"[{tag}] dropping already-completed duplicate {job.job_id}", flush=True)
            continue
        if _already_running(path.name, tag):
            # The SAME job is already claimed under another tag. `os.rename` below is atomic
            # against a competing claim of the same QUEUED file, but it cannot see a job that
            # is running and got REQUEUED underneath it — which is exactly what happens when
            # pipeline.sh is restarted mid-flight: killing the pipeline does not kill a
            # worker's eval subprocess, so the original keeps running while the claim is
            # swept back to queued/ and a second worker picks it up. On 2026-08-13 that put
            # two `eval_vllm` processes on two GPUs writing the SAME cell directories under
            # `resume: true`. Caught by hand before a parquet was corrupted; nothing in the
            # scheduler would have noticed.
            continue
        dest = dest_dir / path.name
        try:
            os.rename(path, dest)  # atomic within the filesystem; loser gets FileNotFoundError
        except (FileNotFoundError, OSError):
            continue  # another worker won the race
        _stamp_owner(dest, tag)
        return dest
    return None


def _boot_id() -> str:
    """Identifies this boot of this machine.

    A pid alone is not a durable identity: pid numbers restart from scratch after a reboot,
    so a claim stamped before a crash can match an unrelated live process afterwards and
    look permanently alive — the exact stall the stamp exists to prevent, reintroduced by
    the one event most likely to strand a claim. Comparing boot ids makes any claim from a
    previous boot unambiguously an orphan.
    """
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return ""


def _progress_path(claim: Path) -> Path:
    """Sidecar holding a claim's CPU-progress baseline.

    Deliberately NOT stored inside the claim file. Doing so meant rewriting the claim on
    every poll, and the worker can move that same file to `done/` at any instant — so a
    write landing microseconds later would RECREATE it under `running/`, producing a claim
    whose job had already finished and which nothing would ever clear. `drain` counts
    `running/`, so one such zombie blocks the pipeline permanently.

    A sidecar cannot resurrect anything: the worst case is a stale file, which the sweep
    below deletes.
    """
    # RUNNING is <root>/manifest/running, so its parent is the manifest dir. Deriving this
    # from `claim` produced <root>/manifest/manifest/.progress — a doubled segment that put
    # every sidecar somewhere the sweep would never look.
    return RUNNING.parent / ".progress" / f"{claim.parent.name}__{claim.name}"


def _read_progress(claim: Path) -> dict:
    try:
        return json.loads(_progress_path(claim).read_text())
    except Exception:  # noqa: BLE001
        return {}


def _write_progress(claim: Path, payload: dict) -> None:
    try:
        p = _progress_path(claim)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload))
    except Exception:  # noqa: BLE001
        pass


def _sweep_progress_sidecars() -> None:
    """Drop sidecars whose claim is no longer in running/."""
    d = RUNNING.parent / ".progress"
    if not d.is_dir():
        return
    live = {f"{t.name}__{c.name}" for t in RUNNING.glob("*") if t.is_dir()
            for c in t.glob("*.json")}
    for f in d.glob("*.json"):
        if f.name not in live:
            f.unlink(missing_ok=True)


def _children(pid: int) -> list[int]:
    try:
        out = subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True).stdout
        return [int(x) for x in out.split()]
    except Exception:  # noqa: BLE001
        return []


def _kill_tree(pid: int, term_grace_s: float = 10.0) -> None:
    """SIGTERM the process and its children, then SIGKILL whatever survives.

    Two lessons from 2026-08-12, both learned by having to finish the job by hand.

    SIGTERM IS NOT ENOUGH. A process wedged in `multiprocessing.util._exit_function` is
    already inside interpreter shutdown; the signal is accepted and then never acted on.
    `kill_stalled` sent TERM, reported success, and both processes were still alive two
    hours later.

    THE CHILDREN MATTER MORE THAN THE PARENT. vLLM's `EngineCore` child holds the ~41 GB
    KV-cache reservation. Killing only the parent leaves the child alive with a live parent,
    which is exactly the state `reap_stranded_engines` refuses to touch (it requires
    ppid == 1) — so the GPU stayed occupied until a human intervened. Killing the tree
    releases the memory in the same pass.
    """
    kids = _children(pid)
    for target in [pid, *kids]:
        try:
            os.kill(target, signal.SIGTERM)
        except OSError:
            pass
    deadline = time.time() + term_grace_s
    while time.time() < deadline:
        if not any(_alive(t) for t in [pid, *kids]):
            return
        time.sleep(0.5)
    for target in [pid, *kids]:
        if _alive(target):
            try:
                os.kill(target, signal.SIGKILL)
            except OSError:
                pass


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _own_ticks(pid: int) -> Optional[int]:
    """utime+stime for `pid` alone, or None if it is gone. Field order per proc(5)."""
    try:
        parts = (Path(f"/proc/{pid}") / "stat").read_text().rsplit(")", 1)[1].split()
        return int(parts[11]) + int(parts[12])  # utime, stime (0-indexed after state)
    except Exception:  # noqa: BLE001
        return None


def _descendants(pid: int, depth: int = 4) -> list[int]:
    """pid's children, grandchildren, ... — bounded so a cycle cannot spin."""
    out: list[int] = []
    frontier = [pid]
    for _ in range(depth):
        nxt: list[int] = []
        for p in frontier:
            for c in _children(p):
                if c not in out and c != pid:
                    out.append(c)
                    nxt.append(c)
        if not nxt:
            break
        frontier = nxt
    return out


def _cpu_ticks(pid: int) -> Optional[int]:
    """CPU consumed by the claim's whole process TREE.

    THE FALSE POSITIVE THIS PREVENTS. `_owner.pid` is the WORKER's pid, and the worker
    spends the entire job blocked in `subprocess.run()` waiting on the eval child — it
    burns essentially no CPU of its own. Measuring only the worker therefore reports every
    healthy long job as frozen, and `kill_stalled` would execute a 30-minute timeout on all
    work regardless of state. The two jobs it killed on 2026-08-12 happened to be genuinely
    wedged, so the bug looked like correct behaviour; the next victim would have been a job
    generating at 99% GPU.

    Summing the tree makes the signal mean what the docstring always claimed: the CLAIM is
    making progress, wherever inside it the work happens to be running.
    """
    own = _own_ticks(pid)
    if own is None:
        return None
    total = own
    for child in _descendants(pid):
        t = _own_ticks(child)
        if t is not None:
            total += t
    return total


def kill_stalled(min_idle_s: int = 1800, grace_s: int = 900) -> int:
    """Kill claims whose owning process has stopped consuming CPU, and fail them.

    THE NIGHT THIS COST US. On 2026-08-11 two eval jobs raised a legitimate guard error
    (`assert_adapters_effective`), and then hung in `multiprocessing.util._exit_function`
    joining a vLLM `EngineCore` child that never terminates. The exception was written to
    the job log, but the process never exited, so the worker never recorded the failure and
    the claim stayed in `running/` — for **18 hours**, with both GPUs idle, five jobs queued
    behind them, and the pipeline's `drain` loop waiting on a queue that could never empty.

    Nothing existing catches this. `is_orphaned` asks whether the owning process is DEAD;
    here it is very much alive, just permanently asleep. `reap_stranded_engines` needs the
    parent gone first. The distinguishing signal is CPU time: a working job accumulates it
    (generation, execution, CodeBLEU all burn CPU), a wedged one does not move at all.

    State is kept in the claim file (`_progress`), so a restarted supervisor does not lose
    its baseline and cannot mistake "I just started watching" for "it has not moved".

    Deliberately conservative, because a false positive kills real work:
      * `grace_s` before a job is watched at all — model load is genuinely quiet;
      * `min_idle_s` (default 30 min) of ZERO tick movement before acting;
      * the job is moved to `failed/`, never silently requeued — a stall is a defect to
        look at, and re-running it blindly would just stall again.
    """
    n = 0
    _sweep_progress_sidecars()
    for tag_dir in sorted(RUNNING.glob("*")):
        if not tag_dir.is_dir():
            continue
        for path in sorted(tag_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text())
            except Exception:  # noqa: BLE001
                continue
            owner = payload.get("_owner") or {}
            pid = owner.get("pid")
            if not isinstance(pid, int) or owner.get("boot_id") != _boot_id():
                continue
            ticks = _cpu_ticks(pid)
            if ticks is None:
                continue  # dead -> is_orphaned()/--sweep-orphans handles it
            now = time.time()
            prog = _read_progress(path)
            started = prog.get("first_seen", now)
            if now - started < grace_s:
                _write_progress(path, {"ticks": ticks, "since": now, "first_seen": started})
                continue
            if prog.get("ticks") != ticks:
                _write_progress(path, {"ticks": ticks, "since": now, "first_seen": started})
                continue
            if now - float(prog.get("since", now)) < min_idle_s:
                continue

            idle_min = (now - float(prog["since"])) / 60.0
            print(f"stalled: {path.name} pid={pid} has burned no CPU for {idle_min:.0f} min "
                  f"— killing and failing it")
            _kill_tree(pid)
            payload["_stalled"] = {"pid": pid, "idle_minutes": round(idle_min, 1),
                                   "detected_utc": _now()}
            payload.pop("_owner", None)
            payload.pop("_progress", None)
            _progress_path(path).unlink(missing_ok=True)
            FAILED.mkdir(parents=True, exist_ok=True)
            _write_json(FAILED / path.name, payload)
            path.unlink(missing_ok=True)
            n += 1
    return n


def _write_json(path: Path, payload: dict) -> None:
    try:
        path.write_text(json.dumps(payload, indent=2))
    except Exception:  # noqa: BLE001
        pass


def _stamp_owner(path: Path, tag: str) -> None:
    """Record which process owns this claim.

    Without this a claim in running/ is indistinguishable from an abandoned one, and an
    abandoned claim is unrecoverable: the pipeline's sweeper only requeued when NO worker
    held the tag, so a worker that died mid-job and was replaced by a fresh worker on the
    same tag stranded its claim forever — and `queue_busy` counts running/, so the drain
    that waits on it never returns. Observed on 2026-08-09 with an RQ2 eval on gpu0.

    mtime cannot substitute: os.rename preserves the file's timestamps, so a claim's mtime
    is when build_manifest wrote it, not when a worker took it.
    """
    try:
        payload = json.loads(path.read_text())
        payload["_owner"] = {"pid": os.getpid(), "tag": tag, "host": socket.gethostname(),
                             "boot_id": _boot_id(), "claimed_utc": _now()}
        path.write_text(json.dumps(payload, indent=2))
    except Exception:  # noqa: BLE001 — a stamp failure must never lose the claim
        pass


def _finish(path: Path, ok: bool, detail: dict[str, Any]) -> None:
    target_dir = DONE if ok else FAILED
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(path.read_text())
    payload.pop("_owner", None)  # a finished job has no owner; keep done/ records clean
    payload["result"] = detail
    (target_dir / path.name).write_text(json.dumps(payload, indent=2))
    path.unlink(missing_ok=True)


def _terminate_group(proc: "subprocess.Popen[Any]", grace_s: float = 30.0) -> None:
    """Stop a job and everything it spawned.

    The job is started with `start_new_session=True`, so it leads its own process group
    and one `killpg` reaches its whole tree — the vLLM engine child, the CodeBLEU pool,
    the sandboxed exec runners. Signalling the job's pid alone does not: on 2026-08-11
    that left 128 pool workers and 4 engines reparented to init, holding 164 GB across
    four GPUs, and they had to be reaped by hand.

    SIGTERM first so vLLM can release its KV cache, then SIGKILL what is left. The grace
    window is generous because a clean engine shutdown is worth waiting for — but it is
    bounded, because a shutdown that hangs is exactly what this exists to survive.
    """
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            return
        try:
            proc.wait(timeout=grace_s if sig is signal.SIGTERM else 10)
            return
        except subprocess.TimeoutExpired:
            continue


def run_job(job: Job, tag: str) -> tuple[bool, dict[str, Any]]:
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{job.job_id}.log"
    started = time.time()
    argv = list(job.argv) if job.raw else [sys.executable, *job.argv]
    env = dict(os.environ)
    env.setdefault("PYTHONPATH", str(PROJECT_ROOT / "src"))

    # APPEND, not truncate. The log is keyed on job_id, so opening "w" made every retry
    # destroy the failed attempt's log — which is precisely the log you need. On
    # 2026-08-11 a cell ran 3.3 h, was killed, and its only surviving trace was the
    # 20-line tail in the manifest, all of it progress-bar output.
    with open(log_path, "a") as log:
        log.write(f"\n# ===== attempt: {job.job_id} on {tag} at {_now()}\n# argv: {argv}\n\n")
        log.flush()
        proc = None
        try:
            # Own process group, so _terminate_group can reach the whole job tree.
            proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                                    cwd=PROJECT_ROOT, env=env, start_new_session=True)
            code = proc.wait()
        except BaseException:  # includes the SIGTERM-driven SystemExit below
            # A worker that is going away must not leave its job running: the claim would
            # be requeued as an orphan (is_orphaned tests the WORKER's pid) and a second
            # copy of a still-running job would be launched onto another card.
            if proc is not None and proc.poll() is None:
                log.write(f"\n# worker stopping — terminating job at {_now()}\n")
                log.flush()
                _terminate_group(proc)
            if not isinstance(sys.exc_info()[1], Exception):
                raise  # SystemExit/KeyboardInterrupt: finish tearing down, then leave
            log.write("\n" + traceback.format_exc())
            code = -1

    detail = {"returncode": code, "seconds": round(time.time() - started, 1),
              "log": str(log_path.relative_to(PROJECT_ROOT)), "worker": tag, "finished_utc": _now()}
    if code != 0:
        detail["tail"] = "".join(log_path.read_text().splitlines(keepends=True)[-20:])
    return code == 0, detail


def _install_termination_handler() -> None:
    """Turn SIGTERM/SIGINT into SystemExit so `run_job`'s teardown runs.

    Default SIGTERM disposition kills the worker outright, which strands both halves of
    a running job — the process tree keeps the GPU, and the claim in running/<tag>/ is
    then requeued as an orphan because `is_orphaned` tests the worker's pid, not the
    job's. `supervise.sh` walks exactly that path when a neighbour takes a card: kill the
    worker, sleep 2, requeue. Raising SystemExit instead lets us stop the job first.
    """
    def _handler(signum: int, frame: Any) -> None:
        raise SystemExit(f"worker received signal {signum}")

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handler)
        except ValueError:  # not the main thread
            pass


def loop(tag: str, poll_seconds: int, max_mem_used_mb: int, max_util_pct: int,
         once: bool = False) -> int:
    _install_termination_handler()
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
        try:
            ok, detail = run_job(job, tag)
        except SystemExit:
            # Retired mid-job. run_job has already stopped the job tree, so the work is
            # genuinely not running and the claim can go straight back to the queue.
            # Leaving it for the orphan sweep would be wrong twice over: the sweep tests
            # the WORKER's pid, so it would requeue this claim even if the job were still
            # alive, and until it ran, `queue_busy` would count a claim nobody holds.
            QUEUED.mkdir(parents=True, exist_ok=True)
            shutil.move(str(claimed), str(QUEUED / claimed.name))
            print(f"[{tag}] retired mid-job — stopped and requeued {job.job_id}", flush=True)
            raise
        _finish(claimed, ok, detail)
        completed += 1
        print(f"[{tag}] {'done' if ok else 'FAILED'} {job.job_id} in {detail['seconds']}s", flush=True)
        if once:
            return completed


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    return True


def _tag_has_live_worker(tag: str) -> bool:
    """Fallback for claims taken before _stamp_owner existed."""
    try:
        out = subprocess.run(["pgrep", "-f", f"obtune.sched.worker --gpu-tag {tag}$"],
                             capture_output=True, text=True, timeout=10)
    except Exception:  # noqa: BLE001
        return True  # cannot tell -> assume live, never requeue a job that is running
    return bool(out.stdout.strip())


def is_orphaned(path: Path) -> bool:
    """Is this claim held by a process that no longer exists?

    Stamped claims answer exactly (the owning pid is dead). Unstamped ones — written by a
    worker from before the stamp existed — fall back to "no live worker holds this tag",
    which is the old, weaker test. Both default to NOT orphaned on any uncertainty: a
    false positive here would launch a second copy of a running job onto the same GPU.
    """
    try:
        payload = json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        return False
    owner = payload.get("_owner")
    if isinstance(owner, dict) and isinstance(owner.get("pid"), int):
        if owner.get("host") not in (None, socket.gethostname()):
            return False  # another host's claim; not ours to judge
        boot = owner.get("boot_id")
        if boot and _boot_id() and boot != _boot_id():
            return True  # stamped before a reboot; its pid means nothing now
        return not _pid_alive(owner["pid"])
    return not _tag_has_live_worker(path.parent.name)


def requeue_stale(tag: str | None = None, only_orphans: bool = False) -> int:
    """Move jobs stranded in running/ back to queued/ (after a killed worker).

    `only_orphans` is the safe form, and the one the pipeline uses on every poll: it
    requeues a claim only once its owner is provably gone. The unconditional form is a
    manual recovery tool — running it while workers are live would double-launch jobs.
    """
    moved = 0
    roots = [RUNNING / tag] if tag else (list(RUNNING.iterdir()) if RUNNING.exists() else [])
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.json")):
            if only_orphans and not is_orphaned(path):
                continue
            shutil.move(str(path), str(QUEUED / path.name))
            print(f"requeued orphan {path.name} (was claimed by {root.name})", flush=True)
            moved += 1
    return moved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gpu-tag", help="worker name, e.g. gpu2 (required to run jobs)")
    ap.add_argument("--once", action="store_true", help="run at most one job then exit")
    ap.add_argument("--requeue-stale", action="store_true",
                    help="return EVERY job in running/ to the queue, then exit (manual recovery; "
                         "do not run while workers are live)")
    ap.add_argument("--sweep-orphans", action="store_true",
                    help="requeue only claims whose owning process is gone; safe with live workers")
    ap.add_argument("--kill-stalled", action="store_true",
                    help="fail claims whose process has burned no CPU for 30 min; catches a job "
                         "that hung after raising (e.g. vLLM shutdown deadlock) and would "
                         "otherwise block the queue indefinitely")
    ap.add_argument("--reap-stranded-gpus", action="store_true",
                    help="terminate OUR orphaned vLLM engines holding GPU memory on unclaimed "
                         "GPUs; safe with live workers. --sweep-orphans frees stuck CLAIMS, "
                         "this frees stuck GPUs — a dead job strands both, and only the first "
                         "was previously recoverable")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --reap-stranded-gpus: report what would be terminated")
    args = ap.parse_args()

    for d in (QUEUED, RUNNING, DONE, FAILED, LOGS):
        d.mkdir(parents=True, exist_ok=True)

    if args.kill_stalled:
        print(f"failed {kill_stalled()} stalled claim(s)")
        return 0

    if args.reap_stranded_gpus:
        from obtune import gpu_alloc

        reaped = gpu_alloc.reap_stranded_engines(dry_run=args.dry_run)
        verb = "would reap" if args.dry_run else "reaped"
        print(f"{verb} {len(reaped)} stranded engine(s)"
              + ("".join(f"\n  gpu{r['gpu']} pid={r['pid']} {r['comm']}" for r in reaped)))
        return 0

    if args.sweep_orphans:
        print(f"requeued {requeue_stale(only_orphans=True)} orphaned claim(s)")
        return 0

    if args.requeue_stale:
        # Scoped to --gpu-tag when given. Unscoped it requeues EVERY claim, including
        # those of workers that are alive and mid-job, which would double-launch them
        # onto occupied GPUs — so the supervisor always passes a tag.
        print(f"requeued {requeue_stale(tag=args.gpu_tag)} stale job(s)"
              f"{f' on {args.gpu_tag}' if args.gpu_tag else ' (ALL tags)'}")
        return 0

    if not args.gpu_tag:
        ap.error("--gpu-tag is required unless --sweep-orphans/--requeue-stale/"
                 "--reap-stranded-gpus/--kill-stalled is given")

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
