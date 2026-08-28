# Geometry, redundancy, and three attempted repairs

*Written 17 August 2026. Covers the 15–17 August chain. Self-contained: it assumes no prior
knowledge of this project.*

> **Superseded on 2026-08-27** by [`MASTER_REPORT_2026-08-27_router-and-merging.md`](MASTER_REPORT_2026-08-27_router-and-merging.md),
> the closing report for this thread. Every number below reproduces from cells. Two corrections:
> the noise floor quoted here is the **pooled Python+JavaScript** figure, where the Python-only bar
> is 0.63 / 1.46 — which changes how the `mole_hardrouter` ≈ `mole_router` equivalence may be
> stated; and §8's owed `H1` read of the best merge density has since landed at **32.2** against
> `merge_dare_ties`' 34.8, i.e. the density headroom does not transfer.

Five experiments and one infrastructure audit. Two of the experiments cost **zero GPU** and one of
those produced the most consequential finding. Every number is recomputed from committed cells
under `results/cells/` or from adapter safetensors under `runs/`; the master report
([`MASTER_REPORT_2026-08-12.md`](MASTER_REPORT_2026-08-12.md)) has the surrounding detail and
§-references below point into it.

---

## 1. The setting, in half a page

A model is shown a **self-contained function and one concrete input** and must predict the exact
return value. Grading runs the real code, so there is no grader subjectivity.

The same program is rewritten in ways that provably preserve behaviour: `L1b` adversarial renaming
(names made to *lie*), `L1r` random hex renaming, `L2` minification, `S1` control-flow flattening,
`S2` opaque predicates + dead code, `S3`/`S4` the two halves of `S2`, and **`H1` — the held-out
obfuscator** (string encoding + mixed boolean-arithmetic), quarantined and never trained on.
**Composites** (`C_L1r_S1`, …) stack two transforms.

The question is what fine-tuning learns: **semantic invariance** (robustness to the whole class of
meaning-preserving rewrites) or **transform memorization** (undoing the specific obfuscators seen).
Accuracy on trained conditions cannot separate these; `H1` can, which is why tuning anything
against `H1` destroys the only instrument that distinguishes them.

### The systems — every name used in this report

All are the same frozen base model (Qwen2.5-Coder-1.5B-Instruct) plus a **LoRA adapter**: a small
trainable weight patch (~0.5 % of model size, "rank 32" = the size of its low-rank bottleneck).

| name | what it is |
|---|---|
| `base` | the untouched pretrained model, no adapter |
| **`tuned_L0`** | one adapter trained on **clean code only**. **This is the control for everything.** |
| `tuned_<X>` | a *specialist* — one adapter trained on condition `X` alone (`tuned_S2`, `tuned_L1b`, …) |
| `mono_all` | one adapter trained on all six trainable conditions at once |
| `loto_hold<X>` | trained on five of the six conditions, then scored on the held-out sixth — an honest unseen-transform measurement using only trainable data |
| `merge_ties`, `merge_dare_ties` | the six specialists algebraically **merged into one adapter**. TIES keeps the largest-magnitude half of the proposed updates and resolves sign conflicts by majority; DARE first drops 50 % at random and rescales the survivors. One adapter, no decision at inference. |
| `l0merge_*` | the same merge algorithms applied to **three clean-code adapters** (seeds 17/42/101) instead of six specialists — the control that asks whether merging does anything at all |
| `crossseed_*` | introduced in §4: the six specialists merged, but each drawn from a *different* seed |
| `router` | a small classifier reads the program, predicts which obfuscation it is, and the matching specialist is applied. 100 % accurate here. |
| `mole_router` / `mole_hardrouter` | **RouterLoRA** — eight specialists kept separate with a trained gate weighting them per token and per layer (`hardrouter` = the same gate forced to one-hot) |
| `icl_k1`, `icl_k2` | no training at all — *k* worked examples in the prompt |
| `oracle_prompt_1shot` | no training — the untuned model is simply *told* which obfuscation was applied |
| `norm_full` | no training — a symbolic code normalizer applied before the model sees the program |
| `s2fam`, `composite_trained`, `composite_ablation` | the three new arms of §5 |

**Why `tuned_L0` is the control and not `base`.** The base model is weak at the *task itself*, so
against it every adapter looks excellent. Only the gap to a clean-code-trained adapter isolates what
**obfuscation** training buys. Most numbers below are best read against `tuned_L0`.

**The noise floor.** Two seeds of the same system differ by **1.32 points on average, 3.61 at the
95th percentile**. Nothing smaller is an effect. A separate, smaller floor (0.1–0.4 pts) comes from
vLLM batching nondeterminism.

**Two evaluation grids, never pooled.** Grid A (`heldout`, 557 corpus programs) and Grid B
(`testset`, 40 ICSE programs) are disjoint: `base` scores 6.4 % on `H1` in one and 11.3 % in the
other. Every table below states its grid.

