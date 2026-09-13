# 2026-09-13 — `merge_panel` was not in the schema's phase literal; two evals died at the first row

**Thread:** modularity · **Status:** fixed, resubmitted · **Related:** [`2026-09-13_f1-routing-and-merging-on-stacks.md`](2026-09-13_f1-routing-and-merging-on-stacks.md)

`ev_merge_granite31-8b` (393027) and `ev_merge_llama31-8b` (393028) failed 4 min 39 s in — after the
vLLM engine came up and the first generation pass ran — on `TrialRow.phase`'s literal: `merge_panel`
was a new phase name and `src/obtune/schema.py` did not list it. Zero cells written. The same class
of fault as the 2026-09-11 F2 composite codes (schema literal missing a new value, caught after
generation), which is exactly what `scripts/validate_eval_configs.py` check 1 exists to catch — and
it did: the validator reported `phase='merge_panel' is not in TrialRow.phase`. **I did not see it.**
I ran the validator with `--model granite31-8b`, piped through `grep -i "merge_panel\|error" | head -5`,
and the first five lines were unrelated errors from a CodeLlama-only config, so the `merge_panel` line
was cut off and I read the truncated output as "no errors for it". The validator worked; the reader
truncated its output. Rule going forward: filter the validator's output on the config's own name
alone, never with `head`.

Fix: `"merge_panel"` added to the phase literal; `tests/test_baseline_configs.py` passes; the
validator now shows no `merge_panel` line. Granite and Llama evals resubmitted; the StarCoder2 eval
(393029) was still queued and reads the patched code at start.
