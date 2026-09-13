# 2026-09-13 — Prose shortened for the 10+2 page limit; Setup made one section; tables untouched

**Thread:** writeup · **Status:** done, rebuilt · **Related:** [`2026-09-13_tables-updated-story-held.md`](2026-09-13_tables-updated-story-held.md)

User: *"10 page limit and 2 for citation so shorten rq parts a lot (though keep the big tables I like
those don't touch tables just prose and arguments not all of these subsections). Setup should be one
section with subsections."*

## What changed

- **Setup is one section with six subsections**: research questions and the two tests (absorbing the
  former standalone "Research Questions" section and the empty "Background"), Models, Dataset,
  Obfuscation taxonomy, Systems (every arm defined once, including the anchored objective by reference
  to the intro's Eq.~1, which RQ3 no longer repeats), Measurement (grading, pairing, bootstrap, format
  gate, pre-registration).
- **RQ1–RQ4 have no subsections.** Each is the claims as they stood, in the order they stood, with the
  same numbers, around the same tables; the argumentative connective tissue, restatements and
  "what this does not mean" passages are cut. RQ1 851 → 470 words, RQ2 558 → 330, RQ3 567 → 310,
  RQ4 744 → 420, master 318 → 170, threats 524 → 250 (paragraphs merged into one block).
- **No table was touched**; every `\input{tables/...}` and every label is where it was. The
  merging-framing comment in RQ1 is kept verbatim, and the story is unchanged: RQ1 still says
  "merging does not compose at all" above Table 6.
- The intro (the user's, 1,421 words), abstract and related work are untouched.
- Originals preserved in `paper/router_merger/sections_pre_shorten_2026-09-13/`.

## Length

Prose outside the intro: ~4,500 → 2,727 words. The draft is `acmsmall,review` (single column with
line numbers), where the body is now 15 pages; that format is not the one the limit is written for.
A `sigconf` (two-column) build of the same source in the scratch directory is the honest measure and
is reported in the commit and to the user. The nine body tables and the four setup tables are the
bulk of the remaining length; the appendix (eleven per-model grids) is outside the body.
