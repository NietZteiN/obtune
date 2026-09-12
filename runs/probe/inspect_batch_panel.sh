#!/bin/bash
# The login node cannot run this: it died with `libgomp: Thread creation failed` and a failed
# 25 MB allocation partway through tokenising 8 rows. Run it where there are resources.
set -u
cd /work/jvl210002/migration/obtune
source scripts/env.sh
for m in granite31-8b starcoder2-15b codellama-7b; do
  echo "############ $m ############"
  python scripts/inspect_batch.py --config train/grid_py_L1b_panel.yaml --model "$m" --rows 8 2>&1 \
    | grep -vE "examples/s|^\[transformers\]|Warning"
done
