### Target Date: 2026-08-28 (Cluster migration to juno — environment rebuilt, data layer verified)

- **Hypotheses / what we're testing:** Setup/infrastructure day, no experiment. One thing is
  nonetheless testable and was pre-registered by [`../../continuation/02_ENVIRONMENT.md`](../../continuation/02_ENVIRONMENT.md) §6:
  **H-migrate — the transfer preserved the result corpus.** CONFIRM if published numbers
  recompute from `results/cells/` to ≤0.02 pts and the H1 quarantine passes all four layers.
  REFUTE if any cell disagrees, in which case nothing downstream can be trusted and the
  transfer must be redone rather than patched.

- **Setup:** New host `juno-l-02` (login), OpenHPC, **SLURM 24.11.5**, 16 cores on the login
  node and **no GPU there at all** — `nvidia-smi` does not exist. GPU capacity is in
  partitions: `h200` (26 nodes × 2 × H200 NVL 141 GB = 52 GPUs), `h100` (3 heterogeneous
  nodes), `a30` (2 × 2), two MIG partitions, and `normal`/`dev` CPU-only. Old host was
  `csr-94608.utdallas.edu`: 4 × A6000 48 GB, no scheduler, shared informally with a borrower
  on the same Unix account.

  Transfer state on arrival: repo + `data/` (448 MB) + `results/` (3.6 GB) + `runs/` (208 GB,
  all ~68 adapters) + `hf_home` (88 GB) all present. `/data/jvl210002` no longer exists.
  Git at `f1a3247` with **165 uncommitted changes and no checkpoint commit** — the step the
  handoff README called step zero was never performed on the old host.

  Work done, in order:
  1. `c72224a` — checkpoint commit of the tree exactly as rsync delivered it, then branch
     `cluster-migration`.
  2. `uv` installed (the env is a uv venv, not conda — the old doc said "conda env"); env
     rebuilt at `/work/jvl210002/migration/envs/obtune` via `env/setup_env.sh`.
  3. 18 hardcoded `/data/jvl210002` references across 9 files repointed; the three roots
     (`OBTUNE_ROOT`, `OBTUNE_ENV`, `OBTUNE_SCRATCH`) now live once in `scripts/env.sh` and
     everything else derives from them.
  4. `configs/compute.yaml` rewritten for juno + SLURM; old `scheduler_policy` retained inert
     as `legacy_scheduler_policy` so its reasoning is not lost.
  5. `src/obtune/gpu.py` given a SLURM branch; `scripts/slurm/submit.py` written to replace
     `src/obtune/sched/`.
  6. `scripts/verify_migration.py` written — the §6 acceptance test, codified.

- **Results:**
  - **Env reproduces the old cluster exactly.** All five pins identical: torch 2.11.0+cu130,
    transformers 5.14.1, trl 1.9.2, peft 0.20.0, vllm 0.26.0. But rebuilding from the
    top-level spec moved **42 transitive packages** (huggingface-hub 1.26→1.29, scipy
    1.18.0→1.18.1, pyarrow, pydantic, starlette, tiktoken…). Reinstalled from
    `env/lock-obtune.txt` instead: now byte-identical to the old env on 222 packages, one
    stray extra (`agent-detector`).
  - **Quarantine intact.** `make check`: manifest verify OK; train corpus **67 files,
    207,136 rows, no H1 labels, no H1 markers, splits disjoint**. `tests/test_quarantine_lint.py`
    5 passed. `scripts/preflight.py`: **0 errors, 17 warnings**, all pre-existing (§12.1
    cell-path grid collisions, 7B adapters absent) and none migration-induced.
  - **H-migrate CONFIRMED, exactly.** Grid A `H1`, n=1214, 405 programs, paired cluster
    bootstrap by `program_id`, 2000 resamples, seed 17:

    | contrast | recomputed | published |
    |---|---|---|
    | `merge_dare_ties` − `tuned_L0` | **−0.66 [−1.89, +0.66]** | −0.66 [−1.89, +0.66] |
    | `l0merge_dare_ties` − `tuned_L0` | **−3.13 [−4.78, −1.40]** | −3.13 [−4.78, −1.40] |

    Point accuracies likewise: `tuned_L0` 24.55, `merge_dare_ties` 23.89,
    `l0merge_dare_ties` 21.42. Not to 0.02 pts — to the digit, CI bounds included.
  - **`runs/manifest/queued` and `running/` are both empty.** The old cluster's queue drained
    before the move; there are no stranded claims to requeue.
  - **No GPU work ran.** `h200` was 41 running / 35 pending and estimated a **7-hour** start
    for a 5-minute `nvidia-smi` job; an `a30` probe was still pending at end of session.

