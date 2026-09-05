### Target Date: 2026-09-05 (Lever 5: 3× labelled input cases per program — null on the specialist, borderline on breadth)

The last untested form of "more data". Earlier entries closed *more programs*
([`2026-09-04_accuracy-campaign-closes.md`](2026-09-04_accuracy-campaign-closes.md): +58 % data,
−0.20 / +0.73, null). This tests **more labelled behaviour per program** — 3 execution-gated
input cases instead of 1, same program set, same conditions — which is free to generate and was
the one remaining reading of H-scale. Jobs `tr_cs_L0` 377851 → `ck_cs_L0` 377852,
`tr_cs_mono` 377853 → `ck_cs_mono` 377854, `ev_cases` 377855. **H1 is not read.** Comparisons
are item-for-item against the canonical adapters on the same 9,582 items / 557 programs;
intervals are program-clustered bootstraps.

- **Hypothesis — H-cases (pre-registered 09-05):** the corpus is saturated in *programs* but not
  in *labelled behaviour per program*, so tripling the cases lifts accuracy where tripling the
  programs did not. CONFIRM if `tuned_L0_cases − tuned_L0` > 0 with the interval excluding zero;
  REFUTE otherwise. **REFUTED on the specialist, not established on breadth.**
- **Results:**

  | cond | `tuned_L0_cases` − `tuned_L0` | `mono_cases` − `mono_all` |
  |---|---|---|
  | L0 | −0.06 [−1.50, +1.38] | +0.60 [−1.08, +2.28] |
  | L1b | +0.48 [−1.09, +1.99] | +1.63 [−0.18, +3.44] |
  | L1r | +1.26 [−0.36, +2.82] | +1.56 [−0.12, +3.23] |
  | L2 | +1.56 [−0.18, +3.17] | **+2.22 [+0.54, +3.84]** |
  | S1 | −0.96 [−2.57, +0.64] | −0.32 [−2.57, +1.92] |
  | S2 | −0.72 [−2.10, +0.78] | +1.44 [−0.30, +3.12] |
  | **pooled** | **+0.31 [−0.55, +1.17]** | **+1.25 [−0.01, +2.54]** |

  The specialist arm is flat — 2× the rows (9,378 vs 4,689) for +0.31 pts. The breadth arm
  (53,682 rows, 6.8 h) is +1.25 with the bound touching zero, and exactly one of twelve cells
  excludes zero (`L2`), which BH-FDR across the family would not keep. **Nothing here clears a
  corrected threshold.**
- **Reading.** Three independent forms of "more data" — more programs (+58 %), variant
  augmentation, and now 3× labelled cases per program — are all null or borderline at 7B. That
  is converging evidence for **H-saturation**: the 7B data curve is flat in this regime, and the
  binding constraint is not corpus size in any of its dimensions. Worth stating plainly because
  it is the cheap lever everyone reaches for first.
- **One honest flag, not a finding.** `mono_cases − tuned_L0_cases` is **+1.50 [+0.01, +2.97]**,
  where the canonical `mono_all − tuned_L0` is +0.56 [−0.89, +1.98] (the tie). A hint that extra
  cases help *breadth* more than the clean-code control — i.e. that the L0-vs-breadth tie might
  be a data-limited artefact rather than a ceiling. It is one marginal contrast selected after
  the fact from a table where the pre-registered test failed, so it is **not** claimed here. It
  is the natural pre-registration for a future entry if the tie is ever revisited.
- **Provenance:** cells `results/cells/rq2_generic/codellama-7b/python/{tuned_L0_cases,mono_cases}__*`;
  bank `data/train/pairs_aug/cases3/` (38,346 rows); adapters `runs/adapters_cases/...`
  (`train_loss` 0.490 / 0.143; truncation 5/9,378 and 58/53,682 at `max_seq_len` 2048);
  ckpt-select val 0.411 (ckpt-147) and 0.367 (ckpt-2514).
