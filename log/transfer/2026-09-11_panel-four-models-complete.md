### Target Date: 2026-09-11 (all four new panel models read: R1 and R2 hold 2/4, R3 holds 1/4 — the effects are real but not universal)
- **Extends** [`2026-09-11_panel-r1-r4-first-two.md`](2026-09-11_panel-r1-r4-first-two.md), which read
  the first two models. That entry's reading that "R3 refutes on both" was correct for those two and
  **incomplete as a generalisation**: StarCoder2 replicates R3. Per CLAUDE.md §6 the earlier entry
  stands unaltered and this one carries the corrected picture.
- **Hypotheses / what we're testing:** R1-R4 as frozen in `d63340c` before any panel cell existed.
- **Setup:** `panel_core`, 5 systems × 7 conditions per model, program-clustered bootstrap
  (2,000 resamples, seed 17). All four `cons_lam3` arms are the retrained ones with `kl_loss`
  verified in their training logs. No H1.
- **Results:**

  | model | R1 `mono_all−tuned_L0` @X1 | R2 `cons_lam3−mono_all` @X1 | R3 `cons_lam3−tuned_L0` @L0 |
  |---|---:|---:|---:|
  | starcoder2-15b | **−2.72 [−4.94, −0.58]** REPL | **+2.31 [+0.58, +4.03]** REPL | −0.96 [−2.51, +0.60] REPL |
  | gemma3-12b | **−4.70 [−6.93, −2.55]** REPL | **+2.64 [+0.91, +4.53]** REPL | −1.80 [−3.53, −0.06] REF |
  | codegemma-7b | −1.98 [−3.95, +0.16] INC | −0.41 [−2.39, +1.49] INC | −2.04 [−3.77, −0.18] REF |
  | granite31-8b | −0.91 [−2.97, +1.15] INC | **−1.89 [−3.54, −0.25] REF** | −3.41 [−5.39, −1.26] REF |
  | **new-model tally** | **2 REPL / 2 INC / 0 REF** | **2 REPL / 1 INC / 1 REF** | **1 REPL / 0 INC / 3 REF** |
  | with the 4 published | 6 of 8 significant | 6 of 8 significant | 5 of 8 |

- **What worked / hypothesis verdict:**
  - **R1 (breadth's unseen-family tax) survives the move off the Meta lineage, weakly.** Two clean
    replications; the other two carry the right sign with intervals spanning zero. No model
    contradicts it. Effect real, magnitude smaller than the published four suggest.
  - **R2 (anchoring removes the tax) is model-dependent.** Two replications, one inconclusive, and
    one genuine refutation on Granite where the anchored arm is *worse* than breadth on the unseen
    family.
  - **R3 (no clean-code tax) is the casualty.** It held on all four Meta-lineage models and fails on
    three of four new ones. 5 of 8 overall; 1 of 4 outside the lineage where it was discovered.
- **Observations:**
  - **StarCoder2 replicates all three** — and it is the model the untuned gate scored **0.0000** and
    rejected. The strongest model in the panel and the most faithful replication of the original
    findings would both have been discarded by the screening rule
    (`docs/MODEL_AND_DATA_SELECTION.md` §5b).
  - **The correction to the two-model read matters more than the addition.** Calling R3 "refuted on
    both" invited the generalisation that clean-code protection is absent outside CodeLlama. It is
    not: it is *model-dependent*, and StarCoder2 is the counter-example. Two models is not enough to
    name a pattern, which is the argument for the eight-model uniform grid now training.
  - No arm is degenerate: `format_fail` at L0 is 0.008-0.022 across every tuned arm on all four
    models, accuracies order sensibly, nothing collapsed.
- **New questions / new hypotheses:** none registered. Granite remains the outlier on every axis
  (anomalous training losses, the only R2 refutation, the largest R3 cost) and its pre-registered
  watch item is still open, still not used as grounds to discard its read.
- **Next Steps:** `tuned_X1` is training for codellama-13b/34b and llama31-8b so that all eight
  models can be read from `panel_core` alone; `an_panel_repl2` (390866) runs the tally over
  whatever has landed. The paper's RQ3 section should not be rewritten until the eight-model
  tally exists.
