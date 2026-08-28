# Claude System Instructions & Workflow Protocol (CLAUDE.md)

*Last updated: 2026-08-28*

You are executing within a constrained compute environment as an expert AI research engineer. You must strictly adhere to the infrastructure layout, experiment discipline, and cognitive workflow defined below.

This file governs the **`obtune/` sub-project** — *"Does Fine-Tuning Teach Semantic Invariance? Generalization, Modularity, and Attention Under Code Obfuscation."* It inherits the monorepo-wide rules in [`../CLAUDE.md`](../CLAUDE.md); where they differ, the more specific rule here wins.

---

## 0. Cognitive Workflow & Scratchpad Protocol

Before executing any complex command, code modification, or long GPU run, update or reference [`CLAUDE_SCRATCHPAD.md`](CLAUDE_SCRATCHPAD.md). This prevents context drift and allows human-in-the-loop verification.

- **Dynamic thinking:** do not settle on the first solution. Ground architectural decisions in the foundational papers in [`papers/`](papers/) (indexed in [`papers/REFERENCES.md`](papers/REFERENCES.md)), the design doc [`docs/design_doc_v0.1.md`](docs/design_doc_v0.1.md), and the hypothesis ledger [`docs/CHECKLIST.md`](docs/CHECKLIST.md).
- **Scratchpad lifecycle:** initialize/update the scratchpad → verify the plan against the Hardware, Storage, and Correctness constraints below → execute → verify the outcome and update the scratchpad.

---

## 1. Compute & Hardware

> **This project uses SLURM.** The login node has no GPU at all — `nvidia-smi` does not
> exist there. Never run a GPU job directly; submit it. This reverses the rule that stood
> until 2026-08-27, when the project lived on an unscheduled box.

- **Host:** `juno-l-02` (login), OpenHPC + SLURM 24.11.5, accessed via SSH. Migrated here
  2026-08-28 from `csr-94608.utdallas.edu`.
- **GPU partitions** (all capped at 2 days walltime). Full inventory in
  [`configs/compute.yaml`](configs/compute.yaml):

  | partition | capacity | note |
  |---|---|---|
  | `h200` | 26 nodes × 2 × H200 NVL (141 GB), 64 cores / 375 GB per node | **the default.** 52 GPUs |
  | `h100` | 3 heterogeneous nodes | only `g-04-02` is full-fat (4 × H100 80 GB) |
  | `a30` | 2 nodes × 2 × A30 | closest analogue to the old A6000s; cheap smoke tests |
  | `a30-2.12gb`, `a30-4.6gb` | MIG slices, 12 GB / 6 GB | too small for 1.5B bf16 training |
  | `normal`, `dev` | 90 / 8 CPU-only nodes | corpus building, merging, analysis, `dev` is 2 h |

- **Submitting work:** `python scripts/slurm/submit.py --queued` drains
  `runs/manifest/queued/`, one sbatch job per manifest; `--argv …` submits an ad-hoc
  command; `--dry-run` prints the script without submitting. The manifest lifecycle
  (`queued → running → done|failed`) is preserved and now moves **inside** the sbatch
  script, so a job that never starts stays queued and a job killed at walltime still
  lands in `failed/`. That last part fixes the old scheduler's headline defect: a worker
  that died mid-run stranded its claim in `running/` and nothing noticed.
- **GPU selection is not yours to make.** SLURM allocates and sets `CUDA_VISIBLE_DEVICES`;
  cgroups enforce it. `gpu.pick_free_gpus()` returns local indices under an allocation and
  `gpu.pin()` is a deliberate **no-op** there — on a 2-GPU node given `--gres=gpu:1` SLURM
  may hand you physical device 1 as local index 0, so rewriting the variable selects the
  wrong device or none, silently.
- **Queue waits are real, and they are the new planning constraint.** On 2026-08-28 `h200`
  had 41 running / 35 pending and estimated a 7-hour start for a 5-minute job. On the old
  box a free card was taken in seconds. **Batch work; do not hold interactive allocations;
  expect a submit-and-return-tomorrow cadence.** `a30` is usually shorter.
- **RETIRED, do not use:** `src/obtune/sched/`, `src/obtune/gpu_alloc.py`,
  `scripts/launch_workers.sh`, `scripts/supervise.sh`, `scripts/pipeline.sh`. These
  implemented GPU polling, an `allowed_gpus`/`gpu_budget` lending policy, and a tmux
  supervisor, all because the old host had no scheduler and was shared informally with a
  borrower **on the same Unix account** (so `uid` was not an ownership test). SLURM solves
  every one of those problems. The reasoning is preserved in
  `configs/compute.yaml::legacy_scheduler_policy` and `git show c72224a`.
