# 2026-09-13 — Backward merging on four models: positive twice, negative once, undefined once

**Thread:** modularity · **Status:** complete for the four models that have merges · **Closes:** [`2026-09-13_merging-gains-backward.md`](2026-09-13_merging-gains-backward.md), [`2026-09-13_merge-backward-reverses-on-granite.md`](2026-09-13_merge-backward-reverses-on-granite.md), [`2026-09-13_starcoder2-has-no-backward-baseline.md`](2026-09-13_starcoder2-has-no-backward-baseline.md)

`ev_invmerge_llama31-8b` landed, completing the set. `merge_dare_ties` against the untuned model,
pooled over L0–S2 and X1 on the 317 common programs:

| model | forward | backward | direction ratio | caveat |
|---|---|---|---|---|
| CodeLlama-7B | **+18.87** | **+3.21 [+1.52, +4.85]** | **+0.17** | 3 `tuned_L0` cells gated |
| Llama-3.1-8B | **+17.53** | **+2.91 [+0.80, +5.11]** | **+0.17** | `mono_all` and `cons_lam3` gated |
| Granite-3.1-8B | **+11.19** | **−7.66 [−10.08, −5.17]** | **−0.68** | 25 cells gated; no tuned control |
| StarCoder2-15B | — | — | — | untuned backward is format-failure 1.00; no contrast defined |

`merge_ties` on Llama-3.1-8B is **+3.11 [+1.25, +5.03]**, direction ratio **+0.26** — the highest
measured on this project, and on this model the plain merge beats the DARE variant backwards while
losing to it forwards.

## Where this leaves the question

**Two of the three models with a usable baseline show the merge gaining backward accuracy
significantly; one shows it losing heavily.** On Llama-3.1-8B the merge's backward gain (+2.91) also
exceeds the clean-code control's (+1.07, n.s.) and the family arm's (+1.83, n.s.), the only two tuned
arms whose cells survive the gate there.

So the earlier entries were each right about their own model and wrong as generalisations in opposite
directions. The statement the four models support:

> A weight-space merge does not reliably pay the backward cost that breadth and clean-code tuning pay.
> On two of four panel models it gains backward accuracy significantly; on one it loses heavily; on one
> the question cannot be asked because the untuned model cannot answer backwards at all.

That is enough to falsify the paper's universal ("every method that fits the forward task buys its gain
by losing backward competence") and **not** enough to claim merging is backward-safe.

## The gate is the limiting instrument, not the sample size

Across all four models the tuned comparison arms — `tuned_L0`, `mono_all`, `cons_lam3` — are the cells
that fail the 0.25 format gate, while the merge arms pass it almost everywhere. The one-shot inverse
template is CodeLlama-7B-specific, and a merge of adapters that individually collapse the format
apparently does not collapse it. That is an observation about the instrument worth following up before
any of this reaches the paper: the arms being compared are not equally measurable, and the direction
of that bias is unknown.

Adapting the inverse template per model is the experiment that would settle it, and it is not run.
