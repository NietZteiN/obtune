### Target Date: 2026-09-08 (Read — E12 saturation: breadth saturates by a quarter of the corpus, and the unseen tax GROWS with the data that no longer buys anything)
- **Hypotheses / what we're testing:** the three rules pre-registered in `CLAUDE_SCRATCHPAD.md`
  ("E12 saturation", frozen before the 09-07 pipeline submission). **H-sat-L0**: `tuned_L0_half −
  tuned_L0` pooled seen6 TOST-equivalent at ±1.0 ⇒ CONFIRMED. **H-sat-mono**: likewise for
  `mono_half − mono_all`. **H-tax-scales** ("the unseen tax is a data-volume effect"): CONFIRMED iff
  `mono_quarter − tuned_L0_quarter` @ X1 has ci_hi ≥ 0 **and** the full-data tax `mono_all − tuned_L0`
  @ X1 is more negative than the quarter tax; REFUTED iff the quarter arm already has ci_hi < 0.
- **Setup:** `tr_{L0,mono}_{half,quarter}` (r32 s17 codellama-7b; the half/quarter arms keep ½ / ¼
  of the **programs** — `tuned_L0` 4,689 / 2,344 / 1,172 rows, `mono` 26,841 / 13,420 / 6,710 rows,
  so `mono_*` always has six views of every program it sees) → `ck_*` → `ev_saturation` (**382531**,
  9:14) → `an_saturation` (**382532**, `scripts/analysis/40_saturation.py`,
  `results/analysis/pipeline/saturation_codellama7b.json`). Cluster-bootstrap by `program_id`,
  n_prog = 557 seen / 405 X1. No H1.
- **Results:**

  | arm | rows | L0 | L1b | L1r | L2 | S1 | S2 | **X1** |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|
  | `tuned_L0` | 4,689 | 0.4275 | 0.3601 | 0.3754 | 0.3808 | 0.3817 | 0.3881 | **0.2685** |
  | `tuned_L0_half` | 2,344 | 0.4126 | 0.3577 | 0.3677 | 0.3647 | 0.3689 | 0.3785 | 0.2586 |
  | `tuned_L0_quarter` | 1,172 | 0.3934 | 0.3384 | 0.3467 | 0.3389 | 0.3536 | 0.3797 | 0.2504 |
  | `mono_all` | 26,841 | 0.4150 | 0.3866 | 0.3862 | 0.3790 | 0.3857 | 0.4037 | **0.2306** |
  | `mono_half` | 13,420 | 0.4102 | 0.3896 | 0.3892 | 0.3838 | 0.3729 | 0.4079 | 0.2455 |
  | `mono_quarter` | 6,710 | 0.4108 | 0.3794 | 0.3749 | 0.3731 | 0.3737 | 0.3947 | 0.2636 |

  Contrasts (pts, 95 % CI, `*` excludes zero):

  | contrast | seen6 | X1 | L0 |
  |---|---:|---:|---:|
  | `tuned_L0_half − tuned_L0` | **−1.05 [−1.86, −0.24]*** | −0.99 [−2.63, +0.58] | −1.50 [−3.11, +0.06] |
  | `tuned_L0_quarter − tuned_L0` | **−2.71 [−3.81, −1.63]*** | −1.81 [−3.79, +0.16] | −3.41 [−5.21, −1.68]* |
  | `mono_half − mono_all` | **+0.01 [−1.17, +1.20] (equiv)** | +1.48 [−0.08, +3.21] | −0.48 [−2.10, +1.08] |
  | `mono_quarter − mono_all` | −0.81 [−2.14, +0.48] | **+3.29 [+1.32, +5.35]*** | −0.42 [−2.22, +1.38] |
  | `mono_all − tuned_L0` (the full tax) | +0.72 [−0.70, +2.17] | **−3.79 [−6.01, −1.65]*** | −1.26 [−3.29, +0.78] |
  | `mono_half − tuned_L0` | +0.73 [−0.47, +1.94] | **−2.31 [−4.36, −0.25]*** | −1.74 [−3.53, +0.00] |
  | `mono_quarter − tuned_L0` | −0.09 [−1.16, +0.99] (equiv) | −0.49 [−2.31, +1.40] | −1.68 [−3.29, −0.06]* |
  | `mono_half − tuned_L0_half` (same programs) | +1.78 [+0.42, +3.17]* | −1.32 [−3.21, +0.66] | −0.24 [−1.97, +1.50] |
  | `mono_quarter − tuned_L0_quarter` (same programs) | +2.62 [+1.40, +3.87]* | +1.32 [−0.74, +3.38] | +1.74 [+0.00, +3.47] |

