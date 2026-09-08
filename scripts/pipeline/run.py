#!/usr/bin/env python3
"""End-to-end autonomous pipeline: a declarative DAG of SLURM jobs.

WHY THIS EXISTS. The paper plan (docs/PAPER_EXPERIMENTS.md, docs/RQ_SUMMARY.md §6) is ~30
stages across build -> train -> ckpt-select -> eval -> analysis -> report, with real
dependencies between them and hours of queue wait between each. Submitting them by hand,
one per queue cycle, is how a week disappears. This turns the plan into ONE file
(plan.yaml) and ONE command, and lets SLURM do the waiting:

    python scripts/pipeline/run.py                # submit every stage that is not done/queued
    python scripts/pipeline/run.py --status       # table: stage / job / state / elapsed
    python scripts/pipeline/run.py --dry-run      # print what would be submitted
    python scripts/pipeline/run.py --only NAME    # (re)submit one stage (+ nothing else)
    python scripts/pipeline/run.py --rq "RQ1'"    # only the stages tagged for one RQ
    python scripts/pipeline/run.py --report       # results/analysis/pipeline_report_<date>.md

DESIGN.
  * Every stage is an sbatch built by scripts/slurm/submit.py (same template, same manifest
    lifecycle, same logs), so nothing here bypasses the provenance layer.
  * Dependencies are expressed to SLURM as `afterok:<jobid>...`. A failed stage leaves its
    descendants PENDING with DependencyNeverSatisfied, which `--sync` detects, cancels (ONLY
    pipeline-owned job ids -- never anything else in the user's queue) and marks `blocked`.
    A gate stage (E5b's power gate) uses exactly this: it exits non-zero when the gate fails
    and the training it guards never runs.
  * Idempotent. State lives in runs/pipeline/state.json (stage -> job id / status). A stage
    is skipped when its `done_when` files exist or its job is queued/running/completed; a
    stage whose job FAILED/TIMEOUT/CANCELLED is resubmitted. So the same command is safe to
    run every morning, and a partial failure is repaired by fixing the cause and re-running.
  * Decision rules are NOT here. They live in the analysis scripts each stage calls, frozen
    in CLAUDE_SCRATCHPAD.md before submission. The pipeline sequences; it does not judge.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "slurm"))

from submit import build_script, submit  # noqa: E402  (scripts/slurm/submit.py)

PLAN = ROOT / "scripts" / "pipeline" / "plan.yaml"
STATE = ROOT / "runs" / "pipeline" / "state.json"
LOGS = ROOT / "runs" / "logs" / "slurm"

LIVE = {"PENDING", "RUNNING", "COMPLETING", "CONFIGURING", "SUSPENDED", "REQUEUED"}
DEAD = {"FAILED", "TIMEOUT", "CANCELLED", "NODE_FAIL", "OUT_OF_MEMORY", "PREEMPTED", "BOOT_FAIL", "DEADLINE"}


# ----------------------------------------------------------------------------- state
def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"stages": {}}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True))


def load_plan(path: Path = PLAN) -> dict:
    plan = yaml.safe_load(path.read_text())
    names = [s["name"] for s in plan["stages"]]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        raise SystemExit(f"duplicate stage names: {sorted(dup)}")
    known = set(names) | {f"ext:{k}" for k in (plan.get("external_jobs") or {})}
    for s in plan["stages"]:
        for d in s.get("deps", []):
            if d not in known:
                raise SystemExit(f"stage {s['name']}: unknown dep {d!r}")
    return plan


# ----------------------------------------------------------------------------- slurm
def sacct(job_ids: list[str]) -> dict[str, dict]:
    """job id -> {state, elapsed}. Missing ids (not yet in accounting) are absent."""
    ids = [j for j in job_ids if j]
    if not ids:
        return {}
    out = subprocess.run(
        ["sacct", "-j", ",".join(ids), "-X", "-n", "-P", "-o", "JobID,State,ElapsedRaw,Reason"],
        capture_output=True, text=True)
    res: dict[str, dict] = {}
    for line in out.stdout.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        jid, state, el = parts[0], parts[1].split()[0], parts[2]
        res[jid] = {"state": state, "elapsed": int(el or 0), "reason": parts[3] if len(parts) > 3 else ""}
    return res


def squeue_reasons(job_ids: list[str]) -> dict[str, str]:
    ids = [j for j in job_ids if j]
    if not ids:
        return {}
    out = subprocess.run(["squeue", "-h", "-j", ",".join(ids), "-o", "%i|%r"],
                         capture_output=True, text=True)
    res = {}
    for line in out.stdout.splitlines():
        if "|" in line:
            jid, reason = line.split("|", 1)
            res[jid] = reason
    return res


def scancel(job_id: str) -> None:
    subprocess.run(["scancel", job_id], capture_output=True, text=True)


# ----------------------------------------------------------------------------- done-ness
def files_exist(paths: list[str]) -> bool:
    if not paths:
        return False
    for p in paths:
        pp = ROOT / p
        if "*" in p:
            if not list(ROOT.glob(p)):
                return False
        elif not pp.exists():
            return False
    return True


def sync(plan: dict, st: dict) -> None:
    """Refresh every recorded job's SLURM state; cancel DependencyNeverSatisfied orphans."""
    stages = st["stages"]
    ids = [v.get("job_id") for v in stages.values() if v.get("job_id")]
    ext = plan.get("external_jobs") or {}
    acct = sacct(ids + [str(j) for j in ext.values()])
    reasons = squeue_reasons(ids)
    for name, rec in stages.items():
        jid = rec.get("job_id")
        if not jid:
            continue
        a = acct.get(jid)
        if a:
            rec["slurm_state"] = a["state"]
            rec["elapsed_s"] = a["elapsed"]
        if reasons.get(jid) == "DependencyNeverSatisfied":
            scancel(jid)
            rec["slurm_state"] = "CANCELLED"
            rec["status"] = "blocked"
            rec["note"] = "upstream failed; cancelled by run.py --sync"
            continue
        state = rec.get("slurm_state", "")
        if state == "COMPLETED":
            rec["status"] = "done"
        elif state in LIVE:
            rec["status"] = "queued" if state == "PENDING" else "running"
        elif state in DEAD or state.startswith("CANCELLED"):
            rec["status"] = "failed"
    st["external"] = {k: acct.get(str(v), {}).get("state", "UNKNOWN") for k, v in ext.items()}
    # file-level done-ness beats accounting: a stage whose outputs exist is done even if its
    # job record was lost (e.g. produced by a hand-submitted job before the pipeline existed)
    for s in plan["stages"]:
        if files_exist(s.get("done_when", [])):
            stages.setdefault(s["name"], {})["status"] = "done"
            stages[s["name"]].setdefault("note", "outputs present")


