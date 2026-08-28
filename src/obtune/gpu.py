"""GPU selection. Two regimes, one call site (CLAUDE.md §1).

**Under SLURM (juno, since 2026-08-28):** the scheduler has already allocated the
devices and set CUDA_VISIBLE_DEVICES, and cgroups enforce it. There is nothing to
pick and nothing to verify — another job *cannot* be on our card. `pick_free_gpus`
returns local indices and `pin` deliberately does NOT touch CUDA_VISIBLE_DEVICES:
on a 2-GPU node given `--gres=gpu:1`, SLURM may hand us physical device 1 as local
index 0, so overwriting the variable with an absolute index selects the wrong
device or no device at all. This is the failure mode worth remembering, because it
does not error — it runs, on someone else's GPU or on none.

**Scheduler-free host (csr-94608, until 2026-08-27):** no allocator existed, so
pick an *idle* GPU from `nvidia-smi` and pin CUDA_VISIBLE_DEVICES **before** torch
is imported. Retained because it is still correct on any unscheduled box.

This module is deliberately torch-free so it can run first.

Typical use at the top of an entrypoint, before any `import torch`:

    from obtune import gpu
    gpu.pin(gpu.pick_free_gpus(1))   # correct under both regimes
    import torch                      # now sees only the allocated device(s)
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


@dataclass
class GpuStat:
    index: int
    mem_used_mb: int
    util_pct: int

    def is_idle(self, max_mem_used_mb: int, max_util_pct: int) -> bool:
        return self.mem_used_mb <= max_mem_used_mb and self.util_pct <= max_util_pct


def query() -> list[GpuStat]:
    """Parse `nvidia-smi` for per-GPU memory + utilization. Empty list if unavailable."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    stats = []
    for line in out.strip().splitlines():
        idx, mem, util = (p.strip() for p in line.split(","))
        stats.append(GpuStat(int(idx), int(mem), int(util)))
    return stats


def under_slurm() -> bool:
    """True inside a SLURM allocation, where device selection is not ours to make."""
    return bool(os.environ.get("SLURM_JOB_ID"))


def visible_device_count() -> int:
    """GPUs this process may use, without importing torch or shelling out if avoidable.

    CUDA_VISIBLE_DEVICES is authoritative when set (SLURM sets it); an empty string
    means zero devices, which is different from unset and must not be read as "all".
    """
    cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
    if cvd is not None:
        return len([p for p in cvd.split(",") if p.strip()])
    on_node = os.environ.get("SLURM_GPUS_ON_NODE", "")
    if on_node.isdigit():
        return int(on_node)
    return len(query())


def pick_free_gpus(
    n: int = 1,
    max_mem_used_mb: int = 1000,
    max_util_pct: int = 5,
) -> list[int]:
    """Return indices of up to `n` idle GPUs (most-free first).

    Raises RuntimeError if fewer than `n` are idle — deliberately: on a shared box you
    wait rather than stomp on someone else's job (CLAUDE.md §1).
    """
    if under_slurm():
        # No idle check: SLURM's cgroup already guarantees exclusivity, and the old
        # check would in any case be measuring the wrong thing here — it looked at
        # *physical* cards on a box we shared informally with a borrower.
        have = visible_device_count()
        if have < n:
            raise RuntimeError(
                f"Need {n} GPU(s); this SLURM allocation has {have}. "
                f"Ask for them with --gres=gpu:{n} (job {os.environ.get('SLURM_JOB_ID')})."
            )
        return list(range(n))

    stats = query()
    if not stats:
        raise RuntimeError("nvidia-smi unavailable — cannot verify a GPU is idle; refusing to guess.")
    idle = [s for s in stats if s.is_idle(max_mem_used_mb, max_util_pct)]
    idle.sort(key=lambda s: (s.mem_used_mb, s.util_pct))
    if len(idle) < n:
        busy = ", ".join(f"gpu{s.index}({s.mem_used_mb}MB,{s.util_pct}%)" for s in stats)
        raise RuntimeError(f"Need {n} idle GPU(s), found {len(idle)}. Current: {busy}. Wait — no scheduler here.")
    return [s.index for s in idle[:n]]


def pin(indices: list[int]) -> str:
    """Set CUDA_VISIBLE_DEVICES. Call BEFORE importing torch. Returns the value in force.

    Under SLURM this is a no-op that returns what the scheduler set. See the module
    docstring: rewriting the variable inside an allocation is silently destructive.
    """
    if under_slurm():
        return os.environ.get("CUDA_VISIBLE_DEVICES", "")
    value = ",".join(str(i) for i in indices)
    os.environ["CUDA_VISIBLE_DEVICES"] = value
    return value


if __name__ == "__main__":
    # `python -m obtune.gpu` — quick status print.
    for s in query():
        flag = "IDLE" if s.is_idle(1000, 5) else "busy"
        print(f"gpu{s.index}: {s.mem_used_mb:>6} MB used, {s.util_pct:>3}% util  [{flag}]")
