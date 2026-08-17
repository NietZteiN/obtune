### Target Date: 2026-08-15 (item-level agreement, and task-vector geometry is mostly initialization)

- **Hypotheses / what we're testing:** Two zero-GPU readouts, both gates on how the follow-up
  programme should be spent (plan: `.claude/plans/1-train-on-s2-family-valiant-noodle.md`).
  - **H1 (complementarity).** `merge_dare_ties` (.348) and `tuned_L0_k0` (.339) tie on `H1`. If
    the systems succeed on *different* items, distinct capability exists and is merely not
    extractable, which softens §12.10. CONFIRM if the oracle over the H1 ladder sits at or above
    a marginal-preserving independence null; REFUTE if it sits below it.
  - **H2 (geometry coverage).** The task-vector geometry thread has reports for only 2 of the 6
    banks on disk. Exploratory: cover the LOTO folds, the 3-seed `L0` bank and the seed-42 bank,
    and ask whether geometry predicts the **LOTO diagonal** (an OOD statistic) rather than
    in-distribution merged accuracy — the half of `CLAIM_LADDER.md` Branch C that is unsupported.

- **Setup:** Host `csr-94608`. **Zero GPU** — every number below is computed on CPU from cell
  parquets and adapter safetensors already on disk. GPU 0 held by the borrower (45.8 GB); the
  `fill22` pipeline stage was left running and untouched. Seed 17 throughout; the permutation
  null uses `numpy.default_rng(17)`, 2000 draws.

  | new / changed | what |
  |---|---|
  | `scripts/analysis/24_item_agreement.py` | new. Pairwise 2×2 + exact McNemar + Jaccard + oracle-of-k, **with a marginal-preserving permutation null**, over an arbitrary system list on one condition. Refuses to pool across grids by item-set identity, not by length. |
  | `scripts/merge/20_geometry_report.py` | `--seeds` added (additive). The script could not express a cross-seed bank at all: `dirs` was `{cond}_r{rank}_s{seed}` for a single seed, so the 3-seed `L0` control was unmeasurable. |
  | `results/analysis/item_agreement_main_qwen25c-1.5b_python_H1.json`, `results/analysis/item_agreement_gridA_H1.json` | H1 agreement, both grids |
  | `results/merge_geometry/{loto,l0seeds,adapters_s42}_qwen25c-1.5b_python.json` | the three uncovered banks |

  Commands:
  ```
  PYTHONPATH=src python scripts/analysis/24_item_agreement.py --condition H1
  PYTHONPATH=src python scripts/analysis/24_item_agreement.py --condition H1 \
      --systems base tuned_L0_s17 tuned_L1b_s17 tuned_L1r_s17 tuned_L2_s17 tuned_S1_s17 \
                tuned_S2_s17 mono_all ctl_r64 oracle_prompt_1shot \
      --out results/analysis/item_agreement_gridA_H1.json
  PYTHONPATH=src python scripts/merge/20_geometry_report.py --root runs/adapters_loto \
      --conditions L1b-L1r-L2-S1-S2 L0-L1r-L2-S1-S2 L0-L1b-L2-S1-S2 L0-L1b-L1r-S1-S2 \
                   L0-L1b-L1r-L2-S2 L0-L1b-L1r-L2-S1 --out results/merge_geometry/loto_*.json
  PYTHONPATH=src python scripts/merge/20_geometry_report.py --conditions L0 --seeds 17 42 101 ...
  PYTHONPATH=src python scripts/merge/20_geometry_report.py --seed 42 --conditions L0 L1b L1r L2 S1 S2 ...
  ```

- **Results:**

  **Item agreement on `H1`.**

  | | Grid B (n=115, 7 systems) | Grid A (n=1214, 10 systems) |
  |---|---|---|
  | best single | .348 `merge_dare_ties` | .280 `tuned_S2_s17` |
  | oracle-of-k | .487 | .390 |
  | raw headroom | +13.9 pts | +11.0 pts |
  | independence null | **.936** [.896, .974] | **.919** [.905, .932] |
  | observed − null | **−44.9 pts** | **−52.9 pts** |
  | mean pairwise φ | +.625 | +.621 |
  | items solved by 0 systems | 59 / 115 | 740 / 1214 |
  | items solved by all | 17 | 40 |

  Grid B headline pair, `merge_dare_ties` × `tuned_L0_k0`: both 34 / a-only 5 / b-only 6 /
  neither 70; McNemar p = 1.000; Jaccard .756. Grid A sole-solve counts: `mono_all` 18,
  `tuned_S2_s17` 16, `oracle_prompt_1shot` 15, every other system ≤ 9.

  **Task-vector geometry, epoch 3, pooled over modules.**

  | bank | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
  |---|---|---|---|---|
  | `L0` × seeds {17, 42, 101} — **same data** | **0.053** | **0.487** | 0.765 | 0.374 |
  | 8 specialists, seed 17 | 0.592 | 0.391 | 0.861 | 0.371 |
  | 6 specialists, seed 42 | 0.575 | 0.388 | 0.845 | 0.370 |
  | 6 LOTO folds, seed 17 | 0.576 | 0.382 | 0.850 | 0.804 |

  Individual `L0` cross-seed pairs: 0.0533 / 0.0531 / 0.0539. Same-seed `L0|S3` = 0.697,
  `L0|S1` = 0.522. LOTO fold mean-cosine-to-others spans 0.5653 (`holdS1`) – 0.5829 (`holdL1r`);
  fold norms span 0.7998 – 0.8099.

