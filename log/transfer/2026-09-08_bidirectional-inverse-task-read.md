### Target Date: 2026-09-08 (Read — RQ5′: output-prediction tuning does NOT teach input prediction; +18 pts forward becomes −1.7 pts backwards)
- **Hypotheses / what we're testing:** the five pre-registered rules of the 09-08 setup entry
  ([`2026-09-08_bidirectional-inverse-task-submitted.md`](2026-09-08_bidirectional-inverse-task-submitted.md),
  frozen in `832a6cb` before submission). Nothing was re-specified after the read; the numbers below
  are `an_inverse` (job **382622**, `results/analysis/pipeline/inverse_codellama7b.json`) as written.
- **Setup:** jobs **382620** (`ev_inverse_core`, 15:18) and **382621** (`ev_inverse_specialists`,
  13:20) produced all 77 cells (11 arms × 7 conditions) of phase `inverse_generic`; `an_inverse`
  ran 35 s. Cluster-bootstrap by `program_id`, n_prog = 557 seen6 / 405 X1 (coverage, not a
  filter). Forward numbers are the existing Grid A cells. The 3 h asked of SLURM for each eval was
  ~12× what it needed — the inverse task caps at 128 output tokens.
- **Results:**
  - **Format gate: nobody blocked.** Pooled-seen6 `format_fail`: `cons_lam3` 0.014, `tuned_L1b`
    0.030, `mono_all` 0.035, `base` 0.035, `formatonly` 0.037, `tuned_X1` 0.054, `tuned_L1r`
    0.054, `tuned_L2` 0.070, `tuned_S2` 0.097, `tuned_S1` 0.141, **`tuned_L0` 0.187** — under the
    0.25 threshold, but `tuned_L0` fails to emit a parsable call on **32 % of S1 and 42 % of S2**
    items (7 % on L0). The forward-only adapter's inverse failures on structural code are largely
    format, not wrong values. The pre-read expectation that `base` might fail the gate was wrong:
    the one-shot demonstration is enough for every arm.
  - **Pooled accuracy, inverse vs forward** (seen6 mean; X1 separately):

    | arm | inv seen6 | fwd seen6 | inv X1 | fwd X1 | inv `format_fail` |
    |---|---:|---:|---:|---:|---:|
    | `base` | 0.290 | 0.204 | 0.257 | 0.119 | 0.035 |
    | `formatonly` | 0.285 | 0.222 | 0.250 | 0.125 | 0.038 |
    | `tuned_L0` | 0.271 | 0.386 | 0.221 | 0.270 | 0.192 |
    | `mono_all` | 0.277 | 0.393 | 0.237 | 0.232 | 0.035 |
    | `cons_lam3` | 0.295 | 0.405 | 0.281 | 0.283 | 0.014 |
    | `tuned_X1` | 0.306 | 0.370 | 0.290 | 0.319 | 0.053 |
    | `tuned_L1b` | **0.346** | — | **0.302** | — | 0.030 |
    | `tuned_L1r` | 0.287 | — | 0.226 | — | 0.055 |
    | `tuned_L2` | 0.297 | — | 0.246 | — | 0.071 |
    | `tuned_S1` | 0.288 | 0.383 | 0.249 | 0.272 | 0.141 |
    | `tuned_S2` | 0.281 | 0.391 | 0.213 | 0.286 | 0.100 |

    The second pre-read expectation was also wrong: base **inverse** accuracy (0.29) is *above*
    base forward (0.20), not below it — execution grading accepts any call that reproduces the
    value, and for many programs a trivial input does. The inverse task is easier for an untuned
    model and harder to improve.
  - **Contrasts (inverse task, pts, cluster-bootstrap 95 % CI, `*` excludes zero):**

    | contrast | Δ | note |
    |---|---:|---|
    | `tuned_L0 − base` @ seen6 | **−1.67 [−3.29, −0.04]*** | forward: +18.09 [+16.11, +20.19]* |
    | `tuned_L0 − formatonly` @ seen6 | −1.22 [−2.82, +0.37] | |
    | `formatonly − base` @ seen6 | −0.45 [−0.76, −0.12]* (equiv ±1.0) | format residue ≈ 0; forward +1.84* |
    | `mono_all − tuned_L0` @ obf | +1.45 [−0.04, +2.94] | |
    | `cons_lam3 − mono_all` @ obf | +1.73 [+0.25, +3.27]* | |
    | `cons_lam3 − tuned_L0` @ obf | +3.18 [+1.63, +4.70]* | |
    | `mono_all − base` @ seen6 | −1.30 [−3.01, +0.36] | forward +18.73* |
    | `cons_lam3 − base` @ seen6 | +0.49 [−1.38, +2.30] | forward +20.00* |
    | `tuned_X1 − tuned_L0` @ X1 | **+7.00 [+4.12, +9.96]*** | |
    | `tuned_X1 − base` @ X1 | +3.37 [+0.41, +6.34]* | the one above-base transfer |
    | `mono_all − tuned_L0` @ X1 | +1.65 [−1.15, +4.36] | |
    | `tuned_L1b − tuned_L0` @ L1b | +9.46 [+7.17, +11.87]* | vs base +8.1 (0.346 vs 0.265) |
    | `tuned_L1r − tuned_L0` @ L1r | −1.50 [−3.59, +0.54] | |
    | `tuned_L2 − tuned_L0` @ L2 | −0.24 [−2.40, +1.86] | |
    | `tuned_S1 − tuned_L0` @ S1 | +9.38 [+6.49, +12.50]* | vs base +2.1 (0.282 vs 0.261) |
    | `tuned_S2 − tuned_L0` @ S2 | +8.45 [+6.06, +11.03]* | vs base **−3.7** (0.293 vs 0.330) |

  - **Direction ratio** DR = (inv − inv_base)/(fwd − fwd_base), pooled seen6: `formatonly` −0.24,
    `tuned_L0` **−0.09**, `mono_all` −0.07, `cons_lam3` +0.03, `tuned_X1` +0.10. At most a tenth
    of any forward gain survives the flip; for two of the five arms the sign reverses.
  - **BH-FDR over the five primary contrasts:** only `tuned_X1 − tuned_L0` @ X1 survives
    (p = 0.001, q = 0.005). `tuned_L0 − base` q = 0.068, `mono_all − tuned_L0` q = 0.068,
    `cons_lam3 − mono_all` q = 0.065, `tuned_L0 − formatonly` q = 0.14. Verdicts use the CIs as
    registered; the q-values are reported beside them.
