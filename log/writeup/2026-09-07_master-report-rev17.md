### Target Date: 2026-09-07 (Master report rev 17 — the paper-plan experiments get their own section, and a headline claim is narrowed in the document itself)

> Continues [`2026-09-07_master-report-rev16.md`](2026-09-07_master-report-rev16.md), the same day.
> Rev 16 closed the objectives campaign. Between rev 16 and here the campaign was re-organised
> around a specific paper ([`docs/PAPER_EXPERIMENTS.md`](../../docs/PAPER_EXPERIMENTS.md)) and its
> first three Tier-1 experiments ran — two confirming, one refuting.

- **Hypotheses / what we're testing:** organizational, with one editorial question that is not.
  Rev 16's own entry flagged that §27 was straining at seven subsections covering two campaigns, so
  the structural question was whether the paper-plan work belongs inside it. It does not: §27 is a
  dated narrative ("since rev 14") and the paper experiments are organised by *claim*, so they get
  §28. The question that matters more: **E5 refuted a hypothesis supporting C2, one of the paper's
  two headline claims.** A report that buries that in a subsection while §1 still asserts the
  unqualified claim would be actively misleading. Failure looks like §1 and §28 disagreeing.

- **Setup:**
  - `MASTER_REPORT.md` 5,008 → 5,145 lines. **§28 new** (three subsections): the plan and its
    Python-only scope decision, E1/E2, E5, and what is in flight. **§1's *Added 6 Sep* block
    amended** to narrow C2 where it is first stated. Front matter (scope counts, §18–§28 model
    range, grid sentence), Contents, §25.1 recount, rev 17 Changelog.
  - Numbers from the two dated transfer entries of 2026-09-07 and
    `results/analysis/{x1_scale_seedband,xy2_family}_2026-09-07.json`; corpus from a third
    parquet-metadata recount → `corpus_inventory_2026-09-07b.json` (dated output, per the rev-16
    lesson).

- **Results:**
  - **Corpus:** **3,258 cells / 2,650,457 trials** (rev 16: 3,237 / 2,622,398). The 21 new cells
    are §28's: 15 `xy2_generic`, 6 `x1_generic` across three model scales. 13B and 34B now have X1
    columns, which they never had before.
  - **C2 is narrowed in three places, not one.** §1 (where the claim is first made), §28.2 (where
    the evidence is), and `PAPER_EXPERIMENTS.md`'s claim table (which now reads "one family pair
    only; scope narrowed to *hard* families; E5b is the redo"). The wording everywhere is *for a
    family that badly damages a clean-code adapter*, which is what X1→H1 actually supports.
  - **The E5 null is reported with its cause and without an excuse.** §28.2 gives the refutation
    first and flatly ("REFUTED", rule not re-specified, +1.21 not called a trend), then the
    measured explanation: Y2 costs a clean-code adapter 3.8 pts against X1's 15.8, and in both
    pairs the specialist recovers ~a third of its family's damage, so ~1.2 pts of signal sat
    against a ±2-pt interval. The ratio table is the honest form of that argument — it shows the
    two pairs agree on the *mechanism* and differ on the *power*, which is a claim a reader can
    check, unlike "the family was too easy".

- **What worked / hypothesis verdict:** the three-place narrowing is the part I would defend. It is
  tempting to record a refutation only where the experiment lives, because §1 is the part people
  quote — which is exactly why §1 had to change. A reader who reads only the first page now sees
  "how far that generalises is a measured open question, not an assumption".

- **Observations:**
  - Rev 17 is the second revision in one day. The Changelog now carries three 2026-09-07 entries
    (16, 17 and rev 16's addendum); that is noisy but correct — each was a real state of the
    document, and collapsing them would erase the order in which claims were narrowed.
  - §28.3 deliberately names what is *not* done — E4, E6, E5b, and the still-absent multiplicity
    correction — inside the report rather than only in the plan, so the report cannot be read as
    claiming a complete campaign.

- **Next steps:** E3's two arms are still training (13B job 381340, 34B 381405, ~20–24 h for the
  latter). When they land, §28.3 becomes a result and §27.7's scale caveat resolves. E5b needs its
  generator and a difficulty gate measured before any adapter is trained.
