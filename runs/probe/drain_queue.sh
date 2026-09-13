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
  # Hold more work in SLURM'"'"'s queue than in ours. h100 and a30 are uncapped, so a pending job there
  # costs nothing and buys a better backfill position; only h200 is share-limited, and submit.py
  # refuses past the share on its own. 8 was too tight while another user held six h100 jobs.
  if [ "$((run+pend))" -lt 14 ] && [ "$left" -gt 0 ]; then
    # 34B needs 128 G of host memory (the earlier 34B runs used it); everything else gets 64-96 G,
    # because over-requesting is not free -- 128 G on a memory-starved h200 once scheduled a job a
    # day out. So the h200 pass asks for 128 G only while a 34B manifest is next in line.
    h200mem=96G
    next34b=$(ls runs/manifest/queued/*.json 2>/dev/null | xargs -r -n1 basename 2>/dev/null | grep -c 34b)
    only34b=$(ls runs/manifest/queued/*.json 2>/dev/null | wc -l)
    [ "$next34b" -gt 0 ] && [ "$next34b" -eq "$only34b" ] && h200mem=128G
    # a30 cards are 23.5 GB. 13B bf16 needs ~26 GB and OOM'd two minutes in on 2026-09-13; 12B and
    # 15B do not fit either. Only the 7-8B models go there, one named manifest at a time, because
    # `--queued` drains by priority and cannot filter. h100 and h200 take anything.
    for spec in "h100 3 64G" "h200 1 $h200mem"; do
      set -- $spec
      out=$(timeout 300 python scripts/slurm/submit.py --queued --partition "$1" --limit "$2" --mem "$3" 2>&1 | grep -E "^submitted|FAILED|REFUSING" | grep -v REFUSING)
      [ -n "$out" ] && echo "$out" | sed "s/^/[$1] /"
    done
    # a30 takes 7-8B TRAININGS only. It cannot SERVE them: vLLM on an 8.5B model leaves 0.92 GiB for
    # the KV cache against the 3.5 GiB an 8192-token context needs, and the engine refuses to start
    # (ev_1shot_codegemma-7b, 2026-09-13). Training fits because there is no KV cache to reserve.
    for j in $(ls runs/manifest/queued/tr_*.json 2>/dev/null | grep -E "codellama-7b|llama31-8b|codegemma-7b|granite31-8b" | head -2); do
      out=$(timeout 300 python scripts/slurm/submit.py --job "$j" --partition a30 --mem 64G 2>&1 | grep -E "^submitted|FAILED")
      [ -n "$out" ] && echo "$out" | sed "s/^/[a30] /"
    done
  fi
  echo "[status] queued=$left running=$run pending=$pend"
  sleep 240
done
