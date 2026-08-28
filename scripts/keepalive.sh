#!/usr/bin/env bash
# Keep workers alive until an ad-hoc queue drains, then exit. Survives logoff.
#
#   setsid nohup bash scripts/keepalive.sh > runs/logs/keepalive.log 2>&1 < /dev/null &
#   bash scripts/keepalive.sh --status
#
# WHY THIS EXISTS
# ---------------
# Three self-healing components already exist and none of them covers this case:
#   * `pipeline.sh::ensure_infra` relaunches workers, but only while the pipeline is running,
#     and the pipeline exits once its stage list is complete.
#   * `supervise.sh` exits on `! grid_work_left && sweep complete` — it is scoped to the RQ1
#     grid plus the rank sweep, so a queue of any OTHER kind of job (attn, merge, one-off
#     evals) leaves it thinking the work is finished.
#   * `watchdog.sh` restarts `pipeline.sh`, which with all stages done exits immediately.
#
# So a hand-enqueued batch runs on whatever workers happen to be alive, and if one dies the
# rest of the batch silently never runs. Workers are `setsid` with PPID 1 so they survive a
# logout, but nothing restarts them. That is the gap this closes, and only that.
#
# WHAT IT DOES NOT DO. It does not enqueue, choose GPUs, or override policy. Card selection
# stays with `launch_workers.sh` (which honours `scheduler_policy.allowed_gpus` and
# `gpu_budget`) and the per-GPU idle check in `sched/worker.py` (>2 GB or >5 % util = refuse),
# which is what keeps us off a borrower's card. Raising the budget is still a config edit.
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

Q=runs/manifest/queued
R=runs/manifest/running
LOCK=runs/manifest/.keepalive.lock
INTERVAL="${INTERVAL:-60}"
IDLE_EXIT="${IDLE_EXIT:-3}"     # consecutive empty polls before declaring the batch done

say() { echo "[$(date '+%F %T')] $*"; }
n_queued()  { ls "$Q" 2>/dev/null | grep -c . || true; }
n_running() { ls "$R"/*/*.json 2>/dev/null | grep -c . || true; }

if [ "${1:-}" = "--status" ]; then
  echo "queued=$(n_queued) running=$(n_running)"
  [ -f "$LOCK" ] && echo "keepalive pid=$(cat "$LOCK") alive=$(kill -0 "$(cat "$LOCK")" 2>/dev/null && echo yes || echo no)" \
                 || echo "keepalive: not running"
  bash scripts/launch_workers.sh --status 2>/dev/null | grep -E "gpu[0-9]:"
  exit 0
fi

# Same lock discipline as supervise.sh: a second copy would double-launch workers.
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then
  say "another keepalive is alive (pid $(cat "$LOCK")) — exiting"; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

say "keepalive up (interval ${INTERVAL}s, exit after ${IDLE_EXIT} empty polls)"
empty=0
while true; do
  bash scripts/launch_workers.sh >/dev/null 2>&1 || true

  # Recover claims held by a worker that has died. `is_orphaned` defaults to NOT-orphaned on
  # any uncertainty, so this cannot relaunch a job that is still running.
  for f in runs/manifest/workers/*.pid; do
    [ -e "$f" ] || continue
    tag=$(basename "$f" .pid)
    kill -0 "$(cat "$f")" 2>/dev/null && continue
    say "worker $tag is dead — requeuing anything it still held"
    python -m obtune.sched.worker --requeue-stale --gpu-tag "$tag" >/dev/null 2>&1 || true
  done

  q=$(n_queued); r=$(n_running)
  if [ "$q" -eq 0 ] && [ "$r" -eq 0 ]; then
    empty=$((empty + 1))
    say "queue empty (${empty}/${IDLE_EXIT})"
    if [ "$empty" -ge "$IDLE_EXIT" ]; then
      say "batch drained — done=$(ls runs/manifest/done 2>/dev/null | wc -l) failed=$(ls runs/manifest/failed 2>/dev/null | wc -l); exiting"
      exit 0
    fi
  else
    # A single empty poll can be a worker between claims, so the counter resets rather than
    # latching; only IDLE_EXIT consecutive empties end the batch.
    [ "$empty" -gt 0 ] && say "work reappeared (queued=$q running=$r) — resetting idle counter"
    empty=0
  fi
  sleep "$INTERVAL"
done
