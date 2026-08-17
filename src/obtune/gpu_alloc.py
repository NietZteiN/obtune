"""Which GPUs are ours, which are someone else's, and which are free to take.

`gpu.py` answers "is this card idle?". That is not enough on a shared box once we hold
cards ourselves: a worker parked on a GPU that a neighbour has taken looks identical,
from `nvidia-smi` alone, to a worker doing useful work. The supervisor needs to tell
three states apart —

    ours      an obtune process is on it (leave it alone; it is working)
    theirs    a process that is not ours is on it (never touch, never queue onto it)
    free      nothing meaningful on it (available)

— so it can hold obtune to a fixed budget of cards while following whatever is free,
rather than being pinned to indices that a neighbour may claim at any time.

"Ours" is decided by reading the owning process's command line, not by bookkeeping we
keep ourselves: bookkeeping goes stale exactly when it matters, which is after a crash.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

#: Substrings that mark a process as this project's.
#:
#: `VLLM::` matters: vLLM calls setproctitle on its engine-core and worker processes, so
#: the process holding the GPU memory during an eval has a command line of
#: `VLLM::EngineCore_DP0` with no trace of obtune or of the conda prefix. Matching on
#: cmdline alone therefore classified our OWN evaluation as a neighbour's job — and the
#: supervisor, seeing "gpu0 taken by another user", SIGTERMed the worker that was running
#: it. That is what killed the RQ2 javascript evals on 2026-08-09 and stranded a claim.
OURS_MARKERS = ("obtune", "/conda_envs/obtune/")

#: Renamed processes that are ours only if they also run under OUR uid. A neighbour's
#: vLLM is titled identically, so the marker alone would claim their card as ours —
#: exactly the mistake this module exists to prevent, in the opposite direction.
UID_SCOPED_MARKERS = ("VLLM::",)

#: A card with less than this in use counts as carrying no real workload.
IDLE_MEM_MB = 1500


@dataclass
class GpuState:
    index: int
    mem_used_mb: int
    util_pct: int
    owner: str  # "ours" | "theirs" | "free"
    pids: tuple[int, ...] = ()

    @property
    def available(self) -> bool:
        return self.owner == "free"


def _cmdline(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().replace(b"\x00", b" ").decode("utf-8", "replace")
    except OSError:
        return ""


def _ppid(pid: int) -> int | None:
    """Parent of `pid`, read from /proc/<pid>/stat.

    Field 4 is ppid, but field 2 (comm) is parenthesised and may itself contain spaces or
    parentheses, so split after the LAST ')' rather than on whitespace from the left.
    """
    try:
        with open(f"/proc/{pid}/stat", "r") as f:
            data = f.read()
        return int(data[data.rindex(")") + 1:].split()[1])
    except (OSError, ValueError):
        return None


def _exe(pid: int) -> str:
    """The process's real executable, independent of what argv says.

    argv[0] is whatever the caller typed: a process launched as bare ``python -m pytest``
    has the cmdline ``python -m pytest ...`` and carries no trace of the environment it
    is running in. /proc/<pid>/exe resolves to the actual binary — for anything in this
    project, ``/data/jvl210002/conda_envs/obtune/bin/python3.12`` — so it matches
    OURS_MARKERS whatever the invocation looked like. This is the load-bearing check;
    the cmdline scan is now a supplement, not the basis.
    """
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return ""


def _same_uid(pid: int) -> bool:
    try:
        return os.stat(f"/proc/{pid}").st_uid == os.getuid()
    except OSError:
        return False


def _is_ours(pid: int, max_depth: int = 12) -> bool:
    """Is this GPU process ours, directly or by descent?

    Renamed children (vLLM engine cores, dataloader forks) carry no marker of their own,
    but they are always descendants of a process that does. Walking the parent chain
    catches them without having to enumerate every library that renames itself. Bounded
    depth so a /proc race cannot spin.
    """
    seen: set[int] = set()
    cur: int | None = pid
    for _ in range(max_depth):
        if cur is None or cur <= 1 or cur in seen:
            break
        seen.add(cur)
        cmd = _cmdline(cur) + " " + _exe(cur)
        if any(m in cmd for m in OURS_MARKERS):
            return True
        if any(m in cmd for m in UID_SCOPED_MARKERS) and _same_uid(cur):
            return True
        cur = _ppid(cur)
    return False


def _compute_apps() -> dict[int, list[int]]:
    """physical GPU index -> pids with memory on it."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"],
            text=True, timeout=30,
        )
        uuids = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader"],
            text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return {}
    by_uuid = {}
    for line in uuids.strip().splitlines():
        idx, uuid = (p.strip() for p in line.split(",", 1))
        by_uuid[uuid] = int(idx)
    res: dict[int, list[int]] = {}
    for line in out.strip().splitlines():
        if not line.strip():
            continue
        uuid, pid = (p.strip() for p in line.split(",", 1))
        idx = by_uuid.get(uuid)
        if idx is not None:
            res.setdefault(idx, []).append(int(pid))
    return res


def survey() -> list[GpuState]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"], text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    apps = _compute_apps()
    states: list[GpuState] = []
    for line in out.strip().splitlines():
        idx, mem, util = (int(p.strip()) for p in line.split(","))
        pids = tuple(apps.get(idx, ()))
        if pids:
            owner = "ours" if any(_is_ours(p) for p in pids) else "theirs"
        else:
            # No compute app, but memory can linger briefly after a process exits.
            owner = "free" if mem < IDLE_MEM_MB else "theirs"
        states.append(GpuState(idx, mem, util, owner, pids))
    return states


