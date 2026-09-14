# 2026-09-14 — The control: the merge is not flat because it is weak

**Thread:** transfer · **Status:** control for [`2026-09-14_three-methods-one-table.md`](2026-09-14_three-methods-one-table.md) and [`2026-09-14_forward-locking-is-the-mechanism.md`](2026-09-14_forward-locking-is-the-mechanism.md) · **Script:** [`scripts/analysis/66_three_methods.py`](../../scripts/analysis/66_three_methods.py)

Two results today rest on the merge behaving like the untuned model: its drop from seen stacks to
unseen-containing ones is within noise of `base`'s in both directions, and its forward-collapse rate
is at `base`'s floor. A method that learned nothing would show both. That has to be ruled out
before either result means anything, and it is the obvious first objection a reviewer will raise.

**Forward accuracy, pooled over the six ladder conditions:**

| model | `base` | breadth | anchored | **merge** |
|---|---|---|---|---|
| CodeLlama-7B | 0.206 | 0.393 | 0.405 | **0.388** |
| CodeLlama-13B | 0.221 | 0.428 | 0.446 | **0.433** |
| CodeLlama-34B | 0.220 | 0.473 | 0.501 | **0.472** |
| Llama-3.1-8B | 0.226 | 0.399 | 0.421 | **0.415** |
| StarCoder2-15B | 0.000 | 0.498 | 0.516 | **0.485** |
| Gemma-3-12B | 0.283 | 0.480 | 0.488 | **0.487** |
| CodeGemma-7B | 0.206 | 0.425 | 0.432 | **0.423** |
| Granite-3.1-8B | 0.267 | 0.396 | 0.382 | **0.387** |

**The merge matches breadth's forward accuracy on all eight models**, never more than 0.013 below it
and above it twice. It is nowhere near the untuned model. So "the merge does not drop because it
never learned" is false: it learned the same amount, measured on the task the adapters were trained
on, and then did not pay the two prices breadth pays.

`66_three_methods.py` now prints the seen-stack accuracy under every drop row for exactly this
reason — a drop column alone cannot tell robustness from having nothing to lose, and the two
readings belong together rather than in two scripts.

**One number to flag.** StarCoder2's untuned forward accuracy on the ladder is **0.000**. That is
not a rounding of something small; the model produces nothing the forward grader accepts. Every
StarCoder2 contrast is therefore against a floor, which is why its `base` cells are format-gated
almost everywhere in both directions. It is the panel's one non-instruction-tuned-style checkpoint
behaving like one, and it should be said in the paper rather than left for a reader to notice in a
table.

**The router has breadth's level, not the merge's.** On CodeLlama-7B, the only model where it is
measured so far: 0.342 against breadth's 0.344 and the merge's 0.319. Its drop, −23.5 %, is
indistinguishable from `base`'s −21.4 %. So on the one model available the router looks like breadth
on level and like base on brittleness, which is a combination nothing yet explains, and its
forward-collapse cell is still empty. The prediction registered in `CLAUDE_SCRATCHPAD.md` is that it
will collapse like the single-adapter arms.
