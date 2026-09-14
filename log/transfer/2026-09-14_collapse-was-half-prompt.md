# 2026-09-14 — Half of this morning's forward-collapse numbers were the missing demo, and the result survives anyway

**Thread:** transfer · **Status:** corrected on all eight models · **Corrects the magnitudes in:** [`2026-09-14_forward-locking-is-the-mechanism.md`](2026-09-14_forward-locking-is-the-mechanism.md), which is not amended · **Cause:** [`2026-09-14_two-prompts-one-phase.md`](2026-09-14_two-prompts-one-phase.md)

The forward-collapse panel means published this morning pooled over **all sixteen backward
conditions**, seven ladder and nine stacks. Every stack cell was evaluated with the one-shot inverse
prompt; the ladder cells on the seven non-CodeLlama-7B models were not. So those means were part
measurement and part prompt, and I did not notice because the prompt fault and the collapse result
were found within an hour of each other.

## How much the demo was doing

Ladder conditions only, the same adapters and items, zero-shot → one-shot (from the
`inverse_1shot` repair, first two models to complete):

| model | arm | 0-shot | 1-shot |
|---|---|---|---|
| CodeGemma-7B | `tuned_L0` | 0.542 | **0.001** |
| CodeGemma-7B | `mono_all` | 0.777 | **0.029** |
| CodeGemma-7B | `tuned_X1` | 0.649 | **0.091** |
| CodeGemma-7B | `cons_lam3` | 0.966 | **0.695** |
| CodeLlama-34B | all four tuned arms | 0.035–0.087 | 0.004–0.023 |
| both | `base` | 0.000 | 0.000 |

Without a worked example most tuned arms simply answer the forward question. With one they stop —
**except the KL-anchored arm**, which still collapses on 70 % of CodeGemma's ladder items.

## The corrected numbers

Recomputed on the **sixteen stack conditions only**, which were written with one prompt on every
model and arm, so nothing here is contaminated. All eight models:

| arm | this morning (mixed prompts) | **corrected (stacks only)** |
|---|---|---|
| `base` | 0.004 | **0.007** |
| `merge_ties` | 0.000 | **0.000** |
| `merge_dare_ties` | 0.001 | **0.001** |
| `tuned_X1` (family) | 0.110 | **0.060** |
| `tuned_L0` (clean) | 0.135 | **0.066** |
| `mono_all` (breadth) | 0.198 | **0.081** |
| `cons_lam3` (anchored) | 0.312 | **0.186** |

**The ordering is identical and every qualitative claim survives.** Both merges sit at the untuned
floor; every single-adapter arm is above it; the KL-anchored arm is highest, now by a factor of 2.3
over the next arm rather than 1.6. What changes is the size: the single-adapter rates are roughly
halved, so "breadth answers the forward question on a fifth of backward items" becomes "on a
twelfth", and that is the number the paper must use.

The merges are unaffected in both readings because they were always one-shot, and `base` is
unaffected because it barely responds to the demo at all — which is itself the reason the confound
was survivable.

## Changes made

`67_backward_failure_modes.py --aggregate` now defaults to the stack set, with `--conds ladder|all`
available and documented as dishonest until the repair lands everywhere. The generated
`tables/master_collapse.tex` is regenerated from the corrected json.

## What I got wrong, and the general lesson

I published a panel mean the same morning I discovered that the phase it reads from holds two
prompts, and did not check whether the metric I was introducing crossed that boundary. The check
took four minutes once asked. The rule that would have caught it is the one `cellkit.check_one_prompt`
now enforces for pooled reads and contrasts — but `67` computes its own aggregate and never calls
it, exactly as `62_merge_backward.py` did. **A guard that only works when a script opts in is not a
guard.** Worth making `cell_path`-style helpers carry it, rather than hoping each new script
remembers.
