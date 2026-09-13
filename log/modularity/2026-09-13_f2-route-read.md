# 2026-09-13 — H-F2-route read: the mixture of specialists does not pay the unseen tax either

**Thread:** modularity · **Status:** read against the pre-registered rule; verdict REFUTED · **Related:** [`2026-09-13_f1-routing-and-merging-on-stacks.md`](2026-09-13_f1-routing-and-merging-on-stacks.md), [`2026-09-13_merging-on-the-panel.md`](2026-09-13_merging-on-the-panel.md)

## Provenance

`ev_f2_mole` 393091 (`obtune.mole.eval_mole`, h200, 60 min, 24 cells: four routing arms + base on the
six X1-containing composites), read by `scripts/analysis/61_f2_route.py` against the controls in
`f2_divergence` on the same items → `results/analysis/pipeline/f2_route_codellama7b.json`. 319 programs
common to every cell on the four fully-unseen-containing stacks; 291 on the two half-unseen ones.

## Numbers (points, paired, four unseen-containing stacks pooled)

| contrast | value |
|---|---|
| `mole_router − mono_all` | **+2.88 [+1.33, +4.41]** |
| `mole_router − tuned_L0` | **+1.39 [+0.26, +2.51]** |
| `mole_router − mole_random` | −0.03 [−0.99, +0.84] |
| `mole_router − mole_uniform` | +0.10 [−0.84, +0.99] |
| `mole_hardrouter − mole_router` | −0.13 [−0.44, +0.18] |
| `mole_router − cons_lam3` | −0.86 [−2.04, +0.26] |
| `mole_uniform − base` | **+14.98 [+12.81, +17.29]** |
| `mono_all − tuned_L0` | −1.49 [−3.08, +0.08] |
| `cons_lam3 − tuned_L0` | **+2.25 [+0.86, +3.61]** |

Half-unseen stacks (C_L1r_X1m, C_S1_X1s): router − mono_all **+3.61**, router − tuned_L0 **+2.12**,
router − random **+1.61**, router − cons_lam3 −1.03 n.s.

## Verdict

**H-F2-route REFUTED** by the registered rule (`mole_router − tuned_L0` ci_lo +0.26 > 0). My prediction
was CONFIRMED ("no gate can route to competence no expert has, so the mixture should sit where breadth
sits"). It was wrong in the same way the merging prediction was wrong: the mixture of specialists,
under any gate, sits **above breadth by 2.9 points and above the clean control** on stacks containing
the unseen family, level with the anchored arm (−0.86 n.s.). The *routing* is worth nothing there
(router = random gate = uniform gate = argmax); the *mixture* is worth everything, as on seen stacks.

## What it means, held for the user

With the merging result this is now a pattern: **every strategy that keeps the specialists as separate
objects — mixing them at inference or merging them in weight space — avoids the unseen-family tax
that a single adapter trained on all five transforms pays.** Breadth is the one composition strategy
that pays it. The paper's RQ1 says "routing tracks breadth wherever the two are measured together and
inherits its verdict"; on the one stimulus that decides the composition test, routing is 2.9 points
above breadth. The tables carry it (the fourth column of the composition table, Appendix B's routing
grid); the prose is held at the user's instruction and the contradiction is marked in the source.
