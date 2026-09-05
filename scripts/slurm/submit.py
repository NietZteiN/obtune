#!/usr/bin/env python3
"""Submit obtune jobs to SLURM. Replaces src/obtune/sched/ on juno.

WHY THIS EXISTS. On csr-94608 there was no scheduler, so the project grew its own:
`sched/worker.py` polled nvidia-smi for an idle card, claimed it under a budget in
configs/compute.yaml, pinned CUDA_VISIBLE_DEVICES before importing torch, and ran
one tmux session per GPU under a supervisor. Every part of that solves a problem
SLURM already solves — allocation, isolation, device pinning, requeue, accounting —
and two of them (the idle check, the shared-uid ownership test) exist only because
a borrower shared the Unix account. None of that is true here.

WHAT IS KEPT. The job manifest is the project's provenance layer, not scheduler
scaffolding: runs/manifest/{queued,running,done,failed} is how a result is traced
back to the argv that produced it, and build_manifest.py emits into it. So the
lifecycle is preserved exactly, and the state transitions happen INSIDE the sbatch
script rather than in a polling worker. A job that never starts stays queued; a job
that dies leaves its record in failed/ with the SLURM id attached.

Usage:
    python scripts/slurm/submit.py --queued                  # submit everything queued
    python scripts/slurm/submit.py --queued --dry-run        # print the sbatch, submit nothing
    python scripts/slurm/submit.py --name smoke --argv scripts/smoke_env.py
                                   # NOTE: --argv is greedy (REMAINDER) -- it must come LAST,
                                   # or the flags after it are passed to the job, not to this script
    python scripts/slurm/submit.py --job runs/manifest/queued/foo.json --partition h100
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from obtune.config import PROJECT_ROOT, RUNS_DIR, load_config  # noqa: E402
from obtune.sched.worker import DONE, FAILED, QUEUED, RUNNING, Job  # noqa: E402

SLURM_DIR = RUNS_DIR / "slurm"
SLURM_LOGS = RUNS_DIR / "logs" / "slurm"

# The sbatch body. Three things are load-bearing:
#   1. `source scripts/env.sh` is what puts $OBTUNE_ENV/bin on PATH. Invoking the
#      interpreter by absolute path instead makes vLLM engine startup die with a bare
#      FileNotFoundError: 'ninja' from a child process (see the comment in env.sh).
#   2. The manifest moves happen here, so they reflect when the job ACTUALLY ran,
#      not when it was submitted. A job pending in the queue is still `queued/`.
#   3. `trap` on EXIT, not an `if` after the command, so a walltime kill or a node
#      failure still files the job under failed/ instead of stranding it in running/.
#      The old scheduler's headline defect was exactly this: a worker that died
#      mid-run left its claim in running/ forever and nothing noticed.
TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
{gres_line}#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
{qos}{extra_sbatch}{dependency}#SBATCH --output={log_dir}/%j_{job_name}.out
#SBATCH --error={log_dir}/%j_{job_name}.out
set -uo pipefail

OBTUNE_ROOT={root}
source "$OBTUNE_ROOT/scripts/env.sh"
cd "$OBTUNE_ROOT"

MANIFEST_SRC={manifest_src}
RUN_DIR="$OBTUNE_ROOT/runs/manifest/running/slurm-$SLURM_JOB_ID"
DONE_DIR="$OBTUNE_ROOT/runs/manifest/done"
FAIL_DIR="$OBTUNE_ROOT/runs/manifest/failed"
MANIFEST_NAME={manifest_name}

if [[ -n "$MANIFEST_SRC" && -f "$MANIFEST_SRC" ]]; then
  mkdir -p "$RUN_DIR"
  mv "$MANIFEST_SRC" "$RUN_DIR/$MANIFEST_NAME"
  CLAIM="$RUN_DIR/$MANIFEST_NAME"
else
  CLAIM=""
fi

finish() {{
  rc=$?
  if [[ -n "$CLAIM" && -f "$CLAIM" ]]; then
    if [[ $rc -eq 0 ]]; then dest="$DONE_DIR"; else dest="$FAIL_DIR"; fi
    mkdir -p "$dest"
    python - "$CLAIM" "$dest/$MANIFEST_NAME" "$rc" <<'EOF'
import json, os, sys, datetime
src, dst, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = json.load(open(src))
d.setdefault("slurm", {{}}).update({{
    "job_id": os.environ.get("SLURM_JOB_ID"),
    "node": os.environ.get("SLURMD_NODENAME"),
    "partition": os.environ.get("SLURM_JOB_PARTITION"),
    "exit_code": rc,
    "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}})
json.dump(d, open(dst, "w"), indent=2)
os.remove(src)
EOF
    rmdir "$RUN_DIR" 2>/dev/null || true
  fi
  exit $rc
}}
trap finish EXIT

echo "# obtune slurm job $SLURM_JOB_ID on $SLURMD_NODENAME ($SLURM_JOB_PARTITION)"
echo "# started $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader || true
echo "# argv: {argv_display}"
echo

{command}
"""


