#!/usr/bin/env python
"""Enqueue Experiment-1 training arms into the file-queue scheduler.

    python scripts/srh/21_enqueue_e1_arms.py --stage 1                 # inspect
    python scripts/srh/21_enqueue_e1_arms.py --stage 1 --write         # enqueue
    python scripts/srh/21_enqueue_e1_arms.py --stage 2 --write --priority 61

Staging, because the cheapest decisive result should land first and because a null in an
early stage makes every later stage uninterpretable:

  stage 1  1.5B: rev, flip, mix50, flipsym          ~5 GPU-h   THE KILL-GATE
           If `rev` reverse-success is ~0, the reverse direction is not learnable on this
           corpus at this scale and no other arm's null means anything. Stop there.
  stage 2  7B:  rev, flip (+ the replication's 7B sft/cft, which are NOT yet queued)
           The decisive comparison: does trivially-free reverse data beat the contrastive
           objective?
  stage 3  7B:  mix50, fwd2x     the budget controls — only if flip > fwd
  stage 4  7B:  cftflip          only if flip or cft is non-zero
  stage 5  7B:  flipsym          only if the mechanistic phase finds disjointness

Arms `fwd` and `cft` are never enqueued: they ARE the replication's `sft`/`cft` adapters.
Retraining them would spend GPU-hours reproducing a run we already have and risk a seed
difference being read as an arm effect.

**Priority is a scheduling decision, not a technical one.** obtune's own RQ1 grid runs at
10–50 and the CFT replication at 60; the default here (61+) puts Experiment 1 behind both.
Raising it delays the project's own experiments, which is a human's call to make.
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
from obtune.srh import arms as srh_arms  # noqa: E402

#: (model infix, arms, default priority). Lower priority runs first.
#:
#: The ladder in use on this host:
#:   10-50  obtune's own RQ1 grid
#:   60     the CFT replication at 1.5B
#:   61     stage 1 here (the 1.5B kill-gate)
#:   62     the CFT replication at 7B  <- Experiment 1's FWD and CFT arms at headline scale
#:   63+    stages 2-5 here
#: Stage 2 sits ABOVE 62 deliberately: it is evaluated against the 7B replication adapters,
#: and the queue has no dependency edges, so priority order is the only thing keeping the
#: 7B SRH arms from finishing before the baselines they are compared against exist.
STAGES: dict[int, tuple[str, tuple[str, ...], int]] = {
    1: ("qwen1.5b", ("rev", "flip", "mix50", "flipsym"), 61),
    2: ("qwen7b", ("rev", "flip"), 63),
    3: ("qwen7b", ("mix50", "fwd2x"), 64),
    4: ("qwen7b", ("cftflip",), 65),
    5: ("qwen7b", ("flipsym",), 66),
}

#: Rough per-arm GPU-hours, for the queue's scheduling hints only.
EST_GPU_H = {
    ("qwen1.5b", "rev"): 0.6, ("qwen1.5b", "flip"): 1.3,
    ("qwen1.5b", "mix50"): 0.6, ("qwen1.5b", "flipsym"): 1.3,
    ("qwen7b", "rev"): 3.1, ("qwen7b", "flip"): 6.1, ("qwen7b", "mix50"): 3.1,
    ("qwen7b", "fwd2x"): 6.1, ("qwen7b", "cftflip"): 11.0, ("qwen7b", "flipsym"): 6.1,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--stage", type=int, required=True, choices=sorted(STAGES))
    ap.add_argument("--language", default="python", choices=["python", "javascript"])
    ap.add_argument("--arms", default=None, help="comma-separated subset of the stage's arms")
    ap.add_argument("--priority", type=int, default=None, help="override the stage default")
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--write", action="store_true", help="actually write the job files")
    args = ap.parse_args()

    model_infix, stage_arms, default_priority = STAGES[args.stage]
    wanted = tuple(args.arms.split(",")) if args.arms else stage_arms
    priority = args.priority if args.priority is not None else default_priority
    lang_short = {"python": "py", "javascript": "js"}[args.language]

    jobs = []
    for arm in wanted:
        spec = srh_arms.resolve(arm)
        if spec.reuses:
            print(f"  [SKIP] {arm}: reuses an existing adapter ({spec.reuses})")
            continue
        rel = f"srh/train/{arm}_{model_infix}_{lang_short}.yaml"
        if not (ROOT / "configs" / rel).exists():
            raise SystemExit(f"missing config: configs/{rel}")
        cfg = load_config(rel)
        if args.seed != 17:
            cfg.setdefault("train", {})["seed"] = args.seed
        out = cft_train.adapter_dir(cfg)
        jobs.append(
            {
                "job_id": cft_train.run_id_for(cfg, "srh"),
                "kind": "train",
                "argv": ["-m", "obtune.srh.train", "--config", rel]
                + (["--seed", str(args.seed)] if args.seed != 17 else []),
                "raw": False,
                "est_gpu_h": EST_GPU_H.get((model_infix, arm), 3.0),
                "priority": priority,
                "meta": {
                    "experiment": "srh/exp1",
                    "stage": args.stage,
                    "arm": arm,
                    "role": spec.role,
                    "tasks": list(spec.tasks),
                    "language": args.language,
                    "adapter_dir": str(out),
                    "already_trained": (out / "final").exists(),
                },
            }
        )

    for j in jobs:
        state = "ALREADY TRAINED" if j["meta"]["already_trained"] else "to run"
        print(f"  [{state}] p{j['priority']} {j['job_id']}")
        print(f"            {j['meta']['role']}")

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

    print(
        "\nEvaluation is NOT enqueued: it needs every arm of the stage to exist, and the "
        "queue has no dependency edges. Once the jobs land in runs/manifest/done/:\n"
        f"    python -m obtune.cft.evaluate --config srh/eval/e1_{model_infix}.yaml --gpu <idle>\n"
        f"    python scripts/cft/12_report.py results/<date>_cft-bidirectional/{args.language}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
