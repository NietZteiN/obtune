### Target Date: 2026-09-01 (Model-agnostic by lint, and the model pin the lint could not see)

- **Hypotheses / what we're testing:** engineering, not science. **H-swap — the codebase can
  follow a base-model change without a rewrite.** CONFIRM if a full replication runs on a new
  family with config-level changes only. REFUTE if code has to move.

- **Setup:** Qwen and DeepSeek became unusable on this cluster; CodeLlama-7b/13b-Instruct are
  the new panel. Refactor + a 51-job dependency-linked DAG
  (`scripts/slurm/pipeline_replication.py`), ~20 GPU-h, ~6 h wall-clock at `MaxJobsPU=4`.

- **Results:**
  - **H-swap SUPPORTED, with one real code fix.** `prompts.py` needed NO change: it builds a
    message list and calls `apply_chat_template`, and CodeLlama accepts a system role
    (`[INST] <<SYS>>`). Verified from the tokenizer alone before pulling 13 G of weights.
  - **`max_seq_len` re-gated to 2048, not inherited.** CodeLlama tokenizes ~17 % longer than
    Qwen (mean 458 vs 393, p95 813 vs 709). At Qwen's 1536 the truncation rate would be
    0.20 %; at 2048 it is 0.07 %, matching Qwen. Confirmed in training at 0.064 %.
  - **Model-agnostic changes:** `train_sft --model`; `layer_fracs` replacing the absolute
    `[4, 9, 14, 19, 23, 27]` (Qwen's 28 layers -> different RELATIVE depths on 32 or 40);
    `--model` required, no defaults, in five modules that were pinned to `qwen25c-1.5b`;
    `{model}`/`{language}` templating in adapter paths; `tests/test_model_agnostic_lint.py`.
  - **The lint immediately caught real coupling** in `attention/validate.py`, whose span->token
    resolution is tokenizer-dependent and was pinned to a Qwen id.

- **What worked / hypothesis verdict:** SUPPORTED. The replication ran on config changes plus
  the fixes below, and every scientific finding reproduced
  (`../transfer/2026-09-01_codellama-replication.md`).

- **Observations:**
  - **The lint could not see the pin that mattered.** `configs/train/_base_lora.yaml:4`
    declares `model: qwen25c-1.5b`, and every "model-neutral" config `_extends` it -- so they
    were never neutral. Training escaped only because `train_sft` applies `--model`;
    `run_ckpt_select` ignored it and built a **Qwen-1.5B** engine for a **CodeLlama** LoRA,
    dying as `RuntimeError: The size of tensor a (1536) must match the size of tensor b
    (4096)` -- a message naming neither model. `run_grid` had the same shape: `--model`
    RESTRICTED a config-declared list rather than supplying one, so the neutral eval configs
    would have `KeyError`d. **17 jobs and everything downstream were doomed at submission.**
    The lint checks hardcoded HF ids and argparse defaults; a model pinned in an INHERITED
    BASE CONFIG is invisible to both, and it is the highest-leverage place to hide one.
  - **I verified neutrality in a way that could not fail.** The pre-flight check simulated
    `expand_systems` with the model passed explicitly -- bypassing the exact resolution path
    that was broken. The check confirmed the assumption instead of testing it.
  - **A DAG cannot be repaired in place once a stage has failed.** `scontrol update
    Dependency` is REFUSED when the list references completed jobs (`Job dependency problem`),
    so recovery is cancel-and-resubmit with a MINIMAL dependency set naming only still-active
    jobs. One missed failure re-poisoned six downstream jobs into `DependencyNeverSatisfied`,
    which is permanent.
  - **Query for all failures; do not inspect the one you are watching.** The first repair
    fixed `ck_L0_s17` and missed `ck_L0_s42`, because a targeted watch answers the question
    asked rather than the one needed.
  - **Fan-in dependencies need ONE `afterok:` prefix**, then colon-separated ids. The first
    launch treated any string containing ':' as pre-prefixed, so all six fan-in jobs silently
    failed to submit: 45 jobs queued happily with **no terminal stages** -- a pipeline that
    looks healthy and can never produce a result.
  - **The login node is for submitting.** Merging loads the 7B base in float32 and dies there
    with `MemoryError`; `/tmp` is node-local, so a script staged there is invisible to compute.

- **New questions / new hypotheses:** **the lint should assert that no config under
  `configs/train/` resolves a `model` key unless explicitly declared** -- i.e. that inheritance
  cannot inject one. That is the generalisation of this bug and it is mechanically checkable.

- **Next Steps:** (1) Extend the lint to inherited pins. (2) Fold the fan-in prefix and the
  minimal-dependency recovery into the driver's docstring (done). (3) `git remote` is still
  EMPTY -- commits protect against working-tree accidents, not against losing the machine.
