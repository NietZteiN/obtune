#!/usr/bin/env python3
"""Run N project commands in parallel inside ONE SLURM allocation, one per GPU.

WHY. Concurrency here is capped by jobs, not GPUs: the h200 partition's QoS (`juno`)
allows 4 jobs per user, `high-throughput` raises that to 8 -- but each h200 node has TWO
GPUs and a one-adapter-per-job pipeline uses one of them. Packing two trainings into a
`--gres=gpu:2` allocation doubles throughput per job slot, on top of whatever the QOS
allows, without asking the cluster for anything extra.

DEVICE ASSIGNMENT. Each child gets `CUDA_VISIBLE_DEVICES=<i>` over the allocation's
devices. This is safe precisely BECAUSE obtune.gpu.pin() is a no-op under SLURM: it
returns whatever the scheduler set rather than rewriting it, so a child that sees exactly
one device pins that device. Setting an absolute physical index would be the destructive
version (CLAUDE.md §1); this sets a per-child view of an allocation SLURM already made.

EXIT CODE is the first non-zero child's, so a packed job fails if ANY member fails and
`afterok` dependents stay unsatisfied rather than running on a missing adapter.

    python scripts/slurm/pack.py --cmd "-m obtune.train_sft --config a.yaml --model m" \
                                --cmd "-m obtune.train_sft --config b.yaml --model m"
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cmd", action="append", required=True,
                    help="one project python command (repeatable); argv after `python`")
    a = ap.parse_args()

    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    devices = [d for d in visible.split(",") if d != ""]
    if len(devices) < len(a.cmd):
        print(f"[pack] allocation has {len(devices)} device(s) "
              f"({visible!r}) but {len(a.cmd)} commands were packed — refusing to "
              f"oversubscribe: two trainings on one GPU is slower than running them "
              f"in series and can OOM.", file=sys.stderr)
        return 2

    procs = []
    for i, cmd in enumerate(a.cmd):
        env = dict(os.environ)
        # Index INTO the allocation, not a physical device id.
        env["CUDA_VISIBLE_DEVICES"] = devices[i]
        argv = [sys.executable] + shlex.split(cmd)
        print(f"[pack] device {devices[i]}: {' '.join(argv[1:])}", flush=True)
        procs.append((cmd, subprocess.Popen(argv, env=env)))

    rc = 0
    for cmd, p in procs:
        r = p.wait()
        print(f"[pack] rc={r}  {cmd}", flush=True)
        if r != 0 and rc == 0:
            rc = r
    print(f"[pack] done, exit={rc}", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
