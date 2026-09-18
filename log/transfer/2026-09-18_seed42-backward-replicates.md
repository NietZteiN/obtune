# 2026-09-18 — The backward claim replicates at seed 42 on both models, and the cost to pooled training is larger there

**Thread:** transfer · **Data:** `results/cells/seed42_inverse/` (161 cells per model) · sixteen
backward conditions clearing the format gate, paired by program, cluster bootstrap 2,000 resamples,
execution-graded.

## Arm minus untuned model, backward

| model | seed | **merge (DARE-TIES)** | breadth | KL-consistency |
|---|---|---|---|---|
| CodeLlama-7B | 17 | **+3.56** [+2.6, +4.6] \* | −2.57 [−4.1, −1.0] \* | +0.71 [−0.8, +2.3] |
| CodeLlama-7B | 42 | **+3.34** [+2.3, +4.5] \* | −4.14 [−5.7, −2.5] \* | +1.12 [−0.3, +2.7] |
| Llama-3.1-8B | 17 | **+3.53** [+2.4, +4.8] \* | −6.17 [−7.8, −4.4] \* | −5.24 [−7.0, −3.4] \* |
| Llama-3.1-8B | 42 | **+3.89** [+2.7, +5.1] \* | **−10.73** [−12.6, −8.8] \* | −9.24 [−11.0, −7.4] \* |

## What replicates

**The merge's backward gain is the most stable number in the study.** Four independent
(model, seed) cells give +3.56, +3.34, +3.53, +3.89 — a spread of 0.55 points — all significant,
none overlapping zero. Whatever weight-space composition is doing to preserve the untrained
direction, it does not depend on the initialisation or the data order.

**Single-adapter training costs backward accuracy at both seeds**, and on Llama-3.1-8B the cost is
*larger* at the second seed, not smaller: breadth −6.17 → −10.73 and the KL arm −5.24 → −9.24. The
effect the paper reports is, on that model, the conservative reading.

## What this does to the paper

The backward result was single-seed on six of eight models and is now two-seed on two. Combined with
the forward replication (`2026-09-18_seed42-replicates-the-forward-claim.md`) and Granite's backward
null (`2026-09-17_granite-exception-replicates-at-seed-42.md`), every load-bearing direction of the
argument has at least one independent-seed check on at least one model, and none of them moved
against the claim.

The honest remainder is unchanged: six models carry one seed, and the router comparison carries one
seed everywhere. Threats says so.
