### Target Date: 2026-09-05 (Execution-trace SFT: H-trace REFUTED; the arm is a near-perfect complement)

Both trace arms evaluated on the six-condition trainable heldout grid (`ev_tr_L0` 377806,
`ev_tr_mono` 377807). **H1 is not read**; `final_eval` stays unspent. Comparisons are
item-for-item against the `rq2_generic` cells (`tuned_L0`, `mono_all`) on the identical
9,582 items / 557 programs; intervals are 2,000-resample bootstraps clustered by
`program_id`. Pre-registration is [`2026-09-04_trace-sft-and-34b-submitted.md`](2026-09-04_trace-sft-and-34b-submitted.md).

- **Hypotheses:**
  - **H-trace — REFUTED.** The pre-registered test was `trace_L0 − tuned_L0` > 0 with the
    interval excluding zero, gain largest on `S1`/`S2`. Both halves fail, and the second
    fails backwards: `S1` is where the trace arm collapses.
  - **H-trace-format — CONFIRMED (control behaves).** `base_trace` pooled 0.104 against
    `base`'s ~0.13 greedy: the trace prompt without trace training is worth *less* than
    nothing, so no part of any trace-arm number is prompt rather than training.
  - **H-trace-complement — NEW, opened by this entry.** The two systems agree far less than
    their equal accuracies suggest, and the union is +10.75 pts [+9.51, +11.98] over
    `mono_all`. Tested by the lever-2b verifier arbitrating between the two answers.
- **Results — `trace_L0` (trained on L0 traces only):**

  | cond | `trace_L0` | `tuned_L0` | `mono_all` | format_fail | at 2048-token cap |
  |---|---|---|---|---|---|
  | L0 | 0.361 | 0.429 | 0.412 | 0.121 | 0.120 |
  | L1b | 0.319 | 0.362 | 0.387 | 0.143 | 0.141 |
  | L1r | 0.319 | 0.375 | 0.384 | 0.157 | 0.154 |
  | L2 | 0.335 | 0.380 | 0.378 | 0.120 | 0.116 |
  | S1 | **0.085** | 0.379 | 0.383 | **0.740** | 0.738 |
  | S2 | 0.241 | 0.389 | 0.405 | 0.221 | 0.220 |

  Two independent failures, separated because the second survives the first:
  1. **Runaway traces.** `format_fail` equals the cap-hit rate to three decimals in every
     cell — the failures are *entirely* traces that never terminate. The model emitted the
     `...` budget cut on **0 of 9,582** outputs although 11.2 % of its training traces end in
     one. A cut token teaches "a trace may be truncated", not "stop at 64 events"; the model
     has no event counter, so the budget was never learnable from the cut alone. This is a
     format defect of trace-v1, not evidence about execution supervision.
  2. **Worse even when it answers.** Conditional on a parsed answer it still trails
     `tuned_L0` on the same items (L0 0.411 vs 0.452; S1 0.327 vs 0.451). A
     trace-then-fall-back-to-`tuned_L0`-on-cap hybrid is −3.65 [−6.00, −1.38] on L0 and
     −7.74 [−9.96, −5.40] on S2, so the format defect does not explain the deficit.
- **Results — `trace_mono` (trained on all six conditions' traces):** the format defect is
  **fixed by distribution, not by format**: `format_fail` 0.011–0.032 (from 0.121–0.740),
  and `S1` recovers from 0.085 to 0.356. Training on S1/S2 traces — which are long — is what
  taught length control; nothing about trace-v1 changed.

  | cond | `trace_mono` | `mono_all` | Δ [95 % CI] | ff |
  |---|---|---|---|---|
  | L0 | 0.392 | 0.412 | −1.98 [−4.49, +0.24] | 0.017 |
  | L1b | 0.382 | 0.387 | −0.48 [−2.89, +1.87] | 0.016 |
  | L1r | 0.384 | 0.384 | +0.00 [−2.40, +2.34] | 0.017 |
  | L2 | 0.377 | 0.378 | −0.12 [−2.45, +2.21] | 0.011 |
  | S1 | 0.356 | 0.383 | −2.65 [−5.46, +0.16] | 0.032 |
  | S2 | 0.389 | 0.405 | −1.56 [−3.78, +0.90] | 0.017 |

  Pooled: `trace_mono − mono_all` **−1.06 [−3.14, +0.75]**, `− tuned_L0` −0.50 [−2.44, +1.52],
  `− trace_L0` +9.59 [+7.97, +11.07]. Every per-condition interval covers zero. **Lever 3 is
  a null**, and an expensive one: 6.3 h of training and a 2048-token generation budget against
  64 for the same accuracy.
- **The finding worth keeping — complementarity.** `trace_mono` and `mono_all` are equal in
  accuracy and substantially *different* in which items they get right: both correct 0.274,
  both wrong 0.501, trace-only **0.107**, mono-only **0.118**. The oracle union is 0.489 vs
  `mono_all`'s 0.392 — **+10.75 pts [+9.51, +11.98]**, uniform across all six conditions
  (per-condition trace-only 0.102–0.114). Execution supervision does change *what* the model
  can do; it just does not raise the count. This is the same shape as the self-consistency
  ceiling (any-of-8 0.559 vs greedy 0.385, [`2026-09-05_verifier-rerank-submitted.md`](2026-09-05_verifier-rerank-submitted.md)):
  a large, real headroom reachable only by a selector. It is now two independent sources of
  ~10-pt headroom for the lever-2b verifier to arbitrate, and unlike sampling, the trace/direct
  pair is two *differently trained* systems rather than eight draws from one.
- **What did not happen:** no H1 read, no selection on anything but val, no config change.
- **Next:** hold lever 3 as reported-null. If `rerank` (377946) clears its decision rule, add
  `trace_mono` as a second candidate source and re-rank the union — the pre-registered test of
  H-trace-complement. A trace-v2 with explicit event numbering (`12:L7 r=3`) would fix defect 1
  at the source, but defect 2 says it would not buy accuracy, so it is not queued.
- **Provenance:** cells `results/cells/trace_generic/codellama-7b/python/{trace_L0,trace_mono,base_trace}__*`;
  training `runs/adapters_trace/codellama-7b/python/{L0,L0-L1b-L1r-L2-S1-S2}_r32_s17`
  (`train_loss` 0.173 / 0.0505, truncation 0/4,688 and 16/26,832 at `max_seq_len` 4096);
  ckpt-select 377804 (best ckpt-222, val 0.339) and 377805 (best ckpt-840, val 0.359).
