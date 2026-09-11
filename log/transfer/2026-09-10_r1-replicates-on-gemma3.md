### Target Date: 2026-09-10 (R1 — breadth's unseen-family tax replicates on Gemma-3-12B, the first model outside the Meta lineage)
- **Hypotheses / what we're testing:** **R1**, frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  `d63340c` **before `ev_panel_g3` produced a single cell**: `mono_all − tuned_L0` @ X1,
  REPLICATED iff ci_hi < 0, REFUTED iff ci_lo > 0, else INCONCLUSIVE. Published values on the
  existing panel: −3.79 (CodeLlama-7B) / −4.28 (13B) / −2.64 (34B) / −2.88 (Llama-3.1-8B).
- **Setup:** `configs/eval/panel_core.yaml` on `gemma3-12b` (job 389609, 13 min 25 s), 5 systems ×
  7 conditions, held-out items, strict exact match. Program-clustered bootstrap, 2,000 resamples,
  seed 17, n = 1,214 items over 405 programs on X1. No H1.
- **Results:**

  | system | L0 | L1b | L1r | L2 | S1 | S2 | X1 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | `base` | 0.3335 | 0.2618 | 0.2731 | 0.2689 | 0.2686 | 0.2897 | 0.1524 |
  | `tuned_L0` | 0.5198 | 0.4409 | 0.4587 | 0.4563 | 0.4563 | 0.4997 | **0.3097** |
  | `tuned_X1` | 0.5060 | 0.4023 | 0.4473 | 0.4407 | 0.4523 | 0.4889 | **0.3756** |
  | `mono_all` | 0.5072 | 0.4753 | 0.4635 | 0.4713 | 0.4571 | 0.5027 | **0.2628** |

  | contrast | Δ pts [95 % CI] | verdict |
  |---|---:|---|
  | **R1** `mono_all − tuned_L0` @ X1 | **−4.70 [−6.93, −2.55]** | **REPLICATED** |
  | `tuned_X1 − tuned_L0` @ X1 | **+6.59 [+4.20, +9.14]** | family exposure helps where breadth hurts |
  | `tuned_L0 − base` @ X1 | +15.73 [+12.76, +18.72] | tuning works, as everywhere |
  | `mono_all − tuned_L0` @ L0 | −1.26 [−3.24, +0.72] | same sign as CodeLlama's −1.74/−2.34/−2.63, not clearing zero here |

- **What worked / hypothesis verdict:** **R1 REPLICATED.** −4.70 sits inside the range of the four
  published values and its interval excludes zero. Breadth's unseen-family tax is **not a CodeLlama
  property**: it survives a change of lineage, tokenizer, pretraining corpus and chat template.
  This is the first genuinely independent test of the paper's central dissociation.
- **Observations:**
  - **The RQ2 side reproduces too, and was not registered.** `tuned_X1 − tuned_L0` @ X1 is +6.59
    here against +4.86 on CodeLlama-7b — training on the held-out family's *sibling* helps by about
    as much as breadth hurts, on a model that shares nothing with the panel it was measured on.
    Reported as observed, not verdicted; it was not part of R1–R4.
  - **The clean-code cost does not clear zero on this model** (−1.26 [−3.24, +0.72]) where it does
    at 13B/34B on CodeLlama. One model, one seed; reported as the weaker half of breadth's
    fingerprint rather than as a failure.
  - **R2 and R3 are NOT read from this grid.** Both involve `cons_lam3`, and this grid's
    `cons_lam3` row was produced by an arm that turned out to be plain SFT
    (`log/setup/2026-09-10_cons-arms-ran-as-plain-sft.md`). Those cells are quarantined and the
    arms are retraining. Had the incident gone unnoticed, R2 would have read **exactly 0.0** and
    been reported as a failed replication of the paper's one positive method result.
  - Coverage note: X1 is 1,214 items over 405 programs here against 1,215/405 on CodeLlama — the
    same item set, so the comparison is like-for-like.
- **New questions / new hypotheses:** none. R2/R3 pend the retrained arms; R4 needs the ladder
  pooled across models and is not a single-model read.
- **Next Steps:** the four consistency arms are retraining with `-m obtune.objectives train --lam 3`
  and `kl_loss` confirmed present in the logs; when they land, re-run `panel_core` for each model
  and read R2/R3.
