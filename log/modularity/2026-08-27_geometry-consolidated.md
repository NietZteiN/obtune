# 2026-08-27 — modularity — task-vector geometry consolidated, and the cross-seed bank's sign conflict

*The `modularity` thread was closed on 2026-08-27 (see `../writeup/2026-08-27_rq2-master-report.md`).
This entry is a documentation + zero-GPU analysis pass over work already done, plus two new numbers.
It does not reopen the thread.*

## Goal / hypothesis

Geometry results were spread across three sections of the master report, written at three different
times for three different reasons, with the later ones silently reinterpreting the earlier. Consolidate
into one section and answer the two questions left dangling: **(a)** what is the cross-seed control
bank's *sign conflict* — the 15 August readout reported only its cosine — and **(b)** can the
geometry→accuracy regression that `§12.12` and `§9` both list as owed actually be run?

## Setup

No GPU. `/data/jvl210002/conda_envs/obtune/bin/python`, `src/obtune/merge_geometry.py` used directly
(the `20_geometry_report.py` CLI's `--seeds` flag builds a conditions × seeds cross-product and
cannot express the alternating assignment), against the bank map in `scripts/merge/24_crossseed_control.py`:
`{L0:17, L1b:42, L1r:17, L2:42, S1:17, S2:42}`. Sign conflict over the standard sampled slice —
layers {0, 7, 14, 21, 27}, 35 modules. Accuracy points read from `results/cells/`, Grid B, mean over
the six trainable conditions. Output: `docs/MASTER_REPORT_2026-08-27.md` §14.

## Results

**(a) The cross-seed bank's sign conflict, computed for the first time.**

| bank | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
|---|---|---|---|---|
| 6 specialists @ s17 (the arm it controls) | 0.5633 | 0.3942 | 0.8399 | 0.3535 |
| 6 specialists @ s42 | 0.5708 | 0.3905 | 0.8427 | 0.3622 |
| **6 specialists, alternating s17/s42** | **0.2458** | **0.5653** | **0.6377** | 0.3525 |

Cosine reproduces the 15 August value (0.2458 vs 0.246). The two new columns are what matter:
**sign conflict rises 43 % and the TIES keep rate falls 20 points** — one fifth more of the update
magnitude is discarded by the sign election — against merged accuracy of:

| | same-seed s17 | cross-seed | Δ |
|---|---|---|---|
| `ties` | 36.17 | 35.77 | **−0.40** |
| `dare_ties` | 44.95 | 41.33 | **−3.62** |

**TIES — the algorithm that performs the sign election sign conflict is a theory of — is the one
that does not care.** The sensitivity lives in DARE's stochastic-dropout stage instead. That is a
sharper refutation than the L0-merge control gave, because here adapter quality is held fixed by
construction (the two pure banks are equivalent, 45.0 vs 45.6) and only the geometry moves.

**(b) The regression should not be run, and that is the finding.** Assembling the ~45 merge points
shows they occupy **four** distinct geometric regimes (same-seed s17, same-seed s42, cross-seed,
`L0`-seeds) and are near-constant *within* each — cosine 0.563 vs 0.575 and sign conflict 0.394 vs
0.388 across the two same-seed banks, while accuracy varies 9 points between algorithms on the same
geometry. A line fitted across regimes is identified almost entirely from the between-bank contrast,
i.e. from four effective observations, three of which differ in *what* they merge as well as *how*.
Reported as a four-row table. Filed as resolved in `§9`.

**Also newly tabulated in §14** (all from existing JSONs, none previously in any document): the
per-projection sign-conflict breakdown (`q_proj` 0.426 highest, `v_proj` 0.352 lowest; `down_proj`
drifts +0.053 over nine epochs against `gate_proj`'s +0.004, a 12× spread); the within-seed pair
structure (inert-material family `S2|S3` 0.698, `L0|S3` 0.697, `S2|S4` 0.691 — the tightest cluster
and the closest to the clean-code direction; `S1` furthest from every renaming condition at
0.457–0.465, reproduced on the s42 bank at 0.453–0.471); and `S1`'s smaller norm (0.331 vs
0.372–0.381), which is a data-volume effect since `S1` bails on short bodies.

## Observations

**The diagnostic now fails on four independent probes**, which is worth stating as a set rather than
as four scattered nulls: the cross-seed control (above), the `L0`-seed bank merging fine at
near-maximal conflict (0.487, keep 0.765 → `l0merge_dare_ties` = `tuned_L0` on `H1`), the within-bank
epoch sweep where sign conflict and accuracy correlate at **+0.84 / +0.998** — the wrong sign — and
the regression that cannot be identified. The epoch correlation is confounded with ‖ΔW‖ and does not
show that conflict *helps*; it does show the weaker sufficient claim that conflict does not *bound*.

**One geometry result is positive and it is evidence for the RQ2 conclusion, not against it.** The
six LOTO folds span cosine 0.559–0.607 and norms 0.7998–0.8099: dropping an entire transform from a
five-condition mixture moves the task vector *less than the spread between folds*. That is the
redundancy claim visible in weight space, independent of any accuracy measurement.

**The reusable lesson is a correction to how the merging literature reads its own diagnostic.** At
r=32, same-seed LoRA cosine is dominated by shared initialization — identical training data gives
0.05, completely different transforms give 0.59. Any geometry→accuracy analysis must be stratified by
seed. It costs seconds of CPU to check and it inverts the interpretation.

## Next steps

(1) None for this thread — it stays closed. (2) If `paper_modularity/` uses geometry, §14.7's four
carry-forward points are the claimable set, and the cross-seed control is the figure. (3) The r×r
contraction (`⟨ΔWᵢ,ΔWⱼ⟩ = sᵢsⱼ·tr((BᵢᵀBⱼ)(AⱼAᵢᵀ))`, verified to 5.6e-16) is worth releasing as a
standalone artifact regardless of which paper lands.
