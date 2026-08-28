# 2026-08-27 — setup — cluster handoff package (`continuation/`)

## Goal

The project is moving to a different cluster and will be continued by a fresh Claude Code session
with no conversational context. Produce a self-contained handoff so that session can pick up
without re-deriving the research state, and without breaking the `H1` quarantine or the grid rules
through ignorance of them.

## Setup

No GPU, no compute. Read-only inspection of the repo, `git status`, `du`, and a `grep` sweep for
cluster-specific absolute paths. New folder `continuation/`, five numbered markdown files, 743
lines total. Every relative link and every referenced code path validated programmatically.

## Results

`continuation/README.md` (entry point) · `00_STATE.md` (research state) · `01_NEXT_STEPS.md` (the
agreed plan) · `02_ENVIRONMENT.md` (what breaks on migration) · `03_OPEN_CORRECTIONS.md` (owed
fixes). Validation: 0 broken relative links; all 18 referenced code paths exist; the three precise
references (`schema.py:146`, `NUMBERS.md:78`, `routing_report.json` `n_heldout: 0`) confirmed
against the files.

## Observations

**The transfer risk is much larger than the migration risk, and it is not the obvious one.**
`git remote -v` is **empty** and `git status` shows **160 changes, 128 of them untracked** — the
untracked set includes both master reports written today, the RQ3 report, the entire
`log/normalization/` thread, and seven configs. There is nowhere to `git pull` from. If the working
tree is not physically transferred, today's work does not exist anywhere else. The handoff leads
with this and gives a `git bundle` recipe rather than assuming a remote.

**Sizes make the priority counterintuitive.** `runs/adapters/` is 56 GB and `runs/merges/` 12 GB,
but `results/cells/` — 2,215 cells and 1,046,382 graded trials, from which *every number in every
report* is recomputed — is only **81 MB**. The minimum viable transfer is repo + `results/` +
`data/` at under 2 GB, which preserves every published number and costs the ability to run new
evals without retraining. Recorded as a table so the decision is explicit rather than accidental.

**Nine files carry 18 hardcoded `/data/jvl210002` paths, and they are not all the same kind.** Four
in `configs/data.yaml` plus two more point *outside* the repo entirely — at `model_understanding/`,
`transcoders/`, and a shared `dataset/` directory. Those are cross-project dependencies, so a
blanket `sed` would produce paths that resolve to nothing. They are listed separately with the
instruction to copy the five source files across, because the failure mode otherwise looks like a
missing-source error rather than a migration problem.

**`CLAUDE.md` §1 will be actively wrong on the new cluster and that is worse than absent.** The
whole no-SLURM apparatus — `src/obtune/sched/`, `allowed_gpus`/`gpu_budget`, the `ppid == 1` check
that exists because a borrower shares this Unix account — is an artifact of this specific host. The
handoff says to decide explicitly whether to port or bypass `sched/`, and to update the charter and
its changelog either way.

**The determinism finding earns its place in a migration doc for a reason that only applies here.**
An identical eval re-run differs by ~1 point on Grid B (12 of 115 generations), and up to 6.1 across
a commit boundary. Someone verifying a transfer will re-run a cell, see a mismatch, and reasonably
conclude the copy failed. `02_ENVIRONMENT.md` §7 pre-empts that, and §6 gives a specific number to
check instead — the RQ2 headline, `merge_dare_ties − tuned_L0` on Grid A `H1` = −0.66
[−1.89, +0.66], which is paired and should reproduce to ≤0.02 pts.

## Next steps

(1) **Commit and bundle before moving** — `git add -A && git commit && git bundle create --all`.
(2) Work `02_ENVIRONMENT.md` §1–§4 on arrival, then the §6 smoke test. (3) Then
`01_NEXT_STEPS.md` Phase 0 → Phase 1 → Phase 2 → 7B. (4) The `03_OPEN_CORRECTIONS.md` items are
all commits rather than runs and can be done at any point; B2 (Branch C) is blocked on the
per-algorithm robustness check.
