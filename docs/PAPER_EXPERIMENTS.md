# Experiment plan for the paper

*Last updated: 2026-09-07*

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

### E3. H-cons-scale — does the one positive result survive scale?
**Question.** C5 is a 7B result. If paired consistency is a small-model repair it is a much weaker
contribution than if it holds at 34B, where breadth's `L0` tax is larger (−2.63 [−4.49, −0.78]).
**Arms.** `cons_lam3` at **13B** and **34B**; controls (`tuned_L0`, `mono_all`) exist at both.
Evaluate on all seven conditions incl. X1.
**Decision rule (to be pre-registered before submission).** CONFIRM if `cons_lam3 − mono_all` on X1
excludes zero above at **both** scales; PARTIAL if one; REFUTE if neither.
**Cost.** 13B ≈ 6.5 h + 34B ≈ 12 h training, + ~1 h eval ≈ **20 GPU-h**.

### E4. H-cons-teacher — is it the *clean-code* teacher, or any teacher?
**Question.** C5's mechanism story is "distil from a model that saw clean code, on the clean parent".
Round 1 separated the *view* (parent vs same input, +0.94 pooled) and round 2 separated the *init*
(`currmono_kl`, −2.47 on X1). Nothing has varied the **teacher itself**.
**Arms.** `cons_lam3` with teacher = **untuned `base`** (does an untrained teacher work?) and with
teacher = **`mono_all`** (does a breadth teacher poison it?). 7B, seed 17.
**Why it matters.** If `base` works as well, the method is "distil from *some* view of the clean
parent" and is much easier to apply; if only `tuned_L0` works, the claim is narrower and must say so.
**Cost.** 2 × 4.4 h + eval ≈ **9.5 GPU-h**.

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

### E6. Which half of X1 does the work? — mechanism ablation
**Question.** X1 is string-encoding **+** MBA arithmetic. Which half buys the H1/X1 transfer?
**Arms.** `X1-str` (encoding only) and `X1-mba` (arithmetic only) as separate conditions; train a
specialist on each; cross-evaluate on full X1.
**Why.** Gives C2 a *within-family* resolution — "the family" is currently an unanalysed unit, and
this is the cheapest way to say what a family is.
**Cost.** generator ~half a day CPU; 2 × 22 min training + eval ≈ **1.5 GPU-h**.

---

## 3. Tier 2 — run if the schedule allows; each pre-empts a specific reviewer objection

### E7. Statistical hardening — GLMM + FDR
CLAUDE.md §4 specifies item-level binomial GLMMs with crossed random effects for program × model and
**BH-FDR across the transfer matrix as one family**. The paper currently has cluster bootstraps and
**no multiplicity correction**, across a matrix of dozens of arms. Two routes: rebuild the R stack
(blocked, §5) **or** implement in Python (`statsmodels` binomial GLM with cluster-robust SEs, plus a
BH pass over the matrix) — the latter is not blocked and is a day of CPU work. **Do the Python route
regardless**; a reviewer asking "how many comparisons?" needs an answer that exists.

### E8. Cross-family replication of C5
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

### E11. H-L0-cost-source — analysis only
§22.6: the `L1b` gain is located, the `L0` cost is not. Testable on **existing cells**: does the cost
concentrate on unusual answer formats, or on long programs? No new compute. Worth it because the
fingerprint is a recurring character in the paper and half of it is unexplained.

---

## 4. Tier 3 — nice to have, cut without regret

- **E12. H-saturation** (§22.3): `train_size` sweep at 50 % / 25 %. ~7 GPU-h. Only interesting if a
  reviewer disputes that data scale is saturated.
- **E13. H-mixture** (§19.4): is the +0.205 mixture gain capacity or ensembling?
- **E14. H-peaked-breadth** (§22.1): any-of-8 for `merge_dare_ties` and the uniform MoLE mixture.
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

- **2026-09-07 (b)** — E1 and E2 run and **both CONFIRMED**; struck through with their results, C1's
  evidence row rewritten to two held-out columns / three scales / three seeds, and the Tier-1 total
  reduced to E3–E6. The X1↔H1 proxy gained a 34B validation that was not planned.
- **2026-09-07** — Created, after objectives round 2 closed and §26 was recomputed over 83 systems.
  Grounded in `MASTER_REPORT.md` rev 16; costs measured from `training_summary.json` across the
  existing adapter tree rather than estimated. Records the single-language scope decision and the
  two infrastructure blockers as explicit paper-level facts rather than open tasks.
