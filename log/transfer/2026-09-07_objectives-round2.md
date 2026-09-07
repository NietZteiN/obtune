### Target Date: 2026-09-07 (objectives round 2: the seed band holds, λ=3 is the peak not a floor, KL-from-`mono_all` passes by 0.16 pts — and the pre-registered format gate is unworkable as written)

Round 2 of the objectives campaign, pre-registered in `CLAUDE_SCRATCHPAD.md` at commit `2b0b841`
and submitted at `9eab051` **before any GPU job**, continuing
[`2026-09-06_consistency-objective-repairs-breadth.md`](2026-09-06_consistency-objective-repairs-breadth.md).
Jobs 380166–380176 (five train → five ckpt-select → one eval, `afterok` chained). H1 is spent, so
every held-out-family read is **X1**. No decision rule was altered after submission.

- **Hypotheses / what we're testing:** round 1 left three things unresolved — it was a single seed,
  λ was read at two values, and the KL term had only been applied starting from `tuned_L0`.
  - **H-cons-seed** — CONFIRM iff `cons_lam3_sN − mono_all_sN` on X1 excludes zero above for
    **both** N ∈ {42, 101}; PARTIAL if one; REFUTE if neither.
  - **H-cons-lam** — decided on the **trainable grid** pooled (L0–S2). CONFIRM if
    `cons_lam10 − cons_lam3` > 0 excluding zero; REFUTE ("over-regularised") if < 0 excluding zero;
    NULL otherwise. X1 reported for λ=5/10 but **never used to choose λ**.
  - **H-curr-kl-from-mono** — CONFIRM iff `currmono_kl − mono_all` on X1 > 0 excluding zero AND
    `currmono_kl − tuned_L0` on X1 does not exclude zero from below.

- **Setup:** CodeLlama-7b, Python, LoRA r=32, one H200 per adapter, env `obtune-cu129`. Five new
  adapters: `cons_lam3` at seeds 42/101, `cons_lam5`, `cons_lam10` (all `objectives.py train
  --objective consistency --teacher-view parent`, teacher = frozen `tuned_L0/best`), and
  `currmono_kl` = round 1's `curr_kl` recipe (5 non-L0 conditions, 1 epoch, lr 5e-5, teacher
  `tuned_L0` on the L0 parent) **initialised from `mono_all/best`** instead of `tuned_L0/best`.
  `mono_all_s42` / `mono_all_s101` re-read on all seven conditions as seed-matched controls.
  Training 4.36–4.40 h each (`currmono_kl` 1.28 h, one epoch); every arm `n_missing_parent: 0`.
  Eval `ev_objectives_r2` 380176, 579 s, 49 cells. Analysis
  [`scripts/analysis/34_objectives.py`](../../scripts/analysis/34_objectives.py)
  `--n-boot 2000 --out results/analysis/objectives_2026-09-07.json`; program-clustered bootstraps,
  seed 17, same rows as round 1.

- **Results — checkpoint selection.** All seven arms selected **checkpoint-419** (epoch 1); the
  three-epoch decline is monotone and identical across seeds and λ. Validation (1,917 items, six
  trainable conditions, X1 correctly excluded from selection):

  | arm | 419 | 838 | 1257 | final |
  |---|---:|---:|---:|---:|
  | `cons_lam3_s17` (r1) | 0.3777 | 0.3652 | 0.3646 | 0.3652 |
  | `cons_lam3_s42` | 0.3782 | 0.3652 | 0.3631 | 0.3641 |
  | `cons_lam3_s101` | 0.3646 | 0.3579 | 0.3605 | 0.3573 |
  | `cons_lam5` | 0.3782 | 0.3652 | 0.3652 | 0.3662 |
  | `cons_lam10` | **0.3824** | 0.3657 | 0.3631 | 0.3652 |

