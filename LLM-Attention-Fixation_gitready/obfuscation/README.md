# Obfuscated-Code Runner

This trimmed artifact keeps only the runtime entrypoint for evaluating models on a prepared obfuscated Java corpus.

It does not include:

- obfuscation generation tooling
- semantic-equivalence checking
- dataset-building or post-verification utilities

## Expected Input Layout

Pass a prepared obfuscated corpus with:

- `<source_root>/<snippet>/<technique>/*.java`
- or the alternate nested layout `<source_root>/<snippet>/<technique>/<tier>/*.java`

For example:

- `/path/to/obf_corpus/Java_000/identifier_renaming/Solution.java`

## Running Qwen2.5 On Obfuscated Code

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

When `--record-layers on`, the run emits:

1. `model_output.json` attention summaries
2. `record_layers_full.json.gz`
3. `bdv_features_b1.npz` and `bdv_features_b3.npz`
4. `bdv_schema.json`

## Output Layout

- prediction runs:
  - `<artifact_root>/obfuscation/result/{model}/{snippet}/{technique}/{run_tag}/{EM|Mismatch}/{run_idx}/`

## Reproducibility

Given the same prepared obfuscated corpus, model configuration, and generation settings, repeated runs follow the same runtime pipeline. Generation remains stochastic unless you also fix model-side sampling controls.
