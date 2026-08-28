# attention — RQ3 — token classes, slicers, anchoring metrics, regression

*Last updated: 2026-08-27*
**Status:** active — RQ3 has a correlational result (§15.1), a causal result (§15.3) and a
training-free intervention (§16.5). Outstanding: a generate-mode confirmation of steering, the
length-matched control, and an unpaid `H1` attention read.

## Hypotheses
| # | Hypothesis | State |
|---|---|---|
| A1 | Tuning re-anchors attention off identifiers onto control/dataflow | **Supported.** `tuned_S2` shift **+0.111** [+0.093, +0.131] on `S2`, 2.6x the clean-code control and specific to `S2` |
| A2 | That re-anchoring is load-bearing, not incidental | **Supported (causal).** Identifier knockout costs `base` −0.089 [−0.158, −0.023] and `tuned_S2` +0.015; paired difference **+0.104** [+0.011, +0.209] |
| A3 | Suppressing attention to provably-inert tokens helps, with no training | **Supported at full depth.** `base`/`S2` **+0.2172**; null at 6/28 layers (partial intervention) |
| A4 | Anchoring shift predicts which transfers succeed | **Open.** The shift ~ knockout-damage regression across all 18 system x condition cells has not been run |
| A5 | The mechanism explains transfer to `H1` | **Open, and inferential.** No `H1` attention read has been paid for |

(see [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) for the full ledger)

## Hypotheses — resolved
- (none yet)

## What worked
- **Teacher-forced log P(gold) instead of exact-match accuracy.** A 12-cell knockout sweep was flat
  (−2.7 .. +2.7 pts) purely because `base` sits at ~22 % on obfuscated `S2` and binary hit/miss has
  no headroom. Log-probability has ~100× the dynamic range and is defined on items the model gets
  wrong. This single change turned RQ3's causal step from null to significant.
- **Manipulation checks before believing a null.** Attention mass at masked keys → 0.0000 at every
  masked layer, and all-28-layer masking changes 68 % of outputs against 62 % identical at 6 layers.
  That dose-response is what later exposed the 6-layer steering null as a partial intervention.
- **Empty-mask control cells.** `L0` has no inert code, so its steering mask is provably empty and
  every Δ must be exactly 0.0000. Five such cells came back exactly 0.0000, which is what makes the
  small-effect cells readable as genuine nulls rather than a mask that stopped firing.
- **Pre-registering the falsifying cell.** `L1r` (renaming) was chosen because every adapter shifts
  attention *toward* identifiers there — the opposite sign from `S2`. A mechanism that only ever
  predicted "less damage" would have been unfalsifiable.

## What didn't
- **Exact-match accuracy as a knockout readout.** Floor effect; see above.
- **Concluding from a 6-layer intervention.** Masking at 6 of 28 layers left every steering cell
  inside ±0.03 and was reported as a dissociation ("the benefit of deleting inert code is sequence
  length, not attention"). The all-28-layer control refuted it within the hour: `base`/`S2` moves
  **+0.2172**. *A null at partial depth is not evidence of no effect.*
- **SDPA attention.** Returns `None` for attention weights; eager is required for any capture.
- Six defects were found in RQ3 code that had never been executed (grader arity, a 2-value unpack
  from a 6-field dataclass, a silent fallback grader, an `npz` schema no writer emitted, missing
  prompt truncation that OOM-killed 24 jobs, `j.shift` colliding with `DataFrame.shift`).

## Open ideas
- Confirmatory `--mode generate` pass on steering — the claim is currently about log-probability,
  not about answers.
- The **length-matched control**: replace inert spans with equal-length neutral filler. Deletion
  removes content *and* shortens; masking removes access and keeps length; filler keeps length and
  removes content. The three together decompose the +4.74.
- Attention supervision during training (auxiliary loss on inert-token attention) — live again after
  the 28-layer result; it had been judged pre-falsified on the 6-layer null.
- An `H1` attention read is still unpaid, so "ignores inert material on `S2`" → "transfers to `H1`"
  remains inferential.

## Entries
| Date | Entry |
|---|---|
| 2026-08-17 | [`2026-08-17_rq3-path-repaired.md`](2026-08-17_rq3-path-repaired.md) |
| 2026-08-18 | [`2026-08-18_rq3-first-sweep.md`](2026-08-18_rq3-first-sweep.md) |
| 2026-08-26 | [`2026-08-26_knockout-null-to-causal.md`](2026-08-26_knockout-null-to-causal.md) |
| 2026-08-27 | [`2026-08-27_steering-depth-and-a-wrong-null.md`](2026-08-27_steering-depth-and-a-wrong-null.md) |

## Doc / results links
- [`../../docs/MASTER_REPORT_2026-08-27.md`](../../docs/MASTER_REPORT_2026-08-27.md) §15 (knockout), §16.5 (steering)
- [`../../docs/REPORT_2026-08-26_rq3-attention-mechanism.md`](../../docs/REPORT_2026-08-26_rq3-attention-mechanism.md)
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
- Cells: `results/attn/knockout/`, `results/attn/steer/`