- **What worked / hypothesis verdict:**
  - **H-inv-transfer — REFUTED.** `tuned_L0 − base` is negative with a CI excluding zero
    (−1.67*), and `tuned_L0 − formatonly` is not positive. The adapter that gains **+18 pts** on
    output prediction loses **1.7 pts** on input prediction over the same programs. Nikiema et
    al.'s "cognitive specialization" replicates at value level: forward tuning teaches the forward
    task, not a direction-free model of the program.
  - **H-inv-breadth — INCONCLUSIVE** (+1.45 [−0.04, +2.94]); the lower bound touches zero.
  - **H-inv-cons — CONFIRMED** (+1.73*), and `cons_lam3 − tuned_L0` @ obf +3.18*. **But read the
    absolute:** `cons_lam3 − base` is +0.49 [−1.38, +2.30]. The consistency objective does not
    teach inversion; it *avoids the damage* the SFT arms take (`cons_lam3` has the lowest
    `format_fail` of any arm, 1.4 %). "Keeps the gain" is the wrong gloss; "does no harm" is right.
  - **H-inv-family — CONFIRMED** (+7.00*), and this is the one result that survives FDR **and**
    beats base (`tuned_X1 − base` @ X1 +3.37*). Forward training on the X1 family is the only
    forward training that transfers to the inverse task above the untuned model — on its own
    family. The family unit holds backwards; nothing else does.
  - **H-inv-diagonal — CONFIRMED by the registered rule** (3/5: L1b +9.46*, S1 +9.38*, S2
    +8.45*; L1r, L2 null), **but the rule compares against `tuned_L0`, which is depressed on
    exactly those conditions.** Against `base`, `tuned_L1b` on L1b is +8.1, `tuned_S1` on S1 is
    +2.1, and `tuned_S2` on S2 is **−3.7**. The S1/S2 "diagonal" gains are mostly recovery of
    `tuned_L0`'s format collapse on structural code, not specialist competence at inversion. The
    verdict stands as registered; the paper must carry the base comparison next to it.
- **Observations (unregistered, flagged as such):**
  - **`tuned_L1b` is the best inverse arm on every one of the seven conditions** (0.346 pooled,
    +5.6 over base; 0.302 on X1, +4.5 over base) — a forward specialist on *misleading* names
    helps the inverse task everywhere, while the random-hex (`L1r`) and minified (`L2`) specialists
    do nothing. One reading: L1b training is the only forward signal that penalises trusting
    identifiers, so it is the only one that forces the model toward values. This is a single seed
    and was not a hypothesis; it is a candidate for RQ4′'s mechanism story, not a finding.
  - Forward and inverse orderings do not match. Forward: `cons_lam3` > `mono_all` > `tuned_L0` >
    `tuned_X1` > `base`. Inverse: `tuned_X1` > `cons_lam3` > `base` > `mono_all` > `tuned_L0`.
    Breadth (`mono_all`) is exactly at base on the inverse task; the forward-only adapter is below it.
  - `tuned_L0`'s inverse profile is condition-shaped: it *gains* on L0/L2/L1r (+4.0/+4.2/+1.1
    over base) and *loses* on L1b/S1/S2 (−1.3/−7.3/−12.1). The forward adapter transfers
    backwards on code that looks like its training data and collapses (via format) on code that
    does not — the same shape as the forward "breadth hurts on X1" result, now in the other direction.
- **New questions / new hypotheses:** (i) an inverse-trained or bidirectionally-trained adapter
  would test whether the asymmetry is a training-signal property or a task property — not
  registered, not run; (ii) whether `tuned_L1b`'s inverse advantage replicates on s42 is a
  one-adapter question that would settle whether the observation above is real; (iii) the DR
  of `cons_lam3` at 13B/34B once E3 lands.
- **Next Steps:** RQ_SUMMARY §6.3 table filled; PAPER_EXPERIMENTS E16 → done; re-run `report`
  (`--only report`) since the queued 382561 predates `an_inverse`. Nothing is tuned on the read.
