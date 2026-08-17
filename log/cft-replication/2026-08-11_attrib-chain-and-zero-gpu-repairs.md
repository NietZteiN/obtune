### Target Date: 2026-08-11 (the ATTRIB chain made autonomous; three zero-GPU repairs)

- **Goal:** get the whole ATTRIB workshop experiment string running unattended to the Aug 28
  freeze, then spend the remaining time on work that needs no GPU. No manuscript work — the
  paper draft is explicitly out of scope for this entry.

- **Setup:**
  - Six new stages appended to [`../../scripts/pipeline.sh`](../../scripts/pipeline.sh):
    `attrib_dose → attrib_seeds → attrib_strategies → attrib_js_train → attrib_js_eval →
    attrib_analysis`, on top of the eleven already complete. Each gates through
    `scripts/preflight.py` before draining and guards on **artifacts**, not on the previous
    stage's marker, so a half-finished predecessor is skipped with a logged reason.
  - Ordered by what can change the paper, not by cost. The dose curve runs first because it is
    the only remaining experiment that can change the **claim type**: everything else sharpens a
    refutation, while saturation at 5–10 % reverse data turns the result into a prescription.
    The JavaScript replication runs last among the experiments because it is the only one
    needing new training, and the freeze rule ships an unlanded item as a limitation.
  - Three eval configs written, each avoiding a trap already recorded in this project:
    - `srh/eval/e2_seeds_qwen1.5b.yaml` — a **new file**. `e1_qwen1.5b_s42.yaml` deliberately
      inherits SEED-17 `sft`/`cft` (correct when written; the s42 twins did not exist yet), its
      results are published, and `run_tag` defaults to the filename stem — so editing it would
      both change a published table and collide on the results directory.
    - `srh/eval/e7_strategies_qwen7b.yaml` — extends `e1_qwen7b.yaml`, **not** `bidir_v1.yaml`,
      which would inherit 1.5B adapter paths onto a 7B base.
    - `srh/eval/e3_javascript_qwen1.5b.yaml` — restates `sft`/`cft` explicitly even though the
      parent names them, because `systems` deep-merges and the parent's paths are Python.
  - Two JS arms created (`srh/train/{flip,mix50}_qwen1.5b_js.yaml`) as one-line `language:`
    overrides, so any Python-vs-JS gap is attributable to the corpus and not the recipe.

- **Results:**

  **`merge_dare_linear` diagnosed — it is an implementation artifact, not a method result.**
  Measured against the EXACT uniform mixture `Σ_i (1/6) dW_i` over 196 modules:

  | merge | ‖dW‖ / exact | cosine to exact |
  |---|---|---|
  | `merge_ties` | 0.243 | 0.843 |
  | `merge_dare_ties` | **0.802** | 0.871 |
  | `merge_dare_linear` | **7.175** | 0.832 |

  All three point the **same way**; they differ only in magnitude. Cause, read from
  `peft/tuners/lora/model.py:893-897`: the linear family puts `sqrt(|w·scaling|)` on `lora_A`
  and `lora_B` **separately**, so `B_new @ A_new` carries 36 terms `B_i A_j` where only the 6
  diagonal ones are wanted, and DARE's `1/(1-density) = 2` rescale hits each factor,
  multiplying the product by 4. TIES-family variants survive because sign election removes most
  of the cross-term mass. A scale-corrected variant (lora_B × 1/7.175, ‖dW‖ 0.282 against
  `dare_ties`' 0.226) is built and unevaluated at
  `runs/merges/scale_corrected/qwen25c-1.5b/python/dare_linear_rescaled_r32_s17`.

  **The HF evaluation path was rendering a different prompt from the accuracy grid.**
  `eval_hf._prompt_and_code_span` called `build_prompt` without `condition` and then did
  `"\n".join(m["content"] for m in messages)` — never applying the chat template. That is
  CLAUDE.md §4 silent-failure #3, and §1 states the requirement outright. Fixed to use
  `prompts.render_chat` and pass `condition`. Nothing was lost: `results/attn/` held only a
  schema and a span-validation file, no dumps produced under the old path.

  **`moe_soft_generate` removed rather than repaired.** It called
  `add_weighted_adapter(..., combination_type="linear")`, which by the measurement above is not
  `Σ w_i dW_i` at all — so no number it produced was the blend it claimed to be. It was also
  unwired, ungraded, emitted non-TrialRow dicts and had no producer for its `--routing` input.
  Replaced with a stub that raises.

- **What worked / hypothesis verdict:**
  - The `merge_dare_linear` question is **settled**: not "DARE-linear is a poor merge method"
    but "PEFT's linear-family combination is wrong for LoRA at this configuration". The cosine
    column is what makes the claim safe — a magnitude-only failure is a different statement from
    a direction failure, and only the former is fixable by rescaling.
  - The prompt-parity bug is the kind that **cannot** be caught by testing modules against
    themselves. `tests/test_prompt_path_parity.py` now compares the two renderings directly with
    a stub tokenizer, so it needs no model download and no GPU. The stub deliberately does not
    render the identity — a stub returning joined contents would have let the original bug pass.

- **Observations:**
  - Every bug found today and yesterday has the same shape: **an identifier or a code path that
    does not encode what actually varies**. Adapter directories ignoring training length, job ids
    ignoring it too, cell paths ignoring the experiment, the common subset ignoring the
    experiment, `systems` shape ignoring which harness consumes it, and now a prompt renderer
    ignoring the template. None of them raised.
  - **Anchor drift worth recording.** Published runs agree — 1.5B `base` strict 2.9 % across
    `e1`, `e1_s42`, `e2_factorial`; 7B 12.9–13.1 % across `bidir`, `e1`, `e2_budget`. The
    unlearning runs read **2.7 %** and **13.3 %**. Their internal contrasts are sound (every arm
    on one program set) but those numbers must not be placed beside the published tables.
  - `cft/evaluate.py` does **not** import `transfer.core_subset` — it only mentions it in a
    comment — so the `is_core` experiment-scoping fix made on 2026-08-10 (which corrected the
    RQ1 common subset from 23 programs back to 340) cannot have moved any paper table.

- **New questions / new hypotheses:**
  - Does the scale-corrected `dare_linear` recover to roughly `dare_ties`' accuracy? If it does,
    the collapse was purely a scale artifact and the arm should be reported as such rather than
    dropped. One eval cell, currently unqueued so as not to compete with the ATTRIB chain.

- **Next Steps:**
  - Let the ATTRIB chain run. First thing to check when `attrib_dose` lands: **`base` must read
    2.9 % strict** — if it does not, the program set drifted and the run is not comparable.
  - Remaining zero-GPU item: Part III Phase 1 (composite stacked conditions — builder `stack:`
    support, composed purity invariants, `C_S4_S3` as the positive control). Substantial build,
    not started.
  - Twelve orphaned duplicate cells (`ties_e6/e9`, `dare_ties_e6/e9`) from the pre-namespacing
    merge run still sit on disk and will inflate any pooled analysis. Deletion needs sign-off
    per CLAUDE.md §2.
