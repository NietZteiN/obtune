# Model and dataset selection for the FSE paper

*Last updated: 2026-09-09*

Scope decision taken 2026-09-09: **no Chinese-origin models anywhere in the paper.** That excludes
Qwen (all sizes, Coder and general), DeepSeek (Coder, R1 distills), Yi, InternLM, GLM, and their
derivatives. The frozen Qwen2.5-Coder-1.5B panel (`RQ_SUMMARY.md` §1–§4, master report §1–§17)
stays in the repository as the record of how the design was arrived at but **no Qwen number appears
in the paper**, including the Qwen composite dissociation (+3.91) and the Qwen task-vector geometry
read (`REPORT_2026-08-17` §3). Where a Qwen result was the only evidence for a statement, that
statement is now unsupported until it is re-measured on the panel below (F1b for the geometry read).
`configs/models.yaml` marks the Qwen entries `role: barred`; the JS tier-3 transpiler is reassigned.

This document does three things: fixes the **model panel** (§1–§3), fixes the **dataset** (§4–§5),
and says what each costs (§6). Every model added follows the gate protocol in §3 before a single
adapter is trained on it — the Llama-3.1 gate (`log/transfer/2026-09-05_x1-family-arm-and-llama31-gate.md`)
is the template.

---

## 1. What an FSE reviewer will ask about the panel

1. *Is this a CodeLlama artefact?* Today every headline is CodeLlama-7b/13b/34b with one Llama-3.1-8B
   replication of the consistency result. Two lineages, both Meta, both Llama-2/3 tokenizers.
2. *Code-specialised vs general models* — does obfuscation adaptation behave differently when the
   base already saw a lot of code? The panel has three code models from one lineage and one general.
3. *Pretrained vs instruction-tuned* — every model in the panel is an `-Instruct`. The "tuning moves
   models away from humans" result (E10) could be an instruct-tuning artefact; nobody has run a
   true pretrained checkpoint.
4. *Recency* — CodeLlama is a 2023 model, weak at output prediction (base L0 0.257). A 2024–25 model
   of the same size is a stronger, fairer base.
5. *Scale* — the 7/13/34B ladder exists and is a strength; keep it.

## 2. Candidate models (non-Chinese only)

All sizes are bf16 weights; one H200 (141 GB) trains any of them with LoRA + gradient checkpointing
(34B peaks well inside one card — `CLAUDE.md` §1). vLLM 0.26 / PEFT 0.20 support every architecture
listed. "gated" = needs an accepted licence on the HF hub (a token is on disk at `$HF_HOME/token`;
Gemma-3 and Llama-3.1 were already fetched with it). Licence and config facts are from the model
cards as known to the author and **must be re-checked at download** (`config.json` for
`n_layers`/`hidden_size`, the card for gating).

| model | origin | type | size | licence / gating | on disk | note |
|---|---|---|---|---|---|---|
| **CodeLlama-7b/13b/34b-Instruct** | Meta (US) | code | 7/13/34B | Llama 2, ungated | ✅ | the scale ladder; keep as primary |
| **Llama-3.1-8B-Instruct** | Meta (US) | general | 8B | Llama 3.1, gated | ✅ | E8 replication exists |
| **Llama-3.1-8B** (pretrained, no instruct) | Meta (US) | general, **base** | 8B | Llama 3.1, gated | ✅ (30 G) | the pretrained-vs-instruct axis; no chat template — prompt builder needs a plain-text path |
| **Gemma-3-12B-it** | Google (US) | general | 12B | Gemma terms, gated | ✅ (23 G) | 2025 model; multimodal checkpoint — load text-only (`Gemma3ForCausalLM`), gate for the vision tower not being touched |
| **CodeGemma-7B-it** | Google (US) | code | 7B | Gemma terms, gated | ❌ | Google's code lineage; pairs with Gemma-3 |
| **StarCoder2-15B-Instruct-v0.1** (and 7B base) | BigCode — ServiceNow/HF (US/FR) | code | 15B / 7B | BigCode OpenRAIL-M, click-through | ❌ | The Stack v2 lineage — the most different code-pretraining pipeline available; the instruct is self-aligned, so also a "no human-preference data" point |
| **Granite-8B-Code-Instruct** (Granite-3.x-8B for general) | IBM (US) | code | 8B | Apache 2.0, ungated | ❌ | ungated, permissive; IBM's own tokenizer and data |
| **Mistral-7B-Instruct-v0.3** / **Codestral-22B** | Mistral (FR) | general / code | 7B / 22B | Apache 2.0 / MNPL (non-commercial, gated) | ❌ | Codestral is research-only; fine for a paper, must be declared |
| **Phi-4** (14B) / Phi-3.5-mini (3.8B) | Microsoft (US) | general | 14B / 3.8B | MIT | mini ✅ (7 G) | Phi-3.5-mini is on disk and is a cheap *small* point to replace Qwen-1.5B's role |
| **OLMo-2-7B/13B-Instruct** | AI2 (US) | general, fully open data | 7/13B | Apache 2.0 | ❌ | the only candidate whose pretraining data is public — the contamination question (§4) can be *answered* on it rather than argued |
| ~~Qwen2.5-Coder-1.5B/7B, Qwen2.5-7B, Qwen3-0.6B, DeepSeek-Coder-6.7B, R1-Distill-Qwen~~ | China | — | — | — | on disk | **barred** |

