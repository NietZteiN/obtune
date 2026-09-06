# 2026-09-06 — quota cleanup: optimizer states dropped, /work 99.7 % → 66.2 %

**Thread:** setup · **Status:** done

## Context
The objectives campaign hit the 1100 GB MooseFS hard cap mid-run on 2026-09-06
(`tr_curr_sft` 378791 failed at `save_model` with `Disk quota exceeded`; see
`../transfer/2026-09-06_consistency-objective-repairs-breadth.md`). The chain was recovered from
checkpoints after freeing only the smoke checkpoints (7.3 GB), leaving `/work` at 99.72 %.

## What was removed (user-authorised, dry-run listed first)
| target | count | size | why safe |
|---|---|---|---|
| `runs/**/optimizer.pt` | 685 files | ~346 GB | training-resume state only; every containing dir keeps `adapter_model.safetensors`; no SLURM job was running |
| `tmp/uv-cache/` | — | 25 GB | rebuildable package cache |

Nothing else: no adapter weights, no `results/`, no `data/`, nothing in `hf_home` (which also holds
the transcoders project's gemma-3-12b / NLA models).

## After
`mfsgetquota /work/jvl210002`: size **728.7 GB / 1100 GB hard (66.24 %)**, from 1096.9 GB (99.72 %).
Verified: 1,041 `adapter_model.safetensors` present; all 8 `runs/adapters_objectives/**/best` links
resolve; `scripts/verify_migration.py` → `MIGRATION VERIFY: OK`. Two `best` links under
`runs/adapters/qwen25c-1.5b/python/*_pilotsplit/` were already dangling (targets never existed
post-migration) and are unrelated.

## Consequence
**No training run under `runs/` is resumable.** Recovery for any adapter is re-training from its
committed config and seed (~18 min/adapter at 7B on one H200). Future runs still write
`optimizer.pt` per checkpoint (~500 MB each at r32/7B); a `save_only_model`-style option or a
post-run sweep would stop this from recurring — not done.