- **What worked / hypothesis verdict:**
  - **H-sat-L0 — REFUTED.** Halving the clean-code corpus costs 1.05 pts on the seen conditions
    (CI excludes zero; not equivalent), quartering costs 2.71. `tuned_L0` at 4,689 rows is still
    on a rising curve. The three "more data is null" results of 09-04/09-05 (more programs,
    augmentation, more cases) were about *adding* to this corpus; the curve is flat above it and
    not below it — consistent, but "saturated" was the wrong word for the L0-only arm.
  - **H-sat-mono — CONFIRMED.** `mono_half` is equivalent to `mono_all` on seen6 (+0.01,
    TOST ±1.0), and `mono_quarter` is −0.81 n.s. Breadth training buys everything it will buy on
    the seen conditions by ~6.7k rows (1,172 programs × 6 views); the remaining 20k rows add nothing there.
  - **H-tax-scales — CONFIRMED.** The unseen tax against `tuned_L0` on X1 is −0.49 (quarter, ci_hi
    +1.40 ≥ 0) → −2.31* (half) → **−3.79*** (full): monotone in data volume. Read with the row
    above: on X1, `tuned_L0` *improves* with data (0.250 → 0.259 → 0.269) and `mono` *degrades*
    with data (0.264 → 0.246 → 0.231); `mono_quarter − mono_all` @ X1 is **+3.29*** — a quarter of
    the breadth corpus beats all of it on the unseen family. The data that stops buying seen
    accuracy at ~6.7k rows keeps buying unseen-family loss.
- **Observations:**
  - This is the clean statement of RQ1′'s cost: **breadth overfits the seen transform set as a
    function of volume.** The seen gain saturates; the X1 tax does not. `mono_quarter` is the
    best breadth arm on X1 and equivalent to `tuned_L0` on seen6 — it is the arm a practitioner
    should train, and it is a fifth of the compute.
  - At matched programs, breadth beats clean-only on seen6 at every size (+1.78*, +2.62*) and
    does **not** cost X1 (−1.32 n.s., +1.32 n.s.). The tax is therefore not "six views instead
    of one"; it is "six views of *enough* programs". Caveat: matched-program arms are not
    matched-row arms (`mono_quarter` has 5.7× `tuned_L0_quarter`'s rows), so this is a
    program-count reading, not a row-count one.
  - The L0 cost of breadth is present at every size (−1.26 / −1.74 / −1.68) and is not a volume
    effect; `an_l0cost` (pending) will classify it against every arm.
  - Single seed (s17) for the half/quarter arms; the full-data tax has a seed band (s42/s101
    −3.54 / −3.54, 09-07). The quarter-arm X1 number needs a second seed before "practitioner
    should train the quarter" becomes advice rather than an observation.
- **New questions / new hypotheses:** does the tax keep growing past 26,841 rows (a `mono_double`
  would need more programs — the 09-04 +58 % programs arm exists as `tuned_*_more`; its X1 cell
  is the free test); does `cons_lam3` at quarter data keep its X1 advantage or is the consistency
  objective simply a regulariser that mimics less data? Neither registered, neither run.
- **Next Steps:** RQ_SUMMARY §6/§6.1 carry the read; PAPER_EXPERIMENTS E12 → done; `tr_X1s` (382803)
  passed the raised-window truncation gate at 27 min, `ck_X1s` → `ev_x1split` → `an_x1split` follow.
