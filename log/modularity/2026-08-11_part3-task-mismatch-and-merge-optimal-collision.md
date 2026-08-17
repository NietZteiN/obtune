### Target Date: 2026-08-11 (Part III would have trained on the wrong task; merge-optimal names collided)

Second modularity entry today. The first,
[2026-08-11_routerlora-build-and-composite-purity.md](2026-08-11_routerlora-build-and-composite-purity.md),
reported the RouterLoRA build as complete and verified. **This entry corrects that**: an audit of
code that had never executed found two defects that would have invalidated the arm. Nothing in the
morning entry is altered; this supersedes its readiness claim.

- **Hypotheses / what we're testing:** Not an experiment — an audit, prompted by "check for bugs in
  the pipeline". The target was deliberately chosen as *code that has never run*, on the grounds
  that everything already executed has at least been smoke-tested by execution itself. Two
  questions: (a) does each new script run at all, and (b) does each identifier encode what
  actually varies — the shape every prior bug in this project has taken.

- **Setup:**
  - Host `csr-94608.utdallas.edu`, commit `469f857` (working tree dirty at time of writing),
    env `/data/jvl210002/conda_envs/obtune`. GPUs 0–1 only (2–3 lent, see CLAUDE.md §1).
  - Audited: `scripts/merge/22_merge_optimal.py`, `src/obtune/mole/train_mole.py`,
    `src/obtune/mole/eval_mole.py`, `configs/mole/routerlora_v1.yaml`,
    `configs/eval/mole_ladder_qwen1.5b.yaml`, and the `p3_*` / `t2_*` stages of `pipeline.sh`.
  - Method: run each entry point (`--plan`, `--dry-run`, `--stub`), then compare what each
    component *claims* to do against what it *does*, by printing the actual artefacts rather
    than reading the code.

- **Results:**

  **1. The gate would have been trained on a different task from the one it is scored on.**
  `train_mole.build_records` used `cft.prompts.build_gen_messages`, which emits

  > *system:* "You are a source-to-source code transformation tool..."
  > *user:* "Obfuscate the following Python code by random variable renaming..."
  > *target:* the obfuscated **program**

  while `eval_mole` scores through `eval_vllm.run_cell`, whose prompt is

  > *system:* "You are a deterministic code execution engine..."
  > *user:* "... Call: f(1,) / Return value:"
  > *target:* the **return value**

  These are different tasks, not different templates. CLAUDE.md §4 silent-failure #3 in its most
  severe form: the gate would have trained cleanly, converged, and produced a plausible accuracy
  answering no question at all. Root cause was modelling `train_mole` on `srh/train.py` (genuinely
  a code→code task) instead of `train_sft.py`, which is what the eight experts were trained with.

  Fixed by routing through `data.build_sft_splits`, the same path `train_sft.py` uses. Verified:
  36 195 train / 2 580 val records, completion is now a return value (`'4'`), system prompt is the
  execution engine's.

  **2. The training mixture excluded the composites — the whole premise of the arm.**
  `mixture_kwargs.conditions` was `[L1b, L1r, L2, S1, S2]` while `eval_conditions` is 6/8
  composite. The gate would never have seen the ambiguous case where no single expert is correct,
  which is the only condition under which a mixture can beat a hard router. Config now trains on
  all 8 single conditions plus all 6 composites.

  **3. Composites are outside `TRAINABLE_CONDITIONS` by design, and blocked correctly.**
  `load_pairs` refused them loudly — the quarantine layer working as intended, since widening that
  tuple would ripple into `merge_adapters`, `transfer`, `cft/` and `router.features`. Resolved with
  a narrow opt-in, `load_pairs(..., allow_composites=True)`, defaulting to the existing strictness.
  A composite is accepted only if the composite ladder itself declares it `trainable: true` and no
  part is H1. **H1 remains refused with the allowance on**; the other two quarantine layers are
  untouched. Six tests pin this, including a synthetic `C_L1r_H1` that must be excluded.

  **4. Merge-optimal candidate names did not encode the other experts' epochs.**
  `mo_r1_L1b_e3` meant "L1b at epoch 3, everyone else at the incumbent" — and the incumbent *moves*
  as the greedy search runs. Demonstrated: `{L1b:3, S1:9, S2:9}` and `{L1b:3, S1:3, S2:1}` both
  produced that identical name. Because `merge_adapters` skips an existing
  `adapter_model.safetensors` and `run_cell` resume skips an existing `trials.parquet`, a pipeline
  restart mid-loop would have **silently scored the wrong merge** and optimised on it. Fixed by
  folding a digest of the full epoch assignment into the name, and by reading the winner's
  target/epoch off the candidate object rather than re-parsing the name string.

  **5. Checked and clean.** `obtune.prompts.build_prompt(oracle=False)` handles composites, so the
  eval path is safe; `oracle=True` raises `KeyError` on `C_` codes, so `prompt.oracle` is pinned
  false in the config with a comment. Pipeline trap patterns: 0 instances of `python … || say`
  swallowing an argparse exit; the `running/*/*.json` globs are correctly 2-deep.

- **Observations:**
  - Every defect was in code that had never executed. Preflight, the test suite and `make check`
    were all green throughout — they check what is declared, not what is meant.
  - Defects 1 and 4 are the same shape as every prior bug here: **an identifier or code path that
    does not encode what actually varies.** In (1) the record builder did not encode which task;
    in (4) the candidate name did not encode which merge.
  - The morning entry's "Part III is built and verified" was true of the mechanics — the dry-run,
    the loss mask, the freeze assertions all passed — and false of the science. Mechanical
    verification cannot catch a component that works perfectly on the wrong input.

- **Next steps:**
  - `p3_composites` must run before `p3_mole_train`; the stage guard now correctly requires
    composite pairs, and the trainer fails loudly if they are absent.
  - When Part III produces numbers, `mole_random` is the control that decides what the headline may
    say. If `mole_router ≈ mole_random` the gain is rank-256 residency, not routing.
  - Still open, unchanged: `stats/R/config.R` needs the composite levels before any `C_` trial
    reaches the R stack.
