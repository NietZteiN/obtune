# Experiment 2 — Is the memorization gradient a property of the regime, or of one adapter?

*Design document. Written 2026-08-05, before any run. Pre-register §3 before executing §6.*

---

## 1. Context and the question

The Week-1 pilot ([`PILOT_REPORT_2026-08-05.md`](PILOT_REPORT_2026-08-05.md)) trained **one** adapter,
on L1b (adversarial renaming), and measured its benefit over a clean-code (L0) control:

| evaluated on | benefit over the control | CI95 | significant |
|---|---|---|---|
| **L1b** (the condition trained) | **+16.2 pts** | [+4.7, +28.5] | yes |
| L1r (same family) | +8.1 | [−1.0, +18.4] | no |
| L2 (same family) | +0.0 | [−8.4, +8.1] | no |
| S1 (other family) | +4.0 | [−1.2, +10.1] | no |
| S2 (other family) | +4.0 | [−4.4, +12.6] | no |
| **H1** (held out) | **−3.0** | [−10.5, +3.9] | no |

That is a memorization profile: a spike on the trained condition, nothing anywhere else. But it is
**one row of a matrix**. Two very different worlds produce it:

- **(a) A property of the regime.** Every adapter spikes on its own condition and transfers nowhere.
  LoRA on output prediction learns condition-specific tricks, full stop.
- **(b) A property of L1b.** Adversarial renaming happens to be an isolated skill, while (say) an
  S1-trained adapter *does* generalize to S2 and H1 — because flattening and MBA rewriting are both
  structural.

Distinguishing them requires the **full matrix**: train an adapter per condition, evaluate each on
every condition, and ask whether the diagonal-only pattern repeats.

**This is the RQ1 experiment**, run with the corrected control-relative metric that the pilot's L0
control forced (design doc §5.1, deviation §9.9).

---

## 2. What gets built and run

**Adapters** — per language: L0 (control), L1b, L1r, L2, S1, S2, × 2 seeds = 12.
Two languages (Python, JavaScript) ⇒ **24 adapters**.

**Evaluation** — each adapter on all 7 conditions (L0, L1b, L1r, L2, S1, S2, H1) in its **own**
language (within-language matrix), plus the **other** language for the cross-language arm (H1b).

**The quantity.** For train condition *i* and eval condition *j*:

> `Δ_ij = acc_j(tuned_i) − acc_j(tuned_L0)`

what training on *obfuscated* condition *i* buys on *j*, over training on *clean* code. The L0 row is
0 by construction; 5 train × 7 eval = **35 cells per language**.

**Cell relation classes** (the unit the hypotheses are actually about):

| class | cells | definition |
|---|---|---|
| `self` | 5 | i == j |
| `same_family` | 8 | i ≠ j, both identifier {L1b,L1r,L2} or both structural {S1,S2} |
| `cross_family` | 12 | identifier ↔ structural |
| `held_out` | 5 | j == H1 |
| `clean` | 5 | j == L0 |

---

## 3. Pre-registered hypotheses

**H-grad (primary).** The control-relative benefit is ordered
`self > same_family > cross_family ≈ held_out ≈ 0`.
*Memorization* ⇒ the ordering holds and the last two classes are statistically **equivalent to zero**.
*Invariance* ⇒ `held_out` is positive with a CI excluding zero.

**H-self.** Δ(`self`) > 0 with CI excluding 0 — the regime learns *something* condition-specific.
(The pilot supports this for L1b; this generalizes it.)

**H-family.** Δ(`same_family`) > Δ(`cross_family`) — transfer, where it exists, respects the
identifier/structural boundary.

**H1b (cross-language).** Within-language Δ exceeds cross-language Δ within each relation class.

**Critically:** "does not generalize" is an *acceptance of the null*, so `cross_family` and
`held_out` must pass an **equivalence test**, not merely fail a significance test. A non-significant
result with a wide CI is *inconclusive*, and will be reported as such.

---

## 4. Statistical analysis

Fitted in the existing R stack (`stats/R/`, glmmTMB + emmeans + DHARMa, `add_fdr()` helper).

### 4.1 Model

```r
glmmTMB(correct ~ train_cond * eval_cond * language +
          (1 | snippet_id) + (1 | snippet_id:eval_cond) +
          (1 | item_id) + (1 | adapter_id),
        family = binomial())
```

Reference level `train_cond = "L0"`, so **Δ_ij is the interaction contrast** (train_i − train_L0)
within eval_j. `adapter_id` (= condition × seed × language) carries seed as a *random* effect, which
is what makes claims generalize to a new seed rather than to these two. `snippet_id:eval_cond`
absorbs program × obfuscation difficulty, the dominant nuisance in a paired design.

