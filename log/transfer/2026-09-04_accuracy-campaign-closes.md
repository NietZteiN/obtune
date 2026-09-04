### Target Date: 2026-09-04 (Accuracy campaign closes: augmentation null, data scale null, 13B +3.4)

Second entry of the day; the first (`2026-09-04_self-consistency-and-seed-band.md`) covered W1 and
the seed band. This one closes W2 (variant augmentation), W3 (split-frozen data scale) and W4
(CodeLlama-13b). Same discipline throughout: trainable grid only (`eval_source: heldout`, Grid A,
six conditions, 557 programs / 9,582 items), program-cluster bootstrap B=2000 seed 17, **H1 not read,
`final_eval` unspent**. All CodeLlama-7b unless marked 13B.

- **Hypotheses / what we're testing:**
  - **H-aug (W2):** invariance is under-taught because every program shows each transform on ONE
    surface. Training on four independent surfaces per program (canonical + re-seeded builders
    101/202/303 for the randomised transforms L1b/L1r/S1/S2; L0/L2 are deterministic) teaches the
    equivalence class rather than the instance. CONFIRM if `mono_aug − mono_all` > 0 with an interval
    excluding zero; REFUTE if it ties. Confound named before running: the aug mix is skewed to the
    randomised conditions (L0 = 4,689 of 79,167 rows = 6 %).
  - **H-scale (W3):** the corpus (1,563 train programs, tier 1 only) is the bottleneck. Adding
    tier-2/3 programs (mbpp, CodeSearchNet) as train-only, with the canonical val/test frozen, moves
    both `tuned_L0` and `mono_all`. CONFIRM if `tuned_L0_scale − tuned_L0` or `mono_scale − mono_all`
    excludes zero upward; REFUTE if both tie. Prior: `mono_all`'s 5.7× rows bought +0.11 pt.
  - **H-13B (W4):** the Qwen 1.5B→7B scale trend holds for CodeLlama: 13B lifts every system, and the
    `mono_all` = `tuned_L0` tie either persists (scale lifts the ceiling) or opens (scale lets breadth
    pay). Two-sided; the prediction recorded in the scratchpad was "cheapest absolute win if the
    trend holds".
- **Setup:**
  - W2: `05_build_variants.py --seed {101,202,303} --out-tag s<seed>` (jobs 376093/4/5; surfaces
    verified distinct per seed), `06_emit_pairs.py --aug-tag s<seed>` → `data/train/pairs_aug/`,
    4-part item ids `pid::cond::i::aug-<tag>`. `configs/train/mono_aug_generic_py.yaml`
    (`augment_tags: [s101, s202, s303]`, `train_size: null`, epochs 2, seed 17,
    `adapter_root: runs/adapters_aug`). Loss-mask gate `inspect_batch.py` PASS on `dev` (376106).
    Train **376282** (7 h 16 m, 2,472 steps, 79,167 rows, train_loss 0.085, truncation 0.14 %),
    ckpt-select **376283** (best `checkpoint-1236` = epoch 1, val 0.3678; epoch 2 0.3683, flat),
    eval **376284** (`configs/eval/aug_scale_generic.yaml --systems mono_aug`).
  - W3: `02_build_corpus.py --extend-frozen scale` (mbpp 959 raw → 747, CSN 161k functions → 4,921
    with signature seeds → 162 after dedup; **912 new programs, +58 %**; canonical
    `data/splits/python.json` untouched, verified), `05_build_variants.py --base-root
    data/train/base_scale --aug-tag scale`, `06_emit_pairs.py --aug-tag scale` (15,540 pairs). Loss-mask
    gate PASS (376126). `L0_scale`: train **376288** (33 min, 348 steps, 7,425 rows, loss 0.394),
    ckpt **376289** (best `checkpoint-348`, val 0.4024), eval **376365** (376290 died on my
    `arch: single` typo, fixed b21525b). `mono_scale`: train **376285** (5 h 16 m, 1,986 steps,
    42,381 rows, loss 0.121), ckpt **376286** (best `checkpoint-662` = epoch 1, val 0.3631, declining
    after), eval **376287**.
  - W4: `codellama-13b` downloaded; `grid_py_L0` / `mono_generic_py` with `--model codellama-13b`.
    `tr13_L0` (2,281 s, loss 0.465), `ck13_L0` (best `checkpoint-222`, val 0.4505); `tr13_mono`
    **376097** (5 h 10 m, 1,257 steps, loss 0.134), `ck13_mono` **376099** (best `checkpoint-838`,
    val 0.4121), eval **376100** (`rq2_generic --model codellama-13b --systems base,tuned_L0,mono_all`).
  - Analysis: `scripts/analysis/26_campaign_arms.py` → `results/analysis/campaign_2026-09-03.json`;
    13B contrasts (same `contrast()` helper, cross-model joins on `item_id`) →
    `results/analysis/campaign_13b_2026-09-04.json`.
