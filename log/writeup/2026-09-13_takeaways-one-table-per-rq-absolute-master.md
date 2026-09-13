# 2026-09-13 — Takeaway boxes, one table per RQ, and an absolute master table at the top

**Thread:** writeup · **Status:** done, rebuilt · **Related:** [`2026-09-13_shortened-to-the-page-limit.md`](2026-09-13_shortened-to-the-page-limit.md)

User: *"Each rq add a takeaway box. Also one table per rq. I don't like this relative reporting I just
want a master table at the top showing all methods all obfuscations and the values for a model."*

- **Absolute master table.** `59_master_tables.py` now also writes `tables/master_abs_codellama7b.tex`
  (and a markdown twin, §6 of `docs/MASTER_TABLES.md`): raw exact-match accuracy of eight methods —
  untuned, ICL, clean LoRA, breadth, anchored, family, mixture (learned-gate MoLE), DARE-TIES merge —
  on all 23 conditions and stacks, plus the backward ladder, for CodeLlama-7B, the one model with every
  arm. No deltas, no percentages; a dagger marks a format-gated cell instead of hiding it. The section
  "Every method against every obfuscation" moves from after RQ4 to before RQ1 and its prose is
  rewritten to describe absolute values only.
- **One table per RQ in the body.** RQ1 keeps the dissociation table; RQ4 keeps the ladder. The
  composition, panel-merging, direction-ratio and by-model tables, and the relative cross-model
  summary, move to a new Appendix C (supplementary tables); every reference in the prose now says so.
  No table was deleted or edited.
- **Takeaway boxes** (`tcolorbox`, defined once in the preamble as `takeaway`) close each RQ. They
  restate the claims as the section states them, so the story is unchanged — including RQ1's verdict on
  routing and merging, which the tables in Appendix C contradict; the pending-decision comment stands.
- Build: 28 pages in acmsmall review; sigconf check reported in the commit.