Fit on the logit scale (correct likelihood for binary data with clustering); **report in accuracy
points** via `regrid = "response"`. A linear-probability sensitivity fit must agree in sign.

### 4.2 Contrasts

```r
emm <- emmeans(m, ~ train_cond | eval_cond * language, regrid = "response")
d   <- contrast(emm, "trt.vs.ctrl", ref = "L0")     # the 35 Δ_ij
cls <- contrast(d, method = class_weights)          # 5 relation-class means
```

Pooling cells into relation classes is far more powerful than 35 pairwise tests, and the classes are
what the hypotheses are stated over. Second-order contrasts on the fitted grid preserve the paired
covariance structure.

### 4.3 Equivalence

Margin, fixed **before** seeing results:

> `EQ_MARGIN_PTS = max(3, 2 × sd_seed)` where `sd_seed` is the seed-to-seed spread of Δ for the L0 control.

Justified as a floor from *control noise*: below it, an apparent transfer cannot be distinguished
from adapter idiosyncrasy. Deriving it from the pilot's +16.2 self-effect would anchor on a single
noisy cell instead. Secondary anchor: equivalence at Transfer Ratio ≤ 0.25 (Δ_class / Δ_self).

TOST via `test(cls, delta = EQ_MARGIN_PTS, side = "equivalence")`. Each class gets a **2×2 verdict**:

| | equivalent | not equivalent |
|---|---|---|
| **significant** | trivial effect | **generalizes** |
| **not significant** | **null accepted** | inconclusive (underpowered) |

H-grad is supported only if `cross_family` and `held_out` land in *null accepted*.

> ⚠️ Power note: for `held_out` (5 cells, and H1 covers only ~68% of programs) the projected 90% CI
> half-width is ~2.9 pts against a 3-pt margin — **marginal**. Pre-register a 4-pt margin for
> `held_out` specifically, or expand H1 program coverage. Do not decide this after seeing the data.

### 4.4 Multiplicity, ordering, cross-language

- **Two BH families, corrected separately**: (A) confirmatory — the 5 relation-class contrasts;
  (B) descriptive — the 35 per-cell Δ_ij. Not pooled: B decomposes A, and pooling would dilute the
  confirmatory tests. TOST p-values are corrected within the same family as their NHST partner.
- **Ordering** via fixed-sequence (closed) testing, one-sided, no correction while it holds:
  self > same_family, then same_family > cross_family, then cross_family ≈ held_out by TOST. Plus an
  ordered trend contrast (weights 3, 1, −1, −3) and a distribution-free Jonckheere–Terpstra on
  per-program Δ.
- **Cross-language** at class level (cell level would separate): `relation * same_lang * eval_lang`,
  with the control being the L0 adapter *of the same training language* — otherwise language
  confounds Δ. H1b is the difference-in-differences, its own BH family.

### 4.5 Detectability

At ~350 held-out programs × 3 items, program ICC ≈ 0.5, paired discordance ≈ 0.20:

| quantity | SE | MDE at 80% power |
|---|---|---|
| single cell Δ_ij (items only) | ~1.9 pts | ~5.5 pts |
| single cell, with seed variance (2 seeds) | ~2.8 pts | **~7.8 pts** |
| pooled `cross_family` (12 cells) | ~1.2 pts | **~3.3 pts** |
| pooled `held_out` (5 cells, 68% coverage) | ~1.8 pts | ~5.0 pts |

Seed variance dominates per-cell precision — which is exactly why the confirmatory claims are the
pooled classes and per-cell Δ_ij are descriptive. Confirm by parametric simulation from the fitted
variance components before trusting the equivalence verdicts.

---

## 5. Data: a clean three-way split

The pilot's binding constraint was **23 common-subset programs**, which cannot resolve the ±8 pt
effects under test. Fix: re-split the 2,231-program corpus into **train / val / test-programs**.

| split | ~programs | used for |
|---|---|---|
| train | 1,670 (75%) | adapter training |
| val | 110 (5%) | checkpoint selection only |
| **test-programs** | **450 (20%)** | **evaluation only — never trained on, never selected on** |

Why not reuse the existing 111-program val split: checkpoint selection already used those programs on
each adapter's *own* training condition, which biases the diagonal cell upward — and the diagonal is
the effect under test.

This gives ~450 × 3 ≈ 1,350 items per cell, versus 99 today. After S1 (~74% coverage) and H1 (~68%)
attrition, the all-conditions common subset should be ~300 programs — **13× the pilot**.

**Consequence:** L0 and L1b must be retrained, since they saw programs that are now test-programs
(~80 min). The ICSE 70-program set is retained as the **secondary, human-comparable** eval.

