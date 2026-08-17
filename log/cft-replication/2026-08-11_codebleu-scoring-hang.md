### Target Date: 2026-08-11 (CodeBLEU scoring hang — the unlearning cells never reached their verdict)

Second entry for this thread today; the first is
[2026-08-11_attrib-chain-and-zero-gpu-repairs.md](2026-08-11_attrib-chain-and-zero-gpu-repairs.md),
which is a separate incident (merge/prompt bugs, ATTRIB chain). This one is the scoring-stage hang
that killed the `srh/exp3-unlearning` eval cells twice.

- **Hypotheses / what we're testing:** Not an experiment — an incident. The question was
  diagnostic: **why do the four `unlearn/negation_*` eval cells never finish?** Two competing
  explanations, with different fixes:
  - **D1 (execution):** the sandboxed exec-equivalence stage is stuck — a generated program loops
    and `exec.pool` fails to enforce `timeout_s: 2.0`. CONFIRM if the pegged processes are the
    `python -I -S runner.py` children; REFUTE if they are not.
  - **D2 (scoring):** the CodeBLEU stage is stuck. CONFIRM if the pegged processes are
    `ProcessPoolExecutor` workers inside `codebleu/parser/DFG.py`.

- **Setup:**
  - Host `csr-94608.utdallas.edu`, GPUs 0–3, commit `469f857` (working tree dirty — this entry's
    change is uncommitted at time of writing). Env `/data/jvl210002/conda_envs/obtune`.
  - Affected cells, all four running concurrently, one per GPU, priority 57, `est_gpu_h` 1.5:
    `evalunlearn_{rev,mix50}msft__qwen25c-{1.5b,7b}_python`
    (configs `configs/unlearn/negation_{rev,mix50}_minus_sft_qwen25c-{1.5b,7b}_python.yaml`,
    each extending [`../../configs/cft/eval/bidir_v1.yaml`](../../configs/cft/eval/bidir_v1.yaml),
    seed 17, 300 programs x 12 systems = 36 000 generations per cell).
  - Diagnosis: `py-spy dump --pid <worker>` on a pegged process; `ps`/`top` for CPU-time
    accumulation; `runs/manifest/{running,failed}/*.json` for the prior attempt's verdict.
  - Guard validated before relaunch with two throwaway scripts (scratchpad, not committed):
    a determinism/leak check and a blow-up search over four degenerate code shapes.

- **Results:**
  - **Attempt 1** (claimed 11:26 UTC): all four cells `returncode: -15` after 11 950–12 162 s
    (~3.3 h each), `finished_utc` identical to the microsecond across all four
    (`2026-08-11T14:49:19.7879xx`) — one external group-kill, not four independent failures. The
    pipeline manager logged normally at 14:48:48 and restarted cold at 14:57:25; the tmux server
    for this uid is gone. Generation had completed 36000/36000 before the kill.
  - **Attempt 2** (claimed 14:52 UTC): generation finished in 19 min (1.5B) / 45 min (7B). The
    jobs then sat in the scoring stage for a further 1 h 15 m – 1 h 40 m with all four GPUs
    holding ~41 GB of resident vLLM engine at **0 % util**. Nine pool workers pegged at ~100 %
    CPU with **71–102 minutes of accumulated CPU time each**; load average 10 on 96 cores.
  - `py-spy` on pid 323671 (a child of the 1.5B mix50 cell): `tree_to_variable_index`
    (`codebleu/parser/utils.py:85`) under ~30 recursive frames of `DFG_python`
    (`codebleu/parser/DFG.py:100/152/186`). **D2 CONFIRMED, D1 REFUTED** — the pegged processes
    are `ProcessPoolExecutor` workers (RES 1.5 GB, forked from the evaluate process), not the
    512 MB sandboxed runners, and `exec.pool`'s timeout was never implicated.
  - Blow-up reproduced synthetically. `codebleu_score` against a 20-deep nested-`for` prediction
    does not return; three other shapes (nested `if`, chained assignment, deep parenthesised
    expression) complete in ≤0.03 s at every depth tried up to 160. So the trigger is **nesting
    depth of compound statements**, not length.

    | shape | n=20 | n=40 | n=80 | n=160 |
    |---|---|---|---|---|
    | `nested_for` | **hangs** | — | — | — |
    | `nested_if` | 0.01 s | 0.01 s | 0.02 s | (size-capped) |
    | `chained_assign` | 0.00 s | 0.01 s | 0.01 s | 0.03 s |
    | `deep_expr` | 0.00 s | 0.00 s | 0.00 s | 0.01 s |

  - Baseline for the same cell shape (300 x 12): `evalunlearn__qwen25c-1.5b_python` **80 min**
    and `evalunlearn__qwen25c-7b_python` **54 min**, both `returncode: 0`, on 2026-08-10.

