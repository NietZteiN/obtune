#!/usr/bin/env python
"""Expand an experiment grid into job files for the queue in `runs/manifest/queued/`.

`src/obtune/sched/worker.py` consumes those files; this is the piece that produces
them. Jobs are ordered so the queue is useful early and never blocks on itself:

    priority 10  train           (nothing else can run until adapters exist)
    priority 20  ckpt-select     (an eval cell needs `best/` to resolve)
    priority 30  eval-cell       (the bulk; each is independent and resumable)

Every job is idempotent — `train_sft` skips a finished adapter and `eval_vllm` skips a
cell whose parquet exists — so the whole manifest can be rebuilt and re-run after an
interruption without losing work.

    python scripts/build_manifest.py --train configs/train/grid_qwen1.5b_py_*.yaml \\
                                     --eval configs/eval/grid_rq1.yaml --seeds 17 42
    python scripts/build_manifest.py ... --dry-run
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import GLOBAL_SEED, RUNS_DIR, load_config  # noqa: E402

QUEUE = RUNS_DIR / "manifest" / "queued"

PRIORITY = {"train": 10, "ckpt-select": 20, "eval-cell": 30}
EST_GPU_H = {"train": 0.7, "ckpt-select": 0.1, "eval-cell": 0.08}


def cfg_rel(path: Path) -> str:
    """Path as load_config() wants it: relative to configs/, which is where it
    anchors relative paths. A caller naturally types `configs/train/x.yaml`, which
    would otherwise resolve to `configs/configs/train/x.yaml`."""
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.relative_to(ROOT / "configs"))
        except ValueError:
            return str(p)
    parts = p.parts
    return str(Path(*parts[1:])) if parts and parts[0] == "configs" else str(p)


def job(kind: str, job_id: str, argv: list[str], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "kind": kind,
        "argv": argv,
        "raw": False,
        "est_gpu_h": EST_GPU_H.get(kind, 1.0),
        "priority": PRIORITY.get(kind, 100),
        "meta": meta,
    }


def train_jobs(configs: list[Path], seeds: list[int]) -> list[dict[str, Any]]:
    from obtune.train_sft import adapter_dir

    out = []
    for cfg_path in configs:
        rel = cfg_rel(cfg_path)
        cfg = load_config(rel)
        for seed in seeds:
            resolved = {**cfg, "train": {**cfg.get("train", {}), "seed": seed}}
            adir = adapter_dir(resolved)
            tag = f"{cfg['model']}_{cfg['language']}_{'-'.join(cfg['train_conditions'])}_s{seed}"
            out.append(job(
                "train", f"train__{tag}",
                ["-m", "obtune.train_sft", "--config", str(rel), "--seed", str(seed)],
                {"adapter_dir": str(adir), "language": cfg["language"],
                 "train_conditions": cfg["train_conditions"], "seed": seed},
            ))
            out.append(job(
                "ckpt-select", f"ckptsel__{tag}",
                ["-m", "obtune.eval_vllm", "--config", str(rel), "--mode", "ckpt-select",
                 "--adapter-root", str(adir)],
                {"adapter_dir": str(adir), "depends_on": f"train__{tag}"},
            ))
    return out


def eval_jobs(eval_cfg_path: Path, systems_filter: list[str] | None) -> list[dict[str, Any]]:
    """One job per (model, language, system, eval condition).

    Split this finely rather than one job per config: cells are independent, so a
    per-cell queue keeps every GPU busy and makes a failure cost one cell, not a run.
    """
    from obtune.eval_vllm import expand_systems

    rel = cfg_rel(eval_cfg_path)
    cfg = load_config(rel)
    models = cfg.get("models") or [cfg["model"]]
    languages = cfg.get("languages") or [cfg["language"]]
    seeds = [int(x) for x in (cfg.get("seeds") or [cfg.get("seed", GLOBAL_SEED)])]
    rank = int((cfg.get("peft") or {}).get("r", 32))

    out = []
    for model in models:
        for language in languages:
            systems = expand_systems(cfg["systems"], model, language,
                                     cfg.get("train_conditions") or [], seeds, rank=rank)
            for sysspec in systems:
                if systems_filter and sysspec.name not in systems_filter:
                    continue
                for cond in cfg["eval_conditions"]:
                    jid = f"eval__{model}_{language}_{sysspec.name}__{cond}"
                    out.append(job(
                        "eval-cell", jid,
                        ["-m", "obtune.eval_vllm", "--config", str(rel),
                         "--systems", sysspec.name, "--eval-conditions", cond],
                        {"model": model, "language": language, "system": sysspec.name,
                         "eval_cond": cond, "adapter": sysspec.adapter,
                         "train_cond": sysspec.train_cond},
                    ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", nargs="*", default=[], help="training config globs")
    ap.add_argument("--eval", nargs="*", default=[], help="evaluation config paths")
    ap.add_argument("--seeds", nargs="*", type=int, default=[GLOBAL_SEED])
    ap.add_argument("--systems", nargs="*", default=None, help="restrict eval to these systems")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--clear", action="store_true", help="empty the queue before writing")
    args = ap.parse_args()

    # A training job must never be enqueued against a corpus containing H1
    # (CLAUDE.md §3.2). Fail the whole manifest rather than queue a poisoned run.
    if args.train:
        check = ROOT / "scripts" / "check_no_h1_in_train.py"
        if check.exists():
            r = subprocess.run([sys.executable, str(check)], cwd=ROOT,
                               capture_output=True, text=True)
            if r.returncode != 0:
                print("REFUSING to enqueue training jobs — H1 quarantine check failed:")
                print((r.stdout + r.stderr)[-2000:])
                return 2
            print("  H1 quarantine check: OK")

    jobs: list[dict[str, Any]] = []
    train_cfgs = sorted({Path(p) for pat in args.train for p in glob.glob(pat)})
    if train_cfgs:
        jobs += train_jobs(train_cfgs, args.seeds)
    for e in args.eval:
        jobs += eval_jobs(Path(e), args.systems)

    if not jobs:
        print("no jobs — pass --train and/or --eval")
        return 1

    by_kind: dict[str, int] = {}
    for j in jobs:
        by_kind[j["kind"]] = by_kind.get(j["kind"], 0) + 1
    print("  " + "  ".join(f"{k}={v}" for k, v in sorted(by_kind.items())) + f"  total={len(jobs)}")

    if args.dry_run:
        for j in jobs[:8]:
            print(f"    [{j['priority']:>3}] {j['job_id']}")
        if len(jobs) > 8:
            print(f"    ... and {len(jobs) - 8} more")
        return 0

    QUEUE.mkdir(parents=True, exist_ok=True)
    if args.clear:
        for f in QUEUE.glob("*.json"):
            f.unlink()
    for j in jobs:
        (QUEUE / f"{j['priority']:03d}_{j['job_id']}.json").write_text(json.dumps(j, indent=1))
    print(f"  wrote {len(jobs)} job files -> {QUEUE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
