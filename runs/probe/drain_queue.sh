#!/bin/bash
# Keep the manifest queue moving while the master-table backfill runs (2026-09-13).
# Emits one line per submission, per failure, and a periodic status; exits when the queue is empty
# AND nothing of ours is left running, so the watch ends by itself.
#
# PARTITION POLICY. h100 and a30 carry no QOS and take the bulk; h200 is capped at obtune's agreed
# share of 2 and submit.py refuses above it, so the h200 pass is limited and its refusal is not an
# error. 34B jobs go to h200 only, at 96-128 G: a30's 24 GB cards and the default 64 G cannot hold
# 34B, which is how two of them died within a minute on 2026-09-13.
cd /work/jvl210002/migration/obtune
source scripts/env.sh
mine() { squeue -h -u "$USER" -o "%j %T %Z" | awk -v r="$PWD" '$3==r' ; }
while true; do
  left=$(ls runs/manifest/queued/*.json 2>/dev/null | wc -l)
  run=$(mine | grep -c RUNNING); pend=$(mine | grep -c PENDING)
  # a failed manifest is worth a line: it is the only signal a job died
  for f in $(ls -t runs/manifest/failed/*.json 2>/dev/null | head -3); do
    b=$(basename "$f" .json)
    case "$b" in ev_depth_*|ev_1shot_*|ev_seenfam_*|tr_L*|tr_S*)
      grep -q "^$b\$" runs/probe/.drain_seen 2>/dev/null || { echo "FAILED manifest: $b"; echo "$b" >> runs/probe/.drain_seen; } ;;
    esac
  done
  if [ "$left" -eq 0 ] && [ "$run" -eq 0 ] && [ "$pend" -eq 0 ]; then
    echo "queue drained: nothing queued, running or pending"; break
  fi
  if [ "$((run+pend))" -lt 8 ] && [ "$left" -gt 0 ]; then
    # 34B needs 128 G of host memory (the earlier 34B runs used it); everything else gets 64-96 G,
    # because over-requesting is not free -- 128 G on a memory-starved h200 once scheduled a job a
    # day out. So the h200 pass asks for 128 G only while a 34B manifest is next in line.
    h200mem=96G
    next34b=$(ls runs/manifest/queued/*.json 2>/dev/null | xargs -r -n1 basename 2>/dev/null | grep -c 34b)
    only34b=$(ls runs/manifest/queued/*.json 2>/dev/null | wc -l)
    [ "$next34b" -gt 0 ] && [ "$next34b" -eq "$only34b" ] && h200mem=128G
    for spec in "h100 3 64G" "a30 2 64G" "h200 1 $h200mem"; do
      set -- $spec
      out=$(timeout 300 python scripts/slurm/submit.py --queued --partition "$1" --limit "$2" --mem "$3" 2>&1 | grep -E "^submitted|FAILED|REFUSING" | grep -v REFUSING)
      [ -n "$out" ] && echo "$out" | sed "s/^/[$1] /"
    done
  fi
  echo "[status] queued=$left running=$run pending=$pend"
  sleep 240
done
