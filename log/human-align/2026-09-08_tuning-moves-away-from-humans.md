### Target Date: 2026-09-08 (E10 — the thread's first entry: fine-tuning moves the model **away** from human difficulty orderings, and the untuned model is the one that tracks people)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  **`4665e17`** before the eval was submitted. **H-human-base** (does the untuned model order items
  like people?): item-level Spearman ρ(base, human) over the 98 cells — ci_lo > 0 CONFIRMED,
  ci_hi < 0 REFUTED, else INCONCLUSIVE. **H-human-shift** (the charter's actual question): Δρ =
  ρ(`tuned_L0`) − ρ(`base`), paired on the same draws — ci_lo > 0 **TOWARD**, ci_hi < 0 **AWAY**,
  else NO DETECTABLE SHIFT; reported for `mono_all` and `cons_lam3`, **verdicted only for
  `tuned_L0`** (one arm, one rule). **H-human-tier**: condition level, REPORTED, never verdicted
  (n = 5). Gates nothing.
- **Why this thread was empty until today.** E10 has been "disabled, not pretended" since the paper
  plan was written, on the grounds that it needed the `tier_icse` items emitted and the Paper-2 item
  map, "a build task that has no script yet". The map was never missing:
  `data/human/paper2_graded.csv` holds **600 graded responses from 50 participants over 98 item
  cells**, and **all 98 match a legacy row**. Only the emitter was missing
  (`scripts/47_emit_icse_items.py`, written today; 320 of the 350 legacy rows parse, and the 30 that
  do not are LeetCode keyword-call rows **outside** the human set, so human coverage is 98/98).
- **Setup:** `ev_human_align_py` **383200** and `ev_human_align_js` **383195** →
  `48_human_align.py` (`results/analysis/pipeline/human_align_codellama7b.json`). CodeLlama-7b,
  `base` / `tuned_L0` / `mono_all` / `cons_lam3` on `T_L0…T_L3`, both languages (50 Python cells,
  48 JavaScript). Human accuracy per cell = share of that cell's responses graded `Correct`
  (6.1 responses per cell, min 5). Bootstrap clusters by **program** (20 of them), never by cell.
  Labels are `T_*` (`schema.TierCondition`), outside `AnyCondition`, never trainable. No H1.
- **Results — mean accuracy on the 98-cell human set:** human **0.368**, `tuned_L0` 0.337,
  `cons_lam3` 0.306, `mono_all` 0.296, `base` 0.276. Every arm is below the human mean, which is
  itself worth stating: on the only items where the comparison is licensed, this 7B model is not at
  human level.
- **Item-level Spearman ρ with human accuracy:**

  | arm | ρ [95 % CI] | Δρ vs base [95 % CI] | verdict |
  |---|---:|---:|---|
  | `base` | **+0.132** [−0.140, +0.381] | — | H-human-base **INCONCLUSIVE** |
  | `tuned_L0` | −0.171 [−0.406, +0.094] | **−0.303** [−0.575, −0.028] | **AWAY** |
  | `mono_all` | −0.043 [−0.276, +0.214] | −0.174 [−0.430, +0.059] | no detectable shift |
  | `cons_lam3` | −0.113 [−0.353, +0.140] | −0.244 [−0.520, +0.056] | no detectable shift |

  **H-human-shift: AWAY.** Fine-tuning on obfuscated output prediction moves the model's item
  difficulty ordering *away* from the human one. The three tuned arms all have the same sign; only
  `tuned_L0` was verdicted, per the frozen rule, and only its interval clears zero.
- **Condition level (REPORTED, never verdicted, n = 5) — and this is the clearer picture:**

  | | T_L0 | T_L1 | T_L1b | T_L2 | T_L3 | rank corr. with human |
  |---|---:|---:|---:|---:|---:|---:|
  | **human** | 0.406 | 0.399 | 0.382 | 0.341 | 0.315 | — |
  | `base` | 0.400 | 0.278 | 0.250 | 0.200 | 0.250 | **+0.82** |
  | `tuned_L0` | 0.350 | 0.333 | 0.250 | 0.300 | **0.450** | −0.10 |
  | `mono_all` | 0.300 | 0.222 | 0.300 | 0.250 | 0.400 | −0.41 |
  | `cons_lam3` | 0.300 | 0.222 | 0.300 | 0.250 | 0.450 | −0.41 |

  Human accuracy falls monotonically across the legacy ladder — people find each tier harder than
  the last. **`base` tracks that gradient (+0.82); every tuned arm inverts it**, and all three do
  their *best* on `T_L3`, the tier humans find hardest. The item-level and condition-level views
  agree, which is the main reason to believe the item-level number at this n.
- **Reading.** The secondary question in the charter was "does tuning move models toward or away from
  human difficulty orderings?" On the only rows where the comparison is licensed, the answer is
  **away** — and the mechanism the condition table suggests is that tuning buys exactly what humans
  do not have: fluency with the specific surface deformations of the ladder. A human's difficulty is
  driven by reading effort, which grows with the obfuscation tier; a tuned model's is driven by
  whether it has seen that deformation, which makes the heaviest tier no worse than the lightest.
  **This is a divergence result, and it is publishable as one** — it says the accuracy gains this
  project measures are not gains in anything that behaves like human comprehension.
- **Caveats, and they are substantial.**
  1. **Power.** 98 cells over 20 programs, with **one trial per cell** on the model side, so the
     model's per-cell accuracy is binary and ρ is estimated from a binary vector against a
     6-response human proportion. The one interval that clears zero does so at **−0.028**. This is a
     weak instrument and the result should be quoted with its interval, never as a bare ρ.
  2. **The design caps the power and cannot be fixed by more compute.** The human study used one
     input case per item; adding cases would change the item and break the byte-identical
     comparability that makes the comparison legal at all.
  3. **The registered grading-sensitivity check fires for one arm:** `tuned_L0`'s text-regrade is
     **+2.19 pts** above strict, over the 2-pt threshold, so by the frozen rule its strict number is
     reported as an **underestimate**. The registered check is also, on inspection, the wrong
     instrument — the pipeline already grades by canonicalising parsed output, so a text compare is
     *stricter* than the grader on string-valued golds. The instrument that answers the question:
     **71.7 % of `base`'s correct answers needed the grader's canonicalisation against 0 % for every
     tuned arm** — the study's spelling is handled upstream, and, incidentally, fine-tuning has
     taught the arms to emit canonical JSON natively. `base` also carries a **7.19 %** format-failure
     rate against 0.94–1.88 % for the tuned arms, so part of its accuracy deficit is formatting; ρ is
     about ordering rather than level, but a format failure is scored wrong and does enter the
     ordering.
  4. Legacy `tier_icse` semantics differ per language (`docs/TIER_MAPPING.md`), and the two languages
     are pooled here because neither half alone reaches 50 cells.
- **Next:** the Paper-3 (n = 73) study is on disk and, per CLAUDE.md, usable at **condition level
  only** — 6 items cannot support an item-level ρ, and saying so is part of the contribution. That
  is a half-day of analysis on existing data and would give the condition-level panel a second,
  independent human anchor. Docs: `docs/RQ_SUMMARY.md`, `docs/PAPER_EXPERIMENTS.md` E10 (claim C8,
  which has read "none — thread never started" since the plan was written).
