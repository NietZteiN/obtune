# 2026-09-13 — The merge's backward gain reverses on Granite

**Thread:** modularity · **Status:** REPORTED (the registration made only CodeLlama-7B a verdict) · **Qualifies:** [`2026-09-13_merging-gains-backward.md`](2026-09-13_merging-gains-backward.md)

`ev_invmerge_granite31-8b` landed (14 cells). Read the same way, on the same 317 programs:

| model | `merge_dare_ties` forward | backward | direction ratio |
|---|---|---|---|
| CodeLlama-7B | **+18.87** | **+3.21 [+1.52, +4.85]** | **+0.17** |
| Granite-3.1-8B | **+11.19** | **−7.66 [−10.08, −5.17]** | **−0.68** |

`merge_ties` moves the same way on both, smaller: −0.02 on 7B, −0.24 on Granite.

**So the merge's backward gain is not a property of merging.** It is a property of DARE-TIES on
CodeLlama-7B, and it reverses — hard — on the model that already reverses RQ3's anchoring repair.
Granite is now the counter-model for two separate findings, which is a pattern about that model
rather than two coincidences.

## What survives of the earlier entry

The earlier entry's headline claim about the *paper* stands, because it is a universal: the abstract
and RQ1 say **every** method that fits the forward task buys its gain by losing backward competence,
and one arm on one model that gains is enough to falsify it as written. What does **not** survive is
any reading of that entry as "merging is backward-safe". It is not; on Granite it is the worst arm
measured in either direction.

The honest statement, on two models: *the backward cost of a merge is model-dependent and can be
large in either direction.* That is weaker than what either single model suggests and is the only
form the evidence supports.

## Read with care: the controls are gated on Granite

**Twenty-five of Granite's backward cells fail the 0.25 format gate** — every `tuned_L0`, `mono_all`
and `cons_lam3` cell, and four of `tuned_X1`. Only `base` and the two merge arms are interpretable, so
this table has no clean-code control, no breadth and no anchored comparison on Granite; the merge is
being compared to the untuned model alone. The one-shot inverse template is CodeLlama-7B-specific and
this is the same collapse recorded on 2026-09-13 for the panel backward grids.

That the merge arms pass the gate where every tuned arm fails it is itself worth noting and not
explained: a merge of adapters that individually collapse the format apparently does not.

StarCoder2 and Llama-3.1-8B are still running; both may be gated the same way.
