### Target Date: 2026-09-11 (a named adapter that is not on disk silently evaluated the BASE model under the arm's name — now a hard error)
- **What happened.** While checking F2's eval config by hand before spending a GPU, `merge_dare_ties`
  resolved to nothing: the config said
  `runs/adapters/{model}/{language}/merge_dare_ties_r32_s17/**best**`, and a merge has no training
  run and therefore no checkpoint subdirectory — the weights sit at the directory itself.
  `h1_confirm_codellama.yaml` already addresses `l0merge` correctly and was the reference.
- **Why it matters more than one typo.** `eval_vllm` did not fail on it. The engine has nothing to
  apply, generation proceeds on the **base model**, and the cell is filed under the arm's name. The
  only trace was the literal string `"missing"` in the run's `adapter_sha256` metadata, which no
  analysis reads. That is CLAUDE.md §4's silent-failure #2 — *"adapter not applied — assert the
  tuned model's outputs actually differ from the base"* — arriving in `results/cells/` as a number.
  A merge arm reading exactly like `base` would have been interpreted as "merging destroys the
  gains", which is *the direction the paper already claims*, and is the worst possible way for a
  path bug to be wrong.
- **Fix.** `eval_vllm` now checks every distinct adapter path for `adapter_model.safetensors` (or
  `.bin`) immediately before generation and raises `FileNotFoundError` naming the system, the
  resolved path, and the likely cause. Failing there costs one queue slot. Not failing costs a
  published number that is the base model wearing another arm's label.
- **Why the check is at generation and not at config load.** The path carries `{model}`/`{language}`
  placeholders and is only concrete once a cell is being run, so a load-time check would either
  miss the real path or have to guess the model. Placing it one line before `engine.generate`
  covers the routed and oracle-routed paths too, which build their adapter lists differently.
- **Related.** `configs/eval/panel_core.yaml`'s header already warned that a wrong config "would
  either fail on a missing adapter or, **worse**, silently skip arms". It was the second of those.
  The header's prediction was right and the guard it implies did not exist.
- **Not claimed:** that any published cell is affected. Every committed config was checked after the
  fix and all adapter paths resolve; this was caught on a config written today and never run.
- **Next Steps:** none. `scripts/preflight_panel.py` could grow the same check per config, which
  would move the failure from job start to submission time.