def _defaults() -> dict:
    cfg = load_config("compute.yaml").get("slurm", {}) or {}
    d = dict(cfg.get("defaults", {}) or {})
    d.setdefault("partition", cfg.get("default_partition", "h200"))
    d.setdefault("gres", "gpu:1")
    d.setdefault("cpus_per_task", 8)
    d.setdefault("mem", "64G")
    d.setdefault("time", "08:00:00")
    return d


def _walltime(job: Job | None, override: str | None, default: str) -> str:
    if override:
        return override
    if job is None:
        return default
    # Twice the estimate, floored at one hour and capped at the partition maximum.
    # Over-asking costs queue position, under-asking costs the whole run, and the
    # old estimates were calibrated on A6000s -- slower than anything here.
    hours = max(1, min(47, math.ceil(job.est_gpu_h * 2)))
    return f"{hours:02d}:00:00"


def build_script(argv: list[str], *, job_name: str, manifest_src: Path | None,
                 partition: str, gres: str, cpus: int, mem: str, time: str,
                 nodelist: str | None = None, exclude: str | None = None,
                 dependency: str | None = None, qos: str | None = None) -> str:
    command = "python " + " ".join(shlex.quote(a) for a in argv)
    # Node selection is not cosmetic on juno: `h100` is heterogeneous and g-06-01
    # advertises 3g.47gb MIG slices, not whole cards. On 2026-08-28 the alignment
    # lambda-sweep's mismatch control ran 2.03 s/it on g-04-02 and 5.7 s/it on
    # g-06-01, and the lambda=10 cell died at 217/222 steps on walltime -- a result
    # lost to node assignment, which read as a lambda effect. Pin or exclude.
    # Dependencies are what make an unattended pipeline possible: a stage that must not
    # start until its inputs exist (train -> ckpt-select -> eval) is expressed to SLURM
    # rather than by a process sitting in a loop waiting. `afterok` means a failed stage
    # leaves everything downstream PENDING with DependencyNeverSatisfied instead of running
    # on missing inputs -- which is the behaviour we want, since an eval whose adapter never
    # trained would otherwise silently score the base model.
    # The h200 partition carries QoS=juno, whose MaxJobsPU=4 is what caps concurrency --
    # NOT our account, which is on `normal` with no limit. `high-throughput` has the
    # OverPartQOS flag and MaxJobsPU=8, so it overrides the partition cap and doubles the
    # number of jobs we can hold. `large` (150) looks better but lacks OverPartQOS, so the
    # partition's 4 still binds. `juno-pri` is also 8 but carries Priority=200000 against
    # the default 1 -- it would jump every other user on a shared cluster for the same
    # throughput, so it is deliberately not the default.
    q = f"#SBATCH --qos={qos}\n" if qos else ""
    dep = f"#SBATCH --dependency={dependency}\n" if dependency else ""
    extra = ""
    if nodelist:
        extra += f"#SBATCH --nodelist={nodelist}\n"
    if exclude:
        extra += f"#SBATCH --exclude={exclude}\n"
    return TEMPLATE.format(
        job_name=job_name,
        partition=partition,
        # `--gres none` (or empty) drops the line: the CPU partitions (`normal`, `dev`)
        # reject any --gres=gpu request with "Requested node configuration is not available".
        gres_line=("" if gres in ("", "none", "0") else f"#SBATCH --gres={gres}\n"),
        cpus=cpus,
        mem=mem,
        time=time,
        qos=q,
        extra_sbatch=extra,
        dependency=dep,
        log_dir=shlex.quote(str(SLURM_LOGS)),
        root=shlex.quote(str(PROJECT_ROOT)),
        manifest_src=shlex.quote(str(manifest_src) if manifest_src else ""),
        manifest_name=shlex.quote(manifest_src.name if manifest_src else ""),
        argv_display=" ".join(argv).replace("{", "{{").replace("}", "}}"),
        command=command,
    )


