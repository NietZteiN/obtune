#!/usr/bin/env bash
# Restart pipeline.sh if it dies while stages remain.
#
#   setsid nohup bash scripts/watchdog.sh > runs/logs/watchdog.log 2>&1 < /dev/null &
#   bash scripts/watchdog.sh --status
#
# WHY THIS EXISTS
# ---------------
# Every other component already self-heals, and `ensure_infra` is what does it: workers are
# relaunched by launch_workers.sh, the supervisor is restarted when pgrep finds none,
# stranded claims are swept by `worker --sweep-orphans`, and stranded GPUs by
# `worker --reap-stranded-gpus`. But `ensure_infra` runs *inside* pipeline.sh — so the one
# process that heals everything else has nothing healing it. If it dies overnight (OOM, a
# bug in a stage, an accidental kill) the remaining stages never run and nothing notices
# until a human looks. That is the last single point of failure in the unattended chain.
#
# WHY BLIND RESTART IS SAFE
# -------------------------
# pipeline.sh takes a lock and exits immediately if a live pipeline already holds it, and
# every stage is guarded by a `.done` marker, so restarting is idempotent: completed stages
# are skipped and each underlying step resumes (train_sft skips a finished adapter,
# eval_vllm skips a written cell, the emitters overwrite deterministically).
#
# WHAT IT DELIBERATELY WILL NOT DO
# --------------------------------
# It does not restart a pipeline that exited because it FINISHED — that would loop forever
# re-running a completed programme. And it stops after MAX_RESTARTS consecutive failures,
# because a pipeline that dies immediately on every start is broken in a way a restart loop
# cannot fix and should not obscure. Both conditions are logged rather than silent.
set -uo pipefail
cd "$(dirname "$0")/.."

INTERVAL="${INTERVAL:-300}"          # seconds between checks
MAX_RESTARTS="${MAX_RESTARTS:-20}"
STATE=runs/manifest/.pipeline
LOG=runs/logs/watchdog.log
mkdir -p "$STATE" runs/logs

say() { echo "[$(date -u +%F' '%H:%M:%S)] watchdog: $*"; }

# The stage list is defined in pipeline.sh; read it from there so the two cannot drift.
stages_all() { sed -n 's/^STAGES_ALL="\(.*\)"$/\1/p' scripts/pipeline.sh; }

# Returns the number of stages still pending, or -1 if the list could NOT be read.
#
# The distinction is load-bearing. An empty list used to be indistinguishable from "every
# stage is finished", so a single unreadable read — pipeline.sh mid-write (writes are not
# atomic, and it is edited often), truncated, or momentarily absent — made the watchdog
# announce completion and exit, silently disabling the last safety net at the exact moment
# the pipeline was most likely to need it. "I cannot tell" must never be reported as "done".
stages_remaining() {
  local n=0 total=0 s
  for s in $(stages_all); do
    total=$((total + 1))
    [ -f "$STATE/$s.done" ] || n=$((n + 1))
  done
  if [ "$total" -eq 0 ]; then echo -1; else echo "$n"; fi
}

pipeline_alive() { pgrep -f 'bash scripts/pipeline.sh$' >/dev/null 2>&1; }

if [ "${1:-}" = "--status" ]; then
  echo "watchdog:  $(pgrep -f 'bash scripts/watchdog.sh$' | grep -v $$ | wc -l) process(es)"
  echo "pipeline:  $(pipeline_alive && echo ALIVE || echo DEAD)"
  _r=$(stages_remaining)
  if [ "$_r" -lt 0 ]; then echo "stages remaining: UNREADABLE (pipeline.sh)"; else echo "stages remaining: $_r"; fi
  exit 0
fi

# Single instance, same pattern as the pipeline's own lock.
LOCK="$STATE/.watchdog.lock"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  say "another watchdog is alive (pid $(cat "$LOCK")) — exiting"; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

say "started (interval ${INTERVAL}s, max ${MAX_RESTARTS} restarts)"
restarts=0
while true; do
  remaining=$(stages_remaining)

  if [ "$remaining" -lt 0 ]; then
    say "WARNING: could not read STAGES_ALL from scripts/pipeline.sh — keeping watch anyway."
    say "         (an unreadable stage list is NOT evidence that the work is finished)"
  elif [ "$remaining" -eq 0 ]; then
    say "all stages complete — nothing left to supervise, exiting"
    exit 0
  fi

  if ! pipeline_alive; then
    if [ "$restarts" -ge "$MAX_RESTARTS" ]; then
      say "pipeline dead and already restarted ${restarts}x — NOT restarting again."
      say "  $remaining stage(s) still pending. This needs a human: see runs/logs/pipeline.log"
      exit 1
    fi
    restarts=$((restarts + 1))
    say "pipeline is DEAD with $remaining stage(s) pending — restart #${restarts}"
    # A pipeline killed without running its EXIT trap leaves the lock behind; the pipeline's
    # own check tolerates a stale lock, but clearing it keeps the log honest.
    [ -f "$STATE/.lock" ] && ! kill -0 "$(cat "$STATE/.lock" 2>/dev/null)" 2>/dev/null \
      && rm -f "$STATE/.lock"
    setsid nohup bash scripts/pipeline.sh >> runs/logs/pipeline.log 2>&1 < /dev/null &
    disown 2>/dev/null || true
    sleep 30
    if pipeline_alive; then say "  restart OK"; else say "  restart FAILED to take"; fi
  fi

  sleep "$INTERVAL"
done
