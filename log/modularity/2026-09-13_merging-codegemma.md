# 2026-09-13 — Merging on CodeGemma: fifth model, and the seen-stack picture is now split

**Thread:** modularity · **Status:** read against the pre-registered rules · **Extends:** [`2026-09-13_merging-on-the-panel.md`](2026-09-13_merging-on-the-panel.md), [`2026-09-13_merging-on-the-panel-starcoder2.md`](2026-09-13_merging-on-the-panel-starcoder2.md)

`ev_merge_codegemma-7b` (h100, 1 h 10 min, **207 cells** — the widened 23-condition config) is the
first model whose specialists, merges and evaluation were all produced by the automated chain with no
manual step. DARE-TIES is the best merge again; DARE-linear is format-gated again.

| stacks | merge − clean | merge − breadth | merge − anchored | breadth − clean | anchored − clean |
|---|---|---|---|---|---|
| seen (6) | +0.44 [−0.48, +1.36] | **−3.83 [−5.34, −2.32]** | **−3.59 [−5.08, −2.24]** | **+4.27** | **+4.03** |
| unseen-containing (4) | −0.10 [−1.02, +0.81] | −0.13 [−1.67, +1.44] | +0.92 [−0.47, +2.35] | +0.03 | −1.02 |
| X1 alone | +0.33 [−1.23, +1.90] | **+2.31 [+0.25, +4.36]** | **+2.72 [+0.74, +4.78]** | −1.98 | **−2.39** |

**H-merge-panel-a INCONCLUSIVE, H-merge-panel-b CONFIRMED.**

## The seen-stack claim across five models

| model | merge − clean on seen stacks |
|---|---|
| CodeLlama-7B | **+0.83 [+0.01, +1.63]** |
| Granite-3.1-8B | **+1.57 [+0.76, +2.46]** |
| Llama-3.1-8B | **+2.31 [+1.27, +3.38]** |
| StarCoder2-15B | −0.69 [−1.57, +0.13] |
| CodeGemma-7B | +0.44 [−0.48, +1.36] |

Three above the clean control significantly, two indistinguishable from it. My original prediction —
merging never beats the control — is refuted on three and holds on two, so the honest summary is
**merging is at or slightly above the clean-code control on seen stacks, and well below breadth and
anchoring there** (below breadth on four of five, the exception being Llama-3.1-8B where they are level).

## The unseen-stack claim is the one that weakened

Earlier entries reported the merge above breadth on unseen-containing stacks on 4/4 models. CodeGemma
is the fifth and it is **flat**: −0.13 [−1.67, +1.44]. On X1 alone it is above breadth (+2.31) and above
anchoring (+2.72), but on the composed unseen stacks it has no advantage over anything. So "the merge
keeps its gain where breadth loses it" is 4 of 5, not universal, and CodeGemma is also the model where
breadth itself pays no unseen-stack tax (+0.03) — there is nothing for the merge to be better than.

That last point is worth keeping: on a model where breadth does not fail, the merge's advantage
disappears. It is consistent with the merge's benefit being the absence of breadth's tax rather than a
capability of its own.
