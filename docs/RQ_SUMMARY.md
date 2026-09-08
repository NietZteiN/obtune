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
| 21 | **In-context learning** (`icl_k1_clean`, `icl_k1_cross`, `icl_k4_cross`) | 1 or 4 demonstrations in the prompt, no tuning | best ICL (`k` = 4, cross-condition demos) is **−9.87 [−11.47, −8.22]** vs the clean-code adapter, pooled; +5…+9 over `base` on every condition, but never within 10 pts of any tuned arm |

### Legend — how systems are named

Every system name in this document is `<recipe>[_<variant>][_s<seed>]`. All are LoRA adapters on
the same base unless the row says otherwise; seed 17 is the default and is omitted from the name.

| name | what it is | approach # |
|---|---|---|
| `base` | the untuned model, same prompt, no adapter | — |
| `tuned_<cond>` (`tuned_L0`, `tuned_S2`, `tuned_X1`, …) | a **specialist**: one adapter trained only on that condition's rows. `tuned_L0` is trained on clean code only (4,689 rows) and is the **clean-code control** every other arm is measured against | 1 |
| `mono_all` | **monolithic breadth**: one adapter on all six seen conditions (`L0 L1b L1r L2 S1 S2`, 26,841 rows) | 2 |
| `mono_cases` | `mono_all` with **3× input cases** per program (more rows, same programs) | 11 |
| `mono_allX` | `mono_all` **plus X1** rows (breadth + family exposure) | 2 + 19 |
| `mono_half`, `mono_quarter` | `mono_all` on ½ / ¼ of the programs (RQ1′ saturation) | 18 |
| `mono_r128` | `mono_all` at LoRA rank 128 instead of 32 | 8 |
| `cons_lam<λ>` (`cons_lam1`, `cons_lam3`) | **paired consistency**, objective O1: standard SFT cross-entropy **plus λ × KL divergence** between the student's answer distribution on the obfuscated view and a frozen `tuned_L0` teacher's distribution on the **clean L0 parent** of the same program. `lam3` means λ = 3. `cons_same` is the control where the teacher sees the same obfuscated input (plain distillation) | 17 |
| `curr_sft`, `curr_kl` | **curriculum**: start from `tuned_L0`, then one epoch on the five obfuscated conditions, without / with the KL term | 16 |
| `neg_ul`, `neg_data` | **semantic negatives**: verified single-operator mutants as extra rows, with / without an unlikelihood term | 15 |
| `align_lam<λ>` | **weight-space alignment**: a hidden-state loss pulling obfuscated representations toward the clean parent's | 14 |
| `trace_L0`, `trace_mono` | **execution-trace SFT**: emit a trace before the answer | 12 |
| `loto_hold<cond>` | **leave-one-transform-out**: `mono_all` with that condition removed from training | 7 |
| `merge_*`, `l0merge_*`, `sweep_*` | **task-vector merges** of the six specialists (TIES / DARE-TIES / DARE-linear; `sweep_*_d0p7` = density 0.7; `l0merge` anchors on `tuned_L0`) | 4 |
| `mole_uniform`, `mole_random`, `mole_router`, `mole_router_bal` | **MoLE mixture** of the 8 experts: gate fixed uniform / frozen at random init / trained / trained with load balancing | 5 |
| `x1_resample` | **resampled surfaces**, objective O3: X1 rebuilt at three obfuscation seeds, 3 surfaces × 1 epoch, step-matched to `tuned_X1` | 10 + 19 |
| `oracle_prompt_1shot` | the base model told the obfuscation type in the prompt | 6 |
| `icl_k<k>_<clean|cross>` | *k*-shot in-context examples, clean or cross-condition, no tuning | — |
| `formatonly` | adapter trained on the answer *format* only (no obfuscated content) — the "did it just learn the format?" control | — |
| `norm_structural`, `norm_full` | **symbolic normalization**: canonicalise the input at inference, no training | 20 |
| `*_cases`, `*_scale`, `*_r64` | data-scale / capacity variants of the named recipe | 11, 8 |
| `_s17`, `_s42`, `_s101` | **training seed**. Two names differing only in seed are the *same recipe*; their gap is the seed band, and a "win" narrower than that band is noise | — |

