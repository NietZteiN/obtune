# 2026-09-15 — The merge's backward *gain* does not replicate on the 1.5 B pilot; its *ordering* does

**Thread:** transfer · **Data:** `results/cells/inverse_generic/qwen25c-1.5b/` (70 cells, run 400692,
completed 2026-09-14) · 14 conditions, paired on 557 programs, cluster bootstrap, seed 17.

The pilot model was never asked the backward question until yesterday — the inverse task postdates it.
Its cells are now on disk, which makes Qwen2.5-Coder-1.5B a fifth lineage and a scale 20× below the
panel's largest, at no GPU cost. It is the obvious out-of-panel test of the paper's load-bearing claim.

## It fails the claim as stated

| arm | backward − untuned |
|---|---|
| clean LoRA | **−6.78** \* |
| breadth | **−8.73** \* |
| **DARE-TIES merge** | **−2.24** \* |
| TIES merge | −0.11 |

On the eight-model panel DARE-TIES is *above* the untuned model on seven and null on one, and neither
merge is ever significantly below it. On the pilot DARE-TIES is significantly **below** base, by 2.24
points. The paper's sentence — "never significantly below the untuned model in any regime on any
model" — is scoped to the eight-model panel and remains true as written, but it is not a universal
claim and this is the counterexample.

## What does replicate is the ordering

The merges still lose far less than the single adapters: −2.24 and −0.11 against −6.78 and −8.73. The
gap between the best merge and the best single adapter is 6.7 points, the same shape as the panel. So
"composing specialists costs less backward than monolithic training" replicates on the pilot; "composing
specialists *gains* backward over the untuned model" does not.

## The most likely reason, and how to settle it

Scale is the obvious candidate — 1.5 B against 7–34 B — and the panel offers weak support: the two
smallest panel models have the two smallest merge gains among the significant ones. But the pilot also
differs in lineage, in training era, and in its condition set (it has S3/S4 as standalone transforms and
no held-out family), so scale is not identified. Settling it needs a second small model in a panel
lineage, which is cheap: a 1.5–3 B CodeLlama or Qwen sibling trained on the panel's six conditions.

## For the paper

Report it. The pilot is already a table in the appendix; adding one line to the threats section —
that the backward gain is a panel result and the one sub-2 B model tested shows only the ordering,
not the gain — costs a sentence and removes the strongest objection a reviewer can raise from data we
ourselves published.
