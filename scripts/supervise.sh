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

# obtune holds at most this many GPUs at once, and follows whatever is FREE rather
# than being pinned to fixed indices — a neighbour can claim a card at any time, and a
# worker parked on someone else's GPU does nothing while another card sits idle.
MAX_GPUS="${MAX_GPUS:-2}"
SWEEP_GPUS="${SWEEP_GPUS:-0 1}"
INTERVAL="${INTERVAL:-300}"
LOG=runs/logs/supervisor.log
PIDDIR=runs/manifest/workers   # written by launch_workers.sh; unset here would crash `set -u`
LOCK=runs/manifest/.supervisor.lock
SWEEP_DONE=results/analysis/rank_sweep.json
mkdir -p runs/logs runs/manifest

say() { echo "[$(date -u +%F' '%H:%M:%S)] $*" | tee -a "$LOG"; }

if [ "${1:-}" = "--status" ]; then
  echo "supervisor: $(pgrep -f 'supervise.sh' | grep -v $$ | wc -l) process(es)"
  python -m obtune.gpu_alloc 2>/dev/null | sed 's/^/  /'
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

say "=== supervisor start (budget: ${MAX_GPUS} GPUs, following whatever is free | sweep: $SWEEP_GPUS | every ${INTERVAL}s) ==="

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

    # Retire any worker parked on a card a neighbour has taken. It cannot run
    # anything there, and while it lives it counts against our budget and blocks us
    # from starting on a card that IS free.
    for f in "$PIDDIR"/*.pid; do
      [ -e "$f" ] || continue
      tag=$(basename "$f" .pid); idx="${tag#gpu}"
      pid=$(cat "$f" 2>/dev/null)
      kill -0 "$pid" 2>/dev/null || continue
      owner=$(python -c "
from obtune import gpu_alloc
print(next((g.owner for g in gpu_alloc.survey() if g.index == $idx), 'free'))" 2>/dev/null)
      if [ "$owner" = "theirs" ]; then
        say "gpu${idx} was taken by another user — retiring our idle worker there"
        kill -TERM "$pid" 2>/dev/null; rm -f "$f"
      fi
    done

    # Top up to the budget on whatever is free right now — but never onto a card the
    # rank sweep is using. The sweep runs arms in pairs and briefly releases both GPUs
    # between pairs; claiming one in that gap put a grid job and a sweep arm on the
    # same card. A live sweep reserves the GPUs it was launched with, not just the
    # ones it happens to occupy this second.
    # Reserve a sweep GPU only while it is plausibly still in use. A flat reservation
    # for the sweep's whole lifetime is too blunt: once its last arm is running on one
    # card, the other sits idle for the rest of the run. A grace window covers the
    # seconds-long gap between arm pairs (the race this exists to prevent) without
    # holding a card the sweep has actually finished with.
    reserved=""
    if pgrep -f "run_rank_sweep.sh" >/dev/null 2>&1; then
      launched=$(pgrep -af "bash scripts/run_rank_sweep.sh" | head -1 \
                 | sed 's/.*run_rank_sweep\.sh //' | tr -s ' ')
      now=$(date +%s)
      for idx in $launched; do
        marker="runs/manifest/.sweep_gpu${idx}.seen"
        owner=$(python -c "
from obtune import gpu_alloc
print(next((g.owner for g in gpu_alloc.survey() if g.index == $idx), 'free'))" 2>/dev/null)
        if [ "$owner" = "ours" ]; then
          echo "$now" > "$marker"
          reserved="$reserved $idx"
        else
          last=$(cat "$marker" 2>/dev/null || echo 0)
          if [ $((now - last)) -lt "${SWEEP_GRACE:-240}" ]; then
            reserved="$reserved $idx"   # still inside the between-arms gap
          fi
        fi
      done
    fi
    claim=$(RESERVED="$reserved" python -c "
import os
from obtune import gpu_alloc
reserved = {int(x) for x in os.environ.get('RESERVED', '').split() if x.strip().isdigit()}
st = [g for g in gpu_alloc.survey() if g.index not in reserved]
held = len(gpu_alloc.ours()) # holdings count reserved cards too: they are ours
slots = max(0, $MAX_GPUS - held)
avail = [g.index for g in st if g.available]
print(' '.join(str(i) for i in avail[:slots]))
" 2>/dev/null)
    if [ -n "$claim" ]; then
      say "claiming free GPU(s): $claim (budget $MAX_GPUS)"
      # shellcheck disable=SC2086
      bash scripts/launch_workers.sh $claim >> "$LOG" 2>&1
    fi
  fi

  # --- rank sweep ---------------------------------------------------------- #
  if [ ! -f "$SWEEP_DONE" ]; then
    if ! pgrep -f "run_rank_sweep.sh" >/dev/null 2>&1; then
      # Relaunch on whatever is free, within budget — the pair it started on may
      # have been claimed by a neighbour in the meantime.
      gpus=$(python -c "
from obtune import gpu_alloc
c = gpu_alloc.claim($MAX_GPUS)
print(' '.join(str(i) for i in (c or gpu_alloc.ours()))[:32])" 2>/dev/null)
      gpus="${gpus:-$SWEEP_GPUS}"
      say "rank sweep is not running and not complete — relaunching on $gpus"
      # shellcheck disable=SC2086
      setsid nohup bash scripts/run_rank_sweep.sh $gpus \
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
