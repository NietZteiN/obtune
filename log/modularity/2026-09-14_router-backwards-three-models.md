# 2026-09-14 — The router backwards on three models: 0.001, 0.023, 0.089. The rule's band catches none of them.

**Thread:** modularity · **Status:** 3 of 5 models read · **Rule:** `CLAUDE_SCRATCHPAD.md`, registered before any mixture backward cell existed

## Forward collapse, `mole_router`, 23 backward conditions

| model | `base` | `mono_all` | `cons_lam3` | merges | **`mole_router`** | verdict by the rule |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | 0.000 | 0.021 | 0.025 | 0.000 | **0.001** | REFUTED (at the merge floor) |
| CodeLlama-7B | 0.000 | 0.037 | 0.005 | 0.000/0.001 | **0.023** | INCONCLUSIVE (0.01–0.05) |
| Granite-3.1-8B | 0.056 | 0.077 | 0.313 | 0.000/0.001 | **0.089** | above 0.05, short of the 0.10–0.35 band |

**The rule I wrote has caught none of the three cleanly.** It asked for 0.10–0.35 to confirm and
below 0.01 to refute, and the three answers are 0.001, 0.023 and 0.089 — one refutation, one in the
inconclusive gap, one in a second gap the rule did not name. That is a badly calibrated rule, not
three ambiguous models: I set the confirm band from the single-adapter arms' rates on the *contaminated*
pooled numbers (breadth 0.198, anchored 0.312) and those arms actually sit at 0.021–0.077 once the
prompt fault is out. The band was drawn around numbers that no longer exist.

**What is true across all three**, and does not depend on the band: the router is at or below its
own model's breadth arm every time (0.001 vs 0.021; 0.023 vs 0.037; 0.089 vs 0.077 — the last is
above), and the merges are at the floor on all three.

## Backward accuracy, the nine stacks, paired on 557 programs

| contrast | CodeLlama-7B | Llama-3.1-8B | Granite-3.1-8B |
|---|---|---|---|
| router − untuned, exact args | −0.02 | **+0.96** \* | −1.09 |
| router − untuned, by execution | **−4.04** \* | −2.18 \*ᵃ | **−2.18** \* |
| router − uniform gate, exact args | +0.00 | +0.07 | **+0.54** \* |
| router − breadth, exact args | **+1.21** \* | **+1.86** \* | **+1.48** \* |
| merge − router, exact args | **+1.89** \* | **+1.16** \* | **+1.13** \* |

ᵃ Llama's execution-graded router−untuned is +2.05 above uniform but below base; the sign differs
from its exact-argument number, which is why both are reported.

**Two things replicate on all three models.** The router beats breadth backwards, significantly,
every time. And the merge beats the router backwards, significantly, every time — by 1.1 to 1.9
points on exact arguments. Nothing else does: the router is above the untuned model on one model,
below on two, and its learned gate is worth nothing over a uniform one on two of three.

## What the paper can say

Not "the mixture inherits breadth's locking" — that is refuted or unsupported everywhere. The
defensible three-model claim is narrower and still useful: **combining per-type adapters, by any
rule, beats training one adapter on the mixture; and merging their weights beats routing between
them.** The learned gate earns its keep on one model of three. Two grids remain.

## The rule is not re-specified

H-router-locks stays as written, with all three readings against it, because re-drawing a band after
seeing the data is how a hypothesis becomes unfalsifiable. The next two models are scored on the same
rule. If the paper wants a claim about locking, it needs a threshold chosen from the repaired
single-adapter rates *before* those two land, and that is a decision to take deliberately rather than
by editing this file.
