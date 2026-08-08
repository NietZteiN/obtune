# obtune — Does fine-tuning teach semantic invariance?

*Generalization, Modularity, and Attention Under Code Obfuscation.*
*Last updated: 2026-08-08*

LLMs degrade sharply on obfuscated code. Prior fine-tuning work targets **deobfuscation** —
recovering the original source. This project asks a different question: does fine-tuning on
**output prediction over code that stays obfuscated** teach *semantic invariance* (robustness to
the whole class of meaning-preserving transforms), or just *transform memorization* (learning to
invert the specific obfuscators seen in training)?

The discriminator is a **held-out obfuscator (H1)** that never appears in any training data.

| RQ | Question | Headline number |
|---|---|---|
| **RQ1** | Does per-condition LoRA tuning transfer across tiers, languages, and a held-out obfuscator? | Transfer matrix + **Invariance Index** (mean TR onto H1) |
| **RQ2** | Where transfer fails, do per-type adapters + a router beat monolithic tuning — and do they beat simply *telling* the model the obfuscation type? | routed vs monolithic vs merged vs oracle-prompt |
| **RQ3** | Does attention re-anchoring (identifiers → control/data flow) predict which transfers succeed? | TR ~ Anchoring Shift, permutation-tested |

Secondary: does tuning move models toward or away from **human** difficulty orderings (Papers 2–3)?

Full design: [`docs/design_doc_v0.1.md`](docs/design_doc_v0.1.md). Hypothesis ledger and phase
tracker: [`docs/CHECKLIST.md`](docs/CHECKLIST.md). Operating rules: [`CLAUDE.md`](CLAUDE.md).

## The condition ladder

Single-transform from the L0 parent, never stacked, identical semantics in Python and JavaScript
(authoritative definitions in [`configs/conditions.yaml`](configs/conditions.yaml)):

`L0` original · `L1b` adversarial rename · `L1r` random hex rename · `L2` sequential minify ·
`S1` control-flow flattening · `S2` opaque predicates + dead code · **`H1` held out, never trained**

The legacy Papers-1/3 tiers (`L0/L1/L1b/L2/L3`) live in a separate `tier_icse` namespace on
byte-identical rows — the only rows comparable to the human baselines. Their semantics differ per
language, which is exactly why they are not reused as condition codes
([`docs/TIER_MAPPING.md`](docs/TIER_MAPPING.md)).

## Layout

```
configs/     all knobs (conditions, models, training, eval, router, merges)
src/obtune/  exec/ (sandboxed execution + canonical outputs)  obf/ (the 7 transforms + semantic gate)
             corpus/ (sourcing, input generation, dedup)      testset/ (ICSE ingest + crosswalk)
             attention/ (RQ3)  router/ (RQ2)  sched/ (GPU job queue)
             prompts.py scoring.py train_sft.py eval_vllm.py eval_hf.py transfer.py
scripts/     numbered pipeline steps + smoke/lint/manifest checks
stats/       R GLMM stack (adapted from Papers 2–3), runs in the existing r_analysis env
data/        symlinked inputs + generated corpora (see data/DATA_SOURCES.md)
log/         dated research ledger, one folder per thread
src/obtune/cft/  side thread: replication of `nikiema2025contrastive` (docs/CFT_REPLICATION.md)
```

## Setup

```bash
bash env/setup_env.sh              # -> /data/jvl210002/conda_envs/obtune
(cd js && npm ci)                  # Babel + javascript-obfuscator (H1 generator only)
make check                         # SHA manifests + H1-marker scan + quarantine lint
pytest tests/ -q
```

## Running

```bash
# Data layer
python scripts/01_ingest_testset.py       # 70 L0 parents + 350 byte-identical legacy rows
python scripts/02_build_corpus.py         # sourcing -> filters -> inputs -> dedup -> splits
python scripts/05_build_variants.py       # 6 trainable conditions, semantic-gate validated
python scripts/gen_h1_quarantined.py --i-am-the-h1-generator   # H1, into data/quarantine/

# Week-1 kill-switch pilot (one idle GPU; check nvidia-smi first)
tmux new -s pilot -d 'CUDA_VISIBLE_DEVICES=0 bash scripts/run_pilot.sh'

# Post-gate grid
python scripts/build_manifest.py --config configs/eval/grid_v1.yaml
bash scripts/launch_workers.sh            # one detached tmux worker per idle GPU
```

## The one rule that matters most

**H1 never touches training** — not directly, not through a merge, not through router training,
not through checkpoint or prompt selection. Four independent enforcement layers are described in
[`CLAUDE.md`](CLAUDE.md) §3.2. If H1 leaks, the headline claim is void and no later analysis can
repair it.

## Changelog
- **2026-08-08** — Added the `nikiema2025contrastive` (Contrastive Fine-Tuning) replication as a
  side thread: `src/obtune/cft/`, `configs/cft/`, [`docs/CFT_REPLICATION.md`](docs/CFT_REPLICATION.md).
  It answers *their* question (forward vs reverse direction) on our corpus and does not touch RQ1–RQ3.
- **2026-08-04** — Project created; scaffold, condition ladder, execution/canonicalization contracts, and the RQ1–RQ3 implementation.
