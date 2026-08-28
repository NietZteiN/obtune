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
export OBTUNE_ENV="${OBTUNE_ENV:-/work/jvl210002/migration/envs/obtune}"
export OBTUNE_SCRATCH="${OBTUNE_SCRATCH:-/work/jvl210002/migration}"

export PATH="$OBTUNE_ENV/bin:$PATH"
export PYTHONPATH="$OBTUNE_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Keep caches and temp off $HOME (monorepo CLAUDE.md §2). On juno both /home and
# /work are the same MooseFS cluster, but compute nodes contend on $HOME, and the
# 88 GB model cache moved with the project rather than being re-downloaded.
export HF_HOME="${HF_HOME:-$OBTUNE_SCRATCH/hf_home}"
export TMPDIR="${TMPDIR:-$OBTUNE_SCRATCH/tmp}"
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-$OBTUNE_SCRATCH/cache/inductor}"
export TRITON_CACHE_DIR="${TRITON_CACHE_DIR:-$OBTUNE_SCRATCH/cache/triton}"

# Quieter vLLM startup; the engine's real errors still reach stderr.
export VLLM_LOGGING_LEVEL="${VLLM_LOGGING_LEVEL:-WARNING}"
export TOKENIZERS_PARALLELISM=false
