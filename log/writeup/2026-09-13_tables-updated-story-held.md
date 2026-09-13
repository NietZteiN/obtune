# 2026-09-13 — Tables carry the new results; the story is held at the user's instruction

**Thread:** writeup · **Status:** done · **Related:** [`../modularity/2026-09-13_merging-on-the-panel.md`](../modularity/2026-09-13_merging-on-the-panel.md), [`2026-09-13_master-tables-in-the-paper.md`](2026-09-13_master-tables-in-the-paper.md)

User: *"push again and update paper tables with results don't change story yet."*

So the generated tables are regenerated from the cells as results land, and the **interpretive prose
is reverted to its pre-merging-result state**. Specifically, `93d8bf6`'s rewrites of
`sections/{abstract,intro-2,rq1}.tex` — which had narrowed "merging fails both tests" to the measured
statement — are backed out with `git checkout 93d8bf6^`. What is kept from that commit:

- `tables/rq1_merge_panel.tex` and its `\input` in RQ1, introduced by one neutral sentence
  ("Table~\ref{tab:rq1_merge_panel} reports the same merge arms measured across the panel") and no claim.
- A Threats paragraph naming what the merge measurement does not cover (no backward run).
- The merging grids for Granite and Llama-3.1-8B in Appendix~B.

**The paper is now internally inconsistent on purpose, and it must not go out this way.** §RQ1 says
merging "does not compose at all" and that "merging and breadth fail both tests"; Table 6 on the same
page shows the best merge above the clean-code control on seen stacks on 3/3 models and above breadth
on unseen-containing stacks on 3/3. A LaTeX comment at the `\input` site says so and names the two
ways out (narrow the claim, or move the table to the appendix). The decision is the user's.

The routing prose from `bf25364` is **not** reverted: the sentence it replaced carried
`+0.0000 [−0.0081, +0.0081]`, which is the single-transform, testset-grid number, and it sat directly
above a table now showing `+1.34 [+0.48, +2.17]` on the stacks. Restoring it would put a contradicted
number in the body text rather than hold a framing. Said plainly to the user, who can reverse it.

Queue at the time of writing: `ev_merge_starcoder2-15b` (393090) and `ev_f2_mole` (393091) moved from
h100, where they had been waiting behind other users, onto idle h200 nodes within obtune's two-slot
share. Their results will appear in the tables on the next regeneration; neither changes prose.
