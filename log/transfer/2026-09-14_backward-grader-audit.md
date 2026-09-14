# 2026-09-14 — Audit of the backward (input-prediction) numbers

**Thread:** transfer · **Status:** grader verified; two corrections to how it has been described · **Related:** [`2026-09-13_backward-task-is-many-to-one.md`](2026-09-13_backward-task-is-many-to-one.md)

The backward numbers now carry an argument in the paper, so the whole path was audited rather than
the aggregate trusted.

## Oracle test — the decisive one

Feed the **gold call** back through `inverse.grade_batch` and require a perfect score. On 120 items per
condition, including an obfuscated single transform and a stack:

| condition | correct | args_exact | format_fail | exec |
|---|---|---|---|---|
| L0 | **1.000** | 1.000 | 0.000 | 120 ok |
| L1r | **1.000** | 1.000 | 0.000 | 120 ok |
| S1 | **1.000** | 1.000 | 0.000 | 120 ok |
| C_L1r_S1 | **1.000** | 1.000 | 0.000 | 120 ok |

The grader recovers a perfect score from a perfect answer on clean code, on a renamed variant, on a
flattened one and on a stack. Nothing in the path silently loses credit.

## Negative controls (S1, 60 items)

| reply | correct | format_fail |
|---|---|---|
| gold call | 1.000 | 0.000 |
| wrong args, `f(0)` for every program | **0.033** | 0.000 |
| prose, "The call is f(1,2)." | 0.000 | 1.000 |
| expression argument, `f(range(3))` | 0.000 | 1.000 |
| multi-line reply | 0.000 | 1.000 |

The 3.3 % is not a leak: calling every program with `0` genuinely returns the gold value 3.3 % of the
time. That is a floor for degenerate hits and an independent measurement of the many-to-one problem.

## Prompt

Rendered and inspected. The system prompt states the inverse task; the gold **output is present** and
the gold **arguments are not** (checked programmatically). The one-shot demo shows the answer format.

**Rule 4 of the prompt reads: "Any arguments that make the call return the given value are
acceptable."** The model is *told* any pre-image will do. That settles which metric is faithful to the
task as posed: `correct` (execution match) is, and `args_exact` is stricter than what was asked. Both
are reported, and the stricter one must not be described as "the right number" — it answers a question
the model was not asked.

## Two corrections to how this has been described

1. **The call is executed against the item's own code, not the clean parent.** I said "graded by
   executing the produced call against the clean parent" in this session, and `sections/setup.tex`
   says it too. `grade_batch` builds its sandbox batch from `it.code`, which for condition `S1` is the
   flattened program — confirmed by the S1 item carrying a dispatch loop and the oracle still scoring
   1.000. This is the better design (it grades under the code the model was shown, which is what the
   prompt's rule 5 promises) but the paper must say what it does. Setup is corrected.
2. **`args_exact` is very slightly permissive for order-sensitive inputs.** Two of 1,671 items on
   CodeLlama-7B have `args_exact = 1` and `correct = 0`. Cause: Python dicts compare equal regardless
   of insertion order, but a program that *iterates* one produces order-dependent output. Gold
   `{5: 1, 'abc': 2, ...}` versus predicted `{'abc': 2, ..., 5: 1}` are equal as values and give
   different outputs. 0.12 % of items, benign, and worth knowing before someone treats
   `args_exact ≤ correct` as an invariant.

## Everything else checks out

`PYTHONHASHSEED` is pinned in the sandbox (`exec/pool.py`), so set and dict iteration is reproducible
and the corpus was determinism-filtered with a deliberately varied seed. The parquet is internally
consistent: 1,671 rows = 557 programs × 3 cases, no duplicates, `args_exact` identical to the grader's
`raw_exact`, no correct-but-format-failed row, no correct-but-not-executed row. `cell_meta.json`'s
accuracy matches the parquet mean to the sixth decimal it is stored at.