**Where the chain starts.** On 15 August the project had just closed RQ2 negatively by elimination
(§12.10): the transform *is* identifiable from the residual stream (linear probe 99.4 % vs 16.7 %
chance), the mixture gate *can* be made to route on it, routing correctly buys **+0.4 pts** (inside
noise), merging three clean-code adapters matches merging six specialists on `H1`, and holding a
transform out of a multi-condition adapter costs ~1.1 pts. The conclusion — **the per-condition
experts carry nothing distinct** — was strong but rested on two soft spots: nobody had checked
whether the systems fail on the *same items*, and nobody had attempted a repair.

---

## 2. Experiment 1 — are the systems complementary? No, they are redundant

**The problem.** On `H1`, the best merge of six obfuscation specialists (`merge_dare_ties`, 34.8 %)
and a single adapter trained only on clean code (`tuned_L0_k0`, 33.9 %) score the same. A tie in the
*margin* says nothing about the *overlap*. If the two succeed on different items, distinct
capability exists and merely isn't extractable — which would soften §12.10 considerably.

**The design.** `scripts/analysis/24_item_agreement.py`: pairwise 2×2 concordance, exact McNemar,
Jaccard on the correct-sets, and the oracle-of-k (per item, did *any* system get it right).

**The trap this had to avoid.** An oracle-of-k rises mechanically with k — *k* independent coins at
1/3 each cover 1−(2/3)^k of the items — so a raw "oracle headroom" number invites exactly the wrong
conclusion. The script therefore computes a **permutation null** that preserves every system's
marginal accuracy exactly and destroys only the item-difficulty coupling. Real systems are
positively coupled (easy items are easy for everyone), so the observed oracle should sit *below*
that null; how far below is the actual measure of redundancy.

**Result** — both grids, and they agree:

| | Grid B `H1` (n=115, 7 systems) | Grid A `H1` (n=1214, 10 systems) |
|---|---|---|
| best single | 34.8 % (`merge_dare_ties`) | 28.0 % (`tuned_S2_s17`) |
| oracle-of-k | 48.7 % | 39.0 % |
| raw "headroom" | +13.9 pts | +11.0 pts |
| **independence null** | **93.6 %** [89.6, 97.4] | **91.9 %** [90.5, 93.2] |
| **observed − null** | **−44.9 pts** | **−52.9 pts** |
| mean pairwise φ | +0.625 | +0.621 |
| items solved by **no** system | 59 / 115 (51 %) | 740 / 1214 (61 %) |
| items solved by **every** system | 17 | 40 |

The headline pair is a clean null on its own: `merge_dare_ties` × `tuned_L0_k0` is both-34 /
merge-only-5 / L0-only-6 / neither-70, McNemar p = 1.000.

**The systems are highly redundant, and the distribution is bimodal** — items are solved by
everything or by nothing. **This hardens §12.10 rather than softening it.** The raw headroom is a
k-artifact and must never be quoted without the null.

One signal survives: `tuned_S2_s17` is both the most accurate system on `H1` (28.0 %) and the
specialist with the most sole-solved items (16) — it uniquely gets items nothing else does. That
pointed directly at Experiment 4.

---

## 3. Experiment 2 — task-vector geometry is mostly initialization

The project measures **task vectors** ΔW = (α/r)·B·A — the weight change an adapter represents —
and reports pairwise cosine and **sign conflict** (the fraction of coordinates where two experts
disagree in sign; TIES merging deletes exactly those). §5.3 uses these to test Horoi et al.'s claim
that over-training experts causes parameter interference that degrades merging.

Only two of six adapter banks had ever been measured. Covering the rest (CPU only; the script needed
one additive `--seeds` flag, because it could not express a cross-seed bank at all) produced this:

| bank | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
|---|---|---|---|---|
| `L0` at seeds {17, 42, 101} — **byte-identical training data** | **0.053** | **0.487** | 0.765 | 0.374 |
| 8 specialists at seed 17 — **completely different transforms** | **0.592** | 0.391 | 0.861 | 0.371 |
| 6 specialists at seed 42 | 0.575 | 0.388 | 0.845 | 0.370 |
| 6 LOTO folds at seed 17 | 0.576 | 0.382 | 0.850 | 0.804 |

Individual `L0` cross-seed pairs: 0.0533 / 0.0531 / 0.0539. Same-seed `L0|S3`: 0.697.

**Three adapters trained on identical data are near-orthogonal, while eight adapters trained on
completely different transforms are 0.59-aligned.** LoRA initializes `A` randomly and `B` at zero,
so each seed selects a different rank-32 subspace; same-seed adapters share it and drift together,
different-seed adapters do not. Sign conflict at 0.487 is a coin flip — maximum disorder.

**Consequences.**

1. **Every §5.3 geometry figure is same-seed**, so it measures *drift within one shared subspace*,
   not how different the experts' knowledge is — which is how the Horoi framing reads it. The
   observations stand; the interpretation does not, and §5.3 now carries that caveat.
2. **Sign conflict demonstrably does not bound merged accuracy.** The L0-merge control is built from
   that near-orthogonal bank — the worst geometry in the project — and merges *fine*
   (`l0merge_dare_ties` = .339 on `H1`, identical to `tuned_L0`). A merge at maximal sign conflict
   lost nothing. That is stronger than §5.3's "the mechanism reproduces but the consequence does
   not": the diagnostic's premise fails.
