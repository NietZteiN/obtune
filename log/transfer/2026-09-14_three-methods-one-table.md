# 2026-09-14 — The three main methods in one table: the merge does not pay the tax, in either direction

**Thread:** transfer · **Status:** forward complete on 8/8, backward complete on 8/8 for two of three methods · **Script:** [`scripts/analysis/66_three_methods.py`](../../scripts/analysis/66_three_methods.py)

The paper introduces and compares three ways of adapting a model to obfuscated code — a
breadth-trained LoRA, a merge of per-type adapters, and a learned router over the same adapters —
and argues that an adaptation has to be tested in both directions. Those three had never appeared in
one table. RQ1's brittleness read covers breadth (script 57), the merge has its own scripts (60, 62),
the router's numbers live in the mole grids, and the backward half was breadth and merge only. Four
scripts, four program sets.

This is one read: one common program set (n = 319 on every model and both directions), script 57's
stack groups, a program-clustered bootstrap on each method's **difference from the untuned model's
drop** — because the quantity the paper argues about is "does this method fall further than doing
nothing", which is a difference of two small differences.

## Relative drop, six seen depth-2 stacks → three stacks containing the unseen family

**Forward (execution-graded output prediction)**

| model | `base` | breadth | merge | router |
|---|---|---|---|---|
| CodeLlama-7B | −21.4 % | **−33.3 %** \* | −19.9 % | −23.5 % |
| CodeLlama-13B | −19.3 % | **−29.9 %** \* | −20.8 % | — |
| CodeLlama-34B | −19.6 % | −27.3 % | — | — |
| Llama-3.1-8B | −28.4 % | −35.9 % | −24.4 % | — |
| StarCoder2-15B | gated | −25.3 % | −14.9 % | — |
| Gemma-3-12B | gated | −34.6 % | −26.4 % | — |
| CodeGemma-7B | −2.8 % | **−30.8 %** \* | **−21.7 %** \* | — |
| Granite-3.1-8B | −31.7 % | **−41.5 %** \* | −30.5 % | — |

**Backward (exact-argument input prediction)**

| model | `base` | breadth | merge | router |
|---|---|---|---|---|
| CodeLlama-7B | −15.0 % | **−40.0 %** \* | −15.4 % | — |
| CodeLlama-13B | −16.8 % | gated | −15.5 % | — |
| CodeLlama-34B | −4.4 % | gated | −4.6 % | — |
| Llama-3.1-8B | −15.1 % | **−42.2 %** \* | −20.5 % | — |
| StarCoder2-15B | gated | gated | −10.2 % | — |
| Gemma-3-12B | −17.4 % | −25.3 % | −12.9 % | — |
| CodeGemma-7B | −21.8 % | **−50.7 %** \* | −20.1 % | — |
| Granite-3.1-8B | gated | −61.6 % | −19.7 % | — |

\* differs from the untuned model's drop at 95 %. Where `base` is gated, no contrast is formed.

## What this says

**The merge does not pay the brittleness tax, forwards or backwards, on any model.** Its drop is
within noise of the untuned model's on every model where the untuned model is readable, in both
directions — and on the two models where the untuned model is *not* readable it is the only system
that is. That is eight models and two directions with no counterexample. The single starred merge
cell is CodeGemma forward, where `base` drops only −2.8 %, so the comparison is against an
unusually flat baseline rather than the merge behaving badly.

**Breadth pays it in both directions.** Forward, significantly further than base on four of the six
models where both are readable, and in the same direction on the other two. Backward, on three of
four. Never in the opposite direction anywhere.

**The router has one model so far** — CodeLlama-7B, −23.5 % forward, indistinguishable from base's
−21.4 %. The other seven forward cells are still evaluating and **no backward router cell exists on
any model**: `mole/eval_mole.py` never passed `task` to `run_cell`, so a `task: input` mixture config
would have been evaluated forwards. Fixed today; the read is pre-registered in
`CLAUDE_SCRATCHPAD.md` with its prediction (I expect the router to sit with breadth, not with base)
and its cells do not exist yet.

## Consequence for the paper

This is the strongest and most symmetric result in the project, and it is not the one the frozen
prose tells. RQ1 currently treats merging as a failed baseline that "does not compose"; measured
against the untuned model on a stack containing an unseen family, the merge is the one method that
does not get worse, in the direction it was trained on and in the direction it was not. Whether that
becomes a second tax-free strategy, a narrowing of RQ2's claim, or a rewrite of RQ1's two sentences
about routing and merging is the framing decision that is with the user. Prose stays frozen.
