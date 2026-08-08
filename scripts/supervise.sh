#!/usr/bin/env bash
# Keep the overnight work alive without a human present.
#
# Detachment alone is not enough. Every process here already runs under setsid with
# PPID 1, yet the tmux server died twice today and took its children with it, costing
# ~4 idle GPU-hours before anyone noticed. This watchdog closes that gap: it re-launches
# whatever has died, requeues jobs orphaned by a dead worker, and exits by itself when
# all the work is genuinely finished.
#
#   setsid nohup bash scripts/supervise.sh > runs/logs/supervisor.log 2>&1 < /dev/null &
#   bash scripts/supervise.sh --status
#
# Safe to run more than once: it takes a lock, and everything it starts is idempotent
# (train_sft skips a finished adapter, eval_vllm skips a written cell).
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

GRID_GPUS="${GRID_GPUS:-2 3}"
SWEEP_GPUS="${SWEEP_GPUS:-0 1}"
INTERVAL="${INTERVAL:-300}"
LOG=runs/logs/supervisor.log
LOCK=runs/manifest/.supervisor.lock
SWEEP_DONE=results/analysis/rank_sweep.json
mkdir -p runs/logs runs/manifest

say() { echo "[$(date -u +%F' '%H:%M:%S)] $*" | tee -a "$LOG"; }

if [ "${1:-}" = "--status" ]; then
  echo "supervisor: $(pgrep -f 'supervise.sh' | grep -v $$ | wc -l) process(es)"
  bash scripts/launch_workers.sh --status
  echo "sweep: $([ -f "$SWEEP_DONE" ] && echo COMPLETE || echo running/pending)"
  for d in runs/adapters/qwen25c-1.5b/python/*_r{64,128,192}_s17; do
    [ -d "$d" ] && echo "  $(basename "$d"): $([ -d "$d/final" ] && echo trained || echo training)"
  done
  exit 0
fi

# Single instance, and a stale lock from a killed supervisor must not block forever.
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  say "another supervisor is alive (pid $(cat "$LOCK")) — exiting"; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

say "=== supervisor start (grid: $GRID_GPUS | sweep: $SWEEP_GPUS | every ${INTERVAL}s) ==="

requeue_orphans() {
  # A worker that dies mid-job leaves its claim in running/<tag>/. Nothing else ever
  # moves it back, so those jobs would be silently lost from the run.
  local n=0
  for dir in runs/manifest/running/*/; do
    [ -d "$dir" ] || continue
    local tag; tag=$(basename "$dir")
    pgrep -f "obtune.sched.worker --gpu-tag $tag\b" >/dev/null 2>&1 && continue
    for f in "$dir"*.json; do
      [ -e "$f" ] || continue
      mv "$f" runs/manifest/queued/ && n=$((n+1))
    done
  done
  [ "$n" -gt 0 ] && say "requeued $n job(s) orphaned by a dead worker"
  return 0
}

grid_work_left() {
  local q r
  q=$(ls runs/manifest/queued 2>/dev/null | wc -l)
  r=$(find runs/manifest/running -name '*.json' 2>/dev/null | wc -l)
  [ $((q + r)) -gt 0 ]
}

while true; do
  # --- grid ---------------------------------------------------------------- #
  if grid_work_left; then
    requeue_orphans
    for g in $GRID_GPUS; do
      if ! pgrep -f "obtune.sched.worker --gpu-tag gpu${g}\b" >/dev/null 2>&1; then
        say "worker gpu${g} is not running — relaunching"
        bash scripts/launch_workers.sh "$g" >> "$LOG" 2>&1
      fi
    done
  fi

  # --- rank sweep ---------------------------------------------------------- #
  if [ ! -f "$SWEEP_DONE" ]; then
    if ! pgrep -f "run_rank_sweep.sh" >/dev/null 2>&1; then
      say "rank sweep is not running and not complete — relaunching on $SWEEP_GPUS"
      # shellcheck disable=SC2086
      setsid nohup bash scripts/run_rank_sweep.sh $SWEEP_GPUS \
        >> runs/logs/rank_sweep_outer.log 2>&1 < /dev/null &
      disown 2>/dev/null || true
    fi
  fi

  # --- done? --------------------------------------------------------------- #
  if ! grid_work_left && [ -f "$SWEEP_DONE" ]; then
    say "grid queue empty and rank sweep complete — supervisor exiting"
    say "  done=$(ls runs/manifest/done 2>/dev/null | wc -l) failed=$(ls runs/manifest/failed 2>/dev/null | wc -l)"
    exit 0
  fi

  sleep "$INTERVAL"
done