## 2a. Measured 2026-09-09: three of the five panel models reject the system role

Before any weights were pulled, every candidate tokenizer was rendered with the project's
real prompt. The result changed the code, not just the config:

| model | `apply_chat_template` with a system turn | mode |
|---|---|---|
| CodeLlama-7b/13b/34b, Llama-3.1-8B-Instruct, **Granite-3.1-8B** | own system turn | `system` |
| **Gemma-3-12B-it** | the template folds it into the first user turn itself | `system` |
| **StarCoder2-15B-Instruct** | `TemplateError: System messages are not allowed in this template` | `merged` |
| **CodeGemma-7B-it** | `TemplateError: System role not supported` | `merged` |
| **Llama-3.1-8B (pretrained)** | no `chat_template` at all | `plain` |

`CLAUDE.md` §4 silent-failure #3 makes this load-bearing: train, vLLM eval, HF eval and
attention extraction must build byte-identical prompts, so the fix cannot be a call-site
`try/except`. `prompts.py` gained one adaptation layer — `template_mode` (resolved once per
template, cached, and **verified**: a template that accepts a system role but silently drops
its text raises rather than training on a prompt with no task description), `adapt_messages`
(folds the system text into the head of the first user turn — exactly what Gemma-3's own
template does, so the merged form is not an invention), `render_plain` (`plain_v1`, a fixed
versioned plain-text form for a checkpoint with no template), and `to_trl_example`, which
hands TRL conversational messages when a template exists and TRL's text prompt-completion
form when it does not. `render_chat`, `render_full`, `objectives._ids` (the KL term),
`attention/capture.py` and `scripts/inspect_batch.py` all route through it.

