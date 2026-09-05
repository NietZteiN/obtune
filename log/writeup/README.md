# writeup — Figures, paper draft, artifact packaging

*Last updated: 2026-09-04*
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
- [`2026-09-04_master-report-rev14.md`](2026-09-04_master-report-rev14.md) — **rev 14**,
  [`../../MASTER_REPORT.md`](../../MASTER_REPORT.md). The report
  rebuilt **additively** on the CodeLlama panel: §1–§17 kept and labelled the frozen Qwen panel
  (those cells cannot be re-evaluated on this cluster, so a rewrite would have had to drop them or
  restate them without provenance), §17 retitled to name its panel, **§18–§25 new** — migration and
  model swap, the full replication, the H1 headline restored as "beats" with an interval, the three
  measurement defects, the accuracy campaign, and the weight-space invariance arm with its control.
  Corpus recounted at **2,966 cells / 2,200,119 trials**; the recompute agreed with every log entry —
  a first — and the only new fact it produced is the common-subset-vs-unrestricted gap, which moves
  one ordering (`merge_dare_ties` vs `tuned_L0`) inside its own interval.
- [`2026-08-27_master-report-rev13.md`](2026-08-27_master-report-rev13.md) — the 08-12 master report
  brought current as [`../../docs/MASTER_REPORT_2026-08-27.md`](../../docs/MASTER_REPORT_2026-08-27.md).
  §2.2's table **regenerated** — 154 systems in 169 rows, **one row per system per grid** (15 were
  sharing a row across two grids, which is how the RQ2 conclusion came to rest on 115 items), with a
  documented source preference for the 41 disagreeing duplicate cells. Verified to reproduce all 74
  old rows exactly. Three failed regenerations first — dropped `base`'s Grid B row, oldest-first
  tie-break, double-rounding. New §7.8, §12.12, §12.13, §15, §16; §1/§9/§10 rewritten; §12.4
  corrected in place.
- [`2026-08-27_rq2-master-report.md`](2026-08-27_rq2-master-report.md) — **RQ2 routing-and-merging
  closed** with [`../../docs/MASTER_REPORT_2026-08-27_router-and-merging.md`](../../docs/MASTER_REPORT_2026-08-27_router-and-merging.md),
  written from cells rather than from reports. Verdict reproduces to ≤0.02 pts. Three new findings:
  the eval stack is 2–15× noisier than recorded on the `tuned_L0` `H1` control (40.0 / 34.8 / 33.9
  across three passes, two of them identical in every recorded field); the **pooled** 1.32/3.61 seed
  band has been applied to Python-only contrasts in five documents and three script docstrings where
  the Python bar is 0.63/1.46; and the best merge density does not transfer to `H1`
- [`2026-08-18_attrib-reframe-directional-confound.md`](2026-08-18_attrib-reframe-directional-confound.md)
  — draft v4. The paper now argues for a confound class rather than against one paper; the CFT
  replication is the worked instance. §1's general test is the contribution and must not be cut
  for pages. No number changed.
- [`2026-08-17_attrib-reviewer-hardening.md`](2026-08-17_attrib-reviewer-hardening.md) — ATTRIB
  draft v3, no number changed. §4's header and scope caveat carry the defence of our CFT
  reconstruction in the body; abstract middle third tightened. **Build recipe is here** (tectonic,
  not pdflatex). The first compile in nine days showed the body has zero spare lines, which is why
  the §2 version of that defence was reverted.
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
