# 2026-09-14 — Input prediction examined: one harness defect fixed, three non-defects measured and left alone

**Thread:** transfer · **Status:** re-grade applied on all eight models; every backward reader now uses it · **Scripts:** [`71_backward_defects.py`](../../scripts/analysis/71_backward_defects.py), [`72_regrade_inverse.py`](../../scripts/analysis/72_regrade_inverse.py) · **Asked for by the user:** "examine and fix the input prediction stuff"

## Every backward format failure on the panel, sorted by what would fix it

1,810,704 backward trials across all eight models, 23 conditions, seven arms; 307,555 are format
failures (17.0 %). Each one classified by remedy:

| kind | of all trials | of failures | verdict |
|---|---|---|---|
| valid call on line 1, then kept generating | 1.26 % | 7.4 % | **harness defect — fixed** |
| truncated at the 128-token cap | 3.05 % | 18.0 % | model failure mode — left alone, see below |
| expression instead of a literal (`2*3`, `-30829 + 30829`, `pi`) | 0.74 % | 4.3 % | rejected by design — stays rejected |
| keyword arguments (`f(a=1, b=2)`) | 0.10 % | 0.6 % | too rare for the code it needs |
| answered the FORWARD question | 5.17 % | 30.4 % | a result, not a defect |
| nothing call-shaped | 6.65 % | 39.2 % | the failure the gate exists to catch |

## The defect

The backward prompt asks for **one call on one line**. Every backward config inherited the forward
stop list — `"\n\n"`, fences, `<end_of_turn>` — and none added `"\n"`. A model that writes the call
and then opens a fresh `Language: python / Program:` block produced a multi-line reply, and
`inverse.extract_call` refuses multi-line replies **by design** (its docstring: hunting for a call
inside prose would repair the failure it exists to report). Correct design, wrong stop list.

22,893 replies on the panel. **21,140 of them are one arm: CodeGemma's TIES merge, where they are
65 % of ALL its trials** — the whole reason that arm was declared unreadable on that model.

**Fix, in three places.** `"\n"` added to the stop list of all 15 `task: input` configs (safe:
0 of 68,310 sampled replies begin with a newline). Existing cells re-graded on their first line by
`72_regrade_inverse.py` — which is the *identical* measurement a `"\n"` stop would have returned,
not a search inside prose: a prose first line still fails, an expression still fails, a keyword call
still fails. Written as `trials_v2.parquet` / `cell_meta_v2.json` beside the untouched originals, so
v1 and v2 stay comparable; `cellkit.trials_path` prefers v2 wherever it exists, and
`OBTUNE_INVERSE_GRADE=v1` forces the originals.

**Effect.** 1,795 backward cells scanned, 153 got a v2, 24,112 rows re-graded, **25 gates lifted,
30 cells moved by ≥ 0.02 — all but a handful CodeGemma `merge_ties`, 0.063 → 0.254 pooled.** Every
other model×arm moves by less than 0.02.

## The non-defects, with the numbers that say why they were left alone

**Truncation looked like the biggest fixable item and is not one.** Gold calls tokenised with the
CodeLlama tokenizer: median 14 tokens, p90 28, **p99 64, and 0.21 % exceed 128**. The cap already
covers every answer that can be right. Of 2,517 truncated outputs sampled, **38 % are loops** (≤ 6
distinct tokens in the last 40) and the rest are enumerations (`[1, 2, 3, …, 33`), pretty-printed
multi-line literals, or calls that embed the obfuscated helpers (`_rs([209], 176), …`) — none of
which is a literal call. Raising `max_tokens` would let loops loop longer. It stays at 128 and
truncation is reported as what it is: the model enumerating or looping instead of answering.

**Keyword arguments** would need reordering against the function signature; at 0.10 % of trials the
code is not worth its risk. **Expressions** are the grader's deliberate line and stay on it: a model
that copies an MBA constant rather than simplifying it has not found the input.

## What changed in the results, and what did not

*Forward collapse:* **unchanged to three decimals** on every arm — it reads the raw reply, which the
re-grade does not touch. Panel means stay untuned 0.007, merges 0.000/0.001, breadth 0.070,
anchored 0.172.

*Backward stacks, level against the untuned model, exact arguments* (`65_backward_stacks.py`):
the only arm that moves is CodeGemma's TIES merge, **gated → +1.90 [+1.4, +2.5]\***. With that cell
readable and the 34B ties stacks landed in the meantime, **`merge_ties` is now positive on all
eight models, significant on seven, gated on none** — +0.42, +0.70\*, +2.08\*, +1.25\*, +6.21\*,
+0.94\*, +1.90\*, +2.35\* — the same pattern as DARE-TIES. The two merge recipes now agree on every
model, which retires the one caveat that entry carried ("nothing should lean on a single recipe").

*Merge backward on the ladder* (`62_merge_backward.py`), backward gain against the untuned model:

| model | `merge_dare_ties` v1 → v2 | `merge_ties` v1 → v2 |
|---|---|---|
| CodeLlama-7B | +3.21\* → +3.21\* | −0.30 → −0.30 |
| CodeLlama-13B | +4.18\* → +4.18\* | +0.71 → +0.71 |
| CodeLlama-34B | +4.40\* → +4.40\* | +4.43\* → +4.43\* |
| Llama-3.1-8B | +2.00\* → +2.00\* | +2.42\* → +2.42\* |
| StarCoder2-15B | +7.72\* → +7.60\* | +5.60\* → +5.48\* |
| Gemma-3-12B | +2.31\* → +2.31\* | +2.36\* → +2.36\* |
| CodeGemma-7B | +6.25\* → +6.20\* | **gated → +2.63 [+1.43, +3.80]\*** |
| Granite-3.1-8B | −0.27 → −0.27 | +6.94\* → +6.94\* |

One cell changes: CodeGemma's TIES merge, from unreadable to a significant gain with direction ratio
+0.23. Two others move by a tenth of a point (StarCoder2, where a handful of first-line calls were
rescued). Every other number is identical. **`merge_ties` on the ladder is now positive on seven of
eight, significant on six, gated on none**, where before the fix it was gated on one.

## What this does not fix

Input prediction is still hard: the best exact-argument accuracy on any stack is 0.134. The
decomposition says most of that is real — 6.65 % of trials are nothing call-shaped, 5.17 % answer
the other question, 3.05 % loop or enumerate — and the one thing that was the harness's fault
accounted for 1.26 % of trials, concentrated in a single arm. The task is genuinely different from
the one the adapters were trained on, and the fixed measurement says so more cleanly, not less.
