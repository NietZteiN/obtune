### Target Date: 2026-09-08 (Read — RQ-A / RQ-B at 34B: the stacking dissociation holds at every scale, and H-cons-stack-strict now clears zero at 13B *and* 34B)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` (RQ1′ composite_scale,
  before the 09-07 submission) and identical to the 7B/13B reads. **RQ-A** CONFIRMED iff
  `mono_all − tuned_L0` pooled over the six depth-2 composites has ci_lo > 0; **RQ-B** CONFIRMED iff
  `cons_lam3 − tuned_L0` pooled has ci_lo > 0. **H-cons-stack-strict** (opened 09-07 after the 7B
  lower bound landed at −0.02): `cons_lam3 − mono_all` pooled ci_lo > 0.
- **Setup:** `ev_composite_34b` **382516** → `an_composite_34b` **382518** (`35_composites.py
  --model codellama-34b --phase composite_scale`, systems `tuned_L0 / mono_all / cons_lam3`, `base`
  omitted as at 13B; `results/analysis/pipeline/composite_scale_codellama34b.json`). 18 cells,
  same six composites and same rows-per-program as the 7B and 13B reads. No H1.
- **Results (accuracy, 34B):**

  | system | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 | pooled |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | `tuned_L0` | 0.3224 | 0.3488 | 0.3639 | 0.4313 | 0.4509 | 0.4799 | 0.4073 |
  | `mono_all` | 0.3982 | 0.3966 | 0.4030 | 0.4535 | 0.4575 | 0.4889 | 0.4377 |
  | `cons_lam3` | **0.4230** | **0.4254** | **0.4246** | **0.4763** | **0.4826** | **0.5201** | **0.4635** |

  Pooled contrasts, pts [95 % CI], program-clustered bootstrap:
  - `mono_all − tuned_L0` **+3.05** [+1.60, +4.50]* — per composite +7.58 / +4.79 / +3.91 / +2.22 /
    +0.66 / +0.90, all six positive. **RQ-A CONFIRMED** (third scale in a row: 7B +3.49, 13B +2.90,
    34B +3.05).
  - `cons_lam3 − tuned_L0` **+5.63** [+4.46, +6.82]* — +10.06 / +7.66 / +6.07 / +4.50 / +3.17 / +4.02.
    **RQ-B CONFIRMED** (7B +4.76, 13B +4.26, 34B +5.63).
  - `cons_lam3 − mono_all` **+2.58** [+1.26, +3.90]* — +2.47 / +2.87 / +2.15 / +2.28 / +2.52 / +3.12,
    remarkably flat across composites. **H-cons-stack-strict CONFIRMED at 34B**, as it was at 13B
    (+1.36 [+0.18, +2.55]); only the 7B lower bound (−0.02) fell short, and by 0.02.
- **Reading.** The dissociation that defines RQ1′ — breadth buys robustness to *recombination of seen*
  transforms and pays for it on *unseen* families — is now measured at 7B, 13B and 34B with the same
  sign and a stable magnitude (+3.49 / +2.90 / +3.05 stacked-seen against −3.79 / −4.28 / −2.64 on
  X1). It is not a small-model artefact. Consistency's stacked-seen advantage over breadth *grows*
  with scale (+1.27 → +1.36 → +2.58), while its X1 advantage over breadth is stable (+4.59 → +3.95 →
  +3.38): at 34B `cons_lam3` beats both baselines on every one of the six composites, on X1, on the
  seen singles and on L0 — there is no column left on which it loses. That is the strongest statement
  the campaign supports for RQ3′ and it is now backed by 18 + 7 cells at each of three scales.
- **Where the breadth gain comes from, again.** As at 7B and 13B, breadth's composite gain is
  concentrated on the identifier×structural pairs that include S1 (+7.58 / +4.79 / +3.91) and nearly
  vanishes on S3/S4-containing pairs (+0.66 / +0.90) — which the 13B read already attributed to the
  clean-only model handling S3/S4 well on its own. Consistency's gain over breadth does *not* have
  this shape (+2.15 … +3.12): it is a uniform lift, consistent with the "it distils the clean-code
  teacher" mechanism rather than with learning any specific transform.
- **Caveats.** Single seed at 34B (as everywhere at scale); `base` not evaluated on the 34B composites
  (omitted by design to save GPU-hours, so no "vs base" number here); the same 557-program set as the
  singles, so the composite subset is the depth-2 coverage set, not the depth-3/4 common subset.
- **Next:** none for this question. §6.1's "stacked-seen, depth 2" 34B cell is filled; RQ-A / RQ-B
  are closed at three scales; H-cons-stack-strict is closed. Docs: `docs/RQ_SUMMARY.md` §6 RQ1′/RQ3′
  rows and §6.1, `docs/PAPER_EXPERIMENTS.md` stage map.
