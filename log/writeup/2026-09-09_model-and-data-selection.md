### Target Date: 2026-09-09 (scope: no Chinese-origin models; panel and dataset plan for FSE)
- **Hypotheses / what we're testing:** Organisational; no run, no read. The user ruled that no Qwen (and, by
  the same rule, no DeepSeek/Yi/InternLM/GLM) model may be used, and asked for a model and dataset selection
  adequate for an FSE paper — "code models and base models".
- **Setup:** `docs/MODEL_AND_DATA_SELECTION.md` created; `configs/models.yaml` marks `qwen25c-1.5b`/`qwen25c-7b`
  `role: barred`, reassigns `transpiler` to `llama31-8b`, and lists candidates under a separate
  `candidates:` key that no loader resolves (`config.py`/`eval_hf.py`/`merge_adapters.py` read `["models"]`
  only). `PAPER_FRAMING.md`, `PAPER_EXPERIMENTS.md` (F10/F11) and `RQ_SUMMARY.md` carry the scope banner.
  Facts checked on disk: HF cache holds Gemma-3-12b-it (23 G), Gemma-3-4b-it, Llama-3.1-8B pretrained (30 G),
  Phi-3.5-mini (7 G) — all non-Chinese and unused; a token sits at `$HF_HOME/token`; the nodes are x86_64 /
  glibc 2.34, so the official Node tarball runs in user space (JS is not admin-blocked); corpus is 2,231
  programs, median 7 LOC, p90 15, max 57; scale corpus 912 train-only programs (MBPP 750, CSN ~160).
- **Results:** none. Two consequences of the rule for the evidence base: the Qwen composite dissociation
  (+3.91) is no longer cited (the CodeLlama reads at 7B/13B/34B carry it), and the Qwen task-vector geometry
  refutation (`REPORT_2026-08-17` §3) can no longer be used to reject the "interference" mechanism for
  merging — F1b (CodeLlama, cross-seed) is now required rather than descriptive.
- **What worked / hypothesis verdict:** n/a.
- **Observations:** Recommended panel = three lineages × {code, general} + one pretrained checkpoint:
  Meta (CodeLlama 7/13/34 + Llama-3.1-8B-Instruct, exist; + Llama-3.1-8B pretrained, on disk), Google
  (CodeGemma-7B-it + Gemma-3-12B-it, on disk), BigCode/IBM (StarCoder2-15B-Instruct + Granite-3.1-8B or
  Mistral-7B-v0.3). Priority StarCoder2 > Gemma-3 > Llama-3.1 pretrained > CodeGemma > Granite; OLMo-2 if a
  contamination *measurement* is wanted. Per model: the Llama-3.1-style gate, then `tuned_L0`/`tuned_X1`/
  `mono_all`/`cons_lam3` + evals ≈ 9.5 GPU-h (7–9B) / 17 (12–15B); five models ≈ 60 GPU-h. Dataset: the
  training corpus is untouched; four reviewer objections (toy functions, contamination, synthetic
  obfuscators, single language) each get an evaluation-only column — D1 length strata, D2 user-space node →
  JS + JS X1, D3 LiveCodeBench post-cutoff slice, D4 `python-minifier`/`javascript-obfuscator` column, D5 CSN
  long slice.
- **New questions / new hypotheses:** H-F10-dissociation, H-F10-repair, H-F10-base-vs-instruct, and the
  D3/D4/D5 rules — drafted in `PAPER_EXPERIMENTS.md` F10/F11, to be frozen in the scratchpad before submission.
- **Next Steps:** user picks the panel size (five vs three); then: download StarCoder2-15B (32 GB), write
  `basecheck_*.yaml` for StarCoder2 / Gemma-3 / Llama-3.1-pretrained, run the gates (~10 min each), and only
  then queue adapters. Install user-space node in parallel (no GPU, no admin).