3. **Any geometry→accuracy regression must be stratified by seed.** Same-seed and cross-seed merge
   points live in different geometric regimes; pooling them fits a line through an artifact.

**Two structural findings from the same pass.**

**The LOTO folds are effectively one vector.** Each fold trains on five of six transforms. Mean
cosine to the other five spans only **0.565–0.583** and norms **0.7998–0.8099** — dropping an entire
transform from a five-condition mixture moves the update *less than the spread between folds*. That
is §12.10's "the experts carry nothing distinct" visible directly in weight space, which nothing had
shown before. Fold norms are ~2× the single-condition specialists (0.80 vs 0.33–0.38) but no better
aligned to each other. The ordering also does not track accuracy — `holdS1` is the most
geometrically distinct yet mid-pack (37.3), `holdL0` the least distinct and highest (41.7).

**The inert-material family is the most coherent cluster in the bank**, and the closest to the
clean-code direction:

| pair | cosine | | pair | cosine |
|---|---|---|---|---|
| `S2\|S3` | **0.698** | | `L0\|S2` | 0.653 |
| `S2\|S4` | **0.691** | | `L1b\|S2` | 0.547 |
| `L0\|S3` | 0.697 | | `S1\|S2` | **0.518** |

Note also that **`S2` is *not* geometrically special** (mean cosine 0.604 vs bank mean 0.592 —
mid-pack). The outlier is `S1` (0.496, norm 0.331) — the condition that transfers to nothing and
actively damages others. **Distinctness tracks interference, not transfer.** The coherence of
`S2/S3/S4` is what motivated Experiment 4's curriculum; the alignment decays with training (top pair
0.826 → 0.723 over nine epochs), which is why that arm kept the 3-epoch recipe.

### 3.1 Decomposing an expert: mostly "learn the task", a little "learn the transform"

The natural next question is whether the experts *disagree*. They mostly do not — they **agree**, and
what they agree on is the task rather than the transform. Projecting each expert's task vector onto
the clean-code direction ΔW_`L0` (norm-weighted over all 196 modules):

| expert | cos(ΔW_c, ΔW_L0) | fraction along ΔW_L0 | residual fraction |
|---|---|---|---|
| `L1b` | 0.581 | 0.581 | 0.814 |
| `L1r` | 0.632 | 0.632 | 0.775 |
| `L2` | 0.614 | 0.614 | 0.789 |
| `S1` | 0.521 | 0.521 | 0.854 |
| `S2` | 0.661 | 0.661 | 0.750 |
| `S3` | 0.634 | 0.634 | 0.774 |
| `S4` | **0.699** | 0.699 | 0.716 |

**52–70 % of every specialist points the same way as an adapter that never saw an obfuscated
program.** That is the weight-space form of the project's central result: the bulk of what
fine-tuning buys is task acquisition, not transform inversion.

**But the residual is not noise — it carries family structure.** Removing the ΔW_`L0` component and
re-measuring the pairwise cosines among the *residuals* gives mean **0.284** (range 0.174–0.451),
against 0.592 for the full vectors — and the ordering is exactly what the transfer matrix predicts:

| residual pair | cos | | residual pair | cos |
|---|---|---|---|---|
| `L1b`\|`L2` | **0.451** | | `L1r`\|`S1` | 0.185 |
| `S2`\|`S4` | **0.438** | | `L1r`\|`S2` | 0.175 |
| `L1r`\|`L2` | 0.391 | | `L1r`\|`S4` | **0.174** |
| `S2`\|`S3` | 0.391 | | | |

The top pairs are within-family (two identifier-destroying transforms; two halves of `S2`); the
bottom pairs are cross-family. **The condition-specific knowledge exists, is real, and clusters by
family** — it is simply a minority direction sitting under a dominant shared one.

**This quantifies the merge dilution.** Measured directly rather than bounded:
‖mean residual‖ / mean‖residual‖ = **0.6255**, so averaging the seven residuals at weight 1/7 costs
**≈37 % of every specialist-specific update by norm**, while the shared component — which all seven
agree on — survives intact. (The pure-orthogonality bound √7/7 = 0.378 would predict a 62 % loss;
the residuals' mild mutual alignment, mean cosine 0.284, is exactly why the real figure is milder.
Quoting the bound instead of the measurement would overstate the effect by 25 points.)

That is why a merge lands near the clean-code control: **the merge preserves precisely the part that
`tuned_L0` already had, and dilutes the part that made each specialist a specialist.**

**And it prescribes a fix that needs no new machinery.** Writing the intended update as
ΔW = ΔW`L0` + γ·(1/n)·Σ residualₑ and expanding residualₑ = ΔWₑ − sₑ·ΔW`L0` gives a plain linear
combination of the *original* task vectors:

> weight on `L0` = 1 − (γ/n)·Σ sₑ  ·  weight on each specialist = γ/n

with sₑ the projection coefficients above (0.475–0.727, Σ = 4.181) and γ = 1/0.6255 = 1.599 chosen
to restore a single specialist's residual magnitude. That evaluates to **`L0` = +0.045, each
specialist = +0.228** (against uniform 1/8 = 0.125) — i.e. *up-weight every specialist ~1.8× and
drop the clean-code ingredient, because the shared direction is already supplied by the specialists
themselves.* `MergeSpec` already accepts explicit `weights`, so this is a re-weighting of the
validated merge driver rather than new mathematics — and it sidesteps the rank ceiling that blocks
exact task arithmetic (`combination_type="cat"` sums ranks: two r32 experts reach vLLM's
`max_lora_rank: 64`, and eight would need r256).

