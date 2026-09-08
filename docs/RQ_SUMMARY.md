# Research questions, approaches, and answers — one page

*Last updated: 2026-09-07*

A compressed index of everything the project has asked and what came back. Full numbers and
provenance are in [`../MASTER_REPORT.md`](../MASTER_REPORT.md); the forward plan is in
[`PAPER_EXPERIMENTS.md`](PAPER_EXPERIMENTS.md). Deltas are percentage points, intervals are
program-clustered bootstraps (2,000 resamples). **Every evaluation is on code that stays
obfuscated** — this project never trains or evaluates on deobfuscation.

Two panels, never pooled: **Qwen2.5-Coder-1.5B** (frozen, §1–§17 of the report) and
**CodeLlama-7b/13b/34b + Llama-3.1-8B** (current, §18–§28). A table says which.

---

## 1. Approaches tried

| # | approach | what it varied | outcome |
|---|---|---|---|
| 1 | **Per-condition LoRA specialists** | one adapter per obfuscation type | works on its own type, transfers within the ladder at 7B+ |
| 2 | **Monolithic breadth (`mono_all`)** | one adapter on all six types | ties on the ladder, **loses** on an unseen transform, **wins** on stacked ones (§4) |
| 3 | **Learned router + per-type experts** | dispatch to specialists | worth **exactly zero** over a random gate |
| 4 | **Task-vector merging** (TIES / DARE-TIES / DARE-linear, 3 densities, 2 seed banks) | weight-space combination | at or below the clean-code control |
| 5 | **MoLE mixtures** (uniform / random / router / hard-router) | mixture of 8 experts | mixing is worth +0.205; *how* you mix is worth 0 |
| 6 | **Oracle prompt conditioning** | telling the model the obfuscation type | ~9 pts *worse* than the clean-code adapter |
| 7 | **Leave-one-transform-out** | holding one type out of training | indistinguishable from training on all six |
| 8 | **Rank / capacity sweep** (r = 32…192) | adapter capacity | capacity is not the bottleneck |
| 9 | **Self-consistency voting** | inference-time sampling | +2.11 for `base`, **−0.99** for a tuned model |
| 10 | **Transform augmentation** | 4 surfaces per program | +0.17 [−1.14, +1.38] |
| 11 | **Data scale** (+58 % programs; 3× input cases) | more data | +0.73 / +0.31, inside the seed band |
| 12 | **Execution-trace SFT** | emit a trace before the answer | null, and unreadable on `S1` (74 % format-fail) |
| 13 | **Best-of-*n* rerank** (vote / logprob / self-judge / trained verifier) | selection | ceiling +17.74, no selector above +1.09 |
| 14 | **Weight-space alignment** | hidden states → clean code | matched − mismatched +0.18 [−0.82, +1.16] |
| 15 | **Semantic negatives + unlikelihood** | verified mutants | **−2.72**, refuted in the wrong direction |
| 16 | **Curriculum** (clean → obfuscated) | training order | order is worth 0; the KL term is worth ~1.3 |
| 17 | **Paired consistency (O1)** | CE + λ·KL to a clean-code teacher on the L0 parent | **the one algorithmic lever that works** |
| 18 | **Model scale** (1.5B → 7B → 13B → 34B) | capacity | **+8.56** 34B vs 7B, entirely through tuning |
| 19 | **Family exposure** (X1, sibling of the held-out obfuscator) | training on the *family*, not the transform | 7B with family exposure ties 34B without |
| 20 | **Symbolic normalization** | zero-training canonicalisation | a second instrument on the same mechanism |

---

## 2. The chartered RQs, and their answers

### RQ1 — Does tuning transfer? (generalization)

