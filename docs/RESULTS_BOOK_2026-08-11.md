# obtune — Results Book

*Last updated: 2026-08-11. Every result, in tables, explained from scratch.*

This document assumes **no prior knowledge of the project**. Part I explains what is being
measured and how to read a number. Parts II–VII are the results, one table per question. Part VIII
is what has not run yet. Part IX is what is known to be wrong.

Companion documents: [`MASTER_REPORT_2026-08-11.md`](MASTER_REPORT_2026-08-11.md) is the same
content written as prose; [`CLAUDE.md`](../CLAUDE.md) is the project charter.

---
---

# PART I — What you need to know to read any table below

## I.1 The research question

Take a program. Obfuscate it — rename the variables, flatten the control flow, inject dead code —
so it computes the same thing but looks different. Now ask a language model to predict its output.

Fine-tuning a model on obfuscated code makes it better at this. **The question is what it learned.**

| hypothesis | what it predicts |
|---|---|
| **Semantic invariance** | it learned to see through *any* meaning-preserving transform, including ones it never saw |
| **Transform memorization** | it learned to undo the *specific* obfuscators in its training set, and nothing more |

The discriminator is a held-out obfuscator that is never trained on. If tuning on transforms A–F
helps on unseen transform G, that is invariance. If it does not, it is memorization.

**One positioning note that matters for reading everything else:** evaluation is *always* output
prediction on still-obfuscated code. The model is never asked to recover the original source. That
is what separates this from the deobfuscation literature — and it is why Part V, which *does* study
recovery, is a separate programme with separate metrics.

## I.2 The condition ladder — the seven codes in every table

Conditions are **single transforms applied to the same parent program**, never stacked, with
identical semantics in Python and JavaScript.

| code | family | what it does | trainable? |
|---|---|---|---|
| `L0` | none | the original, comments and docstrings stripped | yes |
| `L1b` | identifier | **adversarial** renaming — misleading names, including the entry function | yes |
| `L1r` | identifier | random hex renaming (`v_a3f2`) | yes |
| `L2` | identifier | sequential minification (`a`, `b`, …) + annotation stripping | yes |
| `S1` | structural | control-flow flattening — body becomes a dispatch loop over a state variable | yes |
| `S2` | structural | opaque predicates + dead code | yes |
| `S3` | structural | dead **helper functions** only (split out of S2) | yes |
| `S4` | structural | opaque **predicates** only (split out of S2) | yes |
| **`H1`** | **held-out** | string encoding + guarded MBA rewriting | **never** |

**`H1` is the whole experiment.** It is quarantined: never used for training, hyperparameter
selection, router training, checkpoint selection, or merge tuning; evaluated exactly twice; every
read is logged. Four independent enforcement layers exist because any one is bypassable. If H1
leaked, the headline claim would be dead and no analysis could recover it.

## I.3 The systems being compared

| system | what it is |
|---|---|
| `base` | the untouched model. The floor. |
| `tuned_<C>` | one LoRA adapter trained on condition `C` alone. The "specialist". |
| **`tuned_L0`** | **the control.** Trained on *clean* code only. |
| `mono_all` | one adapter trained on all conditions mixed together |
| `oracle_prompt_1shot` | no tuning; the prompt is told which transform was applied, plus one example |
| `router` | a classifier picks which specialist to apply, per item |
| `merge_ties` / `merge_dare_ties` / `merge_dare_linear` | the specialists algebraically merged into one adapter |

## I.4 Why `tuned_L0` is the control, and why this changes every number

The obvious comparison is *specialist vs `base`*. That comparison is misleading, and the project's
own pilot is what forced the change.

Training on **clean** code already improves accuracy on **obfuscated** code, a lot. So a specialist
that beats `base` has proven nothing — most of its gain is just "was fine-tuned at all". The
control isolates the part that is actually about the transform:

```
specialist advantage  =  acc(tuned_C on C)  −  acc(tuned_L0 on C)
```

Every "gain" column in this document is against `tuned_L0` of the **same seed and the same grid**.

## I.5 Transfer Ratio — the RQ1 statistic

```
TR(i→j)  =  [ acc_j(tuned_i) − acc_j(base) ]  /  [ acc_j(tuned_j) − acc_j(base) ]
```

*"How much of the benefit of training on j do you get by training on i instead?"*

| TR value | meaning |
|---|---|
| `1.0` | training on i is as good as training on j — full transfer |
| `0.0` | training on i does nothing for j |
| `< 0` | training on i actively **hurts** on j |
| `—` | denominator too small to divide by (guard: needs ≥3 pts **and** a CI excluding zero) |

The `—` guard matters. When the specialist barely beats base, the denominator is near zero and the
ratio explodes. Blanks in the TR tables are refusals to divide, not missing runs.

## I.6 The two grids — never pool them

| | **Grid A ("corpus")** | **Grid B ("testset")** |
|---|---|---|
| programs | 317 Python / 91 JS | 33 Python / 30 JS |
| conditions | all 7, **including H1** | L0–S2, +S3/S4, +H1 for merges |
| systems | base, specialists (2 seeds), mono, oracle prompt | router, the 3 merges, specialists |
| source | held-out corpus split | ICSE test-set programs |

They are **disjoint in programs**. Pooling them silently averages two different populations. Every
table below is labelled with its grid.

## I.7 Two numbers to keep in your head

| quantity | value | why it matters |
|---|---|---|
| **seed noise** | 1.32 pts mean, **3.61 pts at p95** | measured over 84 matched seed-17/seed-42 pairs. Any single-seed delta below ~3.6 pts is inside the noise of re-rolling the dice. |
| **chance floor** | ~0 | output prediction is free-form generation graded by strict normalized exact match. No substring/containment matching — an audit found ~3% false positives from containment (`927` matching inside `9273`). |

## I.8 Scale of evidence

| | |
|---|---|
| evaluation cells | **597** |
| graded trials | **317,810** |
| models | Qwen2.5-Coder-1.5B-Instruct, Qwen2.5-Coder-7B-Instruct |
| languages | Python, JavaScript |
| seeds | 17, 42 |
| queue state | 164 done · 4 running · 3 queued · **0 failed** |
| test suite | 432 passing |

