# 2026-09-18 — The one-way transfer replicates on a second model, and is now in the paper

**Thread:** transfer · **Extends:**
`2026-09-18_backward-training-transfers-forward-but-not-the-reverse.md`, which reported CodeLlama-7B
alone and said so. Llama-3.1-8B's evals have landed (46 cells per direction).

## Both models, backward-trained control against the untuned model

| model | backward (its own task) | forward (what it costs) |
|---|---|---|
| CodeLlama-7B | **+10.30** [+8.5, +12.1] \* | **+9.63** [+7.8, +11.4] \* |
| Llama-3.1-8B | **+5.18** [+3.2, +7.2] \* | **+7.19** [+5.6, +8.8] \* |

Raw: CodeLlama-7B backward 0.285 → 0.388 and forward 0.170 → 0.267; Llama-3.1-8B backward
0.337 → 0.389 and forward 0.192 → 0.263. Exact-argument recovery rises on both (0.085 → 0.129,
0.088 → 0.118), so the backward gain is not an artefact of execution grading's permissiveness.

**All four contrasts positive and significant.** Training on input prediction improves both
directions on both models. The magnitude differs --- CodeLlama-7B gains twice as much backwards ---
but the sign and significance do not.

## Why this is the mechanism result

The panel could only show that forward-trained arms lose the backward direction. It could not say
whether that was forward training's doing or the backward task being unreachable. This control
separates them: inversion is reachable, and reached more effectively by training on it (+10.3, +5.2)
than by any forward-trained arm (best +3.56). So the losses reported throughout are caused by forward
training rather than by the task.

And the asymmetry is what the paper now leads the mechanism with. Same programs, same rank, same data
budget: backward training improves forward accuracy, forward training damages backward accuracy.
Forward training is narrow in a direction.

## In the paper

Section 6.4 gains a paragraph with all four contrasts; Section 7.1 cites the control as the direct
demonstration that the two views are not redundant --- a single view cannot distinguish "improved at
both" from "improved at one and lost the other", and two views separate them at once.

Two models, not eight. Stated as such in both places.
