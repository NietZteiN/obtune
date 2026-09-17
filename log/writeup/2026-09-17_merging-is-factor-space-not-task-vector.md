# 2026-09-17 — The merge is applied in LoRA factor space, not to task vectors, and the two differ materially

**Thread:** writeup · **Prompted by:** user, "are you sure the merging method is task vector????" ·
**Verdict: they were right, and the paper said the wrong thing.**

## What the paper claimed

Section 3 described the merge as operating on task vectors: "for each specialist $i$, the update
$\Delta_i$ its training produced", then trim / elect sign / merge. That is TIES as published, and it
is not what we run.

## What PEFT actually does

`LoraModel.add_weighted_adapter` routes `ties`/`dare_ties` through
`_generalized_task_arithmetic_weighted_adapter`, which builds **two** lists of task tensors — the
specialists' $A$ factors and their $B$ factors — and calls `ties(...)` on each **independently**. The
combining weight is split as $\sqrt{w_i\cdot\mathrm{scaling}_i}$ on either side so the product
recovers the intended weight. The merged adapter is $B_{\mathrm{merged}}A_{\mathrm{merged}}$.

Sign election therefore happens on the **factors**, not on the update $\Delta_i = B_iA_i$ they
produce.

## How different is it

Measured, not asserted — random factors, $r=4$, three specialists, density 0.5, `majority_sign_method
= total`:

| quantity | value |
|---|---|
| relative error $\lVert B_mA_m - \mathrm{TIES}(\{B_iA_i\})\rVert / \lVert\mathrm{TIES}(\{B_iA_i\})\rVert$ | **1.24** |
| cosine similarity of the two merged updates | **+0.40** |
| entries whose **sign** differs | **39 %** |

These are not the same operation.

## Why we merge in factor space anyway, and what it costs the claim

The alternative is to assemble each $\Delta_i$, merge, and re-extract a low-rank adapter by SVD. That
is what mergekit's LoRA path does and why it was rejected here months ago: the truncation changes the
rank and introduces reconstruction error *before* the merging rule is evaluated, so the deployed
adapter no longer matches the base architecture and the measured effect confounds the merge with its
re-extraction. Factor-space merging preserves the rank exactly.

The honest consequence, now stated in Section 3: our results are evidence about sign-consensus merging
**as it is actually applied to LoRA adapters** — which is how practitioners use it and what PEFT
implements — rather than about the published task-vector algorithm in its original setting. That is
still the claim the paper wants to make, but it is a narrower one than the text implied.

## Not yet done

Whether TIES-on-assembled-$\Delta$ (via SVD re-extraction, accepting the rank change) would score
differently on our panel is untested. It is the obvious follow-up and would separate "sign consensus
helps" from "sign consensus on LoRA factors helps".
