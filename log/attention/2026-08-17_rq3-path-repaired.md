### Target Date: 2026-08-17 (RQ3 opened: the analysis path could not read its own captures)

- **Hypotheses / what we're testing:** Setup day. RQ3 (attention re-anchoring) is the last untouched
  third of the stated research goal — only the span→token validator had ever run (100 % over 413
  programs). Before spending GPU on a real sweep, two things had to be established:
  - **H1.** Does the attention path render prompts with the SAME frozen builder as the accuracy
    grid? CLAUDE.md §1 and silent-failure #3 make this load-bearing: attention cannot use vLLM, so
    if the two paths diverge, Δ-attention is measured on a different distribution than the accuracy
    it is meant to explain, and RQ3's whole claim is a correlation between those two quantities.
  - **H2.** Does the capture → metrics → anchoring chain actually run end to end on real dumps?

- **Setup:** Host `csr-94608`, GPU 1, all four cards free. Smoke capture of 4 items from
  `data/eval/heldout/items/S2/python.jsonl`, layer 14, model `qwen25c-1.5b`, system `base`, written
  to a scratchpad path so nothing entered `results/`. Analysis run in-process against those dumps.

- **Results:**
  - Capture works: 4 npz + 4 sidecars, `rows` [1, 12, 469], 469 tokens, `code_span` (810, 1444).
  - **H1 SUPPORTED for the path that runs.** `eval_hf.py` imports `build_prompt` at MODULE level
    (line 37), so an import failure is a hard `ImportError`, not a fallback. The sidecar records
    `prompt_sha = c1e8fe28c308`, matching the pinned accuracy-grid template.
  - **H2 REFUTED.** `metrics.load_attention_npz` raised `KeyError: meta_json` on the first real
    dump.

- **What worked / hypothesis verdict:** H1 supported, H2 refuted and repaired.

- **Observations:**

  **Two incompatible formats, and the analysis half read the wrong one.** `eval_hf.dump_attention`
  (line 162) writes the layout `results/attn/SCHEMA.md` documents: npz of
  `rows / layers / token_offsets / code_span / input_ids` beside a `.json` sidecar.
  `metrics.save_attention_npz` writes a different, older layout (`attn / layers / offsets /
  meta_json`) that NO writer in the project emits, and `load_attention_npz` understood only that
  one. So `metrics_table`, `anchoring_shift` and the `metrics.py` CLI — the entire RQ3 analysis —
  would have failed on the first file every time. Nothing caught it because the chain had never been
  run on captured data. Same signature as the 2026-08-11 audit: never-executed code that fails the
  moment it runs.

  Repaired: `load_attention_npz` now reads the documented layout (recovering `code` from
  `prompt_text[code_span]`, mapping SCHEMA's `system` to `AttentionRecord.model_state`) and keeps a
  legacy branch. Verified: `metrics_table` over the 4 dumps returns 4 x 30 with all seven
  `mass_*` token-class columns populated, which is what `anchoring_shift` consumes.

  **A parallel unused capture implementation, hardened but not a live bug.**
  `attention/capture.py` is a second, richer implementation (`AttentionRecord`, span-resolution
  rate, `extra`) that `eval_hf` does not call. Its `build_prompt_text` falls back to a built-in
  `_FALLBACK_PROMPT` if `obtune.prompts` fails to import, RECORDING the fact in
  `extra["prompt_from_prompts_module"]` and never acting on it — and `extra` is not even persisted
  to the sidecar, so the flag went nowhere. Added a hard gate (`allow_prompt_fallback=False`) that
  raises instead. **Verified by inducing the failure** with a `find_spec` meta-path blocker: the
  fallback is reachable, flags `False`, and renders a genuinely different prompt. This protects a
  path that is not currently wired in; stated plainly so it is not mistaken for a live-bug fix.

- **New questions / new hypotheses:**
  - Does the `S2` adapter re-anchor attention away from inert spans? §3.5 is now confirmed at power
    (`tuned_S2_s17` +3.46 [+2.06, +4.86] over the control on 1,214 `H1` items), so RQ3 has a sharp
    pre-registered hypothesis rather than a fishing expedition.
  - Which format should be canonical? SCHEMA.md documents the `eval_hf` one and that is what runs;
    `save_attention_npz` should either be rewritten to match or deleted, and the two capture
    implementations reconciled, before a real sweep hardens the duplication.

- **Next Steps:**
  1. Reconcile the two capture implementations (or delete the unused one) so there is one contract.
  2. Design the sweep: which systems (base / `tuned_L0` / `tuned_S2` at minimum), which conditions,
     which layers, and the stratified item subset.
  3. Then the pre-registered test: does anchoring shift predict transfer, and does the knockout
     (`knockout.evaluate_with_knockout`) make it causal.
