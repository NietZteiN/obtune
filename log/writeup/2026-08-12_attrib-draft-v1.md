### Target Date: 2026-08-12 (ATTRIB draft v1 written from results on disk)

- **Hypotheses / what we're testing:** Not an experiment day. The question was whether the
  ATTRIB submission can be written *now* from results already on disk, or whether it is
  blocked on the four queued runs. **Answer: not blocked.** Every claim the paper makes is
  supported by a completed run; the pending work either adds a figure or retires a
  limitation. The one thing this day tested is whether the reports agree with the result
  files — see Observations.

- **Setup:** No GPU. Repo at commit `469f857` (working tree dirty: modified configs and
  analysis artifacts from the 08-11 session, uncommitted). Numbers were extracted directly
  from result files, not from `MASTER_REPORT_2026-08-11.md` or `RESULTS_BOOK_2026-08-11.md`;
  the reports were used only as an index of where to look. Sources, one per claim, are
  tabulated in [`../../paper_bidirectional/NUMBERS.md`](../../paper_bidirectional/NUMBERS.md). Runs read:
  `results/2026-08-10_cft-bidirectional/qwen25c-7b/python/e2_budget_qwen7b/`,
  `.../qwen25c-1.5b/python/e2_factorial_qwen1.5b/`, `.../e1_qwen1.5b_s42/`,
  `results/2026-08-09_cft-bidirectional/qwen25c-1.5b/python/e1_qwen1.5b/`,
  `.../qwen25c-7b/python/bidir_qwen7b/`, `results/forgetting/humanevalplus_*.json`,
  `results/srh/budget_qwen7b_python.json`.

  Written: [`../../paper_bidirectional/main.tex`](../../paper_bidirectional/main.tex) (9 sections + 4 appendices, 5
  body tables), [`../../paper_bidirectional/refs.bib`](../../paper_bidirectional/refs.bib) (6 cited entries trimmed from
  `papers/references.bib`), [`../../paper_bidirectional/NUMBERS.md`](../../paper_bidirectional/NUMBERS.md),
  [`../../paper_bidirectional/README.md`](../../paper_bidirectional/README.md).

- **Results:** The draft's spine, all verified against the files above rather than the
  reports:
  - 2×2 at 1.5B (18 000 trials): data $+30.9$ pp $[+29.3,+32.6]$, objective $-0.2$
    $[-0.7,+0.3]$, interaction $-0.3$ $[-1.3,+0.7]$.
  - 7B budget (21 000 trials): `mix50` $-$ `sft` $= +32.8$ $[+31.3,+34.4]$; `flip` $-$
    `mix50` $= +0.7$ $[-0.3,+1.8]$; `fwd2x` $-$ `sft` $= +0.1$; `cft` $-$ `base` $= -12.8$
    $[-14.8,-10.9]$.
  - Measured budget: `mix50` 1.00× instances / 1.00× steps / 1.05× sequence tokens /
    **0.71× supervised tokens** vs forward-only; `cft` 2.65× sequence for 1.02× supervised.
  - Per-condition reverse (7B): `flip` .827/.797 on S1/S2 against .017/.013/.023 on the
    three renaming conditions — and `rev` is equally near zero there.
  - Seed 42 at 1.5B: max $|\Delta| = 0.7$ pp over `flip`/`rev`/`mix50`/`flipsym`.
  - HumanEval+ `plus`: 7B `sft` .817 ≥ base .805, `flip` .744, `mix50` .732.

- **What worked / hypothesis verdict:** SUPPORTED — the paper is writable today. Reading
  from result files rather than from the two summary reports was the right call and is what
  caught the discrepancies below. Structuring §2 to document CFT reimplementation fidelity
  *before* §5 reports the null keeps the desk-reject objection answered before it is raised.

- **Observations:**
  1. **Two `base` reverse numbers exist** — 12.9 % (`e2_budget_qwen7b`) and 13.0 %
     (`bidir_qwen7b`) — from different 300-program draws of the same split. Neither is
     wrong; mixing them inside one comparison would be. The draft quotes 12.9 % with the
     headline table and 13.0 % only inside the prompting appendix, which is wholly
     `bidir_qwen7b`.
  2. **The E8 table differs between the same two runs** (`base`/`L1r` paper criterion 19.0
     vs 19.7). `ATTRIB_WORKSHOP_PLAN.md` §1.4 quotes the `bidir_qwen7b` version; the draft
     uses `e2_budget_qwen7b` so that the E8 appendix and the headline table come from one
     run. Not an error in either document — a reason to state which run a table came from.
  3. **The planning document's budget ratios are superseded.** §1.1 there carries
     2.60×/1.52×/0.76× as estimates; the measured values from the tokenized corpus are
     2.65×/1.43×/0.71×. The draft uses the measured ones.
  4. **`fwd2x` is per-epoch identical to `fwd`** and differs only in epochs (6 vs 3), so its
     row in the budget table is 1.00× on everything except steps. Worth stating explicitly
     in-text, since a reader scanning the table would otherwise read it as "no extra
     compute".
  5. **No LaTeX toolchain on this host** — `pdflatex`/`xelatex`/`latexmk`/`tectonic` were all
     absent, and neither pandoc, wkhtmltopdf, weasyprint, a headless browser, nor any Python
     PDF library was present either. Installed `tectonic` 0.17.0 later the same day at
     `/data/jvl210002/conda_envs/tex` (one binary, fetches only the packages the document
     uses, runs bibtex and the reruns itself). **v1 now compiles: 8 pages.** Two things had
     to be fixed to get there: the `note`/`file` annotation fields carried over from
     `papers/references.bib` contain raw `_` and halt the engine while building `main.bbl`
     (stripped — must stay stripped on any re-extract), and `\label{app:seeds}` was
     unreferenced. The draft uses no class-specific macros, so dropping in the venue style
     is still a one-line change.
  7. **The body is over the page limit.** §1–§11 run to the top of p. 7 with references
     filling p. 7 and appendices A–D on p. 8, against a 3–6 pp main-text allowance — so
     ~0.3–0.5 pp too long. The trim order is recorded in `paper_bidirectional/README.md`;
     the first cut (§2's fidelity paragraph to an appendix, leaving a pointer) is worth most
     of it on its own.
  6. The queue is in a worse state than the 08-11 report implies: `queued=4 running=0
     failed=4`, all workers down, GPUs 0–1 still holding ~41 GB each at 0 % util. The four
     ATTRIB-relevant evals (`e3_dose`, `e2_seeds`, `e7_strategies`, plus one unlearning
     control) have not run.

- **New questions / new hypotheses:** None for the science. One for the writing: the draft
  currently has **no figure**. The dose ladder is the natural Fig. 1 and its adapters are
  already trained, so the cheapest thing that improves the paper is one eval pass, not a
  plotting decision.

- **Next Steps:**
  1. Bring the workers back up and drain `e3_dose_qwen1.5b` — it is the only pending run
     that *adds* to the paper rather than retiring a limitation.
  2. Re-queue `e7_strategies_qwen7b` (failed once) and `e2_seeds_qwen1.5b`.
  3. ~~Compile v1 and check the page count~~ — done the same day; 8 pages, body ~0.3–0.5 pp
     over. Apply the three trims listed in `paper_bidirectional/README.md` before v2.
  4. Fold the JS replication in behind the dose ladder if the GPUs free up before Aug 28.