---
---

# PART II — RQ1: Does tuning teach invariance or memorization?

## II.1 Accuracy — Grid A, Python, seed 17

n = 317 programs, 86,450 trials. Diagonal (own-condition) cells in **bold**.

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| `base` | .201 | .165 | .164 | .176 | .187 | .147 | **.066** |
| `tuned_L0` *(control)* | .440 | .321 | .353 | .353 | .379 | .411 | .259 |
| `tuned_L1b` | .427 | **.360** | .359 | .354 | .353 | .402 | .263 |
| `tuned_L1r` | .445 | .333 | **.383** | .381 | .375 | .422 | .260 |
| `tuned_L2` | .436 | .328 | .366 | **.363** | .366 | .419 | .254 |
| `tuned_S1` | .433 | .296 | .352 | .355 | **.414** | .418 | .266 |
| `tuned_S2` | .459 | .317 | .367 | .365 | .415 | **.445** | **.294** |
| `mono_all` | .392 | .355 | .341 | .359 | .372 | .390 | .228 |
| `oracle_prompt_1shot` | .243 | .180 | .197 | .213 | .202 | .226 | .158 |

## II.2 Accuracy — Grid A, Python, seed 42

n = 317 programs, 46,550 trials.

| system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| `base` | .201 | .165 | .164 | .176 | .187 | .147 | .066 |
| `tuned_L0` *(control)* | .439 | .318 | .362 | .346 | .373 | .415 | .259 |
| `tuned_L1b` | .430 | **.378** | .374 | .366 | .341 | .407 | .239 |
| `tuned_L1r` | .433 | .342 | **.373** | .373 | .371 | .423 | .255 |
| `tuned_L2` | .441 | .332 | .363 | **.365** | .364 | .419 | .253 |
| `tuned_S1` | .434 | .299 | .341 | .354 | **.427** | .419 | .264 |
| `tuned_S2` | .445 | .322 | .357 | .366 | .413 | **.438** | **.290** |

## II.3 Accuracy — Grid A, JavaScript, seed 17

n = 91 programs, 15,288 trials.

| system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| `base` | .289 | .223 | .223 | .253 | .245 | .110 | .125 |
| `tuned_L0` *(control)* | .528 | .443 | .509 | .528 | .480 | .429 | .238 |
| `tuned_L1b` | .528 | **.517** | .506 | .528 | .469 | .392 | .253 |
| `tuned_L1r` | .531 | .451 | **.520** | .535 | .491 | .388 | .209 |
| `tuned_L2` | .531 | .447 | .509 | **.546** | .491 | .443 | .213 |
| `tuned_S1` | .506 | .425 | .465 | .491 | **.502** | .300 | .202 |
| `tuned_S2` | .520 | .443 | .517 | .520 | .542 | **.513** | **.311** |
| `oracle_prompt_1shot` | .289 | .220 | .238 | .282 | .267 | .264 | .183 |

## II.4 Accuracy — Grid A, JavaScript, seed 42

n = 91 programs, 13,377 trials.

| system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| `base` | .289 | .223 | .223 | .253 | .245 | .110 | .125 |
| `tuned_L0` *(control)* | .513 | .429 | .484 | .528 | .509 | .465 | .249 |
| `tuned_L1b` | .513 | **.506** | .506 | .524 | .484 | .366 | .256 |
| `tuned_L1r` | .531 | .418 | **.513** | .524 | .520 | .410 | .249 |
| `tuned_L2` | .517 | .418 | .502 | **.513** | .539 | .443 | .245 |
| `tuned_S1` | .484 | .410 | .447 | .473 | **.480** | .418 | .242 |
| `tuned_S2` | .520 | .443 | .506 | .498 | .531 | **.531** | **.326** |

## II.5 The specialist advantage — the headline RQ1 number

Own-condition accuracy minus the `tuned_L0` control, Grid A Python seed 17, cluster-bootstrapped by
program (2000 draws).

| condition | specialist | control | **gain (pts)** | 95% CI | excludes 0? | vs p95 seed noise (3.61) |
|---|---|---|---|---|---|---|
| L1b | .360 | .321 | **+3.89** | [1.48, 6.41] | yes | at the band |
| S1 | .414 | .379 | **+3.47** | [0.74, 6.43] | yes | at the band |
| S2 | .445 | .411 | **+3.47** | [1.26, 5.79] | yes | at the band |
| L1r | .383 | .353 | **+3.05** | [0.84, 5.36] | yes | below |
| L2 | .363 | .353 | +1.05 | [−0.95, 3.16] | **no** | below |

**Reading:** four of five specialists significantly beat the control on their own condition, but by
3–4 points — the same magnitude as re-running with a different seed. Specialization is real and
small. *That is itself the central RQ2 result: there is very little for a router to win.*

## II.6 Transfer Ratio matrices

Rows = trained on, columns = evaluated on. `—` = denominator guard refused the division (§I.5).

**Grid A · Python · seed 17**

| train ↓ / eval → | L1b | L1r | L2 | S1 | S2 |
|---|---|---|---|---|---|
| **L1b** | 1.000 | 0.207 | — | **−0.758** | −0.242 |
| **L1r** | 0.297 | 1.000 | — | −0.121 | 0.333 |
| **L2** | 0.189 | 0.448 | 1.000 | −0.364 | 0.242 |
| **S1** | **−0.649** | −0.034 | — | 1.000 | 0.212 |
| **S2** | −0.108 | 0.483 | — | **1.030** | 1.000 |

**Grid A · Python · seed 42**

| train ↓ / eval → | L1b | L1r | L2 | S1 |
|---|---|---|---|---|
| **L1b** | 1.000 | — | — | −0.577 |
| **L1r** | 0.404 | 1.000 | — | −0.038 |
| **L2** | 0.228 | — | 1.000 | −0.154 |
| **S1** | −0.316 | — | — | 1.000 |
| **S2** | 0.070 | — | — | **0.731** |

