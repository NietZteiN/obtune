# CHECKLIST — hypothesis ledger, experiment tracker, phased task list

*Last updated: 2026-08-05*

The living plan that `log/` threads resolve against. Hypotheses are pre-registered here **before** the runs that test them; a hypothesis moves to *resolved* only with a dated log entry quoting the deciding metric.

---

## 1. Hypothesis ledger

| ID | Falsifiable statement | Confirm if | Refute if | Experiment | Status |
|---|---|---|---|---|---|
| **H1a-trainable** | LoRA on condition *i* improves accuracy on *i* (the trainability gate) | self-gain ≥ +5 pts, Wilson/bootstrap CI excludes 0 | gain < 5 pts or CI includes 0 | pilot + RQ1 diagonal | open |
| **H1a** | Within-family transfer (identifier→identifier) is partial; cross-family (identifier→structural) is weak | TR(L1b→L1r/L2) > TR(L1b→S1/S2), both CIs separated | no family structure in the matrix | RQ1 transfer matrix | open |
| **H1b** | Cross-language transfer is weaker than cross-tier transfer within a language | mean TR(py→js) < mean within-language TR | equal or greater | RQ1, both languages | open |
| ~~**H1c**~~ | ~~Positive **raw** transfer onto H1 ⇒ semantic invariance~~ | — | — | — | ✗ **retired 2026-08-05** — raw ΔH1 is confounded with task acquisition (§5.1) |
| **H1c-rev** | **The discriminator, control-relative.** `acc_H1(tuned_i) − acc_H1(tuned_L0)` > 0 ⇒ invariance | CI excludes 0 and positive | ≈0 or negative ⇒ transform memorization | RQ1 H1 column vs the L0 control | **pilot: refuted for i=L1b** (−3.0 pts, CI [−10.5, +3.9]) |
| **H2a** | Obfuscation type is surface-detectable, so learned routing ≈ oracle routing | router test accuracy > 0.95; routed accuracy within 1 pt of oracle-routed | router accuracy < 0.8 or a large routed/oracle gap | RQ2 router | open |
| **H2b** | Per-type adapters + router ≥ monolithic at matched budget | routed accuracy > monolithic, CI excludes 0 | monolithic ≥ routed | RQ2 | open |
| **H2c** | **Conditioning vs capacity.** If oracle prompting recovers most of the tuning gain, the failure is conditioning, not capacity | cond_recovery ≥ 0.5 ⇒ conditioning branch | cond_recovery ≤ 0.2 ⇒ capability branch | pilot + RQ2 | open |
| **H2d** | Merges retain a substantial share of per-type gains | merged accuracy ≥ 0.7 × per-type gain | merges collapse toward base | RQ2 merges | open |
| **H3** | Anchoring Shift under condition *i* predicts TR(i→j) | positive slope, permutation p < 0.05 | slope ≈ 0 or permutation p ≥ 0.05 | RQ3 regression | open |
| **H3-causal** | Tuned-invariant models are less damaged by identifier-attention knockout than base | Δaccuracy(knockout) smaller post-tuning | equal or larger damage | RQ3 knockout (stretch) | open |
| **HA1** | Tuning moves model difficulty orderings toward human ones | Δρ > 0, bootstrap CI excludes 0 | Δρ ≤ 0 | human alignment (Paper-2 98 cells) | open |

**Resolved:**
- ✗ **H1c (raw form) — retired.** The pilot's L0 control showed raw ΔH1 measures task acquisition:
  an adapter trained on clean code reached H1 at .414 vs .384 for the L1b-trained one. Replaced by
  **H1c-rev** (control-relative). See §5.1 and
  [`../log/pilot/2026-08-05_l0-control-refutes-invariance.md`](../log/pilot/2026-08-05_l0-control-refutes-invariance.md).
- ✓ **H1a-trainable — SUPPORTED.** Self-gain +27.3 pts, CI [11.0, 43.2]; and +16.2 pts, CI [+4.7, +28.5]
  even against the clean-code control.

---

## 2. Pre-registration status

- [ ] H1a–H3 pre-registered (OSF) **before** the main RQ1 grid launches. The pilot is exploratory and is labeled as such (`phase=pilot` in every trial row).
- [x] Metric decisions frozen in the design doc before any run: strict scoring without containment (§5.1), TR denominator guard (§5.1), attention mass renormalized over the code-token region (§5.3), cluster bootstrap by `program_id` (§5.2).

---

## 3. Phase tracker

| Phase | Deliverable | Log thread | Status |
|---|---|---|---|
| **0 — Scaffold** | repo, charter, configs, env, canon/exec contracts verified in both languages | `setup/` | done 2026-08-04 |
| **1 — Data layer** | obfuscation pipeline (7 conditions × 2 languages), semantic gate, H1 quarantine, test-set ingest, training corpus | `setup/` | done (Python); JS corpus pending |
| **2 — Kill-switch pilot (GATE)** | 1.5B / Python / train L1b / eval all conditions + oracle prompt → `pilot_decision.json` | `pilot/` | **done 2026-08-05 — passed, + L0 control** |
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

*Run 2026-08-05. Qwen2.5-Coder-1.5B, Python, trained on L1b only (2,231-program corpus,
6,285 L1b pairs, 3 epochs, checkpoint-198 selected by held-in val EM 0.378). Evaluated on
the 23-program all-conditions-succeeded common subset, 99 items/cell, 2,772 trials.
Cluster-bootstrap CIs over `program_id`, 2,000 resamples, seed 17. Full table:
[`../results/analysis/pilot_decision.json`](../results/analysis/pilot_decision.json).*

