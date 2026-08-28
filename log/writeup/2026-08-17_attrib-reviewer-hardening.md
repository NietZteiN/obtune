### Target Date: 2026-08-17 (ATTRIB draft v3 — hardening against the one review that could sink it)

- **Hypotheses / what we're testing:** Not an experiment day, and no number changed. A read of
  draft v2 identified the submission's single largest review risk and two smaller ones. The
  question was where in the manuscript the defence has to live for a triaging workshop reviewer
  to encounter it. **The page limit answered it, not editorial preference** — see Observations.
  Companion entry for the same day, results side:
  [`../cft-replication/2026-08-17_attrib-v2-and-determinism.md`](../cft-replication/2026-08-17_attrib-v2-and-determinism.md).

- **Setup:** No GPU. Edits confined to
  [`../../paper_bidirectional/main.tex`](../../paper_bidirectional/main.tex).

  **Build.** Tectonic 0.17.0 from `/data/jvl210002/conda_envs/tex/bin/`, with
  `XDG_CACHE_HOME=/data/jvl210002/.cache` and `TMPDIR=/data/jvl210002/tmp_pip`. Clean compile:
  0 errors, 0 undefined references, 0 undefined citations, no overfull hboxes.

  > **A wrong turn worth recording, because it cost an unnecessary install.** I concluded the host
  > had no LaTeX and installed conda-forge `texlive-core` into the `tex` env. **Both premises were
  > wrong.** The toolchain was already there and already documented in
  > [`../../paper_bidirectional/README.md`](../../paper_bidirectional/README.md) §Building —
  > tectonic has been in that env since 2026-07-26. I missed it twice over: `tectonic` is not on
  > `$PATH`, so `command -v` found nothing, and I listed the env's `bin/` with `head -40`, which
  > truncates alphabetically just before `t`. **Read the directory's README before concluding its
  > tooling is absent.**
  >
  > The `texlive-core` I added is useless here and should probably come back out (it is ~200 MB in
  > a shared env, so it is left in place pending approval per `../../CLAUDE.md` §2). For the record
  > if anyone reaches for it later: conda-forge's current `texlive-core` ships **binaries only** —
  > `texmf-dist/tex/latex/` is empty, no `.sty` files at all — and its bundled `tlmgr` is broken
  > (`Can't locate TeXLive/TLConfig.pm`). `pdflatex` from that package cannot build this paper.
  > Tectonic is the right tool and the README already said so.

- **The risk, stated plainly.** Our `cft` arm realises the contrastive objective as joint
  next-token cross-entropy over the three instance pools. That is a *reconstruction* of an
  underspecified method, and it was defended only in Appendix A. A reviewer who reads the
  abstract's "the objective accounts for none of the recovery", then discovers in the appendix
  that the objective is ours, can object that the null is a null on our realisation rather than
  on contrastive learning.

- **Results — three edits kept:**
  1. **§4 header softened** — "…the published method does not reproduce" → "…**does not
     reproduce in our setting**". Free; removes a flat claim the section's own last paragraph
     already qualified.
  2. **§4 closing paragraph rewritten.** The scope caveat now names *both* limits (Python and
     smaller corpus; **reconstructed objective**, pointing at App. A) and says this is a failure
     to reproduce in our setting rather than a verdict on contrastive training. Added the
     load-bearing sentence: the positive result rests on neither, since `mix50` and `flip` are
     ordinary supervised fine-tuning. **This is where the defence ended up living in the body** —
     one clause rather than a paragraph, and in §4 rather than §2.
  3. **Abstract middle third tightened** — five sentences to four, ~105 words to ~85, attribution
     stated before the intervals ("a 2×2 that separates the two … attributes the whole recovery
     to the data"). Both limits and the generalisation sentence kept verbatim; no claim weakened.

- **Written and then reverted:** a §2 paragraph, "The published objective, and how we realise it",
  lifting two sentences of App. A (three instance pools with counts, never InfoNCE / margin /
  cosine / embedding; two of three headline CFT results come from provider APIs that cannot
  express an embedding-space loss) up to first use of `cft`. **Reverted on the page limit.**

- **Observations:**
  - **The body had zero slack.** Pre-edit, `References` began on the *last line* of p6. The §2
    paragraph cost ~8 lines even after compression and pushed the body onto p7, against a 3–6 pp
    allowance.
  - **Two stale page-count claims corrected, both in the same direction.**
    `docs/ATTRIB_CHECKLIST_2026-08-17.md` §6a says the body is "~1 pp still over" at 7.0 pp, and
    `paper_bidirectional/README.md` said v2 compiles to 10 pages with the body running to p7.
    Measured: the committed 10:48 PDF was **12 pages with the body ending on p6**, i.e. already
    compliant. Both documents predate the trims that closed the gap and neither was re-measured.
    The README is fixed; the checklist still needs it.
  - **A third README claim is contradicted by the file.** Its applied-cuts list says §2's
    arm-definition table was "inlined as prose". It was not — `tab:arms` is still in §2. Which is
    lucky, since the measurement below shows moving it is the cheapest page available.
  - Measured two ways to buy the page back, since guessing was what caused this. **Moving Table 1
    (arms) to the appendix works** (References returns to p6, defence intact). **Footnoting the
    defence on the `cft` table row does not** (~5 lines at footnote size, still lands on p7).
  - The author chose to revert §2 and keep Table 1. Defensible: the §4 clause carries the
    qualification in the body, and Table 1 is the reader's only map of eight arm names used
    across §3–§5.
  - Final layout is *better* than pre-edit, not merely compliant. The body now fills a full 6 pp
    and References starts clean at the top of p7; before, the bibliography began mid-p6. 13 pp
    total (6 body + refs + appendices A–J); appendices do not count.

- **Next steps:**
  - Rewrite `ATTRIB_CHECKLIST_2026-08-17.md` §6a. It sends the next reader hunting for a page
    that is not missing.
  - Any future body addition must be compiled before it is believed. There are ~0 spare lines.
  - Unchanged: item 9 (venue style, anonymisation, checklist).
