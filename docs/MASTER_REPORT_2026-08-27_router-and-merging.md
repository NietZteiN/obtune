# RQ2 — routing and merging: the master report

*Last updated: 2026-08-27. Self-contained: it assumes no prior knowledge of this project.*

**This is the closing report for one research thread** — the attempt to build a system that is
good at *all* obfuscations by combining adapters that are each good at *one*. The thread ran
2026-08-05 → 2026-08-17, produced **110 combination systems / 1,208 evaluation cells / 393,997 graded trials**
under `results/cells/` (within a 1.5B/Python surface of 1,918 cells; §3), and ended negative. It has three predecessor documents
([`MASTER_REPORT_2026-08-12.md`](MASTER_REPORT_2026-08-12.md) §5 and §12.10,
[`REPORT_2026-08-15_modularity_verdict.md`](REPORT_2026-08-15_modularity_verdict.md),
[`REPORT_2026-08-17_geometry-and-attempted-repairs.md`](REPORT_2026-08-17_geometry-and-attempted-repairs.md))
but **no single document that covers the whole arc and states where it landed**. This is that
document, and it supersedes all three *on RQ2 only*. The project-wide master report is
[`MASTER_REPORT_2026-08-27.md`](MASTER_REPORT_2026-08-27.md), whose §12.12–§12.13 carry this
content in project context — §12.10 of the 08-12 master report in
particular states a conclusion that §5.3 of the 08-17 report already retired.

Every number here was **recomputed from the per-cell parquets on 2026-08-27**, not copied from the
earlier reports. Where a recomputation disagrees with a published number, §8 says so. Three
disagreements were found; none reverses the verdict, one changes how a secondary claim may be
stated, and one is a measurement-noise problem that affects every `H1` number in the project.

---

## Contents

