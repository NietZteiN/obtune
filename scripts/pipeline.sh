#!/usr/bin/env bash
# Run every remaining experiment, in order, unattended.
#
#   setsid nohup bash scripts/pipeline.sh > runs/logs/pipeline.log 2>&1 < /dev/null &
#   bash scripts/pipeline.sh --status
#
# WHY THIS EXISTS, given supervise.sh already runs
# -----------------------------------------------
# `supervise.sh` keeps the GPUs fed from ONE queue and exits when that queue drains. It
# is a worker pool, not a plan: it has no notion of "and then run the next experiment".
# This script is the plan. It advances through stages, enqueues each stage's GPU work,
# waits for it, and moves on — so the whole remaining programme runs from one launch.
#
# The two are complementary and both should be running: this fills the queue, the
# supervisor keeps workers alive on whatever GPUs are free. If the supervisor has exited
# (queue was empty at the time), this restarts it.
#
# CPU USE
# -------
# The box has 96 cores and the GPU work leaves nearly all of them idle. Every CPU-only
# stage (variant generation, pair emission, gate execution, analysis) is launched
# IMMEDIATELY and in the background, so it overlaps GPU stages instead of queuing behind
# them. `CPU_WORKERS` sizes those pools; the executor is the heavy user, and it is
# subprocess-bound rather than GIL-bound, so it scales close to linearly with cores.
#
# RESUMABILITY
# ------------
# Every stage writes a marker under runs/manifest/.pipeline/ when it finishes. Re-running
# skips completed stages, so a crash, a reboot, or a deliberate restart costs nothing.
# Each underlying step is itself idempotent (train_sft skips a finished adapter,
# eval_vllm skips a written cell, the emitters overwrite deterministically).
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

CPU_WORKERS="${CPU_WORKERS:-64}"     # of 96 cores; leaves headroom for the GPU jobs' loaders
POLL="${POLL:-60}"
STATE=runs/manifest/.pipeline
LOG=runs/logs/pipeline.log
LOCK=$STATE/.lock
mkdir -p "$STATE" runs/logs

STAGES_ALL="icl_baseline zero_train_baselines icl_ksweep gridA_baselines mole_routing oracle_bound cpu_s3s4_data gpu_inflight gpu_s3s4_adapters gpu_s3s4_eval gpu_srh7b_eval gpu_seed42 gpu_overtrain cpu_geometry gpu_merge_sweep gpu_unlearn analysis attrib_evals attrib_js_train attrib_js_eval attrib_analysis t2_overtrain t2_geometry t2_epoch_sweep_full t2_merge_optimal t2_controls p3_composites p3_mole_train p3_mole_eval gridA_refill gridB_s3s4 l0ctl_train l0ctl_merge l0ctl_eval loto_train loto_eval merge_headroom_build merge_headroom_eval gate_probe gate_retrain_balanced gate_eval_balanced gate_routing_analysis fill22"

# stdout is already the log when this runs detached (see the launch line at the top),
# and the terminal when run by hand — so `tee -a "$LOG"` wrote every line twice.
say() { echo "[$(date -u +%F' '%H:%M:%S)] $*"; }
done_marker() { [ -f "$STATE/$1.done" ]; }
mark_done()   { date -u +%FT%TZ > "$STATE/$1.done"; say "stage '$1' COMPLETE"; }
# A stage that skips still marks itself done (so the pipeline advances), which means a
# completed run and a run where half the stages produced nothing look identical in the
# markers. Record WHY, so the final summary can say what did not happen — otherwise
# "pipeline COMPLETE" overnight is indistinguishable from "pipeline did nothing".
mark_skipped() { printf '%s\n' "$2" > "$STATE/$1.skipped"; say "stage '$1': SKIPPED — $2"; }

if [ "${1:-}" = "--status" ]; then
  echo "pipeline: $(pgrep -f 'pipeline.sh$' | grep -v $$ | wc -l) process(es)"
  echo "stages:"
  for s in $STAGES_ALL; do
    if done_marker "$s"; then echo "  [x] $s   ($(cat "$STATE/$s.done"))"; else echo "  [ ] $s"; fi
  done 2>/dev/null
  echo "queue: queued=$(ls runs/manifest/queued/*.json 2>/dev/null|wc -l)" \
       "running=$(ls runs/manifest/running/*/*.json 2>/dev/null|wc -l)" \
       "done=$(ls runs/manifest/done/*.json 2>/dev/null|wc -l)" \
       "failed=$(ls runs/manifest/failed/*.json 2>/dev/null|wc -l)"
  bash scripts/launch_workers.sh --status
  exit 0
fi

# Single instance. A stale lock from a killed run must not block forever.
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  say "another pipeline is alive (pid $(cat "$LOCK")) — exiting"; exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

# --------------------------------------------------------------------------- #
# Infrastructure kept alive on every loop, not just at start.

# A worker loads obtune.sched.worker ONCE, at process start. Every scheduler fix made
# afterwards is inert in it until it restarts — and because `launch_workers.sh` skips a
# GPU that already has a live worker, a long-lived worker never picks the fix up on its
# own. That is not hypothetical: on 2026-08-09 all four workers predated the dependency
# handling in worker.py, so `depends_on` was ignored and ckpt-select ran 23 minutes before
# its training job finished, taking the S3/S4 python evaluation down with it.
#
# Warn only. Restarting a worker mid-job would abandon hours of training, so the decision
# stays with a human; what must not happen is the staleness being invisible.
warn_stale_workers() {
  local src=src/obtune/sched/worker.py pid start_s src_s
  [ -f "$src" ] || return 0
  src_s=$(stat -c %Y "$src" 2>/dev/null) || return 0
  for f in runs/manifest/workers/*.pid; do
    [ -e "$f" ] || continue
    pid=$(cat "$f" 2>/dev/null) || continue
    kill -0 "$pid" 2>/dev/null || continue
    start_s=$(stat -c %Y "/proc/$pid" 2>/dev/null) || continue
    if [ "$src_s" -gt "$start_s" ]; then
      say "WARNING: worker $(basename "$f" .pid) (pid $pid) started before the current"
      say "         $src — scheduler fixes in it are NOT active. Restart it when idle."
    fi
  done
}

ensure_infra() {
  # Workers on every free GPU. Idempotent: live workers are skipped.
  bash scripts/launch_workers.sh >> "$LOG" 2>&1
  warn_stale_workers
  # A worker killed mid-job leaves its claim in running/; nothing else moves it back, and
  # `queue_busy` counts running/, so one stranded claim makes `drain` wait forever.
  # The sweep is owner-based (worker.is_orphaned): it requeues a claim only once the pid
  # that took it is provably dead. The earlier version keyed on "no worker holds this
  # tag", which silently did nothing whenever a replacement worker had been started on
  # the same GPU — precisely the case that strands a claim.
  python -m obtune.sched.worker --sweep-orphans 2>&1 | grep -v "^requeued 0 " | tee -a "$LOG" >/dev/null
  # A dead job strands TWO things and only the claim was previously recoverable. vLLM's
  # engine child is reparented to init and keeps its ~41 GB KV-cache reservation, and the
  # worker refuses any GPU with >2 GB used — so on 2026-08-11 all four GPUs sat at 0%
  # utilisation holding 164 GB while seven jobs waited. Nothing self-healed; it took a
  # human. This reaps only OUR orphaned engines on GPUs with no live claim.
  python -m obtune.sched.worker --reap-stranded-gpus 2>&1 \
    | grep -v "^reaped 0 " | tee -a "$LOG" >/dev/null
  # A job can also fail WITHOUT exiting. On 2026-08-11 two evals raised a guard error and
  # then hung in multiprocessing's atexit handler joining a vLLM EngineCore that never
  # terminates: the traceback reached the job log, the process stayed alive and asleep, the
  # claim never left running/, and this drain loop waited 18 hours on a queue that could not
  # empty. `is_orphaned` cannot see it (the owner is alive) and the engine reaper cannot
  # (the parent is alive). CPU time is the discriminator.
  python -m obtune.sched.worker --kill-stalled 2>&1 \
    | grep -v "^failed 0 " | tee -a "$LOG" >/dev/null
  # supervise.sh exits when the queue empties; we refill it, so bring it back.
  # The watchdog restarts THIS script if it dies; nothing restarted the watchdog, which made
  # it the last unsupervised link in the chain. Resurrect it here so the two cover each
  # other: whichever survives brings the other back. Both hold single-instance locks, so a
  # double start is a no-op rather than a race. (If both die in the same instant nothing
  # recovers — that is unchanged, and is what the `--status` commands are for.)
  if ! pgrep -f "bash scripts/watchdog.sh$" >/dev/null 2>&1; then
    setsid nohup bash scripts/watchdog.sh >> runs/logs/watchdog.log 2>&1 < /dev/null &
    disown 2>/dev/null || true
    say "restarted watchdog"
  fi
  if ! pgrep -f "supervise.sh$" >/dev/null 2>&1; then
    # The budget is NOT computed here. supervise.sh reads scheduler_policy.gpu_budget
    # itself, so there is exactly one reader and no value to get stale across the exec.
    # Computing it here and exporting it is what produced a 4-GPU budget against an
    # allowed_gpus of [0, 1] on 2026-08-11.
    setsid nohup bash scripts/supervise.sh >> runs/logs/supervisor.log 2>&1 < /dev/null &
    disown 2>/dev/null || true
    say "restarted supervisor"
  fi
}

# A gate failure in the 2026-08-14 stages SKIPS that stage instead of aborting the run.
# Those stages are independent of one another (a Grid A refill has nothing to do with the
# LOTO folds), so killing the programme for one bad config wastes the rest of the night —
# and under watchdog.sh an `exit 1` becomes a restart loop that re-aborts at the same
# point. The earlier stages keep the original abort semantics: they are a dependency chain,
# where continuing past a failure really does produce garbage.
gate_or_skip() {  # gate_or_skip <stage>  -> 0 to proceed, 1 to skip the stage
  if gate "$1" --queued; then return 0; fi
  mark_skipped "$1" "preflight rejected the queued job(s) - later stages still run"
  rm -f runs/manifest/queued/*.json
  return 1
}

queue_busy() {
  local q r
  q=$(ls runs/manifest/queued/*.json 2>/dev/null | wc -l)
  r=$(ls runs/manifest/running/*/*.json 2>/dev/null | wc -l)
  [ $((q + r)) -gt 0 ]
}

