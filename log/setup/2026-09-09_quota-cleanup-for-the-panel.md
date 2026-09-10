### Target Date: 2026-09-09 (quota cleanup: 125 GB freed so the five-model panel can land; two pre-existing broken symlinks found, not caused by it)
- **Hypotheses / what we're testing:** Housekeeping, no experiment. The question was whether the
  five-model panel could be downloaded at all. It could not: `/work/jvl210002` carries a **per-user
  quota of 1,000 GB soft / 1,100 GB hard** and stood at **1,058 GB — 105.8 % of soft, 42 GB from the
  hard stop** — against ~67 GB of downloads plus ~25 GB of adapters. Two facts made it urgent rather
  than merely tight: the soft-quota grace is one week and had already started, and the quota is
  **shared across every project on this account** — `transcoders/` grew 257 → 272 GB during the
  session as the `nla_ml_*` arrays ran, so headroom fell 41.9 → 25.4 GB in about an hour. At that
  burn the hard quota would have stopped *those* jobs, not just obtune's.
- **Setup:** the download chain (385666–385669) was put on `scontrol hold` before it could half-fill
  the remaining space and leave more `.incomplete` scratch. Deletion followed the CLAUDE.md rule:
  blast radius stated, dry-run first, explicit approval, then the narrowest command. Every guard was
  **re-derived at delete time** rather than read from the dry-run file, which was minutes old.
- **Results — 125 GB freed, 1,074.6 → 965.4 GB (96.5 % of soft, 134.6 GB of headroom):**

  | what | size | why it was safe |
  |---|---:|---|
  | 218 non-selected epoch checkpoints | **98.2 GB** | parent has `ckpt_select.json` recording every epoch's val accuracy, `best` is a resolvable symlink, and the dir is not that target |
  | orphaned `.incomplete` blobs (codellama-34b ×7, gemma-3-12b ×4) | **23.8 GB** | killed-download scratch beside complete shard sets |
  | `Qwen2.5-Coder-1.5B-Instruct` | **2.9 GB** | barred from the paper and the only Qwen/DeepSeek in the cache no other project references |

  Refused by the guards at delete time: **0**. Untouched: every `best/` target and `final/`,
  `adapters_overtrain`, `runs/merges`, `runs/taskvecs`, the six Qwen/DeepSeek models
  `transcoders`/`nla` do reference, `Qwen2.5-0.5B` (referenced by an nla test), and nla's own five
  `.incomplete` files — nla has jobs running and one could be a live download.
- **What worked / hypothesis verdict:** n/a. Three things the dry-run changed, each of which would
  have been a mistake to skip:
  1. **`best/` is a SYMLINK into a checkpoint directory.** A blanket "delete old checkpoints" would
     have destroyed the selected adapter of every arm in the project. The rule became "delete
     `checkpoint-*` that is not `realpath(best)`".
  2. **`runs/merges` and `runs/taskvecs` were withdrawn** from the plan after inspection: `merges`
     holds the cross-seed / residual / epoch-sweep banks those experiments were actually run on, and
     `taskvecs/unlearn` is likewise an experiment artifact. Both had been offered as "regenerable"
     on the strength of their names alone.
  3. **`configs/eval/overtrain_individual_qwen25c-1.5b_python.yaml` pins 12 raw checkpoints** as
     evaluated systems — in `adapters_overtrain`, the tree kept on 09-06 because "its weights are
     results". A config-pin scan is now part of the procedure, not a memory.
- **Observations:**
  - **Two dangling `best` symlinks exist and this cleanup did not cause them.**
    `qwen25c-1.5b/python/{L0,L1b}_r32_s17_pilotsplit/best` point at `checkpoint-200` / `checkpoint-198`
    inside the *non*-pilotsplit adapters, which contain checkpoint-74/148/222 and 73/146/219 — those
    step numbers never existed there. The links are dated **2026-08-28 15:50**, the migration day:
    they are path-rewrite casualties of the csr-94608 → juno move and have been broken for twelve
    days. Neither target appeared in the drop list (verified by grep), and 110 of 112 `best` symlinks
    resolve. The affected adapters are Qwen pilot arms, barred from the paper.
  - What the deletion costs: a non-selected epoch can no longer be re-evaluated. The *record* of the
    selection survives in each `ckpt_select.json` (every epoch's accuracy, the winner, the timestamp).
    This is the same trade taken on 2026-09-06 for 685 `optimizer.pt` files (~346 GB).
  - The 34B model was the single largest waste: 23.7 GB of orphaned blobs beside a complete 62.9 GB
    checkpoint, i.e. a killed download that had been paid for twice.
- **New questions / new hypotheses:** none. One standing risk to name: the quota is shared, so
  another project's run can exhaust it without warning. `scripts/preflight_panel.py` reports model
  and data readiness but not headroom; a quota line in it would make the constraint visible before a
  batch is submitted rather than after it fails.
- **Next Steps:** download chain released (385666 StarCoder2 → 385667 Granite → 385668 CodeGemma →
  385669 tier-1 datasets, all on `dev`); gates 385500/385501 still queued behind the shared 4-job
  limit. Re-run `scripts/preflight_panel.py` when the chain finishes; nothing trains until it exits 0
  and each model's gate passes.
