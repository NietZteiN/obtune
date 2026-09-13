# 2026-09-13 — The scratch quota is exhausted; the model cache is back on /work

**Thread:** setup · **Status:** obtune unblocked; the account-level problem needs the user · **Reverses (for one reason):** the 2026-09-10 move recorded in [`../../scripts/env.sh`](../../scripts/env.sh)

## What is wrong

**Every write under `/scratch/juno/jvl210002` fails with `ENOSPC`, including a 40-byte file**, while
`df` reports 27 T free of 30 T and 1 % of inodes used. It is a quota the filesystem does not expose
through `statfs`, and it is persistent: three writes three seconds apart all failed, an hour after a
50 MB write had succeeded.

## What it cost before it was understood

- `ev_invmerge_llama31-8b` and `ckb_codellama-13b` died writing
  `hub/models--*/refs/main.<hash>.tmp` — the hub client refreshing a **revision pointer** for weights
  that were already local. Neither job needed the network.
- Two models were left with **empty `refs/main`**: CodeLlama-13B and Gemma-3-12B. An empty ref cannot
  resolve to a snapshot, so those models fail on every subsequent job **and** defeat `HF_HUB_OFFLINE=1`,
  which would otherwise have been the clean fix. I set that flag, found it broke exactly those two
  models, and reverted it within the hour.
- No cached `config.json` is corrupted; every one of them parses. The damage is confined to refs.

## What was done

`OBTUNE_HF_STORE` now points at `/work/jvl210002/migration/hf_home`, which is writable, has 99 T free,
and already held six of the eight panel models with intact refs. CodeLlama-13B (25 G) and CodeLlama-34B
(63 G) were **copied** from the scratch cache — copied, not moved; the scratch tree is untouched — and
13B's empty ref was repaired from its single snapshot hash. All nine checkpoints (eight panel models
plus the pretrained baseline) now resolve and load, and the cache accepts writes.

The 2026-09-10 move to /scratch had two reasons. **Space** is now the opposite way round: /work has
99 T free and /scratch will not accept a byte. **Ownership** still stands — a sibling project deleted
CodeLlama-13B and 34B from the /work cache once before, which is precisely why both had to be re-copied
today. The **speed** advantage of /scratch (14 GB/s against /work's 1.3 GB/s) is real and is what this
gives up. Reversing is one line in `env.sh` once the quota is cleared.

## What needs a human

The account's scratch usage is ~2.6 T and most of it is not obtune's: `probing/` 1.6 T,
`nla_ml_gemma4b` 396 G, `nla_ml_gemma12b` 198 G, `nla_ml_dose` 105 G, against obtune's 285 G of model
cache. Deleting a sibling project's data is not a call this project makes. The options are to free some
of that 2.3 T, to ask the administrators whether the directory quota can be raised (the mismatch
between the quota and what `df` reports is itself worth reporting), or to leave obtune on /work.

## For the next person

`df` lying about a WekaFS directory quota is the trap here. When a write fails with ENOSPC and `df`
looks healthy, **test with a tiny file** — `echo t > dir/.wtest` — before believing the free-space
figure. And check `refs/main` for zero length in any HF cache that has seen a full disk: an empty ref
is a silent, model-specific failure that survives the disk being freed.