# ----------------------------------------------------------------------------- submit
def topo(stages: list[dict]) -> list[dict]:
    by = {s["name"]: s for s in stages}
    seen: dict[str, int] = {}
    order: list[dict] = []

    def visit(n: str, path: tuple = ()) -> None:
        if seen.get(n) == 2:
            return
        if seen.get(n) == 1:
            raise SystemExit(f"cycle: {' -> '.join(path + (n,))}")
        seen[n] = 1
        for d in by[n].get("deps", []):
            if not d.startswith("ext:"):
                visit(d, path + (n,))
        seen[n] = 2
        order.append(by[n])

    for s in stages:
        visit(s["name"])
    return order


def resources(plan: dict, s: dict) -> dict:
    kind = s.get("kind", "gpu")
    r = dict(plan["defaults"][kind])
    r.update(s.get("resources", {}))
    return r


def submit_stage(plan: dict, st: dict, s: dict, dep_ids: list[str], dry: bool) -> str | None:
    r = resources(plan, s)
    dep = None
    if dep_ids:
        dep = f"{s.get('dep_type', 'afterok')}:" + ":".join(dep_ids)
    script = build_script([str(a) for a in s["argv"]], job_name=s["name"], manifest_src=None,
                          partition=r["partition"], gres=r["gres"], cpus=int(r["cpus"]),
                          mem=r["mem"], time=r["time"], dependency=dep,
                          qos=r.get("qos", "high-throughput") or None,
                          exclude=r.get("exclude"), nodelist=r.get("nodelist"))
    if dry:
        print(f"  would submit {s['name']:<28} {r['partition']:<7} {r['gres']:<7} {r['time']}  dep={dep or '-'}")
        print("     python " + " ".join(str(a) for a in s["argv"]))
        # placeholder id so downstream stages resolve in the same dry pass (never saved)
        st["stages"][s["name"]] = {"job_id": f"DRY:{s['name']}", "status": "queued", "dry": True}
        return None
    jid = submit(script, s["name"], dry_run=False)
    if jid:
        st["stages"][s["name"]] = {"job_id": jid, "status": "queued", "slurm_state": "PENDING",
                                   "submitted_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                   "dependency": dep, "rq": s.get("rq")}
        print(f"  submitted {s['name']:<28} job {jid}  dep={dep or '-'}")
    return jid


def run(plan: dict, st: dict, only: set[str] | None, rq: str | None, dry: bool) -> None:
    order = topo(plan["stages"])
    ext = plan.get("external_jobs") or {}
    ext_state = st.get("external", {})
    n_sub = 0
    gpu_h = 0.0
    for s in order:
        name = s["name"]
        rec = st["stages"].get(name, {})
        if only is not None and name not in only:
            continue
        if rq is not None and only is None and s.get("rq") != rq:
            continue
        if not s.get("enabled", True):
            continue
        if rec.get("status") in {"done", "queued", "running"} and only is None:
            continue
        # resolve dependencies: a done dep needs no SLURM dependency; a live one contributes
        # its job id; a missing/failed one blocks submission of this stage (it will be
        # picked up on the next run, once the dep has been (re)submitted)
        dep_ids: list[str] = []
        blocked = None
        for d in s.get("deps", []):
            if d.startswith("ext:"):
                k = d[4:]
                if ext_state.get(k) == "COMPLETED":
                    continue
                if ext_state.get(k, "UNKNOWN") in LIVE:
                    dep_ids.append(str(ext[k]))
                    continue
                blocked = f"external {k} is {ext_state.get(k, 'UNKNOWN')}"
                break
            drec = st["stages"].get(d, {})
            if drec.get("status") == "done":
                continue
            if drec.get("status") in {"queued", "running"} and drec.get("job_id"):
                dep_ids.append(drec["job_id"])
                continue
            # dep is being submitted in this same pass: it now has a job id in state
            if drec.get("job_id") and drec.get("status") == "queued":
                dep_ids.append(drec["job_id"])
                continue
            blocked = f"dep {d} is {drec.get('status', 'unsubmitted')}"
            break
        if blocked:
            print(f"  skip      {name:<28} ({blocked})")
            continue
        submit_stage(plan, st, s, dep_ids, dry)
        n_sub += 1
        if s.get("kind", "gpu") == "gpu":
            h, m, *_ = resources(plan, s)["time"].split(":")
            gpu_h += int(h) + int(m) / 60
        if not dry:
            save_state(st)
    print(f"\n{n_sub} stage(s) {'would be ' if dry else ''}submitted; requested GPU walltime ~{gpu_h:.1f} h")


# ----------------------------------------------------------------------------- status
def status(plan: dict, st: dict) -> None:
    print(f"{'stage':<28} {'rq':<6} {'job':>7} {'status':<9} {'slurm':<10} {'elapsed':>8}  note")
    for s in plan["stages"]:
        rec = st["stages"].get(s["name"], {})
        el = rec.get("elapsed_s")
        el_s = f"{el // 3600}h{(el % 3600) // 60:02d}m" if isinstance(el, int) else ""
        note = rec.get("note", "")
        if rec.get("status") == "failed" and rec.get("job_id"):
            logs = sorted(LOGS.glob(f"{rec['job_id']}_*.out"))
            if logs:
                tail = logs[-1].read_text(errors="replace").strip().splitlines()
                note = (tail[-1][:80] if tail else "") or note
        en = "" if s.get("enabled", True) else "(disabled) "
        print(f"{s['name']:<28} {s.get('rq', ''):<6} {rec.get('job_id', ''):>7} "
              f"{rec.get('status', '-'):<9} {rec.get('slurm_state', ''):<10} {el_s:>8}  {en}{note}")
    ext = st.get("external", {})
    if ext:
        print("\nexternal: " + ", ".join(f"{k}={v}" for k, v in ext.items()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None, help="(re)submit exactly these stages")
    ap.add_argument("--rq", default=None, help="restrict submission to stages tagged with this RQ")
    ap.add_argument("--no-sync", action="store_true")
    a = ap.parse_args()

    plan = load_plan(a.plan)
    st = load_state()
    if not a.no_sync:
        sync(plan, st)
        save_state(st)
    if a.status:
        status(plan, st)
        return 0
    if a.report:
        from report import write_report  # noqa: E402  (scripts/pipeline/report.py)
        print(write_report(plan, st))
        return 0
    run(plan, st, set(a.only) if a.only is not None else None, a.rq, a.dry_run)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