- **What worked / hypothesis verdict:**
  - The fix is a hard bound in [`../../src/obtune/cft/metrics.py`](../../src/obtune/cft/metrics.py):
    `_CODEBLEU_TIMEOUT_S = 20.0` enforced with `SIGALRM` inside `codebleu_score`, plus a
    `_CODEBLEU_MAX_CHARS = 50_000` pre-filter. `_CodeBleuTimeout` derives from **`BaseException`
    on purpose** — codebleu's own `except Exception` handlers would otherwise swallow the alarm
    and resume the recursion. Verified: the alarm interrupts a real `DFG_python` blow-up at
    exactly 20.00 s, survives an intervening `except Exception`, and does not leak (the call after
    a timeout returns the byte-identical dict to the call before it).
  - The bound cannot move a published number. It is ~450x the mean call (72 000 calls in 52 min
    = 43 ms, measured in this morning's profile), so nothing that would have completed is
    truncated; and a prediction that defeats the dataflow extractor scores ~0 in every component
    when it does finish.
  - `chunksize` 64 -> 4 in `_codebleu_batch` ([`../../src/obtune/cft/evaluate.py`](../../src/obtune/cft/evaluate.py)):
    at 64, one pathological prediction held 63 ordinary ones behind it.
  - Timeouts are **reported, not swallowed**: `codebleu_score` always returns a `timeout`
    component, the trial row carries `codebleu_timeout` (OR of the target and `other` calls —
    only the target's components are spread into the row, so `other`'s bound would otherwise be
    invisible), and `codebleu_timeout` is in `AGG_FIELDS` so it reaches the cell means. A bounded
    metric that hides how often it hit the bound is a silent cap (CLAUDE.md §4).
  - `tests/test_codebleu_batch.py` (6 tests) and the 47-test `metric|codebleu|eval|quarantine`
    subset pass unchanged — the parallel-equals-serial guarantee still holds with the guard in.

- **Observations:**
  - **This morning's parallelisation did not cause the hang, but it did hide it.** Before it, the
    same recursion showed as one core busy for 52 min and 95 idle — slow, but it finished. Spread
    across 32 workers, several pathological predictions run *concurrently*, so the stage's
    duration became the worst single call rather than the sum, and the worst single call does not
    terminate. Parallelising an unbounded operation converts a slow tail into a hang.
  - The likely source of the degenerate predictions is the **high-λ arms** (`u_lam1p25`,
    `u_lam1p5`): task-vector negation past λ=1 produces repetitive, deeply-nested output. The
    published 08-10 cells (which lack those arms) completed in 54–80 min. Worth confirming from
    `codebleu_timeout` once these cells land — if the flag concentrates on the high-λ systems,
    that is a *finding about over-negation*, not just a harness note.
  - **Nothing catches a hang.** The job has no wall-clock budget: `est_gpu_h: 1.5` is scheduling
    metadata that nothing enforces, and both attempts ran to 3.3 h+ without complaint. The
    watchdog only restarts a dead pipeline, not a wedged job. Attempt 1 was ended by an unrelated
    external kill, which is the only reason we learned anything at all.
  - **SIGTERM to the evaluate parent orphans its children.** Killing the four parents left 128
    `ProcessPoolExecutor` workers and 4 `VLLM::EngineCore` processes reparented to init, still
    pegged and still holding 41 GB of GPU memory each. They had to be reaped separately (the
    interlock used was `ppid == 1`, so a cell a worker had already relaunched could not be hit).
    `worker.py --reap-stranded-gpus` exists for the vLLM half but not for the pool workers.

- **New questions / new hypotheses:**
  - **H-U1:** does `codebleu_timeout` concentrate on `u_lam1p25`/`u_lam1p5`? CONFIRM if the flag
    rate on those systems exceeds the `base`/`rev`/`flip`/`sft` rate by an order of magnitude;
    REFUTE if it is flat across systems (which would make it a corpus property, not an
    over-negation signature).
  - Should the scheduler enforce a wall-clock ceiling per job (say 3x `est_gpu_h`) and mark the
    cell failed with a reason, rather than relying on an operator noticing four idle GPUs?

- **Next Steps:**
  - Four cells requeued at 12:0x local and picked up; gpu0 claimed
    `evalunlearn_mix50msft__qwen25c-1.5b_python` first. Check on landing: (a) the run completes
    in the 54–80 min baseline band, (b) `codebleu_timeout` per system, (c) `base` strict reads
    **2.7 %** for these cells (the unlearning-run anchor from the sibling entry — *not* the 2.9 %
    published anchor; these numbers do not go beside the published tables).
  - Three ATTRIB cells (`e2_seeds`, `e3_dose`, `e7_strategies`) claimed gpu1–3 in the same window
    and are unaffected by this incident, but they run the patched scorer too.
  - Commit the guard with this entry.

---

#### Addendum, same day — obtune cut to two GPUs (2 and 3 lent out)

Not part of the incident above; recorded here because it changes the throughput every estimate
in this entry assumes.

- **What changed.** GPUs **2 and 3 released to a neighbour for the duration**; obtune now runs on
  **0–1 only**. Chose the NVLink pair 2↔3 rather than any two cards so the borrower can still run
  TP=2 — lending 1 and 2 would have left them cross-pair PCIe/SYS
  ([`../../configs/compute.yaml`](../../configs/compute.yaml) `nvlink_pairs`).
- **Why a config change and not just killing two workers.** `supervise.sh` holds a GPU *budget*
  and "follows whatever is free" rather than being pinned to indices, so a card released by
  stopping its worker is reclaimed on the next 300 s poll. Worse, `pipeline.sh::ensure_infra`
  restarted the supervisor with a hardcoded `MAX_GPUS=4` on every poll, so even lowering the
  budget by hand would have been undone within minutes. Three changes make the loan hold:
  - `scheduler_policy.allowed_gpus: [0, 1]` + `gpu_budget: 2` in `configs/compute.yaml` — one
    version-controlled place, per CLAUDE.md §5.
  - `gpu_alloc.free()` filters by it (so `claim()` inherits it); `ours()` deliberately does NOT,
    because a card we are on is ours whether or not policy says we should have taken it, and both
    the budget arithmetic and stranded-engine reaping depend on still seeing it.
  - `launch_workers.sh` filters the **explicit** list as well as the auto-detected one — it is the
    only place a worker is ever spawned, so filtering there covers the supervisor, the pipeline,
    `run_mono_gate.sh` and a human typing `launch_workers.sh 0 1 2 3` alike.
  - `pipeline.sh` now reads the budget from the config instead of hardcoding 4.
- **Verified**, not assumed: with GPUs 2–3 idle and no worker holding them, both
  `launch_workers.sh 2 3` and the bare auto-detect form refuse (`gpu2: lent out … — skipped`);
  and against a simulated survey where 2 and 3 are free, `free()` and `claim(4)` both return `[]`
  — including the case where a neighbour has taken gpu0, which is the one that would otherwise
  tempt the supervisor to hop onto a lent card.
- **The cost, stated plainly.** A hard pin means obtune will NOT hop to 2 or 3 if a neighbour
  takes 0 or 1 — it will run on one card, or none, and wait. That is the intended meaning of
  lending the pair "for the whole thing", but it is a real throughput risk if the neighbour also
  lands on 0/1.
- **Displaced work.** `e2_seeds` and `e3_dose` (both 1.5B, ~15 min in) were stopped and requeued
  via `worker --sweep-orphans`; nothing was lost but their generation time. The 7B
  `e7_strategies` on gpu1 and the unlearning cell on gpu0 were deliberately left running — the 7B
  cell has a 45-minute generation phase and was the most expensive thing to restart.
- **Queue now 5 deep on 2 cards**: 3 unlearning cells + the 2 displaced ATTRIB cells. At the
  54–80 min baseline that is roughly 2–3 h of serialised work rather than ~1 h.
- Stopping the workers again confirmed this morning's finding: SIGTERM to a worker/job orphans
  its pool children and vLLM engine, so the reap step is mandatory, not optional.

---

#### Addendum 2, same day — the `cft` arm nobody declared, and a third hang mode

Uncovered *because* of the CodeBLEU fix: with scoring no longer wedged, the gpu0 cell reached the
§4.2 adapter check and died there. The failure is unrelated to CodeBLEU and older than it.

- **What the run said.** `RuntimeError: system 'cft' produced output identical to the base model on
  all 3000 trials`. There is no `cft` system in `configs/unlearn/negation_mix50_minus_sft_qwen25c-1.5b_python.yaml`.

- **Cause.** `load_config`'s `_deep_merge` recurses into dicts, and `systems:` is a dict, so a
  child's block UNIONS with its parent's instead of replacing it. The parent
  `cft/eval/bidir_v1.yaml` declares `base`/`sft`/`cft`, so **every** `unlearn/negation_*` config
  silently gained a `cft` arm. Resolved vs declared, before the fix:

  | config | declared | resolved |
  |---|---|---|
  | `unlearn/negation_*` (all six) | 11 | 12 (+`cft`) |
  | `srh/eval/e7_strategies_qwen7b` | 2 | 6 (+`base`,`sft`,`cft`,`rev`) |
  | `srh/eval/e2_budget_qwen7b` | 2 | 7 |
  | `srh/eval/e1_qwen1.5b`, `e1_qwen1.5b_s42`, `e2_factorial`, `e3_dose` | 3–4 | +`base`,`sft`,`cft` |

- **This is the root cause of the bug already recorded in `MASTER_REPORT_2026-08-11.md` §10** as
  "`cft` arm in three 7B unlearning configs pointed at the 1.5B adapter". That entry has the
  symptom, not the cause, and understates the scope three ways, all now corrected in the report:
  1. It is not a wrong *path*, it is an injected *arm*. The path being 1.5B at 7B was a consequence.
  2. **The 1.5B runs are affected too.** There the inherited path was a valid 1.5B adapter, so
     nothing looked wrong and no guard fired — but
     `results/2026-08-10_.../qwen25c-1.5b/python/unlearn_negation_python/report.md` carries a `cft`
     row at 8.6 % reverse, in an experiment whose config does not contain the word. Every
     unlearning table with a `cft` row is wrong at BOTH scales, and ~1/12 of every unlearning
     cell's GPU time went to it.
  3. The recorded fix — overriding `cft:` in the 7B configs — was applied **by hand to files headed
     "Generated by … do not hand-edit"**, and the generator did not emit it. The next regeneration
     would have restored the bug silently. `check_cross_model_adapters()` would not have caught the
     1.5B case either: right model, spurious arm.

- **Fix.** `_replace: [<keys>]` in a child config declares those top-level blocks exhaustive
  ([`../../src/obtune/config.py`](../../src/obtune/config.py)); `_replace` without `_extends` is an
  error rather than a silent no-op. Merge stays the **default**, deliberately: the SRH eval configs
  declare only their new arms and rely on inheriting `base`/`sft`/`cft` as references, and their
  published tables contain those arms — flipping the default would silently drop arms from every
  one of them. `20_negation_sweep.py` now emits `_replace: [systems]`, all four current-naming
  configs were regenerated with it, and the two legacy-named ones (the generator's filename scheme
  changed, so it no longer writes them) were edited by hand with that fact recorded in-file.
  [`../../tests/test_config_extends.py`](../../tests/test_config_extends.py) asserts no unlearning
  config resolves to an arm it does not declare, and that none carries `cft`.
  **Verified live**: the relaunched cell logs `300 programs x 11 systems -> 33000 generations`,
  down from 12 / 36000.

- **A third hang mode.** After raising the RuntimeError the process did not exit: `py-spy` put it in
  `multiprocessing/util.py::_exit_function -> join()`, blocked on a vLLM child that never returns.
  It sat there 1 h 20 m holding 41 GB on gpu0 while its worker blocked in `subprocess.run`. So the
  day produced three distinct hangs in one pipeline — scoring (CodeBLEU), teardown (vLLM atexit),
  and the worker waiting on both — none of which any timeout would have caught.

- **Review finding #1 fixed** (`worker.py`), which this incident demonstrated live:
  jobs now start with `start_new_session=True` and a worker stopped by SIGTERM/SIGINT raises
  `SystemExit`, terminates the job's whole process **group** (SIGTERM, then SIGKILL after a bounded
  grace), and returns its claim to `queued/` itself. Previously the job survived its worker,
  `is_orphaned` (which tests the *worker's* pid) requeued the claim anyway, and a second copy of a
  still-running job could start on another card — the path `supervise.sh` takes on every neighbour
  takeover. `run_job` also opens the log with `"a"` now: keyed on `job_id`, `"w"` meant every retry
  destroyed the failed attempt's log. Guarded by
  [`../../tests/test_worker_teardown.py`](../../tests/test_worker_teardown.py), which spawns a real
  grandchild and asserts it dies. Full suite: 465 passing.

- **Not yet done.** The teardown fix is inert in the two live workers (started 2026-08-10; the
  pipeline warns about this every poll) — they must be restarted **between jobs**, because
  SIGTERMing a worker running the OLD code is precisely what orphans a job tree. gpu1 is mid-run on
  the 7B strategies cell; restart both at its next boundary. Review findings 3–5 (the `attrib_evals`
  stage marking itself complete when it enqueued nothing; "enqueue failed" being indistinguishable
  from "already enqueued"; `drain` having no deadlock detection) are untouched.

- **Next.** When the four unlearning cells land: `codebleu_timeout` by system (H-U1), the 54–80 min
  baseline band, `base` strict at 2.7 %, and that no `cft` row appears anywhere in the new reports.
  The old `cft` rows in the 2026-08-10 unlearning results remain on disk and still need regenerating
  or deleting — deletion needs sign-off per CLAUDE.md §2.