**Grid A · JavaScript · seed 17**

| train ↓ / eval → | L1b | L2 | S1 | S2 |
|---|---|---|---|---|
| **L1b** | 1.000 | — | — | −0.435 |
| **L1r** | 0.100 | — | — | −0.478 |
| **L2** | 0.050 | 1.000 | — | 0.174 |
| **S1** | −0.250 | — | 1.000 | **−1.522** |
| **S2** | 0.000 | — | — | 1.000 |

**Grid A · JavaScript · seed 42**

| train ↓ / eval → | L1b | L2 | S1 | S2 |
|---|---|---|---|---|
| **L1b** | 1.000 | — | — | −1.500 |
| **L1r** | −0.143 | — | — | −0.833 |
| **L2** | −0.143 | 1.000 | — | −0.333 |
| **S1** | −0.238 | — | 1.000 | −0.722 |
| **S2** | 0.190 | — | — | 1.000 |

**Reading — three patterns, all replicated across seeds:**

| pattern | evidence | interpretation |
|---|---|---|
| Identifier transforms transfer to each other | L2→L1r 0.448, L1r→L1b 0.297/0.404 | one shared "ignore the names" skill |
| Structural ↔ identifier transfer is **negative** | L1b→S1 −0.758/−0.577, S1→L1b −0.649/−0.316 | the two families *interfere*; training on one costs you the other |
| S2→S1 is the exception | 1.030 / 0.731 | S2 alone generalizes across the structural family |

## II.7 The H1 result — the discriminator

| system | H1 accuracy (Grid A py s17) | gain over `base` | gain over `tuned_L0` control |
|---|---|---|---|
| `base` | .066 | — | — |
| `oracle_prompt_1shot` | .158 | +9.2 | — |
| `mono_all` | .228 | +16.2 | **−3.1** |
| **`tuned_L0`** *(clean code only)* | **.259** | **+19.3** | 0 (is the control) |
| `tuned_L1r` | .260 | +19.4 | +0.1 |
| `tuned_L2` | .254 | +18.8 | −0.5 |
| `tuned_L1b` | .263 | +19.7 | +0.4 |
| `tuned_S1` | .266 | +20.0 | +0.7 |
| **`tuned_S2`** | **.294** | **+22.8** | **+3.5** |

**Reading:** the entire jump from .066 to .259 comes from tuning on **clean code**. Every
obfuscation-specific specialist adds between −0.5 and +3.5 points on top of that. The Invariance
Index is therefore measuring something far weaker than "learned the transform class".

**The one durable exception is `tuned_S2`**, which is the best system on H1 at both seeds in both
languages (py .294/.290, js .311/.326). S2 is the only condition whose training generalizes to the
held-out family beyond the clean-code baseline.

## II.8 Does a bigger adapter help? (rank sweep)

Monolithic adapter at increasing LoRA rank, evaluated on H1, against the `tuned_L0` control.
Equivalence margin 4.0 pts.

| system | H1 acc | control | delta (pts) | 95% CI | verdict |
|---|---|---|---|---|---|
| `mono_all` (r32) | .228 | .258 | −2.95 | [−5.16, −0.74] | **hurts** |
| `mono_r64` | .243 | .258 | −1.47 | [−2.95, −0.05] | trivial |
| `mono_r128` | .217 | .258 | −4.11 | [−6.32, −2.00] | **hurts** |
| `mono_r192` | .212 | .258 | −4.63 | [−7.05, −2.42] | **hurts** |

**Reading:** capacity is not the constraint. Training one adapter on *all* conditions is worse on
the held-out family than training one on clean code alone, at every rank tested, and gets worse as
rank grows. Mixing the transform families in one adapter destroys held-out generalization —
consistent with the negative structural↔identifier transfer in §II.6.

---
---

# PART III — RQ2: Is modularity better than one big adapter?

## III.1 Grid B — Python, n = 33 programs

| system | L0 | L1b | L1r | L2 | S1 | S2 | S3 | S4 | **H1** |
|---|---|---|---|---|---|---|---|---|---|
| `base` | — | — | — | — | — | — | .186 | .221 | — |
| `tuned_L0` | — | — | — | — | — | — | .483 | .448 | — |
| `tuned_L1b` | .490 | .483 | .538 | .517 | .434 | .441 | .497 | .476 | — |
| `tuned_L1r` | .483 | .386 | .476 | .497 | .421 | .441 | .441 | .476 | — |
| `tuned_L2` | .476 | .490 | .503 | .524 | .434 | .434 | .455 | .455 | — |
| `tuned_S1` | .407 | .331 | .455 | .469 | .441 | .352 | .414 | .400 | — |
| `tuned_S2` | .483 | .434 | .497 | .524 | .469 | .483 | .490 | .503 | — |
| `tuned_S3` | .476 | .379 | .497 | .462 | .448 | .469 | .455 | .469 | — |
| `tuned_S4` | .490 | .428 | .538 | .483 | .455 | .469 | .455 | .483 | — |
| **`router`** | .503 | .483 | .483 | .517 | .434 | .483 | — | — | — |
| `merge_ties` | .407 | .310 | .359 | .400 | .386 | .310 | — | — | .293 |
| **`merge_dare_ties`** | .503 | .407 | .434 | .510 | .441 | .428 | — | — | **.374** |
| `merge_dare_linear` | .048 | .048 | .034 | .028 | .048 | .069 | — | — | .051 |

## III.2 Grid B — JavaScript, n = 30 programs