**And it explains the collapsed mixture gate (§12.8) mechanically.** RouterLoRA weights *whole* task
vectors, ~60 % of which is a direction identical across every expert. A gate whose output barely
depends on the input is therefore a *good* optimum: most of what it is weighting does not vary by
condition. The routing problem as posed had roughly 40 % of its signal carrying all of the
information — which is the concrete reason a load-balancing term was needed to make it route at all,
and why routing correctly still bought nothing.

---

## 4. Experiment 3 — does merging care about orthogonality? Only DARE-TIES does

Experiment 2 raised a general question: the L0-merge control succeeded at cosine 0.05, so is LoRA
merging simply insensitive to task-vector orthogonality? A prediction was **registered in the script
docstring before the run**: if the effect is within the seed band, merging is insensitive.

**The design** (`scripts/merge/24_crossseed_control.py`, CPU): the same six conditions, same rank,
recipe, algorithms and density as the headline merges — only the seed each expert is drawn from is
altered (`L0@17, L1b@42, L1r@17, L2@42, S1@17, S2@42`). That makes 9 of 15 pairs cross-seed and
moves mean cosine **0.563 → 0.246**, holding the ingredients fixed. Magnitude was checked before
queueing (the diagnostic that caught the `merge_dare_linear` 7.175× scale artifact): ‖ΔW‖ ratios
0.244 / 0.675 vs 0.189 / 0.623 same-seed — nothing collapsed.

| bank | cosine | L0 | L1b | L1r | L2 | S1 | S2 | mean |
|---|---|---|---|---|---|---|---|---|
| `merge_dare_ties` pure s17 | 0.563 | 49.4 | 39.8 | 42.0 | 50.0 | 44.1 | 44.3 | **45.0** |
| `merge_dare_ties_s42` pure s42 | 0.575 | 50.6 | 40.3 | 43.8 | 48.9 | 43.4 | 46.6 | **45.6** |
| `crossseed_dare_ties` **MIXED** | 0.246 | 45.5 | 36.9 | 40.9 | 44.9 | 40.0 | 39.8 | **41.3** |
| `merge_ties` pure s17 | 0.563 | 41.5 | 31.8 | 34.1 | 38.6 | 38.6 | 32.4 | 36.2 |
| `merge_ties_s42` pure s42 | 0.575 | 41.5 | 32.4 | 33.0 | 39.2 | 37.9 | 33.0 | 36.2 |
| `crossseed_ties` **MIXED** | 0.246 | 41.5 | 33.0 | 32.4 | 38.1 | 37.9 | 31.8 | 35.8 |

Cluster bootstrap by `program_id`, 2000 draws, 1,025 matched items / 40 programs:

| contrast | Δ pts | 95 % CI | McNemar |
|---|---|---|---|
| DARE-TIES mixed − pure s17 | **−3.61** | [−6.95, −0.30] | 0.0002 |
| DARE-TIES mixed − pure s42 | **−4.29** | [−7.51, −1.07] | <0.0001 |
| TIES mixed − pure s17 | −0.39 | [−1.40, +0.57] | 0.50 |

**Refuted for DARE-TIES, confirmed for TIES.** The obvious confound is ruled out rather than argued:
both *pure* banks are equivalent (45.0 vs 45.6; 36.2 vs 36.2), so the mixed bank's loss comes from
mixing seeds, not from the s42 adapters being individually worse. DARE-TIES is negative on all six
conditions.

**Mechanism.** DARE drops 50 % of each task vector at random and rescales the survivors. In a shared
subspace the survivors still reinforce; when the vectors are near-orthogonal, dropping half destroys
more than it preserves. TIES has nothing to lose — it is already the weaker merge (36 vs 45) and its
sign election is near-random either way.

**Why this matters for §12.10, and it goes the right way.** The L0-merge control — the gate for the
whole RQ2 conclusion — is **necessarily cross-seed**, because three `L0` adapters can only differ by
seed, while `merge_dare_ties` is same-seed. So that control was running ~4 points handicapped
against the arm it controls for. Seed-matched, a clean-code merge would land *above* the
six-specialist merge on `H1` rather than level with it. §12.10's conclusion is therefore
**understated, not overstated** — but the asymmetry must be reported, because a reviewer who spots
that the control is cross-seed will otherwise read it as a defect rather than as a bias against our
own conclusion.

---

## 5. Experiment 4 — two training-side repairs, both null

§12.10's honest weakness: five things were measured and nothing was tried as a fix. Two were tried.

