### Target Date: 2026-08-28 (The GPU layer: a CUDA-13 env on a CUDA-12 cluster)

> Second entry for this thread today. `2026-08-28_juno-migration.md` is not edited — its
> "Next Steps" item 1 was "run the GPU smoke gate ... this is the last unverified layer."
> It was unverified for a reason. Entries are append-only (`../../CLAUDE.md` §6).

- **Hypotheses / what we're testing:** **H-gpu — the migrated environment runs on juno's
  GPUs.** CONFIRM if `scripts/smoke_env.py` trains and a vLLM engine starts. REFUTE if
  either fails. Treated as a formality when written; it was not one.

- **Setup:** Jobs submitted through the new `scripts/slurm/submit.py` to `h200`, `h100`,
  `a30` and both MIG partitions simultaneously, on the reasoning that GPU queue latency —
  not GPU time — is the binding constraint here, so the cheapest way to learn anything was
  to race five partitions. A CPU-only `--dry-run` went to `normal`, which was empty.

- **Results:**
  - **The CPU gate passed first and passed cleanly** (`normal`, 1m45s), on the *7B* config:
    truncation **0.064 %** (n=4,683, p95=729, max=3,117), loss mask correct — batch
    (16, 560) with **113 supervised tokens** and every prompt token at −100 (`CLAUDE.md`
    §4.4). Data layer, tokenizer and TRL contract all survived the move.
  - **H-gpu REFUTED, on every GPU node.** `nvidia-smi` reports **driver 550.163.01** on
    both `a30` and `h200`; the lock pins `torch 2.11.0+cu130`, which requires r580+:

    ```
    RuntimeError: The NVIDIA driver on your system is too old (found version 12040).
    ```

    `torch.cuda.is_available()` is **False on every GPU node while `nvidia-smi` works**,
    which is the nastiest shape this failure could take — it reads as a code bug.
  - **Fixed for training.** `envs/obtune-cu129`: the same 222-package lock with
    `torch 2.11.0+cu129` from the PyTorch cu129 index. CUDA 12 minor-version compatibility
    covers r550. Verified on an H200: `cuda available: True`, sm_90, 150 GB,
    **161.7 TFLOP/s** bf16. It also reproduces `verify_migration.py` **identically**
    (−0.66 [−1.89, +0.66] and −3.13 [−4.78, −1.40]), so switching the default env costs
    nothing in reproducibility. `vllm==0.26.0` still installs: `+cu129` is a local version,
    so it satisfies `torch==2.11.0`.
  - **NOT fixed for vLLM.** `vllm._C_stable_libtorch` links `libcudart.so.13`:

    ```
    ImportError: libcudart.so.13: cannot open shared object file
    ```

    Every PyPI `vllm` wheel back to **0.23** declares `cu13` dependencies and none declare
    `cu12`, so this is not a version we can step back from without also stepping back
    `torch`, `transformers` and the entire pinned stack that produced every published
    number. The `rhel9` CUDA repo publishes `cuda-compat` only up to **12-6**, so the
    forward-compatibility route is closed too. `libcudart.so.13` *is* present in the env
    (`nvidia/cu13/lib/`) and a test with it on `LD_LIBRARY_PATH` is queued, but a CUDA 13
    runtime needs an r580 driver regardless of whether the file is found, so a negative is
    expected.
  - **H-feasibility CONFIRMED, and larger than expected.** 7B LoRA SFT on one H200,
    batch 16 × grad-accum 4: **8.64 s/step**, 20 steps in 172.9 s, eval loss 0.5043 /
    token accuracy 0.845 at 0.27 epochs. A full 3-epoch S2 adapter is ~220 optimizer steps
    ≈ **32 minutes**, against `CLAUDE.md` §1's A6000-derived **8–11 hours**. The 7B arm is
    no longer the expensive branch of the plan.

- **What worked / hypothesis verdict:** **H-gpu REFUTED then repaired for training,
  unrepaired for vLLM. H-feasibility SUPPORTED.** The SLURM replacement itself was correct
  on first run — env sourced, `CUDA_VISIBLE_DEVICES` set by the scheduler, `gpu.py`'s SLURM
  branch declining to poll `nvidia-smi`, manifest transitions firing. Every failure today
  was the CUDA build, nothing else.

- **Observations:**
  - **Racing five partitions was the right call and would have been wrong on the old box.**
    The first useful signal came from `normal`, which has no GPU at all. Where GPU-seconds
    are cheap and queue-minutes are expensive, the ordering of gates inverts: run the
    cheapest gate that can falsify the most, wherever it fits.
  - **`nvidia-smi` working is not evidence that CUDA works.** It is the driver's own tool
    and never touches the runtime. Both the sbatch header line and the first probe printed
    a healthy H200 while torch could not open a context. Any future "is the GPU fine?"
    check has to be `torch.cuda.is_available()`, and it is now the first line of
    `gputest.py`.
  - **A lock file pins versions, not ABIs.** `env/lock-obtune.txt` is `uv pip freeze`
    output, which records `torch==2.11.0` and says nothing about `+cu130`. Replaying it
    faithfully on hardware with an older driver produces an environment that is *correct by
    the lock* and *unusable*. `setup_env.sh` now overlays cu129 by default, with
    `OBTUNE_SKIP_CU129=1` for a cluster that has moved to r580.
  - **12-hour walltime requests were costing queue position for 32-minute jobs.** The first
    7B batch was submitted at `-t 12:00:00` on the A6000 estimate; after measuring, the same
    12 jobs went back in at `-t 02:00:00`. Backfill is the whole game on a busy partition,
    and the old feasibility numbers were silently buying us a worse place in line.

- **New questions / new hypotheses:**
  - Is there any vLLM build for CUDA 12 that keeps `transformers 5.14.1` / `trl 1.9.2` /
    `peft 0.20.0`? If not, the choice is between the **HF eval path** (`src/obtune/eval_hf.py`,
    already used for attention and the mole arms — correct, slower) and **asking for an
    r580+ driver**. The latter is the real answer and worth raising with the admins.
  - Does the HF eval path reproduce the vLLM numbers? §12.4 already records a ~4-point
    engine offset between `hf-mole` and vLLM on some cells, so this is **not** a free
    substitution and needs its own calibration cell before any number from it is published.
  - Does the eval nondeterminism band (§8.9, up to 6.1 pts on Grid B `H1`) differ on H200?
    Unmeasurable until an eval engine runs.

- **Next Steps:**
  1. Land the 12-job 7B grid (queued, `t7b_{cond}_s{17,42}`) and the alignment-arm
     validation (`alignval`: cache → dry-run → λ=0 → λ=1 → mismatch).
  2. Resolve the eval engine. Calibrate `eval_hf` against a known vLLM cell before using it
     for anything published.
  3. Re-measure `CLAUDE.md` §1's feasibility table properly once a full 7B run completes.
