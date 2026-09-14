# 2026-09-14 — The backward "format failures" are the model answering the FORWARD question

**Thread:** transfer · **Status:** verified; this reverses how the format gate has been read on tuned backward cells · **Follows:** [`2026-09-14_why-input-prediction-is-hard.md`](2026-09-14_why-input-prediction-is-hard.md), [`2026-09-13_backward-task-format-collapse-on-the-panel.md`](2026-09-13_backward-task-format-collapse-on-the-panel.md)

## What the failing replies actually are

Since 2026-09-13 the panel's tuned backward cells have been marked `fmt` and excluded as "the cell
measures the prompt contract rather than the task". Reading the raw replies shows what they are:

| model / arm | reply |
|---|---|
| `granite31-8b` / `cons_lam3` | `6`, `0`, `999999998` |
| `codegemma-7b` / `cons_lam3` | `6`, `0`, `999999998` |
| `codellama-13b` / `mono_all` | `3,2,1`, `1,1,0` |
| `codellama-34b` / `tuned_L0` | `"1+1"`, `[8,1,5,2,6]` |

These are not malformed calls. They are **values** — the shape of a *forward* answer. Asked "write a
call that returns 6", the arm replies "6".

## Confirmed by exact match to the gold output

For every format-failed reply, is it exactly the item's gold **return value**?

| model | arm | format fail | of those, equal to the gold OUTPUT |
|---|---|---|---|
| CodeLlama-7B | base | 0.02 | 0.00 |
| CodeLlama-7B | `cons_lam3` | 0.01 | 0.00 |
| CodeLlama-13B | base | 0.03 | 0.00 |
| CodeLlama-13B | `cons_lam3` | 0.55 | **0.57** |
| CodeLlama-34B | base | 0.03 | 0.00 |
| CodeLlama-34B | `tuned_L0` | 0.51 | 0.09 |
| Gemma-3-12B | `cons_lam3` | 0.62 | 0.28 |
| **Granite-3.1-8B** | **`cons_lam3`** | **1.00** | **0.98** |
| **CodeGemma-7B** | **`cons_lam3`** | **0.98** | **0.98** |

On Granite and CodeGemma the anchored arm answers the forward question **on every item**, and gets the
forward answer **right 98 % of the time**. It is not confused; it is answering a different question
correctly. **No untuned model does this** (0.00–0.11), so tuning causes it.

**The instruction is present.** Ruled out as a rendering bug: the inverse system prompt and the
"Reply with ONLY the call" rule appear in the rendered chat for Granite (`system` role), CodeGemma
(`merged` into the user turn) and CodeLlama-7B alike.

## Two consequences, one of them against our own method

**1. The gate was hiding a result, not protecting one.** For an untuned model a high backward format
rate really is a prompt-contract failure. For a *tuned* arm it is task collapse: the adapter has bound
"program in this prompt shape" → "emit the return value" so tightly that an explicit instruction to
invert cannot dislodge it. That is the sharpest evidence in the project for the paper's thesis, and it
has been sitting in cells marked `fmt` and excluded from every mean.

**2. The anchored objective is the most forward-locked arm, not the least.** `cons_lam3` is the arm
that collapses hardest — 1.00 on Granite, 0.98 on CodeGemma, 0.55 on CodeLlama-13B — while `base`
never collapses and `tuned_L0` collapses differently (34B's 0.51 is mostly *not* the gold output, so it
is emitting bare literals rather than answering forward). Mechanically this is unsurprising: the KL
term trains the student to match a clean-code teacher's **forward output distribution**, so it binds
forward behaviour harder than plain SFT. On CodeLlama-7B — the one model the reversal test is reported
on — `cons_lam3` does not collapse at all (0.01).

So the paper's claim that anchoring is the arm whose forward gain costs nothing backwards is measured
on the single model where anchoring happens not to be forward-locked. On three of the other seven it
cannot answer backwards at all.

## What must change

- The backward `fmt` marker must distinguish **"did not answer in the required format"** from
  **"answered the forward question"**. The second is a result and belongs in the table with its own
  mark, not excluded.
- `59_master_tables.py` should report, per backward cell, the share of replies equal to the gold
  output — the collapse rate — beside the accuracy.
- The reversal-test claim needs restating: not "anchoring preserves backward competence" but
  "on CodeLlama-7B anchoring preserves it; on Granite, CodeGemma and CodeLlama-13B the anchored arm
  answers forward regardless of the question."

Nothing was deleted; every cell stands. What changes is the reading.
