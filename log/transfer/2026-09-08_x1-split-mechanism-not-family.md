### Target Date: 2026-09-08 (Read — E6 / RQ2′ X1 split: the halves do not transfer to each other, yet either half alone carries ~90 % of the whole on stacked X1)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` (RQ2′, before the 09-07
  submission). **H-family-unit** CONFIRMED iff `tuned_X1m − tuned_L0` @ X1s ci_lo > 0 **and**
  `tuned_X1s − tuned_L0` @ X1m ci_lo > 0 (each half transfers to the other — the family, not the
  mechanism, is the unit); PARTIAL if exactly one; REFUTED if neither. **H-whole-ge-parts** CONFIRMED
  iff neither `tuned_X1m − tuned_X1` nor `tuned_X1s − tuned_X1` @ X1 has ci_lo > 0. **H-mech-dominance**
  and **H-breadth-on-parts** reported, not verdicted.
- **Setup:** X1 split into its guarded-MBA half (**X1m**, 4,263 train pairs / 1,053 held-out items)
  and its string-encoding half (**X1s**, 2,910 / 738 — string encoding needs string literals, so it
  applies to fewer programs; noted before any read). `tr_X1m` (382537's sibling, done 09-07) and
  `tr_X1s` **382803** (resubmitted after the 1.64 % truncation-gate refusal at 2,048; trained with
  `max_seq_len 4096`, the only arm in the campaign with that window — 27 min) → `ck_*` →
  `ev_x1split` **382805** → `an_x1split` **382806** (`39_x1_split.py`,
  `results/analysis/pipeline/x1_split_codellama7b.json`). Conditions L0 / X1 / X1m / X1s; n_prog
  557 / 405 / 351 / 246. No H1.
- **Results:**

  | arm | L0 | X1 | X1m | X1s |
  |---|---:|---:|---:|---:|
  | `base` | 0.2569 | 0.1194 | 0.1331 | 0.1504 |
  | `tuned_L0` | **0.4275** | 0.2694 | 0.3184 | 0.2737 |
  | `tuned_X1` | 0.4108 | **0.3155** | **0.3565** | **0.2913** |
  | `tuned_X1m` | 0.4042 | 0.3105 | 0.3527 | 0.2886 |
  | `tuned_X1s` | 0.3838 | 0.3114 | 0.3175 | **0.2913** |
  | `mono_all` | 0.4114 | 0.2315 | 0.2690 | 0.2344 |

  | contrast | Δ pts [95 % CI] | n_prog |
  |---|---:|---:|
  | `tuned_X1m − tuned_L0` @ **X1s** (cross) | +1.49 [−0.95, +3.93] | 246 |
  | `tuned_X1s − tuned_L0` @ **X1m** (cross) | −0.10 [−2.38, +2.19] | 351 |
  | `tuned_X1m − tuned_L0` @ X1m (own) | **+3.42** [+0.86, +5.89]* | 351 |
  | `tuned_X1s − tuned_L0` @ X1s (own) | +1.76 [−0.81, +4.34] | 246 |
  | `tuned_X1m − tuned_L0` @ X1 | **+4.12** [+2.14, +6.18]* | 405 |
  | `tuned_X1s − tuned_L0` @ X1 | **+4.20** [+2.14, +6.26]* | 405 |
  | `tuned_X1 − tuned_L0` @ X1 | **+4.61** [+2.56, +6.68]* | 405 |
  | `tuned_X1m − tuned_X1` @ X1 | −0.49 [−2.06, +1.07] | 405 |
  | `tuned_X1s − tuned_X1` @ X1 | −0.41 [−2.39, +1.57] | 405 |
  | `mono_all − tuned_L0` @ X1m / X1s / X1 | −4.94* / −3.93* / −3.79* | |
  | `tuned_X1 / X1m / X1s − tuned_L0` @ L0 | −1.68* / −2.34* / **−4.37*** | 557 |

- **What worked / hypothesis verdict:**
  - **H-family-unit — REFUTED by the rule.** Neither half transfers to the other's single-mechanism
    condition: the string adapter is exactly null on MBA (−0.10), and the MBA adapter's +1.49 on
    string encoding has a CI that includes zero (and n_prog = 246, the campaign's thinnest cell).
    Within X1, the *mechanism* is the unit, not the family.
  - **H-whole-ge-parts — CONFIRMED.** Neither half beats the whole on X1 (−0.49, −0.41).
  - **H-mech-dominance (reported):** neither half dominates — +4.12 vs +4.20 on X1; the two are
    indistinguishable. **H-breadth-on-parts (reported):** breadth's tax is present on both halves
    (−4.94* on X1m, −3.93* on X1s), so the tax is not specific to the stacked form.
- **Observations — the result the rules did not anticipate:**
  - **Either half alone recovers ~90 % of the whole adapter's gain on the stacked X1** (+4.12 /
    +4.20 of +4.61), while transferring nothing (or little) to the *other* half's condition. That is
    not additive: if the X1 gain were "MBA skill + string skill", each half would give roughly half.
    Two readings, neither testable from these cells: (i) X1 items fail for the model on
    *whichever* transform it meets first in a stacked program, so relieving either one unlocks most
    of the items (a "weakest-link" gain); (ii) most of the X1 gain is adaptation to the *family's
    surface* — helper-function scaffolding, longer code, the X1 prompt distribution — which either
    half's training data carries and which the single-mechanism conditions do not need. Reading (ii)
    would also explain lossless X1→H1 transfer (H1 shares the scaffolding) and the null X2→Y2
    transfer (different scaffolding). It is the reading that makes "family" mean "surface family".
  - Coverage caveat recorded before the read stands: X1s trains on 32 % fewer pairs than X1m and
    evaluates on 246 vs 351 programs; the X1m→X1s leg's CI half-width is ±2.4 against ±2.3 for the
    other, so the asymmetry is in the point estimates, not the power. `tuned_X1s` is also the only
    arm trained with a 4,096-token window and pays the campaign's largest L0 cost (−4.37*) — the two
    are confounded and neither was registered as a contrast.
  - The clean re-statement of RQ2′ after this read: **six seen transforms do not reach X1; either
    half of X1 does; the halves do not reach each other.** Transfer follows shared *surface*, not
    shared mechanism and not "invariance".
- **New questions / new hypotheses:** the weakest-link vs surface readings separate on items: under
  (i) the items `tuned_X1m` newly solves on X1 should be the ones where the MBA guard sits before the
  encoded string; under (ii) they should be unrelated to transform order. An item-level analysis of
  existing X1 trials could test this without new compute — not registered, not run. E5b (a hard
  second family with a *different* surface) is the experiment that would settle "surface family".
- **Next Steps:** RQ_SUMMARY §6 RQ2′ row + §6.2 rows; PAPER_EXPERIMENTS E6 → done.
