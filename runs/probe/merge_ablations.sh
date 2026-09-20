#!/bin/bash
# Build the RQ1 merge ablations for one model, in one allocation.
#   bash runs/probe/merge_ablations.sh <model>
# Each merge is ~2 minutes; the cost is loading the base model once, which is why they are batched.
# Skips any merge already on disk, so re-running only fills gaps.
set -u
cd /work/jvl210002/migration/obtune
source scripts/env.sh
M="$1"
for spec in ablate_nol0 ablate_ident ablate_struct; do
  for ct in dare_ties; do
    out="runs/adapters/$M/python/merge_${spec}_${ct}_r32_s17"
    [ -f "$out/adapter_model.safetensors" ] && { echo "skip $spec/$ct: exists"; continue; }
    echo "### merge $M $spec $ct"
    python -m obtune.merge_adapters --config "merge/${spec}.yaml" --model "$M" --language python \
      --rank 32 --combination-type "$ct" --out "$out" || echo "FAILED $M $spec $ct"
  done
done
echo "### done $M"
