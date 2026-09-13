# 2026-09-13 — Merging on the panel, fourth model: StarCoder2-15B

**Thread:** modularity · **Status:** read against the pre-registered rules · **Extends:** [`2026-09-13_merging-on-the-panel.md`](2026-09-13_merging-on-the-panel.md)

`ev_merge_starcoder2-15b` 393090 (h200, 56 min, 153 cells) → `merge_panel_starcoder215b.json`. The untuned
StarCoder2 fails the format contract on every forward cell (rate 1.000, accuracy 0), so its
`merge − base` contrasts are meaningless and are not read; the registered contrasts are against
`tuned_L0`, `mono_all` and `cons_lam3`, all well inside the gate. DARE-linear is format-gated on
several cells again and is never the best merge.

| stacks | merge − clean | merge − breadth | merge − anchored | breadth − clean | anchored − clean |
|---|---|---|---|---|---|
| seen (6) | −0.69 [−1.57, +0.13] | **−3.27 [−4.67, −1.86]** | **−5.73 [−7.05, −4.47]** | **+2.57** | **+5.04** |
| unseen-containing (4) | **+1.15 [+0.08, +2.17]** | **+1.70 [+0.05, +3.32]** | +0.39 [−0.92, +1.80] | −0.55 | +0.76 |

**H-merge-panel-a CONFIRMED, H-merge-panel-b CONFIRMED** — the only model where both registered rules
land as predicted. Across four models the seen-stack picture is now merge vs control +0.83* / +1.57* /
+2.31* / −0.69 and merge below breadth on three of four (level on Llama); the unseen-stack picture is
unchanged and sharper: **DARE-TIES above breadth on 4/4** (+2.35, +2.20, +3.09, +1.70, all significant),
at or above the clean control on 4/4, and against anchoring below on CodeLlama-7B, above on Granite,
level on Llama and StarCoder2. The paper's tables carry the fourth block; the prose is held at the
user's instruction (`../writeup/2026-09-13_tables-updated-story-held.md`).
