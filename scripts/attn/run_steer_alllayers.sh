#!/usr/bin/env bash
# All-28-layer steering. Closes the one caveat on the 6-layer null: attention suppressed at 6 of
# 28 layers can still reach the inert keys at the other 22, so a 6-layer null could in principle
# be a partial intervention rather than a real absence of effect. The 2026-08-26 manipulation
# check showed all-28-layer masking changes 68 % of generated outputs against 62 % identical at
# 6 layers, so this is the setting where the intervention is known to bite hardest.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=src
PY="${OBTUNE_ENV:-/work/jvl210002/migration/envs/obtune}/bin/python"
GPU="${GPU:-3}"
ALL=$(seq 0 27 | tr '\n' ' ')
declare -A ADAPTER=( [base]="" [tuned_S2_s17]="runs/adapters/qwen25c-1.5b/python/S2_r32_s17/best" )
for sys in base tuned_S2_s17; do
  for cond in S2 S4 L0; do
    args=(--system "$sys" --condition "$cond" --max-items 150 --layers $ALL \
          --tag inert_all28 --out results/attn/steer)
    [ -n "${ADAPTER[$sys]}" ] && args+=(--adapter "${ADAPTER[$sys]}")
    echo "=== $(date -Is) ALL-LAYERS $sys / $cond ==="
    CUDA_VISIBLE_DEVICES="$GPU" $PY scripts/attn/31_steer.py "${args[@]}" \
      || echo "!! FAILED $sys/$cond"
  done
done
echo "=== $(date -Is) all-layer steering complete ==="
