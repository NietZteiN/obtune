# CHECKLIST — hypothesis ledger, experiment tracker, phased task list

*Last updated: 2026-08-04*

The living plan that `log/` threads resolve against. Hypotheses are pre-registered here **before** the runs that test them; a hypothesis moves to *resolved* only with a dated log entry quoting the deciding metric.

---

## 1. Hypothesis ledger

| ID | Falsifiable statement | Confirm if | Refute if | Experiment | Status |
|---|---|---|---|---|---|
| **H1a-trainable** | LoRA on condition *i* improves accuracy on *i* (the trainability gate) | self-gain ≥ +5 pts, Wilson/bootstrap CI excludes 0 | gain < 5 pts or CI includes 0 | pilot + RQ1 diagonal | open |
| **H1a** | Within-family transfer (identifier→identifier) is partial; cross-family (identifier→structural) is weak | TR(L1b→L1r/L2) > TR(L1b→S1/S2), both CIs separated | no family structure in the matrix | RQ1 transfer matrix | open |
| **H1b** | Cross-language transfer is weaker than cross-tier transfer within a language | mean TR(py→js) < mean within-language TR | equal or greater | RQ1, both languages | open |
| **H1c** | **The discriminator.** Positive transfer onto the held-out obfuscator H1 ⇒ semantic invariance | Invariance Index (raw ΔH1) > 0 with CI excluding 0 | ΔH1 ≈ 0 or negative ⇒ transform memorization | RQ1 H1 column (final_eval) | open |
| **H2a** | Obfuscation type is surface-detectable, so learned routing ≈ oracle routing | router test accuracy > 0.95; routed accuracy within 1 pt of oracle-routed | router accuracy < 0.8 or a large routed/oracle gap | RQ2 router | open |
| **H2b** | Per-type adapters + router ≥ monolithic at matched budget | routed accuracy > monolithic, CI excludes 0 | monolithic ≥ routed | RQ2 | open |
| **H2c** | **Conditioning vs capacity.** If oracle prompting recovers most of the tuning gain, the failure is conditioning, not capacity | cond_recovery ≥ 0.5 ⇒ conditioning branch | cond_recovery ≤ 0.2 ⇒ capability branch | pilot + RQ2 | open |
| **H2d** | Merges retain a substantial share of per-type gains | merged accuracy ≥ 0.7 × per-type gain | merges collapse toward base | RQ2 merges | open |
| **H3** | Anchoring Shift under condition *i* predicts TR(i→j) | positive slope, permutation p < 0.05 | slope ≈ 0 or permutation p ≥ 0.05 | RQ3 regression | open |
| **H3-causal** | Tuned-invariant models are less damaged by identifier-attention knockout than base | Δaccuracy(knockout) smaller post-tuning | equal or larger damage | RQ3 knockout (stretch) | open |
| **HA1** | Tuning moves model difficulty orderings toward human ones | Δρ > 0, bootstrap CI excludes 0 | Δρ ≤ 0 | human alignment (Paper-2 98 cells) | open |

**Resolved:** (none yet)

---

## 2. Pre-registration status

- [ ] H1a–H3 pre-registered (OSF) **before** the main RQ1 grid launches. The pilot is exploratory and is labeled as such (`phase=pilot` in every trial row).
- [x] Metric decisions frozen in the design doc before any run: strict scoring without containment (§5.1), TR denominator guard (§5.1), attention mass renormalized over the code-token region (§5.3), cluster bootstrap by `program_id` (§5.2).

---

## 3. Phase tracker

| Phase | Deliverable | Log thread | Status |
|---|---|---|---|
| **0 — Scaffold** | repo, charter, configs, env, canon/exec contracts verified in both languages | `setup/` | done 2026-08-04 |
| **1 — Data layer** | obfuscation pipeline (7 conditions × 2 languages), semantic gate, H1 quarantine, test-set ingest, training corpus | `setup/` | in progress |
| **2 — Kill-switch pilot (GATE)** | 1.5B / Python / train L1b / eval all conditions + oracle prompt → `pilot_decision.json` | `pilot/` | not started |
| **3 — RQ1 transfer matrix** | 54-run grid, transfer matrices, GLMMs, BH-FDR | `transfer/` | not started |
| **4 — RQ2 modularity** | router, merges, monolithic, oracle arms | `modularity/` | not started |
| **5 — RQ3 attention** | token classes + slicers validated, extraction, anchoring metrics, predictive regression | `attention/` | not started |
| **6 — Human alignment** | Paper-2 Δρ, Paper-3 condition-level profiles, error-category alignment | `human-align/` | not started |
| **7 — Final H1 pass + writeup** | the second and last H1 evaluation, knockout (stretch), figures, artifact | `holdout-final/`, `writeup/` | not started |

---

## 4. Standing correctness checklist (run before trusting any result)

From CLAUDE.md §4 — the tuning-specific silent-failure list:

- [ ] Splits partition by `program_id`, never by row (`scripts/check_no_h1_in_train.py` + `data/splits/`).
- [ ] Adapter actually applied — tuned outputs differ from base on the same items.
- [ ] One prompt builder across train / vLLM eval / HF eval / attention extraction.
- [ ] Loss mask verified on a real batch (`scripts/inspect_batch.py`: prompt tokens are −100).
- [ ] `format_fail_rate` < 2 %; 50 graded trials sample-audited per new condition.
- [ ] Truncation rate at `max_seq_len` < 1 % (S1/S2 inflate length).
- [ ] Forgetting checked: L0 delta and HumanEval+ pass@1 pre/post.
- [ ] Coverage matrix published; headline numbers on the all-conditions-succeeded common subset.
- [ ] H1 access appended to `data/quarantine/h1/ACCESS_LOG.md` with a purpose.
- [ ] `make check` green (SHA manifests + H1-marker scan over the training tree).

---

## 5. Kill-switch verdict box

*Filled in by the Week-1 pilot; leave blank until the numbers exist.*

| Quantity | Value | CI | Gate | Verdict |
|---|---|---|---|---|
| self_gain (L1b) | — | — | ≥ +5 pts | — |
| format_fail_rate | — | — | < 2 % | — |
| forget_L0 | — | — | > −3 pts | — |
| cond_recovery | — | — | ≥0.5 conditioning / ≤0.2 capability | — |
| h1_delta | — | — | sign + CI | — |
| transfer_L2 / transfer_S1 | — | — | L2 > S1 expected | — |
| data_scaling (8k vs 24k) | — | — | within 1 pt ⇒ halve the grid | — |
| seed_noise | — | — | ≪ self_gain | — |

**Branch decision:** —
