### Target Date: 2026-09-10 (H-gate-format CONFIRMED: the pre-registered gate rule would have discarded the strongest new model in the panel)
- **Hypotheses / what we're testing:** **H-gate-format**, frozen in `CLAUDE_SCRATCHPAD.md` and
  committed as `be12802` **before `tuned_L0(gemma3-12b)` existed**: a base model's `format_fail`
  predicts nothing about its tuned ceiling when the failures are a single learnable convention.
  CONFIRMED iff `tuned_L0(gemma3-12b)` on L0 ≥ **0.4275**; REFUTED iff ≤ **0.3335** (its own untuned
  raw rate); INCONCLUSIVE between. Tuned `format_fail` reported beside it, since the mechanism under
  test is that tuning teaches the quoting convention.
- **Setup:** chain 388535 (loss-mask gate, PASS) → 388536 (train, 222 steps, 35.8 min, `train_loss`
  0.386, truncation **0.06 %** at 2,048) → 388537 (ckpt-select, `checkpoint-74` — epoch 1 — at
  0.4834 on the 333-item L0 val split, all four checkpoints within 0.3 pts) → 388538 (eval,
  `rq2_generic`, `base` and `tuned_L0` on the six trainable conditions). `configs/train/grid_py_L0_gemma3.yaml`,
  8 × 8 per `models.yaml`. No X1, no H1.
- **Results:**

  | system | L0 | L1b | L1r | L2 | S1 | S2 |
  |---|---:|---:|---:|---:|---:|---:|
  | `base` acc | 0.3335 | 0.2630 | 0.2731 | 0.2689 | 0.2678 | 0.2903 |
  | `base` `format_fail` | 0.2796 | 0.2865 | 0.2844 | 0.2814 | 0.2719 | 0.2867 |
  | **`tuned_L0` acc** | **0.5180** | 0.4367 | 0.4611 | 0.4569 | 0.4555 | 0.4985 |
  | **`tuned_L0` `format_fail`** | **0.0096** | 0.0097 | 0.0096 | 0.0108 | 0.0128 | 0.0078 |

  `tuned_L0` on L0, same phase and same 1,670 items, program-clustered bootstrap (2,000 resamples):

  | contrast | Δ pts [95 % CI] |
  |---|---:|
  | `gemma3-12b − codellama-34b` | **−0.42 [−2.75, +1.86]** — indistinguishable |
  | `gemma3-12b − codellama-13b` | **+4.91 [+2.46, +7.25]*** |
  | `gemma3-12b − codellama-7b` | **+8.86 [+6.64, +11.03]*** |
  | `gemma3-12b` tuned − its own base | **+18.44 [+15.52, +21.38]** |

- **What worked / hypothesis verdict:** **H-gate-format — CONFIRMED, and not marginally.**
  0.5180 against a 0.4275 threshold, +9.1 points clear of it. `format_fail` collapsed
  **0.2796 → 0.0096, a 29-fold reduction**, which is the mechanism the hypothesis named: one epoch
  of tuning taught the quoting convention, and the flat checkpoint curve (epoch 1 already at the
  ceiling, three epochs within 0.3 pts) is what learning a punctuation habit rather than a
  capability looks like.
- **Observations — what this costs the method, stated plainly:**
  - **The registered gate rule would have thrown away the best new model in the panel.** A 12B model
    ties CodeLlama-34B on clean code (−0.42, interval spanning zero) at roughly a third of the
    parameters, and beats the incumbent 7B by +8.86*. The rule rejected it for a defect that one
    epoch removes.
  - **The rule was not stupid, and this is not hindsight.** It was written from the Llama-3.1 gate
    (2026-09-04), where a model's entire apparent margin *was* format and it was weaker conditional
    on a well-formed answer. That is a real failure mode and the rule catches it. What the rule
    cannot do is distinguish it from *this* case — a model whose margin survives the format
    correction. `format_fail` alone does not separate them; the composition of the failures does,
    and the gate never looked at it.
  - **The fix is a two-part gate, and it is cheap.** `format_fail` ≤ 0.15 **or** (failures are
    dominated by a single recoverable convention **and** conditional accuracy clears the incumbent).
    The diagnostic that settles it — what fraction of unparsable outputs are the gold value modulo a
    fixed transformation — is ~20 lines over cells the gate already writes, needs no GPU, and would
    have flagged Gemma-3 at 34.8 % and CodeGemma at 31.8 % the moment their gates landed.
  - **`codegemma-7b`'s NO-GO is now suspect on the same grounds** (ff 0.204, 31.8 % of failures
    unquoted, same Google lineage). Its probe is the obvious next call, and it is ~25 min of GPU.
  - `granite31-8b` passed the gate as written and needs no revisiting; `starcoder2-15b`'s NO-GO is a
    *different* mechanism (its template's own persona under merged rendering) and is not addressed
    by any of this.
  - Not re-specified after the fact: Gemma-3's original gate verdict stands in the record as NO-GO.
    The probe tested the rule, not the model, and that is what it decided.
- **New questions / new hypotheses:** **H-gate-format-lineage** (opened): the same probe on
  `codegemma-7b` confirms if `tuned_L0(codegemma-7b)` on L0 ≥ `tuned_L0(codellama-7b)` = 0.4293,
  refutes if ≤ its untuned 0.2365. One training run, ~25 min.
- **Next Steps:** decisions for the human — (1) does Gemma-3 rejoin the panel on this evidence, and
  under what recorded justification; (2) run the CodeGemma probe; (3) adopt the two-part gate for
  the remaining and any future candidate. Nothing is re-gated or re-labelled until those are taken.
