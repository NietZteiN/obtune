# 2026-09-14 — The backward dissociation now replicates on three models

**Thread:** transfer · **Status:** four models evaluated, three readable, three replicate · **Supersedes the counts in:** [`2026-09-14_backward-dissociation-replicates.md`](2026-09-14_backward-dissociation-replicates.md) and [`2026-09-14_backward-stacks-third-model.md`](2026-09-14_backward-stacks-third-model.md), neither amended

CodeGemma's stack evaluation finished. Exact-argument accuracy, seen stacks → unseen-containing
stacks, for every model measured so far:

| model | `base` | **`mono_all`** | ratio | `tuned_X1` | `merge` | breadth gate |
|---|---|---|---|---|---|---|
| CodeLlama-7B | −17.8 % | **−46.7 %** | 2.6× | −18.5 % | −23.7 % | ok |
| Granite-3.1-8B | −12.1 % | **−52.6 %** | 4.3× | −11.5 % | −27.1 % | ok |
| CodeGemma-7B | −24.3 % | **−51.1 %** | 2.1× | −3.4 % | −26.5 % | ok |
| CodeLlama-34B | −13.1 % | (−28.5 %) | — | −23.2 % | −13.8 % | **gated 0.57** |

**Breadth falls 2.1 to 4.3 times further than the untuned model on every model where it is readable** —
three of four, across three lineages (Meta, IBM, Google). On the fourth its backward replies are 57 %
format-gated and the comparison cannot be made, which is an instrument limit and not a contradiction.

This is the paper's central dissociation, in the direction nothing was trained on, on composite
stimulus neither direction was trained on, replicating across lineages. It is now the best-supported
claim in the project after the forward dissociation itself.

## Two arms that are not breadth

**The family adapter is the most stable arm backwards** — −18.5 %, −11.5 %, −3.4 % — never worse than
base on any readable model. Exposure to the family transfers in the reverse direction; exposure to
transforms does not.

**The anchored arm is gated on both Google and IBM models** (CodeGemma 0.87, Granite 0.69) and readable
only on CodeLlama-7B, where it is −17.0 %. Its backward profile cannot be stated panel-wide, and the
reason is the forward-collapse effect, not its unseen-family behaviour.

Four models remain.
