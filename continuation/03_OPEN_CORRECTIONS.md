# 03 — Owed corrections

All diagnosed, none applied. Each is a commit, not a run — no GPU required. Grouped by how much
damage leaving them does.

---

## A. Would change how someone reads a published number

### A1. Determinism note in `CLAUDE.md` §4, and an `ACCESS_LOG.md` reconcile

Master report §8.9. `tuned_L0` on Grid B `H1` reads **40.0 / 34.8 / 33.9** across three passes. The
last two are identical in *every* recorded field — adapter path, prompt sha `c1e8fe28…`, 115 items,
`vllm-0.26.0`, T=0 / top-p 1.0 / max_tokens 64, git commit `469f857`, GPU 1 — and still differ on
**12 of 115 generations**, flipping 5 graded trials. Across the commit boundary: 31 of 115
generations, 6.1 points.

The recorded floor elsewhere in the project is "0.1–0.4 points from batching nondeterminism," which
understates this by 2–15×.

**Owed:** (a) a determinism note in `CLAUDE.md` §4's silent-failure list stating the real band;
(b) an `ACCESS_LOG.md` reconcile — one `pilot_eval` plus two `final_eval` passes on the same
quarantined items is more `H1` exposure than §3.2 rule 3 sanctions.

### A2. Seed-band constant in three script docstrings

Master report §8.10. The noise floor is reported three ways — Python **0.63 / 1.46**, JavaScript
2.01 / 4.03, pooled 1.32 / 3.61 — and the **pooled** figure is what propagated into code:

- `scripts/merge/24_crossseed_control.py`
- `scripts/merge/25_residual_merge.py`
- `scripts/attn/30_knockout.py`

Every experiment in RQ2 and RQ3 is Python, so the bar has been ~2.5× too permissive. The docs are
already corrected; the docstrings are not.

### A3. LOTO `train_size` correction

Master report §8.12. `train_size: 30000` never binds in the LOTO configs — they reason from 38,346
rows, which is *all* splits. Realised: folds **22,152–23,373**, `mono_all` **26,841** (+21 %). So
"LOTO diagonal 38.0 vs `mono_all` 39.2" is not like-for-like. Direction is favourable to the
conclusion (the true cost of holding a transform out is *smaller* than the reported 1.1 pts), which
is why it is not urgent — but it should land in its own commit so the correction is auditable.

---

## B. Stale claims that are now answered

### B1. `merge_ties` ‖ΔW‖ = 0.19× is no longer unexplained

Recorded as open in two places:

- `log/modularity/README.md`, under **What didn't**: *"Sign conflict as the explanation for
  `merge_ties`' collapse. Election retains 86 % of mass, but `merge_ties`' ‖dW‖ is 0.19× a single
  expert's. Still unexplained."*
- `paper_modularity/NUMBERS.md:78` — carries it into the draft as **"measured, unexplained."**

**The answer** (master report §14.4b): retention and magnitude are different quantities. The sign
election retains 86 % of magnitude *per surviving coordinate*, but averaging six task vectors that
are only 0.56-aligned cancels most of the vector sum. This also explains the ~9-point TIES vs
DARE-TIES gap — TIES keeps 0.19× a single expert's update, DARE-TIES 0.62×, i.e. **3.3× more
surviving signal** — and accuracy follows.

**Owed:** move the bullet in `log/modularity/README.md` from *What didn't* to *Hypotheses —
resolved* with the answer; update `NUMBERS.md:78` to point at §14.4b.

### B2. Branch C fires — this reverses a verdict recorded on 2026-08-27

Master report §12.13 currently states `CLAIM_LADDER.md` Branches **B, C and D are dead**. That was
written before the `‖ΔW‖` result. Branch C's gate reads:

> *"Fires if: the geometry quantities (sign conflict, cosine, **‖ΔW‖**) predict merged accuracy
> across a wider bank than we currently have — i.e. the density sweep and the second seed produce
> enough merge points to regress accuracy on geometry."*

Both prerequisites landed, `‖ΔW‖` is named in the gate, and it predicts at **ρ = +0.86** (n = 17).
It fires in *full*, since its headline is "predicts but does not prescribe" and the merge-optimal
search (27 candidates, 3 rounds, 0.7 points, every round's winner below status quo) supplies the
second half.

> **Do not apply this correction until the robustness check below passes.**

**Blocking check.** The obvious objection is that ρ = 0.86 restates "DARE-TIES beats TIES" —
algorithm is confounded with norm (TIES merges cluster at 0.06–0.20, DARE-TIES at 0.12–0.57).
Within-algorithm signal does exist: the `dare_ties` density sweep is monotone in both norm and
accuracy (0.567 / 0.226 / 0.115 → 47.03 / 44.71 / 40.53) while `ties` is flat in both
(0.066 / 0.069 / 0.064 → 35.54 / 35.89 / 36.29). But **report ρ per algorithm and a partial
correlation controlling for an algorithm indicator** before this enters a manuscript. If the
within-algorithm ρ collapses, downgrade §14.4b to "norm separates the two algorithms and identifies
the DARE-linear defect" and leave Branch C dead.

**Owed if it passes:** rewrite §12.13's branch verdict; update `paper_modularity/CLAIM_LADDER.md`
Branch C from "half-supported" to fires; consider a sixth entry in its settled list, since the norm
predictor holds whichever branch fires.

---

## C. Bookkeeping

- **`§14.4b` is missing from the master report's table of contents.** Every other anchor and
  relative link in the document validates.
- **The master report changelog** needs the `‖ΔW‖` column (136/169 rows) and, if B2 passes, the
  Branch C reversal.
- **`docs/RESULTS_BOOK_2026-08-11.md`** is the tables-first sibling of the master report and is now
  16+ days stale. Either regenerate it from the same collector or mark it superseded — it currently
  carries no banner and will mislead.
- **`paper_modularity/main.tex` has a deliberately empty thesis slot.** Branch A ("modularity does
  not rescue robustness") is fully supported by what is on disk and should fill it. Branches B and D
  are dead: B needed the composite gate effect to survive at corpus scale and the mixture ladder
  turned out to carry two copies of the same control (`mole_random` has entropy 1.000 and uniform
  mass, i.e. it is behaviourally a second uniform gate); D needed under-trained experts to be harder
  to route and easier to merge, and the uniform-epoch sweep shows merged accuracy *rising* with
  training.

---

## D. A convention worth keeping

Two of the corrections above exist because a number was copied forward from a report instead of
being read from a result file. `paper_modularity/README.md` already records the rule — **every
number is read from a result file, never from a report; reports are an index of where to look** —
and it has caught four report-vs-file discrepancies so far.

Related, and learned expensively on 2026-08-27 while regenerating the master table: **a regenerated
artifact that silently disagrees with the one it replaces is worse than no regeneration.** Three
successive regenerations were wrong (a dropped `base` Grid B row that re-imported a known 4-point
engine offset; an oldest-first timestamp tie-break; a double-rounding). None was visible by
inspection; all were caught by diffing against the predecessor. **The acceptance test for any
regenerated table is "does it reproduce the predecessor exactly, plus the new rows" — not "does it
look right."**