| system | L0 | L1b | L1r | L2 | S1 | S2 | S3 | S4 | H1 |
|---|---|---|---|---|---|---|---|---|---|
| `base` | — | — | — | — | — | — | .299 | .269 | — |
| `tuned_L0` | .425 | .366 | .455 | .410 | .425 | .313 | .418 | .381 | — |
| `tuned_L1b` | .433 | .463 | .425 | .440 | .410 | .284 | .396 | .351 | — |
| `tuned_L1r` | .433 | .366 | .418 | .440 | .440 | .254 | .358 | .351 | — |
| `tuned_L2` | .425 | .351 | .448 | .440 | .425 | .261 | .381 | .366 | — |
| `tuned_S1` | .433 | .328 | .425 | .448 | .433 | .239 | .396 | .358 | — |
| `tuned_S2` | .410 | .366 | .396 | .425 | .440 | .433 | .418 | .418 | — |
| `tuned_S3` | .433 | .373 | .425 | .425 | .448 | .366 | .425 | .396 | — |
| `tuned_S4` | .396 | .366 | .403 | .425 | .433 | .381 | .403 | .425 | — |
| **`router`** | .425 | .455 | .418 | .448 | .433 | .433 | — | — | — |
| `merge_ties` | .351 | .299 | .366 | .351 | .373 | .410 | — | — | .185 |
| **`merge_dare_ties`** | .425 | .358 | .433 | .425 | .410 | .396 | — | — | **.222** |
| `merge_dare_linear` | .157 | .075 | .112 | .045 | .105 | .052 | — | — | .019 |

## III.3 The router is saturated

| metric | value | maximum |
|---|---|---|
| validation accuracy | **0.9969** | 1.0 |
| overall route accuracy | **1.000** | 1.0 |
| mean routing entropy | **~1e-6 nats** | 2.079 nats |
| confusion matrix | perfectly diagonal (176/176 per class × 8) | — |
| best epoch | 7 | — |
| **items routed from the held-out family** | **0** | — |

**Reading:** picking the right specialist is a *solved problem* on seen conditions — and it buys
almost nothing, because the specialists are only ~3.5 pts above the control (§II.5). The last row
is the open question: H1 was never actually routed, so out-of-distribution routing is untested.

## III.4 Merge methods ranked

Best available H1 number per method.

| method | H1 (py) | H1 (js) | what it does | verdict |
|---|---|---|---|---|
| **`merge_dare_ties`** | **.374** | **.222** | randomly prune, then elect by sign | **best system on H1 in the project** |
| `merge_ties` | .293 | .185 | elect by sign only | worse than prune-then-elect |
| `mono_all` *(Grid A)* | .228 | — | one adapter, all data | worse than both |
| `merge_dare_linear` | .051 | .019 | weighted sum | **broken — excluded** |

`merge_dare_linear`'s collapse is a **7.175× ‖ΔW‖ scale artifact**: the merged direction is right
(cosine 0.83 with the working merge) and the magnitude is wrong. It is not a method result. A
scale-corrected re-run is queued.

---
---

# PART IV — Catastrophic forgetting

Does obfuscation tuning damage general coding ability? HumanEval+ pass@1 over 164 tasks; 0 scorer
errors in every run.

| arm | 1.5B base | 1.5B plus | 7B base | 7B plus |
|---|---|---|---|---|
| **untouched base** | **.713** | **.646** | **.854** | **.805** |
| `rev` | .628 | .585 | — | — |
| `flipsym` | .610 | .543 | — | — |
| `flip` | .616 | .512 | .811 | .744 |
| `mix50` | .543 | .470 | .799 | .732 |
| `cft` | .409 | .366 | .860 | .799 |
| **`sft`** *(forward-only)* | **.372** | **.329** | .878 | .817 |

**Reading:**

| finding | evidence |
|---|---|
| At 1.5B, forward-only SFT is the **most destructive** arm tested | .329 vs base .646 — loses 31.7 pts |
| Bidirectional training is **less** damaging, not more | `flip` .512 and `rev` .585 both beat `sft` .329 |
| At 7B the damage vanishes entirely | `sft` .817 ≥ base .805 |

Scale, not bidirectionality, is what protects general ability.

> **This table was 0.0 everywhere until 2026-08-10.** The scorer read an `expected_output` key that
> does not exist, and a bare `except` swallowed the `KeyError`. Every forgetting number published
> before that date was wrong.

---
---

# PART V — Replicating (and refuting) Contrastive Fine-Tuning

## V.1 What is being tested

A separate paper (`nikiema2025contrastive`, arXiv:2509.05553) claims:

> Forward-only fine-tuning on obfuscation yields **0%** at the reverse task (deobfuscation) —
> "cognitive specialization". Contrastive Fine-Tuning recovers **39–52%** *with no reverse training
> data*.

This programme reproduces that setup and adds **the baseline the paper omits**: reverse training
data is *free* — you just swap the two sides of each existing pair. Nothing new is collected.

| arm | trained on | why it exists |
|---|---|---|
| `sft` | forward only | the paper's "0%" arm |
| `cft` | forward + contrastive pos/neg triplets | the paper's method |
| `rev` | reverse only | the ceiling |
| **`flip`** | forward + reverse | **the missing baseline** |
| **`mix50`** | 50% forward / 50% reverse, split by program | **budget-matched control** |
| `fwd2x` | forward, 2× epochs | rules out "flip just trained longer" |
| `cftflip` | all four tasks | does the objective add over exposure? |

**Metrics.** *Forward* = predict the output of obfuscated code (exec-verified). *Reverse* = recover
a program that reproduces the original's outputs. `strict` is the headline; `identity/echo` is the
rate at which the model just parrots its input back.

## V.2 The headline table — 7B, Python, 300 programs / 1500 trials per cell

