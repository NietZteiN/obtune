#!/usr/bin/env bash
# Build the obtune uv environment at $OBTUNE_ENV (see scripts/env.sh).
# One env for train + vLLM eval: vLLM pins torch (2.11.0); TRL/PEFT accept it.
# Merging uses PEFT add_weighted_adapter, so mergekit (accelerate~=1.6 pin) is NOT here.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../scripts/env.sh"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$TMPDIR/uv-cache}"
mkdir -p "$TMPDIR" "$UV_CACHE_DIR" "$(dirname "$OBTUNE_ENV")"

UV="${UV:-$(command -v uv || true)}"
if [[ -z "$UV" ]]; then
  echo "uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

"$UV" venv "$OBTUNE_ENV" --python 3.12
source "$OBTUNE_ENV/bin/activate"

LOCK="$HERE/lock-obtune.txt"

# Default is to REPLAY the lock, not to re-resolve. The five headline pins were
# never the problem: rebuilding on juno from the top-level spec reproduced torch,
# transformers, trl, peft and vllm exactly and still moved 42 transitive packages
# (huggingface-hub 1.26->1.29, scipy 1.18.0->1.18.1, pyarrow, pydantic, starlette).
# scipy is in the bootstrap path for every published CI, so an unpinned rebuild
# would have made the migration's acceptance test -- recomputing a known number
# from results/cells/ -- a test of two things at once. Pass --upgrade to re-resolve
# deliberately, which is the only way the lock should ever move.
if [[ "${1:-}" != "--upgrade" && -f "$LOCK" ]]; then
  echo "installing from $LOCK ($(wc -l < "$LOCK") packages); pass --upgrade to re-resolve"
  "$UV" pip install -r "$LOCK"
else
  "$UV" pip install \
    "vllm==0.26.0" \
    "transformers==5.14.1" \
    "trl==1.9.2" \
    "peft==0.20.0" \
    "accelerate==1.14.0" \
    "datasets>=4.7.0" \
    "evalplus" \
    "tree-sitter" "tree-sitter-python" "tree-sitter-javascript" \
    numpy pandas pyarrow scipy pyyaml pydantic tqdm tensorboard pytest
  "$UV" pip freeze > "$LOCK"
fi
python - <<'EOF'
import torch, transformers, trl, peft, vllm
print("torch", torch.__version__)
print("transformers", transformers.__version__)
print("trl", trl.__version__)
print("peft", peft.__version__)
print("vllm", vllm.__version__)
print("cuda build", torch.version.cuda)
EOF
echo "ENV BUILD OK: $OBTUNE_ENV"
