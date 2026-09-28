#!/bin/bash
#SBATCH --job-name=ckb_s202
#SBATCH --partition=a30
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH --nodelist=g-02-01
#SBATCH --output=/work/jvl210002/migration/obtune/runs/logs/slurm/%j_ckb_s202.out
#SBATCH --error=/work/jvl210002/migration/obtune/runs/logs/slurm/%j_ckb_s202.out
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

# CMD_STATUS is set only when the command RETURNS. At walltime SLURM SIGTERMs the script while
# it is waiting on the python child; bash finishes the wait, then acts on the signal and runs the
# EXIT trap WITHOUT executing the next line -- so `$?` inside the trap is the status of the last
# command that did complete, the `echo` above the command, which is 0. On 2026-09-13 a specialist
# training killed at its 1 h limit (392121, step 178/222) was therefore filed under done/ with
# exit_code 0 and no adapter, and the merge feeder counted the model at 4/5 specialists. An empty
# CMD_STATUS in the trap means "killed before the command returned" and files under failed/.
CMD_STATUS=""
finish() {
  rc=$?
  if [[ -z "$CMD_STATUS" ]]; then rc=124; else rc=$CMD_STATUS; fi
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
    **({"reason": "killed before the command returned (walltime or node failure)"} if rc == 124 else {}),
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
echo "# argv: bash runs/probe/ckpt_select_batch.sh codellama-7b 202"
echo

bash runs/probe/ckpt_select_batch.sh codellama-7b 202
CMD_STATUS=$?
