# 2026-09-21 — The seed noise floor is 0.66 points, and 2.4 on the unseen family

**Thread:** modularity · **Data:** `results/cells/seedvar_generic/codellama-7b/` (105 cells),
against seed 17 in the phases it already lives in. Script `scripts/analysis/83_seed_variance.py`.

Three independent seeds (17, 101, 202) of the same recipe, six specialists and breadth,
CodeLlama-7B. B8 asked for a noise floor because the draft narrates many 1–2 point differences
with nothing to read them against.

## Range across seeds, by condition group

| group | median range | worst arm |
|---|---|---|
| `L0` | 0.66 | breadth 1.50 |
| singles | 0.63 | breadth 1.44 |
| **unseen (`X1`)** | **1.57** | `L1b` **2.39**, `L2` 2.31 |

Over all 21 arm × group combinations: **median range 0.66 points, maximum 2.39**.

**The noise is not uniform — it is roughly three times larger on the held-out family than on
clean code.** That is the condition the paper's sharpest comparisons are made on.

## What this does and does not undercut

The paper's headline router-vs-merge claim on the unseen family is `+0.96` to `+2.75` points
across eight models, with `+0.76` on the ninth-ranked. **Several of those sit inside the
single-arm seed range on that very condition group.**

Two things must not be conflated, and the honest reading needs both:

* The published intervals are **paired program-clustered bootstraps** on one set of adapters.
  They measure sampling variation over programs and are correctly computed.
* This measures **training variation** over seeds, which those intervals do not contain at all.
  A `+0.96` point difference can be significant under the bootstrap and still be smaller than
  what a re-rolled seed moves the same arm.

So this does not show any published interval is wrong. It shows the intervals answer a narrower
question than the prose claims, and that differences under roughly 1 point on `L0`/singles, or
under roughly 2.4 points on the unseen family, should not be narrated as findings on one seed.

## Recommendation for the draft

* Report the noise floor explicitly next to the RQ tables.
* Re-read every claim of the form "arm A exceeds arm B by N points" with N below the relevant
  group's range, and either drop it or state it as within seed noise. The `+0.76` and `+0.96`
  router-merge statements are the first to check.
* Claims comfortably above the floor are unaffected: the merge−base backward gains (+3.0 to
  +6.4), the operator ablation (15–25 points between TIES and DARE-TIES), the depth result
  (+1.05 to +2.73, which is marginal on the low end and should say so), and the whole
  clean-code recovery result (30–90 points).

## Scope

One model, seven arms, three seeds. The floor is CodeLlama-7B's; other models are not measured
and may differ. Nothing here reads H1.
