### Target Date: 2026-09-05 (Span-pooled L_align: the control separates, the comparison that matters does not)

Lever 3b evaluated (`al_span_cache` 377864, arms 377865–67, ckpt 377868–70, `ev_span` 377871):
`L = L_task(x̃) + λ · L_align`, where `L_align` is the MSE between the tuned model's mean-pooled
hidden states **over the code span** of the obfuscated program and the frozen base model's over
the clean L0 parent, at layers {4, 10, 16, 21, 25, 30}. **H1 is not read.** Six-condition
trainable heldout grid, 9,582 items / 557 programs, program-clustered bootstraps.
Pre-registration: [`2026-09-05_span-pooled-alignment-submitted.md`](2026-09-05_span-pooled-alignment-submitted.md).

- **Hypothesis — H-align-span: PASSES ITS RULE, MARGINALLY.** The W5 rule is: matched >
  mismatched, **and** matched − `mono_all` excludes zero on ≥ 1 non-L0 condition, **and** no L0
  tax. All three hold for λ=3 — but only just, and the pass rests on a single cell.
- **The control separates cleanly, which is the part worth trusting.** Two independent signals
  say the objective is doing something specific rather than acting as a generic regulariser:
  1. During training, `align_loss` with **mismatched** targets plateaus at **0.214** and never
     descends, against the matched arm's **0.066** — the matched arm is fitting the *correct*
     clean-code states, not any low-rank projection that shrinks a pooled MSE.
  2. On heldout, **λ=3 − mismatched = +1.38 [+0.19, +2.58]** pooled, and +2.65 [+0.80, +4.57] on
     `S1`. The mismatched control itself sits *below* `mono_all` (−0.56 [−1.78, +0.64]).
- **Results:**

  | cond | λ=1 | λ=1 mism. | λ=3 | `mono_all` | λ=3 − `mono_all` |
  |---|---|---|---|---|---|
  | L0 | 0.411 | 0.402 | 0.415 | 0.412 | +0.30 [−1.26, +1.86] |
  | L1b | 0.392 | 0.376 | 0.392 | 0.387 | +0.54 [−0.90, +2.00] |
  | L1r | 0.378 | 0.378 | 0.384 | 0.384 | +0.00 [−1.50, +1.50] |
  | L2 | 0.387 | 0.378 | 0.393 | 0.378 | **+1.50 [+0.12, +2.99]** |
  | S1 | 0.388 | 0.373 | 0.399 | 0.383 | +1.68 [−0.08, +3.53] |
  | S2 | 0.419 | 0.405 | 0.416 | 0.405 | +1.08 [−0.66, +2.82] |
  | **pooled** | | | | | **+0.81 [−0.15, +1.89]** |

  λ=3 − `tuned_L0` is +1.38 [+0.06, +2.65]. λ ordering on val (λ=3 0.3745 > λ=1 0.3594 >
  mismatched 0.3505) reproduces on heldout, so more alignment weight is monotonically better
  across the range tested — the arm is not at an interior optimum and λ > 3 was never tried.
- **Why this is reported as marginal rather than a win.** The rule's second clause is satisfied by
  **one cell of six** (`L2`, +1.50 [+0.12, +2.99]), and BH-FDR across the six conditions as one
  family — which CLAUDE.md §4 requires for the transfer matrix and is the right standard here —
  would not keep it. The contrast that actually decides whether the lever matters, λ=3 against
  `mono_all` pooled, is **+0.81 [−0.15, +1.89]**: positive, consistent in sign on five of six
  conditions, and not established. **The honest summary is: the alignment signal is real and
  specific (the control proves that), and its effect on accuracy is at the edge of detection.**
  Recording it as a clean confirmation would repeat the error
  [`../transfer/2026-09-03_cis-and-three-corrections.md`](../transfer/2026-09-03_cis-and-three-corrections.md)
  was written to correct.
- **Context that matters more than the sign.** +0.81 pooled sits inside the 1.8-pt band that
  contains every 7B arm in this campaign (`results/analysis/campaign_ranking_2026-09-05.json`),
  against +8.56 for one step of scale. Even read at its most favourable, this lever is small.
- **What did not happen:** no H1 read; checkpoints chosen on val only (λ=1 ckpt-838, mismatched
  ckpt-419, λ=3 ckpt-838); no λ tuned on heldout.
- **Next:** the cheap and well-motivated follow-up is λ ∈ {6, 10} — the effect is monotone in λ
  across the whole range tested and the ceiling has not been found. Not queued: on the evidence
  above the plausible upside is ~1–2 pts, which does not compete with the 34B result for GPU time.
- **Provenance:** cells `results/cells/rq2_generic/codellama-7b/python/align_span_*__*`; cache
  `runs/align_cache/codellama-7b/python/L0-L1b-L1r-L2-S1-S2_s17__best__span.npz`
  (5,019 × 6 × 4096, valid 5,019/5,019); adapters `runs/adapters_align/codellama-7b/python/*_span_*`;
  span-mask gate `scripts/check_span_mask.py` recall = precision = 1.000 on all six conditions.
