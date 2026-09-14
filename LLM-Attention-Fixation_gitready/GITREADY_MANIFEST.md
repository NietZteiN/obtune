# Gitready Manifest

This export is a paper-aligned source subset.

Included:
- core generation and steering runtime
- source datasets for Humaneval and CruxEval (plus dataset metadata)
- steering priors and head-selection utilities
- obfuscated-code run entrypoint for a prepared corpus
- counterfactual and execution-trace evaluation code
- attention-level behavioral analysis helpers
- minimal optional script support (`scripts/steering/compute_head_mask.py`)
- paper PDF for reference

Intentionally excluded:
- generated logs, run outputs, reports, plots, and head-mask dumps
- obfuscation generation, equivalence-checking, and dataset-building tooling
- prepared obfuscated corpora and other generated obfuscation artifacts
- launcher scripts, progress scripts, dataset builders, and evaluation wrappers
- local secrets and key files
