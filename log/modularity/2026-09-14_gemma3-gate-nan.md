# 2026-09-14 — The Gemma-3 gate trains on NaN, and I let it run for six hours before looking

**Thread:** modularity · **Status:** cause not yet identified; job cancelled, manifest held, probe running

## What happened

`tr_gate_gemma3-12b` ran for **5 h 56 m** on an H100 with a loss of `nan` printed every ten steps.
It went non-finite at **step 90** — a few minutes in — and every step after that was NaN. The
periodic checkpoint it had been dutifully writing is worthless: **all 50 gate tensors are NaN**.

The same code trained clean on the other seven models. Zero `nan` lines appear in any of their
logs. So this is Gemma-3-specific, not a bug in the gate that everyone has.

**The process failure is mine and it is simple: I watched the job's elapsed time and its
checkpoint file and never read its loss.** One `grep nan` on the log would have caught it at minute
five. Twelve GPU-hours have now gone into this model's gate across two attempts.

A second failure followed immediately: the queue drain's auto-queue block sees a missing `gate.pt`
and eight ready experts and recreates the manifest, so it queued another 12-hour NaN run within
four minutes of the cancellation, twice. `runs/manifest/held/` is now a veto that block checks
first — and because the running drain was a `while true` loop holding the pre-veto script in
memory, the fix required restarting it, not just writing it.

## What is ruled out so far

`--nan-probe`, added to `train_mole` so the instrumentation runs in the REAL loop rather than a
separate harness that might not reproduce it:

| steps | loss | temperature range |
|---|---|---|
| 1–12 | 0.0165 – 0.9833, all finite | tau 0.988 – 1.004 |

So at the start there is **no base-model overflow and no temperature collapse**: the hidden states
the gate reads are finite, its outputs are finite, and `tau` has barely moved from its initial 1.0.
Whatever happens, happens between step 12 and step 90. A probe to step 140 is running.

## Candidates still open

- **A slow temperature collapse.** `scale = sqrt(d_r) * exp(log_tau)` and `log_tau` is learned and
  unclamped. `min_temperature` is set in exactly one config on the panel (`routerlora_balanced`),
  so nothing floors it here. Twelve steps is far too few to see a drift.
- **A rare batch.** 60,639 training instances; something in one of them — an unusual length, an
  empty completion after masking — could produce the first non-finite value, after which the NaN
  is permanent in the parameters and every later step reports NaN regardless of input.
- **An lr that is marginal on this model.** 1e-3 for a small head is deliberate and works on seven
  models; Gemma-3 is the one with 262 k vocabulary and 2×32 batching instead of 8×8.

The probe distinguishes the first two: it names the first non-finite tensor and attributes it to
the base hidden state or to the gate's own output.

## Not done

No fix is applied and the manifest stays held. Releasing it before the cause is known buys another
twelve hours of NaN, which is exactly what happened once already today.