def allowed_gpus() -> Optional[set[int]]:
    """Indices obtune may place work on, or None when the config says nothing.

    Lending a card by stopping its worker does not hold on its own: the supervisor
    follows whatever is FREE within its budget, so the next poll sees an idle GPU and
    claims it straight back. `scheduler_policy.allowed_gpus` in configs/compute.yaml is
    what makes a loan stick.

    Read on every call rather than cached: the supervisor is a long-lived process, and
    taking a card back (or lending another) must not require restarting it.
    """
    try:
        from obtune.config import load_config

        raw = load_config("compute.yaml").get("scheduler_policy", {}).get("allowed_gpus")
    except Exception:  # noqa: BLE001 — a missing/broken config must not strand the queue
        return None
    if raw is None:
        return None
    return {int(i) for i in raw}


def ours(states: Optional[list[GpuState]] = None) -> list[int]:
    # NOT filtered by the allowlist: a card we are on is ours whether or not policy says
    # we should have taken it, and both the budget arithmetic and stranded-engine reaping
    # depend on seeing it.
    return [g.index for g in (states or survey()) if g.owner == "ours"]


def free(states: Optional[list[GpuState]] = None) -> list[int]:
    """Free cards we are ALLOWED to take. A lent card is never 'free' to us."""
    ok = allowed_gpus()
    return [
        g.index
        for g in (states or survey())
        if g.available and (ok is None or g.index in ok)
    ]


def claim(budget: int, states: Optional[list[GpuState]] = None) -> list[int]:
    """Free GPUs to start on, so that our total holdings stay within `budget`.

    Returns [] when we are already at budget — the caller should then do nothing
    rather than wait on a specific index, because the card it wants may be taken for
    hours and another may come free in the meantime.
    """
    st = states or survey()
    held = len(ours(st))
    slots = max(0, budget - held)
    return free(st)[:slots]


if __name__ == "__main__":
    _ok = allowed_gpus()
    for g in survey():
        lent = "  LENT (not in scheduler_policy.allowed_gpus)" if _ok is not None and g.index not in _ok else ""
        print(f"gpu{g.index}: {g.mem_used_mb:>6} MB {g.util_pct:>3}%  {g.owner}"
              f"{'  pids=' + ','.join(map(str, g.pids)) if g.pids else ''}{lent}")


def stranded_engines(require_no_claim: bool = True) -> list[dict]:
    """Our GPU-holding processes that have been ORPHANED by a dead parent.

    THE DEADLOCK THIS EXISTS TO BREAK, which actually happened on 2026-08-11.
    When an eval process dies, vLLM's `VLLM::EngineCore` child is reparented to init and
    keeps its ~41 GB KV-cache reservation forever. The worker refuses any GPU with >2 GB
    used — correctly, since it cannot tell a live neighbour from a corpse — so all four
    GPUs sat at 0% utilisation holding 164 GB while seven jobs waited in the queue. Nothing
    in the system recovers from that on its own: `--sweep-orphans` returns stranded manifest
    CLAIMS to the queue, but the claim was already returned; it is the GPU that is stuck.

    Three conditions must ALL hold before a pid is reported, and they are re-checked at kill
    time rather than trusted from this scan:

      * `uid == ours` — never touch another user's job on a shared box. NOTE: this is a
        weaker test than it looks. On 2026-08-12 GPUs 2-3 were running `malware_reads` and an
        `sglang::scheduler` under the SAME Unix account, and `_same_uid` returned True for
        both. Uid is not an ownership test here; the ppid and marker checks below are what
        actually protect other people's work. Never relax them.;
      * `ppid == 1` — orphaned. A live parent means a running job, however idle it looks;
      * the process matches a UID_SCOPED_MARKER (`VLLM::`) — an engine, not a shell.

    `require_no_claim` adds the decisive fourth: skip any GPU that still has a claim in
    `runs/manifest/running/`. A worker that legitimately owns a GPU may have just spawned
    an engine whose parent link is momentarily odd, and reaping that would kill live work.
    """
    from obtune.config import RUNS_DIR

    claimed: set[str] = set()
    if require_no_claim:
        running = RUNS_DIR / "manifest" / "running"
        if running.is_dir():
            claimed = {d.name for d in running.iterdir()
                       if d.is_dir() and any(d.glob("*.json"))}

    out: list[dict] = []
    for gpu_index, pids in _compute_apps().items():
        if require_no_claim and f"gpu{gpu_index}" in claimed:
            continue
        for pid in pids:
            if not _same_uid(pid):
                continue
            if _ppid(pid) != 1:
                continue
            try:
                comm = (Path(f"/proc/{pid}") / "comm").read_text().strip()
            except OSError:
                continue
            if not any(m.rstrip(":") in comm for m in UID_SCOPED_MARKERS):
                continue
            out.append({"pid": pid, "gpu": gpu_index, "comm": comm})
    return out


def reap_stranded_engines(dry_run: bool = False) -> list[dict]:
    """Terminate what `stranded_engines` reports, re-verifying each pid at kill time."""
    import os
    import signal

    reaped: list[dict] = []
    for rec in stranded_engines():
        pid = rec["pid"]
        # Re-verify: the scan and the kill are separate moments, and a pid can be reused.
        if not _same_uid(pid) or _ppid(pid) != 1:
            continue
        if dry_run:
            reaped.append(rec)
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            reaped.append(rec)
        except OSError:
            pass
    return reaped
