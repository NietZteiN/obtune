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

from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RUNS_DIR, load_config  # noqa: E402
from obtune.data import DEFAULT_EVAL_SOURCE  # noqa: E402

QUEUE = RUNS_DIR / "manifest" / "queued"

# Priorities encode the dependency chain, since the queue has no DAG: nothing can
# route among per-condition adapters until those adapters exist and have been
# checkpoint-selected, and nothing can merge them either.
PRIORITY = {"train": 10, "ckpt-select": 20, "eval-cell": 30,
            "merge": 40, "router": 45, "eval-rq2": 50}
EST_GPU_H = {"train": 0.7, "ckpt-select": 0.1, "eval-cell": 0.08,
             "merge": 0.1, "router": 0.4, "eval-rq2": 0.08}


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
    """Standard per-condition SFT jobs.

    SRH arms are NOT trainable through here. They use `obtune.srh.train` (a different
    mixture builder, honouring `tasks` and `direction_mix`) and write under
    `runs/adapters_srh/` via `adapter_root`. Emitting a train_sft job for one would
    silently produce a plain forward adapter under an SRH arm's name, in the wrong
    directory — indistinguishable from a real REV/FLIP/MIX50 run at eval time. Refuse
    loudly; `scripts/srh/21_enqueue_e1_arms.py` is the right tool.
    """
    from obtune.train_sft import adapter_dir

    srh = [c for c in configs if "srh" in Path(c).parts or "/srh/" in str(c)]
    if srh:
        raise SystemExit(
            f"build_manifest --train was given SRH config(s): {[str(c) for c in srh]}.\n"
            f"These must be enqueued with scripts/srh/21_enqueue_e1_arms.py — train_sft "
            f"would ignore their `tasks`/`direction_mix` and train plain forward SFT under "
            f"the arm's name.")

    out = []
    for cfg_path in configs:
        rel = cfg_rel(cfg_path)
        cfg = load_config(rel)
        for seed in seeds:
            resolved = {**cfg, "train": {**cfg.get("train", {}), "seed": seed}}
            adir = adapter_dir(resolved)
            # The job id must distinguish configs that differ ONLY in a training knob.
            # It was built from (model, language, conditions, seed) alone, so a 9-epoch
            # overtraining probe on L1b produced the SAME id as the finished 3-epoch job.
            # Two concrete harms, both observed before this guard: the paired ckpt-select
            # found that id already in done/, judged its dependency met, and fired before
            # the new training existed; and on completion the record would have overwritten
            # the 3-epoch run's provenance. Fold in a non-default adapter_root and any
            # run_tag that is not simply the condition list.
            tag = f"{cfg['model']}_{cfg['language']}_{'-'.join(cfg['train_conditions'])}_s{seed}"
            root = cfg.get("adapter_root")
            if root:
                tag = f"{Path(str(root)).name.removeprefix('runs/').removeprefix('adapters_')}__{tag}"
            rt = cfg.get("run_tag")
            if rt and rt not in tag and rt != '-'.join(cfg['train_conditions']):
                tag = f"{tag}__{rt}"
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
    """One job per (model, language, system) — all eval conditions inside it.

    NOT one job per cell. Measured: 7 cells x 1,670 items take 88 s when they share a
    vLLM engine, but a per-cell job pays ~50 s of engine startup EACH — 196 cells
    would burn ~2.7 GPU-hours starting engines. Resumability does not suffer: the
    cell-level parquet check inside eval_vllm still skips finished cells, so a job
    that dies half way redoes only the cells it had not written.
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
            # RQ2 systems (router, merges) are emitted by rq2_jobs(), which attaches
            # the routing map and the ordering that makes them meaningful. Dropped here
            # BEFORE expansion, because `router` without a route map is refused by
            # design — it would otherwise evaluate base weights labelled as routed.
            raw = [r for r in cfg["systems"]
                   if not (r.get("arch", "none") == "router"
                           or str(r.get("arch", "")).startswith("merge"))]
            systems = expand_systems(raw, model, language,
                                     cfg.get("train_conditions") or [], seeds, rank=rank)
            for sysspec in systems:
                if systems_filter and sysspec.name not in systems_filter:
                    continue
                out.append(job(
                    "eval-cell", f"eval__{model}_{language}_{sysspec.name}",
                    ["-m", "obtune.eval_vllm", "--config", str(rel), "--systems", sysspec.name],
                    {"model": model, "language": language, "system": sysspec.name,
                     "n_eval_conditions": len(cfg["eval_conditions"]),
                     "adapter": sysspec.adapter, "train_cond": sysspec.train_cond},
                ))
    return out



def rq2_jobs(eval_cfg_path: Path) -> list[dict[str, Any]]:
    """RQ2 — per-type adapters behind a learned router, and LoRA merges.

    These are the systems that only make sense once the per-condition adapters exist,
    which is why they carry higher priority numbers rather than living in a separate
    manifest: one queue, ordered, so a worker that frees up late still does useful work.

    The router is ONE classifier over the trainable conditions that dispatches to the
    matching per-type adapter — not one router per condition. H1 is never a class; its
    routing entropy is a reported RQ2 result (the out-of-distribution decision).
    """
    rel = cfg_rel(eval_cfg_path)
    cfg = load_config(rel)
    models = cfg.get("models") or [cfg["model"]]
    languages = cfg.get("languages") or [cfg["language"]]
    conds = list(cfg.get("train_conditions") or [])
    rank = int((cfg.get("peft") or {}).get("r", 32))
    seed = int((cfg.get("seeds") or [GLOBAL_SEED])[0])  # RQ2 uses one seed's adapters

    out = []
    for model in models:
        for language in languages:
            tag = f"{model}_{language}"
            rq2_dir = f"results/router/{model}/{language}"

            # --- merges: cheap, CPU-ish, no dependency beyond the adapters --------
            # `--combination-type` is load-bearing: without it every job read the same
            # `combination_type: ties` out of the config and the three "different" merges
            # came out byte-identical, so the RQ2 merge comparison measured one method
            # three times.
            for combo in ("ties", "dare_ties", "dare_linear"):
                out.append(job(
                    "merge", f"merge__{tag}__{combo}",
                    ["-m", "obtune.merge_adapters", "--config", "merge/ties_v1.yaml",
                     "--model", model, "--language", language, "--rank", str(rank),
                     "--combination-type", combo,
                     "--out", f"runs/adapters/{model}/{language}/merge_{combo}_r{rank}_s{seed}"],
                    {"model": model, "language": language, "combination_type": combo},
                ))

            # --- router: features -> classifier -> routing map ---------------------
            # TWO feature sets, not one. The classifier is fit on TRAIN pairs; the routing
            # decisions are made on EVAL items. Reusing a single features.npz for both
            # meant the router was routing the same rows it was trained on, and the
            # emitted job had no --train-jsonl at all, so it exited "no rows" — the actual
            # first failure in this chain.
            feats_train = f"{rq2_dir}/features_train.npz"
            feats_eval = f"{rq2_dir}/features_eval.npz"
            router = f"{rq2_dir}/router.npz"
            # MUST match the evaluator's own default or the route map is keyed to a
            # different item_id namespace and matches nothing: heldout ids look like
            # `cruxevalx_js_0::L0::0`, testset ids like `A:JavaScript/136::L0::0`.
            # Imported rather than hardcoded so the two cannot drift apart.
            eval_source = cfg.get("eval_source", DEFAULT_EVAL_SOURCE)
            train_inputs = [f"data/train/pairs/{c}/{language}.jsonl" for c in conds]
            eval_inputs = [
                f"data/eval/{eval_source}/items/{c}/{language}.jsonl" for c in conds
            ]
            out.append(job(
                "router", f"router_features_train__{tag}",
                ["-m", "obtune.router.features", "--config", "router/router_v1.yaml",
                 "--model", model, "--train-jsonl", *train_inputs, "--out", feats_train],
                {"model": model, "language": language, "stage": "features_train"},
            ))
            out.append(job(
                "router", f"router_features_eval__{tag}",
                ["-m", "obtune.router.features", "--config", "router/router_v1.yaml",
                 "--model", model, "--eval-jsonl", *eval_inputs, "--out", feats_eval],
                {"model": model, "language": language, "stage": "features_eval"},
            ))
            out.append(job(
                "router", f"router_train__{tag}",
                ["-m", "obtune.router.train_router", "--config", "router/router_v1.yaml",
                 "--features", feats_train, "--out", router],
                {"stage": "train", "depends_on": f"router_features_train__{tag}"},
            ))
            adapter_map = {
                c: f"runs/adapters/{model}/{language}/{c}_r{rank}_s{seed}/best" for c in conds
            }
            map_path = f"{rq2_dir}/adapter_map.json"
            # The map itself is materialized in main(), from job meta, so that --dry-run
            # stays side-effect free. It used to be computed into meta, passed as
            # --adapter-map, and never written by anything.
            out.append(job(
                "router", f"router_route__{tag}",
                ["-m", "obtune.router.route", "--router", router, "--features", feats_eval,
                 "--adapter-map", map_path,
                 "--out", f"{rq2_dir}/routing.parquet",
                 "--route-map", f"{rq2_dir}/route_map.json",
                 "--report", f"{rq2_dir}/routing_report.json"],
                # BOTH inputs: the classifier AND the eval-item features it routes.
                # Declaring only the classifier let route start before features_eval
                # existed.
                {"stage": "route",
                 "depends_on": [f"router_train__{tag}", f"router_features_eval__{tag}"],
                 "adapter_map": adapter_map, "adapter_map_path": map_path},
            ))

            # --- the RQ2 eval systems ---------------------------------------------
            out.append(job(
                "eval-rq2", f"evalrq2__{tag}_router",
                ["-m", "obtune.eval_vllm", "--config", rel, "--systems", "router",
                 "--model", model, "--language", language,
                 "--route-map", f"{rq2_dir}/route_map.json"],
                {"model": model, "language": language, "system": "router",
                 "depends_on": f"router_route__{tag}"},
            ))
            for combo in ("ties", "dare_ties", "dare_linear"):
                out.append(job(
                    "eval-rq2", f"evalrq2__{tag}_merge_{combo}",
                    ["-m", "obtune.eval_vllm", "--config", rel, "--systems", f"merge_{combo}",
                     "--model", model, "--language", language],
                    {"model": model, "language": language, "system": f"merge_{combo}",
                     "depends_on": f"merge__{tag}__{combo}"},
                ))
    return out


def write_adapter_maps(jobs: list[dict[str, Any]]) -> list[Path]:
    """Materialize every `adapter_map` a router job refers to.

    `rq2_jobs` passes `--adapter-map <path>` and records the map in job meta, but nothing
    ever created the file, so `router.route` died on a missing path. Done here rather than
    in `rq2_jobs` so that `--dry-run` writes nothing.
    """
    written: list[Path] = []
    for j in jobs:
        meta = j.get("meta") or {}
        amap, path = meta.get("adapter_map"), meta.get("adapter_map_path")
        if not amap or not path:
            continue
        p = PROJECT_ROOT / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(amap, indent=2))
        written.append(p)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", nargs="*", default=[], help="training config globs")
    ap.add_argument("--eval", nargs="*", default=[], help="evaluation config paths")
    ap.add_argument("--rq2", nargs="*", default=[],
                    help="eval configs to also expand into RQ2 router + merge jobs")
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
    for e in args.rq2:
        jobs += rq2_jobs(Path(e))

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

    for p in write_adapter_maps(jobs):
        print(f"  wrote {p.relative_to(PROJECT_ROOT)}")

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
