# 2026-09-14 — The router, backwards, second model: Granite says the opposite of Llama

**Thread:** modularity · **Status:** two of five models read · **Rule:** `CLAUDE_SCRATCHPAD.md`, registered before any cell existed

## Forward collapse, Granite-3.1-8B, 23 backward conditions

| `base` | `tuned_L0` | `mono_all` | `cons_lam3` | `tuned_X1` | `merge_dare_ties` | `merge_ties` | **`mole_router`** |
|---|---|---|---|---|---|---|---|
| 0.056 | 0.182 | 0.077 | 0.313 | 0.031 | 0.001 | 0.000 | **0.089** |

The rule: CONFIRMED above 0.05 and inside the single-adapter band (0.10–0.35); REFUTED below 0.01;
0.01–0.05 inconclusive. **0.089 clears the 0.05 threshold and falls just short of the band** — a
gap the rule did not name. The honest reading is that on this model the router *does* lock:
eighty-nine times the merge floor, above the untuned model's own 0.056, between breadth (0.077)
and clean-code tuning (0.182). Recorded as **CONFIRMED on the threshold clause, short of the band**,
not rounded either way.

So after two models the hypothesis is **split**: Llama-3.1-8B 0.001 (refuted, at the merge floor);
Granite-3.1-8B 0.089 (locks). The merges are at the floor on both. Whether the mixture inherits
locking is model-dependent; whether the merge does is not.

## Backward accuracy, the nine stacks, paired (n = 557)

| contrast | exact arguments | by execution |
|---|---|---|
| router − untuned | −1.09 [−2.30, +0.02] | **−2.18** [−4.12, −0.21] \* |
| router − uniform gate | **+0.54** [+0.12, +0.99] \* | **+2.05** [+1.23, +2.96] \* |
| router − breadth | **+1.48** [+0.72, +2.23] \* | **+3.85** [+2.51, +5.17] \* |
| merge − router | **+1.13** [+0.53, +1.80] \* | **+2.29** [+1.17, +3.47] \* |

Levels (exact args): untuned 0.071, breadth 0.046, uniform 0.055, router 0.060, merge 0.072.

Three differences from Llama, all in the same direction. The router is **below the untuned model**
here (significantly by execution), where on Llama it was above. The learned gate is **worth
something over uniform** here (+0.54 / +2.05, both significant), where on Llama it was a tie. And
the merge is again the best arm backwards and again beats the router. What holds on both models:
router above breadth, merge above router, merges at the collapse floor.

One caution that belongs with every Granite backward number: its untuned model sits at 0.204
format-failure on these stacks, near the 0.25 gate, so `base` is a weaker reference here than on
Llama (0.088).

## What two models say

The claim the paper can make about the mixture is narrower than either model alone suggested:
**the mixture is never as good as the merge backwards, and whether it forward-locks depends on the
model** — not at all on Llama, substantially on Granite. The merge's behaviour does not depend on
the model. Three grids to go; the panel verdict is the count, and it is already clear it will not
be unanimous.
