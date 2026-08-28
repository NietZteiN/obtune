# 2026-08-26 — The symbolic and learned routes to "ignore inert material" are the same skill

**Thread:** normalization · **GPU:** 0, 2 (budget 3) · **Seed:** 17 · **Grid A** (`eval_source: heldout`), n=1667–1670

## Goal / hypothesis

Two unrelated things recover accuracy on inert-material obfuscation:

* **`norm_structural`** — a symbolic dead-code-elimination pass, zero training. It is the strongest
  zero-training arm in the project (`H1` 12.9 against base 6.3).
* **`tuned_S2_s17`** — the one adapter that beats the clean-code control on `H1` (+3.3), and the
  2026-08-26 knockout showed *how*: it re-anchors attention off inert identifiers, causally
  (paired difference **+0.1037** [+0.0109, +0.2085]).

They had never been combined. Pre-registered readings, written before the run:

* **additive** → independent routes to one skill; stacking is a free improvement.
* **saturated** → the same skill twice, i.e. the learned re-anchoring is approximately dead-code
  elimination and not something else. A sharper mechanistic claim than either result alone.

## Setup

`configs/eval/stack_norm_adapter_qwen1.5b.yaml`, phase `baselines_gridA`. `normalize` is a
per-system field in `eval_vllm.SystemSpec`, so an arm can carry an adapter **and** a normalizer;
no new machinery. Conditions `L0`, `L1r`, `S2` — **no `H1`**, deliberately: the question is
answerable for free on `S2`, which carries the same inert material by construction, and spending
a quarantine read to learn something the trainable grid already answers is what CLAUDE.md §3.2
rule 2 exists to prevent.

Statistics are the project's standard: cluster bootstrap by `program_id` (4,000 resamples,
seed 17) and exact McNemar on the discordant pairs.

## Results

Accuracy, Grid A:

| system | L0 | L1r | S2 |
|---|---|---|---|
| `base` | 21.8 | 18.7 | 15.1 |
| `norm_structural` | 22.0 | 18.9 | **19.9** |
| `tuned_L0` | 45.0 | 36.5 | 41.4 |
| `tuned_L0_norm` | 44.9 | 36.5 | **43.0** |
| `tuned_S2_s17` | 45.6 | 37.4 | 45.3 |
| `tuned_S2_norm` | 45.7 | 37.8 | **45.4** |

The paired contrast — what adding the symbolic pass buys each system:

| condition | system | gain from symbolic DCE | 95 % CI | McNemar p | b/c |
|---|---|---|---|---|---|
| **S2** | `base` | **+4.74** | [+3.12, +6.24] | 4.2e−11 | 113/34 |
| **S2** | `tuned_L0` | **+1.56** | [+0.30, +2.88] | 1.5e−02 | 66/40 |
| **S2** | `tuned_S2_s17` | **+0.06** | [−0.96, +1.08] | 1.00 | 35/34 |
| L0 | `tuned_S2_s17` | +0.12 | [−0.42, +0.66] | 0.83 | 12/10 |
| L0 | `tuned_L0` | −0.12 | [−0.60, +0.36] | 0.82 | 8/10 |
| L1r | `tuned_S2_s17` | +0.36 | [−0.12, +0.84] | 0.21 | 11/5 |

## Observations

**Saturated, and the gradient is the result.** The benefit of handing a system pre-cleaned code
falls monotonically with how much inert material that system was trained on: +4.74 for a model
that has never seen any, +1.56 for one trained on clean code only, +0.06 for the S2 specialist.
`tuned_S2`'s CI is ±1.1 pts — inside the project's 1.32-pt seed band, so this is a genuine
equivalence result and not merely a failure to reach significance.

**The controls hold.** On `L0` and `L1r`, which contain no dead code, normalization does nothing
for anybody (|Δ| ≤ 0.36, all null). So the S2 gradient is not a generic "normalized code is easier
to read" effect; it is specific to the material the pass removes.

**This closes the loop with RQ3.** The knockout said `tuned_S2` learned to stop attending to inert
identifiers. This says that whatever it learned leaves *nothing further* for a symbolic DCE pass
to contribute. Two independent instruments — a causal attention intervention and a symbolic
program transformation — agree that the skill `tuned_S2` acquired **is** dead-code elimination,
implemented in attention. Neither instrument alone supports that; together they do.

**It also bounds the negative result usefully.** `tuned_L0` retains +1.56 pts of headroom, so the
clean-code adapter has *most* but not all of the skill. That is the first quantity in this project
separating `tuned_L0` from a specialist on a mechanism rather than on aggregate accuracy.

## Errors hit

Building the span analysis for the follow-up (`normalize/inert.py`) surfaced **a live correctness
bug in the published `norm_structural` arm**. `_pass_fold` collapses `(-1)` to `Constant(-1)`, and
`ast.unparse` re-emits `BinOp(Constant(-1), Pow, Name('r'))` as `-1 ** r` — which Python parses as
`-(1 ** r)`, a constant where the original alternated sign. Two of 200 `L0` programs
(`apps_123_0`, `apps_1661_0`) were being handed to the model with a term of the computation
silently changed, and scored against the original's stored answer.

`scripts/analysis/21_validate_normalized.py` exists precisely to catch this and did not, so the
gate has a gap worth understanding rather than just patching around. Fixed generally rather than
locally: `_emit` now re-parses its own output and refuses to return text that does not mean the
tree it was given (`UnparseUnfaithful`), so any pass tripping the same class of precedence bug
reverts to the un-normalized program instead of shipping a wrong one. A first version of the guard
over-fired on 78/200 programs — `fold` legitimately produces `Constant(-1)` for `x[-1]`, which
round-trips to `UnaryOp(USub, Constant(1))` — so the comparison canonicalizes negative literals on
both sides. It still catches the real bug, because in `-1 ** r` the `USub` operand is a `BinOp`,
not a `Constant`.

The affected cells are the existing `norm_structural` ones. The effect is small (~1 % of programs,
biased against the arm) and does not change any conclusion here, but every published
`norm_structural` number is now known to be a slight under-estimate. The re-run is queued as
`norm_structural_fixed` under a new system name rather than overwriting, so before/after stays
measurable.

## Next steps

* `configs/eval/inert_normalize_qwen1.5b.yaml` — queued. Tests `norm_inert`, which adds dead-store
  elimination. Motivated directly by this result: if symbolic DCE is worth +4.74 to a model
  lacking the skill, the ceiling is set by how much the analysis can prove dead, and
  `norm_structural` proves **0.4 %** of `S4` dead (S4 being made entirely of inert material) because
  its guards are functions of a variable. `norm_inert` reaches 28.4 % on S4 and 39.2 % on S2
  without deciding any predicate, at 1200/1200 execution parity.
* Attention **steering** — the same spans, masked rather than deleted. Separates "the tokens are
  gone" from "attention is not spent on them", which deletion alone confounds.
* If `norm_inert` wins on the trainable grid, it earns a place in the batched confirmatory `H1`
  pass — not a read of its own.
