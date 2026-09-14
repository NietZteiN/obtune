# LLM Attention Fixation

LLM Attention Fixation is a research codebase for studying and steering code-generation attention under original and obfuscated program representations.

Anonymous artifact mirror: https://anonymous.4open.science/r/LLM-Attention-Fixation-296D

The repository combines:

- attention collection and rendering for code-generation runs
- structured steering priors, including slicing, AST, and CFG
- obfuscated-code evaluation runs against a prepared corpus
- execution-trace and counterfactual evaluation pipelines

## What This Repo Is For

The main workflow in this repository is:

1. prepare source Java cases or point the runner at a prepared obfuscated corpus
2. run model generation with optional steering
3. evaluate trace prediction or counterfactual behavior
4. analyze metrics across datasets and techniques

## Main Components

- [main.py](main.py)
  - main attention-collection entrypoint
- [models.py](models.py)
  - model loading, generation, attention export, and steering integration
- [steering](steering)
  - steering configs, runtime logic, priors, and backend adapters
- [obfuscation](obfuscation)
  - obfuscated-code evaluation runner
- [evaluation](evaluation)
  - trace prediction, execution tracing, and evaluation helpers
- [scripts/steering/compute_head_mask.py](scripts/steering/compute_head_mask.py)
  - optional offline head-mask generation utility

## Running Qwen2.5

The lean artifact uses direct entrypoints instead of launcher wrappers.

Original/source-code steering run:

```bash
python main.py \
  --dataset humaneval \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --cache-dir .cache/models \
  --gpu-ids 0 \
  --runs-per-snippet 3 \
  --max-new-tokens 512 \
  --snippet Java_000 \
  --steer \
  --prior slice_hybrid \
  --beta-post 0.8 \
  --steer-last-n-layers 8 \
  --head-subset-mode none \
  --record-layers on \
  --auto-run-tag
```

Obfuscated-code steering run:

```bash
python obfuscation/main.py \
  --dataset humaneval \
  --source-root /path/to/obf_corpus \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --cache-dir .cache/models \
  --gpu-ids 0 \
  --code-snippet Java_000 \
  --techniques identifier_renaming \
  --runs-per-snippet 3 \
  --max-new-tokens 512 \
  --steer \
  --prior slice_hybrid \
  --beta-post 0.8 \
  --steer-last-n-layers 8 \
  --head-subset-mode none \
  --record-layers on \
  --auto-run-tag
```

Supported structured priors in the current steering stack include:

- `slice`
- `slice_hybrid`
- `ast`
- `cfg`
