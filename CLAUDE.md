# Claude System Instructions & Workflow Protocol (CLAUDE.md)

*Last updated: 2026-08-04*

You are executing within a constrained compute environment as an expert AI research engineer. You must strictly adhere to the infrastructure layout, experiment discipline, and cognitive workflow defined below.

This file governs the **`obtune/` sub-project** — *"Does Fine-Tuning Teach Semantic Invariance? Generalization, Modularity, and Attention Under Code Obfuscation."* It inherits the monorepo-wide rules in [`../CLAUDE.md`](../CLAUDE.md); where they differ, the more specific rule here wins.

---

## 0. Cognitive Workflow & Scratchpad Protocol

Before executing any complex command, code modification, or long GPU run, update or reference [`CLAUDE_SCRATCHPAD.md`](CLAUDE_SCRATCHPAD.md). This prevents context drift and allows human-in-the-loop verification.

- **Dynamic thinking:** do not settle on the first solution. Ground architectural decisions in the foundational papers in [`papers/`](papers/) (indexed in [`papers/REFERENCES.md`](papers/REFERENCES.md)), the design doc [`docs/design_doc_v0.1.md`](docs/design_doc_v0.1.md), and the hypothesis ledger [`docs/CHECKLIST.md`](docs/CHECKLIST.md).
- **Scratchpad lifecycle:** initialize/update the scratchpad → verify the plan against the Hardware, Storage, and Correctness constraints below → execute → verify the outcome and update the scratchpad.

---

## 1. Compute & Hardware

> **This project does NOT use SLURM** — there is no scheduler on this host. Jobs run directly; you select GPUs yourself.

- **Host:** `csr-94608.utdallas.edu`, accessed via SSH.
- **GPUs:** **4 × NVIDIA RTX A6000, 48 GB each** (indices 0–3), 96 CPU cores, ~250 GB RAM. Driver 595.71.05 / CUDA 13.2. NVLink pairs are 0↔1 and 2↔3 — for any 2-GPU job use a pair, never `1,2`.
- **GPU selection (before every run):** check `nvidia-smi` for **idle** GPUs (≈0 % util, near-zero memory), then pin `CUDA_VISIBLE_DEVICES=<id>` **before** importing torch. `src/obtune/gpu.py` and `src/obtune/sched/worker.py` both enforce this; the worker refuses a GPU with >2 GB used or >5 % util.
- **Shared box, no scheduler to protect you.** Never launch onto a GPU another job is using. If all 4 are busy, wait.
- **Cards may be LENT OUT.** `scheduler_policy.allowed_gpus` in [`configs/compute.yaml`](configs/compute.yaml) is the authoritative list of cards obtune may place work on, and `gpu_budget` caps how many it holds at once. Both `gpu_alloc.free()/claim()` and `scripts/launch_workers.sh` honour it, so stopping a worker is **not** how you lend a card — the supervisor follows whatever is free and would claim it back within one 300 s poll. Edit the config; do not hand-kill workers. Prefer lending an NVLink pair (0↔1 or 2↔3) so the borrower can still run TP=2.

  **Treat `allowed_gpus` as a CANDIDATE SET, not a fixed assignment.** As of 2026-08-12 it is `[0, 1, 2]` with `gpu_budget: 2` — obtune may consider three cards but never holds more than two. The worker already refuses any GPU with >2 GB used or >5 % util, so a wide candidate set cannot collide with a borrower; it only lets us follow whichever cards are genuinely free. This matters because **the borrower moves**: on 2026-08-12 their job migrated from GPU 2 onto GPU 0 and freed 2, and a hard-pinned `[0, 1]` left obtune on a single working card with an idle GPU it was forbidden to touch. GPU 3 (sglang) is still theirs and stays out of the list.

  **The borrower shares this Unix account.** `uid` is therefore *not* an ownership test — `gpu_alloc._same_uid` returns true for their processes. Anything that kills or reaps must additionally check `ppid == 1` and the process name; see `gpu_alloc.stranded_engines`.
- **Persistence:** long jobs run in a detached `tmux` session (`scripts/launch_workers.sh` spawns one per GPU, setting `CUDA_VISIBLE_DEVICES` at spawn time).
- **Project-specific feasibility:**
  - LoRA SFT on 1.5B: ~2–3 h/adapter on one A6000. On 7–8B: bf16 + gradient checkpointing peaks ≈25–28 GB, so **one GPU per adapter**, ~8–11 h each. No DeepSpeed, no model parallelism.
  - Full grid ≈ 54 runs ≈ 360 GPU-h ≈ 7–10 calendar days at 2–3 free GPUs.
  - Evaluation uses **vLLM offline multi-LoRA** (~3–6 min per 1.5k-item cell on 7–8B).
  - **Attention extraction cannot use vLLM** (it does not expose attentions) — it uses an HF eager forward on a stratified subset. Both paths must import the prompt builder from `src/obtune/prompts.py`, or Δ-attention would be measured on a different distribution than accuracy.

---

## 2. Storage Layout & Environment Configuration

- **Project root:** `/data/jvl210002/my_downloads/obtune/`. `$HOME` is small NFS — never write datasets, model caches, adapters, or attention dumps there.

### Partition boundaries
- **Repo files** (code, configs, docs, logs, manifests) stay lightweight and are committed.
- **Large artifacts** (adapters, attention caches, generated corpora, cell parquets) live under `data/`, `runs/`, `results/` and are gitignored. Manifests, split files, resolved configs and `run_manifest.json` files ARE committed — they are what makes a result reproducible.

### Environment
- Python env: **`/data/jvl210002/conda_envs/obtune`** (built by [`env/setup_env.sh`](env/setup_env.sh); pinned in `env/lock-obtune.txt`). torch 2.11 / transformers 5.14.1 / trl 1.9.2 / peft 0.20.0 / vllm 0.26.0.
- Node workspace: `js/node_modules` (`npm ci` from the committed lockfile). **`javascript-obfuscator` is installed for the H1 generator only.**
- R analysis reuses the existing `r_analysis` env: `/home/012/j/jv/jvl210002/miniconda3/envs/r_analysis/bin/Rscript`.
- `HF_HOME=/data/jvl210002/my_downloads/.cache/huggingface`, `TMPDIR=/data/jvl210002/tmp_pip`.

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
