# 2026-09-14 — Two backward prompts in one phase: the ladder was zero-shot on seven of eight models

**Thread:** transfer · **Status:** found, repair queued, affected claims marked · **Affects:** [`2026-09-13_inverse-core-three-scales.md`](2026-09-13_inverse-core-three-scales.md) and every reading of `62_merge_backward.py`

## What is wrong

`results/cells/inverse_generic/` holds backward cells written by four different configs, and they do
not all use the same prompt.

| cells | config | `prompt_id` |
|---|---|---|
| ladder (L0–S2, X1), CodeLlama-7B | `inverse_generic.yaml` | `inverse_1shot_v1` |
| ladder (L0–S2, X1), **the other seven models** | `inverse_core.yaml` | **`inverse_v1`** |
| all 16 stacks, all eight models | `inverse_stacks.yaml` | `inverse_1shot_v1` |
| ladder, merge arms, all models | `inverse_merge.yaml` | `inverse_1shot_v1` |

`inverse_core.yaml` carries no `one_shot: true` on any of its five systems. Everything else does. So
one column of the master table's backward block mixes a zero-shot read of the ladder with a one-shot
read of the stacks, on seven models — and one row of it compares zero-shot arms against one-shot
merges.

## How large the difference is

CodeGemma-7B, `mono_all`, two comparable conditions:

| cell | prompt | format-fail | accuracy |
|---|---|---|---|
| `mono_all__L1b` | `inverse_v1` | **0.882** | 0.049 |
| `mono_all__C_L1b_S1` | `inverse_1shot_v1` | **0.086** | 0.276 |

The stacked condition is *harder* and scores five times better. The gap is the demo, not the task.

## What this invalidates, and what it does not

**Invalidated, pending the re-read.** The sentence "the backward template was written for
CodeLlama-7B and fails the gate on most cells of the other panel models" describes the ZERO-SHOT
template, which those seven models are the only cells that ever got — CodeLlama-7B was never
evaluated under it. The "20 of 35 gated backward cells" count is the same artefact.
`62_merge_backward.py` reads the ladder, so its format-gate exclusion lists and part of its merge
advantage are a prompt difference rather than a method difference; a warning now sits at the top of
that script and its output should not be quoted until the re-read lands.

**Not affected.** Every stack-based read: [`65_backward_stacks.py`](../../scripts/analysis/65_backward_stacks.py)
and [`66_three_methods.py`](../../scripts/analysis/66_three_methods.py). All sixteen stacks, on all
eight models, for every arm, were written one-shot. So yesterday's eight-model dissociation and
today's three-method table stand exactly as logged, including the result that the merge pays no
brittleness tax in either direction. Nothing in those two tables crosses the prompt boundary.

## The repair

`configs/eval/inverse_ladder_1shot.yaml` re-runs `inverse_core.yaml`'s five arms — `base`,
`tuned_L0`, `mono_all`, `cons_lam3`, `tuned_X1` — on the seven ladder conditions with `one_shot:
true`, for the seven affected models. It writes to a **new phase**, `inverse_1shot`, for two
reasons: `run_cell` resumes on (phase, system, condition), so pointing it at `inverse_generic` would
silently skip every cell it is meant to replace; and the old cells are not wrong, they are a
different prompt, and keeping both readings on disk is what lets the size of this effect be
measured rather than argued about.

`59_master_tables.py`, `65` and `66` now read `["inverse_1shot", "inverse_generic"]`, first hit
wins. CodeLlama-7B and every stack cell are unaffected by that order because they only exist in
`inverse_generic` and were already one-shot.

## The process fault

Four configs wrote into one phase over three days and nothing compared their prompts. The cell
metadata records `prompt_id` precisely so that this is checkable, and no analysis script checks it.
A phase should not accept two prompt ids for the same task without saying so — the cheapest fix is
a guard in `cellkit.load_cell` that refuses a pooled read whose cells disagree on `prompt_id`. Not
written yet; noted here so it is not lost.