# Wait for the GPU queue to drain, keeping infrastructure alive while we wait.
#
# CONFIRM THE QUEUE IS EMPTY BEFORE BELIEVING IT. A worker claims a job by moving the file
# from queued/ to running/<tag>/, and a poll landing inside that move sees it in NEITHER —
# so a single observation of "empty" is not evidence the work is done. On 2026-08-13 that
# race ended `p3_mole_train` 94 seconds after it started, while the gate was still training
# for its full three hours; `p3_mole_eval` then found no checkpoint and skipped, and the
# pipeline reported COMPLETE with the real work still in flight.
#
# Requiring N consecutive empty polls costs N*POLL seconds once per stage and removes the
# whole class of transition-window false negatives.
drain() {
  local label="$1" waited=0 empty=0
  local need_empty="${DRAIN_CONFIRM:-3}"
  while true; do
    if queue_busy; then
      empty=0
    else
      empty=$((empty + 1))
      if [ "$empty" -ge "$need_empty" ]; then break; fi
      say "  ...$label: queue looks empty ($empty/$need_empty confirmations)"
    fi
    ensure_infra
    sleep "$POLL"; waited=$((waited + POLL))
    if [ $((waited % 900)) -lt "$POLL" ]; then
      say "  ...$label: queued=$(ls runs/manifest/queued/*.json 2>/dev/null|wc -l)" \
          "running=$(ls runs/manifest/running/*/*.json 2>/dev/null|wc -l)" \
          "failed=$(ls runs/manifest/failed/*.json 2>/dev/null|wc -l)"
    fi
  done
}

# CPU stages run detached and are NOT waited on by the GPU stages — that overlap is the
# whole point. `cpu_wait` is called only where a later stage genuinely needs the output.
CPU_PIDS=""
cpu_bg() {  # cpu_bg <marker> <command...>
  local marker="$1"; shift
  done_marker "$marker" && return 0
  say "CPU stage '$marker' starting in background (${CPU_WORKERS} workers)"
  ( "$@" >> "runs/logs/cpu_${marker}.log" 2>&1 && mark_done "$marker" \
      || say "CPU stage '$marker' FAILED — see runs/logs/cpu_${marker}.log" ) &
  CPU_PIDS="$CPU_PIDS $!"
}
cpu_wait() { for p in $CPU_PIDS; do wait "$p" 2>/dev/null; done; CPU_PIDS=""; }

# --------------------------------------------------------------------------- #
# PREFLIGHT GATE. Every defect this pipeline has hit so far was visible in a config
# before a single GPU-second was spent: a 7B eval inheriting a 1.5B adapter, an eval
# whose output path collided with a finished run and destroyed it, a job whose
# depends_on named something that would never be queued. Validate, then run.
#
# Re-checked before each drain, not only at startup, because stages ENQUEUE new jobs —
# a config that was fine at t=0 says nothing about the job written at stage 3.
gate() {  # gate <label> [--queued]
  local label="$1"; shift
  if python scripts/preflight.py "$@" >> "$LOG" 2>&1; then
    say "preflight OK ($label)"
    return 0
  fi
  say "PREFLIGHT FAILED ($label) — refusing to run. Errors:"
  python scripts/preflight.py "$@" 2>&1 | grep ERROR | tee -a "$LOG"
  return 1
}

say "=== pipeline start (CPU_WORKERS=$CPU_WORKERS, poll ${POLL}s) ==="
gate startup || { say "=== pipeline ABORTED at preflight ==="; exit 1; }
ensure_infra

# --------------------------------------------------------------------------- #
# STAGE 1 (CPU, immediate) — S3/S4 have gate-validated variants but no training pairs
# and no eval items, so their adapters cannot be trained and they cannot enter the
# transfer matrix. Pure CPU; overlaps everything below.
# The TESTSET variants must be generated before their eval items can be emitted: the
# earlier run built only --target train, so the testset emitter found `missing_variants`
# and wrote 0 items. Each step is idempotent, so re-running the whole chain is safe.
cpu_bg cpu_s3s4_data bash -c "
  python scripts/05_build_variants.py --target testset --conditions S3 S4 --workers $CPU_WORKERS &&
  python scripts/06_emit_pairs.py --conditions S3 S4 &&
  python scripts/07_emit_eval_items.py --conditions S3 S4 --source heldout &&
  python scripts/07_emit_eval_items.py --conditions S3 S4 --source testset &&
  python scripts/check_manifest.py --rebuild"

# --------------------------------------------------------------------------- #
# STAGE 2 (GPU) — whatever is already queued: 7B rev, seed-42 replicates, the repaired
# RQ2 chain, and the 1.5B bidirectional eval re-run.
if ! done_marker gpu_inflight; then
  say "stage 'gpu_inflight': draining the current queue"
  drain gpu_inflight
  mark_done gpu_inflight
fi

# --------------------------------------------------------------------------- #
# STAGE 3 (GPU) — per-condition adapters for the S2 split. Needs stage 1's pairs.
if ! done_marker gpu_s3s4_adapters; then
  cpu_wait
  if [ -s data/train/pairs/S3/python.jsonl ] && [ -s data/train/pairs/S4/python.jsonl ]; then
    say "stage 'gpu_s3s4_adapters': enqueuing S3/S4 adapters"
    python scripts/build_manifest.py \
      --train configs/train/grid_qwen1.5b_py_S3.yaml configs/train/grid_qwen1.5b_py_S4.yaml \
              configs/train/grid_qwen1.5b_js_S3.yaml configs/train/grid_qwen1.5b_js_S4.yaml \
      --seeds 17 >> "$LOG" 2>&1
    gate gpu_s3s4_adapters --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain gpu_s3s4_adapters
    mark_done gpu_s3s4_adapters
  else
    mark_skipped gpu_s3s4_adapters "S3/S4 pairs were not produced"
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE 3b (GPU) — evaluate what stage 3 just trained.
#
# Without this the pipeline spent ~16-24 GPU-h producing four adapters that NOTHING
# consumed: grid_v1.yaml still declares six train_conditions, so S3/S4 would never have
# entered a transfer matrix and the S2-split experiment would have produced no result at
# all while every stage reported success. Guarded on the adapters rather than on stage 3's
# marker, so a partial stage 3 cannot be evaluated as though it were complete.
if ! done_marker gpu_s3s4_eval; then
  have_all=1
  for lang in python javascript; do
    for cond in S3 S4; do
      # `best`, not `final`: a per_type eval loads the CHECKPOINT-SELECTED adapter, so
      # guarding on `final` passed while the artifact the eval actually needs was absent.
      # That is exactly what happened — training finished, ckpt-select had failed, the
      # guard saw `final` and let the eval run straight into LoRAAdapterNotFoundError.
      [ -d "runs/adapters/qwen25c-1.5b/$lang/${cond}_r32_s17/best" ] || have_all=0
    done
  done
  if [ "$have_all" -eq 1 ]; then
    say "stage 'gpu_s3s4_eval': all four S3/S4 adapters present — enqueuing the expansion"
    prio=52
    for lang in python javascript; do
      cat > "runs/manifest/queued/052_evals3s4__qwen25c-1.5b_${lang}.json" <<JSON
{"job_id": "evals3s4__qwen25c-1.5b_${lang}", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/grid_s3s4_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "${lang}"],
 "raw": false, "est_gpu_h": 1.5, "priority": ${prio},
 "meta": {"experiment": "rq1/s2-split", "stage": "gpu_s3s4_eval", "language": "${lang}"}}
JSON
    done
    gate gpu_s3s4_eval --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain gpu_s3s4_eval
    mark_done gpu_s3s4_eval
  else
    mark_skipped gpu_s3s4_eval "not all four S3/S4 adapters were trained"
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE 4 (GPU) — the 7B bidirectional evaluation, once its arms exist. Guarded on the
# adapters rather than on a stage marker: the arms are trained by stage 2's queue, and a
# missing one would otherwise be evaluated as base weights under a tuned label.
if ! done_marker gpu_srh7b_eval; then
  need_rev=runs/adapters_srh/qwen25c-7b/python/all5_rev_r32_s17/final
  need_flip=runs/adapters_srh/qwen25c-7b/python/all5_flip_r32_s17/final
  if [ -d "$need_rev" ] && [ -d "$need_flip" ]; then
    say "stage 'gpu_srh7b_eval': 7B arms present — enqueuing the bidirectional eval"
    cat > runs/manifest/queued/055_evalsrh__qwen25c-7b__python.json <<'JSON'
{"job_id": "evalsrh__qwen25c-7b__python", "kind": "eval-cell",
 "argv": ["-m", "obtune.cft.evaluate", "--config", "srh/eval/e1_qwen7b.yaml"],
 "raw": false, "est_gpu_h": 2.0, "priority": 55,
 "meta": {"experiment": "srh/exp1", "stage": "gpu_srh7b_eval"}}
