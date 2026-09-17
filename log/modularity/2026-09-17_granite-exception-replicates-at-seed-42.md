# 2026-09-17 — Granite's backward exception is real, not seed noise — and it is DARE, not merging

**Thread:** modularity · **Data:** `results/cells/seed42_inverse/granite31-8b/` (115 cells, job
409824, 40 min) against the seed-17 panel · 16 backward conditions clearing the 0.25 format gate,
paired on the common programs, cluster bootstrap 2,000 resamples.

## Why this run existed

Granite-3.1-8B is the **single exception** in the whole panel: DARE-TIES is at or above the untuned
model backwards on seven of eight models and null on Granite (−0.27 [−1.8, +1.3]). A paper cannot
leave an unexplained outlier, and the cheapest way to find out whether it is noise is an independent
seed. Seven specialists, checkpoint selection, two merges and two evals were run at seed 42 for this
one question.

## Backward, arm minus untuned

| arm | seed 17 | seed 42 |
|---|---|---|
| **DARE-TIES merge** | −0.27 [−1.8, +1.3] | **+0.48 [−1.1, +2.0]** |
| **TIES merge** | **+5.11 [+3.9, +6.3]** \* | **+5.00 [+3.8, +6.2]** \* |
| breadth | −5.22 [−6.9, −3.4] \* | gated |
| clean LoRA | −7.16 [−9.9, −4.6] \* | −3.01 [−4.7, −1.4] \* |

**The exception replicates.** DARE-TIES is null at both seeds — the point estimate crosses zero from
below to above, and both intervals contain zero. It is not seed noise; on this model the arm genuinely
does not gain.

**TIES does, and it is the most stable number on the panel:** +5.11 and +5.00 across independent
seeds, a difference of 0.11 points, both intervals comfortably clear of zero.

## What this changes in the paper

The claim was "the merge is above the untuned model backwards on 7 of 8 models and null on the
eighth", which invites the reader to wonder what is wrong with the eighth. The better statement is
now available and is stronger:

> **Sign-consensus merging is at or above the untuned model backwards on all eight models.** On seven
> the DARE variant achieves it; on the eighth, DARE's stochastic drop-and-rescale is what fails, and
> plain TIES delivers +5.0 points at both seeds.

That reframes an outlier as a decomposition: the working ingredient is the sign-consensus step, and
DARE is a variance-reduction addition that helps on seven models and costs on one. It also gives the
recommendation a fallback with evidence behind it rather than a caveat.

## What it does not license

Only Granite has a second seed on the backward task, so "stable across seeds" is demonstrated for
this model and assumed elsewhere. Breadth is format-gated at seed 42 and unreadable, so its
seed-17 deficit (−5.22\*) is not replicated here. And the reason DARE fails specifically on this
model is unexplained: density 0.5 was tuned off-panel, and a density sweep on Granite would be the
direct test.