Stage names (`an_depth`, `ev_teacher`, `tr_cons_tbase`, …) are pipeline stages in
`scripts/pipeline/plan.yaml`, not systems: `bld_` build, `emit_` write items, `tr_` train,
`ck_` checkpoint, `ev_` evaluate, `an_` analyse.

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

**How to read it.** *leader* = the single system with the highest accuracy on that condition
among all 83 systems ever evaluated on it (the ranking in
`results/analysis/campaign_ranking_2026-09-05.json`). *acc* is its strict exact-match accuracy.
The last column says which systems beat `tuned_L0` — the adapter trained on clean code only, the
control — with a 95 % cluster-bootstrap interval that excludes zero, and by how much (points).
Being *leader* is not the same as *beating the control*: the top six always sit inside each
other's intervals, so which of them is nominally first is seed noise.

Columns `base`/`best ICL`/`tuned_L0` are plain accuracies on the same items, no CI. Names, decoded (full key in §1): `mole_random` — mixture of the 8 specialist adapters with the
gate frozen at random init; `cons_lam3` — paired-consistency objective (SFT + 3 × KL to a
clean-code teacher on the L0 parent), seed 17; `cons_lam3_s42` — the same recipe at seed 42;
`mono_cases` — one adapter on all six seen conditions with 3× input cases; `x1_resample` — an X1
specialist trained on three resampled obfuscation surfaces; `tuned_X1` — a plain X1 specialist.

| condition | leader | acc | beats the clean-code control? | `base` | best ICL (no tuning) | `tuned_L0` |
|---|---|---:|---|---:|---:|---:|
| `L0` | `mole_random` | 0.4329 | **nothing does** | 0.257 | 0.329 (`k4_cross`) | 0.429 |
| `L1b` | `cons_lam3` | 0.4047 | all top six, +3.92…+4.22 | 0.197 | 0.271 (`k4_cross`) | 0.359 |
| `L1r` | `mono_cases` | 0.3994 | all top six, +1.92…+2.46 | 0.207 | 0.295 (`k4_cross`) | 0.376 |
| `L2` | `mono_cases` | 0.4006 | two arms, +1.92 / +2.04 | 0.202 | 0.287 (`k4_cross`) | 0.383 |
| `S1` | `cons_lam3_s42` | 0.4018 | one arm, +2.33 | 0.168 | 0.254 (`k4_cross`) | 0.380 |
| `S2` | `cons_lam3_s42` | 0.4229 | all top six, +3.00…+3.36 | 0.193 | 0.281 (`k4_cross`) | 0.388 |
| `X1` (held-out family) | `x1_resample` | 0.3237 | family arms, +3.95…+5.35 | 0.119 | not run | 0.270 |
| `H1` (held out, spent) | `tuned_X1` | 0.3180 | family arms only | — | not run | — |

