# Experiment plan for the paper

*Last updated: 2026-09-08*

**Working title claim:** *fine-tuning on obfuscated code teaches the transformation **family** it was
shown, not semantic invariance — and training on more families makes it worse on an unseen one.*

Scope assumed here: **Python only, CodeLlama-7b/13b/34b**, with Llama-3.1-8B as a cross-family
check. JavaScript is excluded by necessity (`node` is not installed on juno) and that exclusion is
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
| C8 | Tuning moves models toward/away from human difficulty orderings | none — thread never started, data on disk | **not started** — E10, or cut |

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
| E10 | `47_emit_icse_items.py` → `ev_human_align_{py,js}` → `an_human_align` | **submitted 2026-09-08** (383194/383195 → 383196): the map was never missing — 98/98 human cells matched; rules frozen in pre-registration #3 (`4665e17`) |
| E13 | `tr_js_L0` → `ck_js_L0` → `tr_js_{mono,cons}` → `ck_*` → `ev_crosslang_js` → `an_crosslang` | **submitted 2026-09-08** (383164–383171): cross-language replication on the intact JS corpus; seen + composites only, no unseen-family column |
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

---

## Changelog
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