- **Results — H-cons-seed: CONFIRMED.** Both seeds clear on X1 against their own seed-matched
  `mono_all`:

  | contrast | X1 | pooled | grid (L0–S2) | L0 |
  |---|---:|---:|---:|---:|
  | `cons_lam3_s42 − mono_all_s42` | **+4.53 [+2.64, +6.26]** | +1.81 [+0.87, +2.80] | +1.46 [+0.46, +2.51] | +0.78 [−0.60, +2.33] |
  | `cons_lam3_s101 − mono_all_s101` | **+4.12 [+2.39, +5.93]** | +1.62 [+0.55, +2.77] | +1.30 [+0.09, +2.52] | +1.32 [−0.24, +2.99] |
  | three seeds pooled | **+4.59 [+3.16, +5.99]** | +1.71 [+0.88, +2.58] | — | +1.12 [−0.02, +2.33] |

  `cons_lam3` on X1 by seed: **0.2834 / 0.2801 / 0.2743**, range **0.91 pts** — narrower than the
  ±0.8-pt seed band §22 established for plain SFT, so round 1's single-seed read was not luck.
  Against `tuned_L0` the shape also replicates: non-L0 +2.49 / +1.73, L0 −0.54 [−2.09, +1.08] /
  −0.90 [−2.51, +0.78], X1 +0.99 / +0.41 (both inside noise). **`cons_lam3_s42` pooled 0.3937 is
  now the best 7B system on the seven-condition set**, above round 1's 0.3919.

