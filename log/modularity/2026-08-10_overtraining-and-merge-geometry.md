# 2026-08-10 — Does overtraining the experts harm merging? Not here, and the reason matters

*Thread: `modularity` (RQ2). First entry in this thread — the code was built and the router run
days ago, but nothing was ever logged. `log/README.md` said "not started" while
`results/router/.../routing_report.json` already held a saturated router.*

## Goal / hypothesis

Horoi, Wolf, Belilovsky & Dziugaite, *"From Memorization to Parameter Interference: How
Overtraining Experts Harms Model Merging"* (arXiv:2506.14126v2), argue that fine-tuning experts
to their **individual** optimum degrades merging: late training is dominated by memorization of
a few hard examples, which "causes negative parameter interference".

That describes this project's procedure exactly. `eval_vllm.run_ckpt_select` picks `best` by
held-in validation accuracy — individual performance — and every merge here is built from
`best`. The hypothesis under test: **our experts are overtrained, and that is why merging is
lossy.**

## Setup

- Host `csr-94608`, 4 × A6000. Seed 17 throughout. Env `/data/jvl210002/conda_envs/obtune`.
- New: `src/obtune/merge_geometry.py`, `scripts/merge/20_geometry_report.py`,
  `scripts/merge/21_epoch_sweep.py`, `tests/test_merge_geometry.py`.
- Geometry is CPU-only, from checkpoints already on disk: every expert has epoch-1/2/3
  checkpoints plus `final`.
- 9-epoch probe: `configs/train/overtrain_qwen1.5b_py_{L1b,S1,S2}.yaml`, writing to
  `runs/adapters_overtrain/`.

**The identity that makes the geometry free.** Frobenius inner products between LoRA updates
need no dense `dW`: with `dW_i = s_i B_i A_i`,
`<dW_i, dW_j>_F = s_i s_j · tr((B_i^T B_j)(A_j A_i^T))`, and both factors are r×r with r=32.
Verified against a dense computation to 5.6e-16 (`tests/test_merge_geometry.py`).

## Results

### Task-vector geometry across epochs (8 experts, python, 1.5B)

| epoch | mean ‖ΔW‖ | mean cos(i,j) | sign conflict | TIES retention |
|---|---|---|---|---|
| 1 | 0.2988 | 0.5836 | **0.4016** | 0.8537 |
| 2 | 0.3620 | 0.5868 | 0.3940 | 0.8584 |
| 3 | 0.3713 | 0.5922 | **0.3905** | 0.8608 |

`Δ(sign_conflict) = −0.0111`, `Δ(cosine) = +0.0086` → **`interference_grows = False`**.

### Merged-vs-single norm ratio, uniform-epoch merges

| epoch | `ties` ratio | `dare_ties` ratio |
|---|---|---|
| 1 | 0.193 | 0.637 |
| 3 | 0.192 | 0.634 |

### Catastrophic forgetting — the gate that had never once run

`results/forgetting/` was **empty**; CLAUDE.md §4.7 requires this per adapter. Two bugs had to
be fixed before it produced anything (below). Now complete, all with `n_scorer_errors = 0`:

| arm | HumanEval+ pass@1 | Δ vs base | L0 (in-domain) |
|---|---|---|---|
| `base` | 0.713 | — | 0.217 |
| `rev` | 0.628 | −8.5 | 0.217 |
| `flip` | 0.616 | −9.7 | 0.235 |
| `flipsym` | 0.610 | −10.4 | 0.258 |
| `mix50` | 0.543 | −17.1 | 0.233 |
| `cft` | 0.409 | −30.5 | 0.201 |
| **`sft`** | **0.372** | **−34.1** | 0.216 |

## Observations

**1. The mechanism is absent, and the reason is that we are not overtrained.** Sign conflict
*falls* with training and TIES retention *rises* — the opposite of the prediction. The cause is
visible in `trainer_state.json`: training loss is still falling steadily at epoch 2.5
(0.90 → 0.31 over 219 steps, 4626 rows). The existing bank never enters the regime the paper
describes, so it cannot test the claim — it can only show the claim does not apply to a model
that is still learning. **This is a boundary condition, not a refutation.** The 9-epoch probe
is what puts the regime in reach and is running now.

