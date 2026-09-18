# 2026-09-18 — The unseen-family result replicates at a second seed on both models that have one

**Thread:** transfer · **Data:** `results/cells/seed42_generic/` · forward, the seven
unseen-family conditions, paired by program, cluster bootstrap 2,000 resamples.

## Why

CLAUDE.md §4 requires varying seeds before claiming an effect. The paper's central forward claim —
pooled training is below every arm composed from the same data on the held-out family — was
single-seed on six of eight models. Two models now carry a complete seed-42 panel.

## Breadth minus the merge, forward, unseen family

| model | seed 17 | seed 42 |
|---|---|---|
| CodeLlama-7B | −2.21 [−3.5, −0.9] \* | **−1.87 [−3.2, −0.6]** \* |
| Llama-3.1-8B | −2.96 [−4.2, −1.7] \* | **−2.78 [−4.0, −1.5]** \* |

Significant at both seeds on both models, with point estimates within 0.34 and 0.18 points of each
other. The effect is not a seed artefact.

## Scope, stated

This replicates the **breadth-versus-merge** comparison, which is the exactly data-matched one. The
router is absent from the seed-42 configs — no gate was trained at seed 42 for Llama, and CodeLlama's
s42 eval config does not list `mole_router` — so the breadth-versus-router gap, which is the larger
of the two at seed 17, is still single-seed. Granite's seed-42 panel omits the KL and family arms by
construction and was run for the backward question
(`2026-09-17_granite-exception-replicates-at-seed-42.md`), not this one.

So: the claim the paper leads with is now two-seed on two models and single-seed on six. That is
better than it was and short of what a reader might assume from "eight models"; the threats section
should say which claims carry a second seed rather than leaving it to be inferred.
