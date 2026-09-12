#!/bin/bash
# Run one eval config across SEVERAL models in a single allocation.
#
# WHY. Measured runtimes are 9-31 min per model, but on this cluster each separate job also pays a
# full queue wait -- jobs submitted today are being scheduled a DAY or TWO out. With 13 short evals
# queued, the waits dominate the work by more than an order of magnitude. One allocation per config
# turns 7 waits into 1. Evaluation resumes at cell granularity, so a walltime kill costs only the
# cell in flight and a resubmission continues where this left off.
#
# Usage: eval_batch.sh <config> <model> [model ...]
set -u
cd /work/jvl210002/migration/obtune
source scripts/env.sh
CFG="$1"; shift
for m in "$@"; do
  echo "##### $CFG :: $m"
  python -m obtune.eval_vllm --config "$CFG" --model "$m" --language python || echo "FAILED $m"
done
echo "##### batch done: $CFG"
