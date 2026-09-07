#!/usr/bin/env python
"""Smoke-gate an objectives config before committing GPU-hours to it.

Runs `--dry-run` (batch shape, loss mask, teacher/parent correspondence) then `--max-steps 4`
(a real optimizer step, real memory) for one config, and prints per-GPU memory at the end.

Exists because CLAUDE.md §4 requires a smoke test before a long run and the scratchpad is NOT
visible from a compute node -- /tmp is node-local on juno, so a driver script has to live on
/work with the rest of the project (learned the hard way, job 381342).

    python scripts/smoke_objective.py --config train/obj_cons_codellama34b_py.yaml --lam 3
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--lam", default=None)
    ap.add_argument("--out", default=None, help="default: <adapter_root>/_smoke_<config stem>")
    ap.add_argument("--steps", default="4")
    args = ap.parse_args()

    out = args.out or f"runs/adapters_objectives/_smoke_{Path(args.config).stem}"
    base = [sys.executable, "-m", "obtune.objectives", "train", "--config", args.config, "--out", out]
    if args.lam is not None:
        base += ["--lam", str(args.lam)]

    rc_all = 0
    for label, extra in [("--dry-run", ["--dry-run"]), (f"--max-steps {args.steps}", ["--max-steps", args.steps])]:
        print(f"===== {args.config} {label} =====", flush=True)
        t0 = time.time()
        rc = subprocess.call(base + extra, cwd=str(ROOT))
        print(f"===== {args.config} {label}: rc={rc} in {time.time() - t0:.0f}s =====", flush=True)
        rc_all |= rc
        if rc:
            break

    subprocess.call(["nvidia-smi", "--query-gpu=index,memory.used,memory.total", "--format=csv,noheader"])
    print("SMOKE OK" if rc_all == 0 else "SMOKE FAILED", flush=True)
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
