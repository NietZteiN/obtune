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
# SEED IS THE SECOND ARGUMENT (2026-09-14), default 17: the second-seed panel needs best/ exactly as
# the s17 twins did, and the hardwired seed skipped every _s42 adapter as "not trained yet". L0 and X1
# are included because s42 must select them too; they use their own configs, not the _panel ones.
SEED="${2:-17}"
# S3 and S4 are here for the MIXTURE arm's eight experts; a merge needs only L1b..S2. Untrained
# adapters are skipped below, so listing them costs nothing before they exist.
# THE BREADTH ADAPTER IS IN THIS LIST (added 2026-09-16). It was missing, and nothing said so:
# the script reported "9 of 10 selected" and looked finished, while the one adapter every
# seed-42 eval config names as `mono_all_s42` had no best/. The evals then failed at model-load
# time with FileNotFoundError, hours later and on a different machine from the omission.
# Its directory is named by its six conditions rather than one, so it needs its own case below.
for c in L0 L1b L1r L2 S1 S2 S3 S4 X1 L0-L1b-L1r-L2-S1-S2; do
  d="runs/adapters/$M/python/${c}_r32_s${SEED}"
  [ -f "$d/training_summary.json" ] || { echo "skip $c: not trained yet"; continue; }
  [ -e "$d/best/adapter_model.safetensors" ] && { echo "skip $c: best/ already exists"; continue; }
  case "$c" in
    L0) cfg="train/grid_py_L0.yaml" ;;
    X1) cfg="train/grid_py_X1.yaml" ;;
    L0-L1b-L1r-L2-S1-S2) cfg="train/mono_generic_py.yaml" ;;
    *) cfg="train/grid_py_${c}_panel.yaml" ;;
  esac
  echo "### checkpoint-select $M $c s$SEED"
  python -m obtune.eval_vllm --config "$cfg" --model "$M" \
    --mode ckpt-select --adapter-root "$d" || echo "FAILED $M $c s$SEED"
done
# THE BACKWARD-TRAINED CONTROL LIVES UNDER runs/adapters_inverse/, NOT runs/adapters/ (2026-09-16).
# It is trained by the same recipe with prompt.task=input and adapter_root: runs/adapters_inverse,
# precisely so it does not collide with mono_all's directory -- which also means this loop, rooted at
# runs/adapters/$M/python, never saw it. Both models trained to completion (checkpoint-1260 and
# `final`) and neither got a best/, which surfaced only when the evals tried to load one.
d="runs/adapters_inverse/$M/python/L0-L1b-L1r-L2-S1-S2_r32_s17"
if [ -f "$d/training_summary.json" ] && [ ! -e "$d/best/adapter_model.safetensors" ]; then
  echo "### checkpoint-select $M inverse-breadth s17"
  python -m obtune.eval_vllm --config train/inverse_breadth_py.yaml --model "$M" \
    --mode ckpt-select --adapter-root "$d" || echo "FAILED $M inverse-breadth"
fi
echo "### done $M"
