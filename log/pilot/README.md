# pilot — Week-1 kill-switch pilot and its gate decision

*Last updated: 2026-08-05*
**Status:** done — gate passed, proceeding to the full arc

## Hypotheses — open
- **H1c (upgraded, not settled):** the L1b adapter's +27.3 pt gain on H1 reflects obfuscation
  invariance rather than task acquisition. CONFIRM if an **L0-trained control adapter** lifts H1
  markedly less; REFUTE if tuning on clean code lifts H1 by a comparable amount.
- **H2c:** conditioning vs capability. Currently inconclusive at 0.26–0.33; the full RQ2 arms decide.

## Hypotheses — resolved
- ✓ **H1a-trainable** SUPPORTED — self-gain +27.3 pts, CI [11.0, 43.2] excludes 0.
- ✓ **H1a (family structure)** SUPPORTED — identifier-family transfer (L2 +33.3) more than double
  structural-family (S1 +15.2).
- ~ **H1c** provisionally supported — H1 +27.3 pts, CI [16.1, 40.9], and +19.2 pts beyond what
  1-shot oracle conditioning recovers. Held open because L0 rose by as much (+29.3).

## What worked
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
- Report `raw_exact` alongside the normalized grader: base format-failure varies 0–21 % by
  condition, so grading choice interacts with condition here in a way it did not in Papers 2–3.
- Strengthen the oracle by drawing its one-shot demo from the eval condition itself.

## Entries
- [`2026-08-05_kill-switch-pilot.md`](2026-08-05_kill-switch-pilot.md) — gate passed; H1 +27.3 pts; L0 control now the priority

## Doc / results links
- [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) §5 verdict box
- [`../../results/analysis/pilot_decision.json`](../../results/analysis/pilot_decision.json)
