# 2026-09-22 — A5, B7 and B8 reach the paper, and the noise floor is applied to the claims it undercuts

**Thread:** writeup · **Prompted by:** user — wire the three finished reviewer-round items into the
draft, then re-read the draft against the seed floor. · **Related:**
[`../modularity/2026-09-21_seed-noise-floor.md`](../modularity/2026-09-21_seed-noise-floor.md),
[`../../docs/EXPERIMENT_QUEUE.md`](../../docs/EXPERIMENT_QUEUE.md)

## The gap this closes

A5, B7 and B8 were marked **DONE** in the queue on 09-21 and all three had result JSONs under
`results/analysis/pipeline/`. None of them was in the paper: no table emitter, no `\input`, and no
prose. `grep` over `sections/` for "operator", "deployment cost" or "noise floor" returned nothing
but two unrelated hits. "Done" meant measured, not reported.

Three emitters added, each beside the analysis script that produced the numbers, following the
`76_merge_ablation.py` idiom — no number typed into a `.tex`:

| item | emitter | table |
|---|---|---|
| A5 operator ablation | `82_merge_operator.py::_tex` | `tables/merge_operator.tex` (`tab:mergeop`) |
| B7 deployment cost | `80_deployment_cost.py --tex` | `tables/deployment_cost.tex` (`tab:deploycost`) |
| B8 seed noise floor | `83_seed_variance.py::_tex` | `tables/seed_noise.tex` (`tab:seednoise`) |

B7 reads its two JSONs rather than recomputing: the measurement needs a GPU and a fixed decode
workload, and re-running it to typeset it would change the numbers by whatever the node was doing.
`--tex` is therefore a separate, GPU-free entry point. A5 and B8 recompute from the cells, and
both reproduced their committed JSONs exactly.

## A5 is a stronger result than the 09-20 note recorded

The note said averaging "recovers 115 % where DARE-TIES reaches 178 %", from Llama-3.1-8B. Across
four models the picture is worse for averaging than that one readable row suggests: **`linear` is
format-gated on three of the four models on clean code and on the seen singles**, and the single
unseen-family cell where it is readable at all (CodeLlama-13B) puts it at **25 % against an untuned
baseline of 57 %** — worse than not merging. The direction-lock column carries the mechanism:
`linear` answers the forward question when asked to reverse on 0.174 and 0.428 of items, where TIES
is at 0.000 on both models read and DARE-TIES at 0.019 / 0.000.

So the claim in the draft is now "averaging does not merely lose, it breaks the answer contract",
with the scope stated: three operators at one density is not a search, and DARE-TIES is not shown
to be optimal.

## B7 gives the router-cost claim its number

RQ2 said the router "requires all eight experts resident at inference and a gate evaluation at
every layer and token" and stopped there. Measured: **648M / 679M stored parameters against the
merge's 80M / 84M — 8×** — +0.6–0.7 GB peak, and **throughput within 1 % of a single adapter**. The
gate is not what one pays for; the storage is. Also recorded, because it would otherwise read as a
router penalty: every adapted arm decodes at roughly half the untuned model's tokens/sec in this
unfused implementation, which is shared by all of them and separates none.

## B8, and what it actually costs the paper

The floor: median seed range **0.66 points** over 21 arm × group combinations, max **2.39**, and
**1.57 median on the held-out family** — roughly three times the clean-code figure.

It is reported in `evaluation.tex` beside the measurement conventions, because it governs how every
other number is read. The substantive edit is in **RQ3's unseen-family paragraph**. The draft
ordered the router above the merge there by `+0.96` to `+2.75` points on seven of eight models
(`+0.76` on the eighth, interval containing zero). Most of that range sits inside the seed range on
that very condition group.

**What changed and what did not.** No interval was wrong and none was recomputed: the paired
program-clustered bootstraps measure sampling variation over programs and are correct. They simply
do not contain training variation, and the prose was reading them as if they did. The claim is now
scoped to *the router system is **not below** the merge on the held-out family, on eight of eight
models*, with the direction noted as consistent across all eight and a seeded replication named as
what would settle it. `threats.tex` cross-references the floor for the single-seed comparisons.

The merge-vs-untuned margin in the same paragraph (6.6–17.6 points) is far outside anything a seed
moves and is untouched, as are the operator ablation (15–25 points), the backward merge gains
(+3.0 to +6.4) and the clean-code recovery (30–90 points).

### The exhaustive sweep found three more, all the same shape

The first pass was targeted at the claim the 09-21 entry named. A full sweep of the nine prose
sections for sub-3-point magnitudes turned up 40 candidates; most are cosines, lock rates or
format-failure rates, to which an accuracy floor does not apply. Three were real, and all three are
**an equivalence asserted from a null narrower than the floor** — the classic under-powered-null
overclaim:

1. *"Merging and clean-code tuning reach the same accuracy on unobfuscated source"* — from
   `−0.30` to `+1.38` containing zero, on `L0`, where a seed alone moves an arm by up to 1.50.
   Now: we do not separate them, and this is a limit on resolution as much as a null.
2. *"A merge of two structural specialists recovers as much clean-code accuracy as the full six"* —
   from `−1.20` to `+0.54`, same group. Now: recovers **to within about a point**, stated as a
   bound rather than an equivalence. The RQ1 takeaway carried the same sentence and was corrected
   with it.
3. The backward *"costs 1.38 to 3.47 points"* — the low end is at the floor, and the floor is
   **measured forward only**, so it does not license the backward direction either. Said so rather
   than borrowing a number from a direction it was not measured in.

None of these deletes a finding; each states it at the resolution the evidence supports. The
ablation's substantive point — that the gain is not attributable to any particular ingredient and
does not scale with ingredient count — is unchanged.

## Verification

The draft **compiles**, which is new: `envs/tex/bin/tectonic` exists on this host. `paper/NUMBERS.md`
says "there is no LaTeX toolchain on this host" and that is stale. `fse27.pdf` builds at exit 0 with
all three new labels resolved in the `.aux`; the only undefined citation is a pre-existing `ase26`,
unrelated to this work. Structural check on the three tables: column counts match their `tabular`
specs, braces balance, no `\pending` introduced.

## Scope

The noise floor is CodeLlama-7B's. The other seven models are not measured and may differ, and the
draft says so. A5's backward and lock columns exist on two models only.
