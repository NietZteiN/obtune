### Target Date: 2026-09-11 (the uniform `panel_core` grid reproduces CodeLlama-13B's published R1–R3 to within 0.24 pts — so the four new models' failures are about the models, not the grid)
- **Why this check exists.** [`2026-09-11_panel-four-models-complete.md`](2026-09-11_panel-four-models-complete.md)
  reported that R1 and R2 hold on 2 of 4 new panel models and R3 on only 1 of 4, and concluded that
  clean-code protection is **model-dependent**. That conclusion has an obvious alternative: the four
  new models were read through `panel_core`, a **new config** (five arms, seven conditions, written
  2026-09-10), while the published four were read through `x1_generic` / `rq2_generic` /
  `objectives_scale`. If the new grid measured differently, "model-dependent" would really be
  "grid-dependent" and the entry would be wrong.
- **The test.** Run an **incumbent** model through the new grid and compare against its own
  published numbers. CodeLlama-13B's `panel_core` cells completed first, so it is the witness. The
  three contrasts use `tuned_L0`, `mono_all` and `cons_lam3` — all adapters unchanged since
  publication — so any difference is the measurement, not the model.
- **Results:**

  | | published | `panel_core` (uniform grid) | Δ |
  |---|---:|---:|---:|
  | R1 `mono_all − tuned_L0` @ X1 | −4.28 | **−4.04** [−6.26, −1.89] | 0.24 |
  | R2 `cons_lam3 − mono_all` @ X1 | +3.95 | **+3.87** [+2.06, +5.77] | 0.08 |
  | R3 `cons_lam3 − tuned_L0` @ L0 | −0.60 | **−0.72** [−2.28, +0.90] | 0.12 |

  All three **REPLICATED**, all three verdicts unchanged, and the largest disagreement is a quarter
  of a point — well inside every interval.
- **Verdict: the grid is not the explanation.** The four new models' departures from R1–R3 are
  properties of those models. The 09-11 entry's reading stands, and the eight-model tally can be
  read as one table rather than as two measurements stitched together — which was the whole point
  of retraining the incumbents' `tuned_X1` arms so every model could come from one phase.
- **What this does NOT establish.** One incumbent, not four. CodeLlama-7B, 34B and Llama-3.1-8B are
  still evaluating; if any of them disagrees with its published numbers by more than this, that is a
  finding in itself and this entry must be revisited. The check is cheap and is worth repeating on
  each as it lands.
- **Observation.** This is the same instrument as `scripts/verify_migration.py`, which re-derived a
  published Grid-A contrast to the decimal after the cluster move. Recomputing a known number
  through a new path, before trusting the path on unknown numbers, has now caught nothing twice —
  which is the outcome that makes it worth doing a third time.
- **Next Steps:** repeat the comparison for 7B, 34B and Llama-3.1-8B as their grids complete; fold
  the result into the eight-model tally entry.
