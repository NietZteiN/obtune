# 2026-09-14 — Forward-locking is the mechanism, and merging is the only adaptation that avoids it

**Thread:** transfer · **Status:** all eight models, all sixteen backward conditions · **Script:** [`scripts/analysis/67_backward_failure_modes.py`](../../scripts/analysis/67_backward_failure_modes.py)

## What the format gate was hiding

`format_fail` is one bit and the gate on it is one threshold, and about twenty backward cells on
this panel sit over it. Every table said the same thing about all of them — "its responses are
mostly unparseable" — and that is not true of most of them. Four different failures share the
marker:

| mode | what it is |
|---|---|
| **answered forward** | the reply is exactly the gold FORWARD answer — the arm answered the other question |
| **stop failure** | a valid single call sits on line 1 and the model kept generating a fresh prompt |
| **truncated** | generation hit the 128-token cap mid-call; the harness ran out of room, not the model |
| **malformed** | prose, an expression, a bare variable — the failure the gate is meant to catch |

Two cells on the same model, at `C_L1r_X1`, to show the spread. CodeGemma's **untuned** model: 55 %
stop failures, 41 % truncation, **4.7 % malformed** — that cell's gate is mostly harness, and it is
the reference every contrast on that model is formed against. CodeGemma's **anchored** arm: **96 %
answered forward**. One marker, two completely different cells.

## The aggregate

Forward-collapse rate over all trials, pooled over all sixteen backward conditions, all eight models:

| arm | panel mean |
|---|---|
| `base` (untuned) | **0.004** |
| `merge_ties` | **0.000** |
| `merge_dare_ties` | **0.001** |
| `tuned_X1` (family) | 0.110 |
| `tuned_L0` (clean) | 0.135 |
| `mono_all` (breadth) | 0.198 |
| `cons_lam3` (anchored) | **0.312** |

Per model, the tuned arms reach 0.41–0.48 on StarCoder2, 0.25–0.81 on CodeGemma and 0.25–0.64 on
Granite. **The two merges sit at the untuned model's floor on every one of the eight**: the largest
value either merge takes anywhere is 0.002.

## What this settles

**The merge's tax-free behaviour has a mechanism.** Yesterday's finding was that the merge's drop
from seen stacks to unseen-containing ones is within noise of the untuned model's, forwards and
backwards, on eight models
([`2026-09-14_three-methods-one-table.md`](2026-09-14_three-methods-one-table.md)). This says why:
merging does not induce forward-locking at all, while every single-adapter arm does. Averaging
several adapters in weight space averages away the thing that pins the output head.

**The anchored objective is the worst offender, and the ordering is the objective's.** `cons_lam3`'s
extra term is a KL to the clean parent's ANSWER-TOKEN distribution. It matches forward behaviour by
construction and adds a second forward-pinning term on top of the cross-entropy, and it collapses
hardest — 0.312 against breadth's 0.198 and clean-LoRA's 0.135. Forward-locking tracks how directly
an objective pins the output head. This is the refutation of the "KL anchoring preserves the
reverse direction" story, now stated on the whole panel rather than one model.

**The untuned models are a clean floor.** 0.000 on seven of eight and 0.030 on the eighth, so the
full range of the metric is usable and nothing here is a ceiling artefact.

## What is NOT claimed

The grader is unchanged and should stay unchanged: `inverse.py`'s strictness is pre-registered in
its own docstring with the reasoning, and hunting for a call inside prose would repair the failure
the metric exists to report. This script measures what the strictness is catching; it does not
re-grade anything. Two things it surfaces are worth a decision but are not acted on here:

- **Truncation at 128 tokens** is 1.1–4.5 % of all backward trials and up to 41 % of the failures in
  the worst cell. CLAUDE.md §4 item 8 requires this rate to be reported and nothing reported it
  until now. It cannot by itself push a cell over a 0.25 gate.
- **Keyword-argument calls** (`f(v_1118=10, v_b1a6=10)`) are counted malformed. They are single
  calls with literal arguments and arguably satisfy the stated contract. Changing that would move
  every published backward number, so it is a decision, not a fix.

## The router

`mole_router` has no backward cell on any model yet, so its row is empty. Its config exists and the
read is pre-registered. If the mechanism above is right, the router should sit with the
single-adapter arms rather than with the merges — it selects among per-type adapters rather than
averaging them — and that is a sharper prediction than the one already recorded in the scratchpad.
