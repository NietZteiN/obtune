#!/usr/bin/env bash
# Launch one detached worker per IDLE GPU (CLAUDE.md §1).
#
# Uses setsid, NOT tmux. The tmux server on this host has died twice mid-run, taking
# every worker with it and costing hours of idle GPU; processes started with setsid
# reparent to init and have survived both times. A worker is a background daemon, not
# something anyone attaches to, so tmux bought nothing here — `--status` and the
# per-worker logs under runs/logs/ are the interface.
#
#   bash scripts/launch_workers.sh            # every idle GPU
#   bash scripts/launch_workers.sh 0 1        # specific GPUs
#   bash scripts/launch_workers.sh --status
#   bash scripts/launch_workers.sh --stop
#
# CUDA_VISIBLE_DEVICES is set at spawn time, before any python/torch import.
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

QUEUE=runs/manifest/queued
PIDDIR=runs/manifest/workers
mkdir -p "$PIDDIR" runs/logs

worker_pids() { pgrep -f "obtune.sched.worker --gpu-tag" 2>/dev/null; }

case "${1:-}" in
  --status)
    n=$(worker_pids | wc -l)
    echo "workers running: $n"
    for f in "$PIDDIR"/*.pid; do
      [ -e "$f" ] || continue
      pid=$(cat "$f"); tag=$(basename "$f" .pid)
      kill -0 "$pid" 2>/dev/null && echo "  $tag: pid $pid alive" || echo "  $tag: pid $pid DEAD"
    done
    echo "queued=$(ls "$QUEUE" 2>/dev/null | wc -l)" \
         "running=$(find runs/manifest/running -name '*.json' 2>/dev/null | wc -l)" \
         "done=$(ls runs/manifest/done 2>/dev/null | wc -l)" \
         "failed=$(ls runs/manifest/failed 2>/dev/null | wc -l)"
    exit 0 ;;
  --stop)
    for pid in $(worker_pids); do kill -TERM "$pid" 2>/dev/null && echo "stopped $pid"; done
    sleep 3
    for pid in $(worker_pids); do kill -KILL "$pid" 2>/dev/null; done
    rm -f "$PIDDIR"/*.pid
    echo "note: jobs left in runs/manifest/running/ can be recovered with --requeue-stale"
    exit 0 ;;
esac

if [ "$#" -gt 0 ]; then
  GPUS=("$@")
else
  # Only idle GPUs — this is a shared box with no scheduler (CLAUDE.md §1).
  mapfile -t GPUS < <(python -c "
from obtune import gpu
try:
    print('\n'.join(str(i) for i in gpu.pick_free_gpus(4)))
except RuntimeError:
    pass
")
fi

if [ "${#GPUS[@]}" -eq 0 ]; then
  echo "no idle GPU — queue stays in $QUEUE ($(ls "$QUEUE" 2>/dev/null | wc -l) jobs)"
  exit 1
fi

for g in "${GPUS[@]}"; do
  tag="gpu${g}"
  if pgrep -f "obtune.sched.worker --gpu-tag $tag\b" >/dev/null 2>&1; then
    echo "worker for $tag already running"
    continue
  fi
  log="runs/logs/worker_${tag}.log"
  CUDA_VISIBLE_DEVICES="$g" setsid nohup python -m obtune.sched.worker --gpu-tag "$tag" \
    >> "$log" 2>&1 < /dev/null &
  pid=$!
  disown 2>/dev/null || true
  echo "$pid" > "$PIDDIR/${tag}.pid"
  echo "launched worker $tag (pid $pid, CUDA_VISIBLE_DEVICES=$g) -> $log"
done
