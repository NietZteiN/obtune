### Target Date: 2026-09-09 (all five panel gates read: one clean PASS, two blocked by one shared quoting convention, one by its own template's persona, and one invalid because of a bug in this session's code)
- **Hypotheses / what we're testing:** the gate rule frozen before any read — a candidate enters the
  panel iff untuned `format_fail` ≤ 0.15 on L0 and untuned L0 accuracy is in an interpretable band.
  Every read reported whatever the verdict. No gate touches X1 or H1.
- **Setup:** `configs/eval/basecheck_panel.yaml --model <key>`, six trainable conditions, `base`
  only, same held-out items as every panel read. Jobs 385500 (gemma3-12b), 388497
  (llama31-8b-base), 388499 (starcoder2-15b), 388500 (codegemma-7b), 388501 (granite31-8b).
- **Results:**

  | model | L0 acc | L0 `format_fail` | mean obf acc | verdict |
  |---|---:|---:|---:|---|
  | `granite31-8b` | **0.2850** | **0.125** | 0.2625 | **PASS** |
  | `llama31-8b` (existing) | 0.2575 | 0.047 | 0.2195 | PASS |
  | `codellama-7b` (incumbent) | 0.2569 | 0.129 | 0.2002 | PASS |
  | `gemma3-12b` | **0.3335** | 0.280 | 0.2726 | NO-GO |
  | `codegemma-7b` | 0.2365 | 0.204 | 0.2014 | NO-GO |
  | `starcoder2-15b` | **0.0000** | **1.000** | 0.0000 | NO-GO |
  | `llama31-8b-base` | 0.0383 | 0.902 | 0.0121 | **INVALID — see below** |

- **What worked / hypothesis verdict:**
  - **`granite31-8b` PASSES cleanly** and is the only new model that does: it beats the incumbent
    CodeLlama-7b on L0 (+2.8 pts) with a *lower* format floor, and its obfuscated mean is +6.2 pts
    above it. IBM lineage, Apache 2.0, ungated.
  - **`gemma3-12b` and `codegemma-7b` NO-GO on the same cause, and it is a lineage property, not two
    quirks.** Both emit bare unquoted strings where the spec requires a quoted literal: **34.8 %**
    of Gemma-3's failures and **31.8 %** of CodeGemma's are the gold value with its quotes stripped.
    Granite shows the same defect at 26.9 % but stays under the threshold. The Google pair is the
    subject of the running H-gate-format probe; if tuning teaches the convention for one it should
    teach it for both, and that is now a prediction rather than a hope.
  - **`starcoder2-15b` NO-GO, and the cause is the template, not the task.** Every item returns
    prose — "Here's how you can implement this in Python:" — then hits the `\n\n` stop. Its chat
    template **hard-codes its own system persona** ("You are an exceptionally intelligent coding
    assistant…") while refusing a system role, so under `merged` mode this project's instruction
    ("a deterministic code execution engine … reply with the return value alone") is demoted into
    the user turn and loses to the persona the template asserts. This is the confound named as
    untested in `2026-09-09_five-model-panel.md`, arriving on its own: the merged rendering is not
    free on a model whose template already claims the system slot.
- **Observations — the invalid read, which is this session's bug and not a model result:**
  - `llama31-8b-base` returned **empty strings on 92.9 % of its 1,507 L0 failures at
    `n_gen_tokens` ≤ 2**. Cause: `prompts.render_plain` ended the prompt with a newline after
    `### Response`, so a pretrained checkpoint — which continues *blocks*, not lines — emitted a
    blank line first, matching the eval's `stop: ["\\n\\n"]` before producing anything.
  - Fixed: the plain prompt now ends **on** the header. `tests/test_template_adaptation.py` gains a
    regression test naming this job. The cells are moved to
    `results/cells/_invalid_llama31-8b-base_renderplain_bug_2026-09-09/` rather than deleted, and
    the gate is re-running as **388553**. **0.0383 is not this model's number and must not be
    quoted as one.**
  - The bug was invisible to every test written this morning because they check that a prompt
    *renders* and that its parts are consistent — not how a model *continues* it. A prompt can be
    perfectly well-formed and still be unanswerable given the sampler's stop sequence.
- **New questions / new hypotheses:** **H-merged-persona** (opened, not run): the `merged` rendering
  costs accuracy on a model whose template asserts its own system persona, and nothing on one that
  does not. Testable without new models by forcing `merged` on CodeLlama or Granite (whose templates
  accept a system role) and comparing to their `system` cells — one eval each, no training. This is
  the confound that decides whether StarCoder2's NO-GO is about StarCoder2 or about our adaptation.
- **Next Steps:** await 388553 (pretrained Llama, re-run) and the Gemma-3 H-gate-format probe chain
  (388535 → 388536 → 388537 → 388538). Decisions for the human: whether a one-shot gate — the
  project's existing ICL machinery, which pins the answer format by example — is the fair test for
  merged-mode and pretrained checkpoints, given it would no longer be comparable to the zero-shot
  cells the other models were gated on.
