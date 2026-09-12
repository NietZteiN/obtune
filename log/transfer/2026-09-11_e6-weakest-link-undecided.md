### Target Date: 2026-09-11 (E6 weakest-link vs surface: UNDECIDED by the pre-registered rules — every cross-mechanism point estimate leans surface and not one of them reaches significance)
- **Attempts to close** the open question left by
  [`2026-09-08_x1-split-mechanism-not-family.md`](2026-09-08_x1-split-mechanism-not-family.md).
  Rules and their limits were committed in `CLAUDE_SCRATCHPAD.md` **before** any accuracy below was
  computed. Analysis only: existing `x1_split` cells, no GPU, no H1.
- **Hypothesis.** Either half of X1 recovers ~90 % of the whole adapter's gain while transferring
  almost nothing to the other half's condition. Two readings: **weakest-link** (relieving whichever
  mechanism the model meets first unlocks most items) or **surface** (the gain is adaptation to the
  family's scaffolding, which either half's training data carries).
- **Setup.** X1 heldout programs classified by which mechanism is actually present, after stripping
  the fixed helper preamble. Sizes are a property of the stimulus and were recorded before the
  read: `mba_only` 177, `str_only` 51, `mba_first` 49, `str_first` 107, `expansion_only` 21.
  Program-clustered bootstrap, 2,000 resamples, seed 17, TOST margin ±1.5, control `tuned_L0`.
- **Results — the discriminating cells** (a half-adapter on programs containing *none* of the
  mechanism it was trained on can only gain through surface):

  | group | arm | never saw this mechanism? | `− tuned_L0` |
  |---|---|---|---:|
  | `mba_only` (177) | `tuned_X1s` | **yes** | +2.64 [−0.75, +5.87] |
  | `str_only` (51) | `tuned_X1m` | **yes** | +1.96 [−1.96, +6.54] |
  | `mba_first` (49) | `tuned_X1s` | **yes** | **+5.44 [+0.68, +10.88]** |
  | `str_first` (107) | `tuned_X1m` | **yes** | **+4.05 [+0.93, +7.79]** |
  | order test | `tuned_X1m`, mba-first − str-first | | +2.07 [−3.40, +7.77] |

- **Verdict: UNDECIDED**, by the mapping fixed in advance. H-E6-surface-a, H-E6-surface-b and
  H-E6-order are all **INCONCLUSIVE** — no interval excludes zero *and* none is TOST-equivalent to
  it, so the data distinguish neither reading. Recording this as the result rather than reaching
  for the suggestive half is the point of having written the mapping down first.
- **What the numbers lean toward, stated as a lean and not a finding.** **All four cross-mechanism
  point estimates are positive** (+2.64, +1.96, +5.44, +4.05), and two of them exclude zero. Under
  a strict weakest-link reading an adapter that never saw the mechanism in front of it should give
  nothing. It does not give nothing. That is the direction the surface reading predicts. It is also
  four positive estimates out of four with **no multiplicity correction over the 20 contrasts
  computed here**, in groups as small as 49, so it is a lean.
- **The two limits registered in advance both bit, in the directions predicted.** `tuned_X1s` pays
  the campaign's largest L0 cost (−4.37) and is the only arm trained at a 4,096-token window, which
  biases H-E6-surface-a toward zero — its +2.64 is a *floor*, not an estimate. And `str_only` has 51
  programs, so H-E6-surface-b's null means very little. Neither sub-rule was decisive alone, which
  is exactly why the mapping required both.
- **An observation outside the rules, worth keeping.** `mono_all` is **negative on every group**
  and significantly so on `str_only` (−6.54 [−11.76, −1.31]). Breadth's X1 tax is concentrated on
  the programs whose only mechanism is string encoding — the mechanism furthest from anything in
  the six seen transforms. Not registered, not corrected, and a natural hypothesis for a later pass.
- **Next Steps:** E5b (a hard second family with a *different* surface) remains the experiment that
  would settle "surface family", exactly as the 09-08 entry said. This read does not change that,
  and it does not license the surface reading in the paper.
