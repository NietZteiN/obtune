#!/usr/bin/env bash
# Start one detached queue worker per GPU, so work survives logout.
#
#   bash scripts/launch_workers.sh 0 1 2 3     # start on these GPUs
#   bash scripts/launch_workers.sh             # start on every currently-free GPU
#   bash scripts/launch_workers.sh --status
#   bash scripts/launch_workers.sh --stop
#
# Referenced by README.md and by scripts/supervise.sh (which calls it to top up to its
# GPU budget) but never written until now — so the supervisor could detect a free card
# and then fail to claim it.
#
# Why setsid and not just `&`: a worker started from an interactive shell, or from an
# editor's integrated terminal, dies when that session's process group is signalled on
# logout. `nohup` alone only masks SIGHUP; it does not detach the process group. setsid
# gives the worker its own session with PPID 1, which is what actually makes it outlive
# the terminal that started it.
#
# CUDA_VISIBLE_DEVICES is set at SPAWN time (CLAUDE.md §1): the worker itself never
# imports torch, so the pin is always in place before the job subprocess starts.
#
# Idempotent: a GPU that already has a live worker is skipped, so this is safe to re-run
# and safe for the supervisor to call on every poll.
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

PIDDIR=runs/manifest/workers
LOGDIR=runs/logs
mkdir -p "$PIDDIR" "$LOGDIR"

