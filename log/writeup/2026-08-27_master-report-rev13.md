# 2026-08-27 — writeup — master report rev 13: the 08-12 document brought current

*Second entry today; the first is [`2026-08-27_rq2-master-report.md`](2026-08-27_rq2-master-report.md),
which closed RQ2. This one folds that plus everything else since 12 August into the project-wide
master report.*

**Goal.** `MASTER_REPORT_2026-08-12.md` is the most detailed document the project has — §2.2 alone
carries every system against every condition — but it had drifted 15 days. It still said *"RQ3
(attention) has not been run"*, knew nothing of the `normalization` thread, carried a §7 whose
general-ability benchmark had since been shown contaminated, and had a §2.2 table missing ~54
systems. Copy it forward to `MASTER_REPORT_2026-08-27.md` and bring every section current.

**Setup.** No GPU. `/data/jvl210002/conda_envs/obtune/bin/python` over all 2,215 per-cell parquets
(1,918 at 1.5B/Python, 227 at 1.5B/JavaScript, 70 at 7B/Python; 1,046,382 graded trials),
`results/analysis/*.json`, `results/merge_geometry/*.json`, `results/router/.../routing_report.json`.
Contrasts recomputed as paired cluster bootstrap by `program_id`, 2,000 resamples, seed 17.

**Results.**

**§2.2's master table was regenerated in full rather than patched** — **154 systems in 169 rows**,
up from 73 in 74, emitted programmatically from the parquets.

**One row per system PER GRID, which is the consequential change.** Fifteen systems were measured on
both grids and had been sharing a single row — including `merge_ties`, `merge_dare_ties`, both
`l0merge_*` and both `residual_n6_*`, each of which is Grid B throughout but was given a Grid A `H1`
read. Values disagree by up to 16 points across the pair (`residual_n6_s42_d0p5`: .256 A vs .417 B).
**That shared row is the mechanism by which the RQ2 conclusion came to rest on 115 items.** Now every
cell in a row belongs to the grid its `grid` column names, `H1` included, and a sparse `A` row
carrying only `H1` is informative rather than a gap.

**Duplicate cells are resolved by a documented source preference**, inherited from the 08-12
revision rather than invented: prefer vLLM over the `hf-mole` mixture engine except for `mole_*`
rows which must be read through it; then larger n; then newest. **41 cells have duplicates that
disagree, 27 of them by more than 0.5 points**, and 5 are settled by the engine rule alone.

**Verified against the 08-12 table: all 74 of its rows present, every value reproduced exactly, 0
differences, 0 blanks where it had a number.**

**Sections added:** §7.8 (MBPP+ overturns two CFT claims), §12.12 (item-level redundancy, geometry
as an initialization artifact, cross-seed control, residual merge), §12.13 (RQ2 closed, with the
elimination table), §15 (RQ3 — anchoring sweep and causal knockout), §16 (symbolic normalization).
§1, §9 and §10 rewritten. §9 now lists nine resolved items with the section that closed each, rather
than deleting them.

**Corrections carried into the body, not just noted:** §12.4's "every cell inside the 3.61-pt seed
band" is corrected in place — 3.61 is the *pooled* Python+JavaScript band and the Python bar is
0.63/1.46, under which **4 of 15 `hardrouter − router` cells do not clear it** (max |Δ| 2.67 on
`C_L1b_S1`). §12.10's "the per-condition experts carry nothing distinct" is retired in the body and
in the banner on the 08-12 file. `mole_random` is footnoted as a **weaker control than its name
suggests** — a `RouterGate` at random init has mean normalised entropy 1.000 and uniform mass, so it
is behaviourally a second uniform gate.

**Observations.**

**Regenerating beat patching, and not marginally.** The intent was to append the missing rows. The
generator surfaced the shared-row grid problem within minutes — invisible when adding rows by hand,
unavoidable when a script must choose between two values for "the `H1` cell".

**But the first two regenerations were wrong, and only diffing against the old table caught it.**
Pass 1 collapsed `base`'s two grid rows into one (my tie-break preferred larger n, so the Grid B
floor vanished — and most rows in the table are Grid B) and re-imported the 4-point `hf-mole` engine
offset on `base`'s composites that the 08-12 revision had already found and fixed. Pass 2 sorted
timestamps oldest-first, silently reverting five systems to superseded reads. Pass 3 double-rounded
(0.408518 → 0.4085 → 0.408). **The lesson is cheap and general: a regenerated table that silently
disagrees with the one it replaces is worse than no regeneration, so the acceptance test is not
"does it look right" but "does it reproduce the predecessor exactly, plus the new rows".** That diff
is now recorded in the section itself.

**"What has not been run" is the section that ages worst and matters most.** Nine of its fourteen
items had been resolved and one — the HumanEval+ general-ability baseline — had been resolved in a
way that later turned out to be invalid (§7.8). A baseline that has already run is not the same as a
baseline that is valid, and the section now says so explicitly.

**The document's centre of gravity moved while nobody was editing it.** §1 was written around a
negative result with an unexplained exception. As of §15 and §16 the exception has a mechanism
confirmed by two independent instruments, and the negative result is closed. §10's ordering was
rewritten from that footing: item 1 is now `H2`/`H3`, because the step from "ignores inert material
on `S2`" to "transfers to `H1`" is inferential and no further `S2` measurement can convert it.

**Next steps.** (1) `RESULTS_BOOK_2026-08-11.md` is now 16 days stale and is the tables-first sibling
of this document — either regenerate it from the same collector or mark it superseded. (2) The five
corrections owed in §10 item 5 (LOTO `train_size`, the seed-band constant in three script
docstrings, the `CLAUDE.md` determinism note, the `ACCESS_LOG.md` reconcile). (3) Pre-register
`H2`/`H3`.
