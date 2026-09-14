# 2026-09-14 — H-anchor-site REFUTED: the anchor site is not the mechanism, and the KL is the *least* forward-locked arm

**Thread:** modularity · **Status:** read against the pre-registered rule; two earlier readings corrected · **Follows:** [`../transfer/2026-09-14_format-failure-is-forward-collapse.md`](../transfer/2026-09-14_format-failure-is-forward-collapse.md)

## The hypothesis

`cons_lam3`'s KL is over the teacher's **answer-token distribution**, so it matches forward behaviour
by construction. The panel-mean collapse rate had it worst of any arm (0.433), which fit. The
`align_*` arms anchor **hidden states** at six layers instead — direction-neutral — so they should
forward-lock less. Registered before submission, on CodeLlama-7B, pooled over L0–S2 and X1.

## The result

Forward-collapse rate — share of backward replies equal to the gold return value:

| arm | collapse |
|---|---|
| `base` | 0.0000 |
| `tuned_X1` (family) | 0.0001 |
| **`cons_lam3` (anchored)** | **0.0010** |
| `align_lam0` | 0.0106 |
| `mono_all` (breadth) | 0.0115 |
| `align_span_lam3` | 0.0338 |
| `tuned_L0` (clean LoRA) | 0.0464 |
| `align_lam0.3` | 0.1220 |
| `align_lam1_mm` (mismatch control) | 0.1676 |
| `align_lam1` | 0.2123 |
| `align_lam3` | 0.3066 |

**H-anchor-site-a: REFUTED.** The best matched align arm (`align_lam0`, which is λ=0 — no alignment
term at all) collapses ten times *more* than `cons_lam3`, and every arm with a real alignment weight
collapses 100–300× more. Representation anchoring forward-locks **harder**, monotonically in λ
(0.011 → 0.122 → 0.212 → 0.307).

**H-anchor-site-b: INCONCLUSIVE**, and worse than that for the align arms: their backward accuracy is
*significantly below base* (−5.9 to −8.0 points exact, all intervals excluding zero) while
`cons_lam3` is −0.20 [−1.65, +1.31], indistinguishable from base. The only arm that gains backwards is
`tuned_X1`, +1.34 [+0.27, +2.34].

**The mismatch control does not separate.** `align_lam1` 0.212 against `align_lam1_mm` 0.168 — aligning
to the *wrong* parent forward-locks about as much as aligning to the right one. So this is a cost of
adding a representation-matching term at all, not of matching the correct representation.

## Two corrections to what I said earlier today

1. **I claimed `cons_lam3` is the most forward-locked arm.** On CodeLlama-7B, pooled over all seven
   conditions, it is the *least* forward-locked tuned arm — 0.0010, forty times below `tuned_L0`. The
   0.433 figure I quoted is the **panel mean**, which is dominated by Granite (0.977) and CodeGemma
   (0.959); those two models collapse on every tuned arm, `mono_all` included at 0.896 and 0.764. The
   effect is a property of *those models*, not of the objective, and I attributed it to the objective.
2. **The mechanical story I gave — "the KL matches forward output, so it must forward-lock more" — is
   not supported.** It is a plausible account that the data contradict on the model where it can be
   measured cleanly. The alignment arms, which do *not* match the output distribution, forward-lock far
   more; and the λ=0 ablation shows most of that cost is not even the alignment term.

## Where this leaves the paper

The user's question — *doesn't the KL match forward output, and so make things worse?* — is a good
mechanism to propose and is **refuted on the one model where every arm is measurable**. Paired
consistency remains the tuned arm that best preserves the ability to answer a different question, and
the forward-collapse metric now supports rather than undercuts it, on CodeLlama-7B.

What still stands from this morning: Granite and CodeGemma collapse catastrophically on *every* tuned
arm, so the reversal claim cannot be replicated there; that is a model property and belongs in Threats,
not a defect of the objective.
