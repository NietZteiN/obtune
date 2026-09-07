### Target Date: 2026-09-06 (Master report rev 15 — the final H1 read, X1, scale and the objectives campaign land in the living report)

> Continues [`2026-09-04_master-report-rev14.md`](2026-09-04_master-report-rev14.md). Rev 14 closed
> on 2026-09-04 with the H1 final pass unspent and the accuracy campaign at four levers; two working
> days later the pass is spent, three more levers are null, a held-out proxy exists, and one
> training objective beats the seed band. Rev 15 is where that lands.

- **Hypotheses / what we're testing:** organizational — no new experiment. Two documentation
  questions: (a) can the two days be *appended* (one new section, three corrections) without
  touching §1–§23, so that every earlier number keeps the provenance it was published with; and
  (b) can every stale statement left by the H1 spend be found and superseded in place rather than
  silently overwritten — the report is read by people who remember rev 14's "hold the final pass".
  Failure looks like a reader of §24 or §26 acting on advice the 09-05 read retired.

- **Setup:**
  - `MASTER_REPORT.md` 4,607 → 4,888 lines (+321 / −23). **§27 new** (seven subsections, 218
    lines); an *Added 6 Sep* block prepended to §1; §24's first bullet struck through and replaced,
    two bullets added; §25.1 recounted; §26's H1 paragraph given a *Superseded on 2026-09-05* block
    and its scale paragraph extended to 34B; front matter (scope counts, model-labelling sentence,
    grid sentence) and Contents updated; rev 15 Changelog entry. Backup of rev 14 kept in the
    session scratchpad only — the committed history is the archive.
  - **Corpus recount** by a scratch script over parquet *metadata* (`num_rows`, no column reads)
    → [`results/analysis/corpus_inventory_2026-09-06.json`](../../results/analysis/corpus_inventory_2026-09-06.json).
    `28_master_panel.py` was started first and **stopped**: it hard-codes its output to the
    tracked `master_panel_2026-09-04.json` and would have overwritten a dated artifact. The
    grouping rule is the same as that script's (`[quarantined] <dir>` for `_`-prefixed roots,
    else `phase/model/lang`), so the two inventories are comparable.
  - Every number in §27 is copied from a dated log entry that computed it from the parquets
    (2026-09-05 × 9, 2026-09-06 × 2) — none were re-derived here, and none were invented. One
    number I carried in working notes as a "span alignment" contrast (+1.38 [+0.19, +2.58]) could
    not be traced to any entry and was **dropped** rather than published.

- **Results:**
  - **Corpus:** **3,188 cells / 2,546,826 graded trials**, against rev 14's 2,966 / 2,200,119.
    The 222 new cells are all §27: `rq2_generic` 102 → 144 (7B) plus 18 each at 34B and Llama-3.1-8B,
    `objectives_generic` 56, `x1_generic` 56, `trace_generic` 18, `h1_codellama` 12 → 14 (7B) + 3
    (34B), `basecheck` +3 (34B) +6 (Llama). Rev 14's Qwen and quarantined counts reproduce exactly
    (1,515 / 227 / 608 / 28 / 45 cells; 554,064 side-grid trials), which is the check that the two
    counting methods agree.
  - **Panel:** CodeLlama-7b 699 cells / 1,063,102 trials; 13B 18 / 28,746; 34B 24 / 37,395;
    Llama-3.1-8B 24 / 38,328 — 765 / 1,167,571 for the post-migration era.
  - **Stale statements found and superseded:** §24 "the `final_eval` H1 pass is unspent, and the
    standing recommendation is to hold it" (struck through, pointer to §27.1); §26 "the H1 leader is
    `tuned_S2` 0.2834 … pick on other grounds" (superseded block: 34B `tuned_L0` 0.3213 leads, 7B
    `tuned_X1` ties it, and the band is beaten outright); §26 "13B … 2–4 points above every 7B
    system" (34B row added); the front matter's "§18–§25 are CodeLlama-7b" (now §18–§27, with
    34B/Llama named); "everything in §18–§23 is Grid A" (now §18–§27).

- **What worked / hypothesis verdict:** (a) held — the additive structure from rev 14 carried a
  second time; §1–§23 are byte-identical apart from the §1 addendum. (b) is where the work was:
  the H1 spend invalidates *advice* rather than numbers, and advice lives in prose, so the search
  was by hand over §24 and §26 rather than by grep. Superseding in place (strikethrough, a quoted
  "superseded" block) was chosen over deletion so that a reader who remembers the old
  recommendation sees why it changed — the same reasoning §21.3 applied to retired findings.

- **Observations:**
  - The changelog's rev numbers are not monotone (an 08-17 "rev 15" and an 08-27 "rev 17" predate
    09-04's "rev 14"); the live sequence is the one that resumed at rev 13 on 08-27. Left as is —
    renumbering history would be an alteration of an existing record.
  - §27.5's table is deliberately sparse: the four arms that were read on X1 and pooled only
    (`neg_*`, `x1_resample`, `curr_sft`) are shown with two cells so the table does not imply
    per-condition reads that were never tabulated in the entry.

- **Next steps:** when objectives round 2 (jobs 380166–380176) lands, §27.5 gains its seed band
  and λ column and §27.7 is folded into it — rev 16. `28_master_panel.py` should take an `--out`
  argument before it is run again.
