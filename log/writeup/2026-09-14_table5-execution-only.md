# 2026-09-14 — Table 5 keeps the execution grade only; the exact-arguments block is gone and the table fits its page

**Thread:** writeup · **Asked by the user:** "Which is more accurate, graded by execution or by exact arguments, and only keep that on Table 5 — it overflows in the PDF."

## Which grade is accurate

**Execution.** The inverse task asks for *a* call that returns the shown value, and inversion is
many-to-one: 21.5 % of the ladder's gold return values are `None`, a boolean, an empty container or
an integer in −3..3, each with many valid inputs, and even the remaining 78.5 % recover the recorded
input only 9.6 % of the time. "Exact arguments" therefore marks a correct answer wrong whenever it is
not the one input the dataset happened to record. It is a legitimate *secondary* column — it says how
often the model finds the canonical input — but as the primary grade it measures the dataset's
choice of input, not the model's competence. CRUXEval-I grades by execution for the same reason.

The v2 audit ([`../transfer/2026-09-14_backward-grade-v2-audit.md`](../transfer/2026-09-14_backward-grade-v2-audit.md))
checked execution grading from the other side: every executed call marked wrong that a reviewer
might suspect (26 rows that looked double-quoted) is genuinely wrong.

## What changed in the paper

Table 5 (`master_abs_codellama7b`, Section 4) had three blocks — forward, backward by execution,
backward by exact arguments — 69 rows in a full-width float, and LaTeX reported it **31 pt taller
than the page**. The exact-arguments block is no longer emitted to LaTeX (it stays in
`docs/MASTER_TABLES.md`), the caption no longer says "reported twice" and instead states the
execution rule and why, and the remaining 47 rows sit at `\arraystretch{0.92}` with the five
inter-group `\addlinespace` lines removed. **No "Float too large" warning remains in the body**;
Table 5 is on page 9, references on 14, page count unchanged at 35. The same generator writes the
seven per-model appendix tables, so they shrank identically.

## Two slips on the way, recorded because each cost a build

The first rebuild reported success on a stale table: the second generator patch had removed a line
by text but left its indentation behind, the generator raised `IndentationError`, and `>/dev/null`
hid it — the inliner then refreshed nothing and the PDF came out byte-identical. The tell was the
identical byte count, not any message. Generator output is no longer silenced in the build chain.
