### Target Date: 2026-08-11 (the unattended chain had two holes; both are closed and both were tested)

Infrastructure entry, not an experiment. Companion to
[../cft-replication/2026-08-11_codebleu-scoring-hang.md](../cft-replication/2026-08-11_codebleu-scoring-hang.md),
which diagnosed why the four `unlearn/negation_*` cells never finished. This entry covers what
happened when those cells were killed and requeued, and the two autonomy defects that surfaced.

- **Hypotheses / what we're testing:** "Will everything run when I log off?" — treated as a claim
  to be falsified rather than asserted. For each component: what restarts it if it dies, and has
  that path ever actually been exercised?

- **Setup:**
  - Host `csr-94608.utdallas.edu`, commit `469f857`, env `/data/jvl210002/conda_envs/obtune`.
  - **GPUs 2 and 3 were lent to a neighbour at 12:17 local** (`scheduler_policy.allowed_gpus:
    [0, 1]`, `gpu_budget: 2` in `configs/compute.yaml`; now also recorded in CLAUDE.md §1).
    obtune runs on 0–1 for the duration.
  - Diagnosis tools: `py-spy dump` (repeated sampling to distinguish "advancing" from "wedged"),
    `/proc/<pid>/{stat,status,environ,comm}`, `nvidia-smi --query-compute-apps`.

- **Results:**

  **1. A dying job strands its GPU, and nothing recovered from it.**
  After killing the four stale-code eval processes, the requeued jobs would not start. vLLM's
  `VLLM::EngineCore` children had been reparented to init and kept their KV-cache reservations:
  **four dead engines holding 164 GB while seven jobs waited**, all four GPUs at 0 % utilisation.
  The worker correctly refuses a GPU with >2 GB used (it cannot distinguish a live neighbour from
  a corpse), so the queue could never drain. `--sweep-orphans` did not help — it recovers stranded
  *claims*, and the claim had already been returned. It was the GPU that was stuck.

  Added `gpu_alloc.stranded_engines()` / `reap_stranded_engines()`, exposed as
  `worker --reap-stranded-gpus` and called from `ensure_infra` on every loop. It reaps only
  processes that are **ours** *and* **orphaned (ppid 1)** *and* **a vLLM engine** *and* **on a GPU
  with no live claim** — each re-verified at kill time, not trusted from the scan. Six tests pin
  the discriminations, including "never touches another user's process" and "never touches a GPU
  that still has a claim". A latent `NameError` (`Path` unimported) was caught by exercising the
  full path: the dry-run had been short-circuiting on the claim check, so it would have fired only
  when the function was actually needed.

  **2. The one process that heals everything else had nothing healing it.**
  Workers, supervisor, stale claims and stranded GPUs are all recovered by `ensure_infra` — which
  runs *inside* `pipeline.sh`. If the pipeline died overnight the remaining ~53 GPU-h would never
  run and nothing would notice.

  Added `scripts/watchdog.sh` and **tested it against a hard kill**: `kill -9` on the pipeline so
  its EXIT trap would not run (leaving a stale lock, the harder case). The watchdog detected it,
  cleared the stale lock, and restarted it in ~280 s; the pipeline resumed from its `.done` markers
  without redoing work and the four running jobs were untouched. It declines to restart a pipeline
  that exited because it *finished*, and stops after 20 consecutive failures rather than hiding a
  crash loop.

  **3. The supervisor was trying to take the lent cards on every poll.**
  `pipeline.sh` computed the GPU budget and exported it across the exec:
  `budget=$(python -c "...gpu_budget..." 2>/dev/null || echo 4)`. The redirect swallowed an
  ImportError and the fallback **silently reinstated a 4-GPU budget** — precisely what the comment
  directly above it warned against. Observed in the supervisor log:

  ```
  [19:28:06] claiming free GPU(s): 2 3 (budget 4)
    gpu2: lent out (scheduler_policy.allowed_gpus) — skipped
  ```

  Only `launch_workers.sh`'s filter stopped it: one layer of defence doing the work of two.
  Reproduced deterministically — the snippet returns `4` without `PYTHONPATH`, `2` with it.

  Fixed by removing the indirection rather than patching the fallback. `supervise.sh` now reads
  `scheduler_policy.gpu_budget` itself — one reader, one source of truth, nothing to go stale
  across an exec — clamped to `len(allowed_gpus)`, and on a failed read falls back to **1 with a
  loud warning**, not to the largest value. Verified: `=== supervisor start (budget: 2 GPUs ...)`.

  **4. The CodeBLEU parallelisation is confirmed working.** The four requeued jobs launched at
  14:52, after the 07:39 fix, and a watcher captured **179 samples with all four evals at 33
  children** (32 CodeBLEU workers + 1 vLLM engine). The previous run had one GIL-bound thread.

- **Observations:**
  - Killing a job is not free here: `cft.evaluate` has no generation cache, so a requeued eval
    restarts from scratch. Three jobs lost ~2 h each when the cards were withdrawn mid-run. Worth
    weighing before lending or reclaiming a card.
  - Defect 3 is the counterpart of the morning's finding: a *fallback* that fails toward the
    largest value rather than the safest. `|| echo 4` on a shared box is the same error class as
    a bare `except` swallowing a `KeyError`.
  - All six long-lived processes now run with PPID 1 and no controlling TTY; nothing is a child of
    a login shell. Verified rather than assumed.

- **Next steps:**
  - The four workers predate the current `worker.py`. Confirmed benign (their claims carry
    `_owner` stamps, and the reap/sweep run as fresh subprocesses), but they should be restarted
    when next idle to clear the warning.
  - `p3_composites` runs at full scale for the first time unattended. If it fails, the stage logs
    a warning and `p3_mole_train` skips — Part III would silently produce no result rather than a
    wrong one. Check `runs/logs/cpu_p3_composites.log` first.
