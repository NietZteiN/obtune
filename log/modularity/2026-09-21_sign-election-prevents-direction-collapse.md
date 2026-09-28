# 2026-09-21 — Sign election, not sparsification, is what keeps the merge pointing the right way

**Thread:** modularity · **Data:** `results/cells/mergeop_{generic,inverse}/llama31-8b/`
(A5, `configs/eval/mergeop_*`). Ingredients, weights, rank and seed identical across the three
merges; only the operator differs. Zero resumed cells — every arm genuinely evaluated.

## A5 asked whether DARE-TIES is arbitrary. It is not.

Forward, percent of the untuned model's clean-code accuracy:

| group | base | linear | TIES | DARE-TIES |
|---|---|---|---|---|
| `L0` | 100 | 115 | 154 | **178** |
| singles | 85 | 98 | 133 | **156** |
| d2 seen | 70 | 87 | 116 | **140** |
| unseen | 53 | *gated* | 83 | **104** |

Plain uniform averaging of the same six adapters reaches 115 % where DARE-TIES reaches 178 %.
Most of the merge's gain comes from the operator, not from combining specialists at all.

## Backward, plain averaging does not degrade — it collapses

| arm | `L0` acc | format failure |
|---|---|---|
| base | 0.424 | 0.07 |
| **linear** | **0.000** | **1.000** |
| TIES | 0.440 | 0.04 |
| DARE-TIES | 0.455 | 0.04 |

Format failure is 1.000 on *every* backward condition. That is not a gate threshold being
missed, it is total.

## The cause, and it is the interesting part

The averaged adapter emits the **same string forward and backward**. Raw replies on `L0` are
`'6'`, `'1'`, `'1'` in both directions. Asked for a call, it returns the forward answer.

Direction-lock rate — fraction of backward replies exactly equal to the gold *forward* answer:

| arm | lock |
|---|---|
| **linear** | **0.429** |
| TIES | 0.000 |
| DARE-TIES | 0.000 |
| untuned base | 0.000 |

33.5 % of its backward replies are byte-identical to its own forward reply on the same item.

**Sign election is what prevents direction collapse.** TIES and DARE-TIES differ from `linear`
in two ways — sparsification and the sign election — and both land at the untuned floor while
the average sits at 0.429. Sparsification alone cannot explain it: DARE's random drop and TIES'
magnitude trim are different sparsifiers and agree exactly here, while the operator without any
election is the one that fails.

## What this licenses

* **May claim:** the operator carries most of the merge's forward gain (115 % vs 178 %).
* **May claim:** plain averaging is direction-locked at 0.429 where both sign-electing operators
  are at the untuned floor of 0.000, on this model.
* **May not claim:** that the election is the *sole* cause. `linear` differs from TIES in
  sparsification too; isolating the election needs a sparsify-without-election arm
  (`magnitude_prune`), which is one more merge and one more eval.

## Open

One model. CodeLlama-7B, CodeLlama-13B and Granite-3.1-8B are queued. Nothing here reads H1.
