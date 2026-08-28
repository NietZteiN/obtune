#!/bin/bash
#SBATCH --job-name=smoke_h100
#SBATCH --partition=h100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=/work/jvl210002/migration/obtune/runs/logs/slurm/%j_smoke_h100.out
#SBATCH --error=/work/jvl210002/migration/obtune/runs/logs/slurm/%j_smoke_h100.out
set -uo pipefail

OBTUNE_ROOT=/work/jvl210002/migration/obtune
source "$OBTUNE_ROOT/scripts/env.sh"
cd "$OBTUNE_ROOT"

MANIFEST_SRC=''
RUN_DIR="$OBTUNE_ROOT/runs/manifest/running/slurm-$SLURM_JOB_ID"
DONE_DIR="$OBTUNE_ROOT/runs/manifest/done"
FAIL_DIR="$OBTUNE_ROOT/runs/manifest/failed"
MANIFEST_NAME=''

if [[ -n "$MANIFEST_SRC" && -f "$MANIFEST_SRC" ]]; then
  mkdir -p "$RUN_DIR"
  mv "$MANIFEST_SRC" "$RUN_DIR/$MANIFEST_NAME"
  CLAIM="$RUN_DIR/$MANIFEST_NAME"
else
  CLAIM=""
fi

finish() {
  rc=$?
  if [[ -n "$CLAIM" && -f "$CLAIM" ]]; then
    if [[ $rc -eq 0 ]]; then dest="$DONE_DIR"; else dest="$FAIL_DIR"; fi
    mkdir -p "$dest"
    python - "$CLAIM" "$dest/$MANIFEST_NAME" "$rc" <<'EOF'
import json, os, sys, datetime
src, dst, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = json.load(open(src))
d.setdefault("slurm", {}).update({
    "job_id": os.environ.get("SLURM_JOB_ID"),
    "node": os.environ.get("SLURMD_NODENAME"),
    "partition": os.environ.get("SLURM_JOB_PARTITION"),
    "exit_code": rc,
    "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
})
json.dump(d, open(dst, "w"), indent=2)
os.remove(src)
EOF
    rmdir "$RUN_DIR" 2>/dev/null || true
  fi
  exit $rc
}
trap finish EXIT

echo "# obtune slurm job $SLURM_JOB_ID on $SLURMD_NODENAME ($SLURM_JOB_PARTITION)"
echo "# started $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader || true
echo "# argv: scripts/smoke_env.py"
echo

python scripts/smoke_env.py
