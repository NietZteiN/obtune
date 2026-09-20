#!/bin/bash
# Second half of the specialist-geometry sweep. Split out from geometry_sweep.sh because
# that job measured ~18 min on CodeLlama-13B: trim_mask does a top-k over a materialised
# 5120x5120 update per sampled module per pair (15 pairs), and CodeLlama-34B's 8192-wide
# modules over 60 layers are several times worse again. Six models in sequence would not
# fit the `dev` partition's 2 h wall.
# Runs the models geometry_sweep.sh reaches LAST, so the two converge from both ends. An
# overlap just rewrites an identical JSON and costs nothing.
set -u
source "${OBTUNE_ROOT:-/work/jvl210002/migration/obtune}/scripts/env.sh"
cd "$OBTUNE_ROOT"
for m in granite31-8b codegemma-7b gemma3-12b starcoder2-15b; do
  echo "=== $m ==="
  python scripts/analysis/75_specialist_geometry.py "$m" || echo "FAILED: $m"
done
echo "sweep-b done"
