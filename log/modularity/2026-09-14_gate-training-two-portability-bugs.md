# 2026-09-14 — Router-gate training had two portability bugs, both fatal twelve minutes in

**Thread:** modularity · **Status:** both fixed and verified

Six gate runs failed before the mixture arm could exist off CodeLlama. Both causes are the same
shape: `train_mole.py` was written against CodeLlama and never carried to the panel.

## 1. `TemplateError: System role not supported` (CodeGemma)

`render_pair` called `tokenizer.apply_chat_template` on the raw messages. CodeGemma and StarCoder2
refuse a system role. `prompts.py` has had **one adaptation layer** for this since 2026-09-09 and
`train_sft.py` routes through it (`template_mode` → `to_trl_example`); `train_mole.py` never did.
Now both call sites go through `prompts.adapt_messages`, which is the identity in `system` mode, so
CodeLlama's existing gate is unaffected. Verified: system text preserved for CodeGemma (`merged`),
Gemma-3 and CodeLlama (`system`).

## 2. `AttributeError: 'Gemma3Config' object has no attribute 'hidden_size'` (Gemma-3)

Gemma-3 is multimodal: the text tower's `hidden_size` lives on `config.text_config`, not at the top
level. `mole/model.py` read `base.config.hidden_size` directly. Added `_hidden_size(config)`, which
falls back to `text_config`. Verified: Gemma-3 3840, CodeLlama-7B 4096, Granite 4096.

## What this cost, and the pattern worth naming

Six jobs, ~75 GPU-minutes, and the drain kept resubmitting because a failed manifest returns to the
queue — correct behaviour that turns a deterministic bug into a loop. Both failures land **after the
weights load**, so they cost twelve minutes each rather than twelve seconds.

The pattern: every panel-portability fix so far has had to be applied per module. `prompts.py` holds
the adaptation layer, `train_sft.py` uses it, `eval_vllm.py` uses it, `train_mole.py` did not. Worth a
test that asserts every module rendering a chat template goes through `adapt_messages` — the same
shape as `tests/test_quarantine_lint.py`, which greps for raw file reads that bypass the quarantine
entry point.
