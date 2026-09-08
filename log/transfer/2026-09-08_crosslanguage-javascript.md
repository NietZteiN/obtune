### Target Date: 2026-09-08 (E13 — the paper's Python-only scope tested: consistency replicates in JavaScript and *amplifies*; breadth's stacking gain does **not** replicate cleanly)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  **`8da96b4`** before any JS config was written. **H-xlang-stack** `mono_all − tuned_L0` pooled over
  the six JS composites, **H-xlang-cons-seen** `cons_lam3 − tuned_L0` over the five obfuscated seen
  conditions, **H-xlang-cons-stack** `cons_lam3 − mono_all` over the composites — each ci_lo > 0
  CONFIRMED / ci_hi < 0 REFUTED / else INCONCLUSIVE. **H-xlang-L0** `mono_all − tuned_L0` @ L0 —
  ci_hi < 0 CONFIRMED / inside ±1.0 REFUTED / else INCONCLUSIVE. **H-xlang-volume** REPORTED, never
  verdicted.
- **Why this was possible at all.** The paper is Python-only because `node` is not installed on juno.
  That blocks **regenerating** the JavaScript corpus, not **using** it, and the corpus transferred
  intact. Checked before a single config was written: the whole data tree passes
  `scripts/check_manifest.py` (SHA manifests **and** the H1-marker content scan); the JS banks hold
  8,490 train-split rows over 473 programs and 504 heldout items per condition plus all six depth-2
  composites; sequence lengths max **1,247 tokens** so the inherited 2,048 window truncates nothing
  (measured, not assumed — 0.00 % over). **Split disjointness verified explicitly** (§4 item 1): the
  pair files carry all three splits, `train` is 473 programs, `test` is 168, and the 168 are exactly
  the heldout eval set with **zero** overlap against train or val.
- **Setup:** `tr_js_L0` **383164** → `ck_js_L0` → `tr_js_mono` **383166** / `tr_js_cons` **383168**
  (teacher = the **JavaScript** clean-code adapter, not the Python one — E4 showed the teacher is the
  ingredient, so a Python teacher would have been a different experiment) → `ck_*` →
  `ev_crosslang_js` **383170** → `an_crosslang` **383171**
  (`results/analysis/pipeline/crosslang_codellama7b.json`). CodeLlama-7b, seed 17, 168 programs.
  **No unseen-family column**: X1 is Python-only by construction and no JS X1 generator exists, so
  the "cost" side of RQ1′ is untested here and nothing below may be quoted for it. No H1.
- **Results (accuracy, JavaScript):**

  | system | L0 | L1b | L1r | L2 | S1 | S2 |
  |---|---:|---:|---:|---:|---:|---:|
  | `base` | 0.3591 | 0.2639 | 0.3313 | 0.3194 | 0.3214 | 0.2202 |
  | `tuned_L0` | 0.5317 | 0.4742 | 0.5179 | 0.5298 | 0.5190 | 0.3532 |
  | `mono_all` | 0.5000 | 0.5000 | 0.4960 | 0.4940 | 0.5090 | 0.5079 |
  | `cons_lam3` | **0.5655** | **0.5556** | **0.5556** | **0.5437** | **0.5489** | **0.5575** |

  | system | C_L1b_S1 | C_L1r_S1 | C_S1_L1r | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
  |---|---:|---:|---:|---:|---:|---:|
  | `tuned_L0` | 0.4411 | 0.4910 | 0.4950 | 0.4742 | 0.5119 | 0.3611 |
  | `mono_all` | 0.4810 | 0.4750 | 0.4790 | 0.5099 | 0.4802 | 0.5020 |
  | `cons_lam3` | **0.5190** | **0.5230** | **0.5389** | **0.5496** | **0.5357** | **0.5556** |

  Contrasts, pts [95 % CI], program-clustered bootstrap, n_prog = 168:
  - **H-xlang-stack INCONCLUSIVE.** `mono_all − tuned_L0` @ composites **+2.55** [−0.30, +5.31].
  - **H-xlang-cons-seen CONFIRMED.** `cons_lam3 − tuned_L0` @ seen5 **+7.35** [+4.93, +9.72].
  - **H-xlang-cons-stack CONFIRMED.** `cons_lam3 − mono_all` @ composites **+4.91** [+2.68, +7.29].
  - **H-xlang-L0 INCONCLUSIVE.** `mono_all − tuned_L0` @ L0 **−3.17** [−6.75, +0.20].
  - Also: `cons_lam3 − tuned_L0` @ composites +7.46 [+4.99, +10.08]; `mono_all − tuned_L0` @ seen5
    +2.26 [−0.48, +4.97]; `tuned_L0 − base` @ seen5 +18.75 [+15.24, +22.32].
