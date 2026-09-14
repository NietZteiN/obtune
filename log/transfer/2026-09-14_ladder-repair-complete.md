# 2026-09-14 — The ladder repair is complete on all eight models, and StarCoder2 becomes readable

**Thread:** transfer · **Status:** 8/8 one-shot · **Closes:** [`2026-09-14_two-prompts-one-phase.md`](2026-09-14_two-prompts-one-phase.md), [`2026-09-14_the-reversal-was-the-prompt.md`](2026-09-14_the-reversal-was-the-prompt.md), [`2026-09-14_collapse-was-half-prompt.md`](2026-09-14_collapse-was-half-prompt.md)

Every model's backward ladder now exists under the one-shot prompt: seven re-read into phase
`inverse_1shot` (five arms plus both merges, 49 cells each) and CodeLlama-7B, which was always
one-shot. `cellkit`'s registry reports **no mixed-prompt arm on any model**, so the 23-condition
reads are honest again and `67_backward_failure_modes.py` is back to `--conds all` by default.

## Forward collapse, final: 23 conditions, 8 models

| arm | 23-condition (final) | 16-stack cross-check | this morning (contaminated) |
|---|---|---|---|
| `base` | **0.007** | 0.007 | 0.004 |
| `merge_ties` | **0.000** | 0.000 | 0.000 |
| `merge_dare_ties` | **0.001** | 0.001 | 0.001 |
| `tuned_X1` (family) | **0.052** | 0.060 | 0.110 |
| `tuned_L0` (clean) | **0.059** | 0.066 | 0.135 |
| `mono_all` (breadth) | **0.070** | 0.070*† | 0.081 |
| `cons_lam3` (anchored) | **0.172** | 0.186 | 0.312 |

The full read and the stacks-only stopgap agree closely, which is the check that the stopgap was
not itself distorting anything. Use the first column. **Both merges sit at the untuned floor on
every one of the eight models; the KL-anchored arm is 25× the untuned rate and 2.5× the next arm.**

## `62_merge_backward.py`, re-read on repaired cells

| model | `merge_dare_ties` bwd | `merge_ties` bwd | `mono_all` bwd |
|---|---|---|---|
| CodeLlama-7B | **+3.21** [+1.52, +4.85] \* | −0.30 | −0.74 |
| Llama-3.1-8B | **+2.00** [+0.36, +3.79] \* | **+2.42** [+1.37, +3.49] \* | **−7.74** \* |
| StarCoder2-15B | **+7.72** [+5.95, +9.46] \* | **+5.60** [+4.13, +6.97] \* | **−5.54** \* |
| Granite-3.1-8B | −0.27 [−2.33, +1.83] | **+6.94** [+5.29, +8.64] \* | **−4.72** \* |

**Breadth is significantly negative backwards on three of the four models with a readable contrast.**
Across the eight merge×model cells the merges are significantly positive on six, null on two, and
negative on none.

## StarCoder2 has a backward contrast for the first time

Its untuned model now clears the format gate on `L0` and `L2` under the one-shot prompt, where under
the zero-shot one it cleared none. That model has been "unreadable backwards" in every previous
entry, and it was the prompt. On the two readable conditions **every arm is positive backwards** and
the merges are highest (+7.72, +5.60), with breadth the only significantly negative one (−5.54).

Note the forward figures on that model are against a floor: its untuned forward accuracy on the
ladder is 0.000, so `+50.27` means "the merge gets half the items and the untuned model gets none",
not a 50-point improvement over a working baseline. That belongs in the caption wherever StarCoder2
appears.

## Still missing

The mixture column, in both directions. Five backward jobs are running, CodeLlama-7B's single
missing forward cell (X1) is requeued at a smaller batch after an OOM, and three router gates are
still training. Its prediction is registered in `CLAUDE_SCRATCHPAD.md`.
