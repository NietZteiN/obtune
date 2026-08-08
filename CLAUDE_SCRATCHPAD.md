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

- **S1 coverage is bounded by program *length*, not just by bail constructs.** Measured on the 12 Python
  fixtures: 10 flattened cleanly (randomized state ids, shuffled cases, outputs identical), 2 bailed — and
  both bails were `min_states=3`, i.e. the function body was too short to make a dispatch loop, not a
  `try`/`with`/`yield` construct. `configs/data.yaml` sets `loc_min: 3`, so a meaningful slice of the corpus
  will be S1-ineligible for this reason. Consequences to check once the builder runs at scale: (a) S1's
  program set will systematically differ from L1b's — the all-conditions-succeeded common subset is the
  defense and it must be used for headline numbers; (b) if the common subset is much smaller than the full
  set, consider raising `loc_min` for corpus admission rather than letting S1 silently select for long
  programs, which would confound "structural condition" with "longer program".
- **Coverage of S2** on real programs is still unknown until the builder runs.
- **H1 eligibility is literal-density-bound — RESOLVED as a reporting requirement, not a
  bug.** Measured on the real 70 test parents: **Python 27/40, JavaScript 24/30, 51/70
  overall (73 %)**. Of the 13 Python rejects, **6 have zero H1 sites** (no strings, no
  integer literals, no MBA-able operators — there is simply nothing for string encoding
  or MBA to act on) and 7 have 1–2 sites. Lowering `min_total_sites` to 1 would recover
  those 7 but at the cost of near-identity H1 variants, which is precisely the
  degeneracy the bar exists to prevent and would *inflate* the Invariance Index — the
  wrong trade for the headline number. **Decision: keep the bar at 3.** Consequences
  the analysis must honour: report H1 coverage explicitly, compute the Invariance Index
  on the H1-eligible subset, and restrict the other conditions to that same subset when
  comparing, so the H1 column is not read against a different program set.
- **JS corpus scale**: curated ceiling ≈1.3k programs. Transpilation is execution-gated so correctness is safe, but the distribution shifts — the `provenance` covariate must actually be tested in the GLMM, not just recorded.
- **Attention span→token resolution** must be re-measured on Qwen2.5-Coder tokenizers (the transcoders validation was on Llama-3.1-8B and Qwen3-0.6B). Hard-fail below 0.98.
- **Dataset A Python I/O** is human-formatted and the code is double-spaced; canonical outputs are re-derived by execution and disagreements with the human key are logged. Anything beyond `FALSE` vs `False` is a finding, not a formatting artifact.

---

## Side thread — CFT replication (`nikiema2025contrastive`), started 2026-08-08

Full design and the deviation list: [`docs/CFT_REPLICATION.md`](docs/CFT_REPLICATION.md).
Code in `src/obtune/cft/`, configs in `configs/cft/`, tests in `tests/test_cft_*.py`.

**Why:** it is the nearest prior work to the pilot finding (`papers/RELATED_WORK.md` §2.1) and
§7 names CFT as the candidate RQ1 intervention. Before adopting an intervention, check whether
its result reproduces on our corpus.

**Scope limit that cannot be worked around:** the paper's third transformation is string
encryption, which maps onto our `H1`. H1 is quarantined, so this replication covers renaming
(`L1b`/`L1r`/`L2`) and dead code (`S2`), and adds `S1` (control-flow flattening), which the
paper lacks. The paper's *hardest* arm is the one we cannot run.

**Decisions taken here (2026-08-08):**
- **Negatives are the obfuscated variant with one token changed**, not clean-vs-clean as the
  paper does. Under the paper's construction "is B obfuscated?" predicts the label perfectly,
  so L_pos/L_neg can be solved without comparing semantics. `clean_mutant` is kept as a config
  option so the confound is measurable rather than arguable.
- **Every negative is executed** against its parent's cases and kept only if an output really
  differs *and* it still runs on ≥50 % of them. Rejects equivalent mutants (which would teach
  the inverse of the intended lesson) and everywhere-broken ones (trivially spottable).
- **CodeBLEU is the published implementation** (`codebleu==0.7.0`), vendored to `env/vendor/`
  so `env/lock-obtune.txt` is untouched. The distribution's tree-sitter 0.22 pin is deliberately
  NOT vendored — it would shadow the 0.26 grammars `obf/base.py` depends on. `metrics.py`
  *appends* the vendor dir to `sys.path` for that reason.
- **Readability is a labelled substitute**, not Scalabrino et al.'s Java model. Only within-run
  contrasts are interpretable. Its short-identifier threshold (0.5) was set by measurement over
  400 programs (L0 flagged 8 % / L2 flagged 89 %), not by taste.
- **Model ladder:** 1.5B is a pipeline smoke test only. The headline number runs on
  `qwen25c-7b` — the paper's own "QwenCoder" row (39.00 % reverse under CFT), and the paper
  reports an architectural capacity hierarchy, so a null at 1.5B would be uninformative.
- **Queue priority 60** — behind the entire RQ1 grid. A replication of someone else's paper
  does not preempt the project's own experiments.

**Watch item:** `train.py` records `task_token_share` per run. Equal *instance* counts across
the three pools (the paper's balancing) do NOT mean equal loss weight — a `gen` target is a
whole program, a `pos`/`neg` target is one token. If the measured gen share is ~0.99, the
"three-term loss" is close to gen-only plus a rounding error, and that is a fact about the
paper's recipe worth reporting rather than silently correcting.

---

## Next up

1. Finish the module build-out and integration review; get the full test suite green.
2. Run the data layer end to end: test-set ingest → corpus → variants → H1 (quarantined), then `make check`.
3. Pre-register H1a–H3 before the main grid (the pilot is exploratory and labeled `phase=pilot`).
4. Week-1 kill-switch pilot on one idle GPU; fill in the verdict box in `docs/CHECKLIST.md` §5.
