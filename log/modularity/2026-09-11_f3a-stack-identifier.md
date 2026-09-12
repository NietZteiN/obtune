### Target Date: 2026-09-11 (F3a: breadth's advantage on a deep stack needs an IDENTIFIER transform in it — and the direct contrast, not just the two intervals, says so)
- **Closes** `H-stack-identifier`, opened 2026-09-07 in
  [`2026-09-07_composite-depth.md`](2026-09-07_composite-depth.md). No compute: everything below
  comes from cells that already existed.
- **Hypothesis.** RQ2 holds that breadth helps on a stack because the stack still contains a
  transform the breadth arm was trained on, and that the **identifier** transforms carry it. The
  depth-3/4 composites test it by accident of design: three contain `L1r`, one
  (`C3_S1_S3_S4`) is structural-only.
- **Setup.** `mono_all − tuned_L0` on CodeLlama-7b, program-clustered bootstrap (2,000 resamples,
  seed 17), on the **394 programs common to all eight cells**. Intersecting once, up front, is what
  makes the two groups paired; a per-composite intersection would let them rest on different
  program sets and turn a stimulus difference into a group difference. It moves the per-composite
  points by ≤ 0.3 pts from the 09-07 read, which used each composite's own set.
- **Results:**

  | stack | contains identifier? | `mono_all − tuned_L0` |
  |---|---|---|
  | `C3_L1r_S3_S4` | yes | **+3.66 [+1.56, +5.76]** |
  | `C3_L1r_S1_S4` | yes | **+6.38 [+3.91, +8.79]** |
  | `C4_L1r_S1_S3_S4` | yes | **+5.83 [+3.35, +8.31]** |
  | `C3_S1_S3_S4` | **no** | +1.52 [−1.18, +4.07] |
  | pooled, identifier-containing | | **+5.00 [+3.02, +6.88]** |
  | pooled, structural-only | | +1.61 [−1.02, +4.23] |
  | **difference of differences** | | **+3.39 [+0.82, +6.16]** |

- **Verdict: CONFIRMED**, on both the rule as opened and a stricter one.
- **Why the stricter rule was added.** The rule as opened — "CONFIRM if structural-only stacks show
  no breadth gain at depth 3" — is satisfied by `C3_S1_S3_S4`'s interval straddling zero. But *one
  interval excludes zero and another does not* is not a test of the difference between them, and
  the structural-only interval reaches **+4.07**, overlapping every significant one. Reading the
  rule as written would let a difference that was never measured carry the claim. So
  `scripts/analysis/52_f3a_stack_identifier.py` computes the difference of differences on one
  bootstrap, which is legitimate here because all four composites were evaluated on the same
  programs. It comes out **+3.39 [+0.82, +6.16]**, excluding zero. The claim now rests on a measured
  contrast, and it survives.
- **What may be said:** on this model, breadth's advantage over the clean-code control on a depth-3
  stack is ~3.4 pts larger when the stack contains an identifier transform than when it does not,
  and the structural-only stack shows no detectable advantage on its own.
- **What may NOT be said:** that structural transforms contribute *nothing*. n = 1 structural-only
  stack, its point estimate is positive (+1.52), and its interval admits gains up to +4.07. The
  measured claim is about the *difference*, not about the structural stack being zero.
- **New questions:** none. F3's remaining legs (`H-F3-order`, `H-F3-cue-items`) still need F1's
  specialist cells on composites and are unaffected.
- **Next Steps:** carry the direct contrast into `RQ_SUMMARY.md` and the RQ2 section of the draft.
