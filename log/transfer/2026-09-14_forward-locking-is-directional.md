# 2026-09-14 — The control: nothing answers backward when asked forward

**Thread:** transfer · **Status:** control for [`2026-09-14_forward-locking-is-the-mechanism.md`](2026-09-14_forward-locking-is-the-mechanism.md) · **Script:** `scripts/analysis/67_backward_failure_modes.py --aggregate`

"The tuned arms answer the other question" is only a claim about direction if the confusion runs one
way. If these arms had simply muddled the two tasks, the mirror image would show the same thing:
forward replies shaped like a *call* rather than like a value. It does not.

**Share of FORWARD replies that parse as a single call** — the backward answer's form — on the same
arms and nine of the same conditions:

| model | `base` | `tuned_L0` | `mono_all` | `cons_lam3` | `tuned_X1` | `merge_dare_ties` | `merge_ties` |
|---|---|---|---|---|---|---|---|
| CodeLlama-7B | 0.0115 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0002 |
| StarCoder2-15B | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| CodeGemma-7B | 0.0003 | 0.0000 | 0.0001 | 0.0002 | 0.0000 | 0.0001 | 0.0005 |
| Granite-3.1-8B | 0.0023 | 0.0002 | 0.0002 | 0.0000 | 0.0000 | 0.0003 | 0.0013 |

Every cell is under 1.2 %, and the **largest value on every model is the untuned one** — the opposite
of the backward direction, where the untuned model is the floor at 0.004 and the tuned arms run to
0.31. Against the tuned arms' backward collapse rates of 0.110 to 0.312 this is two orders of
magnitude.

**So forward-locking is directional, not task confusion.** Fine-tuning on output prediction makes a
model answer the output question when it is asked the input question, and does not make it answer
the input question when asked the output one. That asymmetry is the thing worth reporting: a
symmetric muddle would be a prompt problem, and this is not one.

It also rules out the cheapest alternative explanation of the merge result. If the merges' zero
collapse rate came from their replies being differently shaped in general, they would show up here;
they are at the same floor as everything else.