JSON
    gate gpu_srh7b_eval --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain gpu_srh7b_eval
    mark_done gpu_srh7b_eval
  else
    mark_skipped gpu_srh7b_eval "7B rev/flip adapters not present"
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE 5 (GPU) — the second seed. CLAUDE.md §4 is explicit that a single run is a data
# point, not a conclusion, and the writeup's headline differences rest on `rev`/`flip`/
# `mix50`. Enqueued last because it is a replication, not a new question: if the box has
# to stop early, the thing lost should be the confirmation and not the result.
# NOTE the entry point. SRH arms train with `obtune.srh.train`, not `obtune.train_sft`,
# and their adapters live under runs/adapters_srh/ via `adapter_root`.
# `build_manifest.py --train` hard-codes train_sft and computes adapter paths with
# train_sft.adapter_dir, so pointing it at an srh config would emit a job that trains a
# PLAIN FORWARD adapter under an SRH arm's name and writes it to the wrong root — the same
# silent-mislabelling failure as the duplicate-YAML-key bug. Use the srh enqueuer.
if ! done_marker gpu_seed42; then
  n_s42=$(ls runs/manifest/queued/*s42*.json runs/manifest/running/*/*s42*.json \
             runs/manifest/done/*s42*.json 2>/dev/null | wc -l)
  if [ "$n_s42" -gt 0 ]; then
    say "stage 'gpu_seed42': $n_s42 seed-42 arm(s) already queued/done — draining, not re-enqueuing"
  else
    say "stage 'gpu_seed42': enqueuing seed-42 replicates via the srh enqueuer"
    python scripts/srh/21_enqueue_e1_arms.py --stage 1 --seed 42 --write >> "$LOG" 2>&1 \
      || say "  WARNING: srh enqueue failed — see $LOG"
  fi
  gate gpu_seed42 --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain gpu_seed42
  mark_done gpu_seed42
fi

# --------------------------------------------------------------------------- #
# STAGE 6a (GPU) — the overtraining probe (Part V). Drains whatever the 9-epoch configs
# queued. Guarded on the ADAPTERS rather than on a marker, so a half-finished probe is not
# analysed as if it were complete.
if ! done_marker gpu_overtrain; then
  say "stage 'gpu_overtrain': draining the 9-epoch probe"
  drain gpu_overtrain
  n_ot=$(ls -d runs/adapters_overtrain/qwen25c-1.5b/python/*/ 2>/dev/null | wc -l)
  say "stage 'gpu_overtrain': $n_ot overtrained adapter(s) present"
  mark_done gpu_overtrain
fi

