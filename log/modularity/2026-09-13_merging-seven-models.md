# 2026-09-13 — Merging on seven models: the seen-stack rule is refuted, the unseen-stack advantage is 6/7

**Thread:** modularity · **Status:** read against the pre-registered rules; only CodeLlama-34B outstanding · **Closes the series:** [`2026-09-13_merging-on-the-panel.md`](2026-09-13_merging-on-the-panel.md), [`2026-09-13_merging-on-the-panel-starcoder2.md`](2026-09-13_merging-on-the-panel-starcoder2.md), [`2026-09-13_merging-codegemma.md`](2026-09-13_merging-codegemma.md)

CodeLlama-13B and Gemma-3-12B landed (207 cells each). DARE-TIES is the best merge on all seven;
DARE-linear is format-gated on five of them and never competitive.

## `merge_dare_ties − tuned_L0` on the six seen stacks — the registered rule a

| model | value | rule a |
|---|---|---|
| CodeLlama-7B | **+0.83 [+0.01, +1.63]** | inconclusive |
| CodeLlama-13B | **+1.67 [+0.83, +2.51]** | inconclusive |
| Llama-3.1-8B | **+2.31 [+1.27, +3.38]** | **REFUTED** |
| StarCoder2-15B | −0.69 [−1.57, +0.13] | **CONFIRMED** |
| Gemma-3-12B | **+1.27 [+0.32, +2.22]** | inconclusive |
| CodeGemma-7B | +0.44 [−0.48, +1.36] | inconclusive |
| Granite-3.1-8B | **+1.57 [+0.76, +2.46]** | inconclusive |

**Five of seven are significantly above the clean-code control**, one is below, one flat. The rule I
registered — merging does not beat the control on seen stacks — is confirmed on one model, refuted on
one, and inconclusive on five because the intervals sit inside the ±1-point equivalence margin I chose.
The margin was too tight for the effect: the honest reading is that **merging beats the clean-code
control on seen stacks by about a point to two, on most models**, which is not what I predicted.

## `merge − breadth` on stacks containing the unseen family — the thing that keeps replicating

| model | merge − breadth | merge − anchored |
|---|---|---|
| CodeLlama-7B | **+2.35 [+0.63, +3.97]** | **−1.39 [−2.72, −0.05]** |
| CodeLlama-13B | **+2.48 [+0.89, +4.08]** | +0.08 [−1.23, +1.39] |
| Llama-3.1-8B | **+3.09 [+1.54, +4.60]** | +0.81 [−0.47, +2.12] |
| StarCoder2-15B | **+1.70 [+0.05, +3.32]** | +0.39 [−0.92, +1.80] |
| Gemma-3-12B | **+1.83 [+0.39, +3.40]** | −0.18 [−1.57, +1.20] |
| CodeGemma-7B | −0.13 [−1.67, +1.44] | +0.92 [−0.47, +2.35] |
| Granite-3.1-8B | **+2.20 [+0.50, +3.84]** | **+2.98 [+1.28, +4.65]** |

**Six of seven significant, none negative.** And against the anchored objective the merge is
*indistinguishable* on four models, below on one (CodeLlama-7B), above on one (Granite). On **X1 alone**
the merge beats breadth on every model measured, by +2.3 to +5.2.

## What the seven models support

- Merging is **below breadth and anchoring on seen stacks** (breadth −1.4 to −3.8, anchoring −2.4 to −5.7
  where significant) — rule b confirmed on four, inconclusive on three, never refuted.
- Merging **does not pay breadth's unseen-family tax**, on six of seven.
- Merging is **at or slightly above the clean-code control** on seen stacks, which is what my
  registration got wrong.
- Against anchoring on unseen-containing stacks the two are **statistically indistinguishable on four of
  seven models**. That is the comparison the paper's contribution rests on, and it is much closer than
  the single-model number suggested.

CodeLlama-34B is the last model; its S2 specialist is training.
