# 2026-08-27 — Training-free attention steering works, and a 6-layer null nearly hid it

**Thread:** attention · **GPU:** 3 (pinned; budget 3) · **Seed:** 17 · n=150/cell, `heldout` · No `H1` read

## Goal / hypothesis

[2026-08-26 (normalization)](../normalization/2026-08-26_symbolic-and-learned-routes-are-one-skill.md)
established that *deleting* provably-inert code is worth **+4.74 pts** to `base` on `S2`
[+3.12, +6.24]. Deletion does two things at once and every normalization result in this project
confounds them:

* **(a)** the distracting tokens are gone, so no attention can land on them;
* **(b)** the sequence is shorter, so every live token sits closer to the answer position.

Masking separates them. The model sees the byte-identical original program, every token keeps its
position, and only attention to the inert *key* positions is suppressed. Spans come from
`normalize.inert.inert_spans` — the same analysis the `dse` pass deletes — so "delete them" and
"stop attending to them" are the same characters by construction.

**Pre-registered, and the sign is the OPPOSITE of the 2026-08-26 knockout.** There the suppressed
tokens were ones the answer depends on and suppression *hurt* `base` (−0.089 [−0.158, −0.023]).
Here they are provably irrelevant, so a distracted model should get **better**: Δ > 0. `tuned_S2`
should gain less (it already ignores this material). `L0` has no inert code, so its mask is empty
and every Δ must be *exactly* 0.

## Setup

* `scripts/attn/31_steer.py` (new), `attention.knockout.inert_key_mask` (new),
  `KnockoutSpec(classes=("inert",))` — `inert` added as a pseudo-class, resolved by `_key_mask`,
  which unions it with any lexical classes. Both `score_with_knockout` and
  `evaluate_with_knockout` now route through that one dispatcher.
* Readout: teacher-forced log P(gold), per the 2026-08-26 floor lesson.
* Drivers: `scripts/attn/run_steer_grid.sh` (6 layers), `run_steer_alllayers.sh` (all 28), both
  `setsid`-detached. Mask unit-tested against the real tokenizer in
  `tests/test_inert_knockout_mask.py`.

## Results

Δ log P(gold) = knocked − clean. **Positive = suppressing attention to inert code helped.**
Parenthesis = items improved/worsened.

| system | cond | 6 layers (4,9,14,19,23,27) | **all 28 layers** |
|---|---|---|---|
| `base` | **L0** | **+0.0000** | **+0.0000** |
| `base` | S2 | +0.0033 (75/75) | **+0.2172** (94/56) |
| `base` | S4 | +0.0110 (78/63) | **+0.0788** (92/49) |
| `tuned_L0` | L0 | +0.0000 | — |
| `tuned_L0` | S2 | −0.0103 (96/54) | — |
| `tuned_L0` | S4 | +0.0058 (86/55) | — |
| `tuned_S2_s17` | **L0** | **+0.0000** | **+0.0000** |
| `tuned_S2_s17` | S2 | −0.0293 (76/74) | **+0.1352** (80/70) |
| `tuned_S2_s17` | S4 | −0.0182 (69/72) | +0.0246 (61/80) |

Mask coverage: `S2` 150/150 items carry inert code (37.2 % of characters), `S4` 141/150 (26.9 %),
`L0` **0/150**.

## Observations

**Training-free steering works.** A static analysis plus an inference-time attention mask raises
log P(gold) with no training and no rewrite of the program. `base` on `S2` at **+0.2172** is roughly
**2.4× the magnitude of the 2026-08-26 identifier knockout** (−0.089) that established RQ3's causal
leg, and it is in the pre-registered direction.

**The ordering matches the mechanism.** `base` gains most, `tuned_S2` less — the specialist already
declines to attend to this material, so forbidding it buys less. Same ordering the knockout and the
symbolic-DCE dose-response produce by two other routes. This is now a *third* independent instrument
pointing at inert material as what costs the model on this family.

**The `L0` control is what makes the nulls readable.** All five `L0` cells are exactly 0.0000 with an
empty mask. So the small-effect cells are genuine nulls, not a mask that silently stopped firing, and
a non-zero value there would have voided the arm.

## Errors hit

**I concluded the wrong thing from the 6-layer grid, and said so, before the control refuted it.**
At 6 of 28 layers every cell is inside ±0.03 with better/worse near 50/50. Against deletion's
+4.74 pts that looked like a clean dissociation — "removing inert code helps, forbidding the model to
look at it does not, therefore the benefit is (b) sequence length, not (a) attention" — and it was
reported that way. It was wrong. Attention suppressed at 6 layers simply reaches the inert keys at
the other 22; the null measured a **partial intervention**, not an absent effect.

The all-28-layer arm was already queued as a caveat-closer when the claim was made, which is the only
reason the error was caught within the hour. Two lessons, the second more general than this thread:

1. **A null at partial depth is not evidence of no effect**, and every knockout or steering result in
   this project must report its layer coverage. The 2026-08-26 manipulation check already contained
   the warning — all-28-layer masking changed 68 % of outputs against 62 % *identical* at 6 layers —
   and it was not applied here.
2. Don't state a dissociation while the control that could break it is still running.

## Next steps

* **Confirmatory `--mode generate` pass.** The claim so far is about log-probability. Steering has
  not been shown to improve *answers*, only confidence in them, and that distinction is exactly the
  one §15.2's floor lesson cuts both ways on.
* **The length-matched control**, which is the arm that would actually decompose (a) against (b):
  replace inert spans with equal-length neutral filler instead of deleting them. Deletion removes
  content and shortens; masking removes access and keeps length; filler keeps length and removes
  content. The three together identify how the +4.74 divides. Eval-only, ~30 GPU-min.
* Attention supervision during training (auxiliary loss on inert-token attention) is **live again**.
  It was judged pre-falsified on the 6-layer null; the 28-layer result withdraws that judgement.
