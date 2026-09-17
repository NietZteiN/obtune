# Retired sections

Not `\input` by `fse27.tex`, kept rather than deleted.

- `master.tex` — was Appendix A alone. Superseded 2026-09-17 by `../master_tables.tex`, which holds
  every appendix table in one file. Its content is there verbatim; this copy is the pre-merge state.
- `rq1.tex`, `rq2.tex`, `rq3.tex`, `rqs.tex` — the research-question structure, retired 2026-09-15
  when the paper was rebuilt around one results table. Their numbers are **superseded, not wrong**;
  several predate the backward v2 re-grade and the two-prompt repair, so do not quote them.
- `intro.tex` — an earlier introduction; `intro-2.tex` is the live one.
- `background.tex` — empty, never used.

Moved here because `scripts/paper/inline_tables.py` globs `sections/*.tex` and was refreshing
generated blocks inside dead files on every run.
