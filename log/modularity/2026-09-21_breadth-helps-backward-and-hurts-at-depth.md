# 2026-09-21 — Ingredient breadth helps backward, does nothing at `L0`, and *hurts* at depth 3

**Thread:** modularity · **Data:** `results/cells/mergeablate_{generic,inverse}/`, four models.
Paired program-clustered bootstrap, 2,000 resamples, seed 17. Script
`scripts/analysis/76_merge_ablation.py`.

Extends [`2026-09-20_ablation-panel-complete-breadth-not-l0.md`](2026-09-20_ablation-panel-complete-breadth-not-l0.md),
which reported depth-2 and shallower only. The depth-3 and depth-4 groups were in the forward
phase all along and were simply not read.

## Three regimes, three different answers

`struct` is two structural specialists (S1+S2); `6-way` is the paper's merge.

| regime | effect of ingredient breadth |
|---|---|
| clean code and single transforms | **none** — all four ingredient sets within noise |
| depth-3 stacks, forward | **negative** — the two-specialist merge *beats* six |
| backward | **positive and large** — narrow merges lose 4–9 points |

`struct − 6-way` on depth-3 seen stacks, forward:

| model | depth 3 | depth 4 |
|---|---|---|
| CodeLlama-7B | +2.63 [+1.6, +3.7] \* | +2.39 [+0.5, +4.4] \* |
| CodeLlama-13B | +1.05 [+0.0, +2.1] \* | +2.15 [+0.2, +4.2] \* |
| Llama-3.1-8B | +2.10 [+0.9, +3.2] \* | +1.44 [−0.6, +3.5] |
| Granite-3.1-8B | +2.73 [+1.4, +4.1] \* | +3.03 [+0.8, +5.3] \* |

Significant on 4 of 4 at depth 3 and 3 of 4 at depth 4.

## Why this is not a restatement of the backward result

It points the other way. Backward, cutting to two specialists costs 4–9 points on every model
where the narrow arm is readable. Forward at depth 3, cutting to two specialists *gains* 1–3
points on every model. The same ablation, opposite signs, and `L0` shows nothing at all.

A reading consistent with both, and not established here: the depth-3 stacks are built from
`S1`/`S3`/`S4` plus one identifier transform, so they are structure-dominated, and a merge of
exactly the structural specialists is not diluted by three identifier specialists that the
stack barely exercises. The backward task has no such dominant family and needs the coverage.
That is a hypothesis about *which* transforms a stack contains, and testing it means an
identifier-dominated depth-3 group, which the corpus does not currently have.

## What the paper may and may not say

* **May:** the clean-code gain is independent of the ingredient set (4/4 models, already in RQ1).
* **May:** backward robustness needs breadth (3/4 models significant, already in RQ3).
* **May now:** the six-way merge is *not* the best ingredient set at depth, and a structural-only
  merge beats it on 4/4 models at depth 3.
* **May not:** anything about *why*. The dominance explanation above is untested.

The honest framing is that ingredient breadth is a trade-off rather than a good, and the paper
currently presents the six-way merge as simply the right choice.

## Open

Four models — the ablation adapters exist only for these. Nothing here reads H1.
