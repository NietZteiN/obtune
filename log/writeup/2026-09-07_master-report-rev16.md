### Target Date: 2026-09-07 (Master report rev 16 — round 2 turns §27.7 from a pre-registration into a result, and retires three cautions)

> Continues [`2026-09-06_master-report-rev15.md`](2026-09-06_master-report-rev15.md). Rev 15 was
> written while objectives round 2 was still on the queue, so it published §27.5 with a "single
> seed" caveat and §27.7 as a list of frozen decision rules. Both landed on 09-07; rev 16 is where
> that lands in the document.

- **Hypotheses / what we're testing:** organizational. The specific risk this revision carries is
  different from rev 15's. Rev 15 had to *supersede advice* (a recommendation the H1 spend
  retired). Rev 16 has to *retire cautions* — three statements that were correct when written and
  are now either resolved or wrong ("this is one seed", "λ was read at two values only", "the
  `mono_all` s42/s101 rows wait on `final_eval`"). Retiring a caution is the more dangerous edit,
  because deleting one silently makes a claim stronger than the evidence that was there before.
  Failure looks like a strengthened claim with no visible reason for the strengthening.

- **Setup:**
  - `MASTER_REPORT.md` 4,888 → 5,008 lines (+144 / −41). **§27.7 rewritten end to end** from the
    pre-registration into the read: accuracy table for the five new arms plus the two seed-matched
    controls, a verdict table for the three hypotheses, three reading paragraphs (what round 2
    settles / corrects / qualifies) and the format-gate defect. **§27.5** — closing caution
    replaced with a pointer to §27.7 and an explicit note that one of its sentences is now
    qualified. **§24** — the "round 2 is in flight" bullet struck and replaced; **H-format-gate**
    added as an open item for the human. **§25.1** — recounted. **§26** — best 7B system on the
    seven-condition set updated. **§20** — a caveat struck (below). **§1** and the front-matter
    preface — the "single seed, seed band in flight" clauses updated. Contents, dateline and a rev
    16 Changelog entry.
  - Numbers from [`log/transfer/2026-09-07_objectives-round2.md`](../transfer/2026-09-07_objectives-round2.md)
    and `results/analysis/objectives_2026-09-07.json`; corpus from a re-run of the rev-15
    parquet-metadata script → `results/analysis/corpus_inventory_2026-09-07.json`. (The first
    run of that script overwrote the tracked 09-06 inventory, because I had hard-coded its output
    filename on 09-06 — the third instance of this defect in three days, after
    `28_master_panel.py` and `34_objectives.py --out`. Restored with `git checkout` and re-run to a
    correctly dated file. Every analysis script in `scripts/analysis/` that writes a dated artifact
    should take a required `--out`.)

- **Results:**
  - **Corpus:** **3,237 cells / 2,622,398 trials** (rev 15: 3,188 / 2,546,826). The 49 new cells
    are round 2's; the CodeLlama-7b panel is now 748 / 1,138,674 and `objectives_generic` is the
    second-largest phase in the project at 105 cells.
  - **Three cautions retired, each with its replacement stated rather than just deleted.**
    (1) §27.5 "this is one seed" → the gain holds at three seeds, spread 0.91 pts, and the sentence
    now says so and links §27.7. (2) §27.5 "λ was read at two values only" → λ = 3 is a plateau and
    λ = 10 is reliably worse; the caution is replaced by the finding, not removed. (3) §20 "the
    `mono_all` s42/s101 rows wait on `final_eval`" → **struck through**, because those rows will
    never exist: the budget was spent on a five-arm manifest that did not include them, so the H1
    column has no seed replicate and can never acquire one. That third one is the edit I was most
    careful with — the honest replacement is not silence but "this can no longer be checked, and
    here is the substitute (X1 at three seeds) and the independent 34B replication".
  - **One sentence of rev 15 is now wrong and is marked as qualified rather than rewritten.**
    §27.5 concluded "the KL term, not the order, is what works … worth ~1.3 pts from either start".
    Round 2 shows that holds on trained conditions only: starting from `mono_all` is free on the
    grid (+0.14 [−0.84, +1.04]) and costs −2.47 [−4.12, −0.91] on X1. §27.5 keeps its original
    sentence with a pointer, and §27.7 carries the correction — per §21.3's convention that a
    superseded claim stays visible.
  - **The format-gate defect is published in the report, not only in the lab log.** It appears in
    §27.7 with the full list of what a literal reading would void (the `tuned_L0` control on 7/7
    conditions, `base`, `formatonly`, six already-published §27.5 cells) and the sensitivity table
    showing all five decisive contrasts unchanged on the format-clean subset, and again in §24 as
    an open item. It is **not** re-specified.

- **What worked / hypothesis verdict:** the strikethrough-plus-replacement device carried all
  three retirements, and it is the right one: a reader diffing rev 15 against rev 16 sees the old
  text, the reason it went, and what stands in its place. The one thing I would do differently is
  structural — §27 is now seven subsections and ~300 lines covering three days and two campaigns,
  and §27.7 in particular is a full experiment report living inside a "since rev 14" section. At
  the next revision §27.5+§27.7 should probably be promoted to their own numbered section for the
  objectives campaign, leaving §27 as the H1/X1/scale narrative.

- **Observations:**
  - Publishing a defect in my own pre-registration inside the master report (rather than only the
    log entry) was a deliberate call. The alternative — log it and keep the report clean — would
    leave §27.5's numbers in the report with no visible trace that a gate written to guard them was
    unusable. A reader who later finds the gate in the scratchpad should find it in the report too.
  - Rev 16 touches §20, which is CodeLlama-era but pre-dates §27 by four days; that is the first
    time a revision has had to reach back past the section it was writing. The trigger was the H1
    spend, not round 2 — it was simply missed in rev 15.

- **Next steps:** unchanged from the transfer thread — **H-cons-scale** (13B/34B) and
  **H-cons-teacher** are open and unscheduled, and **H-format-gate** needs a human decision. If
  either consistency hypothesis runs, §27.5/§27.7 should be promoted to their own section first.
