### Target Date: 2026-09-04 (Weight-space invariance at 7B — the teacher does not matter)

> Continues [`2026-08-30_alignment-arm-lambda-sweep.md`](2026-08-30_alignment-arm-lambda-sweep.md),
> which ran the same objective on Qwen-1.5B trained on `S2` alone and found it flat-not-collapsed.
> That entry recorded a loophole; this one closes it. Trainable grid only — **H1 not read,
> `final_eval` unspent.**

- **Hypotheses / what we're testing:** **H-align** — `L = L_task(x̃) + λ·L_align`, pulling the
  student's answer-position hidden states on obfuscated code toward a frozen `tuned_L0` teacher's
  states on the clean parent, teaches semantic invariance in the weights.
  - CONFIRM if a matched arm beats both its vanilla twin (`mono_all`) **and** its mismatched-teacher
    control on at least one condition without paying an `L0` tax.
  - REFUTE if matched ≈ mismatched (the term is a regularizer, not alignment), or if both sit at or
    below the vanilla twin.
  - **Why rerun a refuted objective.** The 08-30 sweep's teacher (`tuned_L0`, 0.390) was *weaker*
    than the vanilla student it had to beat (`tuned_S2`, 0.404), so the student had nothing to gain
    by construction. On CodeLlama-7b `tuned_L0` is the strongest system in the panel
    (master report §20), which closes that loophole, and the six-condition mixture — where the
    campaign's fingerprint lives — had never been tried.

- **Setup:** [`configs/train/align_codellama7b_py_mono.yaml`](../../configs/train/align_codellama7b_py_mono.yaml),
  an exact twin of `mono_generic_py.yaml` at 7B (six conditions, 26,841 train / 1,000 val rows,
  r32, batch 16 × accum 4, seed 17, 3 epochs) plus the alignment term. Teacher
  `runs/adapters/codellama-7b/python/L0_r32_s17/best`, cached once over **5,019 distinct clean
  parents** (job 377002, 5,016/5,019 valid), k = 4 answer positions, layers L4-10-16-21-25-30 from
  `layer_fracs`. Arms: λ = 0 (plumbing), 0.3, 1, 1 **mismatched**, 3 — jobs 377003, 377108, 377004,
  377005, 377006, each ~3 h 27 m on one H200; checkpoint-select and trainable-grid eval chained
  behind each. Read by [`scripts/analysis/27_align_arms.py`](../../scripts/analysis/27_align_arms.py)
  → `results/analysis/align_2026-09-04.json`; program-cluster bootstrap, B=2000, seed 17,
  557 programs / 9,582 items.

- **Results:**

  | contrast (pooled pts) | Δ [95 % CI] |
  |---|---|
  | `align_lam0 − mono_all` | **+0.28 [−0.71, +1.22]** (null on all six; largest \|Δ\| 0.96) |
  | `align_lam0.3 − mono_all` | +0.00 [−1.16, +1.10] |
  | `align_lam1 − mono_all` | −0.78 [−2.09, +0.38] |
  | `align_lam1_mm − mono_all` | −0.96 [−2.17, +0.21] |
  | `align_lam3 − mono_all` | **−2.11 [−3.44, −0.87]** — excludes zero on **all six** conditions |
  | **`align_lam1 − align_lam1_mm`** | **+0.18 [−0.82, +1.16]** — null on all six |
  | `align_lam0 − tuned_L0` | +0.85 [−0.58, +2.34] (L0 −1.80, L1b +1.93, S2 +2.16 [+0.36, +4.15]) |
  | `align_lam0.3 − tuned_L0` | +0.56 [−0.82, +1.91] (L0 −2.22 [−4.13, −0.30], L1b +2.90 [+0.78, +4.89]) |
  | `align_lam1 − tuned_L0` | −0.22 [−1.69, +1.17] (L0 −3.35 [−5.39, −1.44], L1b +2.47 [+0.42, +4.40]) |
  | `align_lam1_mm − tuned_L0` | −0.40 [−1.96, +1.02] (L0 −3.59 [−5.63, −1.62], L1b +1.69 [−0.36, +3.80]) |
  | `align_lam3 − tuned_L0` | −1.54 [−2.85, −0.28] (L0 −4.97 [−6.94, −3.11], L1b +0.60 [−1.45, +2.53]) |

  - **Dose-response on the grid is monotone and negative:** +0.28 → +0.00 → −0.78 → −2.11 for
    λ = 0 → 0.3 → 1 → 3.
  - **The term's own fit is flat in λ:** final `align_loss` 3.475 (λ=0.3), 3.415 (λ=1), 3.374 (λ=3)
    matched, against **5.239** for the mismatched arm. Tripling the weight twice moves the fit 3 %.
  - **Held-in val is NOT monotone and separates nothing:** 0.3589 (λ=0), 0.3563 (0.3), 0.3615 (1),
    0.3537 (3), and **0.3652 for the mismatched arm — the highest of all five**. Every value is
    inside the `mono_all` seed band (0.3672 / 0.3505 / 0.3573) on 1,917 items.
  - Checkpoint selections: λ=0 `checkpoint-838`, λ=0.3 `checkpoint-838`, λ=1 `final`, λ=1mm
    `checkpoint-838`, λ=3 `checkpoint-1257`.