- **Project-specific feasibility:** the numbers below were measured on A6000s and are now
  **upper bounds pending re-measurement on H200** — see the open item in
  `log/setup/2026-08-28_juno-migration.md`.
  - LoRA SFT on 1.5B: ~2–3 h/adapter on one A6000. On 7–8B: bf16 + gradient checkpointing
    peaks ≈25–28 GB, so **one GPU per adapter**, ~8–11 h each. No DeepSpeed, no model
    parallelism — and with 141 GB per H200 there is even less reason to add either.
  - Evaluation uses **vLLM offline multi-LoRA** (~3–6 min per 1.5k-item cell on 7–8B).
  - **Attention extraction cannot use vLLM** (it does not expose attentions) — it uses an
    HF eager forward on a stratified subset. Both paths must import the prompt builder from
    `src/obtune/prompts.py`, or Δ-attention would be measured on a different distribution
    than accuracy.

---

## 2. Storage Layout & Environment Configuration

- **Project root:** `/work/jvl210002/migration/obtune/`. Keep datasets, model caches,
  adapters and attention dumps out of `$HOME`: on juno both `/home` and `/work` are the
  same MooseFS cluster, but compute nodes contend on `$HOME`.
- **The three roots are defined once**, in [`scripts/env.sh`](scripts/env.sh):
  `OBTUNE_ROOT`, `OBTUNE_ENV`, `OBTUNE_SCRATCH`. Everything else derives from them, and
  each is overridable from the environment. Relocating the project should be a four-line
  change, not the 18-site grep the 2026-08-28 move actually required.

### Partition boundaries
- **Repo files** (code, configs, docs, logs, manifests) stay lightweight and are committed.
- **Large artifacts** (adapters, attention caches, generated corpora, cell parquets) live under `data/`, `runs/`, `results/` and are gitignored. Manifests, split files, resolved configs and `run_manifest.json` files ARE committed — they are what makes a result reproducible.

### Environment
- Python env: **`/work/jvl210002/migration/envs/obtune`** — a `uv` venv, not conda
  (built by [`env/setup_env.sh`](env/setup_env.sh); pinned in `env/lock-obtune.txt`).
  torch 2.11.0+cu130 / transformers 5.14.1 / trl 1.9.2 / peft 0.20.0 / vllm 0.26.0.
  **`setup_env.sh` replays the lock by default**; `--upgrade` re-resolves and rewrites it.
  Rebuilding from the top-level spec instead reproduces all five headline pins and still
  moves ~42 transitive packages, `scipy` among them — and `scipy` is in the bootstrap
  path for every published CI.
- ⚠️ **CUDA: the GPU nodes run driver `550.163.01` (CUDA 12.4), not CUDA 13.** The lock's
  `torch==2.11.0+cu130` therefore reports `torch.cuda.is_available() == False` on **every**
  GPU node — a30 and h200 alike — while `nvidia-smi` works fine, so the failure looks like a
  code bug and is not. The working env is
  **`/work/jvl210002/migration/envs/obtune-cu129`**: identical package versions, with
  `torch 2.11.0+cu129` installed from `https://download.pytorch.org/whl/cu129`. CUDA 12
  minor-version compatibility covers an r550 driver, and it is verified on an H200 —
  `cuda available: True`, sm_90, 150 GB, 161.7 TFLOP/s bf16.
  **vLLM is a separate, unsolved problem:** every PyPI `vllm` wheel back to 0.23 is built
  against CUDA 13 (`vllm._C_stable_libtorch` links `libcudart.so.13`), and the `rhel9`
  repo publishes no `cuda-compat-13-x` forward-compatibility package. Training and the HF
  eval path work; the vLLM eval path does not. Fixing this properly means the cluster
  driver moving to r580+.
- Node workspace: `js/node_modules` (`npm ci` from the committed lockfile). **`javascript-obfuscator`
  is installed for the H1 generator only.** ⚠️ **`node` is not installed on juno.** The
  814 MB `node_modules` tree transferred intact but has no interpreter, so the H1/H2/H3
  generators and everything JavaScript are blocked until a node toolchain is added.
- R analysis: `module load R/4.5.0` (`/opt/ohpc/pub/libs/gnu14/R/4.5.0/bin/Rscript`). The old
  personal `r_analysis` env did **not** transfer; its packages (the GLMM stack under
  `stats/` — lme4, emmeans) must be reinstalled before anything there runs.
