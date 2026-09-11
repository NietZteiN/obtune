### Target Date: 2026-09-11 (first two panel models read: R1 and R2 replicate on Gemma-3, R2 REFUTES on Granite, and R3 refutes on both)
- **Hypotheses / what we're testing:** R1-R4, frozen in `CLAUDE_SCRATCHPAD.md` as `d63340c`
  **before any panel cell existed**, and restated verbatim inside
  `scripts/analysis/51_panel_replication.py` so the reader cannot drift from them.
- **Setup:** `configs/eval/panel_core.yaml`, 5 systems x 7 conditions, held-out items, strict exact
  match; program-clustered bootstrap, 2,000 resamples, seed 17. The `cons_lam3` arms are the
  RETRAINED ones — `kl_loss` verified present in all four training logs after the plain-SFT
  incident (`log/setup/2026-09-10_cons-arms-ran-as-plain-sft.md`). No H1.
- **Results:**

  | | gemma3-12b | granite31-8b | published (CodeLlama 7/13/34B, Llama-3.1-8B) |
  |---|---:|---:|---|
  | **R1** `mono_all − tuned_L0` @ X1 | **−4.70 [−6.93, −2.55]** REPLICATED | −0.91 [−2.97, +1.15] INCONCLUSIVE | −3.79 / −4.28 / −2.64 / −2.88 |
  | **R2** `cons_lam3 − mono_all` @ X1 | **+2.64 [+0.91, +4.53]** REPLICATED | **−1.89 [−3.54, −0.25] REFUTED** | +4.59 / +3.95 / +3.38 / +3.46 |
  | **R3** `cons_lam3 − tuned_L0` @ L0 | **−1.80 [−3.53, −0.06] REFUTED** | **−3.41 [−5.39, −1.26] REFUTED** | −0.30 / −0.60 / +0.42 / +0.00 |
  | R4 `mono_all − tuned_L0` pooled obf | +1.21 [−0.14, +2.66] | +2.72 [+1.14, +4.39] | +1.43 (13B), +0.72 (34B) |

- **What worked / hypothesis verdict:**
  - **R1 REPLICATED on Gemma-3**, inside the published range, on a model sharing no lineage,
    tokenizer or chat template with the panel it was measured on. INCONCLUSIVE on Granite: the
    point estimate has the right sign but the interval spans zero.
  - **R2 REPLICATED on Gemma-3 (+2.64) and REFUTED on Granite (−1.89).** On Granite the anchored
    arm is *worse* than breadth on the held-out family. This is the first evidence that the
    paper's one positive methodological result is **lineage-dependent**.
  - **R3 REFUTED on both.** `cons_lam3` pays a clean-code cost of −1.80 and −3.41, where on all
    four previously published models it never fell significantly below the clean-code control.
    "Paired consistency has no L0 tax" does not survive contact with these two models.
- **Observations:**
  - **The grids are healthy, so these are results and not artefacts.** `format_fail` at L0 is
    0.0096-0.0216 for every tuned arm on both models; accuracies are ordered sensibly; nothing
    collapsed. Granite is simply a weaker model on this task (base 0.2850 vs Gemma-3's 0.3335)
    with differently-behaved arms.
  - **The Granite watch item, registered before its cells existed, is relevant and is NOT the
    explanation.** Its training losses were anomalously high (X1 2.03, `tuned_L0` 1.24, cons 2.72
    against 0.12-0.99 elsewhere) and the pre-registration said to look there first if its X1 column
    read weak. Its X1 column *is* the weakest (`cons_lam3` 0.1878), but the grid shows a working
    model, so high loss alone does not void the read. Recorded as an open question, not a reason to
    discard the verdict.
  - **What this does to the paper.** RQ3's claim must narrow from "anchoring removes breadth's
    costs" to something conditional: it does on CodeLlama x3, Llama-3.1 and Gemma-3, and does not
    on Granite, where it is worse than breadth on the unseen family and pays a clean-code cost.
    Two of four panel models are still pending; the verdict could move either way, and the
    abstract should not be rewritten until they land.
  - Unregistered but visible: on Gemma-3 `cons_lam3` is the best arm on **four of five** obfuscated
    conditions (L1b 0.4879, L1r 0.4719, L2 0.4778, S1 0.4828) while losing L0 — the seen-condition
    gain survives even where the clean-code protection does not.
- **New questions / new hypotheses:** does R2's failure on Granite track its anomalous training
  loss, its small vocabulary (49k vs Gemma's 256k, which changes what a KL over the answer
  distribution actually constrains), or something else? Not registered; not testable from these
  cells alone.
- **Next Steps:** `ev_panel_codegemma-7b` and `ev_panel_starcoder2-15b` are queued. The R2 tally
  across four new models is what the paper's RQ3 section now depends on.
