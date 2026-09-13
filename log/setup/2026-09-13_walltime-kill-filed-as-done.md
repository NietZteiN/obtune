# 2026-09-13 — A walltime kill was filed under done/ with exit code 0

**Thread:** setup · **Status:** fixed in `scripts/slurm/submit.py`; one manifest requeued · **Related:** [`2026-08-28_juno-migration.md`](2026-08-28_juno-migration.md) (the lifecycle design)

## What happened

`tr_S2_llama31-8b` (392121) ran on the MIG node `g-06-01` at ~17 s/step — S2 prompts are the long
ones (526 tokens mean against L0's 303) — and hit its **1 h walltime at step 178/222**. SLURM's
`sacct` says `TIMEOUT`. The manifest lifecycle filed it under **`runs/manifest/done/` with
`exit_code: 0`**, with no `final/`, no `training_summary.json` and only two epoch checkpoints on
disk. Nothing downstream read the manifest as a result — `build_ready_merges.py` checks adapter
files, not manifests, which is how it surfaced: the feeder reported Llama-3.1-8B at "4/5 specialists
trained" while all five training manifests sat in `done/`.

The migration entry promised the opposite: "a job killed at walltime still lands in `failed/`". The
`trap finish EXIT` does run on a walltime kill. The defect is what `$?` holds when it does. SLURM
SIGTERMs the batch script while bash is waiting on the python child; bash finishes the wait, then
acts on the signal and runs the EXIT trap **without executing the next line**, so `$?` inside the
trap is the status of the last command that *completed* — the `echo` before the command — which
is 0.

## Scope

`sacct` over the last five days lists three TIMEOUTs and ~60 FAILEDs on this account. Exactly one
had a manifest in `done/`: this job. Every other failure was ad-hoc (no manifest) or landed in
`failed/` correctly, because those processes *returned* a non-zero status rather than being killed
mid-wait.

## Fix

The script now records `CMD_STATUS=$?` on the line after the command and the trap treats an
**empty** `CMD_STATUS` as "killed before the command returned": `rc=124`, filed under `failed/`
with `"reason": "killed before the command returned (walltime or node failure)"`. A command that
returns keeps its real status. Verified by dry-run and `bash -n`.

## Requeue

`tr_S2_llama31-8b` moved back to `queued/` with `est_gpu_h` 0.5 → 1.5 (the 2× rule gives 3 h; the
0.5 estimate was CodeLlama-7B's 18 min on a full H200, and this ran on a 47 GB MIG slice). The
original `slurm` block is preserved under `meta.previous_slurm`. `training_summary.json` absent →
`build_ready_merges.py` will run checkpoint-select on S2 alone once it lands, then queue the merges.

The other S2 job on the same node, `tr_S2_starcoder2-15b` (392122, 2 h limit), was at 130/222 at
55 min when checked — ~26 s/step, projected 1 h 36 min — and should finish inside its limit.
