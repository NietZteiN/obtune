# Research questions, approaches, and answers — one page

*Last updated: 2026-09-08*

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

**Panel note:** §4.1–§4.4 are Qwen2.5-Coder-1.5B (the frozen panel). **§4.5 is the CodeLlama-7b
replication (job 382427, 2026-09-07, pre-registered as RQ-A/RQ-B)** — the headline dissociation and
the consistency-objective result both replicate, so this RQ no longer rests on one panel.

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

### 4.5 CodeLlama-7b replication — RQ-A and RQ-B, both CONFIRMED (2026-09-07)

Pre-registered before submission (`47ae9af`, rules verbatim in `CLAUDE_SCRATCHPAD.md`); 1,667 items
per cell; program-clustered bootstrap. Source: `results/analysis/composites_codellama7b_2026-09-07.json`,
entry `log/transfer/2026-09-07_composites-on-codellama.md`.

| system | `C_L1b_S1` | `C_L1r_S1` | `C_S1_L1r` | `C_L2_S4` | `C_L1r_S3` | `C_S4_S3` | pooled |
|---|---:|---:|---:|---:|---:|---:|---:|
| `base` | 0.1413 | 0.1309 | 0.1349 | 0.1758 | 0.1719 | 0.1860 | 0.1598 |
| `tuned_L0` | 0.2785 | 0.2937 | 0.2849 | 0.3551 | 0.3599 | 0.3923 | 0.3333 |
| `tuned_S2` | 0.2857 | 0.3033 | 0.3009 | 0.3701 | 0.3766 | 0.4199 | 0.3493 |
| `mono_all` | 0.3448 | 0.3496 | 0.3264 | 0.3851 | 0.3796 | 0.4031 | 0.3683 |
| **`cons_lam3`** | **0.3599** | **0.3559** | **0.3488** | **0.3923** | **0.3868** | **0.4223** | **0.3809** |

| contrast (pooled, pts) | CodeLlama-7b | Qwen-1.5B | verdict |
|---|---:|---:|---|
| `mono_all − tuned_L0` on **stacked-seen** | **+3.49 [+2.04, +5.01]** | +3.91 [+2.58, +5.27] | **RQ-A CONFIRMED** — all six composites positive on CodeLlama |
| `mono_all − tuned_L0` on **unseen** (X1 / H1) | **−3.79 [−6.09, −1.65]** | −4.12 | the other half of the dissociation |
| `cons_lam3 − tuned_L0` on stacked-seen | **+4.76 [+3.53, +6.05]** | — | **RQ-B CONFIRMED** (first conjunct) |
| `cons_lam3 − mono_all` on stacked-seen | +1.27 [−0.02, +2.59] | — | RQ-B second conjunct holds (not below); strict ">" grazes zero → 13B/34B |
| `tuned_S2 − tuned_L0` on stacked-seen | +1.60 [+0.72, +2.45] | — | the structural specialist helps where its family is stacked |

Two things the replication adds. First, the per-composite breadth gain is ordered by how much of
the stack is an *identifier* transform: +6.6/+5.6 (identifier+S1) down to +1.1 (S4+S3, structural
only; −1.0 on Qwen). Breadth helps stacked conditions mostly through the identifier transforms it
has seen — what a family account predicts (H-stack-identifier, open). Second, the order pair:
identifier-first (`C_L1r_S1`) is easier in 7 of 9 model×system comparisons, by ≤2.6 pts, so §4.4's
"no consistent direction" was a Qwen-only, across-systems read; the effect is small and mostly
consistent.

---

## 5. Proposed new RQs

Ordered by what they would buy a paper. **Status 2026-09-07:** RQ-A and RQ-B are answered (§4.5);
the rest were folded into the revised spine in §6 and are now stages of the autonomous pipeline
(`scripts/pipeline/plan.yaml`) — the mapping is given at the end of each item.