| arm | forward (exec) | **reverse (strict)** | reverse (paper metric) | identity / echo |
|---|---|---|---|---|
| `base` *(no tuning)* | .929 | **.129** | .233 | .073 |
| `sft` *(forward-only)* | .971 | **.000** | .004 | .182 |
| `fwd2x` | .969 | **.001** | .019 | .071 |
| `cft` *(the paper's method)* | .975 | **.001** | .002 | **.293** |
| `rev` *(reverse-only)* | .927 | **.329** | .351 | .000 |
| **`flip`** | .971 | **.335** | .353 | .000 |
| **`mix50`** | .961 | **.328** | .356 | .000 |

**Reading — four claims, in order of importance:**

| # | claim | evidence |
|---|---|---|
| 1 | **The paper's headline does not replicate.** CFT reaches 0.1%, not 39% | `cft` .001 |
| 2 | **CFT is worse than doing nothing.** | `base` .129 > `cft` .001 |
| 3 | **The free flip works, at no forward cost.** | `flip` .335 rev, .971 fwd (vs base .929) |
| 4 | **Bidirectional training costs nothing vs reverse-only.** | `flip` .335 ≈ `rev` .329 |

## V.3 The arm the whole argument turns on — `mix50`

`mix50` replaces half the forward instances with their reverse twins, partitioned by `program_id`
so no program appears in both directions.

| axis | `sft` (forward-only) | `mix50` | ratio |
|---|---|---|---|
| instances / epoch | 7,383 | 7,383 | **1.00×** |
| optimizer steps | 346 | 346 | **1.00×** |
| sequence tokens / epoch (∝ FLOPs) | 2,585,834 | 2,703,495 | 1.05× |
| **supervised tokens / epoch** | 1,452,433 | 1,037,139 | **0.71×** |
| **reverse (strict)** | **.000** | **.328** | **∞** |

**Reading:** matched on instances, steps and compute, with **29% less supervision**, `mix50` goes
from 0.0% to 32.8%. Bidirectional exposure produces reverse capability at *negative* budget cost.
"Cognitive specialization" is a property of the data the forward-only regime was given, not of the
objective.

## V.4 The budget accounting — measured, per epoch, 7B Python

| arm | instances | supervised tokens | sequence tokens | steps | relative (inst / sup / seq) |
|---|---|---|---|---|---|
| `fwd` *(reference)* | 7,383 | 1,452,433 | 2,585,834 | 346 | 1.00× / 1.00× / 1.00× |
| `fwd2x` | 7,383 | 1,452,433 | 2,585,834 | 692 | 1.00× / 1.00× / 1.00× |
| `mix50` | 7,383 | 1,037,139 | 2,703,495 | 346 | 1.00× / **0.71×** / 1.05× |
| `rev` | 7,383 | 622,819 | 2,820,935 | 346 | 1.00× / 0.43× / 1.09× |
| **`flip`** | 14,766 | 2,075,252 | 5,406,769 | 692 | 2.00× / **1.43×** / **2.09×** |
| **`cft`** | 18,605 | 1,486,099 | 6,841,124 | 872 | 2.52× / **1.02×** / **2.65×** |
| `cftflip` | 25,988 | 2,108,918 | 9,662,059 | 1218 | 3.52× / 1.45× / 3.74× |

**Reading:** CFT spends **2.65× the compute to add 2% supervised signal**. FLIP spends 2.09× to add
43%, all of it on the target direction. CFT is dominated on every axis a practitioner pays for.

*(These supersede the planning-document estimates of 2.60×/1.52×/0.76×; the numbers above are
measured from the actual tokenized corpus.)*

## V.5 The critical caveat — which conditions the reverse result actually lives on

Reverse success, 7B, broken out by condition. **This is the most important table in Part V.**

| arm | L1b | L1r | L2 | **S1** | **S2** |
|---|---|---|---|---|---|
| `base` | .023 | .110 | .103 | .330 | .077 |
| `sft` | .000 | .000 | .000 | .000 | .000 |
| `cft` | .000 | .000 | .000 | .003 | .000 |
| `fwd2x` | .000 | .000 | .000 | .003 | .000 |
| `rev` | .003 | .010 | .017 | **.817** | **.797** |
| `flip` | .017 | .013 | .023 | **.827** | **.797** |
| `mix50` | .010 | .007 | .023 | **.803** | **.797** |

**Reading:** the reverse capability is **almost entirely structural**. On S1 and S2 the
bidirectional arms reach 80%. On the identifier conditions (L1b/L1r/L2) *every arm including
reverse-only* is near zero.

This is not a failure — it is the **ill-posed-inverse** property, and it must be stated whenever the
headline .335 is quoted. Renaming destroys information: once `total_count` became `v_a3f2`, no
model can recover the original name, because the original name is not recoverable from the code.
Control-flow flattening and dead-code injection *are* invertible, and there the arms succeed.

So the honest headline is: **on the transforms that have a well-posed inverse, free reverse data
takes you from 0% to ~80%, while the contrastive objective takes you to 0.3%.**

## V.6 Forward accuracy is not sacrificed — 7B, by condition

| arm | L1b | L1r | L2 | S1 | S2 |
|---|---|---|---|---|---|
| `base` | .950 | .960 | .963 | .933 | .837 |
| `sft` | .970 | .950 | 1.000 | .933 | 1.000 |
| `cft` | .973 | .960 | .997 | .947 | 1.000 |
| `flip` | .970 | .960 | 1.000 | .927 | .997 |
| `mix50` | .973 | .957 | .990 | .883 | 1.000 |
| `rev` | .940 | .950 | .957 | .970 | .820 |

**Reading:** `flip` matches `sft` on forward everywhere. Bidirectionality is free in this direction
too.

## V.7 Does the contrastive objective add anything over exposure? — 1.5B factorial

| arm | forward (exec) | reverse (strict) | identity |
|---|---|---|---|
| `base` | .868 | .029 | .476 |
| `sft` | .911 | .003 | .017 |
| `cft` | .931 | .003 | .010 |
| `fwd2x` | .920 | .006 | .000 |
| `flip` | .917 | **.314** | .000 |
| `cftflip` | .936 | **.311** | .000 |

**Reading:** `cftflip` .311 vs `flip` .314 — adding the contrastive objective on top of
bidirectional exposure changes nothing. And `fwd2x` .006 rules out "flip just trained longer".
**Exposure is the mechanism; the objective is not.**

## V.8 The echo artifact

| arm (7B) | identity / echo rate |
|---|---|
| `cft` | **.293** |
| `sft` | .182 |
| `base` | .073 |
| `flip` / `rev` / `mix50` | **.000** |

**Reading:** the forward-only and contrastive arms respond by *parroting the input back* 18–29% of
the time. A grader that credited echoes as successful recovery would report a very different
number. This is why identity rate is tracked as a first-class diagnostic rather than folded into
the accuracy.

---
---

# PART VI — Approximate unlearning as a probe of shared representation

## VI.1 The question, and why the obvious experiment is impossible

Does bidirectional training build **one shared** internal mechanism, or **two disjoint** one-way
circuits? Behaviour alone cannot tell them apart — both predict that `flip` does well in both
directions.

**Unlearning can.** Delete the forward direction from `flip` and see what happens to reverse:

| if representations are… | then removing forward should… |
|---|---|
| **disjoint** | leave reverse untouched |
| **shared** | damage reverse collaterally |

*Exact* unlearning cannot test this. Exact unlearning is *defined* as retraining on the retained
data only — which here means training on reverse alone, i.e. **the `rev` arm**, whose reverse
performance is guaranteed to survive. So the signature relocates to: **approximate unlearning
over-removes relative to exact.**

The operator is exact weight-space arithmetic, not an approximation of one:

```
U(λ) = FLIP − λ·SFT        (ΔW = (α/r)·B@A, with DoRA and rsLoRA both off)
```

Two preconditions must hold before any reading is valid:
1. **forward removal reached gold** — `forward(U) ≈ forward(base)`. This defines the operating point.
2. **no collateral collapse** — HumanEval+ intact.

## VI.2 7B sweep

Base forward = .929 · FLIP forward = .970 · **REV reverse = .329 (the gold reference)**

| λ | forward | reverse | HumanEval+ | note |
|---|---|---|---|---|
| 0.00 | .970 | .337 | — | = FLIP |
| 0.25 | .967 | .331 | — | |
| 0.50 | .944 | .322 | — | |
| **0.75** | **.919** | **.305** | — | **operating point — forward ≈ base** |
| 1.00 | .946 | .251 | — | |
| 1.25 | .905 | .222 | **.823** | |
| 1.50 | .825 | .212 | — | forward over-removed |

**Over-removal at the operating point = .329 − .305 = 2.4 pts.** HumanEval+ .823 is *above* base
.805, so precondition 2 holds comfortably.

→ **Forward is removed surgically and reverse survives. The disjoint reading; SRH refuted at 7B.**

## VI.3 1.5B sweep

Base forward = .868 · FLIP forward = .921 · **REV reverse = .314 (gold)**

| λ | forward | reverse | HumanEval+ | note |
|---|---|---|---|---|
| 0.00 | .915 | .314 | .506 | = FLIP |
| 0.25 | .909 | .309 | — | |
| 0.50 | .900 | .267 | — | |
| **0.75** | **.827** | **.126** | **.585** | **operating point** |
| 1.00 | .422 | .071 | .579 | past the point; model collapsing |
| 1.25 | .003 | .002 | — | destroyed |
| 1.50 | .011 | .009 | — | destroyed |

**Over-removal at the operating point = .314 − .126 = 18.8 pts.** And precondition 2 holds in an
unusually clean way: HumanEval+ at λ=0.75 is **.585, higher than FLIP's own .512** — the model is
*not* generically damaged, it is specifically losing reverse.

→ **The shared-representation signature at 1.5B.**

## VI.4 The two scales disagree — and that is the result

| | 7B | 1.5B |
|---|---|---|
| over-removal at operating point | **2.4 pts** | **18.8 pts** |
| HumanEval+ at that point | .823 (≥ base .805) | .585 (> FLIP's .512) |
| reading | separable | entangled |

The natural interpretation — **representations disentangle as capacity grows** — is a claim neither
literature makes.

> ⚠️ **This claim is currently blocked.** Four control jobs are running right now:
> `rev − λ·sft` and `mix50 − λ·sft` at both scales. `rev` never saw forward data, so if its reverse
> falls too, the effect is the *operator damaging any adapter* rather than entanglement. **No Part
> VI claim should be published until those land.**

## VI.5 Why this design is unusually clean

| confound | why it cannot apply here |
|---|---|
| "the forget set was harder" | forget and retain sets are the **same programs, same variants** |
| "the forget set was rarer" | identical counts by construction |
| "different distribution" | they differ *only* in which side is the question |

No capability-unlearning benchmark can currently claim content-identical forget/retain sets. This
may be more publishable than the SRH result itself.

---
---

# PART VII — Are the experts overtrained for merging?

## VII.1 The question

A recent paper (Horoi et al., arXiv:2506.14126v2) argues that fine-tuning experts to their
*individual* optimum degrades **merging**, because late training is dominated by memorization,
which produces negative parameter interference.

**This describes obtune's own procedure exactly.** `run_ckpt_select` picks the checkpoint that
maximizes held-in validation accuracy — each expert's individual optimum — and every merge in the
project is built from it.

**The diagnostic** is *sign conflict*: the fraction of weight coordinates where two experts disagree
in sign. TIES merging discards exactly those, so rising sign conflict = more of the update thrown
away at merge time.

## VII.2 The standard bank — 8 experts × 3 epochs

| epoch | ‖ΔW‖ | cosine(ΔWᵢ,ΔWⱼ) | **sign conflict** | TIES keep rate |
|---|---|---|---|---|
| 1 | 0.299 | 0.584 | **0.4016** | .854 |
| 2 | 0.362 | 0.587 | **0.3940** | .858 |
| 3 | 0.371 | 0.592 | **0.3905** | .861 |

**Δ sign conflict = −0.011 → `interference_grows: false`.** The mechanism is **absent**.

## VII.3 The overtrain probe — 3 experts × 9 epochs

| epoch | ‖ΔW‖ | cosine | **sign conflict** | TIES keep rate |
|---|---|---|---|---|
| 1 | 0.286 | 0.498 | **0.3361** | .890 |
| 2 | 0.417 | 0.461 | 0.3445 | .884 |
| 3 | 0.504 | 0.439 | 0.3502 | .880 |
| 4 | 0.556 | 0.427 | 0.3535 | .878 |
| 5 | 0.583 | 0.423 | 0.3549 | .877 |
| 6 | 0.595 | 0.421 | 0.3556 | .876 |
| 7 | 0.600 | 0.421 | 0.3555 | .876 |
| 8 | 0.601 | 0.421 | 0.3555 | .876 |
| 9 | 0.602 | 0.421 | **0.3555** | .876 |

**Δ sign conflict = +0.019 → `interference_grows: true`.** The mechanism is **present**, and
plateaus at ~epoch 6.

## VII.4 Where the interference lives — by projection, epoch 1 → 9

| projection | ep 1 | ep 9 | Δ |
|---|---|---|---|
| `down_proj` | 0.3391 | 0.3750 | **+0.0359** |
| `o_proj` | 0.3131 | 0.3383 | +0.0252 |
| `v_proj` | 0.3090 | 0.3305 | +0.0215 |
| `k_proj` | 0.3454 | 0.3644 | +0.0190 |
| `up_proj` | 0.3302 | 0.3472 | +0.0169 |
| `q_proj` | 0.3653 | 0.3753 | +0.0100 |
| `gate_proj` | 0.3505 | 0.3577 | +0.0072 |

**Reading:** interference concentrates in `down_proj` — the MLP output projection — at 5× the rate
of `gate_proj`. Localized, which is itself a result.

## VII.5 Verdict

| finding | status |
|---|---|
| Sign conflict **rises** with training past epoch 3 | ✅ confirmed |
| Our standard 3-epoch bank is **under**-trained relative to where interference appears | ✅ confirmed (it *falls* over epochs 1–3) |
| Task vector doubles in norm and experts rotate apart (cos .498 → .421) | ✅ confirmed |
| Rising interference **changes merged accuracy** | ❌ **not** demonstrated — flat within CIs |

**Honest statement:** Horoi's mechanism reproduces in the overtrained regime at LoRA r=32, and does
not measurably change merged accuracy at this scale with 3 experts. Sign conflict is a pairwise
statistic — 3 experts give 3 pairs, 8 give 28 — which is why the 8-expert 9-epoch bank is being
completed before the merge-optimal search runs.

## VII.6 A confound this uncovered, affecting every merge already run

`ckpt_select` chose **different epochs for different conditions**:

| epoch chosen | conditions |
|---|---|
| 1 | `L1r`, `S3` |
| 2 | `L0`, `L1b` |
| 3 | `L2`, `S2`, `S1`, `S4` |

**Every merge in this project therefore combines task vectors of unequal training.** The
uniform-epoch sweep exists to remove this, and it has to be reported either way.

---
---

# PART VIII — What has not run yet

Pipeline is live and unattended (PPID 1, survives logoff). 11 stages complete, 12 remaining, 0 jobs
failed.

## VIII.1 Remaining stages

| # | stage | what it does | GPU-h | status |
|---|---|---|---|---|
| 1 | *(running)* | Part VI controls: `rev−λ·sft`, `mix50−λ·sft`, both scales | ~6 | **running now** |
| 2 | *(queued)* | 3 SRH evals: seed-42 stability, dose–response, 7B strategies | ~3 | queued |
| 3 | `attrib_evals` | enqueue + drain the above | ~3 | pending |
| 4 | `attrib_js_train` | the 4 JavaScript arms at 1.5B | ~10 | pending |
| 5 | `attrib_js_eval` | **does the Part V refutation hold cross-language?** | ~1 | pending |
| 6 | `attrib_analysis` | contrasts + metric tables | 0 | pending |
| 7 | `t2_overtrain` | 5 more 9-epoch arms → 8-expert bank (3 pairs → 28) | ~10 | pending |
| 8 | `t2_geometry` | §VII diagnostics over the full bank | 0 | pending |
| 9 | `t2_epoch_sweep_full` | uniform-epoch merges at {1,3,6,9} — removes the §VII.6 confound | ~5 | pending |
| 10 | `t2_merge_optimal` | 3 greedy rounds optimizing **merged** rather than individual accuracy | ~16 | pending |
| 11 | `t2_controls` | remaining unlearning control + scale-corrected `dare_linear` | ~0.5 | pending |
| 12 | `p3_composites` | 6 stacked conditions (CPU only) | 0 | **built today** |
| 13 | `p3_mole_train` | train the RouterLoRA gate | ~3 | pending |
| 14 | `p3_mole_eval` | the mixture ladder | ~1.5 | pending |

**Total ≈ 53 GPU-h ≈ 3–4 calendar days at 4 GPUs.** Inside the Aug 28 results freeze.

## VIII.2 The next programme — RouterLoRA (built today, not yet run)

Since the hard router is saturated (§III.3), the only remaining headroom is **where no single expert
is correct**. Stacked conditions manufacture exactly that: a variant containing *two* mechanisms,
where a hard router must be wrong and a mixture can be right.

| system | what it isolates |
|---|---|
| `base` | floor |
| **`mole_uniform`** | the mixture with weights pinned at 1/8 — **the primary contrast**, differs from the router in exactly one way |
| **`mole_random`** | the mixture with its gate frozen at random init — **the control that decides the headline** |
| **`mole_router`** | the trained gate: attention over experts, per token and per layer |
| `merge_dare_ties` | best existing fixed mixture (reference, differs in three ways at once) |

| pre-registered gate | rule |
|---|---|
| Gate 1 | `oracle_bestof8 − merge_dare_ties` ≤ 2 pts ⇒ **stop**, report the negative finding |
| Gate 1b | if the S1 specialist drops as much on `C_L1r_S1` as on `L1r`, composites are merely *harder*, not compositional |
| Gate 2 | `mole_router` must beat `mole_uniform` by ≥2 pts **and** gate entropy < 0.9·log 8 in half the layers |
| **`mole_random`** | if `mole_router ≈ mole_random`, the gain is rank-256 residency, **not routing**, and the headline must say so |

Build status as of today:

| check | result |
|---|---|
| gate trainable parameters | 2,766,876 |
| frozen expert bank | 295,436,288 |
| truncation at max_seq_len 2048 | **0.000%** |
| loss mask (prompt tokens = −100) | asserted |
| composite corpus coverage | **74% Python (1658/2231), 99% JS (665/674)** |
| cells schema-valid via the shared eval path | verified with a stub run |

---
---

# PART IX — Known defects and their blast radius

Nine defects found in three days. **Every one was silent** — no crash, no error, plausible-looking
numbers. All shared one shape: *an identifier or code path that did not encode what actually
varied.*

| # | defect | what it produced | blast radius | status |
|---|---|---|---|---|
| 1 | `compute_is_core` grouped across experiments | transfer matrix computed on **23 of 340 programs** | **invalidated a published RQ1 claim** | fixed; claim withdrawn |
| 2 | HumanEval+ scorer `KeyError` under a bare `except` | every forgetting number was 0.0 | all of Part IV | fixed; Part IV is the repaired table |
| 3 | `adapter_dir` ignored training length | 9-epoch runs would overwrite the 3-epoch bank | caught before loss | fixed |
| 4 | `eval_hf` rendered a prompt the accuracy grid never used | comparison across two prompt distributions | Part VIII.2 path only | fixed |
| 5 | `grid_rq1.yaml` hard-coded Python merge paths under two languages | latent cross-language leak | none (caught latent) | fixed + guard |
| 6 | composite purity vacuous **+ H1 content scan skipped** | mislabelled composites could enter training unscanned | Part VIII.2 | fixed today |
| 7 | `base` row through the mixture engine was not base | every ladder delta measured against a mixture | Part VIII.2 | fixed today |
| 8 | `t2_merge_optimal` ran the epoch sweep | Stage 1 reported as evidence for Stage 2 | naming only | renamed today |
| 9 | **7B unlearning configs used the 1.5B `cft` adapter** | a 1.5B LoRA on a 7B base, scored as a real arm | **the `cft` row in 3 runs** | found + fixed today |

## IX.1 Defect #1 — the withdrawn claim

The 2026-08-10 report stated *"transfer into L1b genuinely fails"*. **That claim is withdrawn.** It
came from computing the transfer matrix on 23 programs instead of 340. At the correct n, all L1b
cells are significant (L0→L1b +15.2 [12.1, 18.5]). §II.6 above is the corrected matrix.

## IX.2 Defect #9 — the one found while writing this document

`configs/unlearn/negation_qwen25c-7b_*.yaml` extends the **1.5B** config `cft/eval/bidir_v1.yaml`
and inherited its `cft` adapter path unchanged.

| symptom | value |
|---|---|
| outputs identical to base | **86.5%** (2594 / 3000) |
| same adapter in the correct run | 2.7% (81 / 3000) |
| did `assert_adapter_effective` fire? | **no** — 13.5% of outputs did differ |
| did anything crash? | no |

Why preflight missed it: **preflight only walked `/eval/` and `/train/` paths**, and these configs
live under `configs/unlearn/`. A `check_cross_model_adapters()` covering *every* config now exists,
verified by reintroducing the bug (1 error) and restoring it (0 errors).

**Consequence:** the `cft` row in three unlearning runs is invalid and must be regenerated. Part VI
does **not** depend on it — its argument rests on `flip`/`rev`/`u_lam*`, all correctly pointed — but
any table reproducing that row is wrong.

## IX.3 Open items needing a human decision

| # | item | why it is blocked |
|---|---|---|
| 1 | 12 orphaned duplicate merge cells (`ties_e6/e9`, `dare_ties_e6/e9`) | deletion requires approval per charter §2 |
| 2 | invalid `cft` cells from the 3 unlearning runs | regeneration means deleting cell dirs so `resume` does not skip them |
| 3 | `stats/R/config.R` needs composite levels | `01_schema_validate.R` would reject `C_` trials today |
| 4 | H1 access budget | both granted passes are open; current plan spends no further access |

---
---

# Appendix A — Coverage and data integrity

| check | result |
|---|---|
| SHA manifest verification | OK |
| H1-marker content scan over training corpus | 40 files, 122,119 rows, **no H1 labels, no H1 markers** |
| train/test splits disjoint by `program_id` | verified |
| H1 access log | 24,625 py + 4,146 js trials, all `purpose=final_eval` |
| S3/S4 coverage (train) | python 2223/2231 common · javascript 674/674 |
| preflight | 0 errors, 7 known warnings |
| test suite | 432 passing |

# Appendix B — Statistical methods

| element | choice | why |
|---|---|---|
| confidence intervals | cluster bootstrap by `program_id`, 2000 draws, seed 17 | several items per program are correlated; bootstrapping items would understate CIs |
| multiple comparisons | BH-FDR across the transfer matrix as **one family** | |
| grading | strict normalized exact match | containment matching produced ~3% false positives in audit |
| headline metric | `strict` = exec **and** paper criteria | |
| common subset | all-conditions-succeeded programs | S1/S2 bail on some programs by design; differing program sets would confound cells |
| seed policy | 2 seeds minimum before any effect claim; variance reported | |

# Appendix C — Where each number came from

| part | source |
|---|---|
| II, III | `results/analysis/master_report.json` (regenerated 2026-08-11 over 597 cells) |
| IV | `results/forgetting/humanevalplus_*.json` |
| V | `results/2026-08-10_cft-bidirectional/qwen25c-{1.5b,7b}/python/*/summary.json` |
| V.4 | `results/srh/budget_qwen7b_python.json` |
| VI | `.../unlearn_negation_python/summary.json` + `results/forgetting/` |
| VII | `results/merge_geometry/adapters{,_overtrain}_qwen25c-1.5b_python.json` |
| VIII | `scripts/pipeline.sh --status`, `runs/manifest/` |

## Changelog

- **2026-08-11** — Created. All results in tables, written to be readable with no prior project
  knowledge. Adds material absent from the prose report: Grid A seed-42 and JavaScript panels
  (§II.2–II.4), all four transfer-ratio matrices (§II.6), the rank sweep (§II.8), full Grid B for
  both languages (§III.1–III.2), the measured four-axis budget table (§V.4), **the per-condition
  reverse breakdown that reframes the Part V headline (§V.5)**, per-projection interference
  (§VII.4), and the checkpoint-heterogeneity confound (§VII.6).
