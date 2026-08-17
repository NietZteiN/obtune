#!/usr/bin/env python
"""Enqueue bidirectional-evaluation configs into the file-queue scheduler.

    python scripts/srh/22_enqueue_evals.py srh/eval/e2_factorial_qwen1.5b.yaml
    python scripts/srh/22_enqueue_evals.py srh/eval/e2_factorial_qwen1.5b.yaml --write

WHY THIS EXISTS
`scripts/cft/11_enqueue_arms.py` deliberately refuses to enqueue evaluations, and its
reasoning is sound *for the case it was written for*: the queue has no dependency edges,
so an eval enqueued alongside its training jobs could be claimed first and would score a
missing adapter path.

That objection is about ORDER, not about evaluation. When every adapter an eval names
already exists on disk, there is nothing to wait for and hand-running it only means a
human babysitting `nvidia-smi`. This script closes that gap and keeps the guarantee by
asserting the precondition the queue cannot express: **it refuses to enqueue any config
whose adapters are not already present.** If a path is missing, that is a dependency edge
in disguise and the job does not go in the queue.

This matters on a shared box. A hand-launched eval races other users' jobs for memory and
dies at engine startup when it loses (vLLM raises rather than crowding a neighbour, which
is the desired behaviour but wastes the launch). A queued job is claimed only when its
worker's GPU is genuinely idle -- >2 GB used or >5 % util and the worker keeps waiting.

PRIORITY is a scheduling decision, not a technical one. The ladder in use on this host:
  10-50  obtune's own RQ1 grid
  60     the CFT replication at 1.5B
  61     Experiment 1 stage 1 (the 1.5B kill-gate)
  62     the CFT replication at 7B
  63+    Experiment 1 stages 2-5
Evaluations of already-trained adapters default to 59 here: ahead of any *training* still
queued for the CFT/SRH threads, because they are minutes of GPU time against hours and
they unblock analysis, but behind obtune's own RQ1 grid, which is not this thread's to
delay.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.sched.worker import DONE, QUEUED, RUNNING  # noqa: E402

DEFAULT_PRIORITY = 59


def check_adapters(cfg: dict) -> list[str]:
    """Return the configured adapter paths that do not exist.

    `None` means the untuned base model and is always fine. Everything else must be a
    real directory *now* -- see the module docstring on why this is the whole point.
    """
    missing = []
    for name, rel in (cfg.get("systems") or {}).items():
        if rel is None:
            continue
        if not (ROOT / rel).exists():
            missing.append(f"{name} -> {rel}")
    return missing


def check_model_consistency(cfg: dict) -> list[str]:
    """Adapter paths must carry the config's own model directory.

    This is the defect `scripts/preflight.py` was written for: a `systems:` deep-merge
    silently inherited a 1.5B adapter into a 7B eval, which loads without error and
    produces garbage under a real arm's label. Re-asserted here because enqueuing is the
    last human-visible step before a job runs unattended.
    """
    model = str(cfg["model"])
    return [
        f"{name} -> {rel} (config model is {model})"
        for name, rel in (cfg.get("systems") or {}).items()
        if rel is not None and model not in str(rel)
    ]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("configs", nargs="+", help="eval config paths relative to configs/")
    ap.add_argument("--priority", type=int, default=DEFAULT_PRIORITY)
    ap.add_argument("--est-gpu-h", type=float, default=1.0)
    ap.add_argument("--write", action="store_true", help="actually write the job files")
    args = ap.parse_args()

    # A job already queued, running or done under the same id would either duplicate the
    # work or -- worse -- have two workers write the same results directory concurrently.
    seen = {p.stem for d in (QUEUED, DONE) if d.exists() for p in d.glob("*.json")}
    seen |= {p.stem for p in RUNNING.glob("*/*.json")} if RUNNING.exists() else set()

    jobs, blocked = [], []
    for rel in args.configs:
        cfg = load_config(rel)
        stem = Path(rel).stem
        job_id = f"eval-bidir-{cfg['model']}-{cfg.get('language', 'python')}-{stem}"

        problems = [f"MISSING ADAPTER {m}" for m in check_adapters(cfg)]
        problems += [f"MODEL MISMATCH {m}" for m in check_model_consistency(cfg)]
        if job_id in seen:
            problems.append("job id already queued/running/done — remove it first to re-run")
        if problems:
            blocked.append((rel, problems))
            continue

        n_ad = sum(1 for v in (cfg.get("systems") or {}).values() if v)
        jobs.append({
            "job_id": job_id,
            "kind": "eval-cell",
            # The worker prepends sys.executable and runs from PROJECT_ROOT with
            # CUDA_VISIBLE_DEVICES already pinned at worker spawn, so no --gpu here:
            # passing one would index into the worker's already-masked device list.
            "argv": ["-m", "obtune.cft.evaluate", "--config", rel],
            "raw": False,
            "est_gpu_h": args.est_gpu_h,
            "priority": args.priority,
            "meta": {
                "experiment": "srh/exp1",
                "config": rel,
                "model": cfg["model"],
                "language": cfg.get("language", "python"),
                "systems": sorted((cfg.get("systems") or {})),
                "n_adapters": n_ad,
                "reverse_strategies": cfg.get("reverse_strategies"),
            },
        })

    for rel, problems in blocked:
        print(f"  [BLOCKED] {rel}")
        for p in problems:
            print(f"            {p}")
    for j in jobs:
        print(f"  [ok] p{j['priority']:>3} {j['job_id']}  "
              f"systems={j['meta']['systems']}")

    if blocked:
        print(f"\n{len(blocked)} config(s) blocked — nothing enqueued for them.")
    if not args.write:
        print("\ndry run — pass --write to enqueue")
        return 1 if blocked else 0

    QUEUED.mkdir(parents=True, exist_ok=True)
    for j in jobs:
        dest = QUEUED / f"{j['job_id']}.json"
        dest.write_text(json.dumps(j, indent=2))
        print(f"enqueued {dest}")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
