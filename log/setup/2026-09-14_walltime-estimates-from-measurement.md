# 2026-09-14 — Twelve jobs have been walltime-killed, and the estimates were never measured

**Thread:** setup · **Status:** two auto-queue estimates corrected from data; the rest reviewed

## The pattern

Counting `exit_code 124` across every manifest in `done/` and `failed/`: **twelve distinct jobs**
have been killed at walltime. Five are genuine TIMEOUTs rather than hand cancellations, and they
share one shape — an `est_gpu_h` that was written down rather than measured, doubled into a walltime
by the submitter, and then hit exactly.

| job | est | walltime | ran |
|---|---|---|---|
| `ev_merge_codellama-34b` | 0.6 | 1.2 h | 2.01 h |
| `ev_mole_granite31-8b` | 1.5 | 3.0 h | 3.01 h |
| `ev_mole_llama31-8b` | 1.5 | 3.0 h | 3.00 h |
| `ev_mole_starcoder2-15b` | 1.5 | 3.0 h | 3.01 h |
| `tr_gate_codellama-34b` | 3.0 | 6.0 h | 6.01 h |

Three of those are the *same* hardcoded estimate in the drain's mixture block, killing three
different models at exactly the same wall.

## What the completed runs actually say

**`merge_panel`, 207 cells.** Llama-3.1-8B 0.45 h, Granite 0.63, StarCoder2 0.94, Gemma-3 1.02,
CodeLlama-13B 1.12, CodeGemma 1.18, CodeLlama-34B about 2.9 across two attempts. The hardcoded 0.6
was below what six of the seven needed.

**`mole_panel`, 115 cells.** Measured 0.030–0.048 GPU-h per cell — Llama-3.1-8B did 101 cells in
3.0 h, Granite 75 in 3.0, StarCoder2 63 in 3.0, CodeGemma 30 in 1.12 — so a full grid needs
**3.4–5.5 h**. The hardcoded 1.5 gave three hours.

## Changed

- merge grid: `est 1.5` (3 h), and **2.0 for 34B** (4 h), against a measured 2.9 h worst case.
- mixture grid: `est 3.0` (6 h), covering the slowest measured rate with margin.
- gate training keeps `est 6.0` (12 h): Granite took 5.00 h, CodeGemma 5.48, CodeLlama-13B about
  6.5, so 12 h is right and the earlier 3.0 was what killed the 34B gate at 06:00:26.

The emitted JSON was checked by running the `printf` for both branches, because adding a third
format specifier to a two-argument `printf` is exactly the kind of edit that produces a manifest the
scheduler silently mis-reads.

## The general point

`submit.py` already knows the elapsed time of every job it has ever run, and nothing feeds that back
into the estimate. Every number here was available from `sacct` before it was needed. A helper that
derives `est_gpu_h` from the measured per-cell rate for that (kind, model) would end this class of
failure rather than correcting it one hardcoded constant at a time — noted, not built.
