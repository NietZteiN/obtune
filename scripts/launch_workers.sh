#!/usr/bin/env bash
# Launch one detached tmux worker per IDLE GPU (CLAUDE.md §1).
#
# CUDA_VISIBLE_DEVICES is set at tmux-spawn time, before any python/torch import,
# which is the only point where the pin is guaranteed to take effect. The worker
# then re-checks that the same physical GPU is still idle before claiming each job,
# because this box is shared and someone else may start a run at any time.
#
#   bash scripts/launch_workers.sh            # every idle GPU
#   bash scripts/launch_workers.sh 0 2        # only these
#   bash scripts/launch_workers.sh --status   # what is running
#   bash scripts/launch_workers.sh --stop     # stop all obtune workers
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY=/data/jvl210002/conda_envs/obtune/bin/python

case "${1:-}" in
  --status)
    tmux ls 2>/dev/null | grep '^obtune-' || echo "no obtune workers running"
    echo
    for d in queued running done failed; do
      n=$(find "$ROOT/runs/manifest/$d" -name '*.json' 2>/dev/null | wc -l)
      printf '  %-8s %s\n' "$d" "$n"
    done
    exit 0
    ;;
  --stop)
    tmux ls 2>/dev/null | grep '^obtune-' | cut -d: -f1 | while read -r s; do
      tmux kill-session -t "$s" && echo "stopped $s"
    done
    echo "note: jobs left in runs/manifest/running/ can be requeued with:"
    echo "  PYTHONPATH=src $PY -m obtune.sched.worker --gpu-tag any --requeue-stale"
    exit 0
    ;;
esac

if [ $# -gt 0 ]; then
  GPUS="$*"
else
  GPUS=$(PYTHONPATH="$ROOT/src" "$PY" - <<'EOF'
from obtune import gpu
print(" ".join(str(s.index) for s in gpu.query() if s.is_idle(2000, 5)))
EOF
)
fi

if [ -z "${GPUS// /}" ]; then
  echo "no idle GPUs — nothing launched. On a shared box you wait; there is no queue."
  exit 1
fi

for g in $GPUS; do
  session="obtune-gpu${g}"
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "$session already running — skipping"
    continue
  fi
  tmux new-session -d -s "$session" \
    "cd '$ROOT' && CUDA_VISIBLE_DEVICES=$g PYTHONPATH='$ROOT/src' '$PY' -m obtune.sched.worker --gpu-tag gpu$g 2>&1 | tee -a runs/logs/worker-gpu$g.log"
  echo "launched $session (CUDA_VISIBLE_DEVICES=$g)"
done

echo
echo "attach with: tmux attach -t obtune-gpu<N>    status: bash scripts/launch_workers.sh --status"
