# 2026-09-21 — A5 on four models: averaging does not merely underperform, it fails

**Thread:** modularity · **Data:** `results/cells/mergeop_{generic,inverse}/`, four models forward
and two backward. Script `scripts/analysis/82_merge_operator.py`.
Follows [`2026-09-21_sign-election-prevents-direction-collapse.md`](2026-09-21_sign-election-prevents-direction-collapse.md),
which reported Llama-3.1-8B alone and is superseded in scope, not in direction.

## Forward, percent of the untuned model's clean-code accuracy

| model | group | base | linear | TIES | DARE-TIES |
|---|---|---|---|---|---|
| CodeLlama-7B | `L0` | 100 | *gated* | 142 | **164** |
| | unseen | 46 | *gated* | 88 | **105** |
| CodeLlama-13B | `L0` | 100 | *gated* | 163 | **188** |
| | unseen | 57 | **25** | 95 | **120** |
| Llama-3.1-8B | `L0` | 100 | 115 | 154 | **178** |
| | unseen | 53 | *gated* | 83 | **104** |
| Granite-3.1-8B | `L0` | 100 | *gated* | 133 | **151** |
| | unseen | 58 | *gated* | 72 | **82** |

**Plain averaging is format-gated on almost every cell of every model.** The single-model reading
made it look like a weak-but-working operator at 115 %; across four models it mostly produces
output that cannot be parsed at all. Where it is readable on the unseen family it scores **25 %**
against the untuned model's 57 % — worse than not merging.

Two orderings hold everywhere they are readable:

* `linear` $\ll$ TIES — sparsification and sign election are not cosmetic.
* TIES $<$ DARE-TIES on all four models, by 15–25 points of the reference.

## Direction lock, backward `L0`

| model | base | linear | TIES | DARE-TIES |
|---|---|---|---|---|
| CodeLlama-7B | 0.000 | **0.174** | 0.000 | 0.019 |
| Llama-3.1-8B | 0.000 | **0.428** | 0.000 | 0.000 |

The averaged adapter answers the *forward* question when asked to reverse, on both models. Both
sign-electing operators sit at or near the untuned floor.

## What A5 now licenses

The reviewer's objection was that DARE-TIES "looks arbitrary" with no averaging control. It is not
arbitrary: on four models the control does not merely lose, it fails the answer contract, and the
two sign-electing operators separate from it and from each other consistently.

**Still not licensed:** that the *election* specifically is the cause. `linear` differs from TIES
in sparsification too. Isolating it needs a sparsify-without-election arm (`magnitude_prune`),
which is one merge and one eval and is not run.

## Scope

Backward on two models: the other two backward runs were cancelled to stay inside a 15-GPU cap
after the forward answer was already unambiguous on four. Nothing here reads H1.