- `HF_HOME=/work/jvl210002/migration/hf_home` (88 GB, moved with the project rather than
  re-downloaded), `TMPDIR=/work/jvl210002/migration/tmp`, plus `TORCHINDUCTOR_CACHE_DIR`
  and `TRITON_CACHE_DIR` under `$OBTUNE_SCRATCH/cache/`. All set by `scripts/env.sh`.
- **Three cross-project stimulus files did not transfer** and are needed only to rebuild
  the corpus: `full_human_experiment_v2.json`, `tasks_unified_50.json` (both from
  `model_understanding/`) and `humaneval_x_js_full.json`. `configs/data.yaml` and
  `configs/sources.yaml` point at where they must be placed. `data/` is intact, so
  nothing is blocked until something is regenerated.

### Destructive commands — human-in-the-loop required
**Never run `rm -rf` — or any recursive/forced/bulk deletion — without first confirming with the human.** State the blast radius, dry-run it (`ls`/`find`), wait for explicit approval, then run the narrowest command that does the job. Trained adapters and gate-validated corpora cost GPU-hours and CPU-days to regenerate; treat their deletion like irreplaceable results.

---

## 3. Core Research Goal

Test whether LoRA fine-tuning on **output prediction over still-obfuscated code** teaches **semantic invariance** (robustness to the class of meaning-preserving transforms) or merely **transform memorization** (learning to invert the specific obfuscators seen in training).

**Positioning:** evaluation is *always* on still-obfuscated code. We never train or evaluate on recovery/deobfuscation. That is the clean separation from the DOBF lineage.

- **RQ1 — Generalization.** Per-condition LoRAs; transfer matrix (train-condition × eval-condition) across tiers, languages, and the held-out obfuscator. Transfer Ratio `TR(i→j) = (acc_j(tuned_i) − acc_j(base)) / (acc_j(tuned_j) − acc_j(base))`. **Invariance Index** = mean over `i` of `TR(i→H1)`.
- **RQ2 — Modularity.** Per-type adapters + learned router vs monolithic tuning vs TIES/DARE merges vs **oracle prompt conditioning** vs oracle routing. If oracle prompting ≈ MoE, the finding becomes "models know how but not when" — publishable either way, so the comparison is reported regardless.
- **RQ3 — Mechanism.** Does attention re-anchoring (identifier tokens → control/data-flow tokens) predict which transfers succeed? Predictive regression first; causal claims only via the knockout intervention.
- **Secondary — Human alignment.** Does tuning move models toward or away from human difficulty orderings? Primary anchor is the Paper-2 98-cell item-level set; the Paper-3 n=73 study is used at condition level only (6 items is underpowered for item-level ρ, and saying so is part of the contribution).

### 3.1 The condition ladder

Single source of truth: [`configs/conditions.yaml`](configs/conditions.yaml). Conditions are **single-transform from the L0 parent, never stacked**, with **identical semantics in Python and JavaScript**.

| Code | Family | Transform | Trainable |
|---|---|---|---|
| `L0` | none | normalized original (comments/docstrings stripped in every condition) | yes |
| `L1b` | identifier | adversarial/misleading renaming incl. the entry function | yes |
| `L1r` | identifier | random hex renaming (`v_a3f2`) | yes |
| `L2` | identifier | sequential minification (`a`, `b`, …) + annotation stripping; also the dedup canonicalizer | yes |
| `S1` | structural | control-flow flattening (dispatch loop, randomized state ids) | yes |
| `S2` | structural | opaque predicates + dead code | yes |
| `H1` | held-out | string encoding + guarded MBA rewriting | **never** |

The legacy Papers-1/3 tiers (`L0/L1/L1b/L2/L3`) live in a **separate namespace** (`tier_icse`) on 350 byte-identical rows — the only rows comparable to the human baselines. Their semantics differ per language, which is exactly why they are not reused as condition codes. See [`docs/TIER_MAPPING.md`](docs/TIER_MAPPING.md). ⚠️ Legacy **JS L2/L3 rows contain H1-family features** (string-keyed dispatch tables) and are never trainable and never usable in an "unseen transform" claim.

### 3.2 H1-quarantine discipline (HARD RULE)

H1 is the paper's discriminator. If it leaks, the headline claim is dead and no analysis can recover it.

