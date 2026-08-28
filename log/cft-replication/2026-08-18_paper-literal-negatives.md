### Target Date: 2026-08-18 (the paper-literal negative construction — the promised control, run at last)

- **Hypotheses / what we're testing:** **H-N1 — is our deviation on negatives what produced the
  contrastive null?** Our `cft` arm builds negatives by mutating the *obfuscated* variant, so
  positives and negatives are equally obfuscated. `nikiema2025contrastive` §5.0.2 builds them from
  clean programs of different semantics, which makes "is program B obfuscated?" a perfect predictor
  of the label. We argued that shortcut makes the published construction unusable as a test of
  semantic comparison. The standing objection is that the shortcut *is* the active ingredient: a
  model forced to represent obfuscated-ness explicitly has done part of the work of undoing it.
  `docs/CFT_REPLICATION.md:90-91` promised this "can be measured rather than argued about" and it
  never was. **Verdict: H-N1 REFUTED. The deviation is not what produced the null.**

- **Setup.** New arm `cftclean` = `cft` with `negative_style: clean_mutant`, 1.5B, seed 17,
  identical in every other respect. Configs: `configs/cft/train/cftclean_qwen1.5b_py.yaml`,
  `configs/srh/eval/e9_cleanneg_qwen1.5b.yaml`. Pool
  `data/train/cft/python__cleanneg/`; adapter
  `runs/adapters_cft/qwen25c-1.5b/python/cftclean_r32_s17/`; results
  `results/2026-08-18_cft-bidirectional/qwen25c-1.5b/python/e9_cleanneg_qwen1.5b/`.
  Commit `f1a3247`, GPU 0. Train 9,533 s (2.65 h), 915 steps, 19,498 instances.
  All four arms scored in **one** evaluation pass, 12,000 prompts — necessary because the
  cross-pass determinism floor is ±0.3 pp and the contrast of interest is ~0.3 pp wide.

- **⚠️ A near-miss worth recording before the result.** `scripts/cft/10_build_cft_data.py` writes
  pools to `data/train/cft/<lang>/` with **no output-dir parameter and no versioning**, so
  `--negative-style clean_mutant` would have silently overwritten the pools every published number
  in `paper_bidirectional` was trained on. Fixed before building: `cft_dir()` now takes a
  `variant` that selects a *sibling* directory, threaded through `pool_path`/`report_path`/
  `write_pools`/`load_pool`/`load_mixture`, and the build script now `ap.error`s if a non-default
  `--negative-style` is passed without `--variant`. Verified after the build that
  `data/train/cft/python/` still carries its 2026-08-08 mtimes.

- **Results.** Strict reverse success, 1.5B, 300 programs, 1,500 trials/arm, `simple` strategy:

  | arm | strict reverse | vs `cft` | vs `sft` | vs `base` |
  |---|---|---|---|---|
  | `base` | 2.8 % | — | — | — |
  | `sft` | 0.2 % | — | — | −2.6 [−3.5, −1.7] |
  | `cft` | 0.2 % | — | +0.0 [−0.3, +0.3] | −2.6 [−3.5, −1.7] |
  | **`cftclean`** | **0.5 %** | **+0.3 [−0.1, +0.7]** | **+0.3 [−0.1, +0.7]** | **−2.3 [−3.3, −1.4]** |

  Paired cluster bootstrap by `program_id`, 2,000 resamples, seed 17, via
  `scripts/srh/24_contrasts.py` → `contrasts.md`.

- **What worked / hypothesis verdict:** REFUTED, and the refutation is stronger than the argument
  it replaces.
  - The paper-literal construction recovers **nothing**. `cftclean` is indistinguishable from both
    our `cft` and plain `sft`, and sits 2.3 pp *below* the untouched model.
  - It fails on a setup that is **more** favourable to the objective than our main arm: the
    `cleanneg` pools are *larger* (6,058 pos/neg against 5,611), because `clean_mutant` mutates the
    L0 parent once and reuses it across conditions rather than mutating each variant.
  - Training loss is essentially identical (`cftclean` 0.3537, `cft` 0.3544), so the two arms
    differ in what they were shown, not in how well they fitted it. That is the sentence that
    closes the objection: you cannot attribute the null to a badly-trained arm.
  - Adapter-applied check (CLAUDE.md §4.2): eval log reports "3 distinct adapter(s)", and
    `cftclean` differs from `cft` on every metric (forward exec .928 vs .943, reverse exec .774 vs
    .759, gen tokens 217.2 vs 213.9). Not a silently-unloaded LoRA.

- **Observations:**
  - **Loss looked absent for 2 h and was not.** `logging_steps: 20` should have produced a loss
    line every 20 steps; the console log had zero at step 124. Cause: the trainer's stdout is
    block-buffered to a regular file while the tqdm bar goes to stderr, so the loss dicts sat in an
    unflushed buffer. `trainer_state.json` in `checkpoint-305` had all 15 points, decreasing
    0.850 → 0.339, `eval_loss` 0.2531, no NaN. **For any run launched outside the scheduler,
    `trainer_state.json` is the liveness check, not the log tail.** Diagnosing this required
    reading `/proc/<pid>/fd/1` — five of the six `pgrep` hits were dataloader workers and waiter
    scripts, only pid 2556426 was the trainer.
  - `base` at 2.8 % sits inside the 2.6–3.0 % anchor band from the determinism work, so this pass
    is calibrated against the earlier ones.

- **Next steps:**
  - Paper: Appendix C carries this; the theoretical shortcut argument in Appendix B is retained but
    is no longer the only support for that point.
  - The `clean_mutant` path is now exercised, so `docs/CFT_REPLICATION.md:90-91`'s promise is
    discharged. Update that line.
  - Not run: `cftclean` at 7B, and a `neg`-pool parity sweep. Neither is a dependency.
