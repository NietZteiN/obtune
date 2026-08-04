# Does Fine-Tuning Teach Semantic Invariance?
## Generalization, Modularity, and Attention Under Code Obfuscation

*Technical Design Document — v0.1 (August 2026)*
*Implementation status: see [CHECKLIST.md](CHECKLIST.md); deviations from the original design are recorded in §9.*

---

## 1. Core idea

LLMs degrade sharply on obfuscated code. Prior fine-tuning work targets **deobfuscation** — recovering original source or identifiers (DOBF; KLEE-augmented pair tuning, arXiv:2511.19130; OASIF for VM-obfuscated binaries). No existing work tests whether fine-tuning improves **reasoning on still-obfuscated code** (output prediction without a recovery step), or whether such gains reflect **semantic invariance** (robustness to the class of meaning-preserving transforms) versus **transform memorization** (learning to invert the specific obfuscators seen in training).

Three-stage arc:

1. **Generalization (RQ1)** — LoRA-tune on output prediction under one obfuscation condition; measure transfer across tiers, languages, and a held-out obfuscator.
2. **Modularity (RQ2)** — where transfer fails, test whether per-obfuscation-type adapters with a learned router beat monolithic tuning — and critically, whether they beat simply *telling* the model the obfuscation type (oracle conditioning).
3. **Mechanism (RQ3)** — test whether attention reallocation (identifier tokens → control/data-flow tokens) predicts which transfers succeed, turning the interpretability analysis into the causal explanation of RQ1/RQ2.

**Secondary analysis:** compare post-tuning model error patterns against the existing human baselines — does tuning re-align models with human difficulty orderings or push them further apart?

**Positioning:** evaluation is always on still-obfuscated code. Never train or evaluate on recovery. This is the clean separation from the DOBF lineage.

---

## 2. Research questions & hypotheses

**RQ1.** Does LoRA fine-tuning on output prediction under obfuscation transfer to (a) unseen tiers, (b) the untrained language, (c) a held-out obfuscator absent from all training data?

- **H1a** Within-family transfer (L1b→L1r/L2, identifier-based) is partial; cross-family transfer (identifier→structural) is weak.
- **H1b** Cross-language transfer is weaker than cross-tier transfer within a language.
- **H1c** Held-out-obfuscator performance is the discriminator: near-training-level ⇒ invariance; near-baseline ⇒ memorization.

**RQ2.** When transfer fails, do per-type adapters + learned router outperform (a) monolithic multi-condition fine-tuning, (b) merged LoRAs (TIES/DARE), (c) oracle prompt conditioning, (d) oracle routing?

- **H2a** Router accuracy is high (obfuscation type is surface-detectable), making learned routing ≈ oracle routing.
- **H2b** If oracle prompting ≈ MoE, the failure is *conditioning*, not *capacity* — the architecture story dies and the finding becomes "models know how but not when." Either outcome is publishable; the design reports this comparison regardless.

**RQ3.** Do attention-anchoring shifts predict transfer success?

- **H3** Transfer succeeds precisely in conditions where tuning re-anchors attention mass from identifier tokens onto control-flow and data-flow tokens; conditions where attention remains identifier-anchored show memorization signatures (held-out-obfuscator failure).

---

## 3. Task, data, and obfuscation pipeline

### 3.1 Task

**Output prediction:** given a self-contained function and a concrete input, predict the exact output. Scored by execution-verified exact match under a **strict normalized** protocol (§5.1).

### 3.2 Stimuli

- **Test set** — the existing ICSE stimuli (Dataset A: 20 HumanEval-X snippets × 5 legacy tiers, human-labeled; Dataset B: 50 contamination-controlled base problems × 5 tiers). 70 unique L0 parents (40 Python + 30 JavaScript). Retained exclusively as the test set so results stay comparable to the human baselines.
- **Training corpus** — new, disjoint programs. Self-contained functions filtered for determinism, no I/O, no randomness, ≤ 60 LOC, executable under CPython 3.11+ and Node. Sources: APPS (call-based), CruxEval, HumanEval, MBPP/MBPP+, CodeSearchNet (Python); HumanEval-X JS, CruxEval-X JS, MultiPL-E, plus execution-gated Python→JS transpilation (JavaScript).
- **Deduplication** — AST-hash (sha256 of the L2-canonicalized text, i.e. alpha-equivalence) plus MinHash (128 permutations, 5-gram shingles, Jaccard ≥ 0.8) against the test set, plus explicit upstream-id exclusion lists.

### 3.3 Obfuscation conditions

See [`../configs/conditions.yaml`](../configs/conditions.yaml) for the authoritative definitions and [TIER_MAPPING.md](TIER_MAPPING.md) for the legacy-tier crosswalk. Conditions are **single-transform from the L0 parent, never stacked** — this eliminates the composition-bug class the legacy stacked tiers had — and are **defined identically in both languages**.

