# 2026-09-13 — Two thirds of every backward "correct" answer is a different input that happens to fit

**Thread:** transfer · **Status:** measured; the master table now reports both metrics · **Bears on:** the direction-ratio result in [`2026-09-12_direction-ratio.md`](2026-09-12_direction-ratio.md) and every backward claim in the paper

## The question

The master table's input-prediction block looked wrong: the **untuned** CodeLlama-7B scores **0.285
backward on clean code against 0.257 forward** — apparently reading programs backwards slightly better
than forwards, with no tuning at all.

## The answer

The backward task is graded by **executing the produced call and comparing its return value to the
gold**, and inversion is many-to-one. Every trial also records `args_exact`, whether the call recovers
the gold arguments. Pooled over L0, L1b, S1, S2 and X1 on CodeLlama-7B:

| system | by execution | by exact arguments | share degenerate |
|---|---|---|---|
| `base` | 0.279 | **0.086** | 69 % |
| `tuned_L0` | 0.239 | 0.081 | 66 % |
| `mono_all` | 0.270 | 0.083 | 69 % |
| `cons_lam3` | 0.297 | 0.097 | 67 % |
| `tuned_X1` | 0.295 | 0.102 | 65 % |
| `merge_dare_ties` | 0.314 | 0.112 | 64 % |

Sampled successes of the untuned model make the mechanism obvious:
`exchange_sort([1, 2, 3])` → `0`, `survivor([1,...,10])` → `0`, `parse_int('two')` → `2`. Return values
like `0`, `1`, `True` and `[]` are common, and a plausible-looking call lands on one often enough to
score. **Only 159 of the untuned model's 476 correct answers on L0 recovered the gold arguments.**

## What it does and does not change

- The **ordering** of systems is broadly preserved: the merge and the family adapter lead on both
  metrics, `tuned_L0` is last on both. So the comparative backward claims are not reversed.
- The **magnitudes** collapse by a factor of about three, and with them the apparent parity between
  backward and forward competence. "The untuned model reads backwards as well as forwards" was an
  artefact; under exact arguments it is 0.086 against 0.257.
- Any claim of the form "X gains N points backwards" should be stated on the strict metric or marked
  as execution-match. The direction ratio is computed from execution-match numbers throughout and is
  therefore an upper bound on the real backward transfer.

This is the same class as the 2026-06-09 containment-matching audit that found ~3 % false positives in
the forward grader, but far larger, and it is a property of the *task* rather than of the matcher: an
inverse problem has many solutions and the grader accepts all of them. Keeping execution-match is
defensible — a call that returns the gold value *does* satisfy the stated task — but it must be
reported next to the strict number, which is what the master table now does.

## Reported

`scripts/analysis/59_master_tables.py` emits the backward block **twice**, "by execution" and "by exact
arguments", with the caption stating the 64–69 % figure. Nothing was deleted; the permissive number is
still there for continuity with the published direction ratio.
