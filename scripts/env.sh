# Source before any obtune command:  source scripts/env.sh
#
# Putting the env's bin/ on PATH is not optional. vLLM shells out to the `ninja`
# BINARY when it builds its kernels, so invoking the interpreter by absolute path
# (the natural thing on a box with many conda envs) makes engine startup die with
# a bare `FileNotFoundError: 'ninja'` whose real cause is buried in a child
# process — it surfaces as "Engine core initialization failed" with no root cause.

export OBTUNE_ROOT="${OBTUNE_ROOT:-/data/jvl210002/my_downloads/obtune}"
export OBTUNE_ENV="${OBTUNE_ENV:-/data/jvl210002/conda_envs/obtune}"

export PATH="$OBTUNE_ENV/bin:$PATH"
export PYTHONPATH="$OBTUNE_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Keep caches and temp off the small $HOME NFS (monorepo CLAUDE.md §2).
export HF_HOME=/data/jvl210002/my_downloads/.cache/huggingface
export TMPDIR=/data/jvl210002/tmp_pip

# Quieter vLLM startup; the engine's real errors still reach stderr.
export VLLM_LOGGING_LEVEL="${VLLM_LOGGING_LEVEL:-WARNING}"
export TOKENIZERS_PARALLELISM=false
