### Target Date: 2026-09-08 (E11c — the L0-cost format reversal, with the difficulty confound removed: it gets *bigger*, so the confound was masking the effect, not creating it)
> Continues [`2026-09-08_where-the-l0-cost-lands.md`](2026-09-08_where-the-l0-cost-lands.md), the
> same day. That read found a significant reversal it could not fully trust, because "unusual
> format" and "easy item" were the same stratum. This one holds difficulty fixed.
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  **`8da96b4`** before the `--matched` code existed. Items are binned by the **control's own**
  per-item accuracy (hard = 0, partial, easy = 1 over the control's trials for that item — defined
  without reference to the arm under test, since using the arm's own accuracy would condition on the
  outcome), common vs unusual is compared **within** each bin, and the within-bin deltas are pooled
  weighted by item count. **The rule is two-sided this time:** ci_hi < 0 CONFIRMED, ci_lo > 0
  **CONFIRMED-REVERSED**, inside ±1.0 REFUTED, else INCONCLUSIVE. E11b's one-sided rule had no branch
  for the reversal it found; that was a rule-design error and it is corrected here rather than
  quietly patched into the old rule.
- **Setup:** `an_l0strat2` **383173** (`43_l0_stratify.py --matched`,
  `results/analysis/pipeline/l0_stratify_matched_codellama7b.json`). Same items, same pooled-seed
  units, same paired program-clustered bootstrap. CPU only. No H1.
- **Results — Δ(unusual) − Δ(common), pooled within difficulty bins:**

  | unit | pooled | hard | partial | easy |
  |---|---:|---:|---:|---:|
  | **`mono_all` (3 seeds)** | **+10.21** [+5.34, +15.14]* | +11.69 [+3.63, +20.83] | +23.51 [+8.89, +37.23] | +4.98 [−0.70, +9.67] |
  | `cons_lam3` (3 seeds) | +6.43 [+2.50, +10.98]* | +6.73 [+0.13, +14.60] | +7.04 [−7.27, +21.12] | +5.89 [+2.92, +8.63] |
  | `tuned_X1` | +1.34 [−1.72, +4.16] | −2.28 [−5.56, +2.19] | +9.02 [−10.41, +27.32] | +4.45 [−0.99, +9.38] |
  | `base` | +20.03 [+13.32, +27.12]* | +21.10 [+9.44, +33.97] | +12.91 [−3.77, +30.41] | +20.28 [+10.21, +29.67] |

  **H-L0-format-matched: CONFIRMED-REVERSED** (+10.21 [+5.34, +15.14]).
- **Reading.**
  1. **The confound was hiding the effect, not producing it.** Unmatched, the reversal was +4.70
     [+0.44, +8.89]; matched on the control's own difficulty it is **+10.21** [+5.34, +15.14] — more
     than twice the size, and positive in all three bins. The obvious alternative explanation for
     E11b ("breadth only looks safe on unusual formats because those items are easy") is not merely
     unsupported, it runs backwards: easiness was *diluting* the contrast.
  2. **The same ordering appears in `cons_lam3` at ~60 % of the size and in `base` at twice it.** The
     effect is not specific to breadth; it is what happens to *any* degraded model on this item set.
     That points at a mechanism rather than a quirk of the breadth objective: the unusual classes are
     `bool_none`, `dict_set` and `float` — answers drawn from a tiny output space, where a damaged
     model still lands on the right token — while `int`/`str`/`list` are where accuracy is actually
     losable. **What breadth costs is the ability to get the answers that can be gotten wrong.**
  3. **`tuned_X1` again has a different shape** (+1.34, interval spanning zero, and the only negative
     bin in the table). Whatever the X1-family arm gives up on clean code is still not what breadth
     gives up — E11b's observation survives the matched analysis.
- **Caveats.** Within the hard bin an arm's delta can only be ≥ 0 and within the easy bin only ≤ 0
  (the control is at floor and ceiling by construction), so the *levels* are bounded; the
  **contrast between format groups inside a bin is not**, because both groups are bounded the same
  way, and that contrast is what is reported. The pooled figure is a count-weighted average of three
  such contrasts. Within-bin cells are smaller than the unmatched strata, which is why the intervals
  are wider in absolute terms despite the larger point estimate. 7B, one item set, Python.
- **Next:** none. §22.6's question now has an answer with the confound removed, and the answer is the
  opposite of what the section proposed. Docs: `docs/RQ_SUMMARY.md` §6 RQ1′,
  `docs/PAPER_EXPERIMENTS.md` E11, `MASTER_REPORT.md` §29.1.
