# 2026-09-13 — Master tables in the paper: raw accuracy, delta, and per-cent-of-clean for every condition and stack

**Thread:** writeup · **Status:** done, PDF rebuilt · **Related:** [`../transfer/2026-09-13_backward-task-format-collapse-on-the-panel.md`](../transfer/2026-09-13_backward-task-format-collapse-on-the-panel.md), [`2026-09-10_paper-draft.md`](2026-09-10_paper-draft.md)

## What was asked

A master table for every model and every obfuscation type — clean forward and backward, obfuscated forward and backward, and each intervention's improvement — plus tables for the models, the dataset and the obfuscation taxonomy; then, after the text draft, "more detail, like list the stacks", and "raw numbers on obfuscated and the percentage of original base each brings back".

## What was built

`scripts/analysis/59_master_tables.py` now emits both `docs/MASTER_TABLES.md` and thirteen LaTeX tables under `paper/router_merger/tables/` from the same cells. Nothing is typed by hand; every number is read from `results/cells/*/cell_meta.json`, `configs/models.yaml`, `configs/conditions*.yaml`, and the data files.

Three numbers per (system, condition, direction):

| number | definition |
|---|---|
| **acc** | raw accuracy of that system on that condition |
| **Δ** | points against the untuned model on the same condition |
| **%** | acc as a percentage of the untuned model's *clean-code* accuracy in the same direction — "how much of the original accuracy the system brings back". The untuned model on clean code is 100 by definition; on obfuscated code it shows what the obfuscation removed; above 100 is more than restored. |

Rows per model: the seven ladder conditions (L0, L1b, L1r, L2, S1, S2, X1), then **every stack listed individually** — six seen depth-2, four seen depth-3/4, three unseen-containing depth-2, two half-unseen, one unseen-containing depth-3 — with pooled rows after each group. Backward rows for the ladder only (that task was never run on stacks).

Placement in `paper/router_merger/`:
- **Setup** gained three subsections with `setup_models`, `setup_dataset`, `setup_taxonomy` (12 single transforms with size caps and held-out coverage) and `setup_stacks` (all 16 stacks: parts in order, depth, whether X1 is inside, cap, coverage, group, purpose).
- A new short section **"Every intervention against every obfuscation"** (`sections/master.tex`) with the cross-model summary `master_summary` (mean Δ and mean %, per bucket: clean / seen / unseen family / seen stacks / unseen stacks, with the number of cells and the number gated).
- **Appendix A** with the eight per-model grids, one `table*` each.

## Gate semantics, stated

The format gate (0.25) is applied **per cell**, stricter than the pooled registration. Consequences that are visible in the tables and must not be read as results:
- A **Δ** is gated when the untuned cell on the same condition is gated (no delta against a base that produced nothing parseable). A **%** is gated when the clean-code reference is. These are counted separately in the summary because they differ: the untuned CodeLlama-34B sits at **0.254** on clean code, a hair over the bar, which gates its whole % column while its deltas stand. StarCoder2-15B's untuned model is at 1.000 on every forward cell, so all its forward Δ and % are gated; Gemma-3-12B is at 0.27–0.29 across the ladder and depth-2 stacks.
- The backward and in-context templates are CodeLlama-7B-specific; on the other panel models most backward cells are gated (the 09-13 transfer entry). On 7B itself the per-cell gate marks `tuned_L0` backward on S1/S2/X1 (0.32/0.42/0.28) and `base_1shot` on S2 (0.28), which the pooled rate (0.19) would pass.

## What the grid shows (CodeLlama-7B, the fully interpretable block)

- Obfuscation cost on the untuned model: 66–81 % of clean accuracy retained on the single seen transforms, 46 % on X1, 51–72 % on depth-2 seen stacks, 35–58 % on depth-3/4.
- Every intervention more than restores clean accuracy on seen transforms (135–162 %) and seen stacks (108–164 %); those columns do not separate the interventions.
- Unseen family: breadth 90 %, clean LoRA 105 %, anchored 111 %, family 123 %. Unseen-containing stacks pooled: 93 / 100 / 107 / 120 %. Panel means, same order: 91 / 102 / 99 / 128 % on X1 and 93 / 95 / 98 / 116 % on the stacks — so panel-wide, anchoring closes *most* of breadth's gap to the control rather than exceeding the control; the prose says exactly that.
- Backward: the family adapter never loses (+0.0 to +4.2); anchored stays within 2.3 points of the untuned model everywhere; breadth loses up to 3.9 (L1r).

## Build

`runs/probe/build_paper.sh router_merger`. Two mechanical faults on the way: a size switch placed after `\begin{tabular}` produced `Misplaced \noalign` at the first `\toprule` (the switch belongs on the `\centering` line), and the first layout had five tables 60–314 pt over the text width — fixed with a two-row header on the grids (the one-row "clean LoRA (`tuned_L0`)" spans forced the columns wide), one row per (system, direction, measure) in the summary, and narrower paragraph columns in the taxonomy tables. The overfull boxes that remain in `rq2_identifier`, `rq3_panel` and `rq4_ladder` predate this entry. The `ase26` citation is still undefined (user's, intro-2.tex line 43).

## Not claimed

No new number is a finding. The direction-ratio claim stays CodeLlama-7B only. Nothing in these tables was used to select or tune anything. H1 does not appear.