def submit(script: str, name: str, dry_run: bool) -> str | None:
    SLURM_DIR.mkdir(parents=True, exist_ok=True)
    SLURM_LOGS.mkdir(parents=True, exist_ok=True)
    # The sbatch files ARE the provenance record (they carry the exact argv, and they are
    # committed). Two jobs sharing a --name would otherwise have the second silently
    # overwrite the first's script on disk, leaving a committed record that describes the
    # wrong run -- SLURM itself is unaffected, since it stores the script at submit time, so
    # the corruption is invisible until someone reads runs/slurm/ to find out what ran.
    path = SLURM_DIR / f"{name}.sbatch"
    if path.exists() and path.read_text() != script:
        n = 2
        while (SLURM_DIR / f"{name}.{n}.sbatch").exists():
            n += 1
        path = SLURM_DIR / f"{name}.{n}.sbatch"
        print(f"note: {name}.sbatch exists with different content; wrote {path.name}",
              file=sys.stderr)
    path.write_text(script)
    path.chmod(0o755)
    if dry_run:
        print(f"--- {path} (not submitted) ---\n{script}")
        return None
    out = subprocess.run(["sbatch", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        print(f"sbatch FAILED for {name}: {out.stderr.strip()}", file=sys.stderr)
        return None
    jid = out.stdout.strip().split()[-1]
    print(f"submitted {jid}  {name}")
    return jid


def main() -> int:
    d = _defaults()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--queued", action="store_true",
                     help="submit every job in runs/manifest/queued/, priority order")
    src.add_argument("--job", type=Path, help="submit one job manifest")
    src.add_argument("--argv", nargs=argparse.REMAINDER,
                     help="ad-hoc: everything after this is passed to the project python")
    ap.add_argument("--partition", default=d["partition"])
    ap.add_argument("--gres", default=d["gres"])
    ap.add_argument("--cpus", type=int, default=d["cpus_per_task"])
    ap.add_argument("--mem", default=d["mem"])
    ap.add_argument("--time", default=None, help=f"walltime (default: 2x est_gpu_h, else {d['time']})")
    ap.add_argument("--qos", default="high-throughput",
                    help="SLURM QOS. Default high-throughput (MaxJobsPU=8, OverPartQOS, "
                         "priority 0). Pass '' to take the partition default (juno, cap 4).")
    ap.add_argument("--dependency", default=None,
                    help="SLURM dependency spec, e.g. afterok:12345 or afterok:12345:12346")
    ap.add_argument("--nodelist", default=None,
                    help="restrict to these nodes (e.g. g-04-02, the only full-fat h100)")
    ap.add_argument("--exclude", default=None,
                    help="never place on these nodes (e.g. g-06-01, which is MIG slices)")
    ap.add_argument("--limit", type=int, default=None, help="submit at most N queued jobs")
    ap.add_argument("--name", default="adhoc", help="job name for --argv submissions")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.argv:
        script = build_script(a.argv, job_name=a.name, manifest_src=None,
                              partition=a.partition, gres=a.gres, cpus=a.cpus,
                              mem=a.mem, time=a.time or d["time"],
                              nodelist=a.nodelist, exclude=a.exclude,
                              dependency=a.dependency, qos=a.qos or None)
        return 0 if submit(script, a.name, a.dry_run) or a.dry_run else 1

    paths = [a.job] if a.job else sorted(QUEUED.glob("*.json")) if QUEUED.exists() else []
    if not paths:
        print("nothing queued")
        return 0
    jobs = [(Job.load(p), p) for p in paths]
    jobs.sort(key=lambda t: (t[0].priority, t[0].job_id))  # lower priority runs first
    if a.limit:
        jobs = jobs[: a.limit]

    n = 0
    for job, path in jobs:
        if job.raw:
            print(f"skip {job.job_id}: raw=True jobs exec a shell command, not the "
                  f"project python -- submit it by hand", file=sys.stderr)
            continue
        script = build_script(job.argv, job_name=job.job_id[:60], manifest_src=path,
                              partition=a.partition, gres=a.gres, cpus=a.cpus, mem=a.mem,
                              time=_walltime(job, a.time, d["time"]),
                              nodelist=a.nodelist, exclude=a.exclude,
                              dependency=a.dependency, qos=a.qos or None)
        if submit(script, job.job_id, a.dry_run):
            n += 1
    print(f"{n}/{len(jobs)} submitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
