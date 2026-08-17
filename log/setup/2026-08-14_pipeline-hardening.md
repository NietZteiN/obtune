### Target Date: 2026-08-14 (Pipeline hardening — debugging the 2026-08-14 programme for unattended running)

- **Hypotheses / what we're testing:** Not an experiment. An audit of the eight stages added
  earlier today ([`../modularity/2026-08-14_ood-programme-and-continuous-pipeline.md`](../modularity/2026-08-14_ood-programme-and-continuous-pipeline.md))
  against one question: **if this runs for 16 hours with nobody watching, what silently stops it,
  and what silently produces nothing while reporting success?** Each defect below was found by
  asking that of a specific line, and the two load-bearing recovery paths were tested by inducing
  the failure rather than by reading the code.

- **Setup:** No GPU work of its own. Edits to `scripts/pipeline.sh`, `scripts/launch_workers.sh`,
  and `CLAUDE.md` §1's changelog. The pipeline was STOPPED before every edit and restarted after:
  bash reads a script lazily from a file offset, so editing a running `.sh` in place can corrupt
  execution mid-run — and both edits today landed *ahead* of the interpreter's read position,
  which is exactly the case that corrupts. Workers keep their claimed jobs across a pipeline
  restart, so stopping it costs nothing.

- **Results — six defects, and what each would have done overnight:**

  | # | defect | consequence if left |
  |---|---|---|
  | 1 | Every new stage used `gate X \|\| exit 1` | A bad config in ONE stage kills the whole programme. Worse under the watchdog: `exit 1` becomes a restart loop that re-aborts at the same stage until `MAX_RESTARTS`. The eight stages are mutually independent — a Grid A refill has nothing to do with the LOTO folds. Replaced with `gate_or_skip`, which skips the stage, clears its queued jobs, and lets the rest of the night run. |
  | 2 | `l0ctl_merge` and `merge_headroom_build` run INLINE with no timeout | Each loads a 1.5B model in fp32. A wedge (HF cache lock, NFS stall) blocks the pipeline forever, and the watchdog cannot help — the process is alive, just stuck. This is the 2026-08-11 failure verbatim, where two evals hung in vLLM's atexit and a drain loop waited 18 hours. Wrapped in `timeout`, with exit 124 reported as a timeout rather than a generic failure. |
  | 3 | `l0ctl_eval` guarded on the `dare_ties` merge only | If `ties` failed and `dare_ties` succeeded, the eval queues against a missing adapter directory. Now checks both. |
  | 4 | `build_manifest.py`'s exit code discarded in two stages | A failure there queues nothing, `drain` returns instantly, and the stage marks itself **DONE having produced no jobs** — a silent no-op that reads as success. Now checked, with `mark_skipped` recording why. |
  | 5 | `loto_eval` was all-or-nothing on six folds | `validate_systems` checks only that an adapter PATH is declared, not that it exists, so one missing fold takes the whole 54-cell job down inside vLLM's LoRA load — the 2026-08-09 failure verbatim. Guarding on all six avoided that but discarded five good folds to punish one bad one. Now builds a `--systems` list from the folds that exist and logs which are missing. A 5-fold diagonal is still a usable OOD signal; zero folds is not. |
  | 6 | The watchdog had no watcher | `ensure_infra` already resurrects workers and the supervisor, and `watchdog.sh` resurrects the pipeline — but nothing resurrected the watchdog, making it the last unsupervised link. `ensure_infra` now restarts it too, so the two cover each other. Both hold single-instance locks, so a double start is a no-op. |

  **Both recovery paths tested live, not read:**

  * **Watchdog restart.** Killed `pipeline.sh` with `SIGKILL` while 9 stages were pending.
    `11:06:38 watchdog: pipeline is DEAD with 9 stage(s) pending — restart #1`, one poll interval
    after the kill. Recovered automatically.
  * **Duplicate-claim guard.** Restarting the pipeline mid-stage re-queues a job whose identical
    `job_id` is still live in `running/gpu0/`. The guard (`_already_running`) refused the second
    claim while gpu0's owner stayed alive — the exact race that on 2026-08-13 had two processes
    writing one cell directory. This was the fix that had been written, tested, and left inert in
    the long-lived workers; it is now loaded and demonstrably working.
  * **Layered design confirmed as a side effect.** With `pipeline.sh` dead for ~5 minutes, the
    supervisor kept the workers fed and the in-flight Grid A job kept producing cells (26 → 30).
    The pipeline is the planner, not the engine.

  **Verified rather than assumed, before launch:** all 8 merge output paths match what the eval
  configs declare; the seed-42 expert bank is complete (6/6 adapters); testset `S3`/`S4` eval items
  exist (40 rows each); the LOTO reference adapters exist; the `--systems` filter yields exactly
  30 cells for a simulated 2-fold run; `if timeout …; then … elif [ $? -eq 124 ]` distinguishes a
  timeout from a generic failure in both directions. `bash -n` clean on all three scripts.