- **Results (pts, 95 % CI):**

  | arm | reference | arm acc | Δ pooled | per-condition |
  |---|---|---|---|---|
  | `mono_aug` | `mono_all` | 0.3934 | **+0.17 [−1.14, +1.38]** | L0 −0.84, L1b +0.60, L1r −0.18, L2 +1.50 [−0.12, +3.05], S1 +0.64, S2 −0.60 — all span 0 |
  | `mono_aug` | `tuned_L0` | 0.3934 | +0.73 [−0.69, +2.24] | L0 −2.57 [−4.55, −0.54], L1b +3.02 [+0.84, +5.13], rest null |
  | `tuned_L0_scale` | `tuned_L0` | 0.3842 | **−0.20 [−1.00, +0.61]** | all six span 0 (L0 −0.66 … S1 +0.56) |
  | `mono_scale` | `mono_all` | 0.3991 | **+0.73 [−0.66, +2.10]** | all six span 0 (L1b +1.51, L1r +1.26, L2 +1.08 largest) |
  | `mono_scale` | `tuned_L0` | 0.3991 | +1.29 [−0.14, +2.69] | L0 −1.98 [−3.90, −0.24], L1b +3.92 [+1.75, +6.03], S2 +2.34 [+0.48, +4.26] |
  | `base` 13B | `base` 7B | 0.2211 | +1.54 [+0.10, +2.99] | S1 +4.49, L2 +2.63, L1b +2.47 exclude 0; L0 −0.48, S2 −0.90 null |
  | `tuned_L0` 13B | `tuned_L0` 7B | 0.4201 | **+3.39 [+1.93, +4.89]** | +2.57 … +4.07, S1's lower bound at +0.00, the other five exclude 0 |
  | `mono_all` 13B | `mono_all` 7B | 0.4278 | **+3.60 [+1.83, +5.23]** | +2.97 … +4.07, all six exclude 0 |
  | `mono_all` 13B | `tuned_L0` 13B | 0.4278 | +0.77 [−0.71, +2.20] | L0 −2.34 [−4.31, −0.30], L1b +2.71 [+0.60, +4.83], S2 +1.98 [−0.30, +4.14], rest null |
  | `tuned_L0` 13B | `base` 13B | — | +19.89 [+17.56, +22.18] | (7B: +18.0) |

  - Pooled format_fail: `mono_aug` **0.0058** (lowest of any system in the corpus), `mono_all` 0.0077,
    `mono_scale` 0.0122, `tuned_L0_scale` 0.0168, `tuned_L0` 0.0272; 13B `base` 0.102 / `tuned_L0`
    0.016 / `mono_all` 0.011.
  - Val curves (checkpoint selection, n=1,917 val items for the six-condition adapters): `mono_all`
    0.359 / 0.367 / 0.367 over three epochs; `mono_aug` 0.368 / 0.368 over two; `mono_scale`
    0.363 / 0.362 / 0.357. Three data regimes (26.8k, 42.4k, 79.2k rows), one ceiling.
