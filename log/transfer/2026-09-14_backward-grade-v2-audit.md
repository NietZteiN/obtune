# 2026-09-14 — Audit of the v2 backward grade, and why input prediction reads as harder

**Thread:** transfer · **Status:** audit passed; one suspected false-negative class checked and rejected · **Required by:** CLAUDE.md §4 item 5 (sample-audit graded trials for any new grading) · **Asked by the user:** "Is our new grading accurate?" / "Why is input prediction so much harder?"

## Is v2 accurate? Four checks

**1. Population statistics.** All 24,112 re-graded rows on the panel: 0 remain format failures (by
construction — only a valid first-line call is re-graded); execution ok 22,285, raised 1,756,
timeout 36, unserializable 35. **Correct by execution 0.286, exact arguments 0.087 — the same rates
as ordinary backward rows on the panel.** If first-line extraction were a lenient bucket, these
would sit above the population. They do not.

**2. What line 2 was.** Of the re-graded rows, line 2 begins `Language: py…` in 16,813, `user` in
3,423, `Return value` in 2,133, `Entry point:` in 351. That is a model starting a fresh prompt block
after answering, not a call continued onto a second line. A continued call (`f_eff8([\n (1, 1),…`)
has a first line with no closing paren, fails `extract_call`, and is **not** re-graded.

**3. Thirty rows by eye.** Every first line is a single call; every row marked correct executes to
the gold value (`f_9bff("mkwgl")` → `"++++mkwgl++++"`, `reverse_factorial(120)` → `"5!"`); every
row marked wrong is wrong (`digits(123)` → `3` against `315`; `maxKBitFlips([0,0,0], 1)` → `3`
against `0`). Rows credited by execution but not exact-arguments are the many-to-one case the grader
is designed to accept (`f_8179([1, 2, 3])` → `true`, gold `true`, different arguments).

**4. One suspected false-negative class, checked and rejected.** `reverseVowels("hello")` executed
to `"holle"` and was marked wrong against a gold of `"\"holle\""`. Probed across 12,890
executed-but-wrong rows on two models: 26 (0.20 %) would flip if the gold were JSON-decoded once
more. They should not flip. The gold is a string *containing* quote characters — the program
returns `'"holle"'` — and the model's call returned `holle`. Different values; the grader is right.

**Verdict: v2 is accurate.** It is the measurement a `"\n"` stop would have produced, its rescued
rows behave exactly like the population, and the one anomaly a reviewer would spot is the grader
being correct.

## Why input prediction reads as harder — the honest decomposition

CodeLlama-7B, ladder, v2 grade:

| arm | forward | backward by execution | backward exact args | format fail | raised | **executes, wrong value** | correct |
|---|---|---|---|---|---|---|---|
| untuned | 0.196 | **0.287** | 0.089 | 0.042 | 0.065 | **0.606** | 0.287 |
| breadth | 0.375 | 0.273 | 0.084 | 0.039 | 0.046 | **0.641** | 0.273 |
| DARE-TIES merge | 0.375 | 0.326 | 0.112 | 0.042 | 0.048 | **0.584** | 0.326 |

Three things fall out of that row, and they are different answers to "why harder".

**For the untuned model, input prediction by execution is not harder. It is easier.** 0.287 backwards
against 0.196 forwards on the same programs. The panel agrees: untuned backward-by-execution is
0.25–0.42 on every model, forward on the ladder is 0.20–0.28. So "much harder" is not a fact about
the task as graded by execution.

**What is hard is exact recovery, and that is because the task is underdetermined.** Exact
arguments run 0.06–0.13 for every arm. 21.5 % of the ladder's gold return values are `None`, a
boolean, an empty container or an integer in −3..3 — values with many pre-images — and even on the
other 78.5 % the untuned exact-argument rate is only 0.096. Inversion is many-to-one; grading by
execution is the right instrument, and "exact arguments" is a secondary column that will always be
low for reasons that have nothing to do with the model.

**The dominant failure is a well-formed call that returns the wrong value.** 52–64 % of every
model's backward attempts parse, execute cleanly, and return something other than the gold. Format
failure is 2–8 % on six of eight models; exceptions 5–8 %. The model proposes an input of the right
shape and arity (98.4 % arity, 93.6 % types, measured earlier) and cannot work out which input maps
to the given output. That is the sense in which inversion is a different skill: it needs the model
to run the function backwards, and it runs it forwards on a guess instead.

**And the tuned arms make it worse, not better.** Breadth doubles forward accuracy (0.196 → 0.375)
and *loses* ground backwards (0.287 → 0.273). Every single-adapter arm on the panel does this. The
merge is the exception at 0.326. So the "much harder" that the paper is about is not the task's
difficulty — it is that forward training buys nothing backwards, which is exactly what a surface fit
to the forward mapping predicts and what the backward-trained control now queued (a30 398428) will
test directly.

## The master table under v2

Regenerated and the paper rebuilt (`master_abs_codellama7b.tex`, Section 4). **CodeLlama-7B's table
did not change**: of 22 re-graded 7B cells, the 8 that moved by ≥ 0.005 are all hidden-state
alignment arms (`align_lam0.3`, `align_lam1`) that are not among the table's eight methods. The
model whose table changed is CodeGemma, where the TIES merge went from gated everywhere to readable
(0.063 → 0.254 pooled) — the one arm the missing stop was crippling.