| Code | Family | Transform | Train? |
|---|---|---|---|
| L0 | none | normalized original | yes |
| L1b | identifier | adversarial/misleading renaming | yes |
| L1r | identifier | random hex renaming | yes |
| L2 | identifier | sequential minification + annotation stripping | yes |
| S1 | structural | control-flow flattening (dispatch loop) | yes |
| S2 | structural | opaque predicates + dead code | yes |
| H1 | held-out | string encoding + MBA rewriting | **never** |

- **Python transforms:** custom AST/`symtable` + tree-sitter pipeline (`src/obtune/obf/py/`).
- **JavaScript transforms:** Babel (`src/obtune/obf/js/`). **`javascript-obfuscator` is confined to the H1 generator**: its `deadCodeInjection` forcibly enables `stringArray`, and `stringArray` is on by default, so any use of it for a trainable condition would leak the held-out feature into training. This is the highest-severity risk in the JS half and it is handled architecturally, not by configuration care.
- **Semantic-preservation gate:** every obfuscated variant must produce identical outputs to its L0 parent on all test inputs plus 20 fuzzed inputs. Exceptions are compared **by type only** — renaming legitimately changes messages and tracebacks. Variants failing the gate are discarded and logged with reasons.
- **H1 quarantine:** generated by a separate script, never loadable by any training job; enforced by four independent layers (CLAUDE.md §3.2).

---

## 4. Models & training

### 4.1 Base models
- Llama-3.1-8B-Instruct (general)
- Qwen2.5-Coder-7B-Instruct (code-specialized)
- Qwen2.5-Coder-1.5B-Instruct (scale contrast; cheap ablation platform)

Two model families × general/code contrast answers "is this a Llama quirk?" without exploding compute.

### 4.2 LoRA configuration
Rank r=32, α=64, dropout 0.05; targets: all attention projections (q,k,v,o) + MLP (gate,up,down). Rank ablation r ∈ {8, 32, 64} on the 1.5B model only. bf16 base. HF PEFT + TRL `SFTTrainer`.

SFT format: chat template; prompt = task instruction + code + input; completion = **output literal only**, loss masked on the prompt. No chain-of-thought in v1 — CoT-tuned variants are a stretch goal given the prior finding that CoT length anticorrelates with accuracy (ρ = −0.52).

Schedule: up to 3 epochs, lr 1e-4 cosine, warmup 3 %, effective batch 64. **Checkpoint-select early stopping**: save per-epoch checkpoints and pick the best by greedy exact-match on a held-in validation slice (robust to trainer-API churn and measures the metric we actually care about, unlike eval loss).

Per-condition training size: **24k examples** (8k programs × 3 input cases). Program diversity matters more than input multiplicity for this task; the pilot runs an 8k arm to test whether the curve is already flat, which would cut grid cost ~60 %.

One adapter per training condition per language per model ⇒ 6 × 2 × 3 = 36 primary adapters, plus monolithic runs, merges, and the rank ablation ⇒ ~54 runs.

### 4.3 RQ2 systems
- **Monolithic:** single LoRA on the union of training conditions, **size-matched** (24k total, stratified) for a fair comparison, with an optional full-data run to separate "interference" from "data budget".
- **Merged:** TIES / DARE-TIES / DARE-linear via **PEFT `add_weighted_adapter`** (LoRA-space merging). mergekit's LoRA path is merge-then-SVD-extract and pins an incompatible accelerate; it is kept only as an optional cross-check.
- **MoE (per-type adapters + router):** frozen base mid-layer mean-pooled prompt hidden state → 2-layer MLP → softmax over the **6 trainable conditions** (H1 is never a class). Hard top-1 routing is primary (items grouped by routed class for vLLM throughput); soft mixture is an HF-path ablation on a stratified subset. Reported: routing confusion matrix and the **routing-entropy distribution on H1**, which forces an out-of-distribution decision.
- **Oracle prompt:** untuned base, prompt states the obfuscation type (± a per-type one-shot demo).
- **Oracle routing:** ground-truth label selects the adapter — upper-bounds the router. For H1 no true adapter exists; we report the per-item best-of-6 as the routing upper bound instead (computable from already-run cells at zero extra cost).

### 4.4 Compute budget (re-based on A6000s)
LoRA SFT: ~2–3 h/adapter at 1.5B, ~8–11 h at 7–8B on one 48 GB A6000 (bf16 + gradient checkpointing, ≈25–28 GB peak). Full grid ≈ 360 GPU-h. Evaluation with vLLM multi-LoRA ≈ 3–6 min per 1.5k-item cell ⇒ the whole ~40-cell grid ≈ 1.5–2 GPU-days. Total well within a 7–10 calendar-day window on the shared 4-GPU box.

---

