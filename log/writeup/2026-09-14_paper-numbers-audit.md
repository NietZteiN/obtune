# 2026-09-14 — Audit: every live number in the paper's prose still matches the cells

**Thread:** writeup · **Status:** clean · **Why now:** today moved a great deal of data — the backward ladder was re-read on seven models into a new phase, the mixture column gained cells, and several published figures were corrected. Frozen prose can go stale silently while the tables around it regenerate.

## Method

Strip the inlined table blocks and the LaTeX comments from each section, keep what a reader actually
sees, and list every decimal in it. Then re-derive the load-bearing ones from the cells.

| section | live decimals in prose |
|---|---|
| `abstract`, `background`, `related`, `rqs` | 0 |
| `intro-2` | 1 |
| `intro` | 3 |
| `setup`, `threats` | 3, 2 |
| `master` | 12 |
| `rq2` | 8 |
| `rq1` | 27 |
| `rq3` | 28 |

## Result: clean

The numbers this section's argument rests on are the CodeLlama-7B direction ratios, quoted in both
RQ1 and RQ3. Re-derived today from `58_direction_ratio.py`:

| arm | forward | backward | ratio | paper says |
|---|---|---|---|---|
| `formatonly` | +1.47 | −0.44 | **−0.30** | −0.30 ✓ |
| `tuned_L0` | +19.34 | −1.60 | **−0.08** | −0.08 ✓ |
| `mono_all` | +19.46 | −0.89 | **−0.05** | −0.05 ✓ |
| `cons_lam3` | +20.88 | +0.62 [−1.56, +2.81] | **+0.03** | +0.03, and the interval verbatim ✓ |
| `tuned_X1` | +17.35 | +1.63 [+0.11, +3.20] | **+0.09** | the interval verbatim ✓ |

**None of these moved, and the reason is worth recording: CodeLlama-7B was the one model whose
backward cells were always one-shot.** Every figure in the paper's prose that touches the backward
direction comes from that model, so the two-prompt fault that invalidated numbers across seven other
models reached none of the prose. That is luck rather than design.

## What is flagged and not fixed

Three contradictions sit in a LaTeX comment at the `rq1_merge_panel` table, pending the framing
decision. Their numbers were re-checked and both intervals still hold: the merge's
**+3.21 [+1.52, +4.85]** backwards on CodeLlama-7B (re-read today on repaired cells, unchanged) and
the mixture's **+2.88 [+1.33, +4.41]** above breadth on stacks containing the unseen family, which
the leaderboard reproduces as 0.274 against 0.244 on the same group.

## Two prose defects found that are not numbers

- **Setup** states that a cell over the format gate "measures the prompt contract rather than the
  task". Today's decomposition contradicts that on many cells. Flagged at the site, not rewritten,
  because the fix interacts with the framing decision.
- **`intro-2`** cites `ase26`, which exists in no bibliography here or in any sibling project.
  Flagged at the site. Not invented.
