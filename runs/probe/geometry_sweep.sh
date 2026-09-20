#!/bin/bash
# Specialist-update geometry for the models 75_specialist_geometry.py has not covered.
# CPU-only: reads adapter safetensors and does matrix products, no model load, no GPU.
# Submitted to `dev` deliberately -- that is QoS=juno-dev, a SEPARATE pool from the
# 4-slot juno budget the two projects share, so this costs the other project nothing.
set -u
source "${OBTUNE_ROOT:-/work/jvl210002/migration/obtune}/scripts/env.sh"
cd "$OBTUNE_ROOT"
for m in codellama-13b codellama-34b starcoder2-15b gemma3-12b codegemma-7b granite31-8b; do
  echo "=== $m ==="
  # Do not let one model's failure abort the sweep; the others are independent.
  python scripts/analysis/75_specialist_geometry.py "$m" || echo "FAILED: $m"
done
echo "sweep done"