## 5. Evaluation & analysis

### 5.1 Metrics and the scoring protocol
Primary: **execution-verified exact-match accuracy** per condition, under a strict normalized protocol — normalize (strip whitespace/fences) → structural equality via literal parsing → recursive numeric tolerance 1e-6. **The containment/substring stage of the legacy harness is deliberately removed**: the grading audit in `../../LOG.md` §2026-06-09 showed it produces ~3 % false positives (`927` matching inside `9273`), and with no-CoT completions there is nothing to extract, so leniency buys nothing. `format_fail_rate` and a `raw_exact` variant are logged for a grading-sensitivity appendix.

Transfer matrix per model/language; `TR(i→j)` as defined in §2, with a **denominator guard**: TR is reported only when the self-gain `acc_j(tuned_j) − acc_j(base)` is ≥ 3 points and its bootstrap CI excludes zero — otherwise the ratio is unstable and the cell is marked undefined rather than plotted as a large number. Raw Δ-accuracy is reported alongside every TR.

**Invariance Index** = mean over training conditions of `TR(i→H1)`; because H1 has no self-tuned denominator, it is reported both normalized by the monolithic H1 gain and — as the primary form — as raw Δ-H1 points.

Catastrophic-forgetting check: L0 and HumanEval+ pass@1 pre/post tuning.

### 5.2 Statistics
Item-level binomial GLMMs (logit) with crossed random effects for program and model, fixed effects for train condition, eval condition, language and their interactions; Benjamini–Hochberg FDR **across the transfer matrix as one family**; Wilson CIs for cell accuracies; cluster bootstrap resampling `program_id` (input cases within a program are correlated). Pre-register H1a–H3 before the main runs.

### 5.3 RQ3: attention analysis
Token classes via AST/tree-sitter alignment: `{identifier, control-flow keyword, operator, literal, data-flow-critical, other}`, where data-flow-critical is the static backward def-use slice from the entry function's return expression. Because the classes overlap by construction (a sliced identifier is both), identifier mass is reported both including and excluding sliced defs.

Metrics per model × condition: attention mass fraction per token class (last-token query rows, **renormalized over the code-token region** — BOS-sink and prompt-boilerplate mass would otherwise swamp the effect; this is a pre-registered metric decision), the **Anchoring Shift** Δ = mass(control+dataflow) − mass(identifier), post-tuning minus pre-tuning, and attention entropy.

Causal-predictive test: regress `TR(i→j)` on Anchoring Shift under condition i (mixed model, random intercept per base model) with a ≥5,000-shuffle permutation test — the number of base models is small, so asymptotic p-values are not trustworthy. Claims are framed as **predictive**; they upgrade to causal only via the identifier-attention knockout intervention.

Attention extraction requires HF eager forwards (vLLM does not expose attentions) on a stratified subset, using the same prompt builder as the accuracy runs.

### 5.4 Human-alignment secondary analysis
- **Primary anchor (item-level):** the Paper-2 graded set — ~98 snippet-tier cells. Spearman ρ between per-cell model accuracy and per-cell human accuracy, computed separately pre- and post-tuning; headline statistic is Δρ with a bootstrap CI over cells. Baseline context: ρ = 0.30–0.47 for reasoning-tuned models vs ≈ 0 for coder/instruct in Paper 2.
- **Secondary (condition-level only):** the Paper-3 n=73 study covers 6 snippets × 3 tiers. Item-level correlation on 6 points is uninformative and is **not** run as a headline claim; instead we compare condition-level accuracy profiles (L0→L1b and L0→L2 drops with Wilson CIs) and use the timed/untimed arms as a bracketing band.
- **Error-category alignment:** transform-tag covariates from the existing annotation taxonomy (note: it is a *transform* taxonomy, not a response-error taxonomy) plus a small response-error taxonomy of our own, with programmatic **decoy-capture** detection via the L1b rename map.

---

## 6. Week-1 kill-switch pilot

Qwen2.5-Coder-1.5B, Python only: tune on L1b, evaluate on L0/L1b/L1r/L2/S1/S2/H1; run the oracle-prompt baseline on the same grid.

Gates (emitted to `results/analysis/pilot_decision.json`):

| Quantity | Gate |
|---|---|
| `self_gain` = acc_L1b(tuned) − acc_L1b(base) | ≥ +5 pts, CI excludes 0 — else fix capacity/data before the grid |
| `format_fail_rate` | < 2 % — validates the scoring protocol |
| `forget_L0` | > −3 pts — else add 10 % L0 replay to every grid recipe |
| `cond_recovery` = oracle-prompt gain / self_gain | ≥ 0.5 ⇒ **conditioning** branch (RQ2 routing/prompting becomes the story); ≤ 0.2 ⇒ **capability** branch (transfer matrix is the story) |
| `h1_delta`, `transfer_L2`, `transfer_S1` | first invariance read; sanity check that a rename adapter transfers to L2 more than to S1 |
| `data_scaling` (8k vs 24k), `seed_noise`, `tokens_per_sec` | re-parameterize the grid before launch |

