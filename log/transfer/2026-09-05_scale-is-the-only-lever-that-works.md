### Target Date: 2026-09-05 (CodeLlama-34B: H-34b CONFIRMED — scale buys +8.6 pts, and buys it entirely through tuning)

`base`/`tuned_L0`/`mono_all` on CodeLlama-34B-Instruct over the six-condition trainable heldout
grid (`ev34_grid` 377817), item-for-item against 13B and 7B on the same 9,582 items / 557
programs. **H1 is not read**; `final_eval` stays unspent. Intervals are 2,000-resample
bootstraps clustered by `program_id`. Pre-registration:
[`2026-09-04_trace-sft-and-34b-submitted.md`](2026-09-04_trace-sft-and-34b-submitted.md).

- **Hypothesis — H-34b: CONFIRMED.** The rule was `tuned_L0(34b) − tuned_L0(13b)` > 0 with the
  interval excluding zero and the tuned-over-base gap intact. It is **+5.17 [+3.78, +6.64]**,
  and the gap does not merely survive — it *widens*, from +18.04 at 7B to **+25.13** at 34B.
- **Results:**

  | cond | `base` | `tuned_L0` | `mono_all` | `tuned_L0` 34b − 7b |
  |---|---|---|---|---|
  | L0 | 0.254 | **0.522** | 0.496 | +9.28 [+6.89, +11.56] |
  | L1b | 0.205 | 0.419 | 0.470 | +5.61 [+3.50, +7.73] |
  | L1r | 0.220 | 0.468 | 0.458 | +9.34 [+7.01, +11.62] |
  | L2 | 0.231 | 0.465 | 0.463 | +8.44 [+6.23, +10.72] |
  | S1 | 0.222 | 0.472 | 0.467 | +9.38 [+7.14, +11.86] |
  | S2 | 0.191 | 0.484 | 0.483 | +9.48 [+7.14, +11.69] |
  | **pooled** | | | | **+8.56 [+7.00, +10.15]** |

- **The decisive decomposition — scale does not make the base better, it makes the base more
  teachable.** Read against [`2026-09-05_llama31-probe-fingerprint-replicates.md`](2026-09-05_llama31-probe-fingerprint-replicates.md),
  written the same day, the two model swaps separate cleanly:

  | | base Δ vs CL-7b | tuning gap (`tuned_L0 − base`) |
  |---|---|---|
  | CodeLlama-7b | — | +18.04 [+16.12, +20.20] |
  | **Llama-3.1-8B** (newer, same size) | **+2.08 [+0.19, +3.92]** | +17.18 [+15.23, +19.13] |
  | **CodeLlama-34B** (same family, bigger) | **+1.47 [−0.24, +3.27]** *(null)* | **+25.13 [+22.73, +27.64]** |

  A *newer* base starts ~2 pts ahead and converts tuning identically — the gain is inherited and
  the ladder just shifts. A *bigger* base starts level (its base advantage does not even exclude
  zero) and converts tuning **+7.1 pts better**. Untuned 34B is no better at predicting output
  under obfuscation than untuned 7B; tuned 34B is 8.6 pts better. **The whole 34B gain is
  produced by fine-tuning, not inherited from pretraining.** That is the sharpest statement the
  campaign can make about what capacity is for here: it is not knowledge of obfuscated code, it
  is headroom to learn semantic invariance from the same 26.8k rows.
- **Scale is the only lever that worked.** Against the day's other verdicts — trace SFT null
  ([entry](2026-09-05_trace-sft-is-null-but-complementary.md)), verifier rerank +1.1
  ([entry](2026-09-05_verifier-is-a-good-classifier-and-a-bad-selector.md)), more cases null
  ([entry](2026-09-05_more-cases-per-program-is-null.md)), newer base not promoted — the ladder
  7B → 13B → 34B pays +3.4, then +5.2. Every algorithmic lever tried at 7B is worth ≤ 1 pt;
  capacity is worth 8.6.
- **RQ2 survives scale, and the fingerprint sharpens.** `mono_all − tuned_L0` at 34B is
  **+0.14 [−1.24, +1.53]** — the tie holds at the top of the ladder. And the per-condition
  fingerprint is now measured on four models:

  | model | `L0` cost | `L1b` gain | pooled |
  |---|---|---|---|
  | CodeLlama-7b | −1.74 [−3.78, +0.36] | +2.41 [+0.42, +4.47] | +0.56 |
  | CodeLlama-13b | −2.34 [−4.37, −0.30] | +2.71 [+0.72, +4.83] | +0.77 |
  | **CodeLlama-34b** | **−2.63 [−4.49, −0.78]** | **+5.19 [+3.02, +7.36]** | +0.14 |
  | Llama-3.1-8B | −2.22 [−4.07, −0.30] | +2.83 [+0.96, +4.64] | +0.16 |

  Same signs on every model, across two families and a 5× scale range, with the pooled contrast
  a tie throughout. The `L1b` gain roughly **doubles** at 34B while the `L0` cost grows only
  slightly — breadth training's benefit scales with capacity but its price does not. That is a
  new, testable asymmetry and the first sign that the tie might break upward at larger scale.
- **What did not happen:** no H1 read (the campaign-end `final_eval` batch is still unspent);
  `ck34_L0` best ckpt-74 at val 0.4985, `ck34_mono` selected on val only.
- **Next:** 34B `tuned_L0` is the campaign winner on the trainable grid and the arm to carry
  into the single H1 `final_eval` batch, alongside the X1 arms.
- **Provenance:** cells `results/cells/rq2_generic/codellama-34b/python/{base,tuned_L0,mono_all}__*`;
  adapters `runs/adapters/codellama-34b/python/{L0,L0-L1b-L1r-L2-S1-S2}_r32_s17`
  (`train_loss` 0.376 / 0.108; `tr34_mono` 9.8 h, truncation 32/26,841 at 2048); jobs 377812–377817.
