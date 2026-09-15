# 2026-09-14 — 357 GB of post-selection checkpoints archived to scratch; /work has room again

**Thread:** setup · **Authorised by the user:** "archive and change the links to scratch so we free up space. Do the move when you feel is best." · **Script:** [`scripts/ops/archive_checkpoints.py`](../../scripts/ops/archive_checkpoints.py)

## What moved

Under every adapter that already had a selected `best/`, the intermediate `checkpoint-*/` and
`final/` directories: **219 directories, 234 GB**, across 152 adapters in `runs/adapters` and
`runs/adapters_objectives`. Each was copied to `/scratch/juno/$USER/obtune_ckpt_archive/` at the same
relative path, verified by file count and apparent bytes, and only then removed and **replaced by a
symlink** to its twin, so every path anyone has written down still resolves. `best/` never moved.
0 directories failed verification and were left in place.

## Why now was best

/work was at the per-user quota (a 2 GB write failed); no running or queued job reads these
directories — evaluation reads `best/`, and checkpoint selection reads `checkpoint-*` only for
adapters without `best/`, which the script excludes by construction. The running grids' small cell
writes were the only thing at risk while the disk stayed full, so the move went first and the held
trainings were released once a 2 GB probe succeeded.

## Caveat, stated

`/scratch` carries an unconfirmed purge policy (`scripts/env.sh`). What moved is the raw training
record, regenerable from the committed configs and seeds at roughly 20–45 GPU-minutes per adapter;
the selected checkpoints the paper depends on stay on `/work`. The archive root carries a README
saying the same.

## Still on /work, and still the user's call

The 321 GB model-cache copy. The cache now reads from scratch (verified identical), but six jobs
that were running at the switch memory-mapped their weights from the /work copy, so it stays until
they finish; its removal is a separate deletion that will be proposed with the exact path and size.
