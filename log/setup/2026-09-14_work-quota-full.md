# 2026-09-14 — The /work quota filled mid-run; trainings held, model cache moving to scratch

**Thread:** setup · **Status:** hf_home sync to scratch running; pending trainings held; checkpoint archive proposed to the user

## What happened

`tr_L1b_llama31-8b_s42` died at its final save with `Disk quota exceeded (os error 122)` after 219
of 219 steps — the run had finished and could not write `final/`. Its last checkpoint directory
holds only a README, so nothing is salvageable and it goes back in the queue once there is room.

The account sits at **1,001 GB**: this project 560 GB (adapters 367, objectives 39, cells 9.6), the
model cache 321 GB, environments 53 GB, the sibling project 48 GB, temp 25 GB. A 100 MB write still
succeeds; a checkpoint-sized one did not. Every pending training was **held** (`scontrol hold`,
which fires no trap and is reversed by `release`) so none starts into a full disk; running grids
were left alone — their cells are small and resume covers a failure.

## The move

`/scratch/juno/$USER` accepted a 100 MB write today (it refused a 40-byte one yesterday), has 27 TB
free, and already held a 285 GB copy of the cache. The delta is syncing; when it verifies,
`OBTUNE_HF_STORE` flips back to scratch, the one-line switch `scripts/env.sh` documents. The
`/work` copy stays until the six running jobs that memory-mapped their weights from it finish, and
its deletion needs the user's explicit go-ahead.

## The faster lever, awaiting the user

Under the 152 adapters that already have a selected `best/`, the intermediate `checkpoint-*` and
`final/` directories are **467 directories, 357 GB** (323 under `runs/adapters`, 34 under
`runs/adapters_objectives`). Every evaluation reads `best/` only; the rest is the raw training
record. Copy-verify-remove to `/scratch/juno/$USER/obtune_ckpt_archive/` would free that space in
about an hour without waiting for any job and without deleting anything. Proposed, not done.
