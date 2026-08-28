# START HERE — cluster handoff for `obtune`

**Written 2026-08-27 on `csr-94608.utdallas.edu`, for a fresh Claude Code session on a different
cluster.** Read this file first, in full, before touching anything.

You are picking up a mid-flight ML research project. Everything you need is in this folder plus the
canonical docs it points at. Files are numbered in the order you should read them.

| file | what it is |
|---|---|
| `README.md` (this) | orientation + the transfer checklist that must happen before anything else |
| `00_STATE.md` | where the research actually stands — the verdicts, the numbers, what is closed |
| `01_NEXT_STEPS.md` | the agreed plan for what happens next, in execution order |
| `02_ENVIRONMENT.md` | what will break on a new cluster and exactly how to fix it |
| `03_OPEN_CORRECTIONS.md` | small owed fixes that are already diagnosed, not yet applied |

---

## ⚠️ READ THIS BEFORE MOVING ANYTHING

**The repository has no git remote and 128 untracked files, including both master reports written
today.** Verified 2026-08-27:

```
git remote -v      -> (empty)
git status         -> 160 changes, 128 of them untracked
git rev-parse HEAD -> f1a3247
```

**If the working tree is not transferred, today's work is gone.** There is nowhere to `git pull`
from. Do this on the OLD cluster before or during the move:

```bash
cd /data/jvl210002/my_downloads/obtune
git add -A && git commit -m "checkpoint before cluster migration"
git bundle create ../obtune-$(date +%F).bundle --all      # single portable file
```

Then on the new cluster: `git clone obtune-YYYY-MM-DD.bundle obtune`.

If the tree is copied directly with `rsync` instead, that is fine too — but copy `.git/` with it,
and still commit first so the history has a restore point.

### What must move, and what must not

| path | size | move it? |
|---|---|---|
| the repo itself (code, configs, `docs/`, `log/`, `paper_*/`) | small | **yes — this is the irreplaceable part** |
| `results/cells/` | **81 MB** | **yes.** 2,215 evaluation cells / 1,046,382 graded trials. Every number in every report is recomputed from these. Tiny and irreplaceable |
| `results/` (rest — analysis, merge_geometry, attn, forgetting) | 1.3 GB total | **yes** |
| `data/` | 290 MB | **yes** — includes `data/quarantine/` (the held-out obfuscator) |
| `runs/adapters/` | 56 GB | **yes if you can.** ~68 trained LoRA adapters. Regenerating is ~2–3 GPU-h *each* |
| `runs/merges/` | 12 GB | optional — rebuildable on CPU from `runs/adapters/` via `src/obtune/merge_adapters.py` |
| `runs/mole/` | 22 MB | yes, small |
| `runs/logs/`, `runs/manifest/` | — | no, cluster-specific scheduler state |
| HF model cache | large | no — re-download on the new cluster |

**Minimum viable transfer** if bandwidth is tight: repo + `results/` + `data/` = under 2 GB. That
preserves every published number and every document. You lose the ability to run new evals without
retraining adapters.

---

## What this project is, in one paragraph

`obtune` asks whether fine-tuning a code LLM on **obfuscated** code teaches *semantic invariance*
(robustness to the whole class of meaning-preserving rewrites) or merely *transform memorization*
(undoing the specific obfuscators it saw). The task is **output prediction on still-obfuscated
code** — never recovery/deobfuscation, which is the clean separation from the DOBF literature.
The discriminator is `H1`, a held-out obfuscator quarantined behind four enforcement layers that
nothing may ever train, tune, or select on. The answer so far is **memorization, with one specific
replicated exception** whose mechanism has now been established causally.

Governed by [`../CLAUDE.md`](../CLAUDE.md) — read it second, after this file. It is the project
charter: hardware rules, storage layout, the condition ladder, the `H1` quarantine discipline
(§3.2, a hard rule), the silent-failure checklist (§4), and the log protocol (§6).

## Where to read next, in order

1. **[`00_STATE.md`](00_STATE.md)** — the research state. Start here, not in `docs/`.
2. **[`../docs/MASTER_REPORT_2026-08-27.md`](../docs/MASTER_REPORT_2026-08-27.md)** — the living
   master report, ~3,800 lines. §2.2 is the one table containing every system. **This is the
   canonical document; everything else in `docs/` is either a slice of it or superseded.**
3. **[`01_NEXT_STEPS.md`](01_NEXT_STEPS.md)** — what to actually do.
4. `../CLAUDE.md` §3.2 before you go near `H1`.

Deep dives, only when you need them:
- [`../docs/MASTER_REPORT_2026-08-27_router-and-merging.md`](../docs/MASTER_REPORT_2026-08-27_router-and-merging.md)
  — RQ2 closed, self-contained for someone who has never seen the project
- [`../docs/REPORT_2026-08-26_rq3-attention-mechanism.md`](../docs/REPORT_2026-08-26_rq3-attention-mechanism.md)
  — the causal attention result, self-contained
- [`../log/README.md`](../log/README.md) — the research ledger, one folder per thread, append-only

**Superseded — do not cite:** `docs/MASTER_REPORT_2026-08-{10,11,12}.md` (08-12 carries a
supersession banner), `docs/RESULTS_BOOK_2026-08-11.md` (stale since 11 August), and the two chain
reports `REPORT_2026-08-{15,17}_*.md` (both carry banners; 08-17 retired 08-15's headline claim).

## Working conventions that are not optional

These are inherited from `CLAUDE.md` and from mistakes this project already made. A fresh session
that ignores them will produce numbers that look fine and are wrong.

- **Never pool the two evaluation grids.** Grid A (`heldout`, corpus) and Grid B (`testset`, ICSE)
  are disjoint in programs. `base` scores 6.4 % on `H1` in one and 11.3 % in the other. Grid is
  identified by item count, never by directory name: `H1` at n=1,214 is Grid A, at n=115 is Grid B.
- **`tuned_L0` is the control, not `base`.** The base model is weak at the *task*, so against it
  every adapter looks excellent. Only the gap to a clean-code-trained adapter isolates what
  *obfuscation* training buys.
- **The noise bar is the Python row: 0.63 mean / 1.46 p95.** The widely-quoted 1.32 / 3.61 is the
  Python+JavaScript *pooled* figure and has been misapplied to Python-only contrasts throughout
  (master report §8.10). Everything in RQ2 and RQ3 is Python.
- **Every number is read from a result file, never from a report.** Reports are an index of where
  to look. This convention has caught four report-vs-file discrepancies.
- **Statistics:** cluster bootstrap by `program_id` (multiple input cases per program are
  correlated), BH-FDR across a contrast family, exact McNemar on discordant pairs.
- **Log as you go.** One dated entry per thread per working day under `log/<thread>/`, append-only;
  corrections go in a *new* dated entry. Update `log/README.md`'s timeline every time.
