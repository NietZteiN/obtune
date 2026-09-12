# Experiment checklist — what is still to run, in priority order

*Last updated: 2026-09-12*

The target is one table per model covering **every approach × every obfuscation level**, plus the
clean-code baseline in both directions. This file tracks what that costs and what is done.

**Costs are measured, not estimated.** Per-model training cost comes from the 104
`training_summary.json` files already on disk (`train_runtime_s` ÷ `n_train`); evaluation cost from
the ~45 s/cell observed on h200 for a 7B multi-LoRA grid.

## What exists today

| model | base | clean LoRA | breadth (all obf.) | anchored | family | 5 specialists | merges | router | ICL |
|---|---|---|---|---|---|---|---|---|---|
| CodeLlama-7B | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (5) | ✅ | ✅ |
| CodeLlama-13B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| CodeLlama-34B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Llama-3.1-8B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| StarCoder2-15B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gemma-3-12B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| CodeGemma-7B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Granite-3.1-8B | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Routing, merging and ICL exist on one model of eight.** Everything else in the requested table is
one evaluation away; those three need training first, and that is where the cost is.

Coverage by *condition*: the six-rung ladder and the held-out family (X1) are complete for all eight
models. The six **seen** depth-2 composites and the depth-3/4 stacks exist for CodeLlama-7B only.
The six **unseen-containing** composites are complete for all eight (done 2026-09-12).

---

## P0 — evaluation only, no training, completes most of the requested table

| # | experiment | what it adds | cost |
|---|---|---|---|
| **C1** | **Reverse task on all 8 models**, all seven conditions incl.\ clean code | the clean-code reverse baseline, and turns "undamaged backwards" from a 7B observation into a panel statement | ~4 GPU-h (13B/34B already queued) |
| **C2** | **ICL / one-shot on all 8 models**, six ladder conditions | the in-context-learning row of the table, against tuned arms on identical items | ~3 GPU-h |
| **C3** | **Seen composites on the 7 models that lack them** — base, clean, breadth, anchored on the six depth-2 stacks | the "including some stacks" column, and lets the seen-vs-unseen stack dissociation be read per model rather than on CodeLlama alone | ~4 GPU-h |
| **C4** | **F1 — routing and merging on stacks**, CodeLlama-7B: 4 routing arms, 5 merges, 3 specialists on the 10 existing composites + the router's per-item expert distribution | the last claim slot in RQ1 that has no evidence at all. **Every arm already exists**; config + eval only | ~2 GPU-h |

**P0 total ≈ 13 GPU-h and no training.** It fills every cell of the requested table except routing,
merging and ICL on the seven models that have no specialists.

---

## P1 — the training that routing and merging on all models actually requires

Routing and merging are *built from* the five per-condition specialists. Without them there is
nothing to route between or merge. Measured cost, per model, for all five:

| model | min / 1k rows | 5 specialists | then merges | then router |
|---|---:|---:|---|---|
| Llama-3.1-8B | 6.62 | **2.5 h** | CPU, free | ~1 h |
| CodeGemma-7B | 8.60 | **3.2 h** | CPU, free | ~1 h |
| Granite-3.1-8B | 9.37 | **3.5 h** | CPU, free | ~1 h |
| StarCoder2-15B | 9.57 | **3.6 h** | CPU, free | ~1 h |
| CodeLlama-13B | 11.54 | **4.3 h** | CPU, free | ~1 h |
| Gemma-3-12B | 12.43 | **4.7 h** | CPU, free | ~1 h |
| CodeLlama-34B | 21.93 | **8.2 h** | CPU, free | ~1.5 h |
| **all seven** | | **30.0 GPU-h** | **0** | **~7.5 GPU-h** |

| # | experiment | cost |
|---|---|---|
| **C5** | 5 specialists × 7 models | **30 GPU-h** |
| **C6** | TIES / DARE-TIES / DARE-linear / two L0-anchored merges, 7 models — CPU from C5's weights | **0** |
| **C7** | routing gate × 7 models, then the routing arms | **~7.5 GPU-h** |
| **C8** | evaluate C5–C7 on all conditions + stacks | **~10 GPU-h** |

**P1 total ≈ 48 GPU-h.** This is the price of "routing, merging and breadth on all models".

> **Recommendation: do P1 on a 3-model subset first** — Llama-3.1-8B, StarCoder2-15B and
> Granite-3.1-8B (2.5 + 3.6 + 3.5 = **9.6 GPU-h** of training). They span three lineages and
> straddle the panel's split: Granite is the model that *refuted* the anchoring result, StarCoder2
> the one that replicated everything. If routing and merging behave the same on all three as on
> CodeLlama-7B, the remaining four models buy variance, not a finding.

---

## P2 — hardening, after the table is complete

| # | experiment | what it buys | cost |
|---|---|---|---|
| **C9** | **F8** — second seed for breadth and anchored at 13B | turns RQ3's scale column from one draw into a band | ~13 GPU-h |
| **C10** | **F5** — held-out family and two of its stacks rebuilt at obfuscation seeds 101/202/303 | tests whether anchoring learned a *new surface cue* rather than a capability. ⚠ needs plumbing: the eval-item emitter reads canonical variant directories and has no flag for an alternate build | ~1 GPU-h + ~2 h dev |
| **C11** | **F6 / E5b** — a genuinely hard second family with a *different* surface | the only experiment that would settle the surface-vs-mechanism question E6 returned *undecided* on | ~1 CPU-day + 1.5 GPU-h |

---

## Blocked, and honestly so

- **Everything JavaScript.** `node` is not installed on this cluster. The corpus transferred intact
  so it can be *used*; it cannot be *regenerated*, which blocks the JS held-out family and any new
  JS condition.
- **Nothing else is blocked.** Re-test a blocker before believing it — four of six items once
  recorded as blocked turned out not to be (`MASTER_REPORT` §29.8).

## Struck

- ~~**F4** — compute-matched control for anchoring.~~ **Vacuous as specified**: with λ = 0 the
  objective *is* breadth training, so the control already exists in every comparison.
  **13 GPU-h saved.** See `log/transfer/2026-09-12_f4-is-vacuous-as-specified.md`.

---

## Rules that apply to every item above

1. **Pre-register before submitting.** Decision rules go in `CLAUDE_SCRATCHPAD.md` and are committed
   *before* the job is submitted, and the cell inventory is printed *before* the prediction is
   written — a prediction recorded after the data exists is not a prediction
   (withdrawn example: `CLAUDE_SCRATCHPAD.md`, 2026-09-12).
2. **Common subset first.** Coverage differs by condition; record the program set before any system
   is evaluated.
3. **No held-out-family stimulus is ever stacked** and its evaluation budget is spent — every
   held-out number uses the trainable sibling X1.
4. **A new config is checked before it is queued**: every adapter path must resolve, or the run
   silently scores the base model under another arm's name.