- **What worked / hypothesis verdict:**
  - **H-aug — REFUTED.** `mono_aug − mono_all` +0.17 [−1.14, +1.38]. Four surfaces per program taught
    exactly what one surface taught; the only thing more diversity bought was format (0.0058
    format_fail, the corpus minimum). The mix-skew confound cuts the other way — it should have
    *hurt* L0 relative to `mono_all`, and L0 is −0.84 [−2.40, +0.78], null. So the null is not an
    artefact of the mix.
  - **H-scale — REFUTED on both halves.** `tuned_L0_scale − tuned_L0` −0.20 [−1.00, +0.61];
    `mono_scale − mono_all` +0.73 [−0.66, +2.10], inside the seed band (s42 sat +0.77 above `tuned_L0`
    with no extra data). The corpus is not the bottleneck at 7B, on clean code or on the mix.
  - **H-13B — SUPPORTED, and the tie persists.** +3.39 / +3.60 pts for the two adapters, positive
    on every condition; `base` moves +1.54, so tuning's gain over base is ~+20 at both scales.
    Scale lifts the tuned ceiling, not the tuning effect. And `mono_all − tuned_L0` at 13B is
    +0.77 [−0.71, +2.20] with the identical per-condition fingerprint seen at every 7B seed.
- **Observations:**
  - **The campaign's aggregate finding is the fingerprint.** Across six independent six-condition
    adapters (`mono_all` s17/s42/s101, `mono_aug`, `mono_scale`, 13B `mono_all`) the contrast against
    the clean-code control has the same shape every time: **L0 costs 1.4–2.6 pts (five of six
    exclude zero), L1b gains 1.4–3.9 pts (five of six exclude zero), L1r/L2/S1 null, S2 +1–2 and
    usually null.** Breadth of obfuscation exposure buys the adversarially-renamed condition and
    pays for it on clean code; nothing about seed, data quantity, surface diversity or model scale
    changes that trade. Pooled, the two cancel to a tie every time.
  - The three levers that touched the training data (seed, ×3 surfaces, +58 % programs) all
    landed within the seed band; the one that touched the model did not. For the writeup: at this
    corpus size the 7B adapters are data-saturated, and the remaining headroom on the trainable
    grid is a model-capacity question, not a data question.
  - `mono_scale` peaked at epoch 1 and `mono_aug` was flat from epoch 1 — more rows are converting
    to overfitting or to nothing, not to accuracy. Consistent with the saturation reading.
  - Silent-failure checks: truncation 0.14 % / 0.08 % / 0.04 % / 0.12 %; loss-mask gate passed on
    both new pair sets; `arch: single` crash was a config literal error on row 1, no partial cell.
    H1 marker scan passed on all rebuilt manifests (207k + aug + scale rows).
  - **Not done, and why:** no `mono_aug` / `mono_scale` / 13B read on H1 — the campaign found no
    7B lever, and 13B on H1 would spend the final read on a "bigger model does better" result
    that the trainable grid already shows. If the human wants the 13B `tuned_L0`-vs-`mono_all`
    ordering on H1 it is the one candidate for `final_eval`; my recommendation is to hold it.
- **New questions / new hypotheses:**
  - **H-L1b-L0-trade:** the L0 cost and the L1b gain are the same items — breadth training teaches
    "distrust identifiers", which helps under adversarial renaming and hurts when names are
    honest. Testable from existing cells: partition items by whether `tuned_L0` gets the L0
    variant right, and check whether `mono_all`'s L1b gains concentrate on the programs where it
    loses L0. No GPU needed.
  - **H-saturation:** a data-scale sweep *downward* (50 %, 25 % of the corpus) would locate where
    the 7B curve bends; if 25 % already ties, the corpus could be a quarter the size. Cheap
    (`train_size`), not scheduled.
- **Next Steps:**
  - Master-results artifact: fill the `mono_aug` row (done in the same commit).
  - Recompute MASTER_REPORT CodeLlama tables to include the 13B column (pending, unapproved).
  - H-L1b-L0-trade on existing cells if the human wants it.
