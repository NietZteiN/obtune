# Experiment plan for the paper

*Last updated: 2026-09-09*

**Working title claim:** *fine-tuning on obfuscated code teaches the transformation **family** it was
shown, not semantic invariance — and training on more families makes it worse on an unseen one.*

Scope assumed here: **Python only, CodeLlama-7b/13b/34b**, with Llama-3.1-8B as a cross-family
check. **No Chinese-origin model is used for any paper result** (2026-09-09; `MODEL_AND_DATA_SELECTION.md`) —
Qwen-era numbers are record, not evidence; the panel extension is F10 and the dataset additions F11. JavaScript is excluded by necessity (`node` is not installed on juno) and that exclusion is
**declared in the paper**, not discovered by a reviewer — see §5. Every cost below is measured on
this cluster, not estimated: 7B specialist 22 min, 7B `mono_all` 3.5 h, 7B consistency arm 4.4 h,
13B `mono_all` 5.2 h, 34B `mono_all` 9.8 h, eval ≈ 12 s/cell at 7B. Add ~5 min/job of ckpt-select
and expect queue waits in hours, not minutes (CLAUDE.md §1).

---

## 1. What the paper claims, and what already supports it

| # | claim | current evidence | status |
|---|---|---|---|
| C1 | Breadth training **hurts** on an unseen obfuscator | on H1: **+4.12 [+1.81, +6.75]** (7B), **+2.47 [+0.41, +4.78]** (34B); on X1: **+3.79 / +4.28 / +2.64** at 7B/13B/34B and **+3.79 / +3.54 / +3.54** at s17/s42/s101 (E1/E2, 09-07) | **done** — two held-out columns, three scales, three seeds |
| C2 | What transfers is the **mechanism family**, not invariance | X1→H1 lossless (0.08 pts); `tuned_X1` (7B) ties `tuned_L0` (34B), −0.33 [−2.88, +2.06]; `tuned_X1 − tuned_S2` +3.46 [+1.32, +5.51]. **E5 (09-07) failed to generalise it to a second family** (+1.21 [−0.81, +3.22]) — but that family was too easy to test it (3.8 pts of damage vs X1's 15.8) | **one family pair only**; scope narrowed to *hard* families; E5b is the redo |
| C3 | Within the trained ladder, transfer is near-complete at 7B+ | mean off-diagonal TR **0.9057 [0.8784, 0.9322]**; LOTO recovers 0.9452 [0.8940, 1.0058] of `mono_all` | **done** |
| C4 | Modularity buys nothing, and we know why | router − random gate **+0.0000 [−0.0081, +0.0081]** while mixing is worth +0.2047; merging −3.13 vs specialists' +2.47; oracle over ten systems 52.9 pts below a permutation null | **done** |
| C5 | One objective repairs breadth: **paired consistency** | `cons_lam3 − mono_all` on X1 **+4.59 [+3.16, +5.99]** (3 seeds); no `L0` tax (−0.30 [−1.80, +1.32]); λ=3 is the plateau | **done at 7B** — E1 tests scale, E2 tests mechanism |
| C6 | Ten other levers do not move accuracy | self-consistency, augmentation, data scale, more cases, trace SFT, rerankers, span alignment, negatives, resampling, curriculum — all with intervals | **done** |
| C7 | Attention re-anchoring is the mechanism for the one transfer that works | correlational (§15.1) + knockout (§15.3) + training-free normalization (§16.5) | **partial** — E9 |
| C8 | Tuning moves models **away** from human difficulty orderings | **E10 (2026-09-08): `tuned_L0 − base` Δρ = −0.303 [−0.575, −0.028]** over the 98 Paper-2 cells; at condition level `base` tracks the human gradient at +0.82 rank correlation and every tuned arm inverts it | **answered**; weak instrument (20 programs, one trial per cell) — quote with the interval |

**Read this table as the paper's spine.** C1–C6 are complete and are enough to submit. The
experiments below either (a) close a gap a reviewer will find, or (b) convert a single observation
into a general one.

---

## 2. Tier 1 — run before submitting

### ~~E1. X1 column at 13B and 34B~~ — **DONE 2026-09-07, CONFIRMED**
**Question.** C1 and C2 rest on H1, and **H1 can never be read again** (§3.2 budget spent). Does the
held-out result replicate at scale on a column we *can* still read?
**Arms.** `tuned_L0`, `mono_all` at 13B and 34B, evaluated on X1 (4 cells). Both adapters exist at
both scales; nothing is trained.
**Why first.** It is ~15 minutes of GPU and it gives the paper's central claim a scale replication
that does not depend on the spent budget. If `tuned_L0 − mono_all` on X1 is positive at 13B/34B, C1
stands on two independent held-out columns.
**Result.** `tuned_L0 − mono_all` on X1: 7B **+3.79 [+1.65, +6.09]**, 13B **+4.28 [+2.06, +6.50]**,
34B **+2.64 [+0.25, +5.10]** — all three clear zero (job 381291/381292, 234/301 s). C1 now stands on
two independent held-out columns at three scales. Bonus: the X1↔H1 proxy, calibrated only at 7B,
validates at **34B** to |Δ| 0.49 / 0.33 pts against the already-spent H1 cells.
[`log/transfer/2026-09-07_x1-scale-and-seed-band.md`](../log/transfer/2026-09-07_x1-scale-and-seed-band.md)

### ~~E2. Seed band for the headline contrast on X1~~ — **DONE 2026-09-07, CONFIRMED**
**Question.** `mono_all` has X1 reads at s17/s42/s101 (round 2), but `tuned_L0` has only s17. The
headline contrast therefore has no seed band on any held-out column, and H1 can never provide one.
**Arms.** `tuned_L0_s42`, `tuned_L0_s101` on X1 (2 cells). Adapters exist.
**Result.** +3.79 / +3.54 / +3.54 at s17/s42/s101, every interval clearing zero; `tuned_L0` on X1
spans **0.16 pts** across seeds (job 381290, 201 s). The headline is not a seed draw.

### E3. H-cons-scale — does the one positive result survive scale? — **DONE 2026-09-08, CONFIRMED**
**Read (`an_e3` 382542).** `cons_lam3 − mono_all` on X1 **+3.95** [+2.22, +5.84] at 13B, **+3.38** [+1.32, +5.51]
at 34B (7B: +4.59 at three seeds); `cons_lam3 − tuned_L0` on X1 −0.33 / +0.74, no unseen tax at any
scale. At 34B `cons_lam3` is the best arm on all seven columns. Breadth's L0/X1 taxes are scale-invariant
(L0 −1.74/−2.34/−2.63, X1 −3.79/−4.28/−2.64); the objective, not scale, resolves the trade.
`log/transfer/2026-09-08_consistency-survives-scale.md`.

**Question.** C5 is a 7B result. If paired consistency is a small-model repair it is a much weaker
contribution than if it holds at 34B, where breadth's `L0` tax is larger (−2.63 [−4.49, −0.78]).
**Arms.** `cons_lam3` at **13B** and **34B**; controls (`tuned_L0`, `mono_all`) exist at both.
Evaluate on all seven conditions incl. X1.
**Decision rule (to be pre-registered before submission).** CONFIRM if `cons_lam3 − mono_all` on X1
excludes zero above at **both** scales; PARTIAL if one; REFUTE if neither.
**Cost.** 13B ≈ 6.5 h + 34B ≈ 12 h training, + ~1 h eval ≈ **20 GPU-h**.

### E4. H-cons-teacher — is it the *clean-code* teacher, or any teacher? — **DONE 2026-09-08: the tuned clean-code teacher, narrowly**
**Question.** C5's mechanism story is "distil from a model that saw clean code, on the clean parent".
Round 1 separated the *view* (parent vs same input, +0.94 pooled) and round 2 separated the *init*
(`currmono_kl`, −2.47 on X1). Nothing has varied the **teacher itself**.
**Arms.** `cons_lam3` with teacher = **untuned `base`** (does an untrained teacher work?) and with
teacher = **`mono_all`** (does a breadth teacher poison it?). 7B, seed 17.
**Why it matters.** If `base` works as well, the method is "distil from *some* view of the clean
parent" and is much easier to apply; if only `tuned_L0` works, the claim is narrower and must say so.
**Cost.** 2 × 4.4 h + eval ≈ **9.5 GPU-h**.
**Read (`an_e4` 382548).** `base` as teacher collapses the arm (L0 0.306, X1 0.143; `cons_tbase − mono_all`
@ X1 **−8.98** [−11.44, −6.43] — H-E4-view REFUTED, H-E4-teacher CONFIRMED +13.84). `mono_all` as teacher
matches `cons_lam3` on seen (−0.39 n.s.) but inherits breadth's X1 tax (`cons_tmono − cons_lam3` @ X1
**−4.20** [−6.27, −2.14]; `cons_tmono − mono_all` @ X1 +0.66 n.s. — H-E4-mono REFUTED). The seen gain is
teacher-independent (SFT term); the unseen-family number is distilled from the teacher. The claim is
narrower and must say so: "distil from a clean-code-*tuned* model on the clean parent".
`log/transfer/2026-09-08_teacher-is-the-ingredient.md`.