The three right-hand columns are the same items (`baselines_generic` cells, n = 1,247–1,670 per
condition) and are there to place the tuned arms: ICL with four cross-condition demonstrations is
the best thing that costs no training, and it recovers roughly **40 % of the gap** between `base`
and the clean-code adapter on every condition — never more. `icl_k1_clean` / `icl_k1_cross` sit
2–4 points below `k4_cross` everywhere. No ICL arm has been run on the held-out family.

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
| **RQ1′** | What does breadth training actually **buy and cost**? | stacked-seen: `mono_all − tuned_L0` **+3.49** [+2.04, +5.01] on six depth-2 composites (7B; Qwen +3.91). Unseen: **−3.79** [−6.09, −1.65] on X1, −4.12 on H1; at 34B `tuned_L0` still wins H1 by +2.47. L0: breadth pays ~1.7–2.6 pts. **Saturation (`an_saturation`, done 2026-09-08):** the seen gain saturates by a quarter of the breadth corpus (`mono_half − mono_all` +0.01, equiv), while the X1 tax grows monotonically with volume (−0.49 → −2.31 → −3.79; `mono_quarter − mono_all` @ X1 +3.29 [+1.32, +5.35]) — H-tax-scales CONFIRMED, H-sat-mono CONFIRMED, H-sat-L0 REFUTED (clean-only still rising: half −1.05, quarter −2.71). Breadth overfits the seen transform set as a function of volume. **34B composites (`an_composite_34b`, done 2026-09-08):** `mono_all − tuned_L0` stacked-seen **+3.05** [+1.60, +4.50] — RQ-A CONFIRMED at all three scales (+3.49 / +2.90 / +3.05) against −3.79 / −4.28 / −2.64 on X1; the dissociation is not a small-model artefact. **L0 cost classified (`an_l0cost`, done 2026-09-08):** 21 of 60 arms pay a certified L0 cost, none gains, and the ranking is consistency (−0.1 … −1.0) < breadth (−1.1 … −1.7) < X1-family (−1.6 … −4.3) < alignment/negatives < TIES merges; but at n = 557 a ±1.0 TOST margin is unreachable for any genuinely different arm (38 arms "underpowered"), so "no L0 tax" claims are *no detectable cost*, not certified equivalence. | ~~34B composites~~ ~~depth-3/4~~ ~~saturation~~ ~~L0 cost classified~~ — closed. ~~*where* on L0 the cost lands~~ — answered 2026-09-08 (`an_l0strat`): **neither hypothesis, and the format half is backwards.** Breadth's cost is on the **common** answer types (−2.38 [−3.94, −0.78]) and **short** answers, with none on the unusual tail (unusual − common **+4.70** [+0.44, +8.89]); program LOC −2.00 [−5.87, +2.20] is inconclusive, though `base` *does* localize on length in the same strata (−7.36 [−13.67, −1.13]), so the null is a bound rather than an instrument failure. Both frozen verdicts are INCONCLUSIVE (the rule was one-sided) and are not re-specified. Open only as a design note: the strata cannot separate format rarity from item easiness. |
| **RQ2′** | What is the **unit** of transfer? | family, not transform and not "invariance": X1→H1 transfer is lossless (0.08 pts); `tuned_X1` at 7B ties `tuned_L0` at 34B (−0.33 [−2.88, +2.06]); the gentle second family (X2/Y2) was underpowered by construction. **Inside the family (`an_x1split`, done 2026-09-08): H-family-unit REFUTED** — the MBA half and the string half do not transfer to each other (+1.49 [−0.95, +3.93]; −0.10 [−2.38, +2.19]) — **yet either half alone gives ~90 % of the whole's X1 gain** (+4.12 / +4.20 vs +4.61; H-whole-ge-parts CONFIRMED). Transfer follows shared *surface*, not shared mechanism. | X1 split into its MBA half (X1m) and string-encoding half (X1s), each trained alone: does each half transfer to the other (`an_x1split`, H-family-unit) and does either half carry the whole (H-whole-ge-parts). E5b (a hard second family) waits on a generator. |
| **RQ3′** | Can an objective get **both sides** of the trade? | paired consistency (`cons_lam3`, parent view, tuned_L0 teacher): +4.59 over `mono_all` on X1 with no L0 tax (−0.30 [−1.80, +1.32]), and +4.76 over `tuned_L0` on stacked-seen, not below `mono_all` there (+1.27 [−0.02, +2.59]). **Survives scale (`an_e3`, done 2026-09-08, H-E3 + H-E3-tax CONFIRMED):** `cons_lam3 − mono_all` on X1 **+3.95** [+2.22, +5.84] at 13B and **+3.38** [+1.32, +5.51] at 34B; `cons_lam3 − tuned_L0` on X1 −0.33 / +0.74 (no tax at any scale). At 34B `cons_lam3` is the best arm on all seven columns (seen +3.49 over `tuned_L0`, L0 +3.05 over `mono_all`). **Replicates on Llama-3.1-8B (`an_e8`, done 2026-09-08, all three rules CONFIRMED):** +3.46 [+1.65, +5.35] over `mono_all` on X1, +2.53 [+1.30, +3.73] over `tuned_L0` on seen, L0 +0.00 [−1.56, +1.56] — best or tied-best on every column. **Stacked-seen at scale (`an_composite_34b`, done 2026-09-08): `cons_lam3 − mono_all` +2.58 [+1.26, +3.90] — H-cons-stack-strict CONFIRMED at 13B (+1.36) and 34B; at 34B `cons_lam3` loses on no column of any grid.** **The ingredient (`an_e4`, done 2026-09-08): the *tuned clean-code teacher*.** Teacher = untuned `base` collapses the arm to ~5 pts above base (`cons_tbase − mono_all` @ X1 **−8.98** [−11.44, −6.43]; H-E4-view REFUTED, H-E4-teacher CONFIRMED +13.84); teacher = `mono_all` inherits breadth's X1 tax (`cons_tmono − cons_lam3` @ X1 **−4.20** [−6.27, −2.14]; H-E4-mono REFUTED) while matching `cons_lam3` on seen (−0.39 n.s.). Decomposition: the seen gain comes from the SFT term and is teacher-independent; the unseen-family number is *distilled from the teacher* (student X1 ≈ teacher X1 + ~1 pt in every case). The method is "distil from a clean-code-*tuned* model on the clean parent" — the paper must say so. | ~~survives scale?~~ ~~replicates on Llama?~~ ~~which ingredient?~~ — closed. Open only as writing: state the claim as teacher-distillation, not as invariance learned. |
| **RQ4′** | **Why?** *(support, not a co-equal claim)* | RQ3's attention re-anchoring on seen conditions; modularity's failure (no complementary capability for a router or merge to find) as evidence about the representation. | identifier-knockout signature on X1 across five arms (`an_attention`, **done 2026-09-08: both REFUTED** — `cons_lam3 − mono_all` −0.0001 [−0.097, +0.102] nats, `mono_all − tuned_L0` +0.019 [−0.088, +0.126]; the knockout moves gold log-prob by < 0.5 % for every arm on every condition, so the instrument is inert and RQ4′ keeps only its correlational support. Unplanned: `mono_all`'s clean log P(gold) on X1 is −11.4 vs −6.3 for `tuned_L0`/`cons_lam3`); BH-FDR over the transfer and arms families (`an_fdr`, **done 2026-09-08**: the specialist matrix is 1/30 after multiplicity — only `tuned_S2` on S2, q = 0.030 — while the arms the paper rests on survive: `mono_all` X1 −3.79 q = 0.017, `tuned_X1` X1 +4.86 q = 0.009, `cons_lam3` L1b/S2 q ≤ 0.014; `cons_lam3 − tuned_L0` on X1 does not, q = 0.29). **FDR re-run with the family enlarged 7× (`an_fdr2`, done 2026-09-08): every claim the paper rests on survives** — 203 tests, 69 survive, **none of `arms`' eight lost**; `mono_all` on X1 comes back at q = 0.014 and `tuned_X1` on X1 at q = 0.005; composites 10/12 (RQ-B 6/6, RQ-A 4/6); both primary families reproduce byte-identically. Still not surviving, and still reported that way: `cons_lam3 − tuned_L0` on X1 (q = 0.44) and breadth's L0 cost (q = 0.38). Human alignment (E10) is disabled, not pretended. **Gap, stated not closed:** every FDR family is controlled against `tuned_L0`, so RQ3′'s headline `cons_lam3 − mono_all` @ X1 has never been multiplicity-corrected. A `mono_all`-controlled family is pre-registered for the next read rather than added after noticing. Plus E11b's format/difficulty confound. |
| **RQ5′** | Does forward tuning also help the **inverse** task — a stress test for understanding vs. task fitting? | **No** (`an_inverse`, done 2026-09-08): `tuned_L0` gains +18.09 forward and loses −1.67 [−3.29, −0.04] backwards on the same programs (H-inv-transfer **REFUTED**; DR −0.09). `mono_all` −1.30 vs base (at base); `cons_lam3` +0.49 (does no harm, the only SFT-family arm that does not); `tuned_X1` on X1 +3.37 [+0.41, +6.34] over base and +7.00 over `tuned_L0` (q = 0.005) — the family unit is the one thing that holds backwards. Diagonal 3/5 by the rule, but against base only L1b (+8.1) is real; S2 is −3.7. Nikiema et al.'s direction-specificity replicates at value level. Unregistered: `tuned_L1b` best inverse arm on every condition. | the same held-out items asked backwards — program + return value → a call that returns it, **graded by execution** (any arguments that produce the value count; `src/obtune/inverse.py`) — for 11 forward-trained arms on 7 conditions (`ev_inverse_*` → `an_inverse`, jobs 382620/382621 → 382622). A `formatonly` arm separates answer-format adaptation from reasoning (residue −0.45, ≈ 0); no arm failed the 25 % format gate, though `tuned_L0` fails to emit a call on 32 %/42 % of S1/S2 items. Table and full read in §6.3. |

### 6.1 RQ1′ — what breadth buys and costs: the results so far

`mono_all − tuned_L0` (six-condition breadth vs clean-code-only, same base, same rows per program),
pts [95 % CI], program-clustered bootstrap. Positive = breadth helps. CodeLlama unless marked.

| column | 7B | 13B | 34B | other |
|---|---:|---:|---:|---:|
| **stacked-seen, depth 2** (6 composites, pooled) | **+3.49** [+2.04, +5.01] | **+2.90** [+1.45, +4.37] | **+3.05** [+1.60, +4.50] | Qwen-1.5B **+3.91** [+2.58, +5.27] |
| **stacked-seen, depth 3/4** (4 composites, 394-program common subset) | **+4.15** [+2.37, +5.91] | — | — | — |
| **unseen family X1** | **−3.79** [−6.09, −1.65] | **−4.28** [−6.50, −2.06] | **−2.64** [−5.10, −0.25] | seeds s42/s101: −3.54 / −3.54 |
| **unseen family H1** (budget spent; final read) | −4.12 [−6.75, −1.81] | — | **−2.47** [−4.78, −0.41] | — |
| **clean code L0** (the cost) | −1.74 (`an_l0cost`: −1.32 [−3.35, +0.66] vs the pooled reference; s101 −2.04*) | −2.34 | **−2.63** [−4.49, −0.78] | Llama-3.1-8B **−2.22** [−4.13, −0.24] |
| seen single transform L1b (the gain, for reference) | +2.41 | +2.71 | **+5.19** [+3.02, +7.36] | Llama-3.1-8B +2.83 [+0.90, +4.76] |
| **unseen X1 vs. data volume** (`an_saturation`, 7B, s17) | quarter **−0.49** [−2.31, +1.40] → half **−2.31** [−4.36, −0.25] → full **−3.79** [−6.01, −1.65] | — | — | `tuned_L0` X1 *rises* with data 0.250→0.259→0.269; `mono` X1 *falls* 0.264→0.246→0.231; `mono_quarter − mono_all` @ X1 **+3.29** [+1.32, +5.35] |
| **seen6 vs. data volume** (saturation) | `mono_half − mono_all` **+0.01** [−1.17, +1.20] (equiv); `mono_quarter` −0.81 n.s. | — | — | `tuned_L0_half − tuned_L0` **−1.05** [−1.86, −0.24]; quarter −2.71 — clean-only is *not* saturated |
| **`cons_lam3 − mono_all` on X1** (RQ3′, `an_e3`) | **+4.59** [+3.16, +5.99] (3 seeds) | **+3.95** [+2.22, +5.84] | **+3.38** [+1.32, +5.51] | Llama-3.1-8B **+3.46** [+1.65, +5.35] — consistency removes breadth's unseen tax at every scale and on a second family |
| **`cons_lam3 − tuned_L0` on X1** (the tax consistency pays) | −0.30 [−1.80, +1.32] | −0.33 [−2.06, +1.48] | +0.74 [−0.99, +2.47] | Llama +0.58 [−1.07, +2.22] — none, anywhere |
| **`cons_lam3 − mono_all` on L0** | — | +1.74 [+0.12, +3.41] | **+3.05** [+1.32, +4.79] | and removes the L0 tax |

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
| is the family or the *mechanism* the unit | `tuned_X1m − tuned_L0` on **X1s**; `tuned_X1s − tuned_L0` on **X1m** | +1.49 [−0.95, +3.93]; −0.10 [−2.38, +2.19] | **H-family-unit REFUTED** (`an_x1split`, 2026-09-08): the halves do not reach each other |
| does either half carry the whole | `tuned_X1m − tuned_X1`, `tuned_X1s − tuned_X1` on **X1** | −0.49 [−2.06, +1.07]; −0.41 [−2.39, +1.57] | **H-whole-ge-parts CONFIRMED** — and, unanticipated, either half alone gives +4.12 / +4.20 on X1 against the whole's +4.61: ~90 % of the stacked gain from one mechanism, non-additive |
| breadth's tax on the halves | `mono_all − tuned_L0` on **X1m** / **X1s** | −4.94 [−7.44, −2.47] / −3.93 [−6.64, −1.35] | the tax is not specific to the stacked form |
| a *hard* second family | — | *not run* | E5b: generator not written |

Reading: transfer follows the family, not the transform (six seen transforms do not reach H1;
one sibling does, losslessly) and not "invariance" (a gentle novel family shows nothing). The
grain *inside* a family is now read (`an_x1split`): X1's MBA half and string half do **not** transfer to
each other, yet either half alone recovers ~90 % of the whole adapter's X1 gain. Six seen transforms do
not reach X1; either half of X1 does; the halves do not reach each other. The reading that fits all
three — and lossless X1→H1, and null X2→Y2 — is that transfer follows shared *surface* (the family's
scaffolding and prompt distribution), not shared mechanism and not invariance. Untested alternative:
a weakest-link gain on stacked items; separable at item level from existing trials (not run).

### 6.3 RQ5′ — bidirectional: does output prediction also teach input prediction?

**Why it is a stress test.** Forward tuning could raise accuracy by teaching the model to *run*
the program better, or by teaching it the forward task's surface — what an answer looks like, which
tokens to attend to for a value. Only the first should help when the same program is asked
*backwards* (CRUXEval-I style: given the return value, produce a call that yields it). No adapter
is trained on the inverse task, so any inverse gain is a transfer of program understanding, not of
task fitting. The ATTRIB replication in `paper_bidirectional/` found the opposite for *code*
emission — obfuscate-tuning did not help deobfuscation ("cognitive specialization") — so a null
here would replicate that at value level, and a positive would bound it.

**Design** (pre-registered `CLAUDE_SCRATCHPAD.md` 2026-09-08 before submission; jobs 382620/382621 → 382622):
one prompt family for every arm (`inverse_1shot_v1`, one L0 demonstration, forward template hash
unchanged); grading by execution in the sandbox — the gold arguments are never the target, a call is
correct iff it returns the gold value; `format_fail` = not a single parsable `name(args)` line.
Conditions L0 L1b L1r L2 S1 S2 X1 (no H1). Forward numbers are the existing Grid A cells.

| hypothesis | contrast (inverse task) | Δ pts [95 % CI] | verdict |
|---|---|---:|---|
| format gate | pooled-seen6 `format_fail_rate` per arm; > 0.25 ⇒ NOT INTERPRETABLE | max is `tuned_L0` 0.187 (32 % on S1, 42 % on S2); `cons_lam3` 0.014 | **nobody blocked** |
| format residue | `formatonly − base` @ seen6 | −0.45 [−0.76, −0.12] (equiv ±1.0) | ≈ 0; forward +1.84 |
| H-inv-transfer — forward tuning transfers to the inverse task | `tuned_L0 − base` @ seen6 **and** `tuned_L0 − formatonly` @ seen6 | **−1.67 [−3.29, −0.04]** · −1.22 [−2.82, +0.37] | **REFUTED** — forward +18.09 becomes −1.67 backwards; "cognitive specialization" replicates at value level |
| H-inv-breadth — breadth's stacked-seen gain has an inverse counterpart | `mono_all − tuned_L0` @ obf | +1.45 [−0.04, +2.94] | INCONCLUSIVE (`mono_all − base` −1.30 [−3.01, +0.36]) |
| H-inv-cons — the consistency objective keeps it | `cons_lam3 − mono_all` @ obf | +1.73 [+0.25, +3.27] | **CONFIRMED** — but `cons_lam3 − base` is +0.49 [−1.38, +2.30]: it avoids the SFT arms' damage, it does not teach inversion |
| H-inv-family — the family unit holds backwards | `tuned_X1 − tuned_L0` @ X1 | **+7.00 [+4.12, +9.96]** (q = 0.005) | **CONFIRMED** — and `tuned_X1 − base` @ X1 +3.37 [+0.41, +6.34]: the only forward training that beats base on the inverse task, on its own family |
| H-inv-diagonal — specialists still own their condition | `tuned_c − tuned_L0` @ c, 5 conditions | L1b +9.46* · S1 +9.38* · S2 +8.45* · L1r −1.50 · L2 −0.24 | **CONFIRMED (3/5)** by the rule; against `base` it is L1b +8.1, S1 +2.1, **S2 −3.7** — S1/S2 mostly recover `tuned_L0`'s format collapse |
| direction ratio (descriptive) | DR(arm) = (inv_arm − inv_base)/(fwd_arm − fwd_base), pooled seen6 | `formatonly` −0.24 · `tuned_L0` −0.09 · `mono_all` −0.07 · `cons_lam3` +0.03 · `tuned_X1` +0.10 | ≤ 10 % of any forward gain survives the flip; two arms reverse sign |
| BH-FDR (five primary) | | only `tuned_X1 − tuned_L0` @ X1 survives (q = 0.005); the rest q = 0.065–0.14 | reported, gates nothing |

**Pooled accuracy, inverse vs forward** (seen6 mean; X1 separately; job 382620/382621):

| arm | inv seen6 | fwd seen6 | inv X1 | fwd X1 | inv `format_fail` |
|---|---:|---:|---:|---:|---:|
| `base` | 0.290 | 0.204 | 0.257 | 0.119 | 0.035 |
| `formatonly` | 0.285 | 0.222 | 0.250 | 0.125 | 0.038 |
| `tuned_L0` | 0.271 | 0.386 | 0.221 | 0.270 | 0.192 |
| `mono_all` | 0.277 | 0.393 | 0.237 | 0.232 | 0.035 |
| `cons_lam3` | 0.295 | 0.405 | 0.281 | 0.283 | 0.014 |
| `tuned_X1` | 0.306 | 0.370 | 0.290 | 0.319 | 0.053 |
| `tuned_L1b` | **0.346** | — | **0.302** | — | 0.030 |
| `tuned_L1r` | 0.287 | — | 0.226 | — | 0.055 |
| `tuned_L2` | 0.297 | — | 0.246 | — | 0.071 |
| `tuned_S1` | 0.288 | 0.383 | 0.249 | 0.272 | 0.141 |
| `tuned_S2` | 0.281 | 0.391 | 0.213 | 0.286 | 0.100 |

**Read (2026-09-08, `an_inverse` 382622; log `log/transfer/2026-09-08_bidirectional-inverse-task-read.md`).**
Output-prediction tuning does not teach input prediction. The adapter that gains +18 pts forward loses
1.7 pts backwards on the same programs; breadth (`mono_all`) sits exactly at base; the consistency
objective is the only SFT-family arm that does no harm, and the X1-family adapter is the only arm that
transfers above base — on its own family. Both pre-read expectations were wrong: base inverse accuracy
(0.29) is *above* base forward (0.20), because execution grading accepts any call that reproduces the
value, and no arm failed the format gate. Unregistered, single-seed: **`tuned_L1b` is the best inverse
arm on all seven conditions** (+5.6 over base pooled) while `L1r`/`L2` specialists do nothing — the one
forward signal that penalises trusting identifiers is the one that transfers backwards. Forward and
inverse orderings do not agree (`tuned_X1` > `cons_lam3` > `base` > `mono_all` > `tuned_L0` inverse).

Expectation stated before the read: base inverse accuracy will be well below forward (CRUXEval-I is
harder than CRUXEval-O for every published model) and the base arm may fail the format gate — the
one-shot demonstration and the `formatonly` control exist for exactly that.

Dependencies stated plainly: RQ1′'s scale leg and RQ3′'s survival both hinge on the E3/composite
runs at 13B/34B; if `cons_lam3` does not beat `mono_all` on X1 at either scale, RQ3′ shrinks to a 7B
observation and is reported as such. Refuted hypotheses are reported as refuted.

---

## Changelog
- **2026-09-08 (E7b, E11b)** — §6 RQ1′ row closes the "where does the L0 cost land" question (neither hypothesis; the format half runs significantly the other way) and §6 RQ4′ row carries the enlarged FDR family (every claim survives; the uncorrected `cons_lam3 − mono_all` headline recorded as a gap). Master report rev 18 adds §29 for the whole campaign. Entries `log/transfer/2026-09-08_where-the-l0-cost-lands.md`, `log/writeup/2026-09-08_fdr-family-enlarged.md`, `log/writeup/2026-09-08_master-report-rev18.md`.
- **2026-09-08 (composite_34b, E4, E11)** — §6 RQ1′ row carries the 34B composites (RQ-A at three scales) and the L0-cost classification (21 pay, 0 gain, 38 underpowered at ±1.0 — "no L0 tax" is *no detectable cost*, not certified); §6.1 34B stacked-seen cell filled (+3.05) and the L0 row annotated; §6 RQ3′ row carries H-cons-stack-strict (CONFIRMED at 13B/34B) and the E4 teacher decomposition (tuned clean-code teacher is the ingredient; seen gain teacher-independent, unseen number distilled from the teacher). RQ3′'s open column is now empty. Entries `log/transfer/2026-09-08_composites-at-34b.md`, `_teacher-is-the-ingredient.md`, `_l0-cost-classified.md`.
- **2026-09-08 (E6)** — §6 RQ2′ row and §6.2 carry the X1-split read: halves do not reach each other (H-family-unit REFUTED) but either half carries ~90 % of the stacked gain.
- **2026-09-08 (E8)** — §6 RQ3′ row and §6.1 carry the Llama replication: +3.46 over breadth on X1, +2.53 over clean-only on seen, L0 +0.00.
- **2026-09-08 (E3)** — §6 RQ3′ row and §6.1 carry the scale read: consistency beats breadth on X1 at 13B (+3.95) and 34B (+3.38) with no tax against `tuned_L0`; best arm on every column at 34B.
- **2026-09-08 (E12)** — §6 RQ1′ row and §6.1 carry the saturation read: seen gain saturates by ¼ corpus, X1 tax grows with volume (−0.49 → −2.31 → −3.79).
- **2026-09-08 (RQ5′ read)** — §6 RQ5′ row and §6.3 carry the `an_inverse` read: H-inv-transfer REFUTED (+18 forward → −1.7 backwards), H-inv-family the only above-base transfer, H-inv-cons "does no harm", diagonal qualified against base.
- **2026-09-08 (E9)** — §6 RQ4′ row carries the knockout read: both attention hypotheses refuted, instrument inert.
- **2026-09-08 (FDR)** — §6 RQ4′ row carries the `an_fdr` read (1/30 transfer cells, 8/28 arm cells survive BH).
- **2026-09-08 (RQ5′)** — §6 gains RQ5′ (bidirectional / inverse-task stress test): table row and §6.3 with
  pre-registered hypotheses, all pending on jobs 382620/382621 → 382622.
- **2026-09-08 (ICL)** — §1 row 21 adds the in-context-learning baselines; §3 gains `base` / best-ICL /
  `tuned_L0` reference columns per condition (user request).
- **2026-09-08 (later)** — §1 gains a naming legend (every system name decoded, with the
  approach number it belongs to); §3 now defines *leader* and decodes each leader's name
  (user request: the names were opaque).
- **2026-09-08** — §6.1/§6.2 result tables added for RQ1′ and RQ2′ (user request), including the
  pipeline's first reads (13B composites, depth 3/4) and the pending rows named by job id.
- **2026-09-07 (later)** — §5 marks RQ-A/RQ-B answered and maps every other proposed RQ to a
  pipeline stage or a stated deferral; §6 adopts RQ1′–RQ4′ as the paper's spine (user decision,
  "let's add these as rqs and run the experiment").
- **2026-09-07** — Created. §4 is new analysis, not a restatement: the composite cells existed on
  the Qwen panel and had never been read as a group, and the `mono_all − tuned_L0` sign flip
  between stacked and unseen conditions had not been noticed anywhere in the project.
