# modularity — RQ2 — router, merges, monolithic, oracle arms

*Last updated: 2026-08-17*
**Status:** active — router saturated (100% route accuracy); the uniform-epoch sweep, the merge-optimal
search, the DARE-linear repair and the mixture ladder have all landed; `mole_random` re-run and no
longer inert. Blocking now: the Grid A baseline panel is 33 cells short from `eval_source` resume
aliasing, and 21 already-collected 7B Grid A cells have no matched floor

## Hypotheses — open
- (see [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) for the full ledger)

## Hypotheses — resolved
- **Does training deliberately for the inert-material family (`S2`+`S3`+`S4`) widen the one transfer
  that works?** ✗ refuted. `s2fam` lands **+0.02 pts** [−0.95, +1.02] on the clean-code control and
  −0.07 on `mono_all` — flat, with an unusually tight interval. It still tops the `S2` (43.8) and
  `S1` (41.4) columns and is worst on `L1b` (32.0): wins where it trained, nowhere else. H1
  deliberately unread, so §3.5 is untouched —
  [`2026-08-17_attempted-repairs-are-null.md`](2026-08-17_attempted-repairs-are-null.md).
- **Does training on STACKED transforms beat the same mechanisms unstacked?** ✗ refuted, and the sign
  runs against it: **−1.36 pts** [−2.63, +0.04]. Same six mechanisms, same 22,152 rows, same recipe,
  differing only in whether two mechanisms arrive in one program or two — same entry.
- **Do the H1 systems carry complementary capability that combination fails to extract?**
  ✗ refuted, both grids. The oracle over the ladder sits **45–53 pts below** a null that preserves
  every marginal accuracy and destroys only item-difficulty coupling (φ ≈ .62; 51 %/61 % of items
  solved by *nothing*). The systems are redundant; the raw "+13.9 pts headroom" is an
  oracle-of-k artifact —
  [`2026-08-15_item-agreement-and-seed-geometry.md`](2026-08-15_item-agreement-and-seed-geometry.md).
- **Is LoRA merging insensitive to task-vector orthogonality?** → **algorithm-specific.**
  Same six conditions, same recipe, only the seed assignment altered (mean cosine 0.563 → 0.246):
  **`dare_ties` loses 3.6–4.3 pts** (CI excludes zero, McNemar p<0.001, negative on all six
  conditions) while **`ties` loses 0.4** (CI spans zero). Both *pure* banks are equivalent
  (45.0 s17 vs 45.6 s42), so it is the mixing, not adapter quality. Consequence: the **L0-merge
  control is necessarily cross-seed and was ~4 pts handicapped** against the same-seed arm it
  controls for — which makes §12.10's "specialists contribute nothing" *understated* —
  [`2026-08-15_item-agreement-and-seed-geometry.md`](2026-08-15_item-agreement-and-seed-geometry.md) addendum.
- **Does task-vector sign conflict bound merged accuracy?** ✗ refuted. Three `L0` adapters
  trained on byte-identical data are near-orthogonal (cosine **0.053**, sign conflict **0.487** —
  a coin flip) because LoRA's random `A` init picks a different subspace per seed, yet the
  L0-merge control built from them merges *fine* (`.339` on H1 = `tuned_L0`). Same-seed cosine
  (0.59 across eight different transforms) measures shared init and common drift, not shared
  knowledge — so every §5.3 geometry figure needs that caveat — same entry.
- **Is RouterLoRA's gain a *blend* of experts, or per-token *selection*?** → selection.
  `mole_hardrouter` (the trained gate argmaxed to one-hot, identical weights) reproduces
  `mole_router` to mean |Δ| 1.0 pt / max 2.7, signed both ways, all inside the 3.61-pt p95 seed
  band. "Mixture" is the wrong word for the system —
  [`2026-08-14_gridA-resume-aliasing-and-readouts.md`](2026-08-14_gridA-resume-aliasing-and-readouts.md).
- **Do routing gains transfer to an unseen transform?** ✗ refuted. On H1 all four ladder arms
  (`uniform`, `random`, `router`, `hardrouter`) land at 32.2–33.9: the trained router's 3–5 pt
  edge on the composites is exactly zero where no expert matches the input.
- **Is "demos make the adapter worse" (§11.2) a format-compliance artifact?** ✗ refuted from
  existing cells. The adapter's format-fail rate is flat in k (1.8→1.9→2.3→1.9) and conditioning
  on format-OK trials preserves the k0 > k1,k2,k4 ordering. Demos make it answer wrong, not
  malformed. The trained-with-demos adapter is still needed for the subtler reading.
- **Does merge-objective checkpoint selection beat accuracy-optimal `best`?** ✗ refuted. 27 candidates
  over 3 greedy rounds span 0.7 accuracy points, and every round's winner is 0.7–1.0 pts BELOW
  `merge_dare_ties` (all p>0.4) — [`../writeup/2026-08-13_fse-modularity-draft-v0.1.md`](../writeup/2026-08-13_fse-modularity-draft-v0.1.md).
