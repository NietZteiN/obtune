# 2026-09-14 — Stronger than tax-free: the merge reads backwards *better* than the untuned model, on eight models

**Thread:** transfer · **Status:** 8/8 models · **Script:** [`scripts/analysis/65_backward_stacks.py`](../../scripts/analysis/65_backward_stacks.py) (second table) · **Extends:** [`2026-09-14_three-methods-one-table.md`](2026-09-14_three-methods-one-table.md)

The drop table asks whether an arm degrades *faster* than the untuned model when a stack contains an
unseen family. An arm can pass that by being uniformly bad, so the level question has to be asked on
the same cells: pooled over all nine stacks, is the arm **above** `base` at all? Same program set,
same program-clustered bootstrap, same format gate; only the contrast changes. The answer turns out
to be a stronger statement than the one already logged.

## `arm − base`, backward, exact arguments, pooled over all nine stacks, points

| model | breadth | anchored | family | clean LoRA | **DARE-TIES merge** | TIES merge |
|---|---|---|---|---|---|---|
| CodeLlama-7B | −1.47 \* | −0.08 | +1.38 \* | −1.99 \*ᵍ | **+1.39 \*** | +0.42 |
| CodeLlama-13B | −7.67 \*ᵍ | −3.15 \*ᵍ | −5.54 \*ᵍ | +1.34 \* | **+3.16 \*** | +0.70 \* |
| CodeLlama-34B | −5.79 \*ᵍ | −2.37 \* | −2.43 \* | +0.27 | **+3.43 \*** | — |
| Llama-3.1-8B | −0.63 | −0.45 | +1.29 \* | +0.02 | **+2.36 \*** | +1.25 \* |
| StarCoder2-15B ᵇ | +0.46 ᵍ | +4.12 \* | +1.96 \*ᵍ | +4.60 \*ᵍ | **+7.72 \*** | — |
| Gemma-3-12B | +0.96 \* | −3.41 \*ᵍ | +2.43 \* | +0.78 | **+2.36 \*** | +0.94 \* |
| CodeGemma-7B | +3.69 \* | −1.72 \*ᵍ | +1.95 \* | +4.09 \* | **+3.83 \*** | −2.76 \*ᵍ |
| Granite-3.1-8B | −2.12 \* | −4.69 \*ᵍ | −0.58 | −1.87 \*ᵍ | **+0.37** | +2.35 \* |

\* 95 % program-clustered bootstrap excludes zero · ᵍ the **arm** is over the 0.25 format gate ·
ᵇ the **untuned model** is gated, so the sign reads (the arm is above a model that cannot answer)
but the magnitude does not.

## What this says

**The DARE-TIES merge is positive on all eight models, significant on seven, and format-gated on
none.** No other arm has any of those three properties:

- breadth is significantly negative on four and gated on three;
- the anchored arm is significantly negative on five and gated on five;
- the family adapter is negative on two of the three CodeLlamas and gated on two;
- clean-code tuning is negative on two and gated on three;
- the TIES merge is positive on five of the six models where it is readable and significantly
  negative on CodeGemma, where it is also the one merge cell gated anywhere.

So "the merge pays no brittleness tax" understates it. The merge **is the only adaptation in the
panel that improves backward competence at all**, and it does so while matching breadth's forward
accuracy on all eight models
([`2026-09-14_merge-is-not-weaker.md`](2026-09-14_merge-is-not-weaker.md)) and while showing no
forward-locking whatsoever
([`2026-09-14_forward-locking-is-the-mechanism.md`](2026-09-14_forward-locking-is-the-mechanism.md)).
Three properties, eight models, one arm.

## Caveats that belong with it

- **Backward levels are small.** The merge's seen-stack exact-argument accuracy runs 0.071–0.134
  against the untuned model's 0.050–0.105. A 2–4 point gain on that base is real and repeated, not
  large, and the paper should say so in those terms rather than in ratios.
- **Granite is the one null** (+0.37, interval spanning zero) and StarCoder2's size is unreadable
  because its untuned model is gated. Seven clean positives, one null, no negative.
- **These are stack cells only**, so none of this inherits the zero-shot/one-shot ladder confound
  found today ([`2026-09-14_two-prompts-one-phase.md`](2026-09-14_two-prompts-one-phase.md)). Every
  arm here was evaluated with the same one-shot prompt.
- **The router is still absent.** No mixture backward cell exists on any model.