### ~~E5. A second family pair~~ — **DONE 2026-09-07, REFUTED (underpowered by construction)**
**Question.** C2 rests on **one** family pair (X1 ↔ H1). A reviewer will ask whether "the family is
what transfers" generalises or is a property of string-encoding+MBA.
**Arms.** Build **X2** and **Y2**, two *siblings* of a second mechanism family that is neither
identifier nor structural nor encoding — the natural candidate is **exception-driven control flow**
(computation routed through raised/caught exceptions), which is meaning-preserving, gateable, and
unlike anything in the current ladder. Train `tuned_X2` (7B, 22 min) and evaluate on **Y2**, the
unseen sibling, against `tuned_L0` and `mono_all`.
**Decision rule.** CONFIRM if `tuned_X2 − tuned_L0` on Y2 excludes zero above **and** `mono_all` does
not beat `tuned_L0` on Y2 — i.e. both halves of C1+C2 reproduce on a family the ladder has never seen.
**Result.** `tuned_X2 − tuned_L0` on the unseen sibling Y2 is **+1.21 [−0.81, +3.22]** — refuted on
the rule as written. The arm is alive (X2 diagonal +2.97 [+1.04, +5.06]); the failure is **power**:
Y2 costs `tuned_L0` only 3.8 pts where X1 costs 15.8, so there were ~1.2 pts of signal against a
±2-pt interval. C2's scope narrows to families that badly damage a clean-code adapter. **A hard
second family is still the most valuable experiment available** — see E5b.
[`log/transfer/2026-09-07_second-family-pair-is-null.md`](../log/transfer/2026-09-07_second-family-pair-is-null.md)

### E5b. A *hard* second family pair — the generality test, redone with power
**Question.** E5's family was too gentle to test C2. Redo it with a family that destroys surface
information rather than rerouting control flow, so a clean-code adapter loses ≳10 points on it.
**Candidates.** Numeric-base re-encoding of every literal with computed reconstruction; or
identifier-to-computed-attribute indirection (names resolved through a dict built at import).
**Gate before training (the check E5 skipped).** Build the held-out sibling first, evaluate
`tuned_L0` on it, and proceed **only if** the drop from `L0` exceeds 10 pts — the power estimate
must come from the sibling's difficulty, not from hope.
**Cost.** generator ~1 CPU-day; then ~1.5 GPU-h.

**STATUS 2026-09-08 — specified, deliberately NOT run, and the specification above is now wrong.**
E6 landed between the writing of this entry and this note, and it changes what E5b has to be. E5b as
written asks for a second pair built the way X2/Y2 were: **same mechanism, different surface**. E6
tested exactly that relation *inside* X1 and refuted it — `tuned_X1m` reaches X1s at +1.49
[−0.95, +3.93] and `tuned_X1s` reaches X1m at −0.10 [−2.38, +2.19], i.e. two halves of one family
that share the "read a helper defined at the top of the module and evaluate it" schema do **not**
transfer to each other. A harder X2/Y2 would therefore be predicted to come back null *whatever* its
difficulty, and a null would be uninterpretable: it would confirm E6 rather than test C2.

What C2 actually needs after E6 is a pair that isolates the thing that *did* transfer. X1 → H1 is
lossless (0.08 pts) across genuinely different surfaces — different helper names, different
identities, a different encoding scheme — while X1m → X1s fails across a *shared* surface. So the
unit is neither "the surface" nor "the mechanism" as those were operationalised; the candidate that
survives both observations is **the reading operation the transform forces** (X1 and H1 both force
"evaluate a locally-defined decoder to recover a literal"; MBA and string encoding force different
ones). The redone E5b must vary *that*, holding damage constant:

  * **X3 / Y3** share one forced reading operation and differ in every surface detail — the X1 → H1
    relation reproduced in a domain that is neither encoding nor arithmetic (the strongest candidate
    is comparison/ordering: every `<`, `<=`, `==` routed through a helper that recomputes the
    relation, X3 by sign-of-difference, Y3 by a `sorted`-based lookup).
  * **Damage gate, unchanged and non-negotiable:** build Y3 first, evaluate `tuned_L0` on it, and
    proceed only if the drop from `L0` exceeds 10 pts. E5's null was a power failure and repeating it
    would be a waste of the corpus as well as the GPU.
  * **Pre-register before the generator is written**, so "which pair counts" cannot be chosen after
    seeing which one damages more.

This is a design problem, not an execution problem, and a generator shipped in haste writes a corpus
that costs CPU-days to regenerate and can silently corrupt a headline claim. It is specified here and
left unrun on purpose; `log/transfer/2026-09-08_e5b-redesigned-not-run.md` records the reasoning.

