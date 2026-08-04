# CLAUDE_SCRATCHPAD.md — working state

*Protocol: [`CLAUDE.md`](CLAUDE.md) §0. Update before and after any complex task; this is
working memory, not a log. The durable record lives in [`log/`](log/).*

**Last updated:** 2026-08-04

---

## Current state

Phase 0–1 complete and verified; the RQ1–RQ3 implementation is being built out.

**Frozen contracts** — do not change without a design-doc update, everything depends on them:

| File | Contract |
|---|---|
| `src/obtune/config.py` | `PROJECT_ROOT`, `load_config` (with `_extends`), `GLOBAL_SEED = 17` |
| `src/obtune/paths.py` | quarantine guard; `load_training_jsonl` is the only training-read entry point |
| `src/obtune/schema.py` | `BaseProgram`, `Variant`, `TrainPair`, `EvalItem`, `TrialRow` (the stats contract) |
| `src/obtune/exec/pool.py` | `BatchItem` → `ProgramResult`; `CaseResult.matches` compares exceptions **by type only** |
| `src/obtune/exec/canon.{py,mjs}` | canonical output spec, verified byte-identical across languages |
| `configs/conditions.yaml` | the 7-condition ladder + H1 marker patterns + gate policy |

**Verified by running (2026-08-04):**
- canon parity Python ↔ JavaScript: 9/9 fixtures identical; sets/undefined/NaN/deep-nesting rejected on both sides.
- executor: Python and JS, both languages returning `ok` / `raised` (type only) / `timeout` / `unserializable` correctly; infinite loops terminate via RLIMIT_CPU (Python) and the vm watchdog (JS).
- quarantine lint: 5/5 (loader guard rejects quarantine/eval/outside paths; H1-labeled rows rejected inside the training tree; no `obf/h1` imports outside the generator; javascript-obfuscator confined to H1).
- environment: torch 2.11.0+cu130, transformers 5.14.1, trl 1.9.2, peft 0.20.0, vllm 0.26.0 in `/data/jvl210002/conda_envs/obtune`; Qwen2.5-Coder-1.5B-Instruct downloaded; `js/node_modules` installed (168 packages).

---

## Decisions taken (and the ones rejected)

1. **L2 = sequential minification** (`a`, `b`, …) + annotation stripping, not "L1r + extras". The legacy tiers were never purely identifier-based, so "per the existing tier definition" had to be resolved. Sequential minify matches what the legacy JS-L3 minifier actually produced and gives L1r-vs-L2 a *same-family, different-surface* contrast at equal information loss. **Rejected:** L2 as a strict superset of L1r — it would make L1r→L2 transfer trivial by construction.
2. **Dual tier namespace** (`condition` vs `tier_icse`) rather than relabelling the legacy ladder. Legacy tier semantics differ per language *and* per vintage; one label meaning four transforms is exactly the drift that would invalidate a cross-language claim.
3. **Integral floats collapse to plain integers** in `canon` (`2.0` → `2`). JavaScript has one number type; keeping the Python int/float distinction would score the same program differently by language. Scoring compares numerics with a tolerance anyway.
4. **javascript-obfuscator confined to H1.** Its `deadCodeInjection` forcibly enables `stringArray`, and `stringArray` is on by default — any use for a trainable condition leaks the held-out feature. Handled architecturally, plus a marker scan in the gate. **Rejected:** careful per-condition option configuration; one upstream default change would silently poison the corpus.
5. **No containment stage in scoring.** The `../LOG.md` §2026-06-09 audit measured ~3 % false positives from substring matching (`927` in `9273`). With no-CoT completions there is nothing to extract, so leniency buys nothing.
6. **PEFT `add_weighted_adapter` for merges,** not mergekit (whose LoRA path is merge-then-SVD-extract and which pins an incompatible accelerate).
7. **Single env** for train + vLLM eval: vLLM pins torch 2.11 and TRL/PEFT accept it. DeepSpeed dropped — single-GPU LoRA needs nothing from it.

---

## Open questions / watch items

- **Coverage of S1/S2** on real programs is unknown until the builder runs at scale. Target ≥90 % per condition; below that, headline numbers must use the all-conditions-succeeded common subset (already the plan) and the shortfall must be reported, not smoothed.
- **JS corpus scale**: curated ceiling ≈1.3k programs. Transpilation is execution-gated so correctness is safe, but the distribution shifts — the `provenance` covariate must actually be tested in the GLMM, not just recorded.
- **Attention span→token resolution** must be re-measured on Qwen2.5-Coder tokenizers (the transcoders validation was on Llama-3.1-8B and Qwen3-0.6B). Hard-fail below 0.98.
- **Dataset A Python I/O** is human-formatted and the code is double-spaced; canonical outputs are re-derived by execution and disagreements with the human key are logged. Anything beyond `FALSE` vs `False` is a finding, not a formatting artifact.

---

## Next up

1. Finish the module build-out and integration review; get the full test suite green.
2. Run the data layer end to end: test-set ingest → corpus → variants → H1 (quarantined), then `make check`.
3. Pre-register H1a–H3 before the main grid (the pilot is exploratory and labeled `phase=pilot`).
4. Week-1 kill-switch pilot on one idle GPU; fill in the verdict box in `docs/CHECKLIST.md` §5.
