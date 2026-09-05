#!/usr/bin/env python
"""Smoke every objectives.py mode on one GPU before the full chains are submitted.

    python scripts/33_smoke_objectives.py [--steps 4] [--only cons neg curr_sft curr_kl resample]

Each arm runs as a subprocess (a fresh CUDA context per model load) into
$OBTUNE_SCRATCH/smoke_objectives/<arm>/, first as --dry-run (dataset + collator + the
answer-token correspondence assert) and then for --steps optimizer steps. Nothing here lands
under runs/adapters_objectives, so a passing smoke leaves no adapter to confuse ckpt-select.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = Path(os.environ.get("OBTUNE_SCRATCH", "/work/jvl210002/migration")) / "smoke_objectives"

ARMS = {
    "cons": ["-m", "obtune.objectives", "train", "--config", "train/obj_cons_codellama7b_py.yaml", "--lam", "1"],
    "cons_same": ["-m", "obtune.objectives", "train", "--config", "train/obj_cons_codellama7b_py.yaml", "--lam", "1", "--teacher-view", "same"],
    "neg": ["-m", "obtune.objectives", "train", "--config", "train/obj_neg_codellama7b_py.yaml"],
    "curr_sft": ["-m", "obtune.objectives", "train", "--config", "train/obj_curr_codellama7b_py.yaml", "--objective", "sft"],
    "curr_kl": ["-m", "obtune.objectives", "train", "--config", "train/obj_curr_codellama7b_py.yaml", "--objective", "consistency"],
    "resample": ["-m", "obtune.train_sft", "--config", "train/resample_py_X1.yaml", "--model", "codellama-7b"],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--only", nargs="*", default=list(ARMS))
    args = ap.parse_args()
    failed = []
    for arm in args.only:
        out = SCRATCH / arm
        for extra in (["--dry-run"], ["--max-steps", str(args.steps)]):
            cmd = [sys.executable] + ARMS[arm] + ["--out", str(out)] + extra
            t0 = time.time()
            print(f"\n===== {arm} {' '.join(extra)} =====\n$ {' '.join(cmd)}", flush=True)
            rc = subprocess.call(cmd, cwd=ROOT)
            print(f"===== {arm} {' '.join(extra)}: rc={rc} in {time.time() - t0:.0f}s =====", flush=True)
            if rc != 0:
                failed.append(f"{arm} {' '.join(extra)}")
                break
    print("\nSMOKE FAILED: " + ", ".join(failed) if failed else "\nSMOKE OK: all arms passed", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