- **What worked / hypothesis verdict:**
  - **H1 ✗ REFUTED, decisively and on both grids.** The observed oracle sits 45–53 points *below*
    a null that only destroys item-difficulty coupling. The systems are highly redundant
    (φ ≈ .62) and the solved-count distribution is bimodal — 51 % / 61 % of items are solved by
    nothing at all, 15 % / 3 % by everything. The item-level analysis **hardens** §12.10 rather
    than softening it. The raw "+13.9 pts of headroom" is a k-artifact and must never be quoted
    without the null.
  - **H2 → the answer is that the diagnostic does not measure what it is assumed to measure.**
    See Observations; this supersedes the framing of the geometry half of §5.3.

- **Observations:**

  **Pairwise task-vector cosine is dominated by shared initialization, not by learned content.**
  Three adapters trained on **byte-identical data** are near-orthogonal (0.053) with sign conflict
  at 0.487 — a coin flip, i.e. maximum disorder — while eight adapters trained on **completely
  different transforms** are 0.59-aligned. LoRA initializes `A` randomly and `B` at zero, so each
  seed selects a different rank-32 subspace; two same-seed adapters share that subspace and drift
  together, two different-seed adapters do not. Every cosine and sign-conflict figure in
  MASTER_REPORT §5.3 is same-seed, so it measures **drift within one shared subspace**, and cannot
  be read as "how different is the knowledge" — which is exactly how the Horoi replication frames
  it. The §5.3 observations stand as observations; their interpretation does not.

  **Sign conflict does not bound merged accuracy, and the L0-merge control already proved it.**
  That control is the worst-geometry merge in the project — cosine 0.05, sign conflict 0.487,
  TIES keep 0.765 — and it merges fine: `l0merge_dare_ties` = .339 on `H1`, identical to
  `tuned_L0`, and within ~3 pts of the six-specialist merge on every trainable condition. A merge
  at maximal sign conflict lost nothing. This is stronger than §5.3's existing "the mechanism
  reproduces but the consequence does not": the premise itself fails.

  **The LOTO folds are essentially one vector.** Dropping an entire transform from a
  five-condition mixture moves the task vector (mean cosine range 0.018, norm range 0.010) less
  than the spread between folds. §12.10's conclusion, visible directly in weight space for the
  first time. The ordering does not track the diagonal — `holdS1` is the most geometrically
  distinct yet mid-pack on accuracy (37.3), `holdL0` the least distinct and highest (41.7) — which
  is a first, n=6 and therefore suggestive, data point against Branch C's "predicts" half.

  **Confound found in an existing comparison** (verified from `run_manifest.json`, not from a
  config comment). `configs/train/loto_qwen1.5b_py_hold*.yaml` asserts `train_size: 30000` caps
  every fold and `mono_all` at 30,000. It never binds: the 38,346 figure it reasons from is *all
  splits* (`train 26,841 / test 9,588 / val 1,917`). Realised `n_train` is **22,152–23,373** per
  fold against `mono_all`'s **26,841**, so `mono_all` saw 21 % more data and "LOTO diagonal 38.0
  vs `mono_all` 39.1" is not like-for-like. The direction favours the existing conclusion — the
  true cost of holding a transform out is *smaller* than 1.1 pts — but the comment is wrong.
  Separately: `tuned_L0` reaches the same diagonal on **4,689** rows, a fifth of either.

- **New questions / new hypotheses:**
  - **H3: is LoRA merging insensitive to task-vector orthogonality?** The L0 control says merging
    survives cosine 0.05 / conflict 0.49. Test directly by building a **cross-seed 6-specialist
    merge** (one expert per seed; the seed-42 bank exists). CONFIRM if it lands within noise of
    the same-seed `merge_dare_ties`; REFUTE if it collapses. ~1 GPU-h, and if confirmed the claim
    is about adapter composition in general, not about obfuscation.
  - The geometry→accuracy regression (~45 merge points now on disk) must be **stratified by seed**;
    pooling same-seed and cross-seed points would fit a line through an artifact.
  - Does the same init-dominance hold at other ranks? Every bank here is r=32.

