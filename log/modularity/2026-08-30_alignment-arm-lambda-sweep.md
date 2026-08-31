### Target Date: 2026-08-30 (The alignment arm is well-posed, correctly implemented, and does nothing)

- **Hypotheses / what we're testing:** **H-align — fine-tuning the student's answer-position
  hidden states on OBFUSCATED code toward a frozen `tuned_L0` teacher's states on the CLEAN
  parent (`L = L_task + λ·L_align`) buys out-of-distribution invariance.** Pre-registered in
  `../../continuation/01_NEXT_STEPS.md` Phase 2. CONFIRM if a matched arm beats the vanilla
  `S2` specialist on conditions it never trained on. REFUTE if flat against that twin, **or**
  if matched by the mismatched-teacher control. Two auxiliary checks are load-bearing:
  **λ=0 must reproduce the vanilla specialist** (plumbing), and the **mismatched control**
  decides whether `L_align` is semantic alignment or merely a regularizer.

- **Setup:** `configs/eval/align_lam_sweep_qwen1.5b.yaml` (new), job **359324**, 84 cells,
  `phase: align_lam_sweep`, Grid A (`eval_source: heldout`), 14 systems x 6 conditions.
  Arms trained 08-28/08-29 from `configs/train/align_qwen1.5b_py_S2.yaml` (all on `S2` only,
  `k=4`, layers [4,9,14,19,23,27], seed 17); checkpoint-selected today (jobs 359310-359320)
  on the held-in `S2` val slice. **OOD** below = mean accuracy over the five conditions the
  arm never trained on (L0, L1b, L1r, L2, S1). Cluster bootstrap by program, B=2000, n=412
  (the all-conditions-succeeded common subset). **H1 not read; 0 H1 cells.**

- **Results:**
  - **Plumbing check PASSES.** `align_lam0` vs `tuned_S2` per condition: −0.0057, −0.0032,
    −0.0089, −0.0065, −0.0024, −0.0040. λ=0 reproduces the vanilla specialist.
  - **Matched arm, OOD, vs the vanilla twin — flat at every λ:**

    | λ | matched − vanilla twin | matched − mismatched control |
    |---|---|---|
    | 0.1 | −0.0068 [−0.0152, +0.0015] | +0.0078 [+0.0003, +0.0149] |
    | 0.3 | −0.0078 [−0.0162, +0.0002] | +0.0248 [+0.0147, +0.0348] |
    | 1 | −0.0044 [−0.0128, +0.0040] | +0.0419 [+0.0299, +0.0544] |
    | 3 | −0.0065 [−0.0152, +0.0023] | +0.0610 [+0.0461, +0.0759] |
    | 10 | −0.0065 [−0.0155, +0.0024] | +0.0785 [+0.0604, +0.0968] |

    Every "matched − vanilla" CI contains 0; all five point estimates are slightly negative.
  - **The mismatched control degrades monotonically in λ.** OOD: 0.389, 0.371, 0.358, 0.336,
    0.319 for λ = 0.1, 0.3, 1, 3, 10, against the matched arms' flat ~0.396–0.400.
  - Reference rows, OOD: `base` 0.209, `tuned_L0` (the teacher) 0.390, `tuned_S2` 0.404.

- **What worked / hypothesis verdict:** **H-align REFUTED — flat, NOT collapsed.** The
  pre-registered refutation had two disjuncts and only the first fired. The arm is flat
  against its vanilla twin at every λ, so the objective buys nothing. But it is **not**
  matched by the mismatched control: the matched−mismatched gap is positive at every λ,
  grows monotonically (+0.008 → +0.079), and its CI excludes 0 everywhere. So `L_align` is
  doing real, teacher-identity-dependent work — it is not a regularizer.

- **Observations:**
  - **This is the strongest form a negative result can take here.** λ=0 reproduces vanilla
    (the harness is correct), and aligning to the WRONG program's states actively hurts, more
    as λ rises (the loss has real grip on the representation). The objective is well-posed
    and correctly implemented, and it still does not produce invariance. That rules out
    "bad plumbing" and "inert loss" as explanations, which is exactly what the two controls
    were budgeted to do.
  - **The control's monotone damage is the useful number.** It establishes a dose-response
    for `L_align`: at λ=10 a wrong teacher costs 7.9 OOD points. The matched teacher at the
    same λ costs nothing and gains nothing. So the student can be pulled toward a teacher's
    answer-position geometry, and being pulled toward the RIGHT one is worth ~0.
  - **`tuned_S2` (0.404 OOD) already beats the `tuned_L0` teacher (0.390).** The arm's
    stated ceiling was "think about obfuscated code the way the clean-code adapter thinks
    about clean code" — but on these conditions the vanilla S2 specialist is already above
    that teacher. Aligning to `tuned_L0` may therefore be aiming at a target that is not
    better than where the student already is, which would explain a null without the
    objective being wrong. **Teacher = `tuned_S2`-of-another-seed, or a stronger teacher, is
    the version this result does not rule out.**
  - Consistent with the project's central pattern: this is the sixth attempted repair, and
    the first to optimize invariance as an objective rather than through data. It reproduces
    the same shape as the other five from a genuinely new mechanism, which makes the
    aggregate negative stronger rather than repetitive.

- **New questions / new hypotheses:** **H-teacher — the null is a teacher-quality ceiling,
  not an objective failure.** Predicts that aligning to a teacher that is actually better
  than the student on the target conditions produces a gain. Cheap to test: the cache
  machinery is built and a mismatched control is a free permutation of a cache index.

- **Next Steps:** (1) Re-run one λ with a stronger teacher (H-teacher). (2) Any λ selected
  here is selected on S2-transfer, which is weaker than the LOTO diagonal mean
  `../../continuation/01_NEXT_STEPS.md` names — re-confirm against LOTO before spending an
  H1 access on this arm. (3) On present evidence this arm does not warrant an H1 read.
