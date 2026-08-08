#!/usr/bin/env bash
# Gate 0 — does one adapter trained on ALL obfuscation types reach the held-out one?
#
# Designed to run unattended: launch it in tmux and log off. Every stage is idempotent
# (finished work is skipped), every wait has a timeout, and a crashed trainer aborts
# with a message instead of hanging until morning.
#
#   tmux new -s monogate -d 'bash scripts/run_mono_gate.sh 2 3'
#   tmux capture-pane -pt monogate | tail -40      # or: tail -f runs/logs/mono_gate.log
#
# $1 = GPU for mono work, $2 = GPU for control/base work.
#
# Ends by writing results/analysis/mono_gate_decision.json and then ACTING on it:
#   mono beats the control on H1  -> breadth gives invariance; the per-condition grid
#                                    is unnecessary, so it is NOT launched.
#   otherwise                     -> the grid is the explanatory next step and IS
#                                    launched, so an idle night is not wasted.
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

MONO_GPU="${1:-2}"
CTL_GPU="${2:-3}"
ADAPTERS="runs/adapters/qwen25c-1.5b/python"
MONO_DIR="$ADAPTERS/L0-L1b-L1r-L2-S1-S2_r32_s17"
CTL_DIR="$ADAPTERS/L0_r32_s17"
LOG=runs/logs/mono_gate.log
DECISION=results/analysis/mono_gate_decision.json
MAX_WAIT_MIN="${MAX_WAIT_MIN:-420}"          # 7h ceiling per training wait
export OBTUNE_GPU_MEM_UTIL="${OBTUNE_GPU_MEM_UTIL:-0.45}"

mkdir -p results/analysis runs/logs
say() { echo "[$(date -u +%F' '%H:%M:%S)] $*" | tee -a "$LOG"; }

adapter_ready() { [ -d "$1/final" ] || [ -f "$1/adapter_model.safetensors" ] || [ -d "$1/best" ]; }

wait_for_adapter() {  # $1 = dir, $2 = name
  local waited=0
  if adapter_ready "$1"; then say "$2 already trained"; return 0; fi
  say "waiting for $2 ($1), ceiling ${MAX_WAIT_MIN}m"
  while ! adapter_ready "$1"; do
    sleep 60; waited=$((waited + 1))
    if [ $((waited % 30)) -eq 0 ]; then say "  ...$2 still training (${waited}m)"; fi
    if [ "$waited" -ge "$MAX_WAIT_MIN" ]; then
      say "ABORT: $2 exceeded ${MAX_WAIT_MIN}m"; return 1
    fi
    # A trainer that died without producing an adapter must not wait forever.
    if ! pgrep -f "obtune.train_sft" >/dev/null && ! adapter_ready "$1"; then
      sleep 120  # tolerate the gap between one trainer exiting and the next starting
      if ! pgrep -f "obtune.train_sft" >/dev/null && ! adapter_ready "$1"; then
        say "ABORT: no trainer running and $2 produced no adapter — check its log"; return 1
      fi
    fi
  done
  say "$2 training done (${waited}m)"
}

select_ckpt() {  # $1 = config, $2 = dir, $3 = gpu, $4 = name
  if [ -e "$2/best" ]; then say "$4 checkpoint already selected"; return 0; fi
  say "selecting checkpoint for $4 on GPU $3"
  CUDA_VISIBLE_DEVICES="$3" python -m obtune.eval_vllm --config "$1" --mode ckpt-select \
    --adapter-root "$PWD/$2" >> "$LOG" 2>&1 || { say "WARN: ckpt-select failed for $4"; return 1; }
}

eval_system() {  # $1 = system, $2 = gpu
  say "evaluating $1 on GPU $2 (7 conditions x 557 held-out programs)"
  CUDA_VISIBLE_DEVICES="$2" python -m obtune.eval_vllm --config eval/mono_gate.yaml \
    --systems "$1" >> "$LOG" 2>&1 || say "WARN: eval failed for $1"
}

say "=== Gate 0 start (mono GPU $MONO_GPU, control GPU $CTL_GPU) ==="

# The control finishes long before mono, so its whole chain runs first on its own GPU.
if wait_for_adapter "$CTL_DIR" "L0 control"; then
  select_ckpt train/grid_qwen1.5b_py_L0.yaml "$CTL_DIR" "$CTL_GPU" "L0 control"
  eval_system tuned_L0 "$CTL_GPU"
  eval_system base "$CTL_GPU"
else
  say "continuing without the L0 control — the gate contrast will be unavailable"
fi

if wait_for_adapter "$MONO_DIR" "mono"; then
  select_ckpt train/mono_qwen1.5b_py.yaml "$MONO_DIR" "$MONO_GPU" "mono"
  eval_system mono_all "$MONO_GPU"
else
  say "ABORT: mono adapter unavailable; nothing to gate on"; exit 1
fi

