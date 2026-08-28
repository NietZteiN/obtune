# Thread: normalization

Symbolic, zero-training program transformation as a baseline and as an instrument. The arm feeds
the model a rewritten program and scores against the **original** program's stored answer, so
every result here depends on the rewrite being behaviour-preserving — which is gated by execution,
not by inspection.

## Status

Active. The thread began as a baseline ("how far does a compiler get without a GPU?") and became
a mechanistic instrument: because the pass is a precise, external implementation of "ignore code
that cannot affect the result", how much it adds to a given system measures how much of that skill
the system is missing.

## Hypotheses

| # | Hypothesis | State |
|---|---|---|
| N1 | Symbolic normalization recovers accuracy on inert-material obfuscation | **Supported.** `norm_structural` is +4.74 over `base` on `S2` [+3.12, +6.24], and the strongest zero-training arm on `H1` (12.9 vs 6.3) |
| N2 | The symbolic route and the learned route are independent, so they stack | **Refuted, 2026-08-26.** Adding DCE to `tuned_S2` is worth +0.06 [−0.96, +1.08] — inside the seed band. They are the same skill |
| N3 | How much the pass adds is bounded by how much it can PROVE dead, not by the model | **Open.** Motivates `norm_inert`; `norm_structural` proves only 0.4 % of `S4` dead |
| N4 | Stronger static analysis ⇒ a stronger zero-training baseline | **Running** (`inert_normalize_qwen1.5b.yaml`) |

## What worked

* Treating the pass as a **measuring instrument** rather than a baseline. The dose-response across
  `base` / `tuned_L0` / `tuned_S2` is the thread's main result and none of it needed a new model.
* **Asking whether code has an EFFECT instead of whether a guard is decidable.** S4's opaque
  predicates are functions of a variable and defeat constant folding by design; the branch is still
  inert because neither arm does anything. This sidesteps the arms race the H1 family escalates.
* **Gating soundness by execution.** `25_validate_inert.py` runs both versions on real cases; it is
  what caught the `(-1) ** r` bug that inspection had missed for two weeks.

## What didn't

* **`alpha` (canonical renaming)** costs 6.8 pts on `L0` by discarding meaningful identifiers, and
  swamps `dce`'s gains — which is why `structural` exists as `full` minus `alpha`.
* **Stacking symbolic and learned routes** (N2). Not a wasted run: the null is the mechanistic
  claim.
* **A structural-equality round-trip guard.** Over-fired on 78/200 programs, because folding
  legitimately changes how a negative literal is represented. Needed canonicalization first.

## Entries

| Date | Entry |
|---|---|
| 2026-08-26 | [`2026-08-26_symbolic-and-learned-routes-are-one-skill.md`](2026-08-26_symbolic-and-learned-routes-are-one-skill.md) |