| question | answer | key number | panel |
|---|---|---|---|
| Does a specialist help on its own condition? | yes | +3 to +8 over the clean-code control | both |
| Does it transfer *within* the trained ladder? | **yes at 7B+, no at 1.5B** | mean off-diagonal TR **0.9057** [0.8784, 0.9322] (7B) vs ~0.07 (1.5B) | both |
| Does holding a transform out of training cost anything? | **no** | LOTO recovers **0.9452** [0.8940, 1.0058] of `mono_all` | CodeLlama |
| Does breadth help on an **unseen** obfuscator? | **no — it hurts** | `tuned_L0 − mono_all` **+4.12** [+1.81, +6.75] on H1 at 7B; **+2.47** [+0.41, +4.78] at 34B | CodeLlama |
| Does that survive scale and seeds? | **yes** | on X1: +3.79 / +4.28 / +2.64 at 7B/13B/34B; +3.79 / +3.54 / +3.54 at three seeds | CodeLlama |
| So is it invariance or memorization? | **neither, exactly — it is the *family*** | a 7B adapter trained on X1 (H1's family, different surface) **ties a 34B clean-code adapter** on H1: −0.33 [−2.88, +2.06] | CodeLlama |

### RQ2 — Does modularity rescue it?

| question | answer | key number |
|---|---|---|
| Learned router vs random gate? | **exactly zero** | +0.0000 [−0.0081, +0.0081] |
| Is the *mixture* worth anything? | yes, but not the routing | +0.2047 [+0.1788, +0.2298] |
| Do merges retain per-type gains? | no | merging costs −3.13 [−4.78, −1.40] while specialists contribute +2.47 [+1.32, +3.70] |
| Is there hidden complementary capability? | **no** | oracle over 10 systems sits **52.9 pts below** a marginal-preserving permutation null |
| Does oracle *prompting* substitute for tuning? | no | ~9 pts worse than the clean-code adapter |

**RQ2 is closed, negatively, by elimination rather than assumption.**

### RQ3 — Mechanism (attention)

| question | answer | status |
|---|---|---|
| Does anchoring shift predict which transfers succeed? | yes, correlationally | §15.1 |
| Is it causal? | knockout intervention reproduces on a second model family | §15.3 |
| Training-free version? | symbolic normalization moves the same quantity | §16.5 |
| Generate-mode confirmation, length-matched control | **not run** | open |

### Secondary — human alignment

**Never started.** `data/human/paper2_graded.csv` (98 item-level cells) and `paper3_graded.csv` are
on disk; no result exists. Run it or cut it from the framing.

---

## 3. What actually works, per condition

83 CodeLlama-7b systems, Grid A, items intersected per column. In every column the top six sit
inside each other's intervals, so the informative column is the last one.

| condition | leader | acc | beats the clean-code control? |
|---|---|---:|---|
| `L0` | `mole_random` | 0.4329 | **nothing does** |
| `L1b` | `cons_lam3` | 0.4047 | all top six, +3.92…+4.22 |
| `L1r` | `mono_cases` | 0.3994 | all top six, +1.92…+2.46 |
| `L2` | `mono_cases` | 0.4006 | two arms, +1.92 / +2.04 |
| `S1` | `cons_lam3_s42` | 0.4018 | one arm, +2.33 |
| `S2` | `cons_lam3_s42` | 0.4229 | all top six, +3.00…+3.36 |
| `X1` (held-out family) | `x1_resample` | 0.3237 | family arms, +3.95…+5.35 |
| `H1` (held out, spent) | `tuned_X1` | 0.3180 | family arms only |

---

## 4. Combined (stacked) obfuscation — an RQ the ladder was designed to exclude

The condition ladder is **single-transform from the L0 parent, never stacked**, so that transfer is
attributable to one mechanism. But six **composite** conditions were built and evaluated on the
Qwen panel (`configs/conditions_composite.yaml`): two transforms applied in sequence, including
one order-reversed pair (`C_L1r_S1` vs `C_S1_L1r`).

**⚠️ Panel warning: every number in this section is Qwen2.5-Coder-1.5B.** Composites were never
re-run on CodeLlama, so this is the one RQ whose answer rests entirely on the frozen panel.

### 4.1 Accuracy on stacked conditions

| system | `C_L1b_S1` | `C_L1r_S1` | `C_S1_L1r` | `C_L2_S4` | `C_L1r_S3` | `C_S4_S3` | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| `base` | 0.3133 | 0.2667 | 0.2533 | 0.2159 | 0.1761 | 0.2045 | 0.2383 |
| `tuned_L0` | 0.2474 | 0.2706 | 0.2450 | 0.3431 | 0.3455 | 0.4235 | 0.3125 |
| `mono_all` | 0.3216 | 0.3336 | 0.3256 | 0.3725 | 0.3683 | 0.4133 | 0.3558 |
| `tuned_L1r` | 0.3600 | 0.3467 | 0.3600 | 0.4432 | 0.4205 | 0.4261 | 0.3927 |
| `tuned_S2` | 0.3333 | 0.3600 | 0.3933 | 0.4886 | 0.4489 | 0.4886 | 0.4188 |
| `tuned_L2` | 0.3600 | 0.4067 | 0.4067 | 0.4659 | 0.4545 | 0.4716 | 0.4276 |
| `merge_dare_ties` | 0.4067 | 0.4000 | 0.4400 | 0.4432 | 0.4318 | 0.4659 | 0.4313 |
| **`tuned_L1b`** | 0.4333 | 0.4000 | 0.4267 | 0.4830 | 0.4489 | 0.4659 | **0.4430** |
| **`mole_router`** | 0.4200 | 0.4067 | 0.4200 | 0.5398 | 0.4602 | 0.4773 | **0.4540** |

### 4.2 The headline: breadth **wins** on stacked transforms and **loses** on unseen ones

`mono_all − tuned_L0`, the exact contrast that is *negative* on the held-out obfuscator:

| condition | Δ pts [95 % CI] |
|---|---:|
| `C_S1_L1r` | **+8.06 [+5.66, +10.53]** |
| `C_L1b_S1` | **+7.42 [+4.94, +9.81]** |
| `C_L1r_S1` | **+6.30 [+3.99, +8.85]** |
| `C_L2_S4` | **+2.94 [+0.90, +5.10]** |
| `C_L1r_S3` | **+2.28 [+0.30, +4.37]** |
| `C_S4_S3` | −1.02 [−3.00, +0.90] |
| **pooled** | **+3.91 [+2.45, +5.28]** |
| *for contrast:* **H1 (unseen)** | **−4.12** — i.e. `tuned_L0` wins by +4.12 [+1.81, +6.75] |

**This is a clean dissociation, and it sharpens the whole project's claim.** Breadth training is
not simply bad. It buys robustness to *recombination of transforms it has seen* — worth up to 8
points — and pays for it with robustness to *transforms it has not seen*. Five of six composites
favour breadth with intervals clearing zero; the sixth (`C_S4_S3`, two structural transforms of
the same family) is null.

### 4.3 What stacking costs

Composite accuracy against the same system's accuracy on the composite's own constituent
transforms, restricted to the programs the composite gated:

| system | on composites | on its parts (same programs) | stacking cost |
|---|---:|---:|---:|
| `tuned_L0` | 0.3125 | 0.3948 | **−8.23** |
| `tuned_S2` | 0.4188 | 0.4855 | −6.67 |
| `mono_all` | 0.3558 | 0.3920 | **−3.62** |

Stacking is not free for anyone, but **breadth halves the cost**. Same dissociation, seen from
the other side.

### 4.4 Order effects

`C_L1r_S1` vs `C_S1_L1r` are the same two transforms in opposite order and differ by up to 3.6
points per system (`mole_router` 0.4067 vs 0.4200; `tuned_S1` 0.3400 vs 0.4133), with no
consistent direction across systems. Applying a renamer before or after a flattener is not the
same problem, which is worth stating because a "composition is compositional" assumption is
tempting and wrong here.

---

## 5. Proposed new RQs

Ordered by what they would buy a paper.

### RQ-A — Is the seen/unseen dissociation real on the current panel?
§4 is the strongest new result in this document **and it is Qwen-only**. Re-run the six composites
on CodeLlama-7b for `base`, `tuned_L0`, `mono_all`, `cons_lam3` and one specialist.
*Eval-only if the composite items are rebuilt; ~2 GPU-h.* **Confirm** if
`mono_all − tuned_L0` pooled on composites excludes zero *above* while the H1/X1 contrast stays
negative — one model, one grid, opposite signs.

### RQ-B — Does the consistency objective inherit breadth's stacking robustness?
`cons_lam3` keeps breadth's trained-condition gain without its held-out tax. If it *also* keeps
breadth's +3.91 on stacked transforms, it dominates `mono_all` outright and becomes the paper's
recommended recipe rather than one arm among many. *Same job as RQ-A.*

### RQ-C — How many transforms deep does it go?
All composites are depth 2. Build depth 3 and 4 and measure the decay curve per system. The
interesting shape is whether breadth's advantage *grows* with depth (it is a recombination story)
or saturates (it is a two-transform artefact). *Generator work + ~3 GPU-h.*

### RQ-D — Does order-sensitivity predict anything?
§4.4 shows order matters by up to 3.6 pts with no consistent direction. Is the asymmetry
predictable from the transforms' interaction — e.g. does a renamer applied *after* a flattener
destroy the dispatch-variable names the model was using? This connects directly to RQ3's
attention account and is testable with the existing knockout apparatus. *Analysis + ~2 GPU-h.*

### RQ-E — Is "family" the right grain, and how hard must a family be?
The family result rests on one pair (X1/H1). A second pair returned null because the family was
too gentle — it damaged a clean-code adapter by 3.8 pts against X1's 15.8. The redo needs a family
that costs ≳10 points, with power estimated from the held-out sibling *before* training.
*Generator + ~1.5 GPU-h.*

### RQ-F — Does the clean-code teacher have to be a *tuned* model?
Nothing has yet varied the teacher in the consistency objective — only its view (parent vs same
input) and the student's init. If an untuned `base` teacher works as well, the method is far more
portable; if only `tuned_L0` works, the claim must say so. *~9 GPU-h.*

### RQ-G — What is the `L0` cost made of?
Every breadth adapter pays ~1.7–2.6 pts on clean code and the cause is unlocated. Testable on
**existing cells**: does it concentrate on unusual answer formats, on long programs, or on
specific answer types? *No new compute.*

---

## Changelog
- **2026-09-07** — Created. §4 is new analysis, not a restatement: the composite cells existed on
  the Qwen panel and had never been read as a group, and the `mono_all − tuned_L0` sign flip
  between stacked and unseen conditions had not been noticed anywhere in the project.
