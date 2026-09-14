# 2026-09-14 — Breadth's degradation with divergence replicates in the BACKWARD direction, on a second model

**Thread:** transfer · **Status:** two models, both usable · **Follows:** [`2026-09-14_backward-on-stacks.md`](2026-09-14_backward-on-stacks.md)

Granite's backward stack evaluation finished (96 cells). Unlike its L0 cells — where `cons_lam3` was
100 % forward-collapsed — several arms clear the format gate on **stacks**, so the comparison is
readable there. Exact-argument accuracy, seen stacks against unseen-containing stacks:

| model | arm | seen (6) | unseen inside (4) | change | gate |
|---|---|---|---|---|---|
| CodeLlama-7B | `base` | 0.085 | 0.070 | −17.8 % | ok |
| CodeLlama-7B | **`mono_all`** | 0.078 | 0.042 | **−46.7 %** | ok |
| CodeLlama-7B | `cons_lam3` | 0.090 | 0.075 | −17.0 % | ok |
| CodeLlama-7B | `tuned_X1` | 0.100 | 0.082 | −18.5 % | ok |
| CodeLlama-7B | `merge_dare_ties` | 0.106 | 0.081 | −23.7 % | ok |
| Granite-3.1-8B | `base` | 0.075 | 0.066 | −12.1 % | gated 0.27 |
| Granite-3.1-8B | **`mono_all`** | 0.054 | 0.026 | **−52.6 %** | ok |
| Granite-3.1-8B | `tuned_X1` | 0.060 | 0.053 | −11.5 % | ok |
| Granite-3.1-8B | `merge_dare_ties` | 0.077 | 0.056 | −27.1 % | ok |
| Granite-3.1-8B | `cons_lam3` | 0.022 | 0.006 | −71.9 % | gated 0.69 |

**Breadth falls roughly two to four times further than every other readable arm, on both models**
— −46.7 % and −52.6 % against the untuned model's −17.8 % and −12.1 %, the family adapter's −18.5 %
and −11.5 %, and the merge's −23.7 % and −27.1 %. This is the paper's central dissociation, measured
in the direction nothing was trained on, on composite stimulus neither direction was trained on, and
it now replicates across two models and four lineages of evidence (forward ladder, forward stacks,
backward ladder, backward stacks).

Granite matters here because it is the model that **refutes** the anchoring repair forwards (R2
−1.89, significantly reversed) and collapses on `cons_lam3` backwards. That it still shows breadth's
backward degradation separates the two claims cleanly: the dissociation is robust to the model that
kills the method.

## A second, unplanned observation

**Forward collapse is condition-dependent, and weaker on harder input.** On L0, Granite's `mono_all`
is 92 % format-failed; on the six seen stacks it is 6 %, and 20 % on the unseen-containing ones. The
adapter's forward binding is strongest exactly where its forward answer is most confident, and loosens
as the program gets harder to read. That is consistent with the collapse being a confidence effect
rather than a parse failure, and it is why the stack cells are readable where the ladder cells are not.

Six models' stack evaluations are still running.
