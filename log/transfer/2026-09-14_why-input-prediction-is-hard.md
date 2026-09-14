# 2026-09-14 — Why input prediction is hard: not the prompt, not the grader, mostly capacity

**Thread:** transfer · **Status:** diagnosed · **Follows:** [`2026-09-14_backward-grader-audit.md`](2026-09-14_backward-grader-audit.md), [`2026-09-13_backward-task-is-many-to-one.md`](2026-09-13_backward-task-is-many-to-one.md)

## Not the prompt

On CodeLlama-7B, base, L0 (1,671 items):

| check | value |
|---|---|
| format failure | 0.024 |
| reply parses as a call | 0.976 |
| **correct arity** | **0.984** |
| **correct arity and argument types** | **0.936** |
| exact arguments | 0.096 |

The model reads the signature and emits a well-formed, correctly-typed call 94 % of the time. Whatever
is failing is not the instructions, the format or the parser. Error categories agree: 1,101
`wrong_value`, 54 `call_raised`, 40 `unparseable` — the calls run, they return the wrong thing.

## Partly the task, and partly not reading the question

Two behaviours show the model often is not inverting at all.

**It falls back on canned inputs.** The most frequent predictions are `[1, 2, 3, 4, 5]` (50×), `10`
(39×), `[1,...,10]` (28×), `[1, 2, 3]` (26×), `"hello"` (16×) — about 11 % of all predictions are one
of a handful of toy values.

**It often ignores the value it was asked to invert.** Every program appears three times with three
different gold outputs (87 % of programs have three distinct ones). The share of programs where the
model gives the *identical* prediction for all three:

| system | identical for all 3 | three distinct |
|---|---|---|
| base | 0.195 | 0.504 |
| tuned_L0 | 0.217 | 0.487 |
| cons_lam3 | 0.243 | 0.436 |
| merge_dare_ties | 0.188 | 0.532 |

So roughly one program in five gets a reply that is a function of the *program alone*. Note the
anchored arm is the worst on this (0.243) and the merge the best (0.188) — consistent with their
backward ranking.

## Mostly capacity — and this is the finding that matters

Untuned models, L0. **Backward nearly doubles from 7B to 34B while forward does not move at all.**

| model | params (B) | forward | backward exec | backward exact |
|---|---|---|---|---|
| CodeLlama-7B | 6.7 | 0.257 | 0.285 | **0.096** |
| CodeLlama-13B | 13.0 | 0.252 | 0.418 | **0.145** |
| CodeLlama-34B | 33.7 | 0.254 | 0.466 | **0.156** |
| Llama-3.1-8B | 8.0 | 0.258 | 0.424 | 0.115 |
| Gemma-3-12B | 12.2 | 0.334 | 0.491 | **0.169** |
| CodeGemma-7B | 8.5 | 0.237 | 0.289 | 0.080 |
| Granite-3.1-8B | 8.2 | 0.285 | 0.410 | 0.121 |

A prompt ceiling would not lift with capacity. This one does, by 62 % in exact arguments across one
lineage at fixed prompt, fixed grader and fixed items, while the forward task on the same models and
the same programs is flat at 0.25. Input prediction is simply a harder inference that larger models do
better.

## The consequence for the paper, and it is not comfortable

**The reversal test is measured on CodeLlama-7B, which is the weakest backward model in the panel** —
0.096 exact against Gemma-3's 0.169 and 34B's 0.156. The direction ratio is therefore computed exactly
where the backward signal is smallest, and "every method that fits the forward task pays backward
competence" rests on the model least able to demonstrate otherwise.

Moving the test is only partly possible today. Backward format failure on the tuned arms (L0):

| model | base | tuned_L0 | mono_all | cons_lam3 | tuned_X1 |
|---|---|---|---|---|---|
| CodeLlama-7B | 0.02 | 0.07 | 0.02 | 0.01 | 0.03 |
| CodeLlama-13B | 0.03 | 0.09 | **0.92** | **0.55** | **0.68** |
| CodeLlama-34B | 0.03 | **0.51** | **0.26** | **0.56** | 0.20 |
| Gemma-3-12B | 0.02 | 0.25 | 0.05 | **0.62** | 0.01 |
| Llama-3.1-8B | 0.07 | 0.10 | **0.47** | **0.51** | 0.11 |

CodeLlama-7B is the **only** model whose five arms all clear the gate — which is why the test lives
there, and the reason is the one-shot inverse template being 7B-specific, not a property of the arms.
So the honest position is: the reversal result is sound on 7B and cannot currently be replicated
elsewhere, because on every other model the comparison arms stop answering in the required format.

**The experiment that fixes this** is a per-model adaptation of the inverse template, validated on
format rate before any number is read — the follow-up already recorded on 2026-09-13 and still not
run. Until then the reversal test is one model deep for a reason that is about the instrument, and the
paper should say so rather than presenting 7B as a representative choice.
