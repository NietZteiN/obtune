#!/usr/bin/env python
"""Advance the routing/merging track: checkpoint-select finished specialists, then merge them.

    python scripts/merge/build_ready_merges.py            # report readiness
    python scripts/merge/build_ready_merges.py --submit   # queue whatever is ready

TWO STAGES, AND THE FIRST WAS MISSING FROM THE PLAN. `docs/EXPERIMENT_CHECKLIST.md` P1 read
"5 specialists per model, then merges (CPU, free)". Training a specialist leaves `checkpoint-*/`
and `final/`; it does NOT leave `best/`, and `merge_adapters.py` defaults to `checkpoint="best"`.
So every merge would have failed on a missing path until checkpoint-select had run on all five
adapters. That is ~6 min of GPU per specialist -- small, but it is a GPU step inside a stage costed
as CPU-only, and it gates the entire routing/merging track.

A merge is built FROM the per-condition adapters, so it cannot be queued ahead of them, and
chaining five merges behind five trainings per model across seven models is 35 dependency edges
maintained by hand. This checks readiness instead: a model qualifies when `L0` and all five
specialists exist and it has no merges yet.

CPU ONLY. `merge_adapters.py` loads with `device_map=None` and writes a plain adapter directory,
so these go to a CPU partition and never touch the GPU share.

The five arms mirror CodeLlama-7b's, which is what makes the panel comparable: three merges of the
six adapters (TIES, DARE-TIES, DARE-linear) and two anchored on the clean-code adapter, which are
the "is it the merge or the specialists" control.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ["L1b", "L1r", "L2", "S1", "S2"]
MODELS = ["codellama-13b", "codellama-34b", "llama31-8b", "starcoder2-15b",
          "gemma3-12b", "codegemma-7b", "granite31-8b"]
#: (output name, --combination-type, config). The l0merge arms use the same combination types but
#: a config whose adapter list is anchored on L0; see configs/merge/.
ARMS = [("merge_ties", "ties", "merge/ties_v1.yaml"),
        ("merge_dare_ties", "dare_ties", "merge/ties_v1.yaml"),
        ("merge_dare_linear", "dare_linear", "merge/ties_v1.yaml")]


def needs_ckpt_select(m: str) -> list[str]:
    """Specialists that finished training but have no `best/` yet."""
    d = ROOT / "runs/adapters" / m / "python"
    out = []
    for c in SPEC:
        a = d / f"{c}_r32_s17"
        if (a / "training_summary.json").exists() and not (a / "best/adapter_model.safetensors").exists():
            out.append(c)
    return out


def ready(m: str) -> tuple[bool, str]:
    d = ROOT / "runs/adapters" / m / "python"
    have = [c for c in SPEC if (d / f"{c}_r32_s17/best/adapter_model.safetensors").exists()]
    if not (d / "L0_r32_s17/best/adapter_model.safetensors").exists():
        return False, "no L0"
    pend = needs_ckpt_select(m)
    if pend:
        return False, f"{len(have)}/5 with best/; awaiting ckpt-select: {','.join(pend)}"
    if len(have) < len(SPEC):
        return False, f"{len(have)}/5 specialists trained"
    if list(d.glob("*merge*_r32_s17")):
        return False, "merges already built"
    return True, "ready"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    n_ck = n_mg = 0
    live = subprocess.run(["squeue", "-u", __import__("os").environ.get("USER", ""), "-h", "-o", "%j"],
                          capture_output=True, text=True).stdout.split()
    for m in MODELS:
        ok, why = ready(m)
        print(f"  {m:16s} {why}")
        # Stage 1: checkpoint-select anything trained but unselected. GPU, ~6 min each.
        for c in needs_ckpt_select(m):
            job = f"ck_{c}_{m}"
            if job in live:
                continue
            if a.submit:
                r = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/slurm/submit.py"), "--name", job,
                     "--partition", "h100", "--gres", "gpu:1", "--cpus", "8", "--mem", "64G",
                     "--time", "1:00:00", "--argv", "-m", "obtune.eval_vllm",
                     "--config", f"train/grid_py_{c}_panel.yaml", "--model", m,
                     "--mode", "ckpt-select", "--adapter-root",
                     f"runs/adapters/{m}/python/{c}_r32_s17"],
                    capture_output=True, text=True, cwd=ROOT)
                print(f"      {((r.stdout or r.stderr).strip().splitlines() or [''])[-1]}")
                n_ck += 1
        if not (ok and a.submit):
            continue
        for name, comb, cfg in ARMS:
            out = f"runs/adapters/{m}/python/{name}_r32_s17"
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts/slurm/submit.py"),
                 "--name", f"mg_{name}_{m}", "--partition", "dev", "--gres", "none",
                 "--cpus", "8", "--mem", "64G", "--time", "0:40:00", "--argv",
                 str(ROOT / "src/obtune/merge_adapters.py"), "--config", cfg,
                 "--model", m, "--language", "python", "--rank", "32",
                 "--combination-type", comb, "--out", out],
                capture_output=True, text=True, cwd=ROOT)
            line = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
            print(f"      {line[0]}")
            n_mg += 1
    if a.submit:
        print(f"\n  submitted {n_ck} checkpoint-select and {n_mg} merge job(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
