### Target Date: 2026-09-08 (pipeline stages an_composite_13b, an_depth — RQ1′ first reads)
- **Hypotheses / what we're testing:** Pre-registered 2026-09-07 (`CLAUDE_SCRATCHPAD.md`, "REVISED
  RQs … PIPELINE PRE-REGISTRATION", commit `0286c5f`). (1) **RQ-A at 13B**: `mono_all − tuned_L0`
  pooled over six depth-2 composites, ci_lo > 0. (2) **RQ-B at 13B**: `cons_lam3 − tuned_L0` ci_lo > 0
  AND `cons_lam3 − mono_all` ci_hi ≥ 0. (3) **RQ-C-persists**: `mono_all − tuned_L0` pooled over
  depth-3/4 composites ci_lo > 0. (4) **RQ-C-grows**: that ci_lo above the depth-2 point (+3.49) →
  CONFIRMED; ci_hi below it → REFUTED; else INCONCLUSIVE. (5) **RQ-C-cons-persists**:
  `cons_lam3 − tuned_L0` on depth-3/4 ci_lo > 0.
- **Setup:** pipeline jobs 382515 → 382517 (`eval/composite_scale.yaml`, codellama-13b, 18 cells,
  9 min 40 s on one H200) and 382519 → 382520 → 382521 → 382522 (`bld_depth` 2.5 min CPU;
  `eval/composite_depth.yaml`, codellama-7b, 20 cells, 8 min 24 s). Depth leg on the `--common`
  subset: **394 programs present in every cell** (S1 bails on some programs by design). Contrasts:
  program-clustered bootstrap, 2,000 resamples, seed 17. Outputs
  `results/analysis/pipeline/composite_scale_codellama13b.json`, `composite_depth_codellama7b.json`.
- **Results:**
  *13B, depth 2* (pooled acc: tuned_L0 0.3699, mono_all 0.3988, cons_lam3 0.4124):
  `mono_all − tuned_L0` **+2.90 [+1.45, +4.37]**; `cons_lam3 − tuned_L0` **+4.26 [+3.02, +5.46]**;
  `cons_lam3 − mono_all` **+1.36 [+0.18, +2.55]**. Per composite, breadth's gain is again ordered by
  identifier content: +4.5/+5.0/+4.1 (identifier+S1) → +0.4/+1.4 (S3/S4 stacks).
  *7B, depth 3/4* (394-program common subset; pooled acc: base 0.1221, tuned_L0 0.3114, tuned_S2 0.3349,
  mono_all 0.3529, cons_lam3 0.3616): `mono_all − tuned_L0` **+4.15 [+2.37, +5.91]**;
  `cons_lam3 − tuned_L0` **+5.02 [+3.41, +6.69]**; `cons_lam3 − mono_all` +0.87 [−0.59, +2.33];
  `tuned_S2 − tuned_L0` +2.35 [+1.21, +3.50]; `tuned_L0 − base` +18.92. The depth-4 stack
  `C4_L1r_S1_S3_S4` is the largest breadth gain (+5.17) and the largest cons gain (+7.20).
- **What worked / hypothesis verdict:**
  - RQ-A (13B) **CONFIRMED** — +2.90, ci_lo +1.45.
  - RQ-B (13B) **CONFIRMED**, and now on the *strict* reading too: `cons_lam3 − mono_all` +1.36
    [+0.18, +2.55] clears zero, where at 7B it grazed it (+1.27 [−0.02, +2.59]).
  - RQ-C-persists **CONFIRMED** (+4.15, ci_lo +2.37). RQ-C-grows **INCONCLUSIVE** by rule: the point
    rises from +3.49 (depth 2) to +4.15 (depth 3/4) but ci_lo +2.37 is below the depth-2 point and
    ci_hi +5.91 is above it. RQ-C-cons-persists **CONFIRMED** (+5.02).
- **Observations:** (i) Breadth's stacked-seen gain is now shown at three scales-or-depths on
  CodeLlama (7B d2 +3.49, 13B d2 +2.90, 7B d3/4 +4.15) plus Qwen (+3.91) — the "buy" side of RQ1′ is
  robust; the point at depth 3/4 is the largest, and the direction is "does not decay", which is what
  a recombination account predicts and a two-transform artefact does not. (ii) The consistency arm
  keeps beating `tuned_L0` by more than breadth does at every depth and scale read so far, and the
  gap over breadth itself is positive everywhere (+1.27 / +1.36 / +0.87), reaching significance at
  13B. (iii) The `--common` subset is 394 of 557 programs; the depth-2 numbers are on all 557, so
  the RQ-C-grows comparison crosses program sets — the rule was written that way and stands, but
  the honest statement is "no decay", not "growth". (iv) The 13B eval took 9 min 40 s and the 34B
  will be ~3×; the 5 h request was safe.
- **New questions / new hypotheses:** whether `cons_lam3 − mono_all` on composites clears zero at
  34B (382518 → 382516, pending) decides if RQ-B's strict reading is a scale trend or a 13B read.
- **Next Steps:** nothing manual; `an_composite_34b` and `an_e3` fire on the 34B chain. Master
  report rev 18 collects all of RQ1′ once the 34B leg lands.