### ~~RQ-A — Is the seen/unseen dissociation real on the current panel?~~ — **CONFIRMED (§4.5)**; scale leg → RQ1′
§4 is the strongest new result in this document **and it is Qwen-only**. Re-run the six composites
on CodeLlama-7b for `base`, `tuned_L0`, `mono_all`, `cons_lam3` and one specialist.
*Eval-only if the composite items are rebuilt; ~2 GPU-h.* **Confirm** if
`mono_all − tuned_L0` pooled on composites excludes zero *above* while the H1/X1 contrast stays
negative — one model, one grid, opposite signs.

### ~~RQ-B — Does the consistency objective inherit breadth's stacking robustness?~~ — **CONFIRMED (§4.5)**; scale leg → RQ3′
`cons_lam3` keeps breadth's trained-condition gain without its held-out tax. If it *also* keeps
breadth's +3.91 on stacked transforms, it dominates `mono_all` outright and becomes the paper's
recommended recipe rather than one arm among many. *Same job as RQ-A.*

### RQ-C — How many transforms deep does it go?
All composites are depth 2. Build depth 3 and 4 and measure the decay curve per system. The
interesting shape is whether breadth's advantage *grows* with depth (it is a recombination story)
or saturates (it is a two-transform artefact). *Generator work + ~3 GPU-h.* → **RQ1′**, stages `bld_depth`/`ev_depth`/`an_depth`.

### RQ-D — Does order-sensitivity predict anything?
§4.4 shows order matters by up to 3.6 pts with no consistent direction. Is the asymmetry
predictable from the transforms' interaction — e.g. does a renamer applied *after* a flattener
destroy the dispatch-variable names the model was using? This connects directly to RQ3's
attention account and is testable with the existing knockout apparatus. *Analysis + ~2 GPU-h.* → deferred; §4.5 found the order effect small and mostly consistent (identifier-first easier in 7/9), so it is reported, not pursued.

### RQ-E — Is "family" the right grain, and how hard must a family be?
The family result rests on one pair (X1/H1). A second pair returned null because the family was
too gentle — it damaged a clean-code adapter by 3.8 pts against X1's 15.8. The redo needs a family
that costs ≳10 points, with power estimated from the held-out sibling *before* training.
*Generator + ~1.5 GPU-h.* → **RQ2′**: the grain question runs now as the X1m/X1s split (`an_x1split`); the hard-family redo (E5b) is a disabled stage until its generator exists.

### RQ-F — Does the clean-code teacher have to be a *tuned* model?
Nothing has yet varied the teacher in the consistency objective — only its view (parent vs same
input) and the student's init. If an untuned `base` teacher works as well, the method is far more
portable; if only `tuned_L0` works, the claim must say so. *~9 GPU-h.* → **RQ3′**, stages `tr_cons_tbase`/`tr_cons_tmono`/`ev_teacher`/`an_e4`.