| arm | trained on | rows | rationale |
|---|---|---|---|
| `s2fam` | S2, S3, S4 | 14,037 | §3.5's `S2`→`H1` is the one replicated positive transfer, found by accident on an adapter trained on equal footing with everything else. This trains for it deliberately. `S3`/`S4` are the two halves of `S2`, so this is the whole inert-material family and nothing more — §4 showed breadth is actively destructive to this exact transfer. Experiment 2 supplied the precondition: these three vectors are the most mutually aligned in the bank, so they should compose rather than interfere. |
| `composite_trained` | 6 stacked `C_*` | 22,152 | Every trainable condition is single-transform; `H1` is not. Stacked variants are the closest available proxy for "unseen transform = unfamiliar combination of familiar mechanisms". |
| `composite_ablation` | L1b, L1r, L2, S1, S3, S4 | 22,152 | The same six mechanisms **unstacked**. Without it, "trained on composites" is confounded with "trained on more mechanisms". The pair is the experiment; neither half is. |

Scored on Grid A (`heldout`, n = 1,667) — the same items as `mono_all`, `tuned_L0` and the LOTO
folds. **`H1` deliberately unread**: these arms were still being selected, and CLAUDE.md §3.2 rule 2
forbids selecting on the discriminator.

| system | what | L0 | L1b | L1r | L2 | S1 | S2 | **mean** |
|---|---|---|---|---|---|---|---|---|
| `base` | untrained | 21.7 | 18.8 | 18.7 | 19.8 | 20.7 | 15.3 | 19.18 |
| `tuned_L0` | clean code only, **4,689** rows | 44.7 | 34.3 | 36.7 | 37.8 | 39.0 | 41.8 | **39.04** |
| `mono_all` | all 6 conditions, 26,841 rows | 41.6 | 38.1 | 36.7 | 37.9 | 39.2 | 41.5 | **39.15** |
| `s2fam` | inert-material curriculum | 44.4 | 32.0 | 36.6 | 36.8 | **41.4** | **43.8** | **39.16** |
| `composite_trained` | stacked | 39.8 | 37.9 | 37.8 | 37.3 | 38.3 | 39.7 | **38.46** |
| `composite_ablation` | unstacked | 42.3 | **38.6** | 37.7 | 37.9 | 39.5 | 42.8 | **39.81** |

Cluster bootstrap by `program_id`, 2000 draws:

| contrast | Δ pts | 95 % CI | verdict |
|---|---|---|---|
| **stacked − unstacked** | **−1.36** | [−2.63, +0.04] | null, sign *against* the hypothesis |
| **`s2fam` − `tuned_L0`** | **+0.02** | [−0.95, +1.02] | null, and unusually tight |
| `composite_ablation` − `tuned_L0` | +0.77 | [−0.46, +2.03] | null |
| `s2fam` − `mono_all` | −0.07 | [−1.39, +1.12] | null |

**These are generalization nulls, not in-distribution ones.** `s2fam` never saw
L0/L1b/L1r/L2/S1; `composite_trained` never saw *any* single transform. Most columns are OOD.

**The per-condition shape reproduces the thesis exactly.** `s2fam` tops the `S2` column (43.8) and
the `S1` column (41.4) — the structural family it trained on — and is the *worst* row on `L1b`
(32.0). Wins where it trained, nowhere else, net zero. Training *for* the mechanism reproduces the
mechanism's locality rather than escaping it.

**And `tuned_L0` at 4,689 rows remains statistically indistinguishable from every multi-condition
adapter**, including one with 5.7× the data. Whatever binds this task, it is neither training-set
size nor obfuscation exposure.

**What this does not show.** §3.5's `S2`→`H1` is a claim about `H1`. The curriculum is flat on the
*trainable* ladder; whether it reaches the held-out obfuscator is the question it was built for, and
it is still open.

**Caveats.** One seed per arm, so ~1-point differences sit inside the 1.32-pt mean seed band.
`s2fam` carries a 37 % data deficit (14,037 is the realised S2+S3+S4 train pool) — pre-registered as
making a *win* interpretable and a *loss* unattributable. The result is neither; it is flat.

---

### 5.1 The third repair — preserving the residuals, and it does not help either

§3.1 prescribed a fix with a measured mechanism behind it rather than a hunch: a uniform merge
discards ~37 % of each specialist-specific update while keeping all of the shared part, so supply the
shared component once at full strength and leave the residuals undiluted. Because that expands to a
plain re-weighting of the original vectors (`L0` = +0.045, each specialist = +0.228 against uniform
0.125), it needed no new merge algorithm and no rank growth — only the `weights` argument
`MergeSpec` already accepts (`scripts/merge/25_residual_merge.py`, CPU).

Built at both densities that matter and evaluated on Grid B, six trainable conditions:

| system | L0 | L1b | L1r | L2 | S1 | S2 | **mean** | format-fail % |
|---|---|---|---|---|---|---|---|---|
| **residual** dare d0.3 | 44.3 | 36.4 | 45.5 | 46.6 | 37.9 | 43.2 | **42.31** | 0.5 |
| **residual** dare d0.5 | 47.2 | 39.2 | 46.0 | 50.0 | 44.8 | 47.7 | **45.82** | 0.7 |
| uniform dare d0.3 (sweep winner) | 48.3 | 42.6 | 49.4 | 48.9 | 44.1 | 48.9 | **47.03** | 0.4 |
| uniform dare d0.5 (headline) | 49.4 | 39.8 | 42.0 | 50.0 | 44.1 | 44.3 | **44.95** | 1.5 |
| **residual** ties d0.5 | 40.9 | 32.4 | 34.7 | 38.6 | 38.6 | 35.2 | 36.74 | 1.7 |
| uniform ties d0.5 | 41.5 | 31.8 | 34.1 | 38.6 | 38.6 | 32.4 | 36.17 | 1.4 |