**JavaScript corpus** does not exist yet. Local `humaneval_x_js_full.json` gives ~150 programs;
CruxEval-X JS (800) and MultiPL-E mbpp-js (~400) need HuggingFace downloads. **Verify availability
first** — if they fail, the fallback is execution-gated Python→JS transpilation, with a `provenance`
covariate tested in the GLMM. Do not proceed to JS training on ~150 programs; report the shortfall
instead.

---

## 6. Build order

Infrastructure gaps found by exploration, in dependency order:

1. **`scripts/build_manifest.py`** — the grid→job-file expander. `sched/worker.py` and
   `scripts/launch_workers.sh` already work (filesystem queue, atomic claim, idle-GPU check); only
   the expander is missing, though `README.md` already documents it.
2. **Fix `expand_over: train_conditions`** in `eval_vllm.SystemSpec.from_config` — it is currently
   dropped silently, so `configs/eval/grid_v1.yaml` would evaluate *base weights mislabeled as
   per_type*. This is a live bug that would silently corrupt the whole matrix.
3. **Three-way split** in `scripts/02_build_corpus.py` + `configs/data.yaml`; emit held-out-program
   eval items (new tree + a source knob in `data.eval_variants_path`).
4. **H1 for held-out programs** — new quarantine subset via `scripts/gen_h1_quarantined.py`,
   with its own `ACCESS_LOG.md` entry.
5. **Control-relative matrix in `transfer.py`** — add a `control_train_cond` parameter. The i×j loop
   already exists; generalize the contrast out of `pilot.py`, which hardcodes `train_cond = "L1b"`.
6. **JS corpus** (§5), gated on dataset availability.
7. **Per-condition train configs** — 6 per language, each `_extends: _base_lora.yaml`; seeds via the
   existing `--seed` flag.
8. **R analysis** — `04_rq1_control_relative.R`: the §4 model, class contrasts, TOST, ordering tests.
   Watch the factor-level trap in `00_ingest.R` (unknown `train_cond` tags silently become `NA`).

Then: train (24 adapters) → ckpt-select → eval within-language → eval cross-language → analyze.

**Compute** (1.5B, 2 GPUs): training ~14 GPU-h, checkpoint selection ~1, within-language eval ~14,
cross-language eval ~6 ⇒ **~35 GPU-h ≈ 1–2 days**. Cross-language eval is seed-1-only to control cost.

---

## 7. What each outcome would mean

| result | reading |
|---|---|
| Ordering holds; `cross_family` and `held_out` **equivalent to zero** | **Memorization confirmed as a regime property.** LoRA on output prediction buys condition-specific skill that does not transfer. The strongest form of the paper's negative result, and it makes RQ2 (routing/modularity) the natural response — if adapters don't generalize, you need to pick the right one. |
| `held_out` **positive**, CI excludes 0, for some train conditions | **Partial invariance**, and the identity of those conditions is the finding. Most likely candidates are the structural adapters, since H1's MBA rewriting is arithmetic-structural rather than identifier-level. |
| Ordering holds but classes are **inconclusive** (wide CIs) | Underpowered. Report honestly; expand programs or seeds rather than claiming a null. |
| `self` itself is **not** significant across conditions | The pilot's +16.2 was L1b-specific or noise. Would undercut the premise that any obfuscation-specific learning happens, and sends us back to the training recipe. |

Every one of these is publishable. The design's job is to make them distinguishable, which is what
the equivalence testing and the 13× program increase are for.

---

## 8. Risks

| risk | mitigation |
|---|---|
| JS corpus too small (~150 curated) | Verify HF availability *first*; fall back to execution-gated transpilation with a provenance covariate, or report JS at reduced scale rather than training on 150 programs |
| Seed variance swamps per-cell effects (MDE ~7.8 pts) | Confirmatory claims are pooled classes only; per-cell Δ_ij explicitly descriptive; report σ_adapter / Δ_self |
| Control adapter idiosyncrasy shifts every Δ | Re-anchor the whole analysis on the untuned base as a sensitivity check — the class *ordering* must survive both anchorings |
| Unequal coverage (S1 74%, H1 68%) biases pooling | Primary analysis on the all-conditions common subset; report surviving n; sensitivity on full per-condition sets |
| Ceiling/floor separation in extreme cells | Per-cell flags for acc > 0.95 or < 0.05; points scale primary; DHARMa quantile checks |
| `expand_over` bug silently evaluates base weights | Fixed in build step 2; `assert_adapter_effective` already fails a cell whose outputs are byte-identical to base |

---

## 9. Ledger updates on completion

- `docs/CHECKLIST.md`: resolve **H1a** (family structure), **H1b** (cross-language), and the revised
  **H1c-rev**; add H-grad, H-self, H-family with their verdicts.
- New log thread entries under `log/transfer/`.
- `docs/design_doc_v0.1.md` §9 if any further design deviation is forced.
