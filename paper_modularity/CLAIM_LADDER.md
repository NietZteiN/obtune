# The claim ladder — what each pending run lets the paper say

*Last updated: 2026-08-13.*

`main.tex` has a deliberately empty thesis. This file is where the candidate theses live, each
tied to the run that would license it and the outcome that would kill it. When a run lands,
pick the branch it selects, fill the `\slot{}` macros, and the surrounding prose does not have
to be rewritten — every section was drafted to be true under all four branches.

**Rule.** A branch fires only on its stated gate. If a run comes back ambiguous, the branch
does not fire and the paper stays on the floor (Branch A), which is already fully supported.

---

## What is already settled, whichever branch fires

These go in the paper regardless, and are why there is a paper at all:

1. **A perfect router buys almost nothing.** 100.0 % routing accuracy, near-zero entropy, and
   five of six conditions statistically indistinguishable from a clean-code adapter.
2. **Merge-objective checkpoint selection does not help.** 27 candidates, 3 greedy rounds,
   0.7 points end to end, every round's winner below the status quo.
3. **The DARE-linear catastrophe was a scaling defect.** Repaired: +41.6 points, parity with
   the control. The format-failure diagnostic is what distinguished a bug from a result.
4. **Horoi's interference mechanism reproduces; its consequence does not.** Sign conflict rises
   0.401 → 0.425 over nine epochs on the same 8-expert bank, while merged accuracy *improves*
   on 11 of 12 method × condition pairs.
5. **The CPU-only task-vector diagnostic** and the four-layer quarantine architecture, as
   reusable artifacts.

That set is a coherent negative-results paper on its own. Everything below is upside.

---

## Branch A — *"Modularity does not rescue robustness"* (the floor)

**Fires if:** the repaired `mole_random` (§9 item 3) comes back ≈ `mole_router`, **or** the
corpus-scale composite grid (item 2) leaves the +2.9-point gate effect inside noise.

**Headline:** every way of combining per-transformation specialists — perfect dispatch, three
weight-space merges, merge-optimal selection, an activation-space mixture, oracle prompting —
recovers at most what the individual specialists knew, and usually less. The modular answer to
"one specialist per transformation" does not produce a system that generalizes.

**Support:** complete today, except that item 3 must actually run for the mixture arm's null to
be a null rather than an unknown.

**Risk:** a reviewer reads it as "you tried five things and none worked." Mitigation is already
in the draft — each arm is instrumented well enough to say *why* it did not work, and two of the
five (merge-optimal, DARE-linear) produce mechanism, not just an outcome.

---

## Branch B — *"Routing is solved; composition is not"*

**Fires if:** item 3 lands with `mole_router` − `mole_random` ≥ 2 pts **and** item 2 puts the
composite effect outside its interval at corpus scale. Both are required: item 2 without item 3
cannot distinguish routing from rank-256 residency, and item 3 without item 2 is underpowered.

**Headline:** hard dispatch over specialists saturates at 100 % accuracy and is worth nothing,
because it is only ever asked easy questions. The real problem is the input where *no* single
expert is correct, and there a learned per-token mixture does measurably better than the same
architecture with its weights pinned uniform. Composition, not selection, is the open problem.

**What it needs beyond items 2 and 3:** the hard-router rung (item 5). Without it, "a mixture
beats a router on composites" is asserted rather than measured on the same engine.

**Current evidence:** +2.9 pts \[−0.0, +6.2\], p=0.059, positive on 8 of 8 conditions, no cell
surviving FDR. The right sign everywhere and significance nowhere.

---

## Branch C — *"Merge geometry predicts, but does not prescribe"*

**Fires if:** the geometry quantities (sign conflict, cosine, ‖ΔW‖) predict merged accuracy
across a wider bank than we currently have — i.e. the density sweep (item 4) and the second seed
(item 1) produce enough merge points to regress accuracy on geometry.

**Headline:** inter-expert interference is cheaply measurable from the LoRA factors, on CPU,
before any merge is built — and it tracks merge quality — but acting on it (selecting
checkpoints to minimise it) does not help, because the interference it measures is not what
bounds merged accuracy at this rank.

**Status:** half-supported. The mechanism half is measured; the "predicts" half needs more merge
points than the 27 flat candidates provide. **Note this branch is in tension with item 4 of the
settled list** — if merge-optimal selection buys nothing and longer training helps, geometry may
simply not be the right predictor. That is itself reportable, but it is Branch A's framing.

---

## Branch D — *"Router saturation and merge failure are one phenomenon"* (the strongest)

**Fires if:** item 8 shows the predicted frontier — deliberately under-trained experts are
**harder to route** (routing accuracy falls below 100 %, entropy rises) **and easier to merge**
(merged accuracy rises relative to a matched over-trained bank).

**Headline:** the two failure modes this paper measures separately have one cause. Training an
expert to its individual optimum makes it trivially distinguishable — hence a solved,
uninformative routing problem — *and* mutually interfering — hence a lossy merge. Expert
specialisation is a single dial that trades routability against mergeability, and neither
literature names it because each studies one half.

**Why this is the best outcome:** it is a claim about adapter composition in general, not about
obfuscation. It reframes both of the paper's negative results as measurements of one quantity.
It is also the cheapest untested idea we have — the under-trained bank is a by-product of the
9-epoch sweep, and both the router and the merge harness already run on it.

**Kill condition:** if under-trained experts are *also* routed at 100 %, the dial does not exist
and this reduces to Branch A.

---

## Decision order

Run in this order; each is cheap relative to the one after, and each can retire a branch.

| order | item (§9 of `main.tex`) | retires |
|---|---|---|
| 1 | item 3 — repair `mole_random`, re-evaluate | decides A vs B; **no retraining needed** |
| 2 | item 8 — under-trained bank, routed and merged | decides D |
| 3 | item 2 — composites at corpus scale | powers B |
| 4 | item 1 — second seed for every arm | makes every ±3 pt number claimable |
| 5 | items 4, 5, 6, 7 | scope, threats, and the deployment claim |

Item 3 is first because it costs one evaluation pass and currently blocks the abstract.