- **Results — H-cons-lam: REFUTED ("over-regularised"), and the validation set pointed the wrong
  way.** On the trainable grid, `cons_lam10 − cons_lam3` = **−0.65 [−1.20, −0.14]**, excluding zero
  *below* — the refute branch. `cons_lam5 − cons_lam3` −0.28 [−0.82, +0.27] is null, so λ = 3 is a
  plateau start, not a floor.

  | contrast | grid (L0–S2) | L0 | X1 (reported, not used) |
  |---|---:|---:|---:|
  | `cons_lam5 − cons_lam3` | −0.28 [−0.82, +0.27] | −0.84 [−1.74, +0.06] | −1.07 [−2.31, +0.16] |
  | `cons_lam10 − cons_lam3` | **−0.65 [−1.20, −0.14]** | −1.20 [−2.27, −0.18] | −0.25 [−1.48, +0.91] |
  | `cons_lam10 − cons_lam5` | −0.37 [−0.83, +0.03] | −0.36 [−1.08, +0.36] | +0.82 [−0.33, +2.06] |

  The damage is concentrated on `L0` (−1.20 [−2.27, −0.18]), i.e. too much pull toward the teacher
  re-creates a clean-code tax — the opposite end of the same axis breadth sits on. **Worth
  recording as a process point:** the checkpoint-selection validation column ranked λ=10 *highest*
  (0.3824, above λ=3's 0.3777), and on the held-out grid λ=10 is reliably *worse*. 1,917 validation
  items over six conditions did not predict 9,582 held-out ones. The rule was frozen on the grid,
  which is the only reason this did not become a wrong promotion.

- **Results — H-curr-kl-from-mono: CONFIRMED, by 0.16 pts, and the start still matters.**
  Both clauses pass: `currmono_kl − mono_all` on X1 = **+2.14 [+0.41, +3.79]** (excludes zero
  above), and `currmono_kl − tuned_L0` on X1 = **−1.65 [−3.54, +0.16]** (does not exclude zero from
  below — by 0.16 pts). Recorded as confirmed **on the rule as written**, with the margin stated.

  | contrast | X1 | pooled | grid | L0 |
  |---|---:|---:|---:|---:|
  | `currmono_kl − mono_all` | **+2.14 [+0.41, +3.79]** | +1.24 [+0.27, +2.20] | +1.13 [+0.06, +2.14] | +0.42 [−0.90, +1.74] |
  | `currmono_kl − tuned_L0` | −1.65 [−3.54, +0.16] | +1.39 [+0.26, +2.53] | +1.77 [+0.58, +3.00] | −1.14 [−2.93, +0.72] |
  | `currmono_kl − curr_kl` | **−2.47 [−4.12, −0.91]** | +0.14 [−0.84, +1.04] | +0.47 [−0.54, +1.43] | −0.90 [−2.33, +0.54] |

  The secondary contrast is the informative one. On the **trainable grid the two inits are
  indistinguishable** (+0.14 [−0.84, +1.04]), so round 1's "the KL term is worth ~1.3 pts from
  either start" holds *there*. On the **held-out family it is false**: starting from `mono_all`
  lands 2.47 pts below starting from `tuned_L0` (0.2537 vs 0.2784), an interval clearing zero. One
  epoch of KL-continued training repairs roughly half of breadth's X1 deficit (`mono_all` 0.2323 →
  0.2537, against `tuned_L0`'s 0.2702) and no more. **The init's held-out disadvantage is real and
  only partly recoverable** — which is a sharper statement of the campaign's central finding than
  round 1 could make.

- **⚠️ The pre-registered format gate is unworkable as written, and this is not specific to
  round 2.** The pre-registration says "format_fail reported; > 2 % on any cell voids that cell's
  read." Applied literally it voids **10 of 49** round-2 cells — and, on the same panel, the whole
  of the `tuned_L0` **control** column (0.0216–0.0428 on all seven conditions), `tuned_X1`
  (7/7), `base` (0.119–0.161), `formatonly` (0.080–0.147), and six of round 1's already-published
  X1 cells (`cons_lam1` 0.0272, `cons_lam3` 0.0255, `cons_same_lam1` 0.0313, `neg_ul` 0.0214,
  `curr_sft` 0.0206, `curr_kl` 0.0247). A gate that voids the control arm of every contrast voids
  the campaign, including results already in `MASTER_REPORT.md` rev 15 §27.5. The 2 % figure comes
  from CLAUDE.md §4, where it is a **design expectation for the constrained no-CoT format**, not a
  per-cell validity threshold; it was imported into this pre-registration as the latter without
  checking it against the panel it would be applied to. That is a defect in my pre-registration,
  not a defect in the runs.

  **It does not change any verdict, and that was tested rather than assumed.** Re-running each
  decisive contrast on the subset where *neither* arm format-failed:

  | decisive contrast | as published | format-clean subset |
  |---|---:|---:|
  | H-cons-seed s42 (X1) | +4.53 [+2.63, +6.26] (n=1214) | +4.73 [+3.01, +6.85] (n=1162) |
  | H-cons-seed s101 (X1) | +4.12 [+2.30, +6.01] (n=1214) | +4.26 [+2.24, +5.99] (n=1174) |
  | H-curr-mono − `mono_all` (X1) | +2.14 [+0.41, +3.87] (n=1214) | +2.22 [+0.46, +4.00] (n=1171) |
  | H-curr-mono − `tuned_L0` (X1) | −1.65 [−3.54, +0.33] (n=1214) | −1.74 [−3.69, +0.25] (n=1150) |
  | H-cons-lam grid | −0.65 [−1.19, −0.11] (n=9582) | −0.64 [−1.19, −0.04] (n=9372) |

  Every verdict is identical, and the winning arms format-fail *more* than the controls they beat
  (`cons_lam3_s42` X1 0.0313 vs `mono_all_s42` 0.0214), so format is a headwind to these results,
  not their source. **The gate needs re-specifying before it is used again** — as a differential
  between the two arms of a contrast, or against a panel-calibrated level, not a flat 2 %. Left
  unresolved here deliberately: re-specifying a rule *after* seeing the reads it would void is
  exactly the move pre-registration exists to prevent, so it is recorded and handed to the human.

- **Observations:**
  - `34_objectives.py --out` defaults to `objectives_2026-09-05.json`; the first run of this
    analysis therefore overwrote a tracked dated artifact (additively — 2,364 insertions, 0
    deletions). Restored with `git checkout` and re-run with an explicit
    `--out objectives_2026-09-07.json`. Same class of defect as `28_master_panel.py`
    (rev-15 entry); both should take a required dated output.
  - The QOS caps this account at 4 running jobs, so `tr_currmono_kl` serialised behind the λ batch
    rather than running beside it. Chain still finished inside 10 h unattended.
  - Quota peaked at 67.4 % — the five arms cost ~10 GB, as projected after the 09-06 cleanup.

- **Next steps:** fold §27.7 of `MASTER_REPORT.md` into §27.5 as rev 16 (seed band, λ column,
  KL-from-`mono_all`), and correct §27.5's "single seed" caveat. Open and unscheduled:
  **H-cons-scale** (does the X1 gain survive at 13B/34B?) and **H-cons-teacher** (does a 34B
  `tuned_L0` teacher lift a 7B student past its own 0.32 on X1?). The format gate is open for the
  human to re-specify.
