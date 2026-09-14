# 2026-09-14 — CodeLlama-34B backward on stacks: the dissociation is unreadable there, and the merge is the strongest arm measured

**Thread:** transfer · **Status:** third model complete (96 cells) · **Extends:** [`2026-09-14_backward-dissociation-replicates.md`](2026-09-14_backward-dissociation-replicates.md)

Exact-argument accuracy, seen stacks → unseen-containing stacks:

| arm | seen (6) | unseen inside (4) | change | gate |
|---|---|---|---|---|
| `base` | 0.105 | 0.091 | −13.1 % | ok |
| `tuned_L0` | 0.102 | 0.099 | −3.0 % | ok |
| `mono_all` | 0.050 | 0.036 | −28.5 % | **gated 0.57** |
| `cons_lam3` | 0.084 | 0.066 | −21.0 % | **gated 0.29** |
| `tuned_X1` | 0.080 | 0.061 | −23.2 % | ok |
| **`merge_dare_ties`** | **0.140** | **0.121** | −13.8 % | ok |

**Breadth is not readable on this model** — 57 % of its backward stack replies fail the format gate, so
its −28.5 % cannot be used. The backward dissociation therefore stands on **two of the three models
measured so far** (CodeLlama-7B −46.7 %, Granite −52.6 %), and is untestable on the third rather than
contradicted. That distinction belongs in the writing: it is a limit of the instrument on 34B, the
same forward-collapse effect recorded separately, not a failure to replicate.

**The merge is the strongest backward arm measured anywhere in the project** — 0.140 on seen stacks and
0.121 with an unseen family inside, against the untuned model's 0.105/0.091 and every SFT arm below
both. It is above base on both groups here, as it was on CodeLlama-7B and Granite: three models, three
times above base, never gated.

`tuned_L0` is nearly flat (−3.0 %), which is the opposite of its behaviour on CodeLlama-7B, where it
was the worst arm and fell with depth. Two models disagree on the clean adapter's backward profile; no
claim should rest on it.

Five models' stack evaluations remain.
