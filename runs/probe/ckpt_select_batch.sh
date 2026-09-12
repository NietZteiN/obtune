#!/bin/bash
# Checkpoint-select EVERY trained specialist of one model in a single allocation.
#
# WHY BATCHED. Each selection is ~6 min of GPU, but on a jammed partition each one also costs a
# full queue wait -- five separate jobs for one model were scheduled two days out, so 30 minutes of
# work was going to take 48 hours of waiting. One allocation per model turns five queue waits into
# one. It also loads the base model once instead of five times, which is most of the 6 minutes.
#
# Idempotent: skips any adapter that already has `best/`, so it is safe to re-run as more
# specialists finish training.
set -u
cd /work/jvl210002/migration/obtune
source scripts/env.sh
M="$1"
for c in L1b L1r L2 S1 S2; do
  d="runs/adapters/$M/python/${c}_r32_s17"
  [ -f "$d/training_summary.json" ] || { echo "skip $c: not trained yet"; continue; }
  [ -e "$d/best/adapter_model.safetensors" ] && { echo "skip $c: best/ already exists"; continue; }
  echo "### checkpoint-select $M $c"
  python -m obtune.eval_vllm --config "train/grid_py_${c}_panel.yaml" --model "$M" \
    --mode ckpt-select --adapter-root "$d" || echo "FAILED $M $c"
done
echo "### done $M"
