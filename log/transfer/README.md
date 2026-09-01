# transfer — RQ1 — per-condition adapters, transfer matrix, GLMMs

*Last updated: 2026-09-01*
**Status:** REPLICATED on CodeLlama-7b after the Qwen panel became unusable. TR = 0.906 vs floor, LOTO price of an unseen transform −0.0108 (94.5 %). H1 unspent on both panels.

## Hypotheses — open
- **H-scale-floor** — the format floor shrinks with model scale because format failures migrate
  onto items the model cannot solve anyway. Base format_fail is near-identical at the two scales
  (0.179 at 7B, 0.192 at 1.5B) yet repairing it is worth 2-14 % of the gain at 7B and 62-67 % at
  1.5B. Directly testable: partition items by whether `base` format-fails and compare `base`
  accuracy across the partitions at each scale.
- (see [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) for the full ledger)

## Hypotheses — resolved
- **H-format — REFUTED at 7B, SUPPORTED at 1.5B, 2026-08-30.** Label-shuffled control takes only
  2-14 % of the 7B diagonal gain (negative on S1); recomputing the matrix against the floor moves
  mean off-diagonal TR from 0.8842 to 0.8810. At 1.5B the same control recovers 62-67 %, so the
  1.5B headlines are reported against the wrong reference.
- **H-mem (7B) — REFUTED, 2026-08-30.** Memorization predicts a strong diagonal and a flat
  off-diagonal. Measured on the 412-program common subset: mean off-diagonal
  **TR = 0.885 [0.855, 0.916]**, diagonal − off-diagonal **+0.0199 [+0.0147, +0.0252]**
  (cluster bootstrap by program, B=2000, 0/2000 draws <= 0). Specialization is real and
  reliably non-zero, and an order of magnitude smaller than the transfer.
  Interpretation is gated on **H-format**.

## What worked
- Checkpoint selection before evaluation, on the held-in val slice: selections ranged from
  `checkpoint-73` to `final`, so several conditions peak well before the end of training.
- Reporting on the all-conditions-succeeded common subset (412 of 557 programs; S1 binds at
  416) rather than per-condition full sets.

## What didn't
- Reading a shuffled-label control on `format_fail` and accuracy alone. The first 7B attempt read
  acc 0.001 / format_fail 0.013 — the pre-registered "floor is zero" signature — while emitting one
  constant string on 91 % of items. Output diversity is required alongside both.
- `phase: main` for a new grid. It aliases onto existing Grid B cells under the same system
  names, and `resume: true` would have pooled two grids CLAUDE.md forbids pooling. Caught by
  the collision guard in 4 s (job 359113). A new grid needs a new `phase`, registered in
  `TrialRow.phase`.
- Validating an eval config with `--limit 4`: the adapter-applied guard tripped on byte-identical
  generations that were a small-n artifact, and re-running at `--limit 64` cleared it. Tiny probes
  test plumbing, not correctness.

## Open ideas
- (none yet)

## Entries
- [`2026-09-01_codellama-replication.md`](2026-09-01_codellama-replication.md) — every RQ1/RQ2 finding reproduces on CodeLlama; TR 0.906, LOTO price −0.0108
- [`2026-08-30_format-floor-and-a-collapsed-control.md`](2026-08-30_format-floor-and-a-collapsed-control.md) — H-format refuted at 7B / supported at 1.5B; a mode-collapsed control faked the target signature
- [`2026-08-30_7b-rq1-matrix.md`](2026-08-30_7b-rq1-matrix.md) — 7B RQ1 transfer matrix; TR = 0.885; H-mem refuted, H-format opened.

## Doc / results links
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