Cluster bootstrap by `program_id`, 2000 draws:

| contrast | Δ pts | 95 % CI | verdict |
|---|---|---|---|
| matched density d0.5, `dare_ties` | +0.88 | [−0.66, +2.47] | null |
| matched density d0.5, `ties` | +0.59 | [−0.92, +1.94] | null |
| residual best vs uniform best | −1.27 | [−4.61, +2.25] | null |
| **matched density d0.3, `dare_ties`** | **−4.68** | **[−8.20, −1.33]** | **significantly WORSE** |

**Null at matched density, and actively harmful at the sweep-winning density.** The d0.3 damage has a
clean cause: DARE rescales survivors by 1/density (3.33× at d=0.3), which compounds with the
up-weighted specialists (weights summing to 1.644) to give ‖ΔW‖ = **1.99×** a single expert. Format
failure stayed healthy at 0.5 %, so this is not a `merge_dare_linear`-style artifact — the
over-scaled update simply predicts worse. The best merge in the project remains **uniform
`dare_ties` at d = 0.3 (47.03)**.

**Why this is worth reporting rather than filing away.** The dilution is geometrically real — 37 % of
each residual is genuinely lost — and correcting it changes nothing. So the diluted component was not
carrying recoverable accuracy in the first place. That upgrades §12.10 from "no combination strategy
we tried helps" to something sharper: **the condition-specific part of each expert, even preserved at
full magnitude and correctly weighted, carries no extractable per-condition value.** The negative
result now has a measured mechanism rather than an empirical sweep behind it.

### 5.2 Settling it at power — and a warning about the grid everything was read on

The Grid B read of §5.1's arm looked like the project's first positive result on the discriminator:
`residual_dare_ties` 41.7 on `H1` against the headline merge's 34.8, the only contrast in the
confirmatory pass to survive BH-FDR (q=0.048, McNemar b/c = 8/0). Two defects had to be cleared
before it could mean anything.

**First, it was not attributable.** That arm merged EIGHT ingredients while `merge_dare_ties` merges
six (`ties_v1.yaml`: `adapters: [L0, L1b, L1r, L2, S1, S2]`), so the reweighting and two extra
experts differed at once. **Second, 115 items over 27 programs cannot resolve a 3-point effect**
against a 3.61-pt seed band. Both were fixed: matched 6-ingredient arms at both expert-bank seeds,
a uniform-8 control to isolate ingredient count, and the whole design re-run on **Grid A `H1`,
n=1,214 over 405 programs** (phase `final`, because these system names already occupy the `main`
paths as Grid B cells and `cell_dir` does not key on `eval_source`).

| arm | ingr | weights | bank | **Grid A** | Grid B |
|---|---|---|---|---|---|
| A | 6 | uniform | s17 | 23.9 | 34.8 |
| **B** | 6 | **residual** | s17 | **25.9** | 37.4 |
| C | 8 | uniform | s17 | 23.1 | 35.7 |
| **D** | 8 | **residual** | s17 | 25.3 | **41.7** |
| F | 6 | uniform | s42 | 24.9 | 38.3 |
| **E** | 6 | **residual** | s42 | 25.6 | 41.7 |
| `tuned_L0` | — | — | — | **24.5** | 33.9 |
| `tuned_S2_s17` | — | — | — | **28.0** | — |

Cluster bootstrap by `program_id`, BH-FDR over the family:

| contrast | Δ | 95 % CI | b/c | q | |
|---|---|---|---|---|---|
| **B−A weighting (s17)** | **+1.98** | [+0.49, +3.62] | 49/25 | **0.018** | **significant** |
| **D−C weighting at 8 ingredients** | **+2.22** | [+0.91, +3.54] | 51/24 | **0.012** | **significant** |
| E−F weighting (s42) — replication | +0.74 | [−0.74, +2.06] | 43/34 | 0.362 | null |
| C−A ingredient count | −0.82 | [−1.73, +0.08] | 13/23 | 0.221 | null |
| **D − `tuned_L0`** | **+0.74** | [−0.58, +1.98] | 34/25 | 0.362 | null |

**The verdict is three-part and none of it changes the thesis.** The residual weighting is *real and
small* — +1.98 and +2.22 at two ladder sizes, both surviving FDR at proper power, and it is not
ingredient count (−0.82, null). It **does not replicate on an independent expert bank** (+0.74 on
s42, null). And it **does not beat the clean-code control**: the best residual arm is +0.74 over
`tuned_L0`, null, while `tuned_S2_s17` (28.0) still beats every merge in the project. So: a ~2-point
improvement to *merging*, with equivocal replication, that leaves the invariance question untouched.
That is the "bounded rather than promising" reading, registered in advance.

