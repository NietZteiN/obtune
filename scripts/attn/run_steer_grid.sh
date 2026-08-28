#!/usr/bin/env bash
# Attention-steering grid (idea 2). Runs 3 systems x 3 conditions sequentially on ONE pinned GPU.
#
# Pinned rather than queued because the filesystem job queue only knows the train/eval/rq2 job
# kinds; adding a kind for a 9-cell one-off costs more than it saves. `setsid` + `nohup` is what
# makes it survive an SSH disconnect (parent becomes init), which is the same mechanism
# launch_workers.sh uses.
#
# CONDITIONS. `S2` and `S4` carry inert material (39.2 % / 28.4 % of characters); `L0` is the
# control where the mask is EMPTY and every delta must be exactly 0.0 — if it is not, the mask is
# firing on live code and the whole arm is void.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=src
PY=/data/jvl210002/conda_envs/obtune/bin/python
GPU="${GPU:-3}"
N="${N:-150}"
OUT=results/attn/steer
mkdir -p "$OUT" runs/logs

declare -A ADAPTER=(
  [base]=""
  [tuned_L0]="runs/adapters/qwen25c-1.5b/python/L0_r32_s17/best"
  [tuned_S2_s17]="runs/adapters/qwen25c-1.5b/python/S2_r32_s17/best"
)

for sys in base tuned_L0 tuned_S2_s17; do
  for cond in S2 S4 L0; do
    stem="qwen25c-1.5b__python__${sys}__${cond}__inert__score"
    if [ -f "$OUT/${stem}.json" ]; then echo "[skip] $stem (already on disk)"; continue; fi
    args=(--system "$sys" --condition "$cond" --max-items "$N" --out "$OUT")
    [ -n "${ADAPTER[$sys]}" ] && args+=(--adapter "${ADAPTER[$sys]}")
    echo "=== $(date -Is) $sys / $cond ==="
    CUDA_VISIBLE_DEVICES="$GPU" $PY scripts/attn/31_steer.py "${args[@]}" \
      || echo "!! FAILED $sys/$cond (continuing — a dead cell must not take the grid with it)"
  done
done
echo "=== $(date -Is) steering grid complete ==="
