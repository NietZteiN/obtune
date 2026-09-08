### Target Date: 2026-09-08 (E7d — the GLMM the charter has asked for since the beginning, finally fitted: 4/4 headline contrasts agree with the bootstrap)
- **Hypotheses / what we're testing:** CLAUDE.md §4 specifies **item-level binomial GLMMs with
  crossed random effects**, and every interval this project has ever published is a
  program-clustered bootstrap labelled as a substitute — because lme4 did not survive the migration
  and `statsmodels` was never in the pinned env. Rule frozen in `CLAUDE_SCRATCHPAD.md`
  (pre-registration #2, **`8da96b4`**) before the fit: for each headline contrast the GLMM
  **agrees** iff its posterior mean has the same sign as the bootstrap point **and** its 95 %
  credible interval excludes zero iff the bootstrap CI did. Disagreements are reported as
  disagreements. REPORTED; gates nothing; replaces no existing number.
- **Setup:** `an_glmm` **383180** (`scripts/analysis/45_glmm.py`, 9 min on `normal`).
  `statsmodels` was **not** installed into the training env — it went into a separate venv
  (`/work/jvl210002/migration/envs/obtune-stats`) and the script re-execs itself there, so an
  analysis convenience cannot move a torch/scipy pin under a queued training job. Model, per
  condition: `correct ~ C(system, Treatment(control)) + (1|program_id) + (1|item_id)`, fitted by
  `BinomialBayesMixedGLM` (variational Bayes) over 40,600 item-level rows, 5 systems × 7 conditions.
  One fit per condition so each coefficient *is* the contrast at that condition rather than an
  interaction sum. Reported on the **logit** scale: a GLMM coefficient is a log-odds ratio and
  converting it to "points" would invent a number the model never estimated. No H1.
- **Results — the pre-registered agreement check:**

  | contrast | bootstrap | GLMM (logit) | |
  |---|---:|---:|---|
  | `mono_all − tuned_L0` @ X1 (**C1**) | −3.79 pts* | **−0.546** [−0.761, −0.331]* | AGREES |
  | `cons_lam3 − mono_all` @ X1 (**RQ3′**) | +4.86 pts* | **+0.698** [+0.492, +0.904]* | AGREES |
  | `mono_all − tuned_L0` @ L1b | +2.90 pts* | **+0.354** [+0.186, +0.523]* | AGREES |
  | `tuned_X1 − tuned_L0` @ X1 | +4.86 pts* | **+0.636** [+0.436, +0.837]* | AGREES |

  **4/4.** The project's two headline claims and its two supporting ones survive a change of
  estimator, of error model and of scale.
- **Where the GLMM is *sharper* than the bootstrap, and why that must be read carefully.** Modelling
  item difficulty as a random effect removes variance the bootstrap leaves in the residual, so
  several contrasts that the bootstrap could not separate from zero have credible intervals that
  exclude it: `mono_all − tuned_L0` @ **L0** −0.218 [−0.397, −0.040] (the L0 cost, which no
  bootstrap or FDR pass has ever resolved), `cons_lam3` @ L1r +0.204 [+0.027, +0.382] and @ S1
  +0.242 [+0.045, +0.440], `tuned_X1`'s losses on L1b/L1r/L2 (−0.233/−0.247/−0.430). **None of these
  is promoted to a claim here.** Three reasons, all of which the paper must state: they are
  **uncorrected for multiplicity** (the FDR families are the corrected instrument and they say
  otherwise); `fit_vb` is a **variational** approximation whose credible intervals are known to be
  optimistically narrow; and the campaign's pre-registered inference is the bootstrap, so switching
  to whichever estimator makes a borderline number significant is exactly the practice these rules
  exist to prevent. The honest statement is: **the L0 cost is real in direction and small, resolved
  by an estimator that pools item difficulty and not by the one the claims are registered on.**
- **What this closes.** E7's "largest methodological gap in the report" is closed for the FDR half
  (three families, 09-08) and now for the GLMM half. The remaining shortfall is honest and stated:
  the charter's *crossed program × model* structure is implemented as program × item within one base
  model, because the panel's other scales do not have the same item sets; and lme4 is still absent,
  so this is a Python VB fit rather than the R REML/Laplace fit the charter named.
- **Caveats.** 7B only; VB not MCMC; per-condition fits rather than one interaction model (chosen for
  interpretability, and it means no formal test of a condition × system interaction); the item random
  effect is identified only because every item is scored by all five systems.
- **Next:** none required. If lme4 ever returns, re-fitting is a day's work and the comparison is
  already specified. Docs: `docs/PAPER_EXPERIMENTS.md` E7, `docs/RQ_SUMMARY.md` §6 RQ4′.
