### Target Date: 2026-09-08 (Master report rev 18 — the pipeline campaign gets §29, and two headline claims are narrowed where they are first stated)

> Continues [`2026-09-07_master-report-rev17.md`](2026-09-07_master-report-rev17.md). Rev 17 added
> §28 (the paper plan and its first three experiments). Between rev 17 and here the entire remaining
> plan ran as one 47-stage SLURM graph and every stage was read.

- **Hypotheses / what we're testing:** editorial, with two questions that are not. (1) **Where does a
  47-stage campaign go?** §28 is organised by *paper claim* and its "in flight" paragraph is now
  false, but the campaign is organised by *revised RQ* — so it gets §29 and §28.3 is struck through
  rather than rewritten (entries and sections are append-only in spirit; a struck paragraph tells a
  reader that the plan changed, an edited one hides it). (2) **E4 narrowed a claim that §1 states
  unqualified.** §27.5's "paired consistency keeps breadth's gain and pays neither tax" is still
  true, but the *mechanism* sentence around it — that the objective teaches invariance — is not what
  the teacher-variation experiment supports. A report whose §1 says "the objective works" while §29
  says "it distils a teacher" is the failure mode rev 17 already had to fix once for C2.
- **Setup:** `MASTER_REPORT.md` 5,176 → 5,522 lines.
  - **§29 new**, six subsections: 29.1 RQ1′ (composites at three scales and depth 3/4, saturation,
    the L0-cost classification and stratification), 29.2 RQ2′ (the X1 split), 29.3 RQ3′ (E3 scale,
    E8 Llama, the 34B composites, E4 teacher), 29.4 the two negative stress tests (RQ5′ inverse task,
    RQ4′ inert knockout), 29.5 multiplicity (both FDR passes), 29.6 what the campaign changed.
  - **§1 gains an *Added 8 Sep* block** stating the two narrowings, the two strengthenings and the
    two negative stress tests — where the claims are first made, not only where the evidence sits.
  - **§28.3's "still unrun" paragraph struck through and superseded**; Contents, front-matter scope
    counts and the Changelog updated.
  - Numbers from the eight dated transfer entries of 2026-09-08 and
    `results/analysis/pipeline/*.json`; corpus recounted from parquet metadata →
    `results/analysis/corpus_inventory_2026-09-08.json` (dated output, per the rev-16 lesson).
- **Results:**
  - **Corpus:** **3,564 cells / 3,104,044 trials** (rev 17: 3,258 / 2,650,457). The CodeLlama/Llama
    panel grew from 835 cells to **1,141** (7B 993, 13B 45, 34B 51, Llama-3.1-8B 52) — the campaign
    added 306 cells, more than a third of the panel that existed before it.
  - **Two claims narrowed in two places each.** RQ3′ (§1 and §29.3): *teacher distillation*, not
    learned invariance. RQ2′ (§1 and §29.2): shared **surface**, not shared mechanism. Both wordings
    are the one the measurement supports and neither is softened elsewhere in the document.
  - **RQ4′ loses its causal leg in §1, §29.4 and §29.6.** The identifier knockout moves gold log-prob
    by < 0.5 % for every arm on every condition, so the instrument is inert; the correlational
    support stays and is labelled as correlational. This is the third time a mechanism claim in this
    project has had to be walked back to a correlation, and §29.6 says so rather than burying it.
  - **A measurement statement that changes how earlier numbers read:** every "no L0 tax" in the
    report now means "no *detectable* cost at n = 557". E11 showed a ±1.0 TOST margin is unreachable
    for any genuinely different arm at this cell size — 38 of 60 arms land "underpowered". Nothing
    about the point estimates changed; the certification language did.
  - **Nine refutations are collected in §29.6**, deliberately, with the sentence a reader needs:
    that is the number to quote when the report is accused of finding only what it looked for.
- **What worked / hypothesis verdict:** the part I would defend is §29.6 existing at all. Each
  refutation is already reported in its own subsection; gathering them in one place at the end of the
  section is what stops a 5,500-line document from letting a reader take the confirmations and skip
  the rest. The part I am least sure of is §29's length — it is the longest section added in one
  revision, and a future revision may need to fold §28 and §29 together once the paper's structure is
  fixed rather than the campaign's.
- **Next:** the paper draft itself. Every RQ row in `docs/RQ_SUMMARY.md` §6 now has an answer and an
  empty open column except RQ4′'s two documented gaps (the `mono_all`-controlled FDR family, E11b's
  format/difficulty confound) and E5b/E10, both blocked on things that do not exist yet.