- **What worked / hypothesis verdict:** Six defects found, all fixed, two recovery paths verified
  live. Four of the six (1, 2, 4, 5) share one signature: **a failure that leaves the pipeline
  reporting success.** That is the class worth hunting in unattended code, and it is not what
  reading for correctness finds — it is what reading for *"how does this lie to me"* finds.

- **Observations:**

  **Three of the six defects were re-runs of failures this project has already had.** #2 is the
  2026-08-11 atexit hang, #5 is the 2026-08-09 `LoRAAdapterNotFoundError`, and the duplicate-claim
  race is 2026-08-13. Each had been fixed *in the component where it happened* and then
  reintroduced in new stage code, because the fix lived in a script rather than in a shared helper
  or a test. `gate_or_skip` and `timeout` are now conventions any future stage can copy, but
  nothing yet *forces* a new stage to use them.

  **`launch_workers.sh` never honoured `gpu_budget`, despite CLAUDE.md §1 asserting it did.** It
  filtered by `allowed_gpus` and then started a worker on every remaining candidate — three
  workers against a two-card budget — and since `ensure_infra` re-runs it every poll, a
  hand-stopped worker came straight back. The first fix was itself wrong in a way worth recording:
  it counted live workers only among the *candidate* GPUs, but a busy worker's GPU is not idle and
  is therefore filtered out of the candidate list, so it saw zero live workers exactly when the
  budget was fully spent. Fixed to count every `workers/*.pid`. Twelve minutes later the borrower
  took GPU 2 for an 11-hour job, which the cap declined to contest. CLAUDE.md's changelog now
  records that the claim was aspirational rather than true.

  **A documented invariant is not an enforced one.** The `gpu_budget` claim sat in CLAUDE.md,
  unchallenged, through at least two incidents that a working cap would have prevented. Worth
  treating documented invariants as hypotheses until something tests them.

- **New questions / new hypotheses:**
  - Should new pipeline stages be *forced* through a helper that supplies `gate_or_skip`, a
    `timeout` and an artifact guard, rather than copied by convention? Every stage added since
    2026-08-09 has re-litigated the same three failure modes.
  - Is there a cheap test that asserts "no stage marks itself done without either queuing a job or
    writing a `.skipped`"? That single invariant would have caught defects 1, 4 and 5.

- **Next Steps:**
  1. A dry-run flag on `launch_workers.sh` so the budget cap can have a regression test that does
     not spawn real workers. Currently untested by anything but hand-verification.
  2. The stage-helper refactor above, if a seventh stage is ever added.
  3. Nothing blocks the run: the programme is live, 9 stages pending, ~15 h estimated.

---

## Addendum — a seventh defect, found by watching rather than by reading (2026-08-14, later)

The six defects above were found by auditing the stage code. This one was found by noticing that
`gridA_refill` had written no cells for 11 minutes, and it is the most expensive of the set.

**Symptom.** GPU 0 held 46 GB at **0 % utilisation** across repeated samples while the eval
process burned 98 % of a core (27:29 CPU of 27:59 elapsed). Cell count frozen at 30/49. The
classic shape of a hang — except the process was not blocked, it was *computing*.

**Diagnosis.** `py-spy dump` on the live pid, which cost nothing and settled it immediately:

