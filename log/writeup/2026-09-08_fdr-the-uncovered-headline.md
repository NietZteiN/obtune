### Target Date: 2026-09-08 (E7c — the `mono_all`-controlled FDR family, frozen before its read: RQ3′'s headline survives multiplicity at q = 0.005, and every λ and every seed survives with it)
> Continues [`2026-09-08_fdr-family-enlarged.md`](2026-09-08_fdr-family-enlarged.md), the same day.
> That entry found the gap and deliberately left it open; this one closes it the only way it could
> honestly be closed — by freezing the rule first and running second.
- **Hypotheses / what we're testing:** the E7b read found that every FDR family in the project is
  controlled against `tuned_L0`, which leaves RQ3′'s actual headline — `cons_lam3 − mono_all` @ X1 —
  **in no family at all**. Adding a family on the spot would have been indistinguishable, to a
  reader, from choosing a family in which the headline survives. So the rule went into
  `CLAUDE_SCRATCHPAD.md` and was committed as **`8da96b4`** before `--control-family` existed as
  code: one family, membership **discovered from the directory tree** (every system holding all seven
  generic cells), controlled against **`mono_all`**, 7 conditions, survives iff q < 0.05. Reported;
  gates nothing.
- **Setup:** `an_fdr3` **383172** (`37_fdr_family.py --control-family mono_all`,
  `results/analysis/pipeline/fdr_mono_codellama7b.json`). 30 systems discovered → **203 tests**,
  the same size as E7b's `arms_all`, which is the point: this is the same family with the control
  swapped, not a smaller one chosen to make a q-value work. CodeLlama-7b, Python, heldout. No H1.
- **Results — 54 of 203 survive.**

  | contrast (vs `mono_all`) | Δ pts [95 % CI] | q (BH over 203) |
  |---|---:|---:|
  | **`cons_lam3` @ X1** — *the headline* | **+4.86** [+2.88, +6.83] | **0.0049** |
  | `cons_lam3_s42` @ X1 | +4.70 [+2.72, +6.75] | 0.0049 |
  | `cons_lam3_s101` @ X1 | +4.12 [+2.14, +6.18] | 0.0049 |
  | `cons_lam1` @ X1 | +2.96 [+1.15, +4.70] | 0.0049 |
  | `cons_lam5` @ X1 | +3.95 [+1.89, +5.93] | 0.0049 |
  | `cons_lam10` @ X1 | +4.78 [+2.72, +6.84] | 0.0049 |
  | `tuned_L0` @ X1 (C1, the other direction) | +3.79 [+1.56, +6.09] | 0.0166 |
  | `tuned_X1` @ X1 | +8.24 [+5.84, +10.78] | 0.0049 |
  | `mono_quarter` @ X1 (E12) | +3.05 [+0.99, +5.10] | 0.0278 |
  | `cons_tmono` @ X1 (E4's breadth teacher) | +0.66 [−0.91, +2.31] | 0.61 |
  | `cons_lam3` @ L0 | +0.84 [−0.84, +2.57] | 0.56 |

- **Reading.**
  1. **RQ3′'s headline is corrected and survives**, at q = 0.0049 in a 203-test family — the same
     family size that E7b used for the `tuned_L0`-controlled check. The gap E7b recorded is closed,
     and closed in the order that makes the result mean something.
  2. **It survives at all three seeds and all four λ values.** s17/s42/s101 give +4.86/+4.70/+4.12
     and λ = 1/3/5/10 give +2.96/+4.86/+3.95/+4.78, every one of them at q ≤ 0.005. A result that
     survives multiplicity at seven independent settings of its own hyperparameters is not a draw.
  3. **22 of the 29 X1 cells survive, and 0 of `cons_lam3`'s 6 non-X1 cells do.** That is exactly the
     shape the campaign has always claimed and never before tested this way: consistency's advantage
     over breadth is **specifically on the unseen family**, not a general superiority. Its
     seen-condition and L0 advantages over `mono_all` (+0.54 to +1.68, q = 0.23–0.72) do **not**
     survive multiplicity and must not be quoted as if they did.
  4. **`cons_tmono` at +0.66 (q = 0.61) is E4 corroborated by a second method.** A consistency arm
     with a *breadth* teacher is statistically indistinguishable from breadth itself on X1 — the tax
     is inherited from the teacher, exactly as the teacher-variation experiment concluded.
- **Caveats.** Same duplicate-cell caveat as E7b: `arms_vs_mono_all` resolves cells across six phases
  and point estimates can differ from a three-phase resolution by up to ~0.4 pts. The bootstrap-p is
  still a substitute for the GLMM (`an_glmm` runs separately); BH assumes nothing about dependence
  that would be violated here, but the 203 tests share one control, so they are positively dependent
  and BH is conservative in that setting rather than anti-conservative.
- **Next:** nothing for this question. The GLMM (E7d) is the remaining piece of E7 and is a different
  estimator on the same contrasts, not another family. Docs: `docs/RQ_SUMMARY.md` §6 RQ3′/RQ4′,
  `docs/PAPER_EXPERIMENTS.md` E7.