# --------------------------------------------------------------------------- #
# STAGE 6b (CPU) — task-vector geometry for BOTH banks. This is the readout that decides
# whether Horoi et al.'s interference mechanism appears once the experts are actually
# overtrained; on the 3-epoch bank it does not (d(sign_conflict) = -0.011). CPU only.
if ! done_marker cpu_geometry; then
  say "stage 'cpu_geometry': task-vector geometry, 3-epoch and 9-epoch banks"
  ( python scripts/merge/20_geometry_report.py --root runs/adapters
    # The probe covers L1b/S1/S2 only; the script skips absent conditions rather than failing.
    if [ -d runs/adapters_overtrain/qwen25c-1.5b/python ]; then
      python scripts/merge/20_geometry_report.py --root runs/adapters_overtrain \
        --conditions L1b S1 S2
    else
      echo "no overtrain bank yet — skipping the 9-epoch readout"
    fi ) >> runs/logs/cpu_geometry.log 2>&1
  n_geo=$(ls results/merge_geometry/*.json 2>/dev/null | wc -l)
  say "stage 'cpu_geometry': $n_geo geometry report(s)"
  [ "$n_geo" -eq 0 ] && say "  WARNING: no geometry reports — see runs/logs/cpu_geometry.log"
  mark_done cpu_geometry
fi

# --------------------------------------------------------------------------- #
# STAGE 6c (GPU) — merge quality vs expert training length (Part V, Stage 1). The merges are
# UNIFORM-epoch, which is the control the existing merges lack: they are built from `best`,
# and ckpt_select picked a different epoch per condition, so no existing number separates
# "merging is lossy" from "we merged mismatched vectors". Merging is CPU-only and idempotent;
# only the eval needs a GPU.
if ! done_marker gpu_merge_sweep; then
  if [ ! -f configs/eval/merge_epoch_sweep_qwen25c-1.5b_python.yaml ]; then
    say "stage 'gpu_merge_sweep': building uniform-epoch merges"
    python scripts/merge/21_epoch_sweep.py --enqueue >> runs/logs/cpu_merge_sweep.log 2>&1 \
      || say "  WARNING: merge sweep build failed — see runs/logs/cpu_merge_sweep.log"
  fi
  gate gpu_merge_sweep --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain gpu_merge_sweep
  mark_done gpu_merge_sweep
fi

# --------------------------------------------------------------------------- #
# STAGE 6d (GPU) — approximate unlearning by task-vector negation (Part IV, Stage 1).
# U(lambda) = FLIP - lambda*FWD. Exact weight-space arithmetic, so no training is needed —
# the arms already exist. lambda=0 reproduces FLIP to 1e-7, which is the built-in correctness
# check and is evaluated rather than assumed.
if ! done_marker gpu_unlearn; then
  if [ ! -f configs/unlearn/negation_qwen25c-1.5b_python.yaml ]; then
    say "stage 'gpu_unlearn': building the negation sweep"
    python scripts/unlearn/20_negation_sweep.py --enqueue >> runs/logs/cpu_unlearn.log 2>&1 \
      || say "  WARNING: negation sweep build failed — see runs/logs/cpu_unlearn.log"
  fi
  gate gpu_unlearn --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain gpu_unlearn
  mark_done gpu_unlearn
fi

# --------------------------------------------------------------------------- #
# STAGE 7 (CPU) — analysis over whatever landed. Cheap, and safe to re-run.
if ! done_marker analysis; then
  say "stage 'analysis': transfer matrix + bidirectional reports"
  # `find` rather than a fixed-depth glob. The results path gained a run_tag level when
  # two evaluations were found colliding on one directory, and the old
  # `results/*_cft-bidirectional/*/*/` pattern then matched the LANGUAGE directory —
  # which holds no summary.json. The stage would have completed, reported success, and
  # generated nothing at all. Depth-independent matching cannot regress that way again.
  # Exit codes are CHECKED here. `obtune.transfer` has always exited 1 when its filter
  # matches no rows, but this stage ran it inside an unchecked subshell and then marked
  # itself complete regardless — so RQ1's transfer matrix was silently absent while the
  # pipeline reported success. Both languages, both reported.
  for lang in python javascript; do
    if python -m obtune.transfer --model qwen25c-1.5b --language "$lang" \
         >> runs/logs/cpu_analysis.log 2>&1; then
      say "stage 'analysis': transfer matrix OK (qwen25c-1.5b/$lang)"
    else
      say "stage 'analysis': WARNING transfer FAILED for qwen25c-1.5b/$lang — see runs/logs/cpu_analysis.log"
    fi
  done
  ( n=0
    while IFS= read -r sfile; do
      python scripts/cft/12_report.py "$(dirname "$sfile")" && n=$((n + 1))
    done < <(find results -name summary.json -path "*cft-bidirectional*" | sort)
    echo "generated $n bidirectional report(s)" ) >> runs/logs/cpu_analysis.log 2>&1
  n_rep=$(find results -name report.md -path "*cft-bidirectional*" | wc -l)
  say "stage 'analysis': $n_rep bidirectional report(s) present"
  [ "$n_rep" -eq 0 ] && say "  WARNING: analysis produced no reports — check runs/logs/cpu_analysis.log"
  mark_done analysis
fi

# ==========================================================================- #
# ATTRIB WORKSHOP CHAIN (paper deadline Sept 1, results freeze Aug 28).
#
# Ordered by what can change the paper, not by cost. The dose curve is first because it is
# the only remaining experiment that can change the CLAIM TYPE: everything else sharpens a
# refutation, while a curve that saturates at 5-10 % reverse data turns the paper into a
# prescription. The JavaScript replication is last among the experiments because it is the
# only one needing new training, and the freeze rule says an unlanded item ships as a
# limitation rather than a delay.
#
# Every stage guards on its ARTIFACTS, so a half-finished predecessor is skipped with a
# logged reason rather than analysed as if complete.

# --- the three independent ATTRIB evaluations, enqueued TOGETHER -------------- #
#
# One stage, not three. Each of these evaluations is independent of the other two, but a
# stage enqueues its job and then `drain`s the WHOLE queue before the next stage begins — so
# running them as separate stages left three of four GPUs idle for ~2.5 hours and serialised
# work that has no dependency between its parts. Enqueued together they occupy three cards
# and the stage costs about as long as its slowest member (the 7B four-strategy run).
#
# The cost of merging is diagnostic: a bad config now surfaces alongside two others rather
# than alone. That is acceptable here because all three already pass `preflight` and dry-run
# enqueue cleanly, and each job still lands its own failure record with its own log.
#
#   dose        sft(0%) -> mix5 -> mix10 -> mix25 -> mix50   (the claim-type experiment)
#   seeds       E2 between-seed variance, all six arms at s42
#   strategies  flip/mix50 x 4 prompting strategies at 7B    (closes the E7 asymmetry)
if ! done_marker attrib_evals; then
  n_enq=0
  if [ -d runs/adapters_srh/qwen25c-1.5b/python/all5_mix5_r32_s17/final ]; then
    python scripts/srh/22_enqueue_evals.py srh/eval/e3_dose_qwen1.5b.yaml --write >> "$LOG" 2>&1 \
      && n_enq=$((n_enq + 1)) || say "  WARNING: dose enqueue failed"
  else
    say "  skipping dose: mix5 arm absent"
  fi
  if [ -d runs/adapters_cft/qwen25c-1.5b/python/sft_r32_s42/final ]; then
    python scripts/srh/22_enqueue_evals.py srh/eval/e2_seeds_qwen1.5b.yaml --write >> "$LOG" 2>&1 \
      && n_enq=$((n_enq + 1)) || say "  WARNING: seeds enqueue failed"
  else
    say "  skipping seeds: s42 forward arms absent"
  fi
  if [ -d runs/adapters_srh/qwen25c-7b/python/all5_mix50_r32_s17/final ]; then
    python scripts/srh/22_enqueue_evals.py srh/eval/e7_strategies_qwen7b.yaml --write >> "$LOG" 2>&1 \
      && n_enq=$((n_enq + 1)) || say "  WARNING: strategies enqueue failed"
  else
    say "  skipping strategies: 7B mix50 absent"
  fi
  say "stage 'attrib_evals': $n_enq evaluation(s) enqueued; draining"
  gate attrib_evals --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain attrib_evals
  mark_done attrib_evals
fi

# --- E3: JavaScript replication, the only new TRAINING in this chain --------- #
if ! done_marker attrib_js_train; then
  say "stage 'attrib_js_train': enqueuing the 4 JavaScript arms"
  # sft/cft come from the replication enqueuer, flip/mix50 from the SRH one; each refuses to
  # re-enqueue an arm whose adapter already exists.
  python scripts/cft/11_enqueue_arms.py --language javascript --write >> "$LOG" 2>&1 || \
    say "  note: cft JS enqueue returned non-zero (may already be trained)"
  python scripts/srh/21_enqueue_e1_arms.py --stage 1 --language javascript \
    --arms flip,mix50 --write >> "$LOG" 2>&1 || \
    say "  note: srh JS enqueue returned non-zero (may already be trained)"
  gate attrib_js_train --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain attrib_js_train
  mark_done attrib_js_train
fi

if ! done_marker attrib_js_eval; then
  have=1
  for a in runs/adapters_cft/qwen25c-1.5b/javascript/sft_r32_s17/final \
           runs/adapters_srh/qwen25c-1.5b/javascript/all5_flip_r32_s17/final; do
    [ -d "$a" ] || have=0
  done
  if [ "$have" -eq 1 ]; then
    say "stage 'attrib_js_eval': JavaScript bidirectional eval"
    python scripts/srh/22_enqueue_evals.py srh/eval/e3_javascript_qwen1.5b.yaml --write >> "$LOG" 2>&1 || true
    gate attrib_js_eval --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain attrib_js_eval
    mark_done attrib_js_eval
  else
    mark_skipped attrib_js_eval "JS arms did not all train"
  fi
fi

# --- contrasts + metric tables over everything the chain produced ------------ #
if ! done_marker attrib_analysis; then
  say "stage 'attrib_analysis': contrasts + metric tables"
  # BOTH scripts REQUIRE --run. An earlier version called 23_metric_tables.py with no
  # arguments; argparse would have exited non-zero on every invocation, the `||` would have
  # swallowed it, and the stage would have logged "unavailable" and marked itself complete
  # while producing nothing. Same silent-no-op shape as the analysis-glob depth bug.
  #
  # --factorial only applies to the 2x2 run; passing it elsewhere is an error, so it is
  # applied by name rather than unconditionally.
  n_ok=0
  ( for d in results/*_cft-bidirectional/*/*/*/; do
      [ -f "$d/summary.json" ] || continue
      echo "=== $d"
      extra=""
      case "$d" in *factorial*) extra="--factorial";; esac
      python scripts/srh/24_contrasts.py --run "$d" $extra \
        || echo "  (contrasts unavailable for $d)"
      # E7/E8 are workshop-paper tables about the BIDIRECTIONAL replication runs. The
      # unlearning sweeps live under configs/unlearn/, which 23_metric_tables cannot locate,
      # and it refuses rather than recompute the E8 echo floor on a different program set —
      # correct behaviour, so skip them by name instead of logging a failure every pass.
      case "$d" in
        *unlearn_*) echo "  (skipping metric tables: unlearning run, E7/E8 do not apply)" ;;
        *) python scripts/srh/23_metric_tables.py --run "$d" --table all \
             || echo "  (metric tables unavailable for $d)" ;;
      esac
    done ) >> runs/logs/cpu_attrib_analysis.log 2>&1
  n_ok=$(find results -name contrasts.md -newermt "-1 day" 2>/dev/null | wc -l)
  say "stage 'attrib_analysis': $n_ok contrast table(s) written"
  [ "$n_ok" -eq 0 ] && say "  WARNING: analysis produced nothing — see runs/logs/cpu_attrib_analysis.log"
  mark_done attrib_analysis
fi


# ==========================================================================- #
# ICL BASELINE — the cheapest comparator, and the one a reviewer reaches for first.
# Inference only. If a single in-condition example matches the adapters, the modularity claim
# weakens sharply; if it does not, the fine-tuning result is stronger than it looks. Either
# answer changes the write-up, so it runs before anything expensive.
if ! done_marker icl_baseline; then
  say "stage 'icl_baseline': in-context learning, incl. the held-out H1 query"
  cat > runs/manifest/queued/012_evalicl__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalicl__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/icl_cross_h1_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 1.0, "priority": 12,
 "meta": {"experiment": "baseline/icl",
          "note": "demos from TRAINABLE conditions only; H1 is the query, never the source"}}
JSON
  gate icl_baseline --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain icl_baseline
  mark_done icl_baseline
fi

# ==========================================================================- #
# ZERO-TRAINING BASELINES — symbolic normalization and 7B zero-shot.
#
# The two questions a reviewer asks before reading any adapter number:
#   1. "What does a static normalizer already recover?"  -> normalize_baseline
#   2. "Is this just a small-model artifact?"            -> zeroshot_7b
# Neither needs training, so both are cheap and both can only sharpen the write-up:
# a strong baseline reframes the contribution, a weak one strengthens it.
if ! done_marker zero_train_baselines; then
  say "stage 'zero_train_baselines': symbolic normalization + 7B zero-shot"

  # HARD GATE. The normalization arm shows the model a REWRITTEN program and grades it
  # against the ORIGINAL's stored output, so an unsound pass would not fail loudly — it
  # would score a different program and report a plausible-looking number. Executing every
  # normalized program first is the only thing standing between that and the results table.
  if ! PYTHONPATH=src python scripts/analysis/21_validate_normalized.py --language python \
        > runs/logs/cpu_normalize_soundness.log 2>&1; then
    say "  SKIP normalize_baseline: soundness gate FAILED — see runs/logs/cpu_normalize_soundness.log"
    tail -20 runs/logs/cpu_normalize_soundness.log | while read -r l; do say "    $l"; done
    mark_skipped zero_train_baselines "normalization is not behaviour-preserving"
  else
    say "  normalization soundness: $(tail -1 runs/logs/cpu_normalize_soundness.log)"
    cat > runs/manifest/queued/013_evalnorm__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalnorm__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/normalize_baseline_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 1.5, "priority": 13,
 "meta": {"experiment": "baseline/normalize",
          "note": "static rewrite then UNTUNED model; L0 cell is the cost, not an oversight"}}
JSON
    cat > runs/manifest/queued/014_eval7b__qwen25c-7b_python.json <<'JSON'
{"job_id": "eval7b__qwen25c-7b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/zeroshot_7b.yaml",
          "--model", "qwen25c-7b", "--language", "python"],
 "raw": false, "est_gpu_h": 4.0, "priority": 14,
 "meta": {"experiment": "baseline/zeroshot_7b",
          "note": "base-model panel only; no RQ1 ladder adapters exist at 7B"}}
JSON
    gate zero_train_baselines --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain zero_train_baselines
    mark_done zero_train_baselines
  fi
fi

# ==========================================================================- #
# ICL PART 2 — how many examples, and does ICL survive fine-tuning?
#
# The 2026-08-13 ICL run was k=1 throughout, because k=1 was the only shot count the frozen
# `prompts.build_prompt` could express — not because it is a natural operating point. And
# every ICL arm ran on the untuned base while every adapter arm ran zero-shot, so "adapters
# beat ICL" currently compares two things that were never combined. Both gaps close in one
# engine load; still zero training.
if ! done_marker icl_ksweep; then
  say "stage 'icl_ksweep': k in {0,1,2,4}, on the base AND on tuned_L0"
  cat > runs/manifest/queued/015_evalksweep__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalksweep__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/icl_k_sweep_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 2.0, "priority": 15,
 "meta": {"experiment": "baseline/icl_ksweep",
          "note": "k=1 column is checkable against the 2026-08-13 run; k=0 is the matched floor"}}
JSON
  gate icl_ksweep --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain icl_ksweep
  mark_done icl_ksweep
fi

# ==========================================================================- #
# THE REMAINING BASELINE + ROUTING WORK, authorised 2026-08-13.
#
# GRID RECONCILIATION IS THE POINT OF THE FIRST TWO JOBS. Every baseline so far is Grid B
# (`testset`); every RQ1/RQ2 headline is Grid A (`heldout`). CLAUDE.md forbids pooling them,
# and they are demonstrably different — `base` on H1 is 6.4% on Grid A and 11.3% on Grid B.
# Until the baselines exist on Grid A, no baseline-vs-adapter sentence can be written.
# These spend a logged H1 `final_eval` access, explicitly authorised rather than assumed.
if ! done_marker gridA_baselines; then
  say "stage 'gridA_baselines': zero-training baselines on the adapter grid (1.5B + 7B)"
  cat > runs/manifest/queued/016_evalgA15__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalgA15__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/baselines_gridA_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 6.0, "priority": 16,
 "meta": {"experiment": "baseline/gridA", "note": "unblocks every baseline-vs-adapter claim"}}
JSON
  cat > runs/manifest/queued/017_evalgA7b__qwen25c-7b_python.json <<'JSON'
{"job_id": "evalgA7b__qwen25c-7b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/baselines_gridA_7b.yaml",
          "--model", "qwen25c-7b", "--language", "python"],
 "raw": false, "est_gpu_h": 20.0, "priority": 17,
 "meta": {"experiment": "baseline/gridA_7b", "note": "no RQ1 ladder adapters exist at 7B"}}
JSON
  gate gridA_baselines --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain gridA_baselines
  mark_done gridA_baselines
fi

# The two routing questions the design doc reserved and nothing has since asked.
# `routing_report.json` still records `n_heldout: 0`: the router has only ever been scored on
# conditions it was trained to recognise. `mole_hardrouter` (the trained gate argmaxed) is
# the arm that decides whether "mixture" is an honest word or whether this is a fine-grained
# hard router wearing a mixture's name.
if ! done_marker mole_routing; then
  say "stage 'mole_routing': hardrouter arm + route H1, with gate entropy"
  cat > runs/manifest/queued/018_evalmoleh1__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalmoleh1__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.mole.eval_mole", "--config", "eval/mole_h1_routing_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 2.0, "priority": 18,
 "meta": {"experiment": "part3/routing_ood", "note": "gate frozen; H1 scored, never fitted"}}
JSON
  cat > runs/manifest/queued/019_evalmolelad__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalmolelad__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.mole.eval_mole", "--config", "eval/mole_ladder_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 2.0, "priority": 19,
 "meta": {"experiment": "part3/hardrouter", "note": "adds mole_hardrouter; other arms resume"}}
JSON
  gate mole_routing --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain mole_routing
  mark_done mole_routing
fi

# Zero GPU. Re-run now that the oracle bound refuses to pool grids and reports WHY a
# condition was excluded, instead of silently skipping it.
if ! done_marker oracle_bound; then
  say "stage 'oracle_bound': per-item best-of-8 upper bound (CPU)"
  PYTHONPATH=src python scripts/analysis/20_oracle_bestof8.py >> "$LOG" 2>&1 || \
    say "  oracle bound produced no usable row — reasons are in the JSON, not an error"
  mark_done oracle_bound
fi

# ==========================================================================- #
# TIER 2 — runs AFTER the ATTRIB chain, which is deadline-critical and owns the box first.

# --- complete the 8-expert 9-epoch bank -------------------------------------- #
# The overtraining result currently rests on THREE experts. Sign conflict is a pairwise
# statistic: 3 experts give 3 pairs, 8 give 28. Measured 89/132/160 min per run, so five
# runs across four GPUs is ~3-4 h.
if ! done_marker t2_overtrain; then
  cfgs=""
  for c in L0 L1r L2 S3 S4; do
    f="configs/train/overtrain_qwen1.5b_py_${c}.yaml"
    [ -f "$f" ] && [ ! -d "runs/adapters_overtrain/qwen25c-1.5b/python/${c}_r32_s17/final" ] \
      && cfgs="$cfgs $f"
  done
  if [ -n "$cfgs" ]; then
    say "stage 't2_overtrain': enqueuing 9-epoch arms:$cfgs"
    python scripts/build_manifest.py --train $cfgs --seeds 17 >> "$LOG" 2>&1 \
      || say "  WARNING: overtrain enqueue failed"
    gate t2_overtrain --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain t2_overtrain
  else
    say "stage 't2_overtrain': all five already trained"
  fi
  mark_done t2_overtrain
fi

# --- geometry over the now-complete bank -------------------------------------- #
if ! done_marker t2_geometry; then
  n=$(ls -d runs/adapters_overtrain/qwen25c-1.5b/python/*/ 2>/dev/null | wc -l)
  say "stage 't2_geometry': task-vector geometry over $n overtrained expert(s)"
  python scripts/merge/20_geometry_report.py --root runs/adapters_overtrain \
    >> runs/logs/cpu_geometry.log 2>&1 || say "  WARNING: geometry failed"
  mark_done t2_geometry
fi

# --- Part V Stage 1: merge quality at UNIFORM epoch --------------------------- #
# Named for what it runs. This stage was called `t2_merge_optimal` until 2026-08-11 while
# actually running the epoch sweep; merge-optimal SELECTION is the separate stage below, and
# conflating them would have reported Stage 1 as evidence for Stage 2's recommendation.
# Uniform epoch also removes the heterogeneity confound: ckpt_select picked epoch 1 for L1r/S3
# and epoch 3 for L2/S2/S1/S4, so every existing merge combines task vectors of unequal
# training. Merges cost ~0.4 min each; this stage is eval-bound, not merge-bound.
if ! done_marker t2_epoch_sweep_full; then
  n=$(ls -d runs/adapters_overtrain/qwen25c-1.5b/python/*/ 2>/dev/null | wc -l)
  if [ "$n" -ge 6 ]; then
    say "stage 't2_epoch_sweep_full': uniform-epoch merges over $n experts"
    python scripts/merge/21_epoch_sweep.py --root runs/adapters_overtrain \
      --tag overtrain_full --languages python --epochs 1 3 6 9 --enqueue \
      >> runs/logs/cpu_merge_sweep.log 2>&1 || say "  WARNING: merge sweep failed"
    gate t2_epoch_sweep_full --queued || { say "=== pipeline ABORTED ==="; exit 1; }
    drain t2_epoch_sweep_full
  else
    mark_skipped t2_epoch_sweep_full "only $n overtrained experts (need >=6)"
  fi
  mark_done t2_epoch_sweep_full
fi

# --- Part V Stage 2: merge-optimal checkpoint selection ----------------------- #
# The paper's actual recommendation (Horoi et al., arXiv:2506.14126v2): task-dependent
# aggressive early stopping. `run_ckpt_select` optimises each expert's INDIVIDUAL accuracy,
# which is the objective identified as harmful to merging; this optimises MERGED accuracy
# instead. Greedy and order-dependent — 22_merge_optimal.py records the sweep order rather
# than hiding it, and a second pass over the same order is what tests convergence.
if ! done_marker t2_merge_optimal; then
  n=$(ls -d runs/adapters_overtrain/qwen25c-1.5b/python/*/ 2>/dev/null | wc -l)
  if [ "$n" -ge 6 ]; then
    for r in 1 2 3; do
      say "stage 't2_merge_optimal': greedy round $r"
      python scripts/merge/22_merge_optimal.py --root runs/adapters_overtrain \
        --round "$r" --enqueue >> runs/logs/cpu_merge_optimal.log 2>&1 \
        || { say "  WARNING: merge-optimal round $r failed to enqueue"; break; }
      gate t2_merge_optimal --queued || { say "=== pipeline ABORTED ==="; exit 1; }
      drain t2_merge_optimal
      # --collect promotes the round's winning epoch into the incumbent; the NEXT round is
      # built from that state, so this must run between rounds, not after all of them.
      python scripts/merge/22_merge_optimal.py --root runs/adapters_overtrain \
        --round "$r" --collect >> runs/logs/cpu_merge_optimal.log 2>&1 \
        || say "  WARNING: merge-optimal round $r produced no cells to collect"
    done
  else
    mark_skipped t2_merge_optimal "only $n overtrained experts (need >=6)"
  fi
  mark_done t2_merge_optimal
fi

# --- Part IV controls + the rescaled dare_linear ------------------------------ #
# `rev - lambda*sft` is the control that decides the shared-representation reading: REV never
# saw forward data, so if reverse falls there too the effect is the operator damaging any
# adapter rather than entanglement. Already run; this stage adds the remaining arm and the
# scale-corrected merge, whose collapse to 0.02-0.06 is a 7.175x magnitude artifact.
if ! done_marker t2_controls; then
  say "stage 't2_controls': remaining unlearning control + rescaled dare_linear"
  if [ -d runs/merges/scale_corrected/qwen25c-1.5b/python/dare_linear_rescaled_r32_s17 ]; then
    cat > runs/manifest/queued/054_evalrescaled__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalrescaled__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/dare_linear_rescaled_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.3, "priority": 54,
 "meta": {"experiment": "rq2/merge-artifact",
          "note": "is dare_linear's collapse purely a 7.175x scale artifact?"}}
JSON
  fi
  gate t2_controls --queued || { say "=== pipeline ABORTED ==="; exit 1; }
  drain t2_controls
  mark_done t2_controls
fi

# ==========================================================================- #
# PART III — RouterLoRA. Runs LAST: it is a fifth concurrent workstream and queues behind
# everything deadline-critical. Every stage is skippable and none blocks the ATTRIB chain.

# --- composite corpus (CPU only, ~4-6 CPU-h) ---------------------------------- #
# The test bed. A stacked variant contains TWO mechanisms, so a hard router must be wrong and
# a mixture can be right — the condition the hypothesis actually predicts. C_ codes live in
# their own ladder file and are outside TRAINABLE_CONDITIONS, so nothing in RQ1 shifts.
if ! done_marker p3_composites; then
  say "stage 'p3_composites': building the 6 stacked conditions"
  CC="C_L1r_S1 C_S1_L1r C_L1b_S1 C_L2_S4 C_L1r_S3 C_S4_S3"
  ( set -x
    python scripts/05_build_variants.py --target train --conditions $CC \
      --conditions-config conditions_composite.yaml --workers 32
    python scripts/05_build_variants.py --target testset --conditions $CC \
      --conditions-config conditions_composite.yaml --workers 32
    for c in $CC; do
      python scripts/06_emit_pairs.py --conditions "$c"
      python scripts/07_emit_eval_items.py --conditions "$c"
    done ) >> runs/logs/cpu_p3_composites.log 2>&1 \
    || say "  WARNING: composite build reported errors — see runs/logs/cpu_p3_composites.log"
  n_cov=$(python - <<'PY' 2>/dev/null || echo 0
import json, pathlib
p = pathlib.Path("data/manifests/coverage_matrix_train_composite.json")
d = json.loads(p.read_text()) if p.exists() else {}
print(min([v.get("n_common", 0) for v in d.values()] or [0]))
PY
)
  say "stage 'p3_composites': common subset = $n_cov programs"
  # Gate 0 from the plan: below ~50% coverage the composites select for short programs and
  # the pair set has to be re-picked. Reported, never silently accepted.
  [ "$n_cov" -lt 600 ] && say "  WARNING: composite coverage $n_cov is low — Gate 0 says re-pick pairs"
  mark_done p3_composites
fi

# --- gate training (~2-4 GPU-h at 1.5B; experts and base frozen) -------------- #
if ! done_marker p3_mole_train; then
  n_exp=$(ls -d runs/adapters/qwen25c-1.5b/python/*_r32_s17/best 2>/dev/null | wc -l)
  if [ "$n_exp" -ge 8 ] && [ -s data/train/pairs/C_L1r_S1/python.jsonl ]; then
    say "stage 'p3_mole_train': RouterLoRA gate over $n_exp experts"
    # --dry-run first: it asserts the loss mask is -100 on prompt tokens and that the gate is
    # the ONLY trainable component. A missed freeze is a silent full fine-tune that still
    # produces a plausible loss curve and would be attributed to "the mixture".
    if python -m obtune.mole.train_mole --config mole/routerlora_v1.yaml --dry-run \
         >> runs/logs/gpu_p3_mole.log 2>&1; then
      # Do not enqueue a second copy. The stage can be re-entered after a restart while the
      # first training job is still in flight (that is exactly what a resumed pipeline does),
      # and two gate trainings writing the same out_dir would race on gate.pt.
      if ls runs/manifest/queued/*moletrain*.json runs/manifest/running/*/*moletrain*.json \
           >/dev/null 2>&1; then
        say "stage 'p3_mole_train': a moletrain job is already queued or running — waiting"
      elif [ -f runs/mole/qwen25c-1.5b/python/routerlora_v1_s17/gate.pt ]; then
        say "stage 'p3_mole_train': gate.pt already exists — nothing to train"
      else
      cat > runs/manifest/queued/075_moletrain__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "moletrain__qwen25c-1.5b_python", "kind": "train",
 "argv": ["-m", "obtune.mole.train_mole", "--config", "mole/routerlora_v1.yaml"],
 "raw": false, "est_gpu_h": 3.0, "priority": 75,
 "meta": {"experiment": "rq2/routerlora",
          "note": "gate only; 8 experts + base frozen"}}
JSON
      fi
      gate p3_mole_train --queued || { say "=== pipeline ABORTED ==="; exit 1; }
      drain p3_mole_train
    else
      mark_skipped p3_mole_train "--dry-run failed; see runs/logs/gpu_p3_mole.log"
    fi
  else
    mark_skipped p3_mole_train "$n_exp/8 experts present, or composite pairs missing"
  fi
  mark_done p3_mole_train
fi

# --- the ladder ---------------------------------------------------------------- #
# `mole_uniform` is the PRIMARY fixed-mixture contrast, not merge_dare_ties: it is the same
# module with a = 1/8 pinned, so it differs from mole_router in exactly one way (the weights).
# merge_dare_ties differs in three at once and is a reference, not a comparator.
# `mole_random` decides what the headline may say: if mole_router ~= mole_random the gain came
# from 8 resident experts at effective rank 256, NOT from routing.
if ! done_marker p3_mole_eval; then
  gdir=runs/mole/qwen25c-1.5b/python/routerlora_v1_s17
  if [ -f "$gdir/gate.pt" ]; then
    say "stage 'p3_mole_eval': mixture ladder (uniform / random / router)"
    if [ -f configs/eval/mole_ladder_qwen1.5b.yaml ]; then
      cat > runs/manifest/queued/076_evalmole__qwen25c-1.5b_python.json <<'JSON'
{"job_id": "evalmole__qwen25c-1.5b_python", "kind": "eval-cell",
 "argv": ["-m", "obtune.mole.eval_mole", "--config", "eval/mole_ladder_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 1.5, "priority": 76,
 "meta": {"experiment": "rq2/routerlora", "note": "HF engine; batched, left-padded"}}
JSON
      gate p3_mole_eval --queued || { say "=== pipeline ABORTED ==="; exit 1; }
      drain p3_mole_eval
    else
      mark_skipped p3_mole_eval "configs/eval/mole_ladder_qwen1.5b.yaml missing"
    fi
  else
    mark_skipped p3_mole_eval "no trained gate at $gdir (p3_mole_train did not produce one)"
  fi
  mark_done p3_mole_eval
fi

# =========================================================================== #
# 2026-08-14 PROGRAMME. Ordered so the cheap gate runs before the work it gates.
# =========================================================================== #

# --------------------------------------------------------------------------- #
# STAGE — the 33 Grid A baseline cells the resume-aliasing defect swallowed.
#
# These configs RAN on 2026-08-13 and reported success while writing under half their
# cells: `cell_dir` keys on `phase` but not `eval_source`, so they resumed the Grid B
# cells sitting at the same paths. Both configs now declare `phase: baselines_gridA`
# and the 51 genuinely-Grid-A cells were MIGRATED there (not regenerated — several are
# H1 and would each cost a quarantine access). So resume now skips exactly the cells
# that are already correct and fills only the ~33 that are missing.
if ! done_marker gridA_refill; then
  say "stage 'gridA_refill': refilling the Grid A baseline panel under its own phase"
  cat > runs/manifest/queued/080_gridArefill__qwen25c-1.5b.json <<'JSON'
{"job_id": "gridArefill__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/baselines_gridA_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.8, "priority": 80,
 "meta": {"experiment": "baselines/gridA", "stage": "gridA_refill"}}
JSON
  cat > runs/manifest/queued/081_gridArefill__qwen25c-7b.json <<'JSON'
{"job_id": "gridArefill__qwen25c-7b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/baselines_gridA_7b.yaml",
          "--model", "qwen25c-7b", "--language", "python"],
 "raw": false, "est_gpu_h": 2.5, "priority": 81,
 "meta": {"experiment": "baselines/gridA", "stage": "gridA_refill",
          "note": "7B has NO Grid A base cells at all - the 21 already collected there are uninterpretable without them"}}
JSON
  if gate_or_skip gridA_refill; then
    drain gridA_refill
    mark_done gridA_refill
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE — tuned_L0 on Grid B, S3/S4 only (~10 GPU-min, not the ~1 GPU-h budgeted).
# The rest of that item was already done: `tuned_L0_k0` IS tuned_L0 on Grid B.
# Completes the row so oracle_bestof8 can bound all eight experts on ONE grid.
if ! done_marker gridB_s3s4; then
  say "stage 'gridB_s3s4': the two remaining Grid B control cells"
  cat > runs/manifest/queued/082_gridBs3s4__qwen25c-1.5b.json <<'JSON'
{"job_id": "gridBs3s4__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/tuned_L0_gridB_s3s4_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.2, "priority": 82,
 "meta": {"experiment": "rq2/control", "stage": "gridB_s3s4"}}
JSON
  if gate_or_skip gridB_s3s4; then
    drain gridB_s3s4
    mark_done gridB_s3s4
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE — the L0-merge control. THE GATE: it decides whether merge tuning is worth
# any GPU at all. If merging three clean-code adapters also reaches ~.348 on H1, then
# "merging regresses toward the control" and every merge-improvement item below is
# answering a question that has already been settled in the negative.
# Deliberately ahead of the merge headroom stage for exactly that reason.
if ! done_marker l0ctl_train; then
  say "stage 'l0ctl_train': third random-seed L0 adapter (s101)"
  if ! python scripts/build_manifest.py \
      --train configs/train/l0seed_qwen1.5b_py_s101.yaml --seeds 101 >> "$LOG" 2>&1; then
    mark_skipped l0ctl_train "build_manifest failed - no job queued, see $LOG"
  fi
  if gate_or_skip l0ctl_train; then
    drain l0ctl_train
    mark_done l0ctl_train
  fi
fi

if ! done_marker l0ctl_merge; then
  # Merging is CPU-only (device_map=None, fp32 scaffold), so it does not queue a GPU job.
  if timeout 3600 python scripts/merge/23_l0_control.py >> "$LOG" 2>&1; then
    mark_done l0ctl_merge
  elif [ $? -eq 124 ]; then
    mark_skipped l0ctl_merge "TIMED OUT after 3600s building the L0-control merges"
  else
    mark_skipped l0ctl_merge "23_l0_control.py failed - see $LOG (adapter absent?)"
  fi
fi

if ! done_marker l0ctl_eval; then
  if [ -d runs/merges/qwen25c-1.5b_python_l0control_ties/d0p5 ] \
     && [ -d runs/merges/qwen25c-1.5b_python_l0control_dare_ties/d0p5 ]; then
    say "stage 'l0ctl_eval': L0-merge control vs the real merges, matched items"
    cat > runs/manifest/queued/084_l0ctleval__qwen25c-1.5b.json <<'JSON'
{"job_id": "l0ctleval__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/l0_merge_control_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.5, "priority": 84,
 "meta": {"experiment": "rq2/l0-merge-control", "stage": "l0ctl_eval",
          "note": "spends one H1 final_eval access - the control's whole claim is on H1"}}
JSON
    if gate_or_skip l0ctl_eval; then
      drain l0ctl_eval
      mark_done l0ctl_eval
    fi
  else
    mark_skipped l0ctl_eval "the l0control merges were not built"
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE — LOTO. The OOD *dev* set the project never had (see eval/loto_qwen1.5b.yaml).
# Six mixture adapters, ~2-3 GPU-h each, then one 6x6 eval pass. This is what makes
# every later method sweep selectable without reading H1.
if ! done_marker loto_train; then
  say "stage 'loto_train': six leave-one-transform-out folds"
  if ! python scripts/build_manifest.py \
      --train configs/train/loto_qwen1.5b_py_holdL0.yaml \
            configs/train/loto_qwen1.5b_py_holdL1b.yaml \
            configs/train/loto_qwen1.5b_py_holdL1r.yaml \
            configs/train/loto_qwen1.5b_py_holdL2.yaml \
            configs/train/loto_qwen1.5b_py_holdS1.yaml \
            configs/train/loto_qwen1.5b_py_holdS2.yaml \
      --seeds 17 >> "$LOG" 2>&1; then
    mark_skipped loto_train "build_manifest failed - no folds queued, see $LOG"
  fi
  if gate_or_skip loto_train; then
    drain loto_train
    mark_done loto_train
  fi
fi

if ! done_marker loto_eval; then
  # Guarded on `best`, not `final`: a per_type eval loads the checkpoint-SELECTED adapter,
  # and guarding on `final` is what let an eval run straight into LoRAAdapterNotFoundError
  # on 2026-08-09 after ckpt-select had failed.
  # Evaluate whichever folds actually trained, not all-or-nothing.
  #
  # `validate_systems` only checks that an adapter PATH is declared, not that it exists, so
  # one missing fold would take the whole 54-cell job down inside vLLM's LoRA load — the
  # 2026-08-09 failure verbatim (ckpt-select failed, the eval ran straight into
  # LoRAAdapterNotFoundError). Guarding on all six avoided that but threw away five good
  # folds to punish one bad one. `--systems` gives the third option: run the folds that
  # exist, and say in the log which ones did not. A 5-fold diagonal is still a usable OOD
  # signal; zero folds is not.
  SYS="base,tuned_L0,mono_all"; missing=""
  for h in L0 L1b L1r L2 S1 S2; do
    tag=$(python - "$h" <<'PYEOF'
import sys
conds = ["L0","L1b","L1r","L2","S1","S2"]
print("-".join(c for c in conds if c != sys.argv[1]))
PYEOF
)
    if [ -d "runs/adapters_loto/qwen25c-1.5b/python/${tag}_r32_s17/best" ]; then
      SYS="$SYS,loto_hold$h"
    else
      missing="$missing $h"
    fi
  done
  n_folds=$(( $(echo "$SYS" | tr ',' '\n' | grep -c '^loto_hold') ))
  if [ "$n_folds" -gt 0 ]; then
    [ -n "$missing" ] && say "stage 'loto_eval': WARNING - no 'best' checkpoint for fold(s):$missing"
    say "stage 'loto_eval': ${n_folds}/6 folds x 6 conditions"
    cat > runs/manifest/queued/086_lotoeval__qwen25c-1.5b.json <<JSON
{"job_id": "lotoeval__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/loto_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python", "--systems", "$SYS"],
 "raw": false, "est_gpu_h": 1.5, "priority": 86,
 "meta": {"experiment": "ood/loto", "stage": "loto_eval", "n_folds": $n_folds,
          "note": "no H1 by design - this arm exists so sweeps need not read it"}}
JSON
    if gate_or_skip loto_eval; then
      drain loto_eval
      mark_done loto_eval
    fi
  else
    mark_skipped loto_eval "no LOTO fold produced a 'best' checkpoint"
  fi
fi

# --------------------------------------------------------------------------- #
# STAGE — merge headroom: the configured-but-never-run density sweep, and the
# seed-42 expert bank replicate. Both are merge-time + one eval pass, no training.
# H1 is excluded from this config on purpose: a density sweep IS merge tuning, which
# §3.2 rule 2 forbids selecting on H1. Selection happens against LOTO.
if ! done_marker merge_headroom_build; then
  say "stage 'merge_headroom_build': density sweep + seed-42 merges (CPU)"
  ok=1
  for comb in ties dare_ties; do
    timeout 3600 python -m obtune.merge_adapters --config merge/ties_v1.yaml --model qwen25c-1.5b \
      --language python --combination-type "$comb" --sweep \
      --out "runs/merges/qwen25c-1.5b_python_${comb}" >> "$LOG" 2>&1 || ok=0
    timeout 1800 python -m obtune.merge_adapters --config merge/ties_s42.yaml --model qwen25c-1.5b \
      --language python --combination-type "$comb" \
      --out "runs/merges/qwen25c-1.5b_python_${comb}_s42/d0p5" >> "$LOG" 2>&1 || ok=0
  done
  if [ "$ok" -eq 1 ]; then mark_done merge_headroom_build
  else mark_skipped merge_headroom_build "one or more merges failed - see $LOG"; fi
fi

if ! done_marker merge_headroom_eval; then
  if [ -d runs/merges/qwen25c-1.5b_python_dare_ties/dare_ties_d0p7 ]; then
    say "stage 'merge_headroom_eval': density sweep + seed replicate"
    cat > runs/manifest/queued/088_mergehr__qwen25c-1.5b.json <<'JSON'
{"job_id": "mergehr__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/merge_headroom_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 1.2, "priority": 88,
 "meta": {"experiment": "rq2/merge-headroom", "stage": "merge_headroom_eval"}}
JSON
    if gate_or_skip merge_headroom_eval; then
      drain merge_headroom_eval
      mark_done merge_headroom_eval
    fi
  else
    mark_skipped merge_headroom_eval "the density-sweep merges were not built"
  fi
fi


# --------------------------------------------------------------------------- #
# STAGE — the gate-fix chain (MASTER_REPORT §12.8/§12.9).
#
# Ordered diagnostic-first ON PURPOSE. `gate_probe` decides whether the collapsed gate is a
# TRAINING failure (signal present, objective never asked for it -> the balanced retrain is
# the right fix) or a REPRESENTATION failure (condition not linearly available at the layer
# inputs the gate reads -> no loss function helps and the gate INPUT must change). Running
# the retrain first would spend 3 GPU-h to test a hypothesis the probe settles for a
# fraction of it.
#
# The retrain runs regardless of the probe's verdict, because load balancing and a
# temperature floor are standard MoE hygiene and are worth having in either branch. What the
# probe changes is the INTERPRETATION of the retrain's routing report, and whether fix 4
# (per-sequence routing) becomes the next arm.
if ! done_marker gate_probe; then
  say "stage 'gate_probe': can condition identity be decoded from what the gate reads?"
  cat > runs/manifest/queued/090_gateprobe__qwen25c-1.5b.json <<'JSON'
{"job_id": "gateprobe__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["scripts/analysis/23_gate_input_probe.py", "--model", "qwen25c-1.5b",
          "--language", "python", "--n-programs", "200"],
 "raw": false, "est_gpu_h": 0.5, "priority": 90,
 "meta": {"experiment": "rq2/gate-diagnostic", "stage": "gate_probe",
          "note": "linear probe on decoder-layer INPUT hidden states; no H1, program-disjoint split"}}
JSON
  if gate_or_skip gate_probe; then
    drain gate_probe
    mark_done gate_probe
  fi
fi

if ! done_marker gate_retrain_balanced; then
  say "stage 'gate_retrain_balanced': RouterLoRA with load balancing + temperature floor"
  cat > runs/manifest/queued/091_gatebal__qwen25c-1.5b.json <<'JSON'
{"job_id": "gatebal__qwen25c-1.5b", "kind": "train",
 "argv": ["-m", "obtune.mole.train_mole", "--config", "mole/routerlora_balanced.yaml",
          "--seed", "17"],
 "raw": false, "est_gpu_h": 3.0, "priority": 91,
 "meta": {"experiment": "rq2/gate-fix", "stage": "gate_retrain_balanced",
          "note": "aux_load_balance=0.01, min_temperature=0.5; v1 config untouched"}}
JSON
  if gate_or_skip gate_retrain_balanced; then
    drain gate_retrain_balanced
    mark_done gate_retrain_balanced
  fi
fi

if ! done_marker gate_eval_balanced; then
  gbal=runs/mole/qwen25c-1.5b/python/routerlora_balanced_s17/gate.pt
  if [ -f "$gbal" ]; then
    say "stage 'gate_eval_balanced': the balanced gate on the v1 ladder"
    cat > runs/manifest/queued/092_gatebaleval__qwen25c-1.5b.json <<'JSON'
{"job_id": "gatebaleval__qwen25c-1.5b", "kind": "eval-cell",
 "argv": ["-m", "obtune.mole.eval_mole", "--config", "eval/mole_balanced_qwen1.5b.yaml",
          "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 1.0, "priority": 92,
 "meta": {"experiment": "rq2/gate-fix", "stage": "gate_eval_balanced",
          "note": "the RESULT is gate_report.json, not the accuracy column - see 12.8"}}
JSON
    if gate_or_skip gate_eval_balanced; then
      drain gate_eval_balanced
      mark_done gate_eval_balanced
    fi
  else
    mark_skipped gate_eval_balanced "no balanced gate at $gbal (the retrain produced none)"
  fi
fi

# Routing analysis is CPU-only and reads whatever gate reports exist, so it runs even if the
# retrain was skipped — the v1 numbers alone are worth regenerating now that the capture
# accumulates over the whole cell instead of the final batch.
if ! done_marker gate_routing_analysis; then
  if timeout 900 python scripts/analysis/22_gate_routing_report.py >> "$LOG" 2>&1; then
    mark_done gate_routing_analysis
  else
    mark_skipped gate_routing_analysis "22_gate_routing_report.py failed - see $LOG"
  fi
fi


# --------------------------------------------------------------------------- #
# STAGE — fill the blanks in MASTER_REPORT §2.2.
#
# 500 of the table's 657 empty cells are runnable: every adapter, merge and gate already
# exists, so this is eval only — measured at ~12 min of generation, dominated by vLLM engine
# startup, hence 15 batched jobs rather than one per system.
#
# The other 157 blanks are NOT filled, and that is deliberate:
#   * 114 are composites on Grid A rows. No heldout composite variants exist; those cells are
#     UNDEFINED, not pending.
#   * 43 are `H1`. They would cost ~40 s of GPU and the whole quarantine budget
#     (CLAUDE.md §3.2 rule 3). Squaring off a table is not worth the discriminator.
#   * `oracle_prompt*` on S3/S4/composites is impossible: `prompts.py` is frozen and carries no
#     oracle description for those codes, so those systems are excluded by --systems rather
#     than being allowed to fail mid-job.
#
# `norm_*` composite cells were soundness-gated first (2,355 items x 4 profiles, 0 unsound):
# the arm scores a REWRITTEN program against the ORIGINAL's output, and the gate had only ever
# covered the single-transform ladder.
if ! done_marker fill22; then
  say "stage 'fill22': filling the runnable blanks in MASTER_REPORT 2.2"
  cat > runs/manifest/queued/100_fill22_grid_rq1.json <<'JSON'
{"job_id": "fill22_grid_rq1", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_grid_rq1.yaml", "--model", "qwen25c-1.5b", "--language", "python", "--systems", "base,merge_ties,merge_dare_ties,merge_dare_linear,tuned_L0_s17,tuned_L0_s42,tuned_L1b_s17,tuned_L1b_s42,tuned_L1r_s17,tuned_L1r_s42,tuned_L2_s17,tuned_L2_s42,tuned_S1_s17,tuned_S1_s42,tuned_S2_s17,tuned_S2_s42"],
 "raw": false, "est_gpu_h": 0.15, "priority": 100,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/101_fill22_grid_v1.json <<'JSON'
{"job_id": "fill22_grid_v1", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_grid_v1.yaml", "--model", "qwen25c-1.5b", "--language", "python", "--systems", "base,merge_ties,merge_dare_ties,merge_dare_linear"],
 "raw": false, "est_gpu_h": 0.15, "priority": 101,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/102_fill22_rank_sweep.json <<'JSON'
{"job_id": "fill22_rank_sweep", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_rank_sweep.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 102,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/103_fill22_mono_gate.json <<'JSON'
{"job_id": "fill22_mono_gate", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_mono_gate.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 103,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/104_fill22_merge_overtrain_full.json <<'JSON'
{"job_id": "fill22_merge_overtrain_full", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_merge_overtrain_full.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 104,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/105_fill22_merge_overtrain_sweep.json <<'JSON'
{"job_id": "fill22_merge_overtrain_sweep", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_merge_overtrain_sweep.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 105,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/106_fill22_overtrain_individual.json <<'JSON'
{"job_id": "fill22_overtrain_individual", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_overtrain_individual.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 106,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/107_fill22_merge_optimal_r1.json <<'JSON'
{"job_id": "fill22_merge_optimal_r1", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_merge_optimal_r1.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 107,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/108_fill22_merge_optimal_r2.json <<'JSON'
{"job_id": "fill22_merge_optimal_r2", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_merge_optimal_r2.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 108,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/109_fill22_merge_optimal_r3.json <<'JSON'
{"job_id": "fill22_merge_optimal_r3", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_merge_optimal_r3.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 109,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/110_fill22_dare_linear_rescaled.json <<'JSON'
{"job_id": "fill22_dare_linear_rescaled", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_dare_linear_rescaled.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 110,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/111_fill22_icl_k_sweep.json <<'JSON'
{"job_id": "fill22_icl_k_sweep", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_icl_k_sweep.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 111,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/112_fill22_normalize_baseline.json <<'JSON'
{"job_id": "fill22_normalize_baseline", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_normalize_baseline.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 112,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/113_fill22_icl_cross_h1.json <<'JSON'
{"job_id": "fill22_icl_cross_h1", "kind": "eval-cell",
 "argv": ["-m", "obtune.eval_vllm", "--config", "eval/fill22_icl_cross_h1.yaml", "--model", "qwen25c-1.5b", "--language", "python", "--systems", "base,icl_k1_cross,icl_k1_clean,icl_k1_matched_struct"],
 "raw": false, "est_gpu_h": 0.15, "priority": 113,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  cat > runs/manifest/queued/114_fill22_mole_ladder.json <<'JSON'
{"job_id": "fill22_mole_ladder", "kind": "eval-cell",
 "argv": ["-m", "obtune.mole.eval_mole", "--config", "eval/fill22_mole_ladder.yaml", "--model", "qwen25c-1.5b", "--language", "python"],
 "raw": false, "est_gpu_h": 0.15, "priority": 114,
 "meta": {"experiment": "report/fill-2.2", "stage": "fill22"}}
JSON
  if gate_or_skip fill22; then
    drain fill22
    mark_done fill22
  fi
fi

say "=== pipeline COMPLETE ==="
say "  done=$(ls runs/manifest/done/*.json 2>/dev/null|wc -l)" \
    "failed=$(ls runs/manifest/failed/*.json 2>/dev/null|wc -l)"

# What did NOT happen. Every stage marks itself done even when it skips, so without this a
# run where nothing was produced reads exactly like a successful one.
n_skip=$(ls "$STATE"/*.skipped 2>/dev/null | wc -l)
if [ "$n_skip" -gt 0 ]; then
  say "  $n_skip stage(s) SKIPPED and produced no result:"
  for f in "$STATE"/*.skipped; do
    [ -e "$f" ] || continue
    say "    - $(basename "$f" .skipped): $(cat "$f")"
  done
  say "  ^ these are the stages to look at first."
else
  say "  no stages were skipped."
fi
n_fail=$(ls runs/manifest/failed/*.json 2>/dev/null | wc -l)
if [ "$n_fail" -gt 0 ]; then
  say "  $n_fail job(s) in failed/ — inspect before trusting any table that depends on them:"
  for f in runs/manifest/failed/*.json; do
    [ -e "$f" ] || continue; say "    - $(basename "$f" .json)"
  done
fi
