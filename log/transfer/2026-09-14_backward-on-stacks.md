# 2026-09-14 — The backward task on stacked obfuscation: breadth degrades with depth, the clean adapter collapses

**Thread:** transfer · **Status:** CodeLlama-7B complete (112 cells); the other seven running

The backward task had never been run on a stack. It now is, for all sixteen: six depth-2 seen, four
depth-3/4 seen, four unseen-containing, two half-unseen. Pooled, CodeLlama-7B:

| group | metric | base | clean LoRA | breadth | anchored | family | merge |
|---|---|---|---|---|---|---|---|
| seen stacks (6) | exec | 0.286 | 0.216 | 0.265 | 0.295 | 0.300 | **0.327** |
| seen stacks (6) | exact | 0.085 | 0.063 | 0.078 | 0.090 | 0.100 | **0.106** |
| depth 3–4 (4) | exec | 0.295 | 0.177 | 0.239 | 0.295 | 0.285 | **0.318** |
| depth 3–4 (4) | exact | 0.083 | 0.046 | 0.068 | 0.089 | 0.089 | **0.105** |
| unseen-containing (4) | exec | 0.274 | 0.160 | 0.195 | 0.268 | 0.261 | **0.292** |
| unseen-containing (4) | exact | 0.070 | 0.040 | 0.042 | 0.075 | **0.082** | 0.081 |

## What is new here

**Breadth degrades monotonically with divergence, backwards as well as forwards.** On exact arguments
it goes 0.078 (seen) → 0.068 (depth 3–4) → 0.042 (unseen inside), against a base that is flat at
0.085 / 0.083 / 0.070. That is the forward dissociation appearing in the reverse direction on
stimulus neither direction was trained on — and it is the first evidence that the paper's central
finding is not an artefact of the forward task's format.

**The clean-code adapter is the worst arm backwards everywhere**, and falls further the deeper the
stack: 0.216 → 0.177 → 0.160 by execution, well below the untuned model. Nine of its sixteen stack
cells are format-gated.

**Anchoring holds the untuned level on every group** (0.295 / 0.295 / 0.268 against base's 0.286 /
0.295 / 0.274) and is the only tuned SFT arm that does. The merge is above base on every group and
every metric; family leads on exact arguments where the unseen family is present.

So the reversal claim, which was one model and seven ladder conditions this morning, is now one model
and twenty-three conditions, with the ordering unchanged and the dissociation visible in both
directions.

The other seven models' stack evaluations are running; their comparison arms are expected to be
gated by the forward-collapse effect recorded separately today.
