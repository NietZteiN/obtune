# 2026-09-14 — Backward on stacks, all eight models, paired: the dissociation is 3 of 4, not 4 of 5

**Thread:** transfer · **Status:** complete (8/8) · **Supersedes the numbers in:** [`2026-09-14_backward-stacks-seven-models.md`](2026-09-14_backward-stacks-seven-models.md), [`2026-09-14_backward-stacks-fifth-model.md`](2026-09-14_backward-stacks-fifth-model.md) and [`2026-09-14_backward-dissociation-three-of-four.md`](2026-09-14_backward-dissociation-three-of-four.md) — none amended

StarCoder2's backward-stack evaluation landed, completing the eight-model set. Rather than extend
the ad-hoc table by one row I reimplemented the read as a committed script,
[`scripts/analysis/65_backward_stacks.py`](../../scripts/analysis/65_backward_stacks.py), and the
numbers moved. **Two methodological faults in the previous three entries:**

1. **The program sets were not intersected.** The stacks containing the unseen family cover fewer
   programs (X1 needs ≥ 3 sites), so pooling them against the seen stacks compared two different
   program sets and called the difference a drop. Script 57 does the forward version of this
   comparison on the intersection; the backward version did not.
2. **The drops were compared as two point estimates.** "Breadth falls 2.6× further than base" was
   read off two numbers with no interval on their difference, on a metric whose per-cell values sit
   between 0.04 and 0.09 — differences of small differences, exactly what CLAUDE.md §4 says to bound.

The script fixes both: one common program set across every cell of both groups (n = 319 on every
model), and a program-clustered bootstrap (2,000 resamples, seed 17) on the **difference between a
system's drop and the untuned model's**. Stack groups are script 57's, so forward and backward are
now read on the same columns.

## Exact-argument accuracy, relative drop seen → unseen-containing

| model | `base` | **`mono_all`** | `cons_lam3` | `tuned_X1` | `tuned_L0` | `merge_dare_ties` |
|---|---|---|---|---|---|---|
| CodeLlama-7B | −15.0 % | **−40.0 %** \* | −0.9 % | −10.4 % | gated | −15.4 % |
| CodeLlama-13B | −16.8 % | gated | gated | gated | −16.7 % | −15.5 % |
| CodeLlama-34B | −4.4 % | gated | gated | gated | +10.3 % \* | −4.6 % |
| Llama-3.1-8B | −15.1 % | **−42.2 %** \* | −32.6 % \* | +1.0 % | −14.8 % | −20.5 % |
| StarCoder2-15B | gated | gated | gated | gated | gated | −10.2 % |
| Gemma-3-12B | −17.4 % | −25.3 % | gated | −3.2 % \* | −15.4 % | −12.9 % |
| CodeGemma-7B | −21.8 % | **−50.7 %** \* | gated | +1.1 % \* | −22.3 % | −20.1 % |
| Granite-3.1-8B | gated | −61.6 % | gated | −14.4 % | gated | −19.7 % |

\* the system's drop differs from the untuned model's at 95 %. Where `base` is itself gated
(StarCoder2, Granite) **no contrast is formed and no star can appear** — a gated untuned model is a
drop in parse rate, not a reference. The earlier entries quoted a Granite base of −12.1 % and a
ratio of 4.3×; on the intersected set Granite's base is format-gated and that ratio does not exist.

## What now stands

- **Breadth loses backward competence under an unseen family faster than the untuned model on three
  of the four models where both are readable** — CodeLlama-7B, Llama-3.1-8B, CodeGemma — and not
  significantly on the fourth (Gemma-3, −25.3 vs −17.4). Granite's −61.6 % is the largest drop
  measured but has no reference. Direction is consistent on all five models where breadth is
  readable; none contradicts.
- **By execution grading the same comparison is 2 of 4** (CodeLlama-7B, CodeGemma), with
  Llama-3.1-8B in the right direction and not significant. Execution accepts any call returning the
  gold value, so it is the looser metric; both reads are in
  `results/analysis/pipeline/backward_stacks_{args_exact,correct}.json`.
- **The merge is the most robust arm and the claim is now stronger than it was.** It is never gated
  on any of the eight models — including StarCoder2 and Granite, where the untuned model and every
  tuned arm fail the format contract — and its drop never differs significantly from base on any
  model where base is readable (−4.6 % to −20.5 %). On StarCoder2 the merges are the *only* readable
  backward systems at all, scoring 0.29–0.45 where base cannot be parsed.
- **The anchored arm is readable on two models and disagrees on them, which is unchanged, but the
  7B number moves a long way.** Paired, it is −0.9 % on CodeLlama-7B against base's −15.0 % (better
  than base, not significant) and −32.6 % on Llama-3.1-8B against −15.1 % (worse, significant). The
  previous entry's −17.0 % / −37.1 % pair is superseded. It is gated on the other six.
- **`merge_ties` has no stacked backward cells on any model** — the ladder was evaluated, the stacks
  were not. Only `merge_dare_ties` carries the merge column above.

## Consequence for the paper

RQ1's brittleness claim survives on the backward direction but with a smaller count than the
frozen prose implies: **3 of 4 paired models, not 4 of 5**, and the ratio language ("2.1–4.3×
further") should not be used at all — it was computed from unpaired point estimates and two of its
five rows had a gated reference. Prose stays frozen pending the framing decision; this entry is the
number the prose must be rewritten against.