1. H1 stimuli live **only** under `data/quarantine/`. Nothing else may write there.
2. H1 is **never** used for training, hyperparameter or prompt selection, router training, checkpoint selection, or merge tuning.
3. H1 is evaluated exactly twice: one frozen pilot pass (`purpose=pilot_eval`) and one final pass (`purpose=final_eval`). Every read appends a row to `data/quarantine/h1/ACCESS_LOG.md` (date, script, purpose, log-entry link).
4. Enforcement is four independent layers, because any one alone is bypassable:
   - `src/obtune/paths.py::load_training_jsonl` — the single training-read entry point; raises `QuarantineViolation` for anything outside `data/train/` or inside `data/quarantine/`/`data/eval/`, and rejects H1-labeled rows wherever found.
   - `tests/test_quarantine_lint.py` — greps `src/` and `scripts/` for raw file reads that bypass that entry point, and for imports of `obf/h1/` outside the generator.
   - `scripts/gen_h1_quarantined.py` — the only module permitted to import `src/obtune/obf/h1/`; refuses to run without `--i-am-the-h1-generator`; writes outputs `0o444`.
   - `scripts/check_manifest.py` — SHA manifest verification **plus an H1-marker content scan** over every training file (patterns in `configs/conditions.yaml`). Wired as a pre-commit hook and `make check`. This catches leakage even when labels are correct.

---

## 4. Experimental Correctness & Rigor

Treat a single run as a data point, not a conclusion.

