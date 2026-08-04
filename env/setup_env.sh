#!/usr/bin/env bash
# Build the obtune conda/uv environment at /data/jvl210002/conda_envs/obtune.
# One env for train + vLLM eval: vLLM pins torch (2.11.0); TRL/PEFT accept it.
# Merging uses PEFT add_weighted_adapter, so mergekit (accelerate~=1.6 pin) is NOT here.
set -euo pipefail

export TMPDIR=/data/jvl210002/tmp_pip
export UV_CACHE_DIR=/data/jvl210002/tmp_pip/uv-cache
export HF_HOME=/data/jvl210002/my_downloads/.cache/huggingface

ENV_DIR=/data/jvl210002/conda_envs/obtune
UV=/home/012/j/jv/jvl210002/miniconda3/bin/uv

"$UV" venv "$ENV_DIR" --python 3.12
source "$ENV_DIR/bin/activate"

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

"$UV" pip freeze > "$(dirname "$0")/lock-obtune.txt"
python - <<'EOF'
import torch, transformers, trl, peft, vllm
print("torch", torch.__version__)
print("transformers", transformers.__version__)
print("trl", trl.__version__)
print("peft", peft.__version__)
print("vllm", vllm.__version__)
EOF
echo "ENV BUILD OK: $ENV_DIR"