- [1. The verdict, in one paragraph](#1-the-verdict-in-one-paragraph)
- [2. The setting](#2-the-setting)
- [3. What was built — the full inventory](#3-what-was-built--the-full-inventory)
- [4. The headline table](#4-the-headline-table)
- [5. Arm by arm](#5-arm-by-arm)
- [6. Why this is a dead end, and not "our method underperformed"](#6-why-this-is-a-dead-end-and-not-our-method-underperformed)
- [7. What survives](#7-what-survives)
- [8. Corrections found on re-checking, 2026-08-27](#8-corrections-found-on-re-checking-2026-08-27)
- [9. What would have to be true to reopen the thread](#9-what-would-have-to-be-true-to-reopen-the-thread)
- [10. Provenance and reproduction](#10-provenance-and-reproduction)

---

## 1. The verdict, in one paragraph

Six LoRA specialists were trained, one per obfuscation. Every way of combining them was then
built and measured: a **perfect hard router** (100.0 % dispatch accuracy), **three weight-space
merge algorithms** at three densities and two seed banks, an **eight-expert learned mixture**
routed per token and per layer, a **monolithic** adapter trained on everything at once,
**leave-one-transform-out** folds, **oracle prompting**, and three **attempted repairs**. On the
held-out obfuscator `H1` — the only condition that separates *learning the class of
meaning-preserving rewrites* from *memorising the six rewrites you were shown* — **not one
combination beats an adapter trained on clean code alone.** The best merge lands −0.66 pts
[−1.89, +0.66] against that control on 1,214 items; the best mixture lands inside noise; the
monolithic adapter lands −1.65 [−3.79, +0.49]. The reason is now measured rather than assumed:
combination pays a **dilution cost of ≈3.1 pts** that is about the same size as the **≈2.5 pts**
of specialist knowledge it is trying to exploit, so the net is a wash — and the systems fail on
the *same items* (oracle-of-10 sits **52.9 pts below** an independence null), so there is no
hidden complementary capability for a better combiner to find. **The thread is closed. Three
things came out of it worth keeping** (§7), the largest being that a single specialist,
`tuned_S2`, *does* beat the control on `H1` by **+3.46** [+2.06, +4.94] — a transfer that
combination consistently destroys.

---

## 2. The setting

### 2.1 The task

A model is shown a **self-contained function and one concrete input** and must emit the exact
return value. No chain of thought. Grading executes the real code, so there is no grader
subjectivity; scoring is normalized exact match with a reported format-failure rate.

### 2.2 The obfuscation ladder

Every rewrite provably preserves behaviour (each variant is executed against its parent's inputs
plus fuzzed ones).

| code | what it does |
|---|---|
| `L0` | the clean original, comments and docstrings stripped — **not obfuscated** |
| `L1b` | **adversarial** renaming — identifiers replaced with actively *misleading* ones |
| `L1r` | random renaming — identifiers become meaningless hex |
| `L2` | minification — identifiers become `a`, `b`, `c`…, annotations stripped |
| `S1` | control-flow flattening — the body becomes a dispatch loop over a state variable |
| `S2` | opaque predicates **+** dead code |
| `S3` / `S4` | the two halves of `S2` alone (dead code only; opaque predicates only) |
| `C_X_Y` | **composites** — two transforms stacked on one program |
| **`H1`** | **the held-out obfuscator** — string encoding + mixed boolean-arithmetic. **Never trained on by anything.** |

`H1` is the instrument. Accuracy on a *trained* condition cannot tell semantic invariance from
transform memorization; `H1` can. This is also why "just optimise for `H1`" was never available —
tuning anything against it converts every downstream `H1` number into training accuracy and
destroys the only instrument that separates the two hypotheses.

### 2.3 The systems

All are the same frozen base model (**Qwen2.5-Coder-1.5B-Instruct**) plus a LoRA adapter (rank 32,
~0.5 % of model size) unless stated.

| name | what it is |
|---|---|
| `base` | untouched pretrained model, no adapter |
| **`tuned_L0`** | one adapter trained on **clean code only** — **the control for everything** |
| `tuned_<X>` | a *specialist* — one adapter trained on condition `X` alone |
| `mono_all` | one adapter trained on all six trainable conditions at once |
| `loto_hold<X>` | trained on five of six conditions, scored on the held-out sixth |
| `router` | a classifier reads the program and dispatches to the matching specialist |
| `merge_ties`, `merge_dare_ties`, `merge_dare_linear` | the six specialists algebraically **merged into one adapter** |
| `l0merge_*` | the same algorithms applied to **three clean-code adapters** (seeds 17/42/101) — the control asking whether merging does anything at all |
| `crossseed_*` | the six specialists merged, each drawn from a *different* seed |
| `sweep_*_d0p{3,5,7}` | the merges at three densities |
| `residual_*`, `uniform_n8_*` | §5.6's residual-preserving merge and its matched uniform-weight control |
| `mole_uniform / random / router / hardrouter` | **RouterLoRA** — eight specialists kept resident, weighted per token and per layer by a fixed-uniform gate, a randomly-initialised gate, a trained gate, and the trained gate argmaxed to one-hot |
| `mole_*_bal` | the trained gate plus Switch-style load balancing and a temperature floor |
| `s2fam`, `composite_trained`, `composite_ablation` | the three attempted repairs |
| `oracle_prompt_1shot`, `icl_k*`, `norm_*` | zero-training baselines |

**Why `tuned_L0` and not `base` is the control.** The base model is weak at the *task itself*
(6.4 % on `H1`), so against it every adapter looks excellent. Only the gap to a clean-code-trained
adapter isolates what **obfuscation** training buys.

### 2.4 Two grids, never pooled

| | programs | `H1` items | trainable-condition items |
|---|---|---|---|
| **Grid A** (`heldout`, corpus) | 405 on `H1` | **1,214** | 1,247–1,670 |
| **Grid B** (`testset`, ICSE) | 27 on `H1` | **115** | 145–176 |

They are disjoint in programs. `base` scores 6.4 % on `H1` in Grid A and 11.3 % in Grid B. **Every
table below states its grid**, and several defects in this thread came from cells being silently
compared across them (§8.3).

### 2.5 The noise floor — and the correct bar

Two training seeds of the same system, 42 matched Python cells recomputed today:
**mean |Δ| 0.52, median 0.49, p95 0.96, max 2.22 points.** The widely-quoted **1.32 / 3.61** band
is the *Python + JavaScript pooled* figure from `MASTER_REPORT_2026-08-12.md` §8.4; that document
states the Python-only band as 0.63 / 1.46 and gives the correct rule — *"in Python, differences
under ~1.5 points are not differences; in JavaScript the bar is ~4 points"*. **Everything in this
thread is Python.** See §8.2: the pooled band has been applied to Python-only contrasts throughout
the downstream documents and code, inflating the bar by ~2.5×.

A second, smaller floor exists in the evaluation stack itself, and it is **larger than previously
recorded** — see §8.1.

---

## 3. What was built — the full inventory

| family | systems | cells | trials | what it asked |
|---|---|---|---|---|
| density / overtraining sweeps | 71 | 855 | 143,928 | is the merge failure a hyperparameter or a training-length artifact? |
| specialists + `tuned_L0` control | 27 | 395 | 358,186 | do per-condition adapters transfer? (RQ1, the ingredients) |
| zero-training baselines + `base` | 16 | 312 | 156,410 | is any of this better than prompting or a symbolic normalizer? |
| monolithic + LOTO + capacity controls | 11 | 111 | 171,972 | does training on many transforms generalise to an unseen one? |
| weight-space merges (incl. density, residual) | 14 | 109 | 25,218 | can the specialists be merged into one adapter? |
| RouterLoRA mixture | 6 | 76 | 12,478 | does a *learned* per-token mixture beat a fixed one? |
| merge controls (`l0merge`, `crossseed`) | 4 | 30 | 6,988 | does merging do anything? does it care about geometry? |
| attempted repairs | 3 | 21 | 32,388 | can the negative result be repaired from the training side? |
| hard router | 1 | 6 | 1,025 | does perfect dispatch over specialists help? |

Totals: **1,918 cells / 913,600 graded trials** at 1.5B/Python. The **combination arms proper** —
every family above except the specialist bank and the zero-training baselines they are measured
against — are **1,208 cells / 393,997 trials**. Trial counts are dominated by grid: one Grid A cell
is 1,214–1,670 items, one Grid B cell is 115–176.

---

## 4. The headline table

**Grid A, `H1` (n = 1,214 items, 405 programs).** This is the only table that answers the research
question. Contrasts are paired cluster bootstraps by `program_id`, 2,000 resamples, seed 17,
recomputed 2026-08-27.

| system | `H1` % | vs `tuned_L0` | 95 % CI | |
|---|---|---|---|---|
| `tuned_S2_s17` — one specialist | **28.01** | **+3.46** | [+2.06, +4.94] | **beats the control** |
| `s2fam` — repair 1 | 26.61 | +2.06 | [+0.08, +4.13] | marginal |
| `residual_n6_s17_d0p5` — best merge variant | 25.86 | +1.32 | [+0.00, +2.80] | marginal |
| `tuned_S1_s17` | 25.37 | +0.82 | — | |
| `merge_dare_ties_s42` | 24.88 | +0.33 | [−1.07, +1.73] | null |
| **`tuned_L0` — THE CONTROL** | **24.55** | — | — | |
| `merge_dare_ties` — headline merge | 23.89 | **−0.66** | [−1.89, +0.66] | **null** |
| `composite_ablation` | 23.72 | −0.83 | — | |
| `uniform_n8_s17_d0p5` | 23.06 | −1.49 | — | |
| `mono_all` — one adapter, all six conditions | 22.90 | **−1.65** | [−3.79, +0.49] | null |
| `l0merge_dare_ties` — 3× clean-code merge | 21.42 | **−3.13** | [−4.78, −1.40] | **significantly worse** |
| `l0merge_ties` | 21.33 | −3.22 | — | |
| `merge_ties` | 19.52 | **−5.02** | [−7.26, −2.72] | **significantly worse** |
| `composite_trained` — repair 2 | 19.36 | −5.19 | — | |
| `oracle_prompt_1shot` | 15.65 | −8.90 | — | |
| `base` | 6.43 | −18.12 | — | |

**Read it in this order.** Nothing that combines the specialists is above the control. The one
system that is, is a *single specialist*. And the thing that *is* significantly below the control
is the merge control — three adapters trained on identical clean data, merged.

**Grid B, `H1` (n = 115).** Every mixture arm lives only here, so it is reported separately and
must never be compared against the table above.

| system | `H1` % | | system | `H1` % |
|---|---|---|---|---|
| `residual_n6_s42_d0p5` | 41.7 | | `mole_uniform` | 33.0 |
| `merge_dare_ties_s42` | 38.3 | | `mole_random` | 33.0 |
| `uniform_n8_s17_d0p5` | 35.7 | | `sweep_dare_ties_d0p3` — best density | 32.2 |
| `merge_dare_ties` | 34.8 | | `mole_hardrouter` | 32.2 |
| `tuned_L0_k0` — the control | 33.9 | | `crossseed_dare_ties` | 31.3 |
| `l0merge_dare_ties` | 33.9 | | `merge_ties` | 28.7 |
| `mole_router` | 33.9 | | `merge_dare_linear` — defect | 6.1 |

Grid B compresses the whole field into 8 points and **reverses orderings**: `residual_n6_s42` is
top here (41.7) and mid-pack on Grid A (25.6); `l0merge_dare_ties` ties the control here and is
3.1 points below it at power. **115 items over 27 programs cannot support merge comparisons**, and
every `H1` merge number in the older documents is from this grid.

---

## 5. Arm by arm

### 5.1 The hard router — a solved problem that is worth nothing

A classifier reads the program and dispatches to the matching specialist.
**Route accuracy 1.000** on 1,025 held-in items (confusion matrix perfectly diagonal), per-item
entropy ~3×10⁻⁶ nats against a maximum of 2.079.

Grid B, trainable conditions, against the Grid B clean-code control:

| | L0 | L1b | L1r | L2 | S1 | S2 |
|---|---|---|---|---|---|---|
| `router` | 50.0 | 46.0 | 46.6 | 50.6 | 43.4 | 47.2 |
| `tuned_L0` (Grid B) | 49.4 | 36.9 | 46.0 | 50.0 | 43.4 | 48.9 |
| Δ | +0.6 | **+9.1** | +0.6 | +0.6 | 0.0 | −1.7 |

Perfect dispatch buys a real gain on exactly one condition — `L1b`, adversarial renaming — and
nothing anywhere else. **And it was never tested where it matters:** `routing_report.json` records
`n_heldout: 0` for `H1`. There is no `H1` expert, so on the one condition that probes invariance
the router has no correct answer available, by construction. A router over per-transform experts
is *definitionally* incapable of handling an unseen transform; the arm's ceiling is the best
specialist, and §4 shows what that is.

### 5.2 Weight-space merges — and what the merge control proved

Three algorithms, six specialists, Grid A `H1`:

| | `H1` | vs control |
|---|---|---|
| `merge_dare_ties` | 23.89 | −0.66, null |
| `merge_ties` | 19.52 | −5.02, significant |
| `merge_dare_linear` | 6.1 (Grid B) | catastrophic — **a defect, see below** |

**The `merge_dare_linear` catastrophe was a scaling bug, not a result.** Its format-failure rate
was 48.7 % against 6–8 % everywhere else — the diagnostic that distinguished a bug from a
−40-point finding. Repaired as `dl_rescaled`, it recovers to a 45.5 mean over the trainable
conditions (from 4.0), parity with the control. It is deliberately kept in the record as a defect
with its repair.

**The merge control.** Merge three adapters that are *all clean-code-trained* (seeds 17/42/101),
same algorithms, density and rank. Whatever merging does to N adapters, this does to N adapters
with no obfuscation knowledge between them. On Grid A `H1`:

| contrast | Δ | 95 % CI | |
|---|---|---|---|
| 3× clean-code merge − **one** clean-code adapter | **−3.13** | [−4.78, −1.40] | **merging costs ~3.1 pts** |
| 6-specialist merge − 3× clean-code merge | **+2.47** | [+1.32, +3.70] | **specialists are worth ~2.5 pts** |
| 6-specialist merge − one clean-code adapter | −0.66 | [−1.89, +0.66] | net: a wash |

This is the core mechanism of the whole thread. **Two offsetting effects of nearly equal size.**
Merging dilutes by about as much as the specialists contribute. On Grid B, where these were first
read, the two effects could not be separated and the reading was "the specialists contribute
nothing" — which is wrong, and is retired here (§8.3).

**Density was never swept until late, and 0.5 was not optimal.** `dare_ties` scores a
**47.0 / 44.7 / 40.5** mean over the six trainable conditions at density **0.3 / 0.5 / 0.7** —
monotone, and every merge conclusion in the project used 0.5. **But the headroom does not reach
`H1`:** the `d=0.3` merge scores **32.2** on Grid B `H1` against `merge_dare_ties`' 34.8. The
condition it was tuned on improves; the held-out one does not. That read landed 2026-08-17 and
closes what the previous report listed as owed.

**Merging is algorithm-specifically sensitive to geometry.** Rebuilding the merge with each
specialist drawn from a *different* seed (mean cosine 0.563 → 0.246) costs `dare_ties`
**−3.6 pts** over the trainable conditions and `ties` **−0.4**, while both *pure* banks are
equivalent (45.0 at s17 vs 45.6 at s42) — so it is the mixing, not adapter quality. Consequence:
the `l0merge` control is necessarily cross-seed and is therefore **handicapped by ~4 points
against the same-seed arm it controls for**, which makes the +2.47 specialist contribution above
a *conservative* estimate.

### 5.3 Geometry — the diagnostic measures initialization, not knowledge

The project measures task vectors ΔW = (α/r)·B·A and their pairwise cosine and **sign conflict**
(the coordinate fraction where two experts disagree in sign — exactly what TIES deletes). Covering
every bank (CPU only, seconds per bank) gave:

| bank | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
|---|---|---|---|---|
| `L0` at seeds {17, 42, 101} — **byte-identical training data** | **0.053** | **0.487** | 0.765 | 0.374 |
| 8 specialists at seed 17 — **completely different transforms** | **0.592** | 0.390 | 0.861 | 0.371 |
| 6 specialists at seed 42 | 0.575 | 0.388 | 0.845 | 0.370 |
| 6 LOTO folds at seed 17 | 0.576 | 0.382 | 0.849 | 0.804 |

**Three adapters trained on identical data are near-orthogonal; eight adapters trained on
completely different transforms are 0.59-aligned.** LoRA initialises `A` randomly and `B` at zero,
so each seed picks a different rank-32 subspace. Same-seed cosine measures *shared subspace and
common drift*, not shared knowledge.

Two consequences. **Sign conflict does not bound merged accuracy** — the L0-merge bank has the
worst geometry in the project (0.487, a coin flip) and merges fine. And **the LOTO folds are
effectively one vector**: dropping an entire transform from a five-condition mixture moves the
update (cosine 0.565–0.583) *less than the spread between folds*. That is the redundancy result
visible directly in weight space.

Separately, **Horoi et al.'s over-training mechanism reproduces and its consequence does not**: on
the 8-expert bank with epochs held uniform, sign conflict rises 0.401 → 0.425 over nine epochs
while merged accuracy *improves* on 11 of 12 method × condition pairs.

### 5.4 RouterLoRA — the gate was never a router, and fixing it changed nothing

Eight specialists kept resident; a 2.77 M-parameter gate weights them per token and per layer.

**The gate collapsed.** Reading the per-cell gate diagnostic — which the system had been writing
and nobody had read — every condition produced essentially the same fixed blend: ~.38 on the `L2`
expert, ~.21 on `S2`, ~.25 on `S4`, with `L1r`, `S3`, `L0` and `S1` at **.001–.016**. Total-variation
distance between any condition's profile and the grand mean: **.011–.056**. On the `L1r` cell the
`L1r` expert got **.003** — 38× *below* uniform. On `C_L1r_S1`, the two matching experts together
got **.019** against a chance level of .250.

> **A trap worth recording.** `C_L2_S4` showed .605 — apparently strong compositional routing. It
> is an artifact: `L2` and `S4` are the two experts the gate favours on *every* input. Reading the
> strongest-looking row alone would have produced the opposite conclusion.

**Why:** the gate was trained on task loss alone — no load-balancing term, no entropy regulariser,
no routing supervision. A constant blend is the *expected optimum* of that objective. The learned
temperature fell to .39–.51 from an init of 1.0 across all 28 layers: the gate became *more
confident* about a preference that did not depend on its input.

**Was the signal even there?** A linear probe on the decoder-layer input hidden states — exactly
what the gate's hook receives — predicts the condition at **99.4 % (layer 4) against 16.7 %
chance**, above 97 % at every one of 28 layers, split by `program_id`. The condition is almost
perfectly linearly decodable. **The gate could have routed and didn't** — a training failure, not
a representation failure.

**The fix worked, and bought nothing.** Adding Switch-style load balancing (α = 0.01) and a
temperature floor (0.5), same bank, data, prompt and seed:

| | before | after |
|---|---|---|
| TV distance from grand mean | .011–.056 | **.074–.106** |
| `L1r` expert on the `L1r` cell | .003 | .080 |
| `S1` expert on the `S1` cell | .013 | **.253** (its top expert) |
| `C_L1r_S1` on {L1r, S1} — chance .250 | .019 | **.332** |
| normalised entropy | .151–.180 | .270–.289 |
| **accuracy** | — | **+0.4 pts (range −1.1 to +1.7)** |

Routing became real; accuracy did not move. This outcome was written into the experiment's config
**before it ran** as the case to watch for: *if routing improves while accuracy doesn't, the gain
was never about routing.*

**The ladder's controls are weaker than they look.** `mole_random` — a `RouterGate` frozen at
random init — has a mean normalised entropy of **1.000** and per-expert mass uniform to three
decimals. It is not a "random" gate in any behavioural sense; it is a second uniform gate. It
differs from `mole_uniform` on only 3–11 generations per condition and by ≤1.7 accuracy points.
So `mole_router − mole_random` and `mole_router − mole_uniform` measure the same thing, and the
ladder has three rungs but two distinct controls.

The trained gate's remaining edge is real but small and confined to composites: +0.7 to +7.4 over
uniform on the six composite cells (mean +3.2), +0.9 on `H1`. And **`mole_hardrouter`** — the same
gate argmaxed to one-hot, identical weights — reproduces `mole_router` to mean |Δ| 0.88 / max 2.67
points. The system is a *selection* mechanism, not a mixture. (§8.2: that max of 2.67 does **not**
clear the Python noise bar, contrary to how it has been reported.)

### 5.5 Monolithic training and LOTO — breadth does not generalise

**LOTO** (leave-one-transform-out) was built because the project had exactly one OOD condition and
it *is* the test set, so there was no legitimate signal to develop methods against. Train on five
of six conditions, evaluate on the held-out sixth, rotate. Every diagonal cell is an honest
unseen-transform measurement spending no quarantine budget. Grid A:

| fold | held-out condition | accuracy |
|---|---|---|
| `loto_holdL0` | L0 | 41.7 |
| `loto_holdL1b` | L1b | 36.5 |
| `loto_holdL1r` | L1r | 36.6 |
| `loto_holdL2` | L2 | 36.7 |
| `loto_holdS1` | S1 | 37.3 |
| `loto_holdS2` | S2 | 39.3 |
| **mean** | | **38.0** |
| `mono_all` — saw all six | | 39.2 |
| `tuned_L0` — clean code only | | 39.0 |

**Holding a transform out costs ~1.1 points**, and neither multi-condition adapter beats an adapter
that never saw an obfuscated program. (Caveat, §8.4: `train_size: 30000` never bound in the LOTO
configs, so folds ran 22,152–23,373 rows against `mono_all`'s 26,841 — **+21 %**. The comparison is
not size-matched and the true cost of holding a transform out is *smaller* than 1.1 pts, which
strengthens the finding.)

### 5.6 Three attempted repairs, all null

Each was pre-registered with its refutation condition before running.

| repair | idea | result |
|---|---|---|
| **`s2fam`** | train deliberately on the inert-material family (`S2`+`S3`+`S4`) to widen the one transfer that works | **+0.02 pts** [−0.95, +1.02] on the clean-code control over the trainable conditions. Tops the `S2` (43.8) and `S1` (41.4) columns, worst on `L1b` (32.0) — wins where it trained, nowhere else. On `H1` it reaches 26.6, **below** the plain `S2` specialist's 28.0. |
| **`composite_trained`** | train on *stacked* transforms so the model must compose | **−4.37 pts** [−6.34, −2.47] on Grid A `H1` against the matched unstacked ablation, and −1.33 over the trainable conditions. Same six mechanisms, same rows, same recipe — the sign runs *against* the hypothesis. |
| **`residual_*`** | preserve the condition-specific residuals at full magnitude instead of diluting them | The only one with a signal: **+2.80** [+1.07, +4.69] over the matched 8-ingredient uniform merge on Grid A `H1`. But it reaches only **+1.32** [+0.00, +2.80] over the clean-code control, and **+0.74 (null)** against a same-bank s42 replicate in the pre-registered contrast. A ~2-point improvement to *merging* that leaves the invariance question untouched. |

### 5.7 Zero-training baselines — the floor everything must clear

Grid A `H1`: `oracle_prompt_1shot` (the untuned model simply *told* which obfuscation was applied)
**15.65**; `icl_k4_cross` 18.20; `norm_structural` (symbolic normalizer, no model change) 12.93;
`base` 6.43. Every adapter is far above these, and `oracle_prompt` sits ~9 points *below*
`tuned_L0`. At 1.5B, knowing *which* obfuscation you are looking at is worth nothing if you cannot
already do the task.

---

## 6. Why this is a dead end, and not "our method underperformed"

Each explanation for the failure was eliminated by a purpose-built experiment rather than argued
away:

| candidate explanation | eliminated by | the number |
|---|---|---|
| "the merge algorithm is wrong" | three algorithms + a density sweep + a cross-seed control | best merge −0.66 vs control; best density does not transfer to `H1` |
| "merging is the wrong operator; route instead" | perfect hard router | 1.000 dispatch accuracy, gain on 1 of 6 conditions, undefined on `H1` |
| "the gate is badly trained" | balanced gate | routing became real (TV .056 → .106), **accuracy +0.4** |
| "the condition isn't visible to the gate" | linear probe on the gate's own input | **99.4 %** vs 16.7 % chance |
| "training on more transforms would generalise" | LOTO, six folds | holding one out costs ~1.1 pts, inside noise |
| "the experts are over-trained and interfere" | uniform-epoch geometry sweep | mechanism reproduces (sign conflict 0.401 → 0.425), accuracy *improves* on 11/12 pairs |
| "geometry is the constraint" | L0-merge bank | worst geometry in the project (sign conflict 0.487) merges fine |
| "capability exists but isn't extractable" | item-level agreement + permutation null | oracle-of-10 sits **52.9 pts below** the independence null; φ ≈ .62; **61 % of items solved by nothing** |
| "the training side can repair it" | three pre-registered repairs | +0.02, −1.36, +0.74 |

**The item-agreement result is the one that makes this terminal.** On Grid A `H1` across ten
systems: best single 28.0 %, oracle-of-all 39.0 %, raw "headroom" +11.0 pts — which looks like room
for a better combiner. But an oracle-of-*k* rises mechanically with *k*, so the measure is the
distance to a **permutation null that preserves every system's marginal accuracy exactly and
destroys only the item-difficulty coupling**: that null is 91.9 % [90.5, 93.2]. The observed oracle
is **52.9 points below it**. Items are solved by everything or by nothing (740 of 1,214 by nothing;
40 by all ten). The raw headroom is an artifact and must never be quoted without the null.

**The defensible statement, in one sentence:** *combination methods pay a dilution cost about the
size of the specialist contribution they are trying to exploit, and the specialists are redundant
at the item level, so no combination strategy recovers more than the best single member.*

---

## 7. What survives

Three results and two artifacts leave this thread intact.

1. **`S2` → `H1` is a real, replicated positive transfer.** `tuned_S2_s17` beats the clean-code
   control on the held-out obfuscator by **+3.46** [+2.06, +4.94], q < 0.0001, on 1,214 items; the
   s42 replicate is 27.5. It is the only system in the project that beats the control on `H1`, it
   has the most sole-solved items (16), and **every combination method destroys it** — the best
   merge is 4.12 points below it [+2.55, +5.77]. That is the thread's most useful output: it
   located the one thing worth explaining, and the explanation is now being pursued in the
   `attention` and `normalization` threads (dead-code elimination performed in attention).
2. **Two offsetting effects in merging, measured separately.** Merging costs ~3.1 pts; specialists
   contribute ~2.5. Both significant, both on 1,214 items. This is a transferable statement about
   LoRA merging that has nothing to do with obfuscation.
3. **Task-vector geometry is dominated by LoRA initialization.** Adapters trained on *identical*
   data are near-orthogonal (cosine 0.053) while adapters trained on *completely different*
   transforms share a subspace (0.592). Any paper regressing merge quality on geometry must
   stratify by seed or it fits a line through an artifact.

Reusable artifacts: the **CPU-only task-vector diagnostic** (Frobenius inner products from the r×r
factors, `⟨ΔWᵢ,ΔWⱼ⟩ = sᵢsⱼ·tr((BᵢᵀBⱼ)(AⱼAᵢᵀ))`, verified against dense to 5.6e-16 — turns an
intractable 8-expert × 3-epoch × 196-module sweep into seconds), and the **permutation null for
oracle-of-k**, without which every ensemble "headroom" number in this literature is unreadable.

The negative result itself is publishable: `paper_modularity/` holds an FSE draft built on it, and
`CLAIM_LADDER.md` Branch A ("modularity does not rescue robustness") is fully supported by what is
on disk today. **Branches B, C and D are dead** — B needed the composite gate effect to survive at
corpus scale and the mixture ladder's controls turned out to be two copies of the same control
(§5.4); C needed geometry to predict merged accuracy and §5.3 refutes the premise; D needed
under-trained experts to be harder to route and easier to merge, and the uniform-epoch sweep shows
merged accuracy *rising* with training. The draft's empty thesis slot should be filled with
Branch A.

---

## 8. Corrections found on re-checking, 2026-08-27

### 8.1 The evaluation stack is noisier than recorded, on the exact control everything is read against

`tuned_L0` on Grid B `H1` was evaluated three times with the **same adapter path, same prompt
(sha `c1e8fe28…`), same 115 items, same engine (vllm-0.26.0), same sampling (T = 0, top-p 1.0,
max_tokens 64)**:

| cell | date | git commit | GPU | accuracy |
|---|---|---|---|---|
| `pilot/tuned_L0__H1` | 2026-08-05 | `4927d65` | 2 | **40.0** |
| `baselines/tuned_L0_k0__H1` | 2026-08-13 | `469f857` | 1 | **34.8** |
| `main/tuned_L0_k0__H1` | 2026-08-14 | `469f857` | 1 | **33.9** |

The last two are identical in **every** recorded field including commit and GPU, and still differ
on **12 of 115 generations**, flipping 5 graded trials — 0.9 points. Across the commit boundary the
spread is **6.1 points** and 31 of 115 generations differ. Reported items include
`["Hi","my","name","is","John"]` vs a per-character split, and `20` vs `46214` vs `-4` on one item.

**This exceeds the "0.1–0.4 points from batching nondeterminism" recorded in the earlier reports by
2–15×**, and it lands on `tuned_L0` — the reference for every contrast in this thread. Grid A's
n = 1,214 damps it, and the §4 contrasts are paired at the item level so a shifted control does not
move a paired delta. **But every Grid B `H1` comparison in the older documents is within one
re-evaluation of its neighbour**, and the "the merge ties the control at 34.8 vs 33.9" reading that
opened this thread is inside that band. The Grid A panel is what makes the verdict hold; the Grid B
readings never should have been load-bearing.

Action owed: a determinism note in `CLAUDE.md` §Correctness, and `h1_access_purpose` audit —
`pilot_eval` and two `final_eval` passes on the same quarantined items is more `H1` exposure than
the sanctioned two.

### 8.2 The pooled seed band has been applied to Python-only contrasts

`MASTER_REPORT_2026-08-12.md` §8.4 reports the seed noise floor three ways: **Python 0.63 mean /
1.46 p95**, **JavaScript 2.01 / 4.03**, **pooled 1.32 / 3.61** — and states the correct rule
explicitly. Downstream, the **pooled** figure is what propagated: it appears as the operative
threshold in `REPORT_2026-08-15_modularity_verdict.md`, `REPORT_2026-08-17_…`, four log entries,
and in the docstrings of `scripts/merge/24_crossseed_control.py`, `scripts/merge/25_residual_merge.py`
and `scripts/attn/30_knockout.py`. **Every experiment in this thread is Python**, so the bar has
been set ~2.5× too permissive throughout.

My recomputation over 42 matched Python s17/s42 pairs today: **mean 0.52, median 0.49, p95 0.96,
max 2.22.**

What this changes: **one secondary claim, not the verdict.** "`mole_hardrouter` reproduces
`mole_router` to max 2.7, every cell inside the 3.61-pt band" is the claim that "mixture" is the
wrong word for the system. At the Python bar of ~1.5 the max |Δ| of **2.67** (on `C_L1b_S1`) does
*not* clear it, and neither does 1.7 on `H1` or on `C_L2_S4`. The claim should be restated as
*"11 of 15 cells inside the Python noise bar, mean |Δ| 0.88, signed both ways"* — still a strong
argument for selection over blending, but not the blanket equivalence it was written as. Nothing in
§4 or §6 depends on the band: those contrasts carry bootstrap CIs.

### 8.3 "The per-condition experts carry nothing distinct" is retired

That sentence is the conclusion of `MASTER_REPORT_2026-08-12.md` §12.10 and the headline of the
08-15 verdict. It rested on a Grid B gating claim — *"merging three clean-code adapters reaches the
same `H1` accuracy as merging six specialists"*, 33.9 vs 34.8, a 0.9-point gap read as a tie. At
n = 1,214 that gap is **+2.47 [+1.32, +3.70]**, highly significant. The specialists *do* contribute.
The 08-17 report already retired the sentence; it is restated here because the 08-12 master report
still carries it and is still the document people index into. The correct statement is §6's last
line.

### 8.4 Four smaller items, carried forward

- **`train_size: 30000` never bound in the LOTO configs** — folds ran 22,152–23,373 rows,
  `mono_all` 26,841 (+21 %). "LOTO 38.0 vs `mono_all` 39.2" is not like-for-like. Direction is
  favourable to the conclusion. **Correction owed in its own commit.**
- **`build_manifest.py --eval` silently drops any system whose `arch` starts with `merge`.** A
  config mixing merge and non-merge systems queues some and drops the rest without saying so.
  Documented, not fixed; `--rq2` is not the workaround (it *rebuilds* the merges and would
  overwrite `runs/adapters/.../merge_*`).
- **No orphan recovery while `pipeline.sh` is not running** — `--requeue-stale` is only invoked by
  `supervise.sh`, so a worker that dies mid-run leaves its claim in `running/` forever.
- **Training loss unobservable for the first ~hour** — `worker.py` launches jobs with `stdout`
  block-buffered to file and no `PYTHONUNBUFFERED`; first loss lines appear, clumped, at step 200.

Both of the last two are one-line fixes.

---

## 9. What would have to be true to reopen the thread

Ranked by what each would actually settle. None is recommended over the `attention` /
`normalization` threads now pursuing §7.1.

1. **A second held-out family.** `H1` is one obfuscator, it is partly burned (§8.1), and every
   invariance claim in this thread rests on it. A virtualization-based `H2` and a control-flow `H3`
   would test the claim far harder; stacking existing generators (`H1∘S1`) is the cheap version.
   **This is the only item that could overturn the verdict rather than qualify it** — if `S2`'s
   transfer generalises to an inert-material `H2` but not to a rearranging `H3`, the whole framing
   changes from "combination fails" to "there is one real skill and it is narrow".
2. **7B.** Everything here is 1.5B and single-seed. Five of seven obfuscation penalties largely
   dissolve at 7B (base spread 18.2–29.0 at 1.5B vs 49.4–58.0 at 7B, where `L2` scores *above*
   clean code). Only `L1b` (−8.0), `S1` (−7.1) and `H1` (−20.9) survive — and `H1` is the only
   penalty that does not shrink with scale, which strengthens every `H1` conclusion here. Whether
   combination fails the same way at 7B is unrun.
3. **Supervised routing** — training the gate with the correct expert as an explicit target. It is
   the strongest remaining fix for compositional decomposition, and it was *deliberately* not run:
   a gate *taught* to decompose is a weaker result than one that learned to. Given §5.4's +0.4, it
   would most likely improve routing and not accuracy again.
4. **The invariance-loss arm** — the only attempted repair that optimizes invariance as an
   *objective* rather than through the data. Designed, never built; needs `invariance` added to
   `schema.TrialRow.adapter_arch` first or it fails at the first row written.
5. **Second seeds for the mixture arms.** Every `mole_*` number is n = 1. The specialists have s42
   banks already; the gate does not.

---

## 10. Provenance and reproduction

**Cells.** `results/cells/{main,final,baselines,baselines_gridA,pilot}/qwen25c-1.5b/python/`.
Grid is identified by item count, never by directory: `H1` at n = 1,214 is Grid A, at n = 115 is
Grid B.

**Analysis inputs.** `results/analysis/{gate_routing,gate_input_probe,item_agreement_gridA_H1,
item_agreement_main_qwen25c-1.5b_python_H1}.json`,
`results/merge_geometry/{adapters,adapters_s42,adapters_overtrain,l0seeds,loto}_qwen25c-1.5b_python.json`,
`results/router/qwen25c-1.5b/python/routing_report.json`.

**Statistics.** Paired cluster bootstrap by `program_id`, 2,000 resamples, seed 17; exact McNemar
on discordant pairs; BH-FDR across each contrast family; permutation null preserving marginals for
every oracle-of-k. Grading is execution-verified strict normalized exact match.

**Everything in §4, §5 and §8 was recomputed on 2026-08-27** directly from the per-cell parquets
with `/data/jvl210002/conda_envs/obtune/bin/python`, not read from any earlier report. The four
published contrasts that could be checked against the 08-17 report reproduce to ≤0.02 pts
(−0.66/−0.66, −3.13/−3.13, +2.47/+2.47, +3.46/+3.46).

**Lab notes**, in order: [`../log/modularity/`](../log/modularity/) entries of 08-10, 08-11 (×2),
08-13 (×2), 08-14 (×2), 08-15, 08-17, plus [`../log/setup/2026-08-14_pipeline-hardening.md`](../log/setup/2026-08-14_pipeline-hardening.md).
Thread index: [`../log/modularity/README.md`](../log/modularity/README.md). Manuscript:
[`../paper_modularity/`](../paper_modularity/).

**Cost.** ~17.5 unattended GPU-hours over 42 pipeline stages / 224 jobs for the 13–15 August chain,
plus 11.0 GPU-h for the 15–17 August chain, on two GPUs of a shared four-GPU host. Seven
infrastructure defects were found and fixed during the first chain and four during the second;
**seven of the eleven shared one signature — a failure that leaves the pipeline reporting
success.**

## Changelog

- **2026-08-27** — Created. Closing master report for the RQ2 routing-and-merging thread,
  superseding `MASTER_REPORT_2026-08-12.md` §5/§12.10 and consolidating the 08-15 and 08-17 chain
  reports. All numbers recomputed from cells. Three new corrections recorded: the evaluation-stack
  determinism spread on the `H1` control (§8.1), the pooled-vs-Python seed band (§8.2), and the
  `d=0.3` merge density's failure to transfer to `H1` (§5.2).