- **Reproducibility:** set and record a deterministic seed for every run (`src/obtune/seedutil.py`); every kept run writes a `run_manifest.json` (`src/obtune/provenance.py`) with the command, resolved config, script sha256s, git commit, GPU id, and timestamp.
- **Smoke-test first:** validate on the 1.5B model, a handful of items, single GPU, before any 7–8B run. `scripts/smoke_env.py` is the gate.
- **Tuning-specific silent-failure checks** (this project's equivalent of an MI telemetry list — check all of these before trusting a result):
  1. **Split leakage** — splits partition by `program_id`, never by row. An obfuscated variant of a training program appearing in the test set silently inflates the whole transfer matrix.
  2. **Adapter not applied** — assert the tuned model's outputs (or logits) actually differ from the base before keeping an eval.
  3. **Chat-template / tokenizer mismatch** between training and eval — one prompt builder (`prompts.py`), used by train, vLLM eval, HF eval and attention extraction alike.
  4. **Loss-mask breakage** — `scripts/inspect_batch.py` decodes a real batch and asserts prompt tokens are `-100`. TRL API churn is the expected cause; this is a hard pilot gate.
  5. **Grader false positives** — no containment/substring matching (the audit in `../LOG.md` §2026-06-09 found ~3 % false positives, `927` matching inside `9273`). Strict normalized exact match only; sample-audit 50 graded trials per new condition.
  6. **Format failures masquerading as errors** — report `format_fail_rate`; the constrained no-CoT format should keep it under 2 %.
  7. **Catastrophic forgetting** — L0 accuracy and HumanEval+ pass@1 pre/post for every adapter.
  8. **Truncation** — log the rate at `max_seq_len`; S1/S2 inflate code length and silent truncation would look like a structural-condition effect.
- **Statistics:** new measures enter a GLMM stack adapted from Papers 2–3 (`stats/`): item-level binomial GLMMs with crossed random effects for program × model, Wilson CIs, BH-FDR **across the transfer matrix as one family**. Cluster-bootstrap by `program_id` (multiple input cases per program are correlated — bootstrapping items would understate the CIs). Vary seeds before claiming an effect; report the variance.
- **Coverage honesty:** S1/S2 bail on some programs by design ("correctness beats coverage"). Headline transfer numbers use the **all-conditions-succeeded common subset** so cells are not confounded by differing program sets; per-condition full sets are secondary. `data/manifests/coverage_matrix.json` is published.

---

## 5. Documentation & Engineering Hygiene

- **Document in stride,** not post-hoc.
- **Configuration management:** all hyperparameters, model specs, condition definitions and pipeline knobs live in version-controlled files under `configs/`. Do not pass complex arguments ad hoc.
- **Code comments:** comment non-obvious algorithmic blocks (flattening IR, MBA guards, span→token resolution, TR denominator guard) and record the reasoning behind design paths taken **and rejected**.

---

## 6. Experiment Log Protocol

Maintain a continuous research ledger in the [`log/`](log/) folder (this replaces a flat `LOG.md`). Entries are organized by experiment thread and by date; [`log/README.md`](log/README.md) is the master index.

**Dating convention:** point-in-time artifacts carry `YYYY-MM-DD` in their name — log entries (`log/<thread>/YYYY-MM-DD_<slug>.md`), results runs (`results/YYYY-MM-DD_<experiment>/`). Living documents (`CLAUDE.md`, `README.md`, `docs/*`, `configs/*`) keep a stable filename, open with `Last updated: YYYY-MM-DD`, and end with a `## Changelog`.

```
log/
  README.md                 # master index — update Timeline + By-thread tables on every new entry
  TEMPLATE.md               # copy-paste daily-entry + thread-README templates
  <thread>/                 # setup, pilot, transfer, modularity, attention, human-align, writeup
    README.md               # status · hypotheses (open/resolved) · what worked / didn't · entries
    YYYY-MM-DD_<slug>.md    # one entry per working day per thread
```

Every working day, for each thread you advanced: create the entry file from `log/TEMPLATE.md`; **never alter an existing entry** (corrections go in a new dated entry that references the old one); update the thread README's status/hypothesis ledger; add a row to `log/README.md`'s Timeline. Ground every claim in real metrics — never invent numbers.

---

## Changelog
- **2026-08-14** — §1's claim that "`gpu_alloc.free()/claim()` **and** `scripts/launch_workers.sh`
  honour it" was true of `allowed_gpus` but **false of `gpu_budget`**: `launch_workers.sh`
  filtered by the allowed list and then started a worker on *every* remaining candidate. With
  `[0, 1, 2]` and `gpu_budget: 2` that is three workers against a two-card budget, and because
  `pipeline.sh::ensure_infra` re-runs it on every poll, a hand-stopped worker came straight back.
  The script now reads `gpu_budget` and caps the number of LIVE workers, counting every
  `runs/manifest/workers/*.pid` rather than only the candidates it was about to consider — a busy
  worker's GPU is not idle, so counting within the candidate list saw zero live workers exactly
  when the budget was already spent. Twelve minutes after the fix the borrower took GPU 2 for an
  11-hour job, which the cap correctly declined to contest. The doc statement is now accurate;
  it was aspirational before.
- **2026-08-12** — §1: `allowed_gpus` is now a candidate set (`[0, 1, 2]`, budget 2) rather than a
  fixed pair, after the borrower's job moved from GPU 2 onto GPU 0 and left obtune pinned to one
  working card beside an idle-but-forbidden GPU. Also recorded that the borrower shares this Unix
  account, so `uid` is not an ownership test for any reaper.
- **2026-08-11** — §1: recorded that GPUs 2–3 are lent to a neighbour and that `scheduler_policy.allowed_gpus` / `gpu_budget` in `configs/compute.yaml` — not stopping a worker — is how a card is lent.
- **2026-08-04** — Charter created. Adapted from `../transcoders/CLAUDE.md`: kept §1 compute (same host, no SLURM), §2 storage and the destructive-command rule, and the §6 log-folder protocol. Wrote a new §3 (the fine-tuning/invariance goal, the 7-condition ladder, the dual tier namespace) with §3.2 promoting H1 quarantine to a four-layer hard rule, and replaced the MI silent-failure list in §4 with the tuning-specific one.

- **2026-08-28** — **Cluster migration: `csr-94608` → `juno`.** §1 rewritten end to end. The
  old §1 opened with "This project does NOT use SLURM"; juno has SLURM, the login node has no
  GPU, and `nvidia-smi` does not exist there, so every operational instruction in it was not
  merely stale but actively wrong. `src/obtune/sched/`, `gpu_alloc.py`, `launch_workers.sh`,
  `supervise.sh` and `pipeline.sh` are retired in favour of `scripts/slurm/submit.py`, which
  keeps the manifest lifecycle (it is the provenance layer, not scheduler scaffolding) and
  moves the state transitions into the sbatch script so a walltime kill files the job under
  `failed/` instead of stranding it. `gpu.py` gained a SLURM branch: `pin()` is a no-op inside
  an allocation, because rewriting `CUDA_VISIBLE_DEVICES` there selects the wrong device
  silently. §2 rewritten for the new roots, which are now defined once in `scripts/env.sh`
  rather than at 18 sites. Three facts worth carrying: **queue waits are hours** where a card
  used to be free in seconds; **node is not installed**, which blocks all JavaScript work; and
  the **`r_analysis` env did not transfer**, which blocks `stats/`. Migration verified by
  recomputing published numbers from `results/cells/` — `merge_dare_ties − tuned_L0` on Grid A
  H1 reproduces at −0.66 [−1.89, +0.66] exactly (`scripts/verify_migration.py`), and the H1
  quarantine passes all four layers on 207,136 train rows. Full account:
  `log/setup/2026-08-28_juno-migration.md`.