### E6. Which half of X1 does the work? — mechanism ablation
**Question.** X1 is string-encoding **+** MBA arithmetic. Which half buys the H1/X1 transfer?
**Arms.** `X1-str` (encoding only) and `X1-mba` (arithmetic only) as separate conditions; train a
specialist on each; cross-evaluate on full X1.
**Why.** Gives C2 a *within-family* resolution — "the family" is currently an unanalysed unit, and
this is the cheapest way to say what a family is.
**Cost.** generator ~half a day CPU; 2 × 22 min training + eval ≈ **1.5 GPU-h**.

---

## 3. Tier 2 — run if the schedule allows; each pre-empts a specific reviewer objection

### E7. Statistical hardening — GLMM + FDR — **FDR DONE 2026-09-08 (twice); GLMM still owed**
CLAUDE.md §4 specifies item-level binomial GLMMs with crossed random effects for program × model and
**BH-FDR across the transfer matrix as one family**. The paper currently has cluster bootstraps and
**no multiplicity correction**, across a matrix of dozens of arms. Two routes: rebuild the R stack
(blocked, §5) **or** implement in Python (`statsmodels` binomial GLM with cluster-robust SEs, plus a
BH pass over the matrix) — the latter is not blocked and is a day of CPU work. **Do the Python route
regardless**; a reviewer asking "how many comparisons?" needs an answer that exists.
**Read (`an_fdr` 382559, `an_fdr2` 383162).** Bootstrap-p + BH, labelled as a substitute for the GLMM
(lme4/statsmodels absent). Pre-registered families: transfer **1/30** survives (`tuned_S2` on S2,
q = 0.030 — the specialist matrix does not survive multiplicity), arms **8/28** including the headline
`mono_all` on X1 −3.79 (q = 0.017). Enlarged 7× as a robustness check: **203 tests, 69 survive, none
of the eight lost**; `mono_all` on X1 comes back at **q = 0.014**. Composites 10/12 (RQ-B 6/6, RQ-A
4/6). Both primary families reproduce byte-identically. **Gap stated, not closed:** every family is
controlled against `tuned_L0`, so RQ3′'s headline `cons_lam3 − mono_all` @ X1 is uncorrected; a
`mono_all`-controlled family is pre-registered for the next read rather than added on the spot.
**Read 3 (`an_fdr3` 383172, E7c).** The gap above, closed the only honest way — rule frozen in the
pre-registration (`8da96b4`) before `--control-family` existed as code. A `mono_all`-controlled family
of the same 203 tests: **`cons_lam3 − mono_all` @ X1 +4.86 [+2.88, +6.83], q = 0.0049**, and the same
at all three seeds and all four λ. 22 of 29 X1 cells survive; **0 of `cons_lam3`'s 6 non-X1 cells do**,
which is the shape the campaign claims. **Read 4 (`an_glmm` 383180, E7d) — the GLMM itself, no longer blocked.** `statsmodels` into a side
venv (the script re-execs itself there, so the pinned training env is untouched); per-condition
`correct ~ C(system) + (1|program_id) + (1|item_id)`, VB, 40,600 item-level rows. **4/4 headline
contrasts agree** with the bootstrap in sign and in exclusion of zero. Borderline contrasts the GLMM
resolves (breadth's L0 cost, −0.218 [−0.397, −0.040]) are reported and **not** promoted — uncorrected,
VB intervals are optimistically narrow, and the registered inference is the bootstrap. The remaining
shortfall is stated: crossed program × item within one base model rather than program × model, and a
Python VB fit rather than the R REML fit the charter named. `log/writeup/2026-09-08_glmm-agrees.md`. `log/writeup/2026-09-08_fdr-family-enlarged.md`,
`log/writeup/2026-09-08_fdr-the-uncovered-headline.md`.

### E8. Cross-family replication of C5 — **DONE 2026-09-08, CONFIRMED**
**Read (`an_e8` 382552).** On Llama-3.1-8B `cons_lam3 − mono_all` on X1 **+3.46** [+1.65, +5.35], `cons_lam3 −
tuned_L0` on seen **+2.53** [+1.30, +3.73], L0 +0.00 [−1.56, +1.56], X1 +0.58; best or tied-best arm on all
seven columns. Breadth's fingerprint (L0 −2.22*, X1 −2.88*) replicates too. `log/transfer/2026-09-08_consistency-replicates-on-llama.md`.

`cons_lam3` on **Llama-3.1-8B**, whose `base`/`tuned_L0`/`mono_all` already exist and whose breadth
fingerprint already replicates (−2.22 / +2.83). Shows the objective is not a CodeLlama artefact.
**Cost.** ~5 h + eval ≈ **6 GPU-h**.

### E9. Finish RQ3 (C7)
Outstanding per `log/attention/README.md`: a **generate-mode** confirmation of the steering result,
and the **length-matched control** (S1/S2 inflate code length, so an attention shift could be a
length effect). The H1 attention read is now impossible — say so and use X1.
**Cost.** attention extraction is HF-eager on a stratified subset; ~4 GPU-h.

### E10. Human alignment (C8) — decide: run or cut
`data/human/paper2_graded.csv` (98 item-level cells) and `paper3_graded.csv` are on disk and the
thread has never started. Either run the item-level ρ comparison (analysis-only on existing model
cells, ~1 CPU-day, no GPU) or **remove human alignment from the framing**. Do not leave it as a
stated RQ with no result.

### E11. H-L0-cost-source — analysis only — **classification DONE 2026-09-08; stratification still open**
§22.6: the `L1b` gain is located, the `L0` cost is not. Testable on **existing cells**: does the cost
concentrate on unusual answer formats, or on long programs? No new compute. Worth it because the
fingerprint is a recurring character in the paper and half of it is unexplained.
**Read (`an_l0cost` 382560).** 60 arms vs `tuned_L0` on L0, TOST ±1.0: 21 pay a certified cost, 0 gain,
1 L0-free (a seed twin), 38 underpowered — a 557-program cell gives ±1.5–2 pt CIs, so ±1.0 equivalence
is unreachable for any genuinely different arm. Ordering: consistency (−0.1 … −1.0) < breadth (−1.1 …
−1.7) < X1-family (−1.6 … −4.3) < alignment/negatives < TIES merges ≪ `cons_tbase` −12.0, `base` −17.0.
**Read 2 (`an_l0strat` 383161).** The stratification: **neither, and the format half is backwards**.
`mono_all` (3 seeds) loses on the **common** answer types (−2.38 [−3.94, −0.78]) and not at all on the
unusual tail (+2.32) — difference **+4.70** [+0.44, +8.89] — and its whole cost sits on **short**
answers (−4.16) with none on long ones (+0.30). Program LOC −2.00 [−5.87, +2.20], inconclusive, but
`base` localizes on length in the same strata (−7.36 [−13.67, −1.13]) so the null is a bound rather
than an instrument failure. Both frozen verdicts are INCONCLUSIVE (the rule was one-sided) and are
**not** re-specified. Confound stated: unusual format and easy item are the same stratum here.
**Read 3 (`an_l0strat2` 383173, E11c).** The confound broken: matched on the control's own per-item
difficulty the format contrast is **+10.21** [+5.34, +15.14] against +4.70 unmatched, positive in all
three bins — **CONFIRMED-REVERSED** under a two-sided rule. Easiness was diluting the effect, not
producing it. E11 is now fully answered.
`log/transfer/2026-09-08_l0-cost-classified.md`, `log/transfer/2026-09-08_where-the-l0-cost-lands.md`,
`log/transfer/2026-09-08_l0-cost-format-matched.md`.

---

## 4. Tier 3 — nice to have, cut without regret

- **E12. H-saturation** (§22.3): `train_size` sweep at 50 % / 25 %. ~7 GPU-h. **DONE 2026-09-08** —
  more interesting than the reviewer-defence it was planned as: H-sat-mono CONFIRMED (`mono_half − mono_all`
  +0.01 equiv), H-sat-L0 REFUTED (clean-only −1.05* at half, −2.71* at quarter), **H-tax-scales CONFIRMED**
  — the X1 tax is −0.49 → −2.31* → −3.79* across quarter/half/full, and `mono_quarter` beats `mono_all` on
  X1 by +3.29 [+1.32, +5.35]. Breadth overfits the seen set as a function of volume.
  `log/transfer/2026-09-08_saturation-the-tax-grows-with-data.md`.
- **E13. H-mixture** (§19.4): is the +0.205 mixture gain capacity or ensembling?
- **E14. H-peaked-breadth** (§22.1): any-of-8 for `merge_dare_ties` and the uniform MoLE mixture.
- **E16. RQ5′ — the bidirectional stress test** (added 2026-09-08 at the user's request; **done 2026-09-08**
  — jobs 382620/382621 → 382622: **H-inv-transfer REFUTED** — `tuned_L0` +18.09 forward, −1.67 [−3.29, −0.04] backwards; `cons_lam3` +0.49 vs base (no harm), `mono_all` −1.30; **H-inv-family CONFIRMED**, `tuned_X1` +3.37 over base on X1-inverse, the only above-base transfer, q = 0.005; diagonal 3/5 by rule but S2 −3.7 vs base. Unregistered: `tuned_L1b` best inverse arm on all 7 conditions. `log/transfer/2026-09-08_bidirectional-inverse-task-read.md`). Every adapter was trained on program + call → value; ask the same
  held-out items backwards (program + value → a call that returns it, CRUXEval-I style), graded by
  **execution**, for 11 forward-trained arms on 7 conditions (no H1). A `formatonly` control and a
  25 % format gate separate answer-format adaptation from reasoning. Pre-registered: H-inv-transfer
  (`tuned_L0` clears both `base` and `formatonly`), H-inv-breadth, H-inv-cons, H-inv-family,
  H-inv-diagonal, plus a descriptive direction ratio. A null replicates ATTRIB's "cognitive
  specialization" at value level; a positive bounds it. ~6 GPU-h. `docs/RQ_SUMMARY.md` §6.3.

- **E15. The canary guard** (§21.1): re-evaluate one adapter per eval job and assert ≥95 % raw-output
  agreement. Not a paper result — an infrastructure guard that would have caught the prefix-cache
  collision. Cheap; do it if any large eval batch is still to come.

---

## 5. Blocked on infrastructure — needs an admin, not a GPU

| blocker | what it blocks | consequence for the paper |
|---|---|---|
| **`node` not installed** | the entire JavaScript ladder, the H1/JS generator, cross-language transfer (**H1b**) | the paper is **single-language**. This must be a *declared scope decision* in the limitations section, not silence. The frozen Qwen JS panel cannot substitute: CLAUDE.md §3.1 records that legacy JS `L2`/`L3` rows contain H1-family features and are never usable in an unseen-transform claim |
| **`r_analysis` env did not migrate** | the GLMM stack in `stats/` | E7's Python route removes this from the critical path |

Both are worth requesting now: neither is queue-bound, and `node` is the only thing standing between
this paper and the bilingual design the project was chartered around.

---

## 6. Suggested order

**Superseded 2026-09-07 by the autonomous pipeline.** Everything below that is not struck through
is now a stage in `scripts/pipeline/plan.yaml` (`python scripts/pipeline/run.py --status`), with
dependencies expressed as SLURM `afterok` chains and the decision rules frozen in
`CLAUDE_SCRATCHPAD.md` before submission. The mapping:

| experiment | pipeline stages | status |
|---|---|---|
| E3 | `an_e3` (chains 381340/382139/382140 at 13B; 381405/382141/382142 at 34B) → 382542 | **done 2026-09-08**: H-E3 + H-E3-tax CONFIRMED at both scales |
| E4 | `tr_cons_tbase`, `tr_cons_tmono` → `ck_*` → `ev_teacher` → `an_e4` | **done 2026-09-08** (382548): H-E4-view REFUTED, H-E4-teacher CONFIRMED, H-E4-mono REFUTED — the tuned clean-code teacher is the ingredient |
| E5b | `e5b_hard_family` | **disabled** — respecified 2026-09-08 after E6 changed its requirement; generator deliberately not written (see E5b) |
| E6 | `bld_x1split` → `emit_x1split_*` → `tr_X1m`, `tr_X1s` (382803, 4,096 window) → `ck_*` → `ev_x1split` → `an_x1split` (382806) | **done 2026-09-08**: H-family-unit REFUTED, H-whole-ge-parts CONFIRMED; either half ≈ 90 % of the whole on X1 |
| E7 | `an_fdr` + `an_fdr2` + `an_fdr3` + `an_glmm` | **FDR done 2026-09-08** (382559, 383162, 383172): transfer 1/30, arms 8/28, enlarged family 69/203 with none of the eight lost, `mono_all`-controlled family closes the headline at q = 0.0049. GLMM unblocked via a side venv and running (383180) |
| E8 | `tr_cons_llama` → `ck_cons_llama` → `ev_llama` → `an_e8` (382549–382552) | **done 2026-09-08**: H-E8 / H-E8-seen / H-E8-tax all CONFIRMED |
| E9 | `ko_x1_{base,tuned_L0,mono_all,cons_lam3,tuned_X1}` → `an_attention` | scheduled |
| E10 | `47_emit_icse_items.py` → `ev_human_align_{py,js}` → `48_human_align.py` | **done 2026-09-08** (383195/383200): **H-human-shift AWAY** (Δρ −0.303 [−0.575, −0.028]); H-human-base INCONCLUSIVE; condition level `base` +0.82 against every tuned arm negative |
| E13 | `tr_js_L0` → `ck_js_L0` → `tr_js_{mono,cons}` → `ck_*` → `ev_crosslang_js` → `an_crosslang` | **done 2026-09-08** (383164–383171): `cons_lam3` best on all 12 columns (+7.35 seen, +4.91 over breadth on composites, +3.37 on L0); **breadth's stacking gain does NOT replicate** (+2.55 [−0.30, +5.31], three of six composites negative); no unseen-family column |
| E11 | `an_l0cost` → `an_l0strat` | **done 2026-09-08** (382560, 383161): 21 pay / 0 gain / 38 underpowered at ±1.0; the cost lands on **common** formats and **short** answers, the reversal of the hypothesis (+4.70 [+0.44, +8.89]) |
| E12 | `tr_{L0,mono}_{half,quarter}` → `ck_*` → `ev_saturation` → `an_saturation` | **done 2026-09-08** (382531 → 382532): H-tax-scales CONFIRMED, the X1 tax grows with data volume |
| RQ-A/B at scale | `ev_composite_13b/34b` → `an_composite_*` | **done 2026-09-08** (13B 382514 → 382515; 34B 382516 → 382518): RQ-A/RQ-B CONFIRMED at both; H-cons-stack-strict CONFIRMED at 13B (+1.36) and 34B (+2.58) |
| RQ-C depth | `bld_depth` → `emit_depth_items` → `ev_depth` → `an_depth` | scheduled |
| E16 / RQ5′ | `ev_inverse_core`, `ev_inverse_specialists` → `an_inverse` (`42_inverse.py`) | **done 2026-09-08** (382620/382621 → 382622): H-inv-transfer REFUTED; family holds; `results/analysis/pipeline/inverse_codellama7b.json` |
| report | `report` (`afterany` on every `an_*`) → `results/analysis/pipeline_report_<date>.md` | scheduled |

Requested GPU walltime ≈ 45 h across 47 stages; the plan is idempotent (`done_when` files), so a
failed stage is fixed and resubmitted with `run.py --only <stage>` without touching the rest.

Original ordering, kept for the record:

1. ~~E1 + E2~~ — **done 2026-09-07, both CONFIRMED** in ~12 min of GPU.
2. **E5 generator** (CPU, no queue) in parallel with **E3** (the long 34B run) on the GPU.
3. **E4**, **E6** — both short, both sharpen a mechanism claim.
4. **E7** (Python GLMM+FDR) as CPU work throughout.
5. **E10 decision** — run or cut, but decide before the framing is written.
6. Tier 2 as schedule allows; Tier 3 only on reviewer demand.

**Total Tier 1 remaining (E3–E6): ≈ 32 GPU-hours** plus ~1.5 CPU-days of generator work. At current `h200` queue
behaviour that is roughly a week of submit-and-return-tomorrow, not a month.

**Pre-registration.** Every experiment above with a decision rule gets that rule committed to
`CLAUDE_SCRATCHPAD.md` **before submission**, per the practice that has held since 2026-09-02. E5 in
particular defines a new held-out sibling: it must be registered with the same discipline H1 had, or
it inherits none of H1's credibility.

## 7. Experiments for the RQ1–RQ4 paper plan (added 2026-09-09)

[`PAPER_FRAMING.md`](PAPER_FRAMING.md) re-cut the paper around four RQs — composition (RQ1), what is
learned (RQ2), anchoring (RQ3), robustness (RQ4) — and marked which stated findings the record does
not yet support. These are the experiments that close those gaps, numbered **F1–F9** so they do not
collide with E1–E16 above. Costs are from measured rates on this cluster: 7B eval ≈ 18 s/cell via vLLM
multi-LoRA (535 s for 30 composite cells, job 382427), MoLE eval through the HF path (slower; budget
2× the vLLM rate), 7B consistency arm 4.4 h, composite build 2.5 min CPU for four conditions. Decision
rules go into `CLAUDE_SCRATCHPAD.md` **before** each submission, as every read since 2026-09-02 has;
every contrast is a program-clustered bootstrap (2,000 resamples, seed 17). **No stage reads H1, and
H1 is never stacked** — every unseen component below is X1 (or its halves X1m/X1s), the calibrated
proxy.

### Priority table

| # | RQ leg it closes | what runs | new training? | GPU | CPU |
|---|---|---|---|---|---|
| **F2** | RQ1 divergence gradient · RQ4 unseen-in-stack | build 6 composites containing X1/X1m/X1s; evaluate 10 systems | none | ~1.5 h | ~0.5 h |
| **F1** | RQ1 routing + merging on stacks | 4 MoLE arms, 5 merges, 3 specialists on the 10 existing composites; router decision dump | none | ~2 h | — |
| **F3** | RQ2 "stacking destroys the cue" | analysis over F1's specialist cells + cue-survival regex; **F3a** closes H-stack-identifier from existing JSON | none | — | ~2 h |
| **F4** | RQ3 compute-matched control | `cons_lam0` (paired SFT, λ = 0) at 7B; 3 seeds if the first clears | 3 × 4.4 h | ~14 h | — |
| **F5** | RQ4 surface-perturbation | X1 + two X1 composites rebuilt at obfuscation seeds 101/202/303; 6 systems | none | ~1 h | ~1 h |
| **F1b** | RQ1 merging mechanism | task-vector geometry on CodeLlama-7b, cross-seed and same-seed banks | none | — | ~1 h |
| **F7** | RQ4 reverse task at scale | inverse eval for base/`tuned_L0`/`mono_all`/`cons_lam3` at 13B and 34B | none | ~2.5 h | — |
| **F8** | seed band at 13B for RQ3 | `cons_lam3_s42`, `mono_all_s42` at 13B | 2 × ~6 h | ~13 h | — |
| **F6** | RQ2/RQ4 second hard family (= E5b) | X3/Y3 generator, damage gate, `tuned_X3` | 1 × 22 min | ~1.5 h | ~1 day |

**Order.** F2 first — it is the cheapest experiment and the one both RQ1's last sentence and RQ4's
headline depend on. F1 second (eval-only). F3/F3a/F1b are CPU work that runs while GPU jobs queue.
F4 is the one new training arm the paper cannot go out without. F5, F7, F8 harden; F6 stays
design-gated. Total: **~22 GPU-h without F8/F6, ~37 GPU-h with** — a week of submit-and-return at
current `h200` queue behaviour.

### F1. Routing and merging on stacked inputs — the RQ1 legs that have never been measured on this panel
**Question.** The finding says inference-time routing and weight merging fail on stacks. On the
CodeLlama panel both were measured on single transforms only (router − random gate +0.0000; merges
−3.13 vs specialists' +2.47); the only stacked reads are Qwen-1.5B on a 34/40-program subset that
`RQ_SUMMARY.md` §4.1 forbids ranking.
**Arms** (all exist; eval-only), on the 6 depth-2 composites (`composite_generic` items) and the 4
depth-3/4 composites (`composite_depth` items, `--common` subset):
- MoLE: `mole_router`, `mole_hardrouter`, `mole_random`, `mole_uniform` (gate checkpoint
  `runs/mole/codellama-7b/python/routerlora_codellama7b_s17/gate.pt`, experts as in
  `configs/eval/mole_ladder_codellama-7b.yaml`) — a new `configs/eval/mole_composite_codellama-7b.yaml`
  with `eval_conditions` set to the ten composites. **Also dump the gate's per-item expert
  distribution** (argmax expert, entropy) — the finding's mechanism ("matches no single distribution")
  is a claim about what the router *does*, and on singles it is at 100 % route accuracy with entropy
  ~1e-6; on a stack it must either pick one part or spread.
- Merges: `merge_ties`, `merge_dare_ties`, `merge_dare_linear`, `l0merge_ties`, `l0merge_dare_ties`
  (`runs/adapters/codellama-7b/python/*merge*`) — add to a `composite_generic`-style config.
- Specialists for F3: `tuned_L1r`, `tuned_S1`, `tuned_L1b` (`tuned_S2` already has composite cells).
Controls `base`, `tuned_L0`, `mono_all`, `cons_lam3` exist on every composite.
**Decision rules (to pre-register).**
- **H-F1-route** — routing adds nothing on stacks: CONFIRMED iff `mole_router − mole_random` pooled
  over the ten composites is TOST-equivalent at ±1.0; REFUTED iff ci_lo > +1.0.
- **H-F1-route-vs-breadth** — a router over specialists does not reach breadth on stacks: CONFIRMED
  iff `mole_router − mono_all` pooled ci_hi < 0.
- **H-F1-merge** — merging is at or below the clean-code control on stacks: CONFIRMED iff
  `merge_dare_ties − tuned_L0` pooled ci_hi ≤ 0 (report all five merges; the l0merge rows are the
  "is it the merge or the specialists" control, as on singles).
- **H-F1-router-behaviour** (descriptive): on `C_L1r_S1` vs `C_S1_L1r`, fraction of items routed to
  an identifier expert vs a structural expert, and mean gate entropy vs the singles' ~1e-6.
**Cost.** ~12 systems × 10 composites = 120 cells; ~40 min vLLM + MoLE via HF ≈ **2 GPU-h**. New
config only; `35_composites.py --systems …` reads the result.

### F1b. Task-vector geometry on CodeLlama, cross-seed — reported, gates nothing
**Question.** The finding attributes merging's failure to "contrasting task-vector geometries". On
Qwen that was refuted (`REPORT_2026-08-17` §3: same-data different-seed adapters are near-orthogonal
at sign conflict 0.487 and merge fine). CodeLlama has the banks to repeat it — `L0` at s17/s42/s101,
six specialists at s17 and s42.
**What runs.** The existing geometry script with `--seeds`: pairwise cosine, sign conflict, TIES
keep fraction, ‖ΔW‖ for (a) `L0` cross-seed, (b) specialists same-seed, (c) specialists cross-seed.
CPU only, ~1 h.
**Use.** If CodeLlama reproduces Qwen, the paper reports merging's failure *without* the
interference mechanism and cites this as the reason. If it does not, that is a result.

### F2. The divergence ladder — stacks that contain an unseen family
**Question.** RQ1's last sentence ("failures worsen as the stack diverges from training") and RQ4's
"stacks containing unseen transformation families" both need stacks with an unseen component. None
exists. X1 is trainable and `obf/builder.py::load_composite_transform` chains arbitrary `parts`, so
this is a composite build plus an eval — **H1 is never a part**.
**New composites** (`configs/conditions_composite.yaml`, own namespace, `size_cap` calibrated on real
programs before the full build as the file's header requires):

| code | parts | divergence level |
|---|---|---|
| `C_L1r_X1` | L1r → X1 | d2: one unseen, depth 2, identifier + encoding |
| `C_X1_S1` | X1 → S1 | d2: one unseen, depth 2, encoding + structural |
| `C_S2_X1` | S2 → X1 | d2: one unseen, depth 2, inert material + encoding |
| `C_L1r_X1m` | L1r → X1m | d2 with a *single-mechanism* unseen half (MBA) |
| `C_S1_X1s` | S1 → X1s | d2 with the string half |
| `C3_L1r_S1_X1` | L1r → S1 → X1 | d3: one unseen, depth 3 |

Existing levels: **d0** = the six depth-2 seen composites; **d1** = depth-3/4 seen; **d4** = X1
alone (itself two mechanisms, E6) and X1m/X1s. Coverage will shrink (X1 needs ≥ 3 sites → 405
programs; S1 bails on some) — record the common subset **before** any read and run every contrast
on it.
**Systems** (all exist): `base`, `tuned_L0`, `mono_all`, `cons_lam3`, `tuned_X1`, `mono_allX`
(breadth + family), `tuned_S2`, `mole_router`, `merge_dare_ties`, `x1_resample`.
**Decision rules (to pre-register).**
- **H-F2-breadth-monotone** — breadth's advantage falls with divergence: CONFIRMED iff
  `mono_all − tuned_L0` has ci_lo > 0 at d0 (known) **and** ci_hi < 0 at d2 (pooled over the three
  full-X1 stacks) — i.e. the sign flips once an unseen component enters; INCONCLUSIVE if d2 straddles.
  The d3 point is reported; a "worsens further" reading needs d3 ci_hi below the d2 point.
- **H-F2-cons-no-tax** — anchoring pays no tax at any level: CONFIRMED iff `cons_lam3 − tuned_L0`
  ci_hi ≥ 0 at d2 and d3.
- **H-F2-cons-vs-breadth** — anchoring beats breadth where the two behaviours collide: CONFIRMED iff
  `cons_lam3 − mono_all` ci_lo > 0 pooled at d2.
- **H-F2-family-stacks** — family exposure survives stacking with seen transforms: CONFIRMED iff
  `tuned_X1 − tuned_L0` ci_lo > 0 pooled at d2; `mono_allX − mono_all` reported beside it.
- **H-F2-route / H-F2-merge** — as F1's rules, on the d2 stacks.
**This is the experiment RQ4 is decided by.** If `cons_lam3` holds `tuned_L0`'s level on d2/d3 while
`mono_all` drops below it, the paper's Fig 1 exists; if `cons_lam3` drops with breadth, RQ4's answer
is "a better heuristic, not robustness" and is reported that way.
**Cost.** build ~10 min CPU (`05_build_variants.py --target train --conditions … --conditions-config
conditions_composite.yaml`; then `07_emit_eval_items.py --source heldout`); eval 10 × 6 = 60 cells ≈
20 min + MoLE ≈ **1.5 GPU-h**. Analysis: `35_composites.py` with a `--composites` list per level.

### F3. Cue destruction — the causal link from RQ2 to RQ1
**Question.** RQ2 claims stacking fails *because* it destroys the single-transform cue. The order pair
`C_L1r_S1` / `C_S1_L1r` is the built-in test: S1 emits `_st_` state variables and renaming them second
(`C_S1_L1r`) removes the surface cue an S1 specialist keys on, while `C_L1r_S1` keeps it. No specialist
has composite cells on CodeLlama; F1 supplies them.
**Analysis** (CPU, on F1's cells):
- **H-F3-order** — the S1 specialist's gain survives when its cue survives and not otherwise:
  CONFIRMED iff [`tuned_S1 − tuned_L0` on `C_L1r_S1`] − [same on `C_S1_L1r`] has ci_lo > 0 (paired by
  program).
- **H-F3-cue-items** — item-level: regex the composite source for surviving `_st_` names (S1 cue) and
  for L1b's misleading-name markers; CONFIRMED iff the specialist's per-item gain is larger on
  cue-present items (bootstrap on the difference). Analysis of existing trials + F1; no GPU.
- **H-F3-retention** (descriptive): for each specialist, fraction of its diagonal gain retained on
  composites containing its transform, by depth.
**F3a — close H-stack-identifier from existing JSON.** `composite_depth_codellama7b.json` already has
the structural-only depth-3 stack `C3_S1_S3_S4`: `mono_all − tuned_L0` **+1.61** [−1.02, +4.31], n.s.,
against +6.10* on `C3_L1r_S1_S4` and +5.17* on the depth-4 stack. The rule as opened 09-07 ("CONFIRM
if structural-only stacks show no breadth gain at depth 3") is met; write the read and move the
hypothesis to resolved. No compute.

### F4. Compute-matched control for anchoring — is it the KL or the second view?
**Question.** `cons_lam3` sees two views per row (the obfuscated input and the clean parent through
the teacher). Nothing has matched that budget without the KL term, so "gains stem from the clean-code
anchor" has a teacher ablation (E4) and a view ablation (`cons_same`) but no *data-exposure* control.
**Arm.** `cons_lam0`: the consistency pipeline with `objective.lam: 0.0` — paired SFT over both views,
no KL — 7B, r32, s17 (`configs/train/obj_cons_codellama7b_py.yaml` with `lam: 0.0`; confirm the
trainer does not short-circuit λ = 0 into plain SFT before submitting). If the first seed clears the
rule, s42/s101 for the band.
**Decision rule.** **H-F4-kl** — the KL term, not the data exposure, is the ingredient: CONFIRMED iff
`cons_lam3 − cons_lam0` @ X1 ci_lo > 0 **and** `cons_lam0 − mono_all` @ X1 ci_hi ≤ +1.0 (paired SFT
alone does not remove breadth's tax). Also report `cons_lam0 − tuned_L0` @ L0 (does the second view
alone protect clean code?).
**Cost.** 4.4 h + ~5 min eval per seed → **~14 GPU-h** for three seeds.

### F5. Surface perturbation — is anchoring's unseen-family level a new surface heuristic?
**Question.** RQ4 asks whether the model learned a *new* surface cue. X1 has one canonical surface;
`x1_resample` proved the transform can be rebuilt at other obfuscation seeds (three surfaces exist
as *training* data, `05_build_variants.py --seed <s> --aug-tag <tag>`). No arm has been *evaluated* on
a resampled surface.
**What runs.** Build held-out items for X1, `C_L1r_X1` and `C_X1_S1` at seeds 101/202/303; evaluate
`base`, `tuned_L0`, `mono_all`, `cons_lam3`, `tuned_X1`, `x1_resample` (6 × 9 = 54 cells).
**Decision rules.** **H-F5-stability** — anchoring's X1 level does not depend on the surface:
CONFIRMED iff `cons_lam3` at each resampled seed is TOST-equivalent (±1.5) to its canonical X1 cell,
paired by program. **H-F5-specialist-fragile** (descriptive): the seed-to-seed range for `tuned_X1`
vs `x1_resample` vs `cons_lam3` — a surface heuristic shows as range, not level.
**Cost.** ~1 h CPU build, ~20 min eval → **~1 GPU-h**.

### F6. A hard second family (= E5b, unchanged) — design-gated
The specification in E5b stands: X3/Y3 sharing one forced reading operation (comparison/ordering
routed through a helper), Y3 built first, `tuned_L0` must lose > 10 pts on it before anything is
trained, pre-registered before the generator is written. With F2 in place it gains a second use: a
`C_L1r_Y3` stack is the unseen-in-stack test on a family that is *not* X1's. ~1 CPU-day + 1.5 GPU-h.

### F7. The reverse task at 13B and 34B
**Question.** RQ4's reverse-task leg is 7B only, and the honest result is "undamaged" (`cons_lam3 −
base` +0.49 [−1.38, +2.30]), not "consistent". Two more scales make it a statement about the
objective rather than a model.
**What runs.** `inverse_generic` for `base`, `tuned_L0`, `mono_all`, `cons_lam3` at 13B and 34B
(adapters exist; 7 conditions × 4 arms × 2 scales = 56 cells; the inverse task caps at 128 tokens so
34B is ~45 min).
**Decision rules.** **H-F7-no-harm** — CONFIRMED iff `cons_lam3 − base` @ seen6 ci_hi ≥ 0 at both
scales; **H-F7-vs-sft** — CONFIRMED iff `cons_lam3 − tuned_L0` @ obf ci_lo > 0 at both. Report DR.
**Cost.** ~**2.5 GPU-h**.

### F8. Second seed at 13B
`cons_lam3_s42` and `mono_all_s42` at 13B (6.5 h + 5.2 h). Turns the 13B column of RQ3 from one draw
into a band. Rule: `cons_lam3 − mono_all` @ X1 ci_lo > 0 at s42 (H-E3 at a second seed).
**~13 GPU-h**; run only after F2/F1/F4 are queued.

### F9. Analysis-only closures (no compute)
- Depth-3 structural-only breadth gain → H-stack-identifier resolved (F3a).
- Per-composite `cons_lam3 − mono_all` on the depth-3/4 stacks from `composite_depth_codellama7b.json`,
  to state whether the depth-4 stack's +7.20 over `tuned_L0` is also a gain over breadth.
- Item-level "weakest-link vs surface" split on the X1 trials (E6's open question): under a weakest-link
  gain the items `tuned_X1m` newly solves are those where the MBA guard precedes the encoded string.

### F10. Panel extension — three lineages × {code, general} + one pretrained checkpoint
**Question.** Every headline is Meta-lineage (CodeLlama ×3, Llama-3.1-8B). §1–§3 of
[`MODEL_AND_DATA_SELECTION.md`](MODEL_AND_DATA_SELECTION.md) fix the panel; **all five were adopted
on 2026-09-09** and are in `configs/models.yaml`: `starcoder2-15b` (BigCode), `gemma3-12b`,
`llama31-8b-base` (pretrained — the base-vs-instruct axis), `codegemma-7b`, `granite31-8b`.
Priority in that order. Note §2a of that document: three of the five needed a prompt-rendering
adaptation before they could be trained at all.
**What runs per model.** The gate (§3 of that doc, ~10 min), then the core arms `tuned_L0`,
`tuned_X1`, `mono_all`, `cons_lam3` (teacher = the model's own `tuned_L0`), evaluated on the six
ladder conditions, X1, the six depth-2 composites and F2's unseen-in-stack composites.
**Decision rules (per model, to pre-register).** **H-F10-dissociation** — `mono_all − tuned_L0`
ci_lo > 0 on stacked-seen AND ci_hi < 0 on X1. **H-F10-repair** — `cons_lam3 − mono_all` @ X1 ci_lo > 0
AND `cons_lam3 − tuned_L0` @ L0 ci_hi ≥ 0. **H-F10-base-vs-instruct** (pretrained Llama-3.1 vs its
instruct twin, descriptive + E10 re-run): does the human-divergence Δρ have the same sign on a
checkpoint that never saw instruction data?
**Cost.** ≈ 9.5 GPU-h per 7–9B model, ≈ 17 per 12–15B; five models ≈ **60 GPU-h**; the three-model
minimum ≈ **43 GPU-h**.

### F11. Dataset additions — evaluation-only columns, training corpus untouched
From §4–§5 of `MODEL_AND_DATA_SELECTION.md`: **D1** length-stratified reads of every headline
(analysis only); **D2** user-space `node` (x86_64, glibc 2.34 — the official tarball runs without
admin) → JS ladder + JS X1 regenerated; **D3** LiveCodeBench post-cutoff slice (≥ 2025-01, ≥ 300
programs after the execution gate) as an eval-only contamination control; **D4** an off-the-shelf
obfuscator column (`python-minifier`; `javascript-obfuscator` after D2); **D5** a CSN long slice
(`loc_max` 120), eval-only. Each new column inherits X1's own-namespace rule.
**Decision rules.** D3/D5: the headline contrasts (H-F10-dissociation, H-F10-repair) reproduce on the
new column at 7B — CONFIRMED per contrast by the same ci rules. D4: classify the in-the-wild obfuscator
as seen-like or unseen-like by whether `mono_all − tuned_L0` on it has ci_lo > 0 or ci_hi < 0.
**Cost.** ~3 CPU-days of corpus work in total; ≈ 2 GPU-h per panel model of evaluation.

### Pre-registration
Every F-rule above is copied into `CLAUDE_SCRATCHPAD.md` and committed **before** the first F-job is
submitted, exactly as the pipeline's 47 stages were (`0286c5f`). F2 defines six new composites; they
inherit X1's own-namespace rule (any adapter that saw X1 is reported apart from the headline systems)
and, like X1, are never pooled with H1 or compared to it.

---

## Changelog
- **2026-09-09 (b)** — Scope: no Chinese-origin models. F10 (panel extension, five non-Chinese models
  across three lineages + a pretrained checkpoint) and F11 (evaluation-only dataset additions D1–D5) added.
- **2026-09-09 (RQ1–RQ4 plan)** — §7 added: experiments **F1–F9** for the four-RQ framing in
  `PAPER_FRAMING.md`. F2 (stacks containing the unseen family — the divergence ladder) and F1 (routing
  and merging on stacks, never measured on this panel) are the two the stated findings cannot go out
  without; F4 is the compute-matched control the anchoring claim lacks; F3a closes H-stack-identifier
  from existing cells. Nothing was run.
- **2026-09-08 (open-items wave)** — the six items left "open" or "blocked" were re-examined and four
  of them were not blocked at all. **`node` blocks regenerating the JavaScript corpus, not using it**,
  and the corpus transferred intact (2,022 train pairs / 504 heldout items per condition plus the six
  composites, passing the SHA manifests and the H1-marker scan), so E13 — a cross-language
  replication on CodeLlama-7b — is trained and queued. **E10's "missing" Paper-2 item map is on disk**
  (600 responses, 50 participants, 98 cells, all 98 matching a legacy row); the items only needed an
  emitter, `scripts/47_emit_icse_items.py`, and E10 is submitted. **The GLMM is not blocked**:
  `statsmodels` installs into a side venv so the pinned training env is untouched. E7c and E11c are
  read (above). Only **E5b** is genuinely unbuilt, and it is respecified rather than run because E6
  refuted the relation its planned design tested.
- **2026-09-08 (E7b / E11b reads)** — E7's BH-FDR re-run with the family enlarged 7× (arms_all 203 tests, composites 12): every claim the paper rests on survives, the two primary families reproduce byte-identically, and the uncorrected `cons_lam3 − mono_all` headline is recorded as a gap for the next pre-registration. E11's stratification done: the L0 cost is on common answer types and short answers, not the exotic tail. Master report rev 18 (§29) written.
- **2026-09-08 (E4 / composite_34b / E11 reads)** — E4: the tuned clean-code teacher is the ingredient, claim narrowed to teacher-distillation. 34B composites: RQ-A/RQ-B at three scales, H-cons-stack-strict closed. E11 classification: 21 pay / 0 gain / 38 underpowered; stratification remains. Every pipeline stage is now terminal and read.
- **2026-09-08 (E6 read)** — X1 split done: the halves do not transfer to each other, either half carries ~90 % of the stacked gain.
- **2026-09-08 (E8 read)** — E8 done: consistency replicates on Llama-3.1-8B (+3.46 over breadth on X1).
- **2026-09-08 (E3 read)** — E3 done: consistency survives scale (13B +3.95, 34B +3.38 over breadth on X1, no tax).
- **2026-09-08 (E12 read)** — saturation done: seen gain saturates by ¼ corpus, X1 tax grows with volume.
- **2026-09-08 (E16 read)** — E16 done: forward tuning does not transfer to the inverse task (−1.67 vs +18.09); only the X1-family adapter beats base backwards, on X1.
- **2026-09-08** — E16 (RQ5′, bidirectional / inverse-task stress test) added at the user's request and submitted; stage row in §6.

- **2026-09-07 (c)** — §6 superseded by the pipeline mapping table; E5b and E10 recorded as
  disabled stages with their reasons rather than left as open items. RQs revised to RQ1′–RQ4′
  (`RQ_SUMMARY.md` §6); this plan's experiments are the evidence for them, unchanged.
- **2026-09-07 (b)** — E1 and E2 run and **both CONFIRMED**; struck through with their results, C1's
  evidence row rewritten to two held-out columns / three scales / three seeds, and the Tier-1 total
  reduced to E3–E6. The X1↔H1 proxy gained a 34B validation that was not planned.
- **2026-09-07** — Created, after objectives round 2 closed and §26 was recomputed over 83 systems.
  Grounded in `MASTER_REPORT.md` rev 16; costs measured from `training_summary.json` across the
  existing adapter tree rather than estimated. Records the single-language scope decision and the
  two infrastructure blockers as explicit paper-level facts rather than open tasks.