- **Does over-training the experts harm merging (Horoi et al.)?** ✗ refuted as a *consequence*, on the
  full 8-expert bank with epochs held uniform. Sign conflict rises 0.401→0.425 (mechanism present),
  while merged accuracy IMPROVES on 11 of 12 method×condition pairs; pooled e9−e1 = +3.1 [+0.0,+6.1]
  for `dare_ties`. Both caveats in `MASTER_REPORT` §5.3 (3-vs-8 experts, unequal epochs) are removed.
- **Was `merge_dare_linear` an algorithmic result?** ✗ a scaling defect. Repaired (`dl_rescaled`):
  +41.6 [+33.9,+49.9] pooled, parity with the clean-code control, format-fail 53.5% → 0.6–2.8%.

## What worked
- **Computing task-vector geometry from the r x r factors.** Frobenius inner products between
  LoRA updates need no dense dW: `<dW_i,dW_j> = s_i s_j tr((B_i^T B_j)(A_j A_i^T))`. Turns an
  intractable 8-expert x 3-epoch x 196-module sweep into seconds of CPU. Verified against dense
  to 5.6e-16.
- **Reusing existing checkpoints as a training-length sweep.** Every expert kept its epoch-1/2/3
  checkpoints, so the whole geometry study cost zero GPU.

## What didn't
- **`mole_random`, entirely.** Bit-identical to `mole_uniform` on all 1,299 items: a `ConstantGate`
  exposes no parameters, so the arm's re-init loop is a no-op once `mole_uniform` has run first.
  The residency question is unanswered and the mixture headline is blocked —
  [`2026-08-13_mole-random-inert-control.md`](2026-08-13_mole-random-inert-control.md).
- **The overtraining hypothesis, as applied to the existing bank.** Sign conflict FALLS with
  training (0.402 -> 0.391) and TIES retention rises. Cause: we never reach the regime — loss is
  still falling at epoch 2.5. Not a refutation of the paper, a boundary condition on our setup.
- **Sign conflict as the explanation for `merge_ties`' collapse.** Election retains 86% of mass,
  but merge_ties' ||dW|| is 0.19x a single expert's. Still unexplained.

## Open ideas
- Router saturation and merge failure may be two symptoms of ONE cause: over-specialised experts
  are trivially distinguishable (easy to route) and mutually interfering (hard to merge). Joint
  prediction: undertrained experts should be harder to route AND easier to merge. Neither
  literature makes it; this project has both systems built. **Now the most promising open idea in
  the thread** — it is `CLAIM_LADDER.md` Branch D, and the under-trained bank it needs is a
  by-product of the 9-epoch sweep that has already run.

## Entries
- [`2026-08-17_attempted-repairs-are-null.md`](2026-08-17_attempted-repairs-are-null.md) —
  both attempted repairs to the negative result are null (+0.02 and −1.36); `allow_composites` was
  missing from `run_ckpt_select` (would have failed after a 5.3 h train) and from `preflight`.
- [`2026-08-15_item-agreement-and-seed-geometry.md`](2026-08-15_item-agreement-and-seed-geometry.md) —
  the H1 systems are redundant, not complementary (oracle 45–53 pts *below* a marginal-preserving
  null); and task-vector cosine is dominated by shared init, not learned content, so §5.3's
  geometry cannot be read as "how different is the knowledge".
- [`2026-08-13_mole-random-inert-control.md`](2026-08-13_mole-random-inert-control.md) — the RouterLoRA
  control never randomised; diagnosis, blast radius, and the fix.
- [`2026-08-11_part3-task-mismatch-and-merge-optimal-collision.md`](2026-08-11_part3-task-mismatch-and-merge-optimal-collision.md)
  — audit of never-executed code: the gate would have trained on the wrong task; merge-optimal names collided.
- [`2026-08-11_routerlora-build-and-composite-purity.md`](2026-08-11_routerlora-build-and-composite-purity.md)
  — RouterLoRA built end to end; composite purity was vacuous and skipped the H1 content scan.
- [`2026-08-10_overtraining-and-merge-geometry.md`](2026-08-10_overtraining-and-merge-geometry.md)
  — geometry null + the reason for it; forgetting gate run for the first time; six bugs.

## Doc / results links
- [`../../docs/REPORT_2026-08-17_geometry-and-attempted-repairs.md`](../../docs/REPORT_2026-08-17_geometry-and-attempted-repairs.md)
  — self-contained account of the 15–17 Aug chain: item-level redundancy, geometry as an
  initialization artifact, the cross-seed merge control, and the two null repairs
- [`../../docs/REPORT_2026-08-15_modularity_verdict.md`](../../docs/REPORT_2026-08-15_modularity_verdict.md)
  — the 13–15 Aug chain that closed RQ2 by elimination
- [`../../paper_modularity/`](../../paper_modularity/) — the FSE manuscript this thread feeds, with
  `CLAIM_LADDER.md` recording which pending run licenses which headline
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