In `system` mode the layer is the identity, so **every adapter already trained is
unaffected**. `tests/test_template_adaptation.py` (30 cases) asserts, per model, that the
mode is what `models.yaml` declares, that the system text survives rendering, that the
prompt is a prefix of prompt+completion (TRL's `completion_only_loss` contract), and that
what the trainer templates equals what eval renders.

Rejected alternative for the pretrained checkpoint: borrow the instruct twin's template.
It would put control tokens in front of a checkpoint that never saw them, and the
base-vs-instruct comparison — the reason that model is in the panel — would be confounded
by a template the base model cannot read.

One more consequence, recorded in `models.yaml`: Gemma-3-12B is a
`Gemma3ForConditionalGeneration` checkpoint and PEFT matches `target_modules` by **name
suffix**, so `q_proj` would attach LoRA to the vision tower as well. `peft_exclude_modules:
[vision_tower, multi_modal_projector]` is declared per model and passed to `LoraConfig`.

## 3. Recommended panel and the gate every new model passes

**Panel (recommendation).** Three lineages × {code, general}, with the CodeLlama scale ladder as
the spine and one true pretrained checkpoint:

| lineage | code model | general model |
|---|---|---|
| Meta | CodeLlama-7b / 13b / 34b (`codellama-*`, exist) | Llama-3.1-8B-Instruct (`llama31-8b`, exists) + **Llama-3.1-8B pretrained** (`llama31-8b-base`) |
| Google | **CodeGemma-7B-it** (`codegemma-7b`) | **Gemma-3-12B-it** (`gemma3-12b`) |
| BigCode / IBM | **StarCoder2-15B-Instruct** (`starcoder2-15b`) | **Granite-3.1-8B-Instruct** (`granite31-8b`) |

That is **five new models — all five adopted 2026-09-09** and entered in `configs/models.yaml`
with `role: candidate_main`, every `n_layers`/`hidden_size` read from the downloaded
`config.json` rather than a model card. Alternates (Mistral-7B-v0.3, OLMo-2-13B) stay under
`candidates:`. If the budget or the queue forces a cut, the order of importance is
StarCoder2-15B (different pretraining pipeline) > Gemma-3-12B (already on disk, 2025) > Llama-3.1-8B
pretrained (the base-vs-instruct axis, already on disk) > CodeGemma-7B > Granite/Mistral. OLMo-2 is
the right choice **if** the paper makes a contamination argument (§4.2) — it replaces Granite in
that case.

**What runs on every panel model** (the *core arms*; the full 116-system panel stays CodeLlama-7b):
`base`, `tuned_L0`, `mono_all`, `cons_lam3` (teacher = that model's own `tuned_L0`), `tuned_X1`;
evaluated on the six ladder conditions, X1, the six depth-2 composites, and F2's unseen-in-stack
composites. That is enough to reproduce RQ1's breadth dissociation, RQ3's repair, and RQ4's
unseen-in-stack read per model; RQ2's cue evidence (X1 split, order pair) stays CodeLlama-7b.

**Gate protocol per model** (pre-declared before any adapter is trained; the Llama-3.1 gate is the
worked example):
1. `configs/eval/basecheck_panel.yaml --model <key>` (model-neutral): untuned accuracy and `format_fail` on the seven columns. The model
   enters the panel if `format_fail` ≤ 0.15 on L0 and untuned L0 accuracy is within the range the
   paper can interpret (a base at 0.05 has no room for the −4 pt unseen tax to be visible).
2. Chat template renders a system role deterministically (`prompts.py` unchanged) — or, for the
   pretrained checkpoint, the plain-text prompt path is used and *declared*.
3. Truncation at `max_seq_len` re-gated on 1,500 `mono` rows (0 % at 2,048 is the target; Gemma-3
   and StarCoder2 tokenizers differ from Llama's).
4. `inspect_batch.py` loss-mask gate (prompt tokens −100) on one real batch.
5. Adapter-applied assertion on the first eval.
6. `tuned_L0` seed 17 must clear `base` by more than the seed band before `mono_all`/`cons_lam3` are
   queued (the Llama-3.1 rule: promote only if the tuned ceiling is real).

## 4. Dataset — what exists and what a reviewer will attack

**Exists.** Python corpus of **2,231 programs** (APPS 1,584 · CRUXEval 543 · HumanEval 104), split by
`program_id` into 1,563 train / 111 val / 557 test; **median 7 LOC, p90 15, max 57**, ≤ 2,500 chars;
3 train cases / 5 eval cases per program, execution-verified, deterministic across 3 runs, strict
normalised exact-match grading. A **train-only scale extension of 912 programs** (MBPP 750 · CSN
~160 real GitHub functions) with the test set frozen. The **human-baseline test set** (Papers 2–3:
40 programs, legacy tiers, 98 graded cells). Seven trainable conditions + X1/X1m/X1s/X2/Y2 + ten
composites, all with SHA manifests and the H1-marker scan. JavaScript: 2,022 train pairs / 504
held-out items per condition, intact but not regenerable (no `node`).

**The four objections, and the answer to each.**

### 4.1 "Toy functions" (median 7 LOC)
True, and partly by design: output prediction must be execution-gradable and the obfuscators must
gate. Two mitigations, both cheap: (a) report the LOC distribution and a **length-stratified**
read of every headline contrast (short / medium / long tertiles — the E11 machinery already
stratifies by LOC); (b) add a **long slice**: raise `loc_max` to 120 for a CSN-only build and run
it as an *evaluation-only* column (no training), so the claim "the dissociation holds on 60–120 LOC
real-world functions" is either made or withdrawn.

### 4.2 Contamination
HumanEval, MBPP and APPS are in the pretraining data of every 2023–25 model. The paper's contrasts
are all *between tuned arms on the same items*, and the discriminating column is an obfuscation
family the pretraining data cannot contain — but `base` and L0 numbers are still exposed. Answer
with a **post-cutoff slice**: LiveCodeBench call-based Python problems with release dates after
every panel model's cutoff (filter ≥ 2025-01 to clear Gemma-3 and Llama-3.1), built through the
same corpus pipeline (execution gate, dedup against the existing corpus, program-id split), used as
an **evaluation-only** column. If the headline contrasts reproduce on it, contamination is answered;
if `base`/L0 accuracy drops but the contrasts hold, that is the expected and reportable shape.
OLMo-2 (§2) turns this from an argument into a measurement: its pretraining corpus is public, so
overlap with our programs can be counted.

### 4.3 "Synthetic obfuscators"
All seven conditions are our own generators. Add one **off-the-shelf obfuscator column**,
evaluation-only: Python — `python-minifier` (rename + minify; a real-world analogue of L1r/L2)
and, if `node` is restored (§5), `javascript-obfuscator` at a preset the H1 generator does not use.
The claim becomes "an in-the-wild obfuscator behaves like the seen-family or the unseen-family
column", which is exactly the question RQ1 asks, on a transform nobody in the project wrote.

### 4.4 Single language
JavaScript is blocked only on the absence of a `node` binary — and the login/compute nodes are
x86_64 with glibc 2.34, so the official Node 22 tarball runs **in user space with no admin**
(`$OBTUNE_ROOT/../tools/node`, on `PATH` from `scripts/env.sh`). That unblocks regenerating the JS
ladder, a JS X1, and the H1/JS generator. It also retires the `transpiler` dependency on Qwen for
JS tier 3 (reassigned to `llama31-8b` in `models.yaml`; tier 3 is not needed for the paper).

## 5. Dataset plan, in order

| # | addition | kind | cost | what it buys |
|---|---|---|---|---|
| D1 | length-stratified reads of every headline contrast | analysis | CPU, hours | answers 4.1 without new data |
| D2 | user-space `node` → JS ladder + JS X1 regenerated | infra + CPU build | ~1 day CPU | answers 4.4; gives E13 its missing unseen column |
| D3 | LiveCodeBench post-cutoff eval slice (target ≥ 300 programs after gating) | corpus build, eval-only | ~1 day CPU + ~1 GPU-h per model | answers 4.2 |
| D4 | `python-minifier` (and `javascript-obfuscator` after D2) eval column | generator wrapper, eval-only | ~0.5 day CPU + 0.5 GPU-h per model | answers 4.3 |
| D5 | CSN long slice, `loc_max` 120, eval-only | corpus build | ~0.5 day CPU + 0.5 GPU-h per model | answers 4.1 with data |

None of D1–D5 changes the training corpus; every adapter already trained stays valid. D3–D5 are
**evaluation-only columns** and inherit X1's own-namespace rule: never pooled with the ladder, never
used to select anything.

## 6. Cost

Per new 7–9B model, core arms + evals: `tuned_L0` 22 min + `tuned_X1` 22 min + `mono_all` 3.5 h +
`cons_lam3` 4.4 h + ckpt-select + ~40 min eval ≈ **9.5 GPU-h**; 12–15B ≈ **17 GPU-h**; the gate
itself ≈ 10 min. Five new models ≈ **60 GPU-h**; the three-model minimum (StarCoder2-15B, Gemma-3-12B,
Llama-3.1-8B pretrained) ≈ **43 GPU-h**. Dataset additions D3–D5 add ≈ 2 GPU-h per panel model.
Downloads: CodeGemma-7B ~17 GB, StarCoder2-15B ~32 GB, Granite-8B ~16 GB, OLMo-2-13B ~27 GB —
`/work` has 101 TB free.

---

## Changelog
- **2026-09-09 (b)** — All five adopted and entered in `models.yaml`. §2a added: **three of the five
  reject the system role** (StarCoder2, CodeGemma) or have no chat template at all (pretrained
  Llama-3.1), measured on the real tokenizers before any weights were pulled; `prompts.py` gained a
  single verified adaptation layer that every path routes through, covered by 30 tests, and the
  identity in `system` mode so no existing adapter is affected. Gate config is model-neutral
  (`eval/basecheck_panel.yaml --model <key>`). Gemma-3 needs `peft_exclude_modules` for its vision
  tower. Downloads submitted (StarCoder2 385346, CodeGemma 385353, Granite 385360); gates submitted
  for the two already on disk (Gemma-3 385500, pretrained Llama-3.1 385501).
- **2026-09-09** — Created. Chinese-origin models barred from the paper; Qwen panel results withdrawn
  from the evidence base (kept as record); five-model non-Chinese panel recommended across three
  lineages × {code, general} plus one pretrained checkpoint; gate protocol fixed; dataset objections
  4.1–4.4 answered with evaluation-only additions D1–D5, none of which touches the training corpus.