**2. The merge loses a constant fraction, independent of training length.** The
merged/single-expert norm ratio is 0.193 → 0.192 (`ties`) and 0.637 → 0.634 (`dare_ties`)
across epochs 1→3. Two independent measurements — coordinate sign conflict and aggregate norm
ratio — agree that interference does not worsen with training here.

**3. Sign conflict does NOT explain `merge_ties`' collapse.** Sign election retains 86 % of
mass, yet `merge_ties`' effective ‖ΔW‖ is 0.19× a single expert's. The shrinkage must come from
the density-0.5 trim plus averaging, not from experts disagreeing. Open thread; `merge_ties` is
also our weakest merge (0.287 on H1 vs `merge_dare_ties`' 0.348).

**4. Experts are highly aligned (mean cosine 0.58).** They share a large common direction with
small condition-specific parts on top. That fits the RQ1 finding that `L0` (clean-code)
training reaches H1 as well as obfuscated training does — most of what an adapter learns is the
output-prediction task, not the transform.

**5. A confound in every existing merge number.** `ckpt_select` chose a *different epoch per
condition* — `L1r`/`S3` at epoch 1, `L0`/`L1b` at epoch 2, `L2`/`S2`/`S1`/`S4` at epoch 3. So
the merges already combine task vectors of unequal training, and no existing number separates
"merging is lossy" from "we merged mismatched vectors". The uniform-epoch merges are the
control that had never been run; evals are in flight.

**6. Forward-only training is by far the most destructive to general code ability.** `sft`
loses 34 points of HumanEval+ and `cft` 30, against `flip`'s 10. In-domain L0 is untouched
throughout, so this is a genuine out-of-domain dissociation. It materially strengthens the
bidirectional headline: the free direction-swap is not only better at reverse, it is *less
damaging*. Report §6 claims bidirectionality is "not paid for in forward performance" — true,
but it *is* paid for out-of-domain, and forward-only is paid for far more.

### Bugs found (six, four of them near-misses that would have destroyed artifacts)

- **The forgetting gate had never run.** Two defects, both fixed: `forgetting.py` lacked the
  `drop_overlong` guard, so one 8193-token item killed the run; and the HumanEval+ scorer
  indexed `problems[tid]["expected_output"]`, a key that does not exist, so **every** task
  raised `KeyError` into a bare `except: continue` and `pass@1` came out a plausible-looking
  **0.0**. Expected outputs come from `get_groundtruth(...)`. A >10 % scorer-error rate now
  raises instead of reporting a number.
- **`adapter_dir` ignored training length** — the 9-epoch config resolved to the *same
  directory* as the 3-epoch expert and would have overwritten the bank the whole RQ1 matrix
  rests on. Added a backwards-compatible `adapter_root` override.
- **`build_manifest` job ids ignored it too** — the probe collided with the finished 3-epoch
  job, so its ckpt-select saw the dependency already in `done/` and would have fired early.
- **A worker claimed the bad job before the delete**, so two processes were training into one
  directory. Killed before any checkpoint was written.
- **Two `systems` shapes, no check.** `configs/eval/*` is consumed by `eval_vllm` (list of
  rows); `configs/{cft,srh,unlearn}/eval/*` by `cft.evaluate` (name → path mapping). A
  generated config used the wrong one and two jobs died in `expand_systems`. Preflight now
  checks the shape against the directory.

All four collisions are the same failure: **an identifier that does not encode what actually
varies.**

## Next steps

- Land the 9-epoch geometry readout and compare against the table above. If sign conflict still
  does not grow, the honest conclusion is that the mechanism does not reach LoRA at r=32 on
  this task — a scale/method boundary worth reporting, since the paper studies full fine-tuning.
- Read out the uniform-epoch merge sweep (running) — the behavioural test, which can move even
  when the geometry does not.
- Explain `merge_ties`' 0.19× shrinkage; decide whether it is a broken arm like
  `merge_dare_linear` (5.58× — mis-scaled, excluded from the sweep).
- Merge-optimal checkpoint selection (`--objective {accuracy,merge}`): the paper's actual
  recommendation is task-dependent early stopping, and `ckpt_select` already has the machinery.
- Update `docs/REPORT_bidirectional_2026-08-09.md` §6.4 with the forgetting table — the
  "bidirectionality is free" claim needs the out-of-domain qualification.
