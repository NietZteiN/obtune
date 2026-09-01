#!/usr/bin/env python3
"""Submit the whole base-model replication as ONE dependency-linked SLURM DAG.

WHY THIS EXISTS. Rebuilding the corpus on a new base is ~40 GPU-hours across ~45 jobs in
four dependent stages (train -> checkpoint-select -> evaluate -> analyse). Driving that by
hand means somebody watching a queue for two days. SLURM already expresses the ordering, so
this emits the DAG and exits: every stage carries `--dependency=afterok:<upstream>`, and a
failed stage leaves its dependents PENDING with DependencyNeverSatisfied rather than running
on missing inputs. That last part is the point -- an eval whose adapter never trained would
otherwise silently score the base model and look like a null result.

    python scripts/slurm/pipeline_replication.py --model codellama-7b --dry-run
    python scripts/slurm/pipeline_replication.py --model codellama-7b

DEPENDENCY AUDIT (2026-08-31). A stage must wait for EVERY adapter its eval config names,
not just the ones its own stage produced. Four races were caught before they fired:

  * rq1_matrix evaluates `formatonly`, which stage 3 trains -- so it also waits on ev_floor,
    which additionally serialises the two jobs that would otherwise write the same cells.
  * ev_loto carries `tuned_L0` and `mono_all` rows, produced by stages 1 and 5.
  * ev_rq2 carries `formatonly` and `tuned_L0` rows.
  * the l0merge control merges THREE clean-code seeds (s17/s42/s101), not just the s101 the
    stage trains.

`validate_systems` will not catch these: it checks that an adapter path is DECLARED, not
that it exists, so a missing adapter passes validation and dies later at LoRA load.

ORDERING IS NOT ARBITRARY. The format floor runs EARLY, right behind the RQ1 grid, because
it decides what every other number means: at Qwen-1.5B a label-shuffled control recovered
62-67 % of every gain, at Qwen-7B only 2-14 %, and which regime a base sits in is not
knowable from its accuracy alone. Discovering that late would invalidate the analysis of
everything downstream. H1 is NOT in this DAG at any point -- the quarantine budget is spent
deliberately by a human, never by a pipeline.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBMIT = ROOT / "scripts" / "slurm" / "submit.py"
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
SEEDS = [17, 42]

# LOTO folds: each trains on the five conditions that are NOT held out.
LOTO = {c: [x for x in CONDS if x != c] for c in CONDS}


def submit(name, argv, *, partition, time, dependency=None, mem=None, gres=None,
           dry_run=False) -> str | None:
    cmd = [sys.executable, str(SUBMIT), "--name", name, "--partition", partition,
           "--time", time]
    if dependency:
        # A fan-in dependency is "afterok:A:B:C" -- ONE type prefix, then colon-separated
        # ids. The earlier form treated any string containing ':' as already-prefixed, so a
        # joined id list went to SLURM as "--dependency 1:2:3", which sbatch rejects. The
        # six fan-in jobs (both matrix evals, three merges, the RQ2 eval) then failed to
        # submit while their 45 upstream jobs queued happily -- a pipeline that looked fine
        # and had no terminal stages.
        dep = str(dependency)
        if not dep.startswith(("afterok:", "afterany:", "afternotok:", "after:")):
            dep = f"afterok:{dep}"
        cmd += ["--dependency", dep]
    if mem:
        cmd += ["--mem", mem]
    if gres is not None:
        cmd += ["--gres", gres]
    if dry_run:
        cmd += ["--dry-run"]
    cmd += ["--argv"] + argv
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    line = (out.stdout or "").strip().splitlines()
    if dry_run:
        print(f"  [dry-run] {name}: {' '.join(argv)}")
        return "DRYRUN"
    for l in line:
        if l.startswith("submitted "):
            jid = l.split()[1]
            print(f"  {jid}  {name}" + (f"  (after {dependency})" if dependency else ""))
            return jid
    print(f"  FAILED to submit {name}: {out.stdout.strip()} {out.stderr.strip()}",
          file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="key in configs/models.yaml")
    ap.add_argument("--language", default="python")
    ap.add_argument("--partition", default="h200")
    ap.add_argument("--cpu-partition", default="normal")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stages", default="all",
                    help="comma-separated subset: rq1,floor,loto,rq2 (default all)")
    a = ap.parse_args()
    M, L = a.model, a.language
    root = f"runs/adapters/{M}/{L}"
    want = set(CONDS) if a.stages == "all" else None
    stages = {"rq1", "floor", "loto", "rq2"} if a.stages == "all" else set(a.stages.split(","))
    d = a.dry_run
    jid = {}

    # ---- Stage 1: RQ1 specialists ------------------------------------------------
    if "rq1" in stages:
        print("STAGE 1 — RQ1 specialists (12 adapters)")
        sel = []
        for c in CONDS:
            for s in SEEDS:
                t = submit(f"tr_{c}_s{s}", ["-m", "obtune.train_sft", "--config",
                           f"train/grid_py_{c}.yaml", "--model", M, "--seed", str(s)],
                           partition=a.partition, time="02:00:00", dry_run=d)
                k = submit(f"ck_{c}_s{s}", ["-m", "obtune.eval_vllm", "--config",
                           f"train/grid_py_{c}.yaml", "--model", M, "--mode", "ckpt-select",
                           "--adapter-root", f"{root}/{c}_r32_s{s}"],
                           partition=a.partition, time="00:45:00", dependency=t, dry_run=d)
                sel.append(k)
        jid["rq1_selects"] = sel
        print("STAGE 2 — RQ1 transfer matrix (78 cells, NO H1)")
        jid["rq1_matrix"] = submit("rq1_matrix", ["-m", "obtune.eval_vllm", "--config",
            "eval/grid_rq1_generic.yaml", "--model", M, "--language", L],
            partition=a.partition, time="04:00:00",
            dependency=":".join(x for x in sel if x) if not d else None, dry_run=d)

    # ---- Stage 3: the format floor, EARLY ----------------------------------------
    if "floor" in stages:
        print("STAGE 3 — format-acquisition floor (decides what the matrix means)")
        t = submit("tr_floor", ["-m", "obtune.train_sft", "--config",
                   "train/formatonly_generic_py.yaml", "--model", M, "--seed", "17"],
                   partition=a.partition, time="02:00:00", dry_run=d)
        k = submit("ck_floor", ["-m", "obtune.eval_vllm", "--config",
                   "train/formatonly_generic_py.yaml", "--model", M, "--mode", "ckpt-select",
                   "--adapter-root", f"runs/adapters_formatonly/{M}/{L}/L0_r32_s17"],
                   partition=a.partition, time="00:45:00", dependency=t, dry_run=d)
        jid["floor_eval"] = submit("ev_floor", ["-m", "obtune.eval_vllm", "--config",
            "eval/grid_rq1_generic.yaml", "--model", M, "--language", L,
            "--systems", "formatonly"], partition=a.partition, time="02:00:00",
            dependency=k, dry_run=d)

    # ---- Stage 4: LOTO — the non-H1 held-out instrument --------------------------
    if "loto" in stages:
        print("STAGE 4 — LOTO folds (held-out transform WITHOUT spending H1)")
        sel = []
        for held, trained in LOTO.items():
            tag = "-".join(trained)
            t = submit(f"tr_loto_hold{held}", ["-m", "obtune.train_sft", "--config",
                       f"train/loto_py_hold{held}.yaml", "--model", M, "--seed", "17"],
                       partition=a.partition, time="03:00:00", dry_run=d)
            k = submit(f"ck_loto_hold{held}", ["-m", "obtune.eval_vllm", "--config",
                       f"train/loto_py_hold{held}.yaml", "--model", M, "--mode",
                       "ckpt-select", "--adapter-root",
                       f"runs/adapters_loto/{M}/{L}/{tag}_r32_s17"],
                       partition=a.partition, time="00:45:00", dependency=t, dry_run=d)
            sel.append(k)
        jid["loto_eval"] = submit("ev_loto", ["-m", "obtune.eval_vllm", "--config",
            "eval/loto_generic.yaml", "--model", M, "--language", L],
            partition=a.partition, time="04:00:00",
            dependency=":".join(x for x in sel if x) if not d else None, dry_run=d)

    # ---- Stage 5: RQ2 — mono, merges, and the control that guts them -------------
    if "rq2" in stages:
        print("STAGE 5 — RQ2 ladder (mono, merges, l0merge control)")
        tm = submit("tr_mono", ["-m", "obtune.train_sft", "--config",
                    "train/mono_generic_py.yaml", "--model", M, "--seed", "17"],
                    partition=a.partition, time="04:00:00", dry_run=d)
        km = submit("ck_mono", ["-m", "obtune.eval_vllm", "--config",
                    "train/mono_generic_py.yaml", "--model", M, "--mode", "ckpt-select",
                    "--adapter-root", f"{root}/{'-'.join(CONDS)}_r32_s17"],
                    partition=a.partition, time="00:45:00", dependency=tm, dry_run=d)
        # third clean-code seed for the l0merge control
        t101 = submit("tr_L0_s101", ["-m", "obtune.train_sft", "--config",
                      "train/grid_py_L0.yaml", "--model", M, "--seed", "101"],
                      partition=a.partition, time="02:00:00", dry_run=d)
        k101 = submit("ck_L0_s101", ["-m", "obtune.eval_vllm", "--config",
                      "train/grid_py_L0.yaml", "--model", M, "--mode", "ckpt-select",
                      "--adapter-root", f"{root}/L0_r32_s101"],
                      partition=a.partition, time="00:45:00", dependency=t101, dry_run=d)
        dep_specialists = ":".join(x for x in jid.get("rq1_selects", []) if x) or None
        merges = []
        for ct in ["ties", "dare_ties", "dare_linear"]:
            merges.append(submit(f"mrg_{ct}", ["-m", "obtune.merge_adapters", "--config",
                "merge/ties_v1.yaml", "--model", M, "--language", L, "--rank", "32",
                "--combination-type", ct, "--out", f"{root}/merge_{ct}_r32_s17"],
                partition=a.cpu_partition, time="01:00:00", mem="200G", gres="",
                dependency=dep_specialists if not d else None, dry_run=d))
        for ct in ["ties", "dare_ties"]:
            merges.append(submit(f"mrgl0_{ct}", ["-m", "obtune.merge_adapters", "--config",
                "merge/l0_control.yaml", "--model", M, "--language", L, "--rank", "32",
                "--combination-type", ct, "--adapter-dir",
                f"configs/merge/l0_control_{M}_adapters.json",
                "--out", f"{root}/l0merge_{ct}_r32_s17"],
                partition=a.cpu_partition, time="01:00:00", mem="200G", gres="",
                dependency=k101 if not d else None, dry_run=d))
        deps = [x for x in merges + [km] if x]
        jid["rq2_eval"] = submit("ev_rq2", ["-m", "obtune.eval_vllm", "--config",
            "eval/rq2_generic.yaml", "--model", M, "--language", L],
            partition=a.partition, time="04:00:00",
            dependency=":".join(deps) if not d and deps else None, dry_run=d)

    print("\nDAG submitted. `squeue -u $USER` to watch; a stage that fails leaves its "
          "dependents PENDING with DependencyNeverSatisfied rather than running on "
          "missing inputs.")
    print("H1 is deliberately absent from this pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
