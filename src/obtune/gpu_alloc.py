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

import subprocess
from dataclasses import dataclass
from typing import Optional

#: Substrings that mark a process as this project's.
OURS_MARKERS = ("obtune", "/conda_envs/obtune/")

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
            owner = "ours" if any(
                any(m in _cmdline(p) for m in OURS_MARKERS) for p in pids
            ) else "theirs"
        else:
            # No compute app, but memory can linger briefly after a process exits.
            owner = "free" if mem < IDLE_MEM_MB else "theirs"
        states.append(GpuState(idx, mem, util, owner, pids))
    return states


def ours(states: Optional[list[GpuState]] = None) -> list[int]:
    return [g.index for g in (states or survey()) if g.owner == "ours"]


def free(states: Optional[list[GpuState]] = None) -> list[int]:
    return [g.index for g in (states or survey()) if g.available]


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
    for g in survey():
        print(f"gpu{g.index}: {g.mem_used_mb:>6} MB {g.util_pct:>3}%  {g.owner}"
              f"{'  pids=' + ','.join(map(str, g.pids)) if g.pids else ''}")
