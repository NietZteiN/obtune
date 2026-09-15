# 2026-09-14 — Llama-3.1-8B is not weak forward; its strong backward score is trivial return values

**Thread:** transfer · **Prompted by:** user, "why is llama so shit at output prediction but so good at
input prediction" · **Data:** `results/analysis/pipeline/base_fwd_vs_bwd_by_model.json`,
`backward_arms_llama_vs_7b.json` · untuned models, 15 conditions (5 singles, X1, 6 seen stacks, 3 unseen
stacks), 21.7k forward and 21.7k backward items per model.

## The premise is half wrong

Forward, Llama-3.1-8B is not worse than the CodeLlama-7B reference. Untuned: 0.186 against 0.164
pooled; on the master table's single-obfuscation row 0.219 against 0.194, and its tuned arms land at
0.39–0.43 against 0.38–0.40. It is an ordinary member of the panel forward.

What is true is that it reads **unusually strong backward untuned** — 0.331 by execution, second only
to Gemma-3 — and that **every single-adapter arm goes red backwards** on its table where CodeLlama-7B's
stay at or above base. Both come from the same place.

## Where the backward score comes from

Backward is graded by execution: any call that returns the gold value is correct. 15.3 % of the
backward items have a **trivial gold** — the return value is `0`, `1`, `-1`, `None`, `True`, `False`,
`[]`, `''`, `{}` or `()`. A model that writes a well-formed call with small generic literals hits those
without inverting anything.

| untuned model | backward, exec | on trivial golds | on the rest | by exact args | degenerate share |
|---|---|---|---|---|---|
| CodeLlama-7B | 0.285 | 0.368 | 0.270 | 0.084 | 70.6 % |
| **Llama-3.1-8B** | **0.331** | **0.547** | 0.292 | 0.086 | **74.0 %** |
| Gemma-3-12B | 0.384 | 0.634 | 0.339 | 0.116 | 69.9 % |
| CodeLlama-34B | 0.326 | 0.489 | 0.297 | 0.107 | 67.2 % |

Llama's 4.6-point lead over CodeLlama-7B by execution is **almost entirely the trivial-gold items**:
0.547 against 0.368 there, 0.292 against 0.270 on the rest. **By exact arguments the two are the same
model: 0.086 against 0.084.** 74 % of Llama's execution-graded backward successes do not recover the
gold arguments, the highest share on the panel. It is not better at inversion; it is better at writing a
plausible call whose small arguments happen to produce a common return value — the fluency of an
instruction-tuned general model, which the execution grader pays for.

## Why its tuned arms go red backwards

Forward tuning removes exactly that habit. On Llama, every single-adapter arm drops the trivial-gold
backward rate from 0.547 to 0.35–0.37 while leaving the non-trivial rate where it was (0.26–0.28
against 0.292):

| Llama-3.1-8B arm | exec | on trivial golds | on the rest | exact args |
|---|---|---|---|---|
| base | 0.331 | 0.547 | 0.292 | 0.086 |
| clean LoRA | 0.292 | 0.355 | 0.281 | 0.084 |
| breadth | 0.272 | 0.352 | 0.257 | 0.074 |
| anchored | 0.281 | 0.365 | 0.265 | 0.078 |
| router | 0.307 | 0.372 | 0.295 | 0.094 |
| **DARE-TIES merge** | **0.369** | 0.498 | **0.345** | **0.106** |

So the red is real but it is the loss of a guessing strategy, not the loss of an inversion skill: by
exact arguments the tuned arms are within 1.2 points of the untuned model. The merge is the one arm
that is above base in **both** readings — 0.345 on non-trivial golds against 0.292, and 0.106 by exact
arguments — which is the same "merge reads backward better than base" result seen on all eight models,
and the only backward improvement on Llama that survives removing the trivial items.

On CodeLlama-7B the same forward tuning does not disturb the trivial-gold rate (0.368 → 0.37–0.44),
which is why its table has no such band of red: it never had the habit to lose.

## What to take from it

1. Execution grading is the right backward grade (inversion is many-to-one), but on an instruction-tuned
   general model it rewards generic-input guessing. The paper already reports the degenerate share;
   for Llama it should be read alongside the table.
2. "Forward tuning hurts backward" on Llama means "forward tuning removes a guess". The claim that
   survives is the merge's, on both grades.
3. Nothing here changes a ranking: by exact arguments the untuned panel spans 0.06–0.12 and Llama is in
   the middle of it.
