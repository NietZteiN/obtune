### Target Date: 2026-09-11 (F9: on SEEN-transform stacks, anchoring matches breadth rather than beating it — the depth-4 cell is the lone exception and is not strong enough to carry a claim)
- **Closes** the second F9 bullet in [`docs/PAPER_EXPERIMENTS.md`](../../docs/PAPER_EXPERIMENTS.md)
  §7: "state whether the depth-4 stack's +7.20 over `tuned_L0` is also a gain over breadth."
  Analysis only, no compute, from `composite_depth_codellama7b.json` as it stands.
- **Question.** `cons_lam3` beats the clean-code control on every deep stack. The control that
  matters is not `tuned_L0` but `mono_all` — breadth already gets most of that gain, so the open
  question is whether anchoring adds anything on top of it.
- **Results** (CodeLlama-7b, 394 programs, program-clustered bootstrap):

  | stack | `cons_lam3 − tuned_L0` | `cons_lam3 − mono_all` | `mono_all − tuned_L0` |
  |---|---:|---:|---:|
  | `C3_L1r_S3_S4` | **+3.47 [+1.19, +5.58]** | −0.25 [−2.20, +1.78] | **+3.73 [+1.35, +6.10]** |
  | `C3_S1_S3_S4` | **+3.13 [+0.76, +5.58]** | +1.52 [−0.59, +3.73] | +1.61 [−1.02, +4.31] |
  | `C3_L1r_S1_S4` | **+6.27 [+3.98, +8.55]** | +0.17 [−1.78, +2.03] | **+6.10 [+3.72, +8.54]** |
  | `C4_L1r_S1_S3_S4` | **+7.20 [+4.66, +9.75]** | **+2.03 [+0.17, +3.82]** | **+5.17 [+2.62, +7.70]** |
  | **pooled** | **+5.02 [+3.41, +6.69]** | +0.87 [−0.59, +2.33] | **+4.15 [+2.37, +5.91]** |

- **Answer: mostly no.** Anchoring's large gains over the clean-code control on deep seen stacks are
  almost entirely what breadth already buys. Pooled, `cons_lam3 − mono_all` is **+0.87
  [−0.59, +2.33]** — indistinguishable from zero. Three of the four stacks straddle zero
  individually, one of them (`C3_L1r_S3_S4`) with a negative point estimate.
- **The depth-4 exception, and why it is not being promoted to a finding.** `C4_L1r_S1_S3_S4` gives
  **+2.03 [+0.17, +3.82]**, the only cell where anchoring beats breadth. It is one significant
  result out of four comparisons, its lower bound is **+0.17**, and no multiplicity correction has
  been applied to this set. It would very likely not survive BH-FDR across the four. It is recorded
  as a **directional observation**: anchoring's margin over breadth is largest at the deepest stack
  (−0.25, +0.17, +1.52, +2.03 as depth and breadth of the stack grow). That ordering is suggestive
  and it is not evidence.
- **Why it matters anyway.** The suggestion — that anchoring's advantage appears only once the input
  is far enough from any single training transform — is exactly what F2's divergence ladder tests,
  on an independent axis (unseen family rather than depth). If F2's `cons_lam3 − mono_all` at d2 is
  positive, this ordering becomes a second, pre-existing line of support. If F2 comes out flat,
  this cell is noise and should be dropped. **Written down now so that reading is not chosen later.**
- **What may NOT be said:** that anchoring beats breadth on stacked seen inputs. The pooled estimate
  does not support it and three of four cells do not either.
- **Next Steps:** none. Re-read this entry beside F2's result rather than in isolation.