alive() {  # alive <gpu-index> -> 0 if a worker for that tag is running
  local tag="gpu$1" pid
  pid=$(cat "$PIDDIR/$tag.pid" 2>/dev/null) || true
  [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null && return 0
  # Fall back to a process scan: a worker started by hand has no pidfile, and starting a
  # second one on the same card would have both claiming jobs onto one GPU.
  pgrep -f "obtune.sched.worker --gpu-tag $tag\$" >/dev/null 2>&1
}

case "${1:-}" in
  --status)
    for i in 0 1 2 3; do
      if alive "$i"; then
        pid=$(cat "$PIDDIR/gpu$i.pid" 2>/dev/null || pgrep -f "obtune.sched.worker --gpu-tag gpu$i\$" | head -1)
        job=$(ls runs/manifest/running/gpu$i/*.json 2>/dev/null | head -1 | xargs -r basename)
        echo "  gpu$i: RUNNING (pid ${pid:-?})${job:+  job=$job}"
      else
        echo "  gpu$i: down"
      fi
    done
    exit 0
    ;;
  --stop)
    for i in 0 1 2 3; do
      pid=$(cat "$PIDDIR/gpu$i.pid" 2>/dev/null) || continue
      kill -TERM "$pid" 2>/dev/null && echo "  stopped worker gpu$i (pid $pid)"
      rm -f "$PIDDIR/gpu$i.pid"
    done
    exit 0
    ;;
esac

GPUS=("$@")
if [ ${#GPUS[@]} -eq 0 ]; then
  # No explicit list: take whatever is genuinely free. The worker re-checks idleness
  # before every claim anyway, so this only decides where to place a worker, never
  # whether it is safe to run — that guard stays with the worker (CLAUDE.md §1).
  # One id per line, and nothing at all when none are free: a bare print('') emits a
  # blank line, which mapfile turns into a one-element array of "" — that slipped past
  # the emptiness check below and logged "skipping non-numeric gpu id:" on every poll.
  mapfile -t GPUS < <(python -c "
from obtune import gpu
for g in gpu.query():
    if g.is_idle(2000, 5):
        print(g.index)
" 2>/dev/null)
fi

# Drop anything not in scheduler_policy.allowed_gpus (configs/compute.yaml). This must
# happen for the EXPLICIT list too, not just the auto-detected one: `launch_workers.sh 0
# 1 2 3` from a human or from run_mono_gate.sh would otherwise put a worker straight onto
# a card that has been lent out. Filtering here covers every caller, because this script
# is the only place a worker is ever spawned.
if [ ${#GPUS[@]} -gt 0 ]; then
  # Kept ids go to stdout (captured); the skip notice goes to stderr, so it lands in the
  # caller's log instead of being parsed as a gpu id.
  #
  # The exit status is CHECKED. Capturing straight into `mapfile` would turn any failure of
  # this python — a broken env, an unparseable compute.yaml — into an empty GPU list, which
  # is indistinguishable from "every card is busy": every worker would silently stop being
  # started and the queue would stall with a reassuring message. Fail loudly and keep the
  # loan rather than guessing in either direction.
  if ! filtered=$(GPUS_IN="${GPUS[*]}" python -c "
import os, sys
from obtune import gpu_alloc
ok = gpu_alloc.allowed_gpus()
for tok in os.environ['GPUS_IN'].split():
    if not tok.isdigit() or ok is None or int(tok) in ok:
        print(tok)                # non-numeric falls through to the loop's own warning
    else:
        print(f'  gpu{tok}: lent out (scheduler_policy.allowed_gpus) — skipped', file=sys.stderr)
"); then
    echo "ERROR: could not apply scheduler_policy.allowed_gpus (configs/compute.yaml)."
    echo "       Refusing to start any worker rather than risk placing one on a lent card."
    exit 1
  fi
  mapfile -t GPUS < <(printf '%s\n' "$filtered" | grep -v '^[[:space:]]*$')
fi

if [ ${#GPUS[@]} -eq 0 ]; then
  echo "no free GPU to start a worker on"
  exit 0
fi

# Cap the number of LIVE workers at scheduler_policy.gpu_budget.
#
# `allowed_gpus` is a CANDIDATE set (CLAUDE.md §1: the borrower moves, so we follow whatever
# is free) and `gpu_budget` is how many cards we may hold at once. Until now only
# supervise.sh read the budget; this script filtered by allowed_gpus alone and started a
# worker on EVERY candidate. With allowed_gpus=[0,1,2] and gpu_budget=2 that is three
# workers against a two-card budget, and because pipeline.sh's ensure_infra calls this on
# every poll, the extra worker came straight back after any manual stop. CLAUDE.md already
# stated that this script honours the budget; it did not.
#
# Workers that are ALREADY alive count toward the budget, so a top-up run cannot exceed it.
budget=$(python -c "
from obtune.config import load_config
sp = load_config('compute.yaml').get('scheduler_policy') or {}
b = sp.get('gpu_budget')
print(int(b) if b else 0)
" 2>/dev/null) || budget=0
if [ "${budget:-0}" -gt 0 ]; then
  # Count EVERY live worker, not just those among the candidates. A worker that is busy on
  # a job makes its GPU non-idle, so auto-detect drops that card from GPUS — counting only
  # within GPUS therefore saw zero live workers exactly when the budget was already spent,
  # and topped up onto a third card every poll.
  live=0
  for f in "$PIDDIR"/gpu*.pid; do
    [ -e "$f" ] || continue
    n=$(basename "$f" .pid); n=${n#gpu}
    alive "$n" && live=$((live + 1))
  done
  room=$((budget - live))
  [ "$room" -lt 0 ] && room=0
  keep=()
  for i in "${GPUS[@]}"; do
    if alive "$i"; then keep+=("$i")            # already counted; never stop it here
    elif [ "$room" -gt 0 ]; then keep+=("$i"); room=$((room - 1))
    else echo "  gpu$i: at gpu_budget ($budget) — not started"; fi
  done
  GPUS=("${keep[@]}")
fi

for i in "${GPUS[@]}"; do
  [[ "$i" =~ ^[0-9]+$ ]] || { echo "skipping non-numeric gpu id: $i"; continue; }
  if alive "$i"; then
    echo "  gpu$i: worker already running — skipped"
    continue
  fi
  setsid nohup env CUDA_VISIBLE_DEVICES="$i" \
    python -m obtune.sched.worker --gpu-tag "gpu$i" \
    >> "$LOGDIR/worker_gpu$i.log" 2>&1 < /dev/null &
  pid=$!
  echo "$pid" > "$PIDDIR/gpu$i.pid"
  disown 2>/dev/null || true
  echo "  gpu$i: started worker (pid $pid) -> $LOGDIR/worker_gpu$i.log"
done
