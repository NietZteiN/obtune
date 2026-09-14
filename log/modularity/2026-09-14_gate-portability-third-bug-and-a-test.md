# 2026-09-14 — A third Gemma-3 gate bug, and the test that should have caught all of them

**Thread:** modularity · **Status:** fixed and covered by a test · **Extends:** [`2026-09-14_gate-training-two-portability-bugs.md`](2026-09-14_gate-training-two-portability-bugs.md), which is not amended

After the chat-template and `hidden_size` fixes, Gemma-3's gate failed a third time:

```
ValueError: could not locate the decoder layer list on this model
```

`_decoder_layers` walked four paths — `model.layers`, `model.model.layers`, `transformer.h`,
`model.decoder.layers`. Gemma-3 is multimodal and its decoder is under the **text tower**,
`model.language_model.layers`. Three paths added; verified on meta-device instantiations: Gemma-3 48
layers, CodeLlama-7B 32, Granite 40, CodeGemma 28.

## The part worth keeping

**Three bugs, three failed jobs, ~40 GPU-minutes, and every one of them was answerable in under a
second without a GPU.** Each surfaced only after the weights had loaded, twelve minutes into a
two-hour job, and each was found by reading a traceback from a queue rather than by asking the
question up front.

`tests/test_mole_panel_portability.py` now asks all three for all eight models:

- `_hidden_size` resolves and `_decoder_layers` finds a non-empty list, on a `torch.device("meta")`
  instantiation — no weights, no GPU, sub-second;
- `render_pair` does not raise and preserves the system text, for every tokenizer in the panel.

Sixteen cases, all passing. This is the same move as `tests/test_quarantine_lint.py`: turn a class of
mistake that only shows up at run time into something a commit can catch.
