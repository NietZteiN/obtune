# 2026-09-14 — CodeLlama-13B backward on stacks: breadth unreadable, merge above base for the fourth time

**Thread:** transfer · **Status:** fifth model complete (96 cells) · **Extends:** [`2026-09-14_backward-dissociation-three-of-four.md`](2026-09-14_backward-dissociation-three-of-four.md)

| arm | seen (6) | unseen inside (4) | change | gate |
|---|---|---|---|---|
| `base` | 0.092 | 0.074 | −20.3 % | ok |
| `tuned_L0` | 0.110 | 0.086 | −21.2 % | ok |
| `mono_all` | 0.011 | 0.002 | −82.4 % | **gated 0.92** |
| `cons_lam3` | 0.063 | 0.051 | −20.1 % | **gated 0.29** |
| `tuned_X1` | 0.034 | 0.020 | −40.3 % | **gated 0.72** |
| **`merge_dare_ties`** | **0.129** | **0.100** | −22.5 % | ok |

**Breadth is unreadable here too** — 92 % of its backward stack replies are format-gated, the worst
rate of any model. So after five models the count is: the backward dissociation is **readable on three
and replicates on all three** (CodeLlama-7B, Granite, CodeGemma), and **unreadable on two**
(CodeLlama-34B, CodeLlama-13B). No model contradicts it.

Note which models are unreadable: both are the larger CodeLlamas, the same lineage where the claim
*is* readable at 7B. Model size within a lineage predicts the collapse better than lineage does, which
is consistent with the forward-collapse rate rising with capacity everywhere it can be measured.

**The merge is above the untuned model on all four readable models** — 0.129/0.100 here against
0.092/0.074 — and has never been format-gated on any of the five. It is the only arm in the project
with that record, and it makes the merge the most robustly measurable arm backwards as well as the
strongest.

Three models remain.
