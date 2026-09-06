### Target Date: 2026-09-06 (four new fine-tuning objectives: paired consistency is the one that works)

- **Hypotheses / what we're testing:** Every arm in the campaign so far shared one objective —
  next-token CE on the answer span — and varied data, model, or rank. Four arms change the
  *objective* (pre-registered in `CLAUDE_SCRATCHPAD.md` §"OBJECTIVES CAMPAIGN", frozen at commit
  `447ecdb` before any GPU job; H1 is spent, so the held-out-family read is **X1**, the lossless
  proxy from [`2026-09-05_x1-is-a-trainable-proxy-for-h1.md`](2026-09-05_x1-is-a-trainable-proxy-for-h1.md)).
  All CIs are program-clustered bootstraps, 2000 resamples, item-for-item against the
  `x1_generic` controls on the same `heldout` rows.
  - **H-cons (O1, paired consistency):** `L = CE(x_obf) + λ·KL(p_T(·|x_L0-parent) ‖ p_S(·|x_obf))`
    at the answer tokens, teacher = frozen `tuned_L0/best` loaded as a second PEFT adapter.
    CONFIRM if `cons_lam1 − mono_all` on X1 excludes 0 above AND `cons_lam1 − cons_same_lam1 > 0`
    (`cons_same` = the teacher sees the *same* obfuscated input, i.e. plain distillation — separates
    "consistency across surfaces" from "a stronger teacher"). Also read vs `tuned_L0` on X1.
  - **H-neg (O2, semantic negatives):** verified single-operator mutants of the obfuscated rows;
    mutant + true output is an extra CE row, mutant + *original* output is a negative row scored
    by unlikelihood `−log(1−p)` at the first diverging token. CONFIRM if `neg_ul − neg_data > 0`
    on X1 excluding 0; `neg_data − mono_all` is the data-only read (expected null).
  - **H-resample (O3):** X1 rebuilt at seeds 101/202; 3 surfaces × 1 epoch, step-matched to
    `tuned_X1` (1 surface × 3 epochs). CONFIRM if `x1_resample − tuned_X1` on X1 excludes 0.
  - **H-curr (O4, curriculum):** init from `tuned_L0/best`, 1 epoch on the five non-L0 conditions
    at lr 5e-5. CONFIRM if `curr_kl − tuned_L0 ≥ 0` on L0 (no tax) AND `curr_kl − mono_all > 0`
    pooled non-L0; `curr_kl − curr_sft` separates the objective from the order.

