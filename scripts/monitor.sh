#!/usr/bin/env bash
# Live status for the obtune box. Runs in tmux window `monitor`.
cd "$(dirname "$0")/.."
while true; do
  clear
  echo "=== obtune @ $(date '+%F %H:%M:%S') ==="
  echo "-- queue --"
  printf "   queued=%s running=%s done=%s failed=%s\n" \
    "$(ls runs/manifest/queued/ 2>/dev/null | wc -l)" \
    "$(ls runs/manifest/running/*/ 2>/dev/null | grep -c json)" \
    "$(ls runs/manifest/done/ 2>/dev/null | wc -l)" \
    "$(ls runs/manifest/failed/*.json 2>/dev/null | wc -l)"
  echo "-- workers --"
  for f in runs/manifest/workers/*.pid; do
    [ -e "$f" ] || continue
    pid=$(cat "$f"); kill -0 "$pid" 2>/dev/null && st=alive || st=DEAD
    echo "   $(basename "$f" .pid) pid=$pid $st"
  done
  echo "-- steering grid (idea 2) --"
  n=$(ls results/attn/steer/*__score.json 2>/dev/null | wc -l)
  echo "   cells complete: $n / 9"
  pgrep -f run_steer_grid.sh >/dev/null && echo "   driver: RUNNING" || echo "   driver: not running"
  tail -2 runs/logs/steer_grid.log 2>/dev/null | sed 's/^/   /' | cut -c1-100
  echo "-- gpus --"
  nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader | sed 's/^/   /'
  sleep 20
done
