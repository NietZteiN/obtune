# Source before any obtune command:  source scripts/env.sh
#
# Putting the env's bin/ on PATH is not optional. vLLM shells out to the `ninja`
# BINARY when it builds its kernels, so invoking the interpreter by absolute path
# (the natural thing on a box with many conda envs) makes engine startup die with
# a bare `FileNotFoundError: 'ninja'` whose real cause is buried in a child
# process — it surfaces as "Engine core initialization failed" with no root cause.

# --- Cluster-specific roots: the single source of truth ------------------------
# Every other tracked file derives its paths from these three. Override them in
# the environment to relocate the project without editing anything tracked; that
# is what made the csr-94608 -> juno move a four-line change instead of an
# 18-site sed. OBTUNE_SCRATCH holds everything that must NOT live in the repo or
# in $HOME: model cache, temp, compiler caches.
export OBTUNE_ROOT="${OBTUNE_ROOT:-/work/jvl210002/migration/obtune}"
# NOTE THE SUFFIX. The plain `envs/obtune` build follows the committed lock exactly and
# is unusable on this cluster's GPUs: the lock pins torch 2.11.0+cu130 and juno runs
# driver 550.163.01 (CUDA 12.4), so torch.cuda.is_available() is False on every GPU node
# while nvidia-smi works fine. `envs/obtune-cu129` is the same package set with
# torch 2.11.0+cu129, which CUDA 12 minor-version compatibility covers on r550, and it
# reproduces the published numbers identically (scripts/verify_migration.py).
export OBTUNE_ENV="${OBTUNE_ENV:-/work/jvl210002/migration/envs/obtune-cu129}"
export OBTUNE_SCRATCH="${OBTUNE_SCRATCH:-/work/jvl210002/migration}"

export PATH="$OBTUNE_ENV/bin:$PATH"
export PYTHONPATH="$OBTUNE_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Keep caches and temp off $HOME (monorepo CLAUDE.md §2). On juno both /home and
# /work are the same MooseFS cluster, but compute nodes contend on $HOME.
#
# HF_HOME MOVED TO /scratch ON 2026-09-10, for two independent reasons:
#   * OWNERSHIP. The old location ($OBTUNE_SCRATCH/hf_home, on /work) is a cache SHARED by every
#     project on this account. On 2026-09-10 another project deleted CodeLlama-13B and 34B from
#     it -- 87 GB the paper's scale legs depend on -- to make room for its own datasets. A cache
#     obtune owns cannot be reclaimed by a neighbour.
#   * SPACE. /work carries a 1.1 TB per-user quota shared across projects and was exhausted twice
#     in 24 hours; /scratch/juno/$USER is a separate 30 TB quota (8 KB used before this move).
# It is also faster: measured on a compute node, /scratch reads at 14,186 MB/s against /work's
# 1,289 MB/s (11x) and writes at 1.49x -- WekaFS with 32 MB readahead vs MooseFS.
#
# CAVEAT, and the reason this holds only models and datasets: /scratch/juno carries a purge
# policy whose terms are unconfirmed (a `purge_scratch_test` directory sits beside the user
# directories). Everything here is RE-DOWNLOADABLE from the hub, so a purge costs time and
# nothing else. Adapters and results stay on /work, which is backed by the quota we pay for.
# Override by exporting HF_HOME before sourcing this file; the /work copy is left in place.
# NB: the hub TOKEN lives at $HF_HOME/token, so it must travel with the cache. Moving HF_HOME
# without it breaks every gated repo (gemma-3, codegemma, both Llamas) with a 401 GatedRepoError
# at the first hub call -- even when the weights are already present locally.
export OBTUNE_HF_STORE="${OBTUNE_HF_STORE:-/scratch/juno/$USER/hf_home}"
export HF_HOME="${HF_HOME:-$OBTUNE_HF_STORE}"
export TMPDIR="${TMPDIR:-$OBTUNE_SCRATCH/tmp}"
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-$OBTUNE_SCRATCH/cache/inductor}"
export TRITON_CACHE_DIR="${TRITON_CACHE_DIR:-$OBTUNE_SCRATCH/cache/triton}"

# Quieter vLLM startup; the engine's real errors still reach stderr.
export VLLM_LOGGING_LEVEL="${VLLM_LOGGING_LEVEL:-WARNING}"
# vLLM's engine core is spawned, not forked. Added 2026-09-10 after two checkpoint-select jobs
# died 28 minutes in on the h100 partition's MIG node (g-06-01, 4 x nvidia_h100_nvl_3g.47gb)
# with `RuntimeError: Cannot re-initialize CUDA in forked subprocess`. h200 never showed it --
# the difference is several jobs sharing one physical card through MIG slices, where a CUDA
# context already exists when the engine forks. `spawn` is the documented remedy and costs a
# few seconds of start-up on the partitions that were fine anyway.
export VLLM_WORKER_MULTIPROC_METHOD="${VLLM_WORKER_MULTIPROC_METHOD:-spawn}"

# Share of the juno QOS POOL obtune may hold. The account is shared with another project and the
# juno QOS allows 4 running jobs per user, so holding all four squeezes them out entirely.
# THE POOL IS NOT ONE PARTITION: `h200` and `normal` are both QoS=juno, so a CPU analysis blocks a
# GPU training job and moving work to `normal` frees nothing (corrected 2026-09-11). `dev` is
# QoS=juno-dev, a separate pool. The authority is configs/compute.yaml::share_limits; this
# variable is legacy and inert for submission (see the note there).
# scripts/slurm/submit.py REFUSES an h200 submission above this, rather than relying on whoever
# is submitting to count first — which failed within an hour of the share being agreed.
# h100 and a30 carry no QOS (`scontrol show partition`), so work there is unaffected.
# Set to 0 to disable.
export OBTUNE_H200_SHARE="${OBTUNE_H200_SHARE:-2}"
export TOKENIZERS_PARALLELISM=false

# flashinfer JIT-compiles its sampling kernel on first use and needs nvcc/CUDA_HOME. juno's
# compute nodes have neither ("Could not find nvcc and default cuda_home='/usr/local/cuda'
# doesn't exist", job 359038), so the vLLM engine dies during startup -- AFTER reporting a
# healthy GPU, which makes it read as an environment failure rather than a missing compiler.
# vLLM's native sampler needs no compiler and every eval here is greedy (temperature=0), so
# nothing is given up. With this set, the engine starts and generates on an A30 (job 359040).
# Do NOT "fix" this by pointing CUDA_HOME at the env's nvidia/cuda_nvcc: that is a CUDA 13
# toolkit against a 12.4 driver, the same mismatch that made this environment unusable once.
export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}"