> ### The Grid B warning, which matters more than the residual result
>
> **Grid B overstated the effect by 3–5×.** The same contrast is +7.0 (q=0.048) on 115 items and
> +1.4 raw / +1.98 matched on 1,214. Every arm dropped ~10 points between grids, and the *ordering*
> changed: `D` was the top arm on Grid B (41.7) and is mid-pack on Grid A (25.3).
>
> **Grid B `H1` — 115 items over 27 programs — cannot support merge comparisons.** It produced one
> q=0.048 "survivor" that shrank to a third of its size at power. Every `H1` merge number the RQ2
> conclusion has been read against is from that grid: `merge_dare_ties` 34.8, `tuned_L0_k0` 33.9,
> `l0merge_dare_ties` 33.9, `mole_router` 33.9. They should carry an explicit power caveat, and any
> future `H1` merge claim should be made on Grid A.
>
> **The one thing this run does firm up is §12.10 itself.** At n=1,214 the best uniform merge scores
> **23.9 against the clean-code control's 24.5** — the merge is, if anything, slightly *below* the
> control rather than level with it. The central negative result now holds at ten times the power it
> was established on.

### 5.3 The Grid A panel corrects §12.10's gating claim

Completing the panel on Grid A (`merge_ties`, `l0merge_ties`, `l0merge_dare_ties`; `merge_dare_ties`
was already there) put every `H1` number the RQ2 conclusion rests on onto the 1,214-item grid. It
changes the reading.

| system | **Grid A** (n=1214) | Grid B (n=115) |
|---|---|---|
| `base` | 6.4 | 6.4 |
| `merge_ties` | 19.5 | 28.7 |
| `l0merge_ties` | 21.3 | 30.4 |
| `l0merge_dare_ties` — the control | **21.4** | 33.9 |
| `mono_all` | 22.9 | 22.9 |
| `merge_dare_ties` — headline merge | **23.9** | 34.8 |
| **`tuned_L0` — THE CONTROL** | **24.5** | 24.5 |
| `residual_n6_s42` — best residual arm | 25.6 | 41.7 |
| `tuned_S2_s17` | **28.0** | 28.0 |

| contrast | Δ | 95 % CI | q | |
|---|---|---|---|---|
| 6-specialist merge vs `tuned_L0` | −0.66 | [−1.89, +0.66] | 0.358 | null |
| **6 specialists vs 3× clean-code merge** | **+2.47** | [+1.24, +3.71] | **0.0001** | **significant** |
| **3× clean-code merge vs ONE clean-code adapter** | **−3.13** | [−4.86, −1.57] | **0.0001** | **significant** |
| `tuned_S2_s17` vs `tuned_L0` (§3.5) | **+3.46** | [+2.06, +4.86] | **0.0000** | **significant** |

**§12.10's gating claim does not survive the power increase.** It read: *"merging three clean-code
adapters reaches the same `H1` accuracy as merging six specialists"* — 33.9 vs 34.8 on Grid B, a
0.9-point gap taken as a tie. At n=1,214 the gap is **+2.47 and highly significant**. The specialists
*do* contribute to the merge.

**What the panel actually shows is two offsetting effects that Grid B could not separate:**

1. **Merging costs ~3 points.** Merging three clean-code adapters scores 21.4 against a single
   clean-code adapter's 24.5 (−3.13, significant). That is the dilution of §3.1 measured directly on
   `H1`, in a bank where there is no specialist knowledge to lose — so it isolates the cost of the
   operation itself.
2. **Specialists recover ~2.5 of it** (+2.47, significant).

Net, the six-specialist merge lands 0.66 below the clean-code control, null — the same bottom line as
before, reached for a materially different reason. **"The per-condition experts carry nothing
distinct" is too strong and should be retired.** They carry something worth +2.5 points into a merge;
it is simply cancelled by what merging costs. The defensible statement is narrower and more
interesting: *combination methods pay a dilution cost that is about the size of the specialist
contribution they are trying to exploit, so the net is a wash.*

**§3.5 is also confirmed at power**: the `S2` specialist beats the clean-code control by **+3.46**
[+2.06, +4.86], q < 0.0001, on 1,214 items. It remains the only system in the project that beats the
control on the held-out obfuscator, and `s2fam` (26.6) does not reach it.

---

## 6. What the chain adds up to

§12.10 concluded that no combination strategy can extract value the experts do not carry. This chain
supplies three independent confirmations and one correction:

| line of evidence | what it adds |
|---|---|
| **Item-level redundancy** (§2) | The systems fail on the *same* items — oracle 45–53 pts *below* an independence null. There is no hidden complementary capability for a better method to find. |
| **Weight-space redundancy** (§3) | Dropping an entire transform from a five-condition mixture moves the task vector less than the spread between folds. The same conclusion, visible in the weights. |
| **Attempted repairs** (§5, §5.1, §5.2) | Training deliberately for the one transfer that works buys **+0.02 pts**; training on stacked transforms is **−1.36**; preserving the condition-specific residuals at full magnitude is **+0.88** at matched density and **−4.68** at the best density. Three fixes, all null. |
| **Correction** (§3, §4) | The geometry diagnostics measure shared initialization, not shared knowledge; sign conflict does not bound merged accuracy; and the gating L0-merge control was ~4 pts handicapped, making §12.10 conservative. |

