### Target Date: 2026-09-11 (F3a's rule tested OUT OF SAMPLE on the unseen-containing stacks — CONFIRMED and larger; and a correction to the per-composite column of the entry that opened it)
- **Two things, one script.** `scripts/analysis/52_f3a_stack_identifier.py` gained a `--stimulus`
  flag and a bug fix. Extends
  [`2026-09-11_f3a-stack-identifier.md`](2026-09-11_f3a-stack-identifier.md), whose headline is
  unchanged; per CLAUDE.md §6 that entry stands unaltered and this one carries the correction.

#### 1. The rule holds out of sample, and the effect is larger
- **Why this is a test and not a description.** F3a's rule — *breadth's stack gain is larger when an
  identifier transform is present* — was committed at **19:15:53** (`acfe301`). F2's first cell was
  written at **20:47**. The hypothesis predates the data by 91 minutes and the ordering is checkable
  in git, so applying it to F2's six unseen-containing composites is out-of-sample.
- **Result:**

  | stimulus | identifier-containing | structural-containing | **difference** |
  |---|---:|---:|---:|
  | depth-3/4, all SEEN (in-sample) | +5.00 [+3.02, +6.88] | +1.61 [−1.02, +4.23] | **+3.39 [+0.82, +6.16]** |
  | F2's stacks, each containing the UNSEEN family | +1.98 [−0.12, +4.18] | **−3.88 [−6.08, −1.71]** | **+5.85 [+3.10, +8.72]** |

- **CONFIRMED, and the mechanism sharpens.** On seen stacks the identifier group merely gains more.
  On unseen-containing stacks the structural group goes **significantly negative** — breadth is
  actively *worse* than the clean-code control there — while the identifier group stays positive.
  The gap widens from +3.39 to **+5.85**.
- **This is what the pooled d2 figure in [F2](../transfer/2026-09-11_f2-divergence-ladder.md) was
  hiding.** That level reported −1.71 [−3.60, +0.31] and a verdict of INCONCLUSIVE; it is the
  average of two opposite-signed populations. The F2 entry flagged the split as post-hoc. It is not
  post-hoc under *this* rule, which predates the cells.
- **Still not claimed:** that the identifier group is positive on unseen-containing stacks. It is
  +1.98 [−0.12, **+4.18**], straddling zero. What is established is the **difference** between the
  groups, which is what the rule asks.

#### 2. Correction: the per-composite column of the F3a entry mixed program sets
- **What was wrong.** The pooled and difference rows were computed on the 394 programs all cells
  share, as that entry described. The **per-composite** rows were not: they went through
  `bootstrap_delta`, which intersects only the two cells it is handed — each composite's own,
  larger set. One table, two program sets. That is the exact confound the entry's own text warns
  about two paragraphs earlier.
- **Corrected values** (`mono_all − tuned_L0`, depth-3/4):

  | composite | as recorded | corrected (common 394) | shift |
  |---|---:|---:|---:|
  | `C3_L1r_S3_S4` | +3.66 | +3.73 | +0.07 |
  | `C3_L1r_S1_S4` | +6.38 | +6.10 | −0.28 |
  | `C4_L1r_S1_S3_S4` | +5.83 | **+5.17** | **−0.66** |
  | `C3_S1_S3_S4` | +1.52 | +1.61 | +0.09 |

- **The headline is untouched.** Difference of differences **+3.39 [+0.82, +6.16]**, byte-identical,
  because the group rows were always on the common set. Every significance verdict is unchanged.
  The corrected `C4` value now matches `composite_depth_codellama7b.json`'s published +5.17, which
  is the check that should have caught this the first time.
- **Why it stayed invisible.** On the depth-3/4 stimulus the four composites happen to share almost
  all their programs, so the two sets nearly coincide and the largest error is 0.66 pts. On F2's
  composites, whose coverage differs sharply (405 vs 287), the same bug moved `C_L1r_X1` from +2.67
  to **+1.48** — and produced per-composite rows that did not add up to the pooled row printed
  beneath them. **The inconsistency is what exposed it**: the same contrast disagreed between two
  scripts, and only one of them could be right.
- **Next Steps:** none. `52` now filters to the common subset everywhere, and both stimuli were
  re-run; the F2 analysis (`53`) filtered correctly from the start and needed no change.