- **What replicates, and more strongly than in Python.** `cons_lam3` is **the best arm on all twelve
  columns**, and its margins are roughly three times the Python ones: +7.35 over the clean-code arm
  on seen conditions (Python: +2.41), +4.91 over breadth on composites (Python: +1.27, 34B: +2.58).
  It is positive against breadth on **all six** composites individually (+3.79 to +5.99, every
  interval clearing zero). And a result with no Python counterpart: **`cons_lam3 − tuned_L0` @ L0 is
  +3.37 [+0.79, +5.95]** — in JavaScript the objective beats the clean-code specialist *on clean
  code*, where in Python it merely ties it (−0.48 n.s.). RQ3′ is not a CodeLlama-Python artifact.
- **What does not replicate, and it is the paper's RQ1′ headline.** Breadth's stacked-seen gain is
  **+2.55 with an interval spanning zero**, against Python's +3.49 / +2.90 / +3.05 at three scales.
  Worse for the claim than the pooled number suggests, the per-composite pattern is **heterogeneous
  in a way Python's never was**: three of the six are *negative* (`C_L1r_S1` −1.60, `C_S1_L1r` −1.60,
  `C_L1r_S3` −3.17) and the pooled figure is carried almost entirely by one composite,
  **`C_S4_S3` +14.09**, the only one whose interval clears zero. In Python all six were positive at
  every scale. So the honest statement is not "underpowered, same effect": it is **the JS
  composites do not show the Python shape**, and the one place breadth wins big is where the JS
  `tuned_L0` is unusually weak (`S2` 0.3532 and `C_S4_S3` 0.3611 against ~0.50 everywhere else).
- **H-xlang-volume — REPORTED, and the prediction on record was wrong.** Before the read I recorded
  that JS trains on 8,490 rows against Python's 26,841 (**32 %**, close to E12's quarter arm where
  breadth's taxes essentially vanished), and predicted **a smaller JS L0 cost**. Observed:
  **−3.17 against Python's −1.32** — the point estimate is more than twice as large, i.e. the
  opposite direction. The interval is wide and spans zero, and the pre-registration already said
  this comparison is confounded by the programs, the tokenizer and the per-language ladder surface,
  so this does not refute E12 — but the prediction it licensed did not come true and is reported as
  such. One independent corroboration of the volume story does survive, from the checkpoint selector
  rather than the accuracy: on Python both `tuned_L0` and `mono_all` peak at epoch 2 of 3, while on
  JavaScript `tuned_L0` peaks at epoch 2 and **`mono_all` peaks at epoch 1** — breadth overfits a
  third of the data a full epoch sooner.
- **Caveats.**
  1. **168 programs against Python's 557.** Intervals are ~1.7× wider, which is enough to make
     "INCONCLUSIVE" the expected verdict for a Python-sized effect — but does not explain three
     negative composites.
  2. **Cross-language magnitudes are not comparable**, and this run makes that concrete: the JS
     items are easier for this model (`tuned_L0` val accuracy 0.535 against Python's 0.408), and the
     JS ladder's per-condition difficulty profile differs (JS `tuned_L0` is far weaker on `S2` than
     on anything else, which Python's is not). Only signs and orderings transfer.
  3. **No unseen-family column**, so the half of RQ1′ that the paper's headline actually rests on —
     the tax — is **untested in JavaScript**. A JS X1 generator would need `node` and does not exist.
  4. Single seed, 7B only, `formatonly` not run in JS so there is no format floor for these numbers.
- **Next:** if the cross-language claim is to go in the paper as more than a robustness note, it
  needs (a) a second seed and (b) a JS X1, which needs a node toolchain — installable from
  nodejs.org without root, and now the only thing standing between this project and a complete
  second language. Docs: `docs/RQ_SUMMARY.md` §6, `docs/PAPER_EXPERIMENTS.md` E13,
  `MASTER_REPORT.md` §29.8.