---

### ADDENDUM, same day — H3 answered: merging IS seed-sensitive, but only DARE-TIES

H3 above predicted merging would be insensitive to task-vector orthogonality. **Refuted for
DARE-TIES, confirmed for TIES.** Built `scripts/merge/24_crossseed_control.py` (CPU) +
`configs/eval/crossseed_merge_qwen1.5b.yaml`; job `150_crossseed_merge`, 59.3 s on gpu0, rc 0.

Bank: same six conditions, same rank/recipe/density, only the seed assignment altered
(`L0@17, L1b@42, L1r@17, L2@42, S1@17, S2@42`) — 9 of 15 pairs cross-seed, mean cosine
**0.563 → 0.246**. Magnitude-checked before queueing (the `merge_dare_linear` lesson):
‖ΔW‖ ratios 0.244 / 0.675 vs 0.189 / 0.623 same-seed — nothing collapsed.

| bank | cos | L0 | L1b | L1r | L2 | S1 | S2 | mean |
|---|---|---|---|---|---|---|---|---|
| `merge_dare_ties` pure s17 | 0.563 | 49.4 | 39.8 | 42.0 | 50.0 | 44.1 | 44.3 | **45.0** |
| `merge_dare_ties_s42` pure s42 | 0.575 | 50.6 | 40.3 | 43.8 | 48.9 | 43.4 | 46.6 | **45.6** |
| `crossseed_dare_ties` MIXED | 0.246 | 45.5 | 36.9 | 40.9 | 44.9 | 40.0 | 39.8 | **41.3** |
| `merge_ties` pure s17 | 0.563 | 41.5 | 31.8 | 34.1 | 38.6 | 38.6 | 32.4 | 36.2 |
| `merge_ties_s42` pure s42 | 0.575 | 41.5 | 32.4 | 33.0 | 39.2 | 37.9 | 33.0 | 36.2 |
| `crossseed_ties` MIXED | 0.246 | 41.5 | 33.0 | 32.4 | 38.1 | 37.9 | 31.8 | 35.8 |

Cluster bootstrap by `program_id`, 2000 draws, seed 17, on 1,025 matched items / 40 programs:

| contrast | Δ pts | 95 % CI | McNemar |
|---|---|---|---|
| DARE-TIES mixed − pure s17 | **−3.61** | [−6.95, −0.30] | 0.0002 |
| DARE-TIES mixed − pure s42 | **−4.29** | [−7.51, −1.07] | <0.0001 |
| TIES mixed − pure s17 | −0.39 | [−1.40, +0.57] | 0.50 |

**The quality confound is ruled out, not argued:** both pure banks are equivalent (45.0 vs 45.6
for `dare_ties`; 36.2 vs 36.2 for `ties`), so the mixed bank's loss is attributable to *mixing
seeds*, not to the s42 adapters being individually worse. DARE-TIES is negative on all six
conditions.

**Mechanism.** DARE drops 50 % of each task vector at random and rescales the survivors. In a
shared subspace the survivors still reinforce; when the vectors are near-orthogonal, dropping half
destroys more than it preserves. TIES has nothing to lose — it is already the weaker merge (36 vs
45), and its sign election is near-random at cosine 0.05 either way.

**Implication for §12.10, and it goes the right way.** The **L0-merge control is necessarily
cross-seed** — three `L0` adapters can only differ by seed — while `merge_dare_ties` is same-seed.
So the control was running ~4 points handicapped relative to the arm it controls for. Corrected,
a seed-matched clean-code merge would land *above* the six-specialist merge on `H1` rather than
level with it. §12.10's conclusion ("the specialists contribute nothing distinct") is therefore
**understated**, not overstated — but the asymmetry has to be reported, because a reviewer who
notices the control is cross-seed will otherwise read it as a flaw.

**Caveats.** n=1 seed assignment; only two seeds exist for the specialists, so 6 of 15 pairs stay
same-seed and the true orthogonal-bank effect is likely *larger* than −4. No `H1` read (deliberate).

- **Next Steps:**
  1. Add the §5.3 caveat and the `--seeds` result to MASTER_REPORT; the geometry tables are not
     wrong but their reading is. **Also add the addendum's L0-control asymmetry to §12.10.**
  2. Correct the LOTO configs' size-matching comment in its own commit + entry, so an arm's diff
     stays about the arm.
  3. Build the cross-seed merge (H3) — cheapest remaining question with a general answer.
  4. Then the training arms (`s2fam`, `S7`, composites) per the plan; they size-match to 22,152.
