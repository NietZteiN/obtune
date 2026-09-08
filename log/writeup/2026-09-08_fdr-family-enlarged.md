### Target Date: 2026-09-08 (E7b — the same BH-FDR with the family enlarged 7×: every claim the paper rests on still survives, and the primary families reproduce bit for bit)
> Continues [`2026-09-08_fdr-over-the-families.md`](2026-09-08_fdr-over-the-families.md), the same
> day. That entry corrected the two families pre-registered on 09-07. This one asks the question a
> reviewer asks next: the pipeline campaign roughly tripled the number of arms, so are those q-values
> still the right ones?
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  **`e5d08ab`** before the code existed. The 09-07 families — `transfer` (30 tests) and `arms`
  (28 tests) — **stay primary and unchanged**. Two families are added as a **conservative robustness
  check only**: enlarging a family can only raise q, never lower it, so nothing can be *upgraded* by
  this; a claim either survives the widest reasonable family or it does not. Membership is
  **discovered from the directory tree**, never hand-picked, so no arm can enter because of how its
  number came out. Rule unchanged: survives iff q < 0.05. Reported; gates nothing.
- **Setup:** pipeline stage `an_fdr2`, job **383162** (2 min 31 s, `normal`),
  `scripts/analysis/37_fdr_family.py --extended` →
  `results/analysis/pipeline/fdr_extended_codellama7b.json`. The original
  `fdr_codellama7b.json` is untouched. CodeLlama-7b, Python, heldout. No H1.
- **Results:**
  - **Reproducibility check first.** The `transfer` and `arms` families come back **byte-identical**
    to the 09-08 run — all 58 rows, every delta, CI, p and q equal on a field-by-field comparison.
    The bootstrap is seeded and the cell resolution is deterministic; this is the first time that has
    been *verified* rather than assumed.
  - **`arms_all` — 30 systems discovered, 203 tests, 69 survive.** The family is 7.25× the size of
    `arms`, and **not one of `arms`' eight survivors is lost**:

    | claim | `arms` (28 tests) | `arms_all` (203 tests) |
    |---|---:|---:|
    | `mono_all − tuned_L0` @ X1 (**C1, the headline**) | −3.79, q = 0.017 | −3.79, **q = 0.014** |
    | `tuned_X1 − tuned_L0` @ X1 | +4.86, q = 0.009 | +4.45, **q = 0.005** |
    | `cons_lam3 − tuned_L0` @ L1b | +4.58, q = 0.009 | +4.46, **q = 0.005** |
    | `mono_all − tuned_L0` @ L1b | +2.90, q = 0.028 | +2.90, **q = 0.032** |
    | `cons_lam3 − tuned_L0` @ X1 | +1.07, q = 0.29 | +1.07, **q = 0.44** (still no) |
    | `mono_all − tuned_L0` @ L0 (the cost) | −1.32, q = 0.26 | −1.32, **q = 0.38** (still no) |

    Some q-values *fell* despite the larger family — BH's threshold depends on the whole p-value
    distribution, and `arms_all` contains many strongly-significant cells (all seven `cons_tbase`
    columns, the `x1_resample` row) that pull the step-up boundary out. That is not a loophole; it is
    why "more tests always means weaker" is a rule of thumb rather than arithmetic.
  - **New cells that survive and matter:** `cons_tmono − tuned_L0` @ X1 **−3.13** (q = 0.038) — E4's
    "a breadth teacher imports breadth's tax" survives multiplicity; `cons_tbase` on all seven
    columns (q = 0.005 throughout, −12.8 on X1) — the untuned-teacher collapse is not a fluke;
    `tuned_L0_quarter` @ L0 −3.29 (q = 0.005) — E12's data-volume effect on clean code survives.
    `mono_quarter` @ X1 −0.74 (q = 0.59) does not survive, exactly as E12's saturation story predicts.
  - **`composites` — 12 tests, 10 survive.** All six of `cons_lam3 − tuned_L0` (q ≤ 0.006, +2.69 to
    +8.14) and four of six of `mono_all − tuned_L0` (+3.00 to +6.62); the two that do not are the
    S3/S4-containing pairs `C_L1r_S3` +1.98 (q = 0.065) and `C_S4_S3` +1.08 (q = 0.264) — the same
    two composites the 13B and 34B reads identified as the ones where a clean-only model already
    does well. **RQ-A survives per-cell multiplicity on 4/6 composites; RQ-B on 6/6.**
- **The gap this exposes, stated rather than closed.** Every family here tests against `tuned_L0`.
  RQ3′'s actual headline — **`cons_lam3 − mono_all` @ X1** (+4.59 at 7B, +3.95 at 13B, +3.38 at 34B,
  +3.46 on Llama) — is therefore **in no family and has never been multiplicity-corrected**. I noticed
  this only while reading these results, which is exactly why I am not adding a third family now: a
  family chosen after seeing that the headline was uncovered cannot be told apart, by a reader, from
  a family chosen because the headline survives in it. It goes to the next pre-registration as a
  stated gap, and the paper must say the contrast is uncorrected until then.
- **A second caveat, smaller but real.** `arms_all` resolves cells across six phases where `arms`
  used three, so a system whose adapter was read in more than one phase can resolve to a *different
  read of the same adapter*. Across the 28 shared rows the point estimates move by at most **0.42
  pts** (`mono_all` on L1r, +0.66 → +1.08) and only 4 of 28 are numerically identical. No verdict
  changes, but it is the same duplicate-cell issue §8 documents, and it means the two families'
  numbers should not be quoted interchangeably to two decimals.
- **What worked / verdict:** the check did what a robustness check should — it moved no claim and
  removed one worry. The headline C1 result (`mono_all` loses on the unseen family) survives at
  q = 0.014 in a 203-test family; the two contrasts the campaign has always reported as
  *not* surviving (`cons_lam3 − tuned_L0` on X1, breadth's L0 cost) still do not, and are still
  reported that way. The honest addition is the uncovered-headline gap above.
- **Next:** pre-register a `mono_all`-controlled family (all arms × 7 conditions vs `mono_all`) so
  RQ3′'s headline gets the same treatment; that is a rule to freeze *before* the next read, not a
  run to do now. Docs: `docs/RQ_SUMMARY.md` §6 RQ4′, `docs/PAPER_EXPERIMENTS.md` E7.
