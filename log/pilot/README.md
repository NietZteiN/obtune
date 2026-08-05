# pilot — Week-1 kill-switch pilot and its gate decision

*Last updated: 2026-08-05*
**Status:** done — gate passed; H1 result reinterpreted after the L0 control

## Hypotheses — open
- **H1c-revised:** no training condition yields a *control-relative* gain on H1 whose CI excludes
  zero. The full grid tests this for all six conditions; S1/S2 adapters are the likeliest to break
  it, since H1's MBA rewriting is arithmetic-structural rather than identifier-level.
- **H2c:** conditioning vs capability. Inconclusive at 0.26–0.33 — and to be re-read knowing the
  gain it is a fraction *of* is mostly task acquisition.

## Hypotheses — resolved
- ✓ **H1a-trainable** SUPPORTED — self-gain +27.3 pts, CI [11.0, 43.2] excludes 0.
- ✓ **H1a (family structure)** SUPPORTED — identifier-family transfer (L2 +33.3) more than double
  structural-family (S1 +15.2).
- ✗ **H1c (as originally stated) REFUTED** by its own control. An adapter trained on *clean* code
  reaches H1 at .414 versus .384 for the L1b-trained adapter; the control-relative difference is
  −3.0 pts, CI [−10.5, +3.9]. The +27.3 pt raw gain was task acquisition, not invariance.
- ✓ **Memorization gradient** — obfuscation-specific benefit is significant only on the trained
  condition (L1b +16.2, CI [+4.7, +28.5]), fades on its family (L1r +8.1, ns), and is zero-to-negative
  on L2/S1/S2/H1. Concentrated where trained, absent where held out.

## What worked
- **Running the control.** It cost one 37-minute training run and overturned the headline reading
  before the 54-run grid was launched on a confounded metric — the single highest-value hour so far.
- The kill-switch design paid off immediately: one 39-minute training run plus 28 eval cells
  answered the go/no-go question and surfaced the confound worth chasing.
- Checkpoint selection by held-in val exact match chose epoch 2 over epoch 3 (0.378 vs 0.345) —
  eval loss alone would have kept training.
- Reporting on the all-conditions common subset was load-bearing, not ceremonial: S1 covers only
  74 % of training programs and 33/40 Python test parents.

## What didn't
- The bare oracle prompt *hurt* on H1 (.111 → .081): naming an obfuscation the model has never
  seen, without a demonstration, is worse than saying nothing.
- Transfer Ratio is undefined for every off-diagonal cell in a single-adapter pilot (no `tuned_j`).
  The Invariance Index is therefore raw-points only until the per-condition grid exists.

## Open ideas
- A *format-only* control (base model + format demo, no tuning) would separate "learned the task"
  from "learned the answer format"; the L0 control shares the format with the treatment.
- n=23 common-subset programs cannot resolve effects near ±8 pts (e.g. L1r +8.1). Expanding the
  test set is now the binding constraint on every secondary claim.
- Report `raw_exact` alongside the normalized grader: base format-failure varies 0–21 % by
  condition, so grading choice interacts with condition here in a way it did not in Papers 2–3.
- Strengthen the oracle by drawing its one-shot demo from the eval condition itself.

## Entries
- [`2026-08-05_l0-control-refutes-invariance.md`](2026-08-05_l0-control-refutes-invariance.md) — control refutes the invariance reading; Invariance Index redefined
- [`2026-08-05_kill-switch-pilot.md`](2026-08-05_kill-switch-pilot.md) — gate passed; H1 +27.3 pts; L0 control now the priority

## Doc / results links
- [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) §5 verdict box
- [`../../results/analysis/pilot_decision.json`](../../results/analysis/pilot_decision.json)
