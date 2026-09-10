### Target Date: 2026-09-10 (four probes: the gate rejected three of five panel models and was wrong about every one, for three unrelated reasons)
- **Hypotheses / what we're testing:** four rules, all frozen before their arms existed
  (`be12802`, `83c5d73`). **H-gate-format** (gemma3-12b): CONFIRM ≥ 0.4275, REFUTE ≤ 0.3335.
  **H-gate-format-lineage** (codegemma-7b): CONFIRM ≥ 0.4293 (the incumbent `tuned_L0(codellama-7b)`),
  REFUTE ≤ 0.2365. **H-persona-override** (starcoder2-15b): CONFIRM ≥ 0.4293, REFUTE ≤ 0.05.
  **P3** (llama31-8b-base, one-shot): REPORTED, gates nothing; measurable iff it clears ~0.15 with
  `format_fail` < 0.25.
- **Setup:** one `tuned_L0` per model (`configs/train/grid_py_L0_<model>.yaml`, batch shape from
  `models.yaml` rather than `grid_py_L0`'s hard-coded 7B shape), each behind a loss-mask gate, then
  ckpt-select, then `rq2_generic` with `--systems base,tuned_L0`. P3 is eval-only
  (`configs/eval/basecheck_1shot.yaml`) and ran the incumbent alongside so the number has a
  comparable reference. No X1, no H1.
- **Results — `tuned_L0` on L0, same 1,670 items, program-clustered bootstrap (2,000 resamples):**

  | model | gate said | tuned L0 | tuned `ff` | verdict |
  |---|---:|---:|---:|---|
  | `starcoder2-15b` | 0.0000 (ff 1.000) | **0.5401** | 0.0138 | **H-persona-override CONFIRMED** |
  | `codellama-34b` | — | 0.5222 | 0.0138 | (existing) |
  | `gemma3-12b` | 0.3335 (ff 0.280) | **0.5180** | 0.0096 | **H-gate-format CONFIRMED** |
  | `codellama-13b` | — | 0.4689 | 0.0162 | (existing) |
  | `codegemma-7b` | 0.2365 (ff 0.204) | **0.4647** | 0.0150 | **H-gate-format-lineage CONFIRMED** |
  | `codellama-7b` | 0.2569 (ff 0.129) — PASS | 0.4293 | 0.0222 | incumbent |

  `starcoder2-15b − codellama-34b` **+1.80 [−0.36, +3.89]** (ties, at under half the parameters);
  `− gemma3-12b` +2.22 [+0.06, +4.49]*; `− codellama-13b` +7.13*; `− codellama-7b` +11.08*.
  `codegemma-7b − codellama-7b` (same size class) **+3.53 [+1.26, +5.69]***.
  Mean over the five obfuscated conditions: starcoder2 **0.4823**, gemma3 0.4617, codellama-7b 0.3771.

  **P3, one-shot, NOT comparable to any zero-shot cell:** `llama31-8b-base` L0 **0.3150** (ff 0.167)
  against the incumbent's **0.3018** (ff 0.181) on the same footing, and ahead on the structural
  conditions (S1 0.2799 vs 0.2157, S2 0.2867 vs 0.2154). Zero-shot the same model read 0.0383.

- **What worked / hypothesis verdict:** all three registered hypotheses **CONFIRMED**; P3 measurable
  with room to spare. **The gate rejected three of five new models and was wrong about every one —
  and for three unrelated reasons, which is the part that matters:**
  1. **`gemma3-12b`, `codegemma-7b` — a quoting convention.** Bare unquoted strings where the spec
     wants a quoted literal; 34.8 % and 31.8 % of their failures were the gold value modulo quotes.
     One epoch fixes it (ff 0.280 → 0.0096, 0.204 → 0.0150).
  2. **`starcoder2-15b` — a template persona.** Its chat template refuses a system role *and*
     asserts its own ("an exceptionally intelligent coding assistant"), so under `merged` rendering
     this project's instruction is demoted into the user turn and loses; the base model answers in
     prose and scores 0.0000. SFT overrides the persona completely.
  3. **`llama31-8b-base` — a stop-sequence collision.** A pretrained checkpoint opens a *block*, and
     the shared `stop: ["\n\n"]` truncates its blank first line before any content.
  Not one was a property of the model. All were the **prompt-and-stop contract** meeting a model it
  was not written for.
- **Observations:**
  - **The rule was built from its own exception.** It came from the 2026-09-04 Llama-3.1-Instruct
    gate, where a model's entire apparent margin *was* format and it was weaker conditional on a
    well-formed answer. That case is real; it is also, on this evidence, the minority. Four of five
    new models had a format floor that said nothing about their tuned ceiling.
  - **What the diagnostic is actually good for.** Untuned `format_fail` is a reliable signal that
    *the prompt contract does not fit the model* — which is a reason to investigate, never a reason
    to discard. The composition of the failures is what separates the two cases, and it is nearly
    free to compute over cells the gate already writes.
  - **A fourth infrastructure trap, found by the CodeGemma re-run.** Its first probe read 0.0000 /
    ff 1.000 — not a refute but an invalid cell. CodeGemma's `generation_config` lists
    `eos_token_id=1` only while its template terminates turns with `<end_of_turn>` (107), so a model
    fine-tuned on that template emits the terminator, vLLM never stops, and generation repeats to the
    cap: `'1<end_of_turn>\n<end_of_turn>\n1<end_of_turn>…'`. Gemma-3 escaped because its config lists
    `[1, 106]`. `<end_of_turn>` is now a stop string — a no-op for any model that never emits that
    text, so no published cell changes. StarCoder2, Granite and CodeLlama were checked and are clean.
  - **The panel this evidence implies is materially better than the one the gate would have left.**
    Best three: `starcoder2-15b` (0.5401), `codellama-34b` (0.5222), `gemma3-12b` (0.5180). The gate
    would have left CodeLlama-7B and Granite.
- **New questions / new hypotheses:** none registered. Worth stating for the paper: the base-vs-instruct
  comparison (does E10's human-divergence survive on a checkpoint that never saw instruction data?)
  is now live, since the pretrained arm is measurable one-shot.
- **Next Steps:** human decisions — (1) which models form the final panel, given the gate's verdicts
  are not usable as a screen; (2) whether the two-part gate is adopted for anything further. The
  original NO-GO verdicts stand in the record unrevised; these probes tested the rule, not the models.