Decision rules: transfer near-ceiling everywhere and oracle prompt ≈ tuning ⇒ re-scope to "obfuscation robustness is conditioning, not capability" (drop the MoE build, expand RQ3 + human alignment). Transfer partial/failing ⇒ proceed with the full RQ1→RQ2→RQ3 arc. Either branch yields a paper; the pilot only decides which.

---

## 7. Timeline (≈ 14 weeks)

| Weeks | Work |
|---|---|
| 1 | Kill-switch pilot; obfuscation-pipeline hardening; H1-quarantine checks |
| 2–3 | Training-corpus generation, semantic gate, dedup, pre-registration |
| 4–6 | RQ1: all per-condition adapters, transfer matrix, GLMMs |
| 7–8 | RQ2: monolithic, merges, router training, oracle baselines |
| 9–10 | RQ3: attention extraction, anchoring metrics, predictive regression |
| 11 | Human-alignment analysis; forgetting checks; ablations (rank, soft routing) |
| 12–14 | Writing, figures, artifact packaging (code + adapters + stimuli release) |

---

## 8. Risks & mitigations

| Risk | Mitigation |
|---|---|
| **javascript-obfuscator leaks H1 features into trainable conditions** (`deadCodeInjection` forces `stringArray`, which is default-on) | Architectural confinement to the H1 generator + an H1-marker regex scan in the semantic gate on every trainable variant |
| **MBA correctness in dynamic languages** (`+` is string concat or numeric; JS bitwise coerces to int32) | Guarded helper functions only, never bare rewrites; identities verified over random integers; reject H1 variants with too few actually-rewritten sites (a guard that degenerates to identity would make H1 spuriously easy) |
| **Flattening Python without gotos** | `while _st != -1` dispatch; `for` desugared via `next(it, SENTINEL)` (total, no try/except); hard bail on try/with/yield/match; exception comparison by type only |
| Ceiling effects on easy items | Stratify by L0 human difficulty; report per-stratum; add harder programs if base L0 accuracy > 85 % |
| Contamination (base models saw seed programs) | Report L0 base accuracy as a contamination proxy; the training corpus is transform-generated so obfuscated forms are near-certainly unseen; H1 doubly so |
| Router trivially perfect | Expected (H2a) — reframed as a finding: type is surface-detectable, so the interesting contrast is oracle prompt vs MoE (conditioning vs capacity) |
| "Attention is not explanation" critiques | Predictive regression + permutation test; causal upgrade only via the knockout intervention |
| JS/Python tooling asymmetry | Strength-match S1/S2 across languages via base-model accuracy deltas; report asymmetry rather than hiding it |
| JS corpus ceiling (~1.3k curated) | Execution-gated Python→JS transpilation to reach 4–6k, with a `provenance` covariate tested in the GLMM |
| Coverage imbalance across conditions distorting the matrix | Headline numbers on the all-conditions-succeeded common subset; `coverage_matrix.json` published |
| TR denominator instability | Denominator guard (self-gain ≥ 3 pts, CI excludes 0); raw Δ reported alongside |

---

## 9. Deviations from the original v0.1 brief

Recorded here so the implementation and the design stay honest with each other.

1. **Hardware re-based.** The brief budgeted A100-80GB hours; this project runs on 4× RTX A6000 48 GB with no scheduler. Single-GPU LoRA throughout; DeepSpeed dropped (it adds version risk and buys nothing at this scale).
2. **L2 disambiguated.** "Full identifier obfuscation per the existing tier definition" was under-determined — no legacy tier is purely identifier-based (Python L2 was flow flattening; JS L2 was dead code + string table). L2 is defined as maximal identifier destruction via sequential minification, matching what the legacy JS-L3 minifier actually produced, and giving L1r-vs-L2 a "same family, different surface" contrast at equal information loss.
3. **Dual tier namespace** instead of relabelling. Legacy tiers keep their own field on byte-identical rows; new conditions are regenerated from the L0 parents with language-identical semantics.
4. **Structural conditions split** into S1 (flattening) and S2 (opaque predicates + dead code) as separate single transforms rather than a stacked ladder.
5. **Scoring tightened** — containment stage removed (see §5.1), string comparison made case-sensitive.
6. **Merging via PEFT rather than mergekit** (dependency conflict; LoRA-space merge is also the more direct operation).
7. **Training-set size stated and justified** (24k/condition) rather than "all pairs"; the pilot tests whether even that is more than needed.
8. **JS corpus scale** acknowledged: curated ceiling ≈1.3k, reached via execution-gated transpilation with a provenance covariate.