### RQ-G — What is the `L0` cost made of?
Every breadth adapter pays ~1.7–2.6 pts on clean code and the cause is unlocated. Testable on
**existing cells**: does it concentrate on unusual answer formats, on long programs, or on
specific answer types? *No new compute.* → **RQ1′/RQ4′ support**, stages `an_l0cost` (every arm's L0 cell vs `tuned_L0`, TOST ±1.0) and the saturation arms (`an_saturation`: is the tax a data-volume effect?).

---

## 6. The revised research questions (adopted 2026-09-07)

The chartered RQs (§2) no longer describe what the project found. RQ1 as chartered is a false
binary — *invariance or memorization?* — and the answer is neither: transfer is near-complete
inside the trained ladder (TR 0.906 at 7B+), fails on an unseen family, and is recovered by training
on a *sibling* of that family. RQ2 is finished (router = random gate, merges at or below control)
and is a section, not a question. RQ3 is real but partial and reads better as support. Human
alignment has data on disk and zero results. The paper is therefore written to four revised
questions; each names the evidence that carries it and the pipeline stages that complete it.
Decision rules for every new stage are frozen in `CLAUDE_SCRATCHPAD.md` (2026-09-07, "REVISED RQs")
before submission; **no stage reads H1** (budget spent), the held-out family is X1 throughout.

| | question | what carries it now | what the pipeline adds |
|---|---|---|---|
| **RQ1′** | What does breadth training actually **buy and cost**? | stacked-seen: `mono_all − tuned_L0` **+3.49** [+2.04, +5.01] on six depth-2 composites (7B; Qwen +3.91). Unseen: **−3.79** [−6.09, −1.65] on X1, −4.12 on H1; at 34B `tuned_L0` still wins H1 by +2.47. L0: breadth pays ~1.7–2.6 pts. | the same composite grid at 13B and 34B (`an_composite_*`); depth-3/4 composites — does the gain persist or grow (`an_depth`, RQ-C); half/quarter-data arms — is the unseen tax a data-volume effect (`an_saturation`); every arm's L0 cost classified (`an_l0cost`). |
| **RQ2′** | What is the **unit** of transfer? | family, not transform and not "invariance": X1→H1 transfer is lossless (0.08 pts); `tuned_X1` at 7B ties `tuned_L0` at 34B (−0.33 [−2.88, +2.06]); the gentle second family (X2/Y2) was underpowered by construction. | X1 split into its MBA half (X1m) and string-encoding half (X1s), each trained alone: does each half transfer to the other (`an_x1split`, H-family-unit) and does either half carry the whole (H-whole-ge-parts). E5b (a hard second family) waits on a generator. |
| **RQ3′** | Can an objective get **both sides** of the trade? | paired consistency (`cons_lam3`, parent view, tuned_L0 teacher): +4.59 over `mono_all` on X1 with no L0 tax (−0.30 [−1.80, +1.32]), and +4.76 over `tuned_L0` on stacked-seen, not below `mono_all` there (+1.27 [−0.02, +2.59]). | survives scale? 13B/34B (`an_e3`, H-E3); which ingredient — the parent view, the tuned teacher, or a breadth teacher (`an_e4`); replicates on Llama-3.1-8B (`an_e8`). |
| **RQ4′** | **Why?** *(support, not a co-equal claim)* | RQ3's attention re-anchoring on seen conditions; modularity's failure (no complementary capability for a router or merge to find) as evidence about the representation. | identifier-knockout signature on X1 across five arms — does `cons_lam3` depend less on identifier keys than `mono_all`, and does breadth make the model *more* identifier-dependent on the unseen family (`an_attention`); BH-FDR over the transfer and arms families (`an_fdr`, reported). Human alignment (E10) is disabled, not pretended. |

### 6.1 RQ1′ — what breadth buys and costs: the results so far

`mono_all − tuned_L0` (six-condition breadth vs clean-code-only, same base, same rows per program),
pts [95 % CI], program-clustered bootstrap. Positive = breadth helps. CodeLlama unless marked.

| column | 7B | 13B | 34B | other |
|---|---:|---:|---:|---:|
| **stacked-seen, depth 2** (6 composites, pooled) | **+3.49** [+2.04, +5.01] | **+2.90** [+1.45, +4.37] | *pending (382516)* | Qwen-1.5B **+3.91** [+2.58, +5.27] |
| **stacked-seen, depth 3/4** (4 composites, 394-program common subset) | **+4.15** [+2.37, +5.91] | — | — | — |
| **unseen family X1** | **−3.79** [−6.09, −1.65] | **−4.28** [−6.50, −2.06] | **−2.64** [−5.10, −0.25] | seeds s42/s101: −3.54 / −3.54 |
| **unseen family H1** (budget spent; final read) | −4.12 [−6.75, −1.81] | — | **−2.47** [−4.78, −0.41] | — |
| **clean code L0** (the cost) | −1.74 | −2.34 | **−2.63** [−4.49, −0.78] | Llama-3.1-8B **−2.22** [−4.13, −0.24] |
| seen single transform L1b (the gain, for reference) | +2.41 | +2.71 | **+5.19** [+3.02, +7.36] | Llama-3.1-8B +2.83 [+0.90, +4.76] |

Reading: one pair of adapters, opposite signs on the two axes at every scale read — breadth buys
recombination of what it saw and pays on what it did not, plus a clean-code tax that grows with
scale. The stacked gain does not decay with depth (RQ-C-persists CONFIRMED; RQ-C-grows
INCONCLUSIVE — the point rises, the interval straddles). Still to land: the 34B composite column
(`an_composite_34b`), whether the unseen tax is a data-volume effect (`an_saturation`, H-tax-scales),
and every arm's L0 cost classified (`an_l0cost`).

### 6.2 RQ2′ — the unit of transfer: the results so far

| test | contrast | Δ pts [95 % CI] | verdict |
|---|---|---:|---|
| a sibling family transfers to the held-out family | `tuned_X1 − tuned_S2` on **H1** (vs the best transform-trained 7B arm) | **+3.46** [+1.32, +5.51] | H-X1-family CONFIRMED |
| …and adding it to breadth rescues breadth | `mono_allX − mono_all` on **H1** | **+7.66** [+5.35, +10.04] | H-mono-X CONFIRMED |
| X1→H1 transfer is lossless | `tuned_X1`: X1 0.3188 → H1 0.3180; `mono_allX`: 0.3097 → 0.3089 | 0.08 / 0.08 pts | X1 and H1 are one problem to the model (learned from the final read; not assumed for new families) |
| family exposure vs scale | `tuned_X1` (7B) − `tuned_L0` (34B) on **H1** | −0.33 [−2.88, +2.06] | indistinguishable: a 7B adapter with the family ≈ a 34B adapter without |
| the X1 diagonal | `tuned_X1 − tuned_L0` on **X1** | **+4.86** [+2.80, +6.92] | survives BH-FDR (q = 0.009, `an_fdr`) |
| a *gentle* second family (X2 → Y2) | `tuned_X2 − tuned_L0` on **Y2** | +1.21 [−0.81, +3.22] | H-family-generalises REFUTED — underpowered by construction (Y2 costs `tuned_L0` 3.8 pts vs X1's 15.8) |
| is the family or the *mechanism* the unit | `tuned_X1m − tuned_L0` on **X1s**; `tuned_X1s − tuned_L0` on **X1m** | *pending (382540 → 382541)* | H-family-unit |
| does either half carry the whole | `tuned_X1m − tuned_X1`, `tuned_X1s − tuned_X1` on **X1** | *pending* | H-whole-ge-parts |
| a *hard* second family | — | *not run* | E5b: generator not written |

Reading: transfer follows the family, not the transform (six seen transforms do not reach H1;
one sibling does, losslessly) and not "invariance" (a gentle novel family shows nothing). The
open question is the grain *inside* a family — whether X1's MBA half and string half are one
skill or two — and that is what the X1m/X1s stages measure. Caveat on file: X1s covers fewer
programs (2,910 vs 4,263 training pairs), so its leg has less power.

Dependencies stated plainly: RQ1′'s scale leg and RQ3′'s survival both hinge on the E3/composite
runs at 13B/34B; if `cons_lam3` does not beat `mono_all` on X1 at either scale, RQ3′ shrinks to a 7B
observation and is reported as such. Refuted hypotheses are reported as refuted.

---

## Changelog
- **2026-09-08** — §6.1/§6.2 result tables added for RQ1′ and RQ2′ (user request), including the
  pipeline's first reads (13B composites, depth 3/4) and the pending rows named by job id.
- **2026-09-07 (later)** — §5 marks RQ-A/RQ-B answered and maps every other proposed RQ to a
  pipeline stage or a stated deferral; §6 adopts RQ1′–RQ4′ as the paper's spine (user decision,
  "let's add these as rqs and run the experiment").
- **2026-09-07** — Created. §4 is new analysis, not a restatement: the composite cells existed on
  the Qwen panel and had never been read as a group, and the `mono_all − tuned_L0` sign flip
  between stacked and unseen conditions had not been noticed anywhere in the project.