```
__init__ (pydantic/main.py:263)
load_pairs (obtune/data.py:146)
pick_demos (obtune/icl/demos.py:60)
_icl_demos (obtune/eval_vllm.py:219)
render_prompts (obtune/eval_vllm.py:269)
```

`eval_vllm._icl_demos` calls `pick_demos` once **per evaluation item**, and every call re-ran
`data.load_pairs(...)`: five JSONL opens plus a pydantic `TrainPair` construction for every row in
the pool. Five source conditions is ~31k train rows, so a Grid A cell of 1,658 items spent
**~51 million model constructions** choosing 1,658 demonstrations, single-threaded, before a
single token was generated.

**Why it hid for a full day.** `cell_meta.elapsed_s` times *generation only* — `render_prompts`
runs before the timer starts. Every Grid B ICL cell therefore reported ~1 s while actually
spending over a minute in demo selection, and the project's own timing data said the ICL arms were
the cheapest thing on the grid. The bug was invisible in exactly the instrument that would have
caught it.

**Fix.** A module-level pool cache in `icl/demos.py` keyed by `(language, source_conditions)`,
plus `clear_demo_pool_cache()` for tests. Measured on the real corpus: **13.7 min → 0.17 s per
Grid A cell, 4857x**. In production the stage went from 0 cells in 11 minutes to 11 cells in 4
minutes, with GPU utilisation rising from 0 % to 97 % — i.e. it became GPU-bound, which is what it
always should have been.

**Determinism was the only thing that mattered here, so it was proved, not argued.** Caching
changes which objects are reused, and a change in demo selection would silently invalidate every
Grid B ICL cell already on disk. Excluding a program removes it wholesale, so
`sorted(all_pids) − excl` is element-for-element identical to the old `sorted(by_prog)` and
`by_prog[pid]` is untouched for survivors. Verified against a verbatim copy of the pre-cache
implementation over 120 `(excluded_pid, k, seed)` triples comparing full demo content — program
id, condition, prompt and completion: **0 mismatches**. Test suite 652 passed.

**Cost avoided.** Ten Grid A ICL cells remained at ~13.7 min each — ~2.3 hours on this stage
alone, with every later stage sitting behind it, and the whole thing looking like a hang rather
than like slow progress.

**What this says about the audit.** `kill_stalled` would never have caught it: that guard uses CPU
time as the discriminator for a wedged process, and this process was pegged at 98 % CPU. A job
that is *busy doing the wrong thing* is invisible to every liveness check in the system. The
detector that worked was a human noticing that GPU utilisation and cell count disagreed with each
other — which argues for a cheap progress-rate check (cells per minute per job, against the
job's own history) rather than another liveness probe.

**Provenance note.** Killing the spinning job left `080_gridArefill__qwen25c-1.5b.json` in
`runs/manifest/failed/`. It is not a failure; `runs/manifest/failed/README.md` now records what
each entry there actually is, because the pipeline's completion summary counts that directory and
would otherwise report two failures that never happened.

**Two more checks, both clean, and one environment finding (2026-08-14, final pass):**

* **ckpt-select honours `adapter_root`.** The LOTO folds write to `runs/adapters_loto/`, and had the
  paired ckpt-select job looked in the default `runs/adapters/` they would never have produced a
  `best/` — 13 GPU-hours of training that `loto_eval` would then skip. `build_manifest.py` passes
  `--adapter-root` explicitly and `run_ckpt_select` uses it. Verified, not assumed.
* **The same-condition merge path executes.** `L0__s17`/`L0__s42` as PEFT adapter names, through
  `base_condition` and the quarantine guard, produced a valid r=32 adapter. This is the only
  genuinely new code path in the L0-merge control and it had never run.
* **The root filesystem is 100 % full** — 70 G used, ~20 M free, and `/tmp` lives on it. The
  pipeline is insulated (workers carry `TMPDIR=/data/jvl210002/tmp_pip`, and `HF_HOME`, `runs/`,
  `results/` are all on `/data`, which has 13 T free), and `merge_adapters` stages its temp
  directory next to the OUTPUT rather than in `/tmp`, so no stage depends on root having space.
  But it is a shared box: the largest consumers are another user's pip temp and torchinductor
  cache. Flagged rather than fixed — clearing another account's files is not ours to do.

