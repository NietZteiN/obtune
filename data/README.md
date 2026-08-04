# data/ — inputs and generated corpora

Nothing in here is committed except this file, [`.gitignore`](.gitignore), [`DATA_SOURCES.md`](DATA_SOURCES.md),
and the JSON manifests under `manifests/` and `splits/` (they are small and they are the
reproducibility record).

Provenance of every symlinked input, and the script that regenerates every derived tree,
is in [`DATA_SOURCES.md`](DATA_SOURCES.md).

## Layout

```
stimuli/     symlinks -> span-annotated ICSE stimuli (read-only)
human/       symlinks -> Paper-2 / Paper-3 human baselines (read-only)
raw/         downloaded source datasets
train/       base/ + variants/<cond>/ + pairs/<cond>/    <- the ONLY tree a training job may read
eval/        testset/{base,variants/<cond>,legacy_icse}/  <- never read by training
quarantine/  h1/  <- HELD-OUT OBFUSCATOR. See the warning below.
rejects/     semantic-gate failures, with reasons
manifests/   coverage_matrix.json, dedup_report.json, SHA manifests
splits/      program-level train/val/test assignment
```

## ⚠️ quarantine/

`quarantine/h1/` holds the held-out obfuscator that decides the paper's headline claim
(semantic invariance vs transform memorization). It is written only by
`scripts/gen_h1_quarantined.py` and read only by the two sanctioned evaluation passes,
each of which appends to `quarantine/h1/ACCESS_LOG.md`.

If H1 ever enters training — directly, via a merge, via router training, or via
checkpoint/prompt selection — the invariance claim is void and no downstream analysis can
recover it. The enforcement layers are described in [`../CLAUDE.md`](../CLAUDE.md) §3.2.
