### Target Date: 2026-09-07 (stacked obfuscation on CodeLlama-7b — RQ-A / RQ-B read)
- **Hypotheses / what we're testing:** Pre-registered in `CLAUDE_SCRATCHPAD.md` (2026-09-07, frozen
  before job 382427 was submitted).
  - **RQ-A / H-stack-dissociation.** On CodeLlama-7b, `mono_all − tuned_L0` pooled over the six
    composite conditions excludes zero ABOVE — while the same pair is negative on the unseen column
    (X1: `tuned_L0 − mono_all` +3.79 [+1.65, +6.09]). CONFIRM if the pooled composite interval is
    above zero; REFUTE if null or negative. Qwen reference: +3.91.
  - **RQ-B / H-cons-stacking.** `cons_lam3 − tuned_L0` pooled on composites excludes zero above AND
    `cons_lam3 − mono_all` pooled does not exclude zero from below.
- **Setup:** `configs/eval/composite_generic.yaml` — 5 systems (base, tuned_L0, mono_all, cons_lam3,
  tuned_S2) × 6 composites (C_L1b_S1, C_L1r_S1, C_S1_L1r, C_L2_S4, C_L1r_S3, C_S4_S3), 1,667 items
  each, python, vLLM multi-LoRA. Job 382427 `ev_composite`, h200, 535 s wall. Analysis
  `scripts/analysis/35_composites.py` (new) → `results/analysis/composites_codellama7b_2026-09-07.json`;
  bootstrap clustered by raw `snippet_id` (a program under two composites is ONE cluster), n_boot 2000,
  seed 17. Qwen replicate on the same script with `--alias tuned_L0=tuned_L0_s17` →
  `composites_qwen1.5b_2026-09-07.json`. No H1 cell read.
- **Results:** (accuracy; pooled over six composites)

  | system | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 | pooled |
  |---|---|---|---|---|---|---|---|
  | base | .1413 | .1309 | .1349 | .1758 | .1719 | .1860 | .1598 |
  | tuned_L0 | .2785 | .2937 | .2849 | .3551 | .3599 | .3923 | .3333 |
  | mono_all | .3448 | .3496 | .3264 | .3851 | .3796 | .4031 | .3683 |
  | **cons_lam3** | **.3599** | **.3559** | **.3488** | **.3923** | **.3868** | **.4223** | **.3809** |
  | tuned_S2 | .2857 | .3033 | .3009 | .3701 | .3766 | .4199 | .3493 |

  Contrasts (pts, program-clustered 95 % CI; * excludes zero):
  - `mono_all − tuned_L0` **+3.49 [+2.04, +5.01]*** — per composite +6.62 / +5.59 / +4.15 / +3.00 / +1.98 / +1.08, all six positive.
  - `cons_lam3 − tuned_L0` **+4.76 [+3.53, +6.05]*** — +8.14 / +6.23 / +6.38 / +3.72 / +2.69 / +3.00.
  - `cons_lam3 − mono_all` **+1.27 [−0.02, +2.59]** — all six per-composite point estimates positive (+0.64 … +2.23).
  - `tuned_S2 − tuned_L0` +1.60 [+0.72, +2.45]*; `tuned_L0 − base` +17.36 [+16.25, +18.48]*.
  - Order pair: tuned_L0 C_L1r_S1 .2937 vs C_S1_L1r .2849 (+0.9); mono_all .3496 vs .3264 (+2.3);
    cons_lam3 .3559 vs .3488 (+0.7). Identifier-first (C_L1r_S1) is easier for every tuned CodeLlama
    system (base reverses by 0.4); on Qwen base (+1.3), tuned_L0 (+2.6) and mono_all (+0.8) go the
    same way, tuned_S2 the other way (−3.3). Identifier-first is easier in 7 of 9 model×system
    comparisons, ≤2.6 pts where it holds — a small, mostly consistent order effect.
  - format_fail: 1.6–2.7 % across cells (tuned_S2__C_S4_S3 2.4 %). Reported, not gated.
  - Qwen replicate (same script, raw-program clustering): `mono_all − tuned_L0` +3.91 [+2.58, +5.27]*.
    Qwen `base`/`tuned_S2` composite cells come from an earlier, different item set (zero snippet
    overlap with `tuned_L0_s17`) and are NOT comparable; only the mono/L0 pair is reported for Qwen.
- **What worked / hypothesis verdict:**
  - **RQ-A CONFIRMED.** The dissociation replicates on CodeLlama-7b at almost the same magnitude as
    Qwen (+3.49 vs +3.91). One model, one grid: breadth is **+3.5 on stacked-seen** and **−3.8 on
    unseen** (X1). This is the signed trade the paper's RQ1′ is built on.
  - **RQ-B CONFIRMED.** `cons_lam3` beats `tuned_L0` by +4.76 on composites and is not below
    `mono_all` (point +1.27, lower bound −0.02). Consistency keeps breadth's stacking robustness
    while it already carries none of breadth's held-out tax (+4.59 on X1) or L0 tax (−0.30). The
    stronger claim "cons_lam3 strictly beats mono_all on composites" is NOT established: the interval
    grazes zero. It would need the 13B/34B replicate (E3) or a second seed to settle.
- **Observations:** (i) The composite gain of breadth is monotone in how much the identifier
  component contributes: largest on C_L1b_S1 / C_L1r_S1 (+6.6 / +5.6), smallest on the
  structural-only stack C_S4_S3 (+1.1) — on Qwen the latter was −1.0. Breadth helps stacked
  conditions mostly through the identifier transforms it has seen, which is what a "family" account
  predicts. (ii) `tuned_S2` (structural specialist) gains +1.6 pooled with its largest gain on
  C_S4_S3 (+2.8) — the specialist helps where its own family is stacked. (iii) tuned_L0's stacking
  cost vs the singles is not computed here; §4 of RQ_SUMMARY has the Qwen figure (−8.23).
- **New questions / new hypotheses:** H-cons-stack-strict (cons_lam3 > mono_all on composites,
  excludes zero) — test on 13B/34B when the E3 adapters exist (`composite_scale`). H-stack-depth
  (RQ-C): does the breadth advantage grow or shrink at depth 3–4? H-stack-identifier: is the
  breadth gain on composites carried entirely by the identifier component? (test: composites
  paired with/without an identifier transform; the C_S4_S3 row already suggests yes.)
- **Next Steps:** Fold into RQ_SUMMARY §4 and the revised RQ set (§6); add `composite_scale` and the
  depth-3/4 composites to the autonomous pipeline; E3 chains (382139–382142) still pending.
