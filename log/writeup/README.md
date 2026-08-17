# writeup — Figures, paper draft, artifact packaging

*Last updated: 2026-08-13*
**Status:** active

## Hypotheses — open
- **H-S2:** the `S2`→`H1` transfer comes from both transforms burying the computation under *inert*
  material, so the learned skill is "ignore what cannot affect the result". CONFIRM if a
  pre-registered `H2` of the inert-padding family is reached by the `S2` adapter and a
  rearranging `H3` is not; REFUTE if `S2`→`H2` is null.
- **H-S2-half:** the `H1` transfer is attributable to dead code (`S3`) or to opaque predicates
  (`S4`), not to their combination. CONFIRM if one of `S3`/`S4` reproduces `S2`'s `H1` gain at full
  scale; REFUTE if neither does.
- (full ledger: [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md))

## Hypotheses — resolved
- **Q1 — is the pilot's diagonal-only profile a property of the regime or of `L1b`?** ✓ regime
  (mean off-diagonal transfer ratio 0.073), with `S2` as the single exception —
  [`2026-08-10_master-report.md`](2026-08-10_master-report.md).
- **Q2 — do the RQ2 arms recover what the monolithic arm loses?** ✗ refuted. A router with 1.000
  routing accuracy yields exactly the specialists' gains; merges are at or below the clean-code
  control; oracle prompting is ~20 pts below every adapter at 1.5B — same entry.

## What worked
- Writing the ATTRIB draft from result files directly, using `MASTER_REPORT`/`RESULTS_BOOK`
  only as an index of where to look. This is what caught the three run-to-run discrepancies
  recorded in [`2026-08-12_attrib-draft-v1.md`](2026-08-12_attrib-draft-v1.md) — two `base`
  numbers, two E8 tables, and superseded budget ratios in the planning doc.
- Aggregating from the per-cell parquets directly, keyed by the cell's system label, rather than
  through `obtune.trial_table` — whose `is_core` definition drifted when the `S3`/`S4` cells landed.
- Separating the two evaluation grids (corpus vs ICSE test set) before computing anything; they are
  disjoint in programs and pooling them averages different populations.

## What didn't
- `merge_dare_linear`: 5 % accuracy, 54 % format-fail. A broken arm, not a result.
- HumanEval+ forgetting harness: pass@1 = 0.0 for every adapter measured. Never validated.

## Open ideas
- RQ3 attention now has a concrete target: does the `S2` adapter re-anchor attention away from
  inert spans, and does that shift predict the `H1` gain?
- Oracle prompting at 7B+ — the RQ2 "know how but not when" branch is a scale question.

## Entries
- [`2026-08-13_fse-modularity-draft-v0.1.md`](2026-08-13_fse-modularity-draft-v0.1.md) — the FSE RQ2
  draft in `paper_modularity/`, written from 897 cells; four sections of the master report are stale,
  and the mixture arm's decisive control turned out to be inert.
- [`2026-08-12_attrib-draft-v1.md`](2026-08-12_attrib-draft-v1.md) — ATTRIB draft v1 written
  from result files; the paper is not blocked on the four queued runs, and it currently has
  no figure (the dose ladder is the natural Fig. 1 and its adapters are already trained).
- [`2026-08-10_master-report.md`](2026-08-10_master-report.md) — master report over all 453 cells.

## Doc / results links
- [`../../paper_modularity/`](../../paper_modularity/) — the FSE RQ2 submission: `main.tex`, `refs.bib`,
  `NUMBERS.md`, `CLAIM_LADDER.md` (the four candidate theses and what fires each), `analysis/`
- [`../../paper_bidirectional/`](../../paper_bidirectional/) — the ATTRIB submission: `main.tex`, `refs.bib`,
  `NUMBERS.md` (per-claim provenance), `README.md` (build + what lands next)
- [`../../docs/ATTRIB_WORKSHOP_PLAN.md`](../../docs/ATTRIB_WORKSHOP_PLAN.md)
- [`../../docs/MASTER_REPORT_2026-08-11.md`](../../docs/MASTER_REPORT_2026-08-11.md)
- [`../../docs/RESULTS_BOOK_2026-08-11.md`](../../docs/RESULTS_BOOK_2026-08-11.md)
- [`../../docs/MASTER_REPORT_2026-08-10.md`](../../docs/MASTER_REPORT_2026-08-10.md)
- [`../../scripts/make_master_report.py`](../../scripts/make_master_report.py) → `results/analysis/master_report.json`
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
