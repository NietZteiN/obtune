#!/bin/bash
# Run SEVERAL trainings in parallel inside ONE SLURM allocation.
#
#   bash runs/probe/train_batch.sh <model> <seed> <per_gpu> <cond> [cond...]
#
# WHY THIS EXISTS. The juno QoS caps obtune at four RUNNING JOBS per user across h200 and normal --
# and that cap counts JOBS, not GPUs, while every h200 node carries 2 x H200 NVL at 141 GB. Seven
# seed-42 trainings submitted as seven jobs therefore queue behind a four-slot door on a partition
# with 52 idle GPUs. Submitted as ONE job holding both GPUs and running `per_gpu` trainings on each,
# the same seven occupy one slot and run four at a time. The limit is not GPUs; it is our packing.
#
# SIZING -- AND per_gpu=1 IS THE RIGHT DEFAULT, MEASURED 2026-09-16. Memory is not the binding
# constraint: a 7-8B LoRA at the panel's 16x4 shape fits twice over in 141 GB and the first packed
# batch (granite31-8b s42, per_gpu=2) raised no OOM at all. COMPUTE is. Two trainings sharing one
# H200 each ran about 2.75x slower than the same recipe alone -- L0 took 55 min packed against
# ~20 min solo -- so four concurrent at 2.75x is ~1.45x the throughput of running them one at a
# time, where two concurrent at full speed would be ~2x. Packing two per GPU is therefore SLOWER in
# aggregate than one per GPU, and it converts a single OOM into a dead batch.
#
# Use per_gpu=1 and add GPUs instead. The value of this script is not per-GPU density: it is that N
# trainings occupy ONE job slot, which is what gets past the four-job QoS cap on h200.
#
# Each training keeps its own log under runs/logs/batch/, so a failure is attributable to a
# condition rather than to "the batch". The script waits for all of them and reports each exit code;
# it exits non-zero if any failed, so a dependent job (checkpoint selection) will not start on a
# partial set.
set -u
cd /work/jvl210002/migration/obtune
source scripts/env.sh
M="$1"; SEED="$2"; PER_GPU="$3"; shift 3
CONDS=("$@")
NGPU=$(python - <<'PY'
import os
v=os.environ.get("CUDA_VISIBLE_DEVICES","")
print(len([x for x in v.split(",") if x!=""]) or 1)
PY
)
SLOTS=$(( NGPU * PER_GPU ))
echo "### batch: model=$M seed=$SEED gpus=$NGPU per_gpu=$PER_GPU -> $SLOTS concurrent; ${#CONDS[@]} trainings"
[ "$PER_GPU" -gt 1 ] && echo "### NOTE: per_gpu>1 measured ~2.75x slower per training on H200; per_gpu=1 has higher throughput."
mkdir -p runs/logs/batch
declare -A PID2C
launch() {
  local c="$1" gpu="$2"
  case "$c" in
    L0)                  cfg="train/grid_py_L0.yaml" ;;
    X1)                  cfg="train/grid_py_X1.yaml" ;;
    L0-L1b-L1r-L2-S1-S2) cfg="train/mono_generic_py.yaml" ;;
    *)                   cfg="train/grid_py_${c}_panel.yaml" ;;
  esac
  local log="runs/logs/batch/${M}_${c}_s${SEED}.log"
  echo "  -> $c on local gpu $gpu  ($cfg)  log=$log"
  CUDA_VISIBLE_DEVICES="$gpu" python -m obtune.train_sft --config "$cfg" --model "$M" --seed "$SEED" \
      > "$log" 2>&1 &
  PID2C[$!]="$c"
}
i=0; fail=0
for c in "${CONDS[@]}"; do
  d="runs/adapters/$M/python/${c}_r32_s${SEED}"
  [ -f "$d/training_summary.json" ] && { echo "  skip $c: already trained"; continue; }
  while [ "$(jobs -rp | wc -l)" -ge "$SLOTS" ]; do
    wait -n || fail=1
  done
  launch "$c" $(( i % NGPU )); i=$(( i + 1 ))
done
while [ "$(jobs -rp | wc -l)" -gt 0 ]; do wait -n || fail=1; done
echo "### batch done for $M s$SEED"
for c in "${CONDS[@]}"; do
  d="runs/adapters/$M/python/${c}_r32_s${SEED}"
  [ -f "$d/training_summary.json" ] && echo "  ok   $c" || { echo "  FAIL $c"; fail=1; }
done
exit $fail
