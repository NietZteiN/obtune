# 2026-09-13 — H-merge-backward REFUTED: the merge is the *best* arm backwards

**Thread:** modularity · **Status:** read against the pre-registered rule; the paper's "every method pays" sentence is now false as written · **Related:** [`2026-09-13_merging-on-the-panel.md`](2026-09-13_merging-on-the-panel.md), [`../transfer/2026-09-12_direction-ratio.md`](../transfer/2026-09-12_direction-ratio.md)

## Provenance

`ev_invmerge_codellama-7b` 393616 (h200, 9 min 46 s, 14 cells) through `configs/eval/inverse_merge.yaml`,
phase `inverse_generic`, one-shot, graded by executing the produced call. Read by
`scripts/analysis/62_merge_backward.py` against the controls already in that phase, on the **317
programs** common to every cell, clustered bootstrap 2,000 / seed 17. Three `tuned_L0` backward cells
(S1, S2, X1) exceed the 0.25 format gate and are excluded and named; every other cell passes.

## Numbers (points against the untuned model, pooled over L0–S2 and X1)

| arm | forward | backward | direction ratio |
|---|---|---|---|
| `merge_dare_ties` | **+18.87 [+16.38, +21.54]** | **+3.21 [+1.52, +4.85]** | **+0.17** |
| `merge_ties` | **+12.95 [+10.83, +15.26]** | −0.30 [−1.31, +0.71] | −0.02 |
| `mono_all` (breadth) | **+18.68 [+16.02, +21.53]** | −0.74 [−2.69, +1.20] | −0.04 |
| `cons_lam3` (anchored) | **+19.95 [+17.29, +22.81]** | +0.39 [−1.73, +2.60] | +0.02 |
| `tuned_X1` (family) | **+18.86 [+16.45, +21.49]** | +1.70 [−0.11, +3.49] | +0.09 |

## Verdict

**REFUTED.** The registered rule said REFUTED iff `merge_dare_ties − base` backwards has ci_lo > 0; it
is +1.52. I predicted CONFIRMED — "a weight-space average of adapters each fitted to the forward task
should inherit their backward cost" — and wrote in the registration that if merging turned out
backward-neutral the paper's "every method pays" sentence would be false and anchoring would lose its
uniqueness claim. Merging is not backward-neutral. It is **backward-positive, significantly, and by
more than any other arm in the panel**, with the highest direction ratio measured on this project.

That is three wrong predictions about merging today, all in the same direction: I expected it to behave
like breadth because it is built from the same specialists, and it does not, forward or backward.

## What it does to the paper

Two sentences are now false as written and one is weakened:

1. Abstract and RQ1: *"every method that fits the forward task buys its gain by losing backward
   competence on the very same programs."* `merge_dare_ties` fits the forward task as well as breadth
   (+18.87 against +18.68) and **gains** backwards.
2. RQ4: anchoring is *"the only arm in the supervised-fine-tuning family whose forward gain cost nothing
   backwards."* Merging is not in the SFT family, so the sentence survives on a technicality; the
   claim a reader takes from it does not.
3. The direction-ratio table's story — negative for everything that fits forward, ~0 for anchoring —
   needs a row for merging at +0.17.

**The prose is unchanged**, per the user's standing instruction to hold the story. The pending-decision
comment in `sections/rq1.tex` now names this as the third contradiction between the text and its own
tables. The table generator will pick up the merge row when `tables/direction_ratio.tex` is regenerated
from a widened source.

## Caveats worth keeping

- One model. `ev_invmerge` for Llama-3.1-8B, StarCoder2 and Granite is queued; the one-shot inverse
  template is CodeLlama-7B-specific, so their cells may be format-gated, and the analysis refuses to
  read an arm whose backward cells are gated rather than reporting a number from them.
- `tuned_L0`'s three gated cells mean the clean-code control is absent from this pooled read; the
  earlier direction-ratio analysis (412 programs, per-condition gate) has it at −0.08.
- `merge_ties` — the same merge recipe without DARE — is flat backwards (−0.30) and much weaker
  forwards. Whatever is happening is specific to DARE-TIES, not to merging as such.
