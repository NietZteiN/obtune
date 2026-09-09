### Target Date: 2026-09-09 (five-model panel adopted; three of the five reject the system role, so the prompt builder gained an adaptation layer)
- **Hypotheses / what we're testing:** Setup day. The user chose the five-model option from
  `docs/MODEL_AND_DATA_SELECTION.md` §3. The gate rule is pre-registered here **before** any read:
  a candidate enters the panel iff untuned `format_fail` ≤ 0.15 on `L0` **and** untuned `L0`
  accuracy sits in a band where the paper's ±4-point contrasts are visible (not at the floor, not
  saturating the ladder). Every gate read is REPORTED whatever the verdict — a NO-GO is a result
  about base models. No gate touches X1 or H1.
- **Setup:**
  - **Panel entered in `configs/models.yaml`** with `role: candidate_main`, every `n_layers` /
    `hidden_size` read from the downloaded `config.json`: `starcoder2-15b`
    (bigcode/starcoder2-15b-instruct-v0.1, L40 h6144), `gemma3-12b` (google/gemma-3-12b-it, L48
    h3840 text_config), `codegemma-7b` (google/codegemma-7b-it, L28 h3072), `granite31-8b`
    (ibm-granite/granite-3.1-8b-instruct, L40 h4096), `llama31-8b-base` (meta-llama/Llama-3.1-8B,
    L32 h4096, pretrained). Alternates (Mistral-7B-v0.3, OLMo-2-13B) stay under `candidates:`,
    which no loader resolves.
  - **Downloads** (SLURM CPU, `scripts/hf_snapshot.py`): StarCoder2 **385346**, CodeGemma **385353**,
    Granite **385360**. Gemma-3-12B (23 G) and pretrained Llama-3.1 (30 G) were already in
    `$HF_HOME` and complete. CodeGemma is `gated=manual` on the hub but the account's token already
    has access (verified by fetching `config.json`).
  - **Gates submitted** for the two on disk: `gate_gemma3-12b` **385500**, `gate_llama31-8b-base`
    **385501** (`configs/eval/basecheck_panel.yaml`, model-neutral, `--model <key>`; six trainable
    conditions, `base` only, no X1/H1). All five jobs are PENDING on `QOSMaxJobsPerUserLimit`
    behind another project's array.
- **Results:** no accuracy numbers yet — the finding of the day is a code one, measured on the real
  tokenizers before any weights were pulled:

  | model | system turn under `apply_chat_template` | mode |
  |---|---|---|
  | CodeLlama ×3, Llama-3.1-8B-Instruct, Granite-3.1-8B | rendered as its own turn | `system` |
  | Gemma-3-12B-it | the template folds it into the first user turn itself | `system` |
  | StarCoder2-15B-Instruct | `TemplateError: System messages are not allowed in this template` | `merged` |
  | CodeGemma-7B-it | `TemplateError: System role not supported` | `merged` |
  | Llama-3.1-8B (pretrained) | no `chat_template` at all | `plain` |

  So **three of the five could not have been trained by this repo at all**, and two of those would
  have raised inside TRL rather than at a place anyone was looking.
- **What worked / hypothesis verdict:** n/a (no hypothesis read). The fix, in `src/obtune/prompts.py`
  under "Template adaptation", is one policy resolved once per template and used by every path —
  CLAUDE.md §4 #3 forbids a call-site fix, because a training/eval prompt divergence is invisible in
  the loss curve:
  - `template_mode()` → `system` | `merged` | `plain`, cached on the template string, and
    **verified**: a template that accepts a system role but silently drops its content raises
    instead of training on a prompt with no task description.
  - `adapt_messages()` folds the system text into the head of the first user turn — which is exactly
    what Gemma-3's own template does to a system message, so the merged form is the family's own,
    not an invention — and **raises rather than dropping** the system turn if there is no user turn.
  - `render_plain()` (`plain_v1`) is the fixed plain-text form for a checkpoint with no template.
    Rejected: borrowing the instruct twin's template — it would put control tokens in front of a
    checkpoint that never saw them and confound the base-vs-instruct comparison that model is *for*.
  - `to_trl_example()` hands TRL conversational messages where a template exists and TRL's text
    prompt-completion form where it does not; `train_sft.py` maps the dataset through it, and
    `measure_truncation`, `objectives._ids` (the consistency KL term), `attention/capture.py` and
    `scripts/inspect_batch.py` all route through the same renderers.
  - In `system` mode every one of these is the identity, so **no adapter trained before today is
    affected** and no published cell changes.
  - `tests/test_template_adaptation.py`: 30 cases, all passing offline, asserting per model that the
    mode matches what `models.yaml` declares, the system text survives rendering, the prompt is a
    prefix of prompt+completion (TRL's `completion_only_loss` contract), and what the trainer
    templates equals what eval renders.
- **Observations:**
  - A second landmine, found while wiring the panel and disarmed: Gemma-3-12B is a
    `Gemma3ForConditionalGeneration` checkpoint and PEFT matches `target_modules` by **name suffix**,
    so `q_proj` also matches the vision tower's attention — LoRA would have been attached to an
    image encoder this task never uses, adding trainable parameters and quietly making any
    merge/geometry comparison against the text-only models not like-for-like.
    `peft_exclude_modules: [vision_tower, multi_modal_projector]` is declared in `models.yaml` and
    passed to `LoraConfig` (PEFT 0.20 supports `exclude_modules`).
  - StarCoder2's template also injects its own assistant preamble ("You are an exceptionally
    intelligent coding assistant…"). That is part of the model and is left alone; it is noted in
    `models.yaml` so it is not mistaken for our system prompt later.
  - `render_provenance()` (mode + version) goes into the training manifest **beside**
    `prompt_template_sha256`, not inside it: the hash names the prompt *text* and every published
    cell already carries it, while how a given model lays that text out is the separate fact a
    reader needs to compare two models.
- **New questions / new hypotheses:** whether the `merged` rendering costs anything measurable
  against a `system` rendering on the *same* model — untestable on StarCoder2/CodeGemma (their
  templates refuse), but testable on CodeLlama or Granite by forcing `merged`. Not registered, not
  run; worth one cell if a reviewer asks whether the adaptation confounds the cross-model comparison.
- **Next Steps:** collect the two gate reads (385500/385501) and the three downloads; then gates for
  StarCoder2 / CodeGemma / Granite; then, per model that passes, the truncation re-gate at 2,048 and
  the loss-mask gate before any adapter is queued. `docs/MODEL_AND_DATA_SELECTION.md` §2a and §3
  carry the panel and the rule.