| Quantity | Value | CI95 | Gate | Verdict |
|---|---|---|---|---|
| self_gain (L1b) | **+27.3 pts** | [11.0, 43.2] | ≥ +5 pts | ✅ pass |
| format_fail_rate (tuned) | **1.0 %** | — | < 2 % | ✅ pass |
| forget_L0 | **+29.3 pts** | [14.0, 44.9] | > −3 pts | ✅ pass (improves) |
| cond_recovery (1-shot oracle) | **0.333** | gain [−3.7, 24.2] | ≥0.5 cond. / ≤0.2 cap. | ⚠️ inconclusive band |
| cond_recovery (bare oracle) | **0.259** | gain [1.0, 13.7] | as above | ⚠️ inconclusive band |
| **h1_delta (Invariance Index, raw)** | **+27.3 pts** | **[16.1, 40.9]** | sign + CI excludes 0 | ✅ **excludes 0** |
| h1 beyond prompt-only conditioning | **+19.2 pts** | oracle gain +8.1 [2.2, 15.4] | — | not merely format learning |
| transfer_L2 / transfer_S1 | **+33.3 / +15.2** | — | L2 > S1 expected | ✅ as predicted |
| data_scaling (8k vs 24k) | not run | — | within 1 pt ⇒ halve the grid | ⏳ deferred |
| seed_noise | not run | — | ≪ self_gain | ⏳ deferred |

Per-condition accuracy (base → tuned):

| | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| base | .253 | .242 | .202 | .202 | .323 | .212 | **.111** |
| 1-shot oracle | .475 | .333 | .323 | .333 | .323 | .343 | .192 |
| tuned on L1b | **.545** | **.515** | **.576** | **.535** | **.475** | **.495** | **.384** |

**Branch decision: PROCEED to the full RQ1→RQ2→RQ3 arc, running both RQ2 arms.**
No gate failed. `cond_recovery` landed at 0.26–0.33, inside the 0.2–0.5 band the design
reserved for "run both" — prompt-only conditioning recovers roughly a third of the tuning
gain, so conditioning is a real part of the story but does not explain it. The RQ2 oracle
comparison stays a headline arm rather than an appendix.

> ⚠️ **SUPERSEDED 2026-08-05 by the L0 control** — see the block below and
> [`../log/pilot/2026-08-05_l0-control-refutes-invariance.md`](../log/pilot/2026-08-05_l0-control-refutes-invariance.md).

**H1c was provisionally read as SUPPORTED**, with caveats that the control has now settled:
- Training on L1b alone lifted the held-out obfuscator by +27.3 pts, CI excluding zero.
- That is *not* just the model learning the answer format: the 1-shot oracle, which also
  teaches the format (H1 format-fail 21.2 % → 9.1 %), recovers only +8.1 pts, leaving
  **+19.2 pts** attributable to tuning beyond conditioning.
- **Caveat 1 — one training condition.** Transfer Ratio is undefined for every off-diagonal
  cell here (no `tuned_j` exists for j ≠ L1b), so the Invariance Index is reported in raw
  points only. The normalized form needs the full per-condition grid.
- **Caveat 2 — gains are large everywhere, including L0 (+29.3).** A substantial share of
  every number is task acquisition, not obfuscation robustness. The base model is weak at
  the task itself (L0 .253). The grid must separate "learned the task" from "learned
  invariance"; the L0-trained adapter is the control that does it, and it is not run yet.
- **Caveat 3 — n=23 programs.** Adequate for a kill-switch, not for the paper's claims.

### 5.1 L0 control — H1c refuted as stated (2026-08-05)

Caveat 2 was the decisive one. An adapter trained on **clean L0 code only**, same recipe, reaches
the held-out obfuscator *at least as well* as the L1b-trained adapter:

| | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| base | .253 | .242 | .202 | .202 | .323 | .212 | .111 |
| tuned on L1b | .545 | .515 | .576 | .535 | .475 | .495 | **.384** |
| tuned on L0 (control) | .485 | .354 | .495 | .535 | .434 | .455 | **.414** |

**Control-relative benefit** of training on obfuscated rather than clean code —
`acc(tuned_L1b) − acc(tuned_L0)`:

| eval cond | Δ pts | CI95 | excludes 0 |
|---|---|---|---|
| **L1b** (trained) | **+16.2** | [+4.7, +28.5] | **yes** |
| L1r (same family) | +8.1 | [−1.0, +18.4] | no |
| L2 | +0.0 | [−8.4, +8.1] | no |
| S1 | +4.0 | [−1.2, +10.1] | no |
| S2 | +4.0 | [−4.4, +12.6] | no |
| **H1** (held out) | **−3.0** | [−10.5, +3.9] | no |

**Verdict: H1c as originally stated is REFUTED.** The +27.3 pt raw H1 gain is task acquisition —
learning output prediction and its answer format — obtainable from clean code alone. What survives
is a **transform-memorization gradient**: obfuscation-specific benefit is significant only on the
trained condition, fades on its family, and is zero-to-negative on the held-out one.

**Consequences already applied:**
- The Invariance Index is redefined relative to the clean-code control (design doc §5.1, §9.9);
  raw Δ-vs-base is a task-acquisition measure and must never be cited as invariance.
- An **L0 control adapter is a required cell** of every model × language block.
- `src/obtune/pilot.py` reports `condition_specific_benefit` and
  `invariance_index_control_relative` as first-class outputs.
