### Target Date: 2026-09-11 (CORRECTION: g-06-01 runs training and does NOT run vLLM — `spawn` fixed the symptom that was reported, not the one that matters)
- **Corrects** [`2026-09-11_mig-node-usable-for-vllm.md`](2026-09-11_mig-node-usable-for-vllm.md),
  written four hours earlier, which concluded the node was usable for 6 h evals. Per CLAUDE.md §6
  that entry stands unaltered; this one is the record.
- **What that entry got right, and it still stands.** Training never needed the exclusion —
  `tr_llama31-8b_X1` ran there to completion at 22 s/it (3 epochs, train_loss 0.758) on a node
  nothing else could reach. And `VLLM_WORKER_MULTIPROC_METHOD=spawn` **did** fix
  `Engine core initialization failed`: three checkpoint-selects died in `wait_for_engine_startup`
  at 27–39 min before the change, and after it the engine constructs — weights load in 2.3 s and
  the per-cell telemetry line prints.
- **What it got wrong.** "The engine started" was treated as evidence the node works. It is not.
  With the engine up, **`generate()` never returns.** Two evals ran 35 minutes and produced
  **nothing**:

  | instrument | reading |
  |---|---|
  | cells written | **0** of 54 and 0 of 35 |
  | CPU consumed (`sstat`) | **19 s** across 35 min of walltime |
  | node load | **0.51** on 64 cores with four GPU jobs allocated |
  | files written anywhere on disk in 40 min | **0** (inductor cache, vLLM cache, `$TMPDIR`, `results/`, `runs/`) |

  Hung, not slow. And the job history settles it: **every non-vLLM job on g-06-01 has COMPLETED**
  (three neighbour jobs plus our training) and **every vLLM job has failed, hung or been
  cancelled** — six of them now.
- **The reasoning error worth naming.** The first entry reasoned forward from a mechanism: the
  documented fix for the documented error was applied, the documented error stopped appearing, so
  the node was declared usable. It did not ask the cheaper question the scheduler could answer
  directly — *has a vLLM job ever succeeded here?* One `sacct` query over the node's history would
  have said no in three seconds, before three evals and a checkpoint-select spent 35 minutes each.
  A fix that removes an error message is not a fix that produces a result.
- **Cost: 35 minutes of four MIG slices, and nothing else.** Not one cell was written, so nothing
  was lost and nothing partial has to be distinguished from complete. Evaluation resumes at cell
  granularity, so had any cell landed it would simply have been kept.
- **Fix, narrower than the original exclusion.** `scripts/slurm/submit.py` now auto-excludes
  g-06-01 for any `h100` submission whose argv contains `obtune.eval_vllm`, and for nothing else.
  Training keeps a node it demonstrably uses; an explicit `--nodelist`/`--exclude` still wins, so
  the decision can be revisited after a driver upgrade without editing the file. Verified: training
  submissions get no exclusion, `h200` is untouched, an explicit nodelist overrides.
- **Chains rebuilt.** Cancelling the checkpoint-select left two jobs in
  `DependencyNeverSatisfied`; the llama31-8b and codellama-7b chains and the F2 eval were
  resubmitted off the node, and the three panel analyses re-chained onto the new job ids so the
  eight-model tally still waits for all four incumbent evals rather than firing on a cancellation.
- **Open, and honestly unresolved:** why `generate()` hangs on a MIG slice when the engine
  initialises fine. Not worth chasing — the node is 5× slower for training anyway and the cluster
  driver (r550 against vLLM's CUDA 13 wheels) is the standing suspect for the whole family of
  vLLM problems here.
- **Next Steps:** none. The evals queue behind real cards, which is the honest state.