- **Setup:** CodeLlama-7b, Python, LoRA r=32, seed 17, one H200 per adapter, env
  `obtune-cu129`. Trainer `src/obtune/objectives.py` (`-m obtune.objectives train`), configs
  `configs/train/obj_{cons,neg,curr}_codellama7b_py.yaml` and `configs/train/resample_py_X1.yaml`;
  negatives built by `scripts/32_build_negatives.py` (job 378683: 6,621 verified pairs over
  L0–S2, yield 78 % identifier / 76 % S1 / 55 % S2, parent-mismatch 0); X1 surfaces by
  `x1_build_s101/s202` (378684–378687, 4,947 rows each, code differs from the s17 surface on
  4,935/4,947, gold identical). Smoke 378765 (all six arms, `--dry-run` + `--max-steps 4`) after
  the TRL `loss_type="nll"` fix (`04d349a`: TRL 1.9.2's default `chunked_nll` returns
  `logits=None`, which the KL and unlikelihood terms index). Chains (train → ckpt-select
  `afterok`): `cons_lam1` 378779→378780, `cons_lam3` 378781→378782, `cons_same_lam1`
  378783→378784, `neg_ul` 378785→378786, `neg_data` 378787→378788, `x1_resample` 378789→378790,
  `curr_sft` 378791→**379318**, `curr_kl` 378793→378794; eval **379319**
  (`configs/eval/objectives_codellama7b.yaml`, phase `objectives_generic`, 8 systems × 7
  conditions = 56 cells, 10:51 wall). Analysis `scripts/analysis/34_objectives.py --n-boot 2000`
  → [`results/analysis/objectives_2026-09-05.json`](../../results/analysis/objectives_2026-09-05.json).
  Adapters under `runs/adapters_objectives/codellama-7b/python/`. Ckpt-select (val, never X1
  for the six-condition arms): `cons_lam1` ckpt-419 (0.368), `cons_lam3` ckpt-419 (0.378),
  `cons_same` ckpt-838 (0.364), `neg_ul` ckpt-1252 (0.343), `neg_data` ckpt-1569 (0.361),
  `x1_resample` ckpt-108 (0.268 on the 261-item X1 val), `curr_sft` ckpt-346 (0.351),
  `curr_kl` ckpt-346 (0.360). Training: consistency arms 4.4–4.9 h / 1257 steps (the teacher
  forward roughly doubles `mono_all`'s 3.5 h), `neg_ul` 5.2 h / 1878 steps, `neg_data` 4.3 h /
  1569, `curr_*` 1.0–1.25 h / 346, `x1_resample` 0.6 h / 162. Loss telemetry: KL to the L0
  teacher 2.08 nats/token at init → 0.064 (`lam1`) / 0.060 (`same`) at epoch 3, 0 rows failing
  the answer-token correspondence assert in any arm; unlikelihood 0.076 → 0.020 with 0 bad
  rows and 2.79 negatives per microbatch (expected 2.64). `format_fail` 0.010–0.017 on every
  arm (controls 0.008–0.029). H1 **unread** (no H1 cell exists in `objectives_generic`).

- **Results:** (points; `*` = interval excludes zero; 557 programs pooled, 405 on X1)

  | system | L0 | L1b | L1r | L2 | S1 | S2 | **X1** | pooled |
  |---|---|---|---|---|---|---|---|---|
  | `tuned_L0` | 0.4281 | 0.3589 | 0.3790 | 0.3826 | 0.3801 | 0.3887 | 0.2702 | 0.3735 |
  | `mono_all` | 0.4126 | 0.3878 | 0.3856 | 0.3802 | 0.3857 | 0.4043 | 0.2323 | 0.3750 |
  | `tuned_X1` | 0.4126 | 0.3408 | 0.3617 | 0.3515 | 0.3681 | 0.3833 | 0.3188 | 0.3640 |
  | `cons_lam1` | 0.4251 | 0.4041 | 0.3940 | 0.3874 | 0.3986 | 0.4139 | 0.2628 | 0.3882 |
  | **`cons_lam3`** | 0.4251 | 0.4047 | 0.3940 | 0.3934 | 0.3994 | 0.4157 | **0.2834** | **0.3919** |
  | `cons_same_lam1` | 0.4174 | 0.3812 | 0.3868 | 0.3874 | 0.3889 | 0.4001 | 0.2603 | 0.3788 |
  | `neg_ul` | 0.3916 | 0.3812 | 0.3737 | 0.3731 | 0.3272 | 0.3809 | 0.1713 | 0.3505 |
  | `neg_data` | 0.4030 | 0.3938 | 0.3886 | 0.3988 | 0.3641 | 0.3959 | 0.1985 | 0.3701 |
  | `x1_resample` | 0.4006 | 0.3341 | 0.3491 | 0.3473 | 0.3536 | 0.3779 | 0.3237 | 0.3566 |
  | `curr_sft` | 0.4096 | 0.3806 | 0.3749 | 0.3796 | 0.3769 | 0.3995 | 0.2578 | 0.3727 |
  | `curr_kl` | 0.4257 | 0.3926 | 0.3856 | 0.3904 | 0.3873 | 0.4127 | 0.2784 | 0.3860 |

  - **H-cons.** `cons_lam1 − mono_all`: X1 **+3.05 [+1.24, +4.78]\***, pooled +1.32 [+0.25, +2.46]\*,
    non-L0 +1.34 [+0.26, +2.46]\*. `cons_lam3 − mono_all`: X1 **+5.11 [+3.05, +7.08]\***, pooled
    +1.70 [+0.50, +2.97]\*, non-L0 +1.78 [+0.59, +3.02]\*. `cons_lam1 − cons_same_lam1`: pooled
    +0.94 [+0.10, +1.79]\*, L1b +2.29 [+0.84, +3.86]\*, X1 +0.25 [−1.15, +1.65]. `cons_lam3 −
    cons_same_lam1`: pooled +1.31 [+0.45, +2.15]\*, X1 +2.31 [+0.82, +3.87]\*. `cons_same_lam1 −
    mono_all`: X1 +2.80 [+0.99, +4.62]\*, pooled +0.39 [−0.84, +1.55]. Versus **`tuned_L0`**:
    `cons_lam3` pooled +1.84 [+0.88, +2.84]\*, non-L0 +2.24 [+1.24, +3.26]\*, L1b +4.58 [+2.83,
    +6.33]\*, S2 +2.70 [+1.02, +4.44]\*, **L0 −0.30 [−1.80, +1.32], X1 +1.32 [−0.58, +3.13]**;
    `cons_lam1` X1 −0.74 [−2.63, +1.07].
  - **H-neg.** `neg_ul − neg_data`: X1 **−2.72 [−4.20, −1.15]\***, pooled −1.96 [−3.22, −0.67]\*.
    `neg_data − mono_all`: X1 **−3.38 [−5.28, −1.40]\***, pooled −0.48 [−1.71, +0.64], S1 −2.17
    [−4.33, +0.00], L2 +1.86 [+0.18, +3.47]\*. `neg_ul − mono_all`: X1 −6.10 [−8.25, −3.87]\*,
    pooled −2.45 [−3.97, −1.04]\*. `neg_ul − tuned_L0`: X1 −9.88 [−12.44, −7.49]\*, L0 −3.65
    [−5.80, −1.68]\*.
  - **H-resample.** `x1_resample − tuned_X1`: X1 **+0.49 [−1.07, +1.90]**, pooled −0.74 [−1.42,
    −0.03]\*, every trainable condition negative with L0 −1.20 [−2.64, +0.18] the largest.
    `x1_resample − mono_allX`: X1 +1.40 [−0.74, +3.54], pooled −2.32 [−3.80, −0.84]\*.
  - **H-curr.** `curr_kl − tuned_L0`: L0 **−0.24 [−1.68, +1.14]**, pooled +1.25 [+0.39, +2.14]\*,
    non-L0 +1.52 [+0.61, +2.46]\*, X1 +0.82 [−0.66, +2.31]. `curr_kl − mono_all`: non-L0
    **+1.06 [−0.12, +2.28]**, pooled +1.10 [−0.13, +2.31], X1 +4.61 [+2.63, +6.58]\*. `curr_kl −
    curr_sft`: pooled **+1.32 [+0.66, +1.98]\***, L0 +1.62 [+0.42, +2.81]\*, X1 +2.06 [+0.82,
    +3.29]\*. `curr_sft − tuned_L0`: pooled −0.07 [−1.05, +0.96], L0 −1.86 [−3.35, −0.30]\*;
    `curr_sft − mono_all`: pooled −0.22 [−1.32, +0.84], X1 +2.55 [+0.91, +4.28]\*.

- **What worked / hypothesis verdict:**
  - **H-cons — SUPPORTED, both clauses, and it is the first arm in the campaign that gets both
    halves.** `cons_lam1 − mono_all` on X1 is +3.05 [+1.24, +4.78] and `cons_lam1 − cons_same`
    is +0.94 [+0.10, +1.79] pooled. Read against the standing best: `mono_all` pays a −3.79 X1
    penalty and a −1.55 L0 tax relative to `tuned_L0` for its gains on the trained conditions
    (the "breadth hurts" finding of [`2026-09-03_h1-repair-clean-code-beats-breadth.md`](2026-09-03_h1-repair-clean-code-beats-breadth.md)).
    `cons_lam3` keeps the breadth gain (+2.24 [+1.24, +3.26] over `tuned_L0` on the non-L0
    conditions, L1b +4.58, S2 +2.70) **and pays neither** (L0 −0.30 [−1.80, +1.32], X1 +1.32
    [−0.58, +3.13]). Its pooled 0.3919 is the highest of the fifteen 7B systems evaluated on this
    seven-condition set (next: `mono_allX` 0.3798, `tuned_S2` 0.3792). What it does *not* do is beat `tuned_L0` on the held-out family — the X1 interval
    covers zero at both λ. Verdict: the consistency term **repairs** breadth's held-out
    penalty; it does not yet exceed the clean-code specialist there.
  - **The mechanism has two parts and they separate.** Plain distillation from the L0 teacher on
    the same input (`cons_same`) already recovers +2.80 [+0.99, +4.62] on X1 — most of the
    `lam1` X1 gain is "a better teacher", not "a clean-code view". The parent view adds on top
    on the trained conditions at both λ (pooled +0.94 / +1.31, both excluding zero, concentrated
    on L1b +2.29 — the renaming condition, where the parent view carries exactly the identifier
    information the surface destroyed) and on X1 only at λ = 3 (+2.31 [+0.82, +3.87]; λ = 1
    +0.25). λ moves in the expected direction: `lam3 − lam1` is non-negative on every
    condition (equal on L0 and L1r; pooled +0.37, X1 +2.06), though not a pre-registered contrast.
  - **H-neg — REFUTED in the wrong direction.** The unlikelihood term costs −1.96 pooled and
    −2.72 on X1 against its own data-only control, and the mutant positives alone cost −3.38
    [−5.28, −1.40] on X1 (null pooled, a lone L2 gain). Semantic negatives are the first lever
    in the campaign to *hurt* the held-out family; see Observations for why.
  - **H-resample — REFUTED (null on X1, small cost elsewhere).** +0.49 [−1.07, +1.90] on X1
    against `tuned_X1` with a −0.74 pooled cost. Three surfaces of X1 teach exactly what one
    surface teaches. This is the third "more surfaces" null after `mono_aug` and the case
    multiplier ([`2026-09-05_more-cases-per-program-is-null.md`](2026-09-05_more-cases-per-program-is-null.md)).
  - **H-curr — NOT CONFIRMED by its own rule, but the objective half is real.** The no-tax
    clause holds (L0 −0.24 [−1.68, +1.14]); the `curr_kl − mono_all` non-L0 clause misses,
    +1.06 [−0.12, +2.28]. The pre-registered separator is decisive: `curr_kl − curr_sft` is
    +1.32 [+0.66, +1.98] pooled and positive on every one of the seven conditions, while
    `curr_sft` alone is indistinguishable from `mono_all` (−0.22) and pays an L0 tax (−1.86).
    **Order is worth nothing; the KL term is worth the same ~1.3 pts it is worth from scratch.**

- **Observations:**
  - The two arms that improve — `cons_*` from scratch and `curr_kl` from `tuned_L0` — are the
    two that carry the KL-to-L0-teacher term; the two arms that match or lose — `curr_sft`,
    `neg_data` — are the two that only change the data. This is consistent with H-saturation
    (more data of any kind is null at 7B) and locates the one non-saturated lever in the
    *target distribution*, not the input distribution: the teacher's answer distribution on the
    clean parent is a softer, better-calibrated label than the one-hot gold, and the parent
    view is a second independent signal that the model should not care about the surface.
  - Why negatives hurt: a mutant that is one operator away from the original with a verified
    different output is, by construction, a program whose *text* is almost identical to a
    training program but whose *label* is different. Adding 6,621 of them (20 % of the rows) as
    positives forces the model to separate near-identical surfaces by output — the opposite of
    invariance — and the effect lands hardest exactly where the surface is least familiar (X1
    −3.38). Unlikelihood on the original output then pushes probability mass off tokens that
    are right most of the time (the first diverging token is usually a single digit or sign),
    which reads as a further uniform ~2-pt cost. It was also the only arm whose ckpt-select
    val fell below `mono_all`'s (0.343 vs 0.367). The lever is not salvageable by tuning λ
    without a second held-out family, and the read is closed.
  - `cons_lam1`'s val-selected checkpoint scores 0.368 on the six-condition val set, equal to
    `mono_all`'s 0.367, yet is +1.32 pooled on held-out — the val set does not resolve a ~1-pt
    effect (documented tolerance 0.2 pts on ~1.9k items ≈ 1 pt noise), and both consistency
    arms selected epoch 1 where `mono_all` selected epoch 2.
  - Silent-failure checks: adapter-applied assertion passed for all eight systems; 56/56 cells;
    `format_fail` ≤ 0.017; truncation 0.9 % on the resample corpus; answer-token
    correspondence 0 failures over ~40k (consistency) and 0 bad unlikelihood rows over ~1.9k
    steps. Single seed (s17) — the campaign's seed band on `mono_all` was ±~1 pt, so the X1
    numbers of +3.05/+5.11 are outside it and the pooled +1.3/+1.7 are at its edge.
  - Operational: `/work/jvl210002` hit its **1100 GB hard quota** mid-campaign (00:27 UTC);
    `tr_curr_sft`'s redundant `final/` save failed with `Disk quota exceeded` after
    `checkpoint-346` was complete, so the chain tail was resubmitted against the checkpoint
    (379318/379319). 7.3 GB of 4-step smoke checkpoints were removed to keep the other three
    trainers alive; nothing else was deleted. 343 GB of `optimizer.pt` resume state across 681
    old checkpoints is the obvious next cleanup and awaits a decision.

- **New questions / new hypotheses:**
  - **H-cons-scale:** does the consistency term's X1 gain survive at 13B/34B, where the base
    tuning gap is larger? Scale was the only lever above 1 pt at 7B; consistency is now the
    only *algorithmic* lever above 1 pt at 7B, and they are plausibly orthogonal.
  - **H-cons-lam:** λ = 3 > λ = 1 everywhere; the curve above 3 is unmeasured (a λ sweep on the
    trainable grid only — X1 is not for tuning).
  - **H-cons-seed:** replicate `cons_lam3` at s42 and s101 before any claim stronger than
    "repairs breadth's held-out penalty".
  - **H-cons-teacher:** the teacher is `tuned_L0` (7B). Would `tuned_L0` (34B) as teacher lift
    a 7B student past its own 0.32 on X1 — i.e. is this the distillation route to the 34B
    number at 7B cost?
  - **H-curr-kl-from-mono:** `curr_kl` starts from `tuned_L0`; starting from `mono_all` with
    the KL term is the cheapest test of whether the term repairs an already-trained breadth
    adapter (1 h vs 4.4 h).

- **Next Steps:** (1) seed replication of `cons_lam3` (s42, s101) and a λ ∈ {5, 10} pair on
  the trainable grid — pre-register, then submit; (2) `curr_kl` from `mono_all/best`; (3) master
  report §26 once the seeds are in. The H1 column stays closed; the X1 read of these arms is
  final and nothing in this entry is used to select anything on X1.