- **What worked / hypothesis verdict:** **H-align REFUTED at 7B, with the loophole closed.**
  - The **plumbing gate passed**: λ = 0 is a null against `mono_all` on all six conditions and
    reproduces the campaign fingerprint against `tuned_L0` (L0 −1.80, L1b +1.93). So the harness is
    the vanilla recipe plus one term, as designed.
  - **The control is the verdict.** Matched − mismatched is **+0.18 [−0.82, +1.16]**, null on every
    condition, while both sit ~1 point below the vanilla twin. An arm aligned to a *different
    program's* clean states is indistinguishable from one aligned to its own. `L_align` is a
    hidden-state perturbation whose **magnitude** matters and whose **target** does not.
  - The `L0` tax breadth imposes does not close under the objective; it deepens monotonically
    (−1.80 → −3.35 → −4.97). At λ = 3 the term also erases the `L1b` gain (+1.93 → +0.60), i.e. it
    destroys the one located effect the fingerprint contains
    (`../transfer/2026-09-04_l1b-l0-trade-is-two-effects.md`).

- **Observations:**
  - **A gradient-accumulation defect was found while λ = 0 trained, and the gate then settled it
    empirically.** `AlignTrainer.compute_loss` never forwarded `num_items_in_batch`, so
    transformers skipped its `/grad_accum` division: every logged loss and gradient in every
    alignment arm ever run — the 08-30 Qwen sweep included — is 4× the vanilla recipe's at the same
    step (9.42 vs 2.27 at epoch 0.05), and grad_norm ~4.6 against ~1.0 meant the 1.0 clip engaged
    almost every step. Fixed in `7ad5353` (`model_accepts_loss_kwargs = False`) but deliberately
    **not** in the running arms: all five share it, so within-sweep contrasts are unaffected, and a
    mixed sweep would have been worse than a consistent one. What it weakened was the claim that
    λ = 0 is an *exact* twin of `mono_all` — which is exactly what the gate measures, and the gate
    passed.
  - The mismatched arm posting the **highest held-in val of all five** is the sharpest form of the
    result: on the metric the objective is trained against, being pointed at the wrong program is
    not a disadvantage.
  - This is the **fourth** arm in this project whose interpretation was decided by its negative
    control (`mole_random`, `l0merge`, oracle-of-k, and now this). In every case the treatment
    moved and the control moved with it.

- **New questions / new hypotheses:** none worth opening from these numbers. Two untried answers to
  the `n ≠ m` problem remain on the shelf — mean-pooled per-layer states with an InfoNCE objective,
  and token-aligned matching through `Variant.rename_map` (available for `L1b`/`L1r`/`L2`, absent
  for `S1`/`S2`) — but neither is motivated by this result: the answer-position variant already has
  *exact* correspondence, and it was the teacher, not the correspondence, that turned out not to
  matter. Reopening would need a reason to believe the alignment target is right and only the
  comparison was wrong.

- **Next Steps:** master report §23.3 updated with the full sweep. Arm closed; adapters retained
  under `runs/adapters_align/codellama-7b/python/`.
