#!/bin/bash
# 79_merge_space_check across the rest of the panel. CPU-only.
set -u
source "${OBTUNE_ROOT:-/work/jvl210002/migration/obtune}/scripts/env.sh"
cd "$OBTUNE_ROOT"
for m in codellama-13b llama31-8b granite31-8b codegemma-7b gemma3-12b starcoder2-15b; do
  echo "=== $m ==="
  python scripts/analysis/79_merge_space_check.py "$m" || echo "FAILED: $m"
done
echo "merge-space sweep done"
