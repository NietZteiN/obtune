# human-align — Secondary — human difficulty-ordering alignment

*Last updated: 2026-09-08*
**Status:** **first result, 2026-09-08** — tuning moves the model **away** from human difficulty orderings (Δρ = −0.303 [−0.575, −0.028]); the untuned model is the one that tracks people (+0.82 rank correlation with the human tier gradient, against negative for every tuned arm). Claim C8 is answered.

## Hypotheses — open
- (see [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) for the full ledger)

## Hypotheses — resolved
- ✗ **H-human-shift** → **AWAY** (2026-09-08, `an_human_align`): `tuned_L0 − base` Δρ = **−0.303 [−0.575, −0.028]** on item-level Spearman against human accuracy over the 98 Paper-2 cells. `mono_all` −0.174 and `cons_lam3` −0.244 have the same sign with intervals spanning zero; only `tuned_L0` was verdicted, per the frozen rule.
- ? **H-human-base** INCONCLUSIVE (2026-09-08): base ρ = +0.132 [−0.140, +0.381].
- ▫ **H-human-tier** REPORTED, never verdicted (n = 5): human accuracy falls monotonically across the legacy ladder; `base` tracks it at +0.82 while `tuned_L0` / `mono_all` / `cons_lam3` sit at −0.10 / −0.41 / −0.41 and all three do their best on `T_L3`, the tier humans find hardest.

## What worked
- The blocker was imaginary. E10 was recorded as needing "the Paper-2 item map — a build task that has no script yet"; the map is on disk (`data/human/paper2_graded.csv`, 600 responses / 50 participants / **98 cells, all 98 matching a legacy row**) and only the item emitter was missing. Checking a stale blocker before believing it is the transferable lesson.

## What didn't
- **Power, and no amount of compute fixes it.** 98 cells over 20 programs with **one trial per cell**, because the human study used one input case per item; adding cases would change the item and break the byte-identical comparability that licenses the comparison at all. The one interval that clears zero does so at −0.028.
- The pre-registered grading-sensitivity check was the **wrong instrument** — a text-level regrade is stricter than the pipeline's own canonicalising grader on string-valued golds. Kept and reported as registered, with the right instrument beside it (71.7 % of `base`'s correct answers needed canonicalisation, against 0 % for every tuned arm).

## Open ideas
- (none yet)

## Entries
- [`2026-09-08_tuning-moves-away-from-humans.md`](2026-09-08_tuning-moves-away-from-humans.md) — E10's first read: **AWAY** at item level, and at condition level `base` tracks the human gradient while every tuned arm inverts it.

## Doc / results links
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