- **What worked / hypothesis verdict:** **H-migrate SUPPORTED.** The irreplaceable part of the
  project — the cell tree, the quarantined corpus, the adapters — survived intact and is
  verified rather than assumed. The environment is a bit-for-bit rebuild, not an approximation.

- **Observations:**
  - **The single most useful thing done today was pinning the env to the committed lock.**
    A fresh resolve reproduced every version anyone would have checked and still moved scipy,
    which is in the bootstrap path for every published CI. Had the acceptance test been run
    against the drifted env, a disagreement would have been ambiguous between a bad transfer
    and a dependency bump — and an agreement would have been luck. `setup_env.sh` now replays
    the lock by default and only re-resolves under `--upgrade`.
  - **Queue waits are the new planning constraint, and they invert the old workflow.** On
    csr-94608 a free card was taken in seconds and the whole `sched/` apparatus existed to
    arbitrate that. Here a GPU-second costs hours of latency. Phase 0's "~1 GPU-hour" is now
    ~1 GPU-hour plus an unknown queue wait, and interactive debugging on a GPU is no longer
    a thing that can be done casually.
  - **`gpu.pin()` under SLURM is a silent-corruption hazard, not a no-op nicety.** On a 2-GPU
    node with `--gres=gpu:1`, SLURM may allocate physical device 1 and present it as local
    index 0. Code that then sets `CUDA_VISIBLE_DEVICES=0` from an absolute index selects the
    wrong device or none — and it does not raise. This is why `pin()` now refuses to write
    inside an allocation instead of merely being skipped at the call sites.
  - **Three gaps the handoff doc predicted, now confirmed real.** (a) `node` is not installed,
    so the H1 generator and all JavaScript work are blocked despite `js/node_modules` having
    transferred; this also blocks Phase 1's `H2`/`H3` JS generators. (b) The `r_analysis`
    conda env did not transfer, blocking `stats/`. (c) Three cross-project stimulus files
    (`full_human_experiment_v2.json`, `tasks_unified_50.json`, `humaneval_x_js_full.json`)
    did not come across; `data/` is intact so nothing is blocked *now*, but the corpus cannot
    be rebuilt and `make testset` will fail.
  - The old `CLAUDE.md` §1 opened with "**This project does NOT use SLURM**". Left alone it
    would have actively misled every future session, which is why §1/§2 were rewritten today
    rather than filed as an owed correction.

- **New questions / new hypotheses:**
  - **H-feasibility:** LoRA SFT timings are all A6000-derived. On H200 (141 GB, ~3–4× the
    throughput) both the 2–3 h/adapter figure at 1.5B and the 8–11 h at 7B should fall
    substantially, and 7B may stop being the expensive branch of the plan. If so the
    Phase 0 → Phase 1 → Phase 2 → "then 7B" ordering in
    [`../../continuation/01_NEXT_STEPS.md`](../../continuation/01_NEXT_STEPS.md), which was
    budget-driven, is worth revisiting with the PI — the instrument-before-experiment
    *rationale* still holds, but the cost argument behind the ordering may not.
  - Does vLLM 0.26.0 + torch 2.11.0+cu130 work on sm_90 without a rebuild? Expected yes;
    unverified until a GPU job runs.
  - Does eval nondeterminism (§8.9: up to 6.1 pts on Grid B `H1`) behave differently on H200
    than on A6000? The band was measured on one card type and the mechanism is batching.

- **Next Steps:**
  1. **Run the GPU smoke gate** — `scripts/smoke_env.py` via `scripts/slurm/submit.py`,
     confirming an adapter loads and vLLM starts on sm_90. This is the last unverified layer.
  2. Re-measure the feasibility numbers on H200 and update `CLAUDE.md` §1.
  3. Install a `node` toolchain — blocks the H1 generator and all of Phase 1's JS work.
  4. Rebuild the R analysis env for `stats/`.
  5. Recover the three missing stimulus files from the old cluster while it is still reachable.
  6. Then **Phase 0** ([`../../continuation/01_NEXT_STEPS.md`](../../continuation/01_NEXT_STEPS.md)):
     the norm-matched merge rescaled to 1.0× a single expert, one Grid A `H1` eval, predicted null.
