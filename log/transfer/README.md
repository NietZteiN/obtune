# transfer — RQ1 — per-condition adapters, transfer matrix, GLMMs

*Last updated: 2026-09-03*
**Status:** master report reproduced on CodeLlama-7b with cluster-bootstrap CIs on every contrast, and one human-authorized H1 repair read (`pilot_eval`; `final_eval` unspent). **`tuned_L0` BEATS `mono_all` on H1: +0.041 [+0.018, +0.064]** — stronger than Qwen's "matches". `tuned_L0` ties the best specialist and best merge on H1, and ties `mono_all` / beats every merge on the trainable grid. RQ1 TR 0.906 [0.878, 0.932]; router == random [−0.008, +0.008]; LOTO fold indistinguishable from `mono_all`. Prefix-cache collision (2026-09-03) fixed, 28 cells quarantined, 13 re-run.

## Hypotheses — open
- **H-mixture** — the gain from an expert mixture is a capacity/ensembling effect, not a dispatch effect. Predicts that mixing N experts with a fixed uniform gate tracks mixing N adapters of any kind, including clean-code ones. The `l0merge` control says this for merging; the uniform/random tie says it for routing.
- **H-scale-floor** — the format floor shrinks with model scale because format failures migrate
  onto items the model cannot solve anyway. Base format_fail is near-identical at the two scales
  (0.179 at 7B, 0.192 at 1.5B) yet repairing it is worth 2-14 % of the gain at 7B and 62-67 % at
  1.5B. Directly testable: partition items by whether `base` format-fails and compare `base`
  accuracy across the partitions at each scale.
- (see [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) for the full ledger)

## Hypotheses — resolved
- **H-breadth-transfers — REFUTED with an interval on CodeLlama, 2026-09-03.** The adapter trained on all six obfuscations is 4.1 pts BELOW the clean-code-only adapter on the unseen obfuscator (+0.0412 [+0.0181, +0.0643] for `tuned_L0 − mono_all`) and ties it on the trainable grid. Breadth bought format, not transfer.
- **H-closest-specialist — WITHDRAWN (unmotivated), 2026-09-03.** Opened on the `tuned_S2` (0.283) > `merge_dare_ties` (0.277) ordering on H1; the program-bootstrap CI on that gap is +0.0066 [−0.0107, +0.0247]. There is no ordering to explain. See `2026-09-03_cis-and-three-corrections.md`.
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
- **Canary re-eval per job** (2026-09-03): re-evaluate one adapter at the END of every eval job and assert ≥95 % raw-output agreement with its first cell. The only guard that compares an adapter against itself across engine state; would have caught the prefix-cache collision on day one.
- (none yet)

## Entries
- [`2026-09-03_h1-repair-clean-code-beats-breadth.md`](2026-09-03_h1-repair-clean-code-beats-breadth.md) — H1 repair read: `tuned_L0` beats `mono_all` +0.041 [+0.018, +0.064], ties best specialist and merge; on the trainable grid the RQ2 ladder collapses onto the clean control; ICL recovers 0.37 of tuning's gain
- [`2026-09-03_prefix-cache-collision.md`](2026-09-03_prefix-cache-collision.md) — vLLM prefix cache keyed on a non-unique `lora_name`; 28 cells contaminated incl. the H1 pilot's `tuned_L0`; RQ2 control column and ICL fractions re-running; Qwen floor fractions unverifiable
- [`2026-09-03_cis-and-three-corrections.md`](2026-09-03_cis-and-three-corrections.md) — cluster-bootstrap CIs on every CodeLlama contrast; three stated findings fail (tuned_L0 "beats"→matches; merge "departure"→noise; LOTO "costs 1.1 pts"→indistinguishable from mono_all); RQ1, routing null and merge-vs-l0merge survive
- [`2026-09-02_h1-codellama-pilot.md`](2026-09-02_h1-codellama-pilot.md) — H1 pilot: clean-code result reproduces, merge result inverts; the format floor is worth nothing on H1
- [`2026-09-02_codellama-master-report-tranches.md`](2026-09-02_codellama-master-report-tranches.md) — routing worth nothing (router == random); capacity not the cause of breadth failure; RQ3 mechanism reproduces; a Grid B/Grid A mixup caught by sample size
- [`2026-09-01_codellama-replication.md`](2026-09-01_codellama-replication.md) — every RQ1/RQ2 finding reproduces on CodeLlama; TR 0.906, LOTO price −0.0108
- [`2026-08-30_format-floor-and-a-collapsed-control.md`](2026-08-30_format-floor-and-a-collapsed-control.md) — H-format refuted at 7B / supported at 1.5B; a mode-collapsed control faked the target signature
- [`2026-08-30_7b-rq1-matrix.md`](2026-08-30_7b-rq1-matrix.md) — 7B RQ1 transfer matrix; TR = 0.885; H-mem refuted, H-format opened.

## Doc / results links
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