The negative result is now supported at the item level, in weight space, and against two attempted
repairs — and its principal control is biased *against* it rather than for it.

---

## 7. Infrastructure defects found and fixed

Four defects, and three share the signature this project keeps re-encountering: **a failure that
would leave the pipeline reporting success, or would land only after the expensive part was paid
for.**

| # | defect | consequence | status |
|---|---|---|---|
| 1 | `eval_vllm.run_ckpt_select` called `load_pairs` without `allow_composites` | `QuarantineViolation` **after a 5.3-hour training run** — checkpoint selection impossible for any composite-trained arm | **fixed**, forwarded from the same config the adapter was trained with; guard verified still active for non-opted-in configs |
| 2 | `scripts/preflight.py` validated `train_conditions` against `TRAINABLE_CONDITIONS` only | 6 hard errors → preflight permanently red, and a gate that always fails is a gate nobody reads | **fixed**, same pattern |
| 3 | `build_manifest.py --eval` silently drops any system whose `arch` starts with `merge` | A config mixing merge and non-merge systems queues some and drops the rest without saying so. `--rq2` is not the fix — it *rebuilds* the standard merges and would overwrite `runs/adapters/.../merge_*` | **documented**; used the hand-written queue entry the density sweep also uses |
| 4 | `train_size: 30000` in the LOTO configs never binds | The configs reason from 38,346 rows, which is *all splits*. Realised: folds **22,152–23,373**, `mono_all` **26,841** (+21 %). So "LOTO diagonal 38.0 vs `mono_all` 39.1" is not like-for-like — the true cost of holding a transform out is *smaller* than the reported 1.1 pts | **recorded**; correction owed in its own commit |

Defects 1 and 2 share one root cause worth stating: `allow_composites` was designed as "a narrow
allowance requested explicitly by the one caller that needs it" — RouterLoRA, which trains through
`mole/train_mole.py`. The first `train_sft` arm to use composites walked through every *other*
caller that never received the opt-in. A narrow allowance is only narrow until a second caller
appears.

**Two gaps left open deliberately.** There is no orphan recovery while `pipeline.sh` is not running
(`--requeue-stale` is only invoked by `supervise.sh`), so a worker that dies mid-run leaves its
claim in `running/` forever and nothing notices. And training loss is unobservable for the first
~hour because `worker.py` launches jobs with `stdout` block-buffered to file and no
`PYTHONUNBUFFERED` — the reference run's first loss lines appear, clumped, at step 200. Both are
one-line fixes to files another session was concurrently editing.

---

## 8. What is still open

* **The one batched confirmatory `H1` pass** — now the decisive item. It owes reads for: the
  curriculum and composite arms (§5), the best merge density (`d=0.3`, best on 5 of 6 trainable
  conditions and never read on `H1`), the seed-42 merge replicate, the cross-seed merges (§4), and
  the balanced RouterLoRA gate. One pass, declared in `ACCESS_LOG.md` as a third pass.
* **§3.5 is untouched.** `S2`→`H1` remains the project's one replicated positive transfer, and the
  curriculum arm's effect on it is unmeasured.
* **The geometry→accuracy regression**, now with ~45 merge points on disk — and it must be
  stratified by seed (§3).
* **The invariance-loss arm** — the only remaining attempted repair, and the only one that optimizes
  invariance as an *objective*. Designed, not built; needs `invariance` added to
  `schema.TrialRow.adapter_arch` first, or it fails at the first row written.
* **More held-out families.** `H1` is one obfuscator and is partly burned. `H1∘S1` composites are
  the cheap version; a virtualization-based `H2` is the honest one.
* **Everything here is 1.5B and single-seed.** Five of seven obfuscation penalties largely dissolve
  by 7B, so these findings must be scoped as "at a scale where these transforms still cost the model
  something".

## Provenance

- Cells: `results/cells/main/qwen25c-1.5b/python/` — `{s2fam, composite_trained,
  composite_ablation, crossseed_ties, crossseed_dare_ties}__{L0…S2}`, plus the pre-existing
  comparators.
- Analysis: `results/analysis/item_agreement_*.json`, `results/merge_geometry/{loto, l0seeds,
  adapters_s42}_qwen25c-1.5b_python.json`.
- New code: `scripts/analysis/24_item_agreement.py`, `scripts/merge/24_crossseed_control.py`,
  `scripts/merge/20_geometry_report.py --seeds`, `configs/train/{s2fam, composite,
  composite_ablation}_qwen1.5b_py.yaml`, `configs/eval/{crossseed_merge,
  curriculum_composite}_qwen1.5b.yaml`.
- Statistics: cluster bootstrap by `program_id`, 2000 resamples, seed 17; exact McNemar on
  discordant pairs; permutation null for every oracle-of-k.
- Training: 11.0 GPU-h total (2.02 + 5.29 + 3.67), one attempt each, zero failures. Grading is
  strict normalized exact match, execution-verified.
- Lab notes: [`../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md`](../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md)
  and its same-day addendum.

## Changelog

- **2026-08-17** — Created, covering the 15–17 August chain: item-level agreement, task-vector
  geometry as an initialization artifact, the cross-seed merge control, the two attempted repairs,
  the residual merge, and four infrastructure defects.
