#!/usr/bin/env python3
"""Submit the REMAINING master-report tranches as one dependency-linked SLURM DAG.

Tranche A (baselines) and C (rank sweep) were launched separately; this covers what is
left, in the order that maximises information per GPU-hour:

    I  S3/S4 specialists + s2fam    -- also the experts the 8-way MoLE gate needs
    B  routing / MoLE                -- router features -> router -> gate -> eval
    D  merge sweeps and controls     -- densities, crossseed, residual (mostly CPU)
    H  forgetting                    -- HumanEval+/MBPP+ pre/post (CLAUDE.md §4 check 7)

WHAT THIS DELIBERATELY DOES NOT RUN. **H1.** The quarantine budget is two reads for the
life of the project (CLAUDE.md §3.2 rule 3) and spending one is a decision for a human, not
a pipeline. Every eval config here is H1-free and the confirmatory read is left unsubmitted.

Partitions alternate h200/h100: the per-user job cap is enforced PER PARTITION, so spreading
gets more slots than any single queue allows. GPUs are the real scarcity (h200 was 4 free of
52 when this was written), so `--gres=gpu:2` packing is NOT used -- no node had two free
devices and every packed job would have queued forever.

    python scripts/slurm/pipeline_tranches.py --model codellama-7b --dry-run
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBMIT = ROOT / "scripts" / "slurm" / "submit.py"


def sub(name, argv, *, partition, time, dep=None, mem=None, gres=None, dry=False):
    cmd = [sys.executable, str(SUBMIT), "--name", name, "--partition", partition,
           "--time", time]
    if dep:
        d = str(dep)
        if not d.startswith(("afterok:", "afterany:")):
            d = f"afterok:{d}"
        cmd += ["--dependency", d]
    if mem:
        cmd += ["--mem", mem]
    if gres is not None:
        cmd += ["--gres", gres]
    if dry:
        cmd += ["--dry-run"]
    cmd += ["--argv"] + argv
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if dry:
        print(f"  [dry] {name}: {' '.join(argv)}")
        return "DRY"
    for l in (out.stdout or "").splitlines():
        if l.startswith("submitted "):
            j = l.split()[1]
            print(f"  {j}  {name}" + (f"  (after {dep})" if dep else ""))
            return j
    print(f"  FAILED {name}: {out.stdout.strip()} {out.stderr.strip()}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--language", default="python")
    ap.add_argument("--stages", default="I,B,D,H")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    M, L, d = a.model, a.language, a.dry_run
    st = set(a.stages.split(","))
    root = f"runs/adapters/{M}/{L}"
    P = ["h200", "h100"]
    n = [0]

    def part():
        n[0] += 1
        return P[n[0] % 2]

    jid = {}

    if "I" in st:
        print("TRANCHE I — S3/S4 specialists (+ s2fam); also the MoLE experts")
        sel = []
        for c in ["S3", "S4"]:
            p = part()
            t = sub(f"tI_tr_{c}", ["-m", "obtune.train_sft", "--config",
                    f"train/grid_py_{c}.yaml", "--model", M, "--seed", "17"],
                    partition=p, time="03:00:00", dry=d)
            sel.append(sub(f"tI_ck_{c}", ["-m", "obtune.eval_vllm", "--config",
                    f"train/grid_py_{c}.yaml", "--model", M, "--mode", "ckpt-select",
                    "--adapter-root", f"{root}/{c}_r32_s17"],
                    partition=p, time="01:00:00", dep=t, dry=d))
        p = part()
        t = sub("tI_tr_s2fam", ["-m", "obtune.train_sft", "--config",
                "train/s2fam_generic_py.yaml", "--model", M, "--seed", "17"],
                partition=p, time="04:00:00", dry=d)
        # s2fam declares `adapter_root: runs/adapters_curriculum` (inherited from the Qwen
        # config), so its adapter is NOT under runs/adapters/. Verifying adapter_dir(cfg).name
        # alone is not enough -- that checks the leaf and silently accepts the wrong root,
        # which is exactly how this select failed with "no checkpoints under ...".
        sel.append(sub("tI_ck_s2fam", ["-m", "obtune.eval_vllm", "--config",
                "train/s2fam_generic_py.yaml", "--model", M, "--mode", "ckpt-select",
                "--adapter-root",
                f"runs/adapters_curriculum/{M}/{L}/S2-S3-S4_r32_s17"],
                partition=p, time="01:00:00", dep=t, dry=d))
        jid["I"] = [x for x in sel if x]

    if "B" in st:
        print("TRANCHE B — routing / MoLE (needs all 8 experts)")
        dep_I = ":".join(jid.get("I", [])) or None
        # router.features defaults to runs/router/features/router_features.npz with NO model
        # in the name, and train_router to runs/router/router_v1.npz -- so two panels would
        # silently overwrite each other's artifacts. Both paths are passed explicitly and
        # namespaced by (model, language).
        featf = f"runs/router/features/{M}_{L}_router_features.npz"
        routf = f"runs/router/{M}_{L}_router_v1.npz"
        feats = sub("tB_router_feats", ["-m", "obtune.router.features", "--config",
                    "router/router_v1.yaml", "--model", M, "--out", featf],
                    partition=part(), time="02:00:00", dep=dep_I if not d else None, dry=d)
        rt = sub("tB_router_train", ["-m", "obtune.router.train_router", "--config",
                 "router/router_v1.yaml", "--features", featf, "--out", routf],
                 partition="normal", gres="", time="01:00:00", dep=feats, dry=d)
        mt = sub("tB_mole_train", ["-m", "obtune.mole.train_mole", "--config",
                 f"mole/routerlora_{M.replace('-','')}.yaml"],
                 partition=part(), time="08:00:00", dep=dep_I if not d else None, dry=d)
        jid["B"] = sub("tB_mole_eval", ["-m", "obtune.mole.eval_mole", "--config",
                 f"mole/routerlora_{M.replace('-','')}.yaml", "--model", M,
                 "--language", L], partition=part(), time="03:00:00",
                 dep=":".join(x for x in [mt, rt] if x) if not d else None, dry=d)

    if "D" in st:
        print("TRANCHE D — merge sweeps and controls (CPU merges, then one eval)")
        merges = []
        for ct in ["ties", "dare_ties"]:
            for dens in ["0.3", "0.7"]:
                merges.append(sub(f"tD_sweep_{ct}_d{dens.replace('.','p')}",
                    ["-m", "obtune.merge_adapters", "--config", "merge/ties_v1.yaml",
                     "--model", M, "--language", L, "--rank", "32",
                     "--combination-type", ct, "--density", dens, "--out",
                     f"{root}/sweep_{ct}_d{dens.replace('.','p')}_r32_s17"],
                    partition="normal", gres="", mem="200G", time="01:00:00", dry=d))
        jid["D"] = [x for x in merges if x]

    if "H" in st:
        print("TRANCHE H — catastrophic forgetting (CLAUDE.md §4 check 7)")
        for sysname, adir in [("base", None), ("tuned_L0", f"{root}/L0_r32_s17/best"),
                              ("mono_all", f"{root}/L0-L1b-L1r-L2-S1-S2_r32_s17/best")]:
            # forgetting.py labels a run with --tag; there is no --system flag. Passing one
            # would abort with "unrecognized arguments" before loading anything.
            argv = ["-m", "obtune.forgetting", "--model", M, "--language", L,
                    "--tag", sysname]
            if adir:
                argv += ["--adapter", adir]
            sub(f"tH_forget_{sysname}", argv, partition=part(), time="03:00:00", dry=d)

    print("\nDAG submitted. H1 is deliberately NOT in it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