say "=== collating ==="
python -m obtune.trial_table >> "$LOG" 2>&1
python - "$DECISION" <<'PY' 2>&1 | tee -a "$LOG"
import json, sys
sys.path.insert(0, "src")
import pandas as pd
from obtune.control_relative import bootstrap_delta

out_path = sys.argv[1]
df = pd.read_parquet("results/trials.parquet")
df = df[(df.language == "python") & (df.phase == "main")]
if df.empty:
    print("no phase=main trials"); raise SystemExit(0)

cells = df.groupby(["adapter_arch", "eval_cond"])["snippet_id"].apply(set)
common = set.intersection(*cells.tolist())
d = df[df.snippet_id.isin(common)]
conds = [c for c in ["L0","L1b","L1r","L2","S1","S2","H1"] if c in set(d.eval_cond)]
cell = lambda arch, c: d[(d.adapter_arch == arch) & (d.eval_cond == c)]

print(f"\nheld-out programs in common: {len(common)}   trials: {len(d)}\n")
print(f"{'system':14}" + "".join(f"{c:>8}" for c in conds))
acc = {}
for label, arch in (("base","none"), ("tuned_L0","per_type"), ("mono_all","mono")):
    row = {c: (cell(arch, c).correct.mean() if len(cell(arch, c)) else None) for c in conds}
    acc[label] = row
    print(f"{label:14}" + "".join(f"{row[c]:8.3f}" if row[c] is not None else f"{'--':>8}" for c in conds))

print("\nmono - L0 control  (+ = breadth of obfuscation training buys something)")
print(f"{'eval':6}{'delta':>9}{'CI95':>20}{'verdict':>16}")
contrasts = {}
for c in conds:
    t, ctl = cell("mono", c), cell("per_type", c)
    if not len(t) or not len(ctl):
        continue
    con = bootstrap_delta(t, ctl, c, n_resamples=4000, eq_margin=(4.0 if c == "H1" else 3.0))
    contrasts[c] = con.to_dict()
    print(f"{c:6}{con.value_pts:>+9.1f}{f'[{con.ci_lo:+.1f},{con.ci_hi:+.1f}]':>20}{con.verdict:>16}")

h1 = contrasts.get("H1")
if h1 is None:
    verdict, run_grid = "no_h1_cells", True
elif h1["value_pts"] > 0 and h1["excludes_zero"]:
    verdict, run_grid = "INVARIANCE__breadth_generalizes", False
elif h1["value_pts"] < 0 and h1["excludes_zero"]:
    # Missing branch: a significantly NEGATIVE delta fell through to
    # "inconclusive/underpowered", which is the opposite of what it means.
    verdict, run_grid = "BREADTH_HURTS__worse_than_clean_code_control", True
elif h1.get("equivalent"):
    verdict, run_grid = "NO_TRANSFER__breadth_does_not_reach_heldout", True
else:
    verdict, run_grid = "INCONCLUSIVE__underpowered_on_H1", True

json.dump({
    "gate": "mono_all vs tuned_L0 on held-out H1",
    "n_programs_common": len(common), "n_trials": int(len(d)),
    "accuracy": acc, "contrasts_vs_control": contrasts,
    "h1_verdict": verdict, "launch_per_condition_grid": run_grid,
    "note": ("mono is NOT size-matched to a per-condition adapter (~27k vs ~4.7k pairs): "
             "the simple approach is given every advantage, so a failure here is decisive "
             "while a success needs a size-matched arm to separate breadth from volume."),
}, open(out_path, "w"), indent=2)
print(f"\nVERDICT: {verdict}")
print(f"launch per-condition grid: {run_grid}")
PY

RUN_GRID=$(python -c "import json;print(json.load(open('$DECISION'))['launch_per_condition_grid'])" 2>/dev/null || echo True)
VERDICT=$(python -c "import json;print(json.load(open('$DECISION'))['h1_verdict'])" 2>/dev/null || echo unknown)
say "gate verdict: $VERDICT"

if [ "$RUN_GRID" = "True" ]; then
  say "breadth did not settle it — rebuilding the queue with RQ1 + RQ2 and launching workers"
  python scripts/build_manifest.py --train "configs/train/grid_qwen1.5b_*.yaml" \
      --eval configs/eval/grid_rq1.yaml --rq2 configs/eval/grid_rq1.yaml \
      --seeds 17 42 --clear >> "$LOG" 2>&1
  bash scripts/launch_workers.sh >> "$LOG" 2>&1 && say "grid workers launched" \
    || say "WARN: could not launch grid workers (no idle GPU?) — queue is still in runs/manifest/queued/"
else
  say "breadth DOES generalize — per-condition grid deliberately NOT launched; it is moot."
  say "next step is a SIZE-MATCHED mono arm to separate 'breadth helps' from 'more data helps'."
fi

say "=== Gate 0 complete — decision in $DECISION ==="
