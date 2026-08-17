#!/usr/bin/env python
"""Enqueue the CFT training arms into the file-queue scheduler.

    python scripts/cft/11_enqueue_arms.py --language python            # inspect
    python scripts/cft/11_enqueue_arms.py --language python --write    # enqueue
    python scripts/cft/11_enqueue_arms.py --language python --write --priority 5

The workers in `src/obtune/sched/worker.py` claim a job only when their GPU is genuinely
idle (CLAUDE.md §1), so enqueuing is the safe way to run on this shared box: the jobs
start by themselves whenever a GPU frees, and never crowd out a neighbour's work.

**Priority is a scheduling decision, not a technical one.** Lower numbers run first, and
obtune's own RQ1 grid sits at priority 10 (train) through 50 (eval-rq2). Enqueuing the
CFT arms below 10 delays that grid; enqueuing them above 50 means they wait for all of
it. The default (60) deliberately puts them LAST — a replication of someone else's paper
should not preempt the project's own experiments unless a human says so.

Evaluation is NOT enqueued here. It needs both adapters to exist, and the queue has no
dependency edges — a bidirectional eval job that started early would silently evaluate a
missing adapter path. Run it by hand once the two training jobs land in
`runs/manifest/done/`:

    python -m obtune.cft.evaluate --config cft/eval/bidir_v1.yaml --gpu <idle>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.cft import train as cft_train  # noqa: E402
from obtune.config import load_config  # noqa: E402
from obtune.sched.worker import QUEUED  # noqa: E402

#: Below obtune's own eval jobs (50) by default — see the module docstring.
DEFAULT_PRIORITY = 60

ARMS = ("sft", "cft")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--language", default="python", choices=["python", "javascript"])
    ap.add_argument("--model", default="qwen1.5b", help="config filename stem infix")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--priority", type=int, default=DEFAULT_PRIORITY)
    # Seed replication (E2). The adapter directory and run id both carry the seed
    # (cft_train.adapter_dir / run_id_for), so a second seed lands beside the first
    # rather than overwriting it — but ONLY if the override is applied to the config
    # before those are computed, which is why it is set below rather than passed
    # through argv alone.
    ap.add_argument("--seed", type=int, default=17,
                    help="retrain an arm at a second seed; 17 is the original")
    ap.add_argument("--est-gpu-h", type=float, default=3.0)
    ap.add_argument("--write", action="store_true", help="actually write the job files")
    args = ap.parse_args()

    lang_short = {"python": "py", "javascript": "js"}[args.language]
    jobs = []
    for arm in args.arms.split(","):
        rel = f"cft/train/{arm}_{args.model}_{lang_short}.yaml"
        path = ROOT / "configs" / rel
        if not path.exists():
            raise SystemExit(f"missing config: {path}")
        cfg = load_config(rel)
        if args.seed != 17:
            cfg.setdefault("train", {})["seed"] = args.seed
        out = cft_train.adapter_dir(cfg)
        job_id = cft_train.run_id_for(cfg)
        jobs.append(
            {
                "job_id": job_id,
                "kind": "train",
                "argv": (["-m", "obtune.cft.train", "--config", rel]
                         + (["--seed", str(args.seed)] if args.seed != 17 else [])),
                "raw": False,
                "est_gpu_h": args.est_gpu_h,
                "priority": args.priority,
                "meta": {
                    "experiment": "cft/replication",
                    "paper": "nikiema2025contrastive (arXiv:2509.05553)",
                    "arm": arm,
                    "seed": args.seed,
                    "tasks": list(cfg["tasks"]),
                    "language": args.language,
                    "adapter_dir": str(out),
                    "already_trained": (out / "final").exists(),
                },
            }
        )

    for j in jobs:
        state = "ALREADY TRAINED" if j["meta"]["already_trained"] else "to run"
        print(f"  [{state}] p{j['priority']:>3} {j['job_id']}  tasks={j['meta']['tasks']}")

    if not args.write:
        print("\ndry run — pass --write to enqueue")
        return 0

    QUEUED.mkdir(parents=True, exist_ok=True)
    for j in jobs:
        if j["meta"]["already_trained"]:
            print(f"skip {j['job_id']}: adapter already exists")
            continue
        dest = QUEUED / f"{j['job_id']}.json"
        dest.write_text(json.dumps(j, indent=2))
        print(f"enqueued {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
