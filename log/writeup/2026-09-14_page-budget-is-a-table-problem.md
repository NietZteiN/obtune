# 2026-09-14 — The paper is 3 pages over and cutting prose cannot fix it

**Thread:** writeup · **Status:** measured, nothing changed · **Constraint:** 10 body pages + 2 for citations (user, 2026-09-13)

## Where it stands

| | pages |
|---|---|
| body | **1–13** |
| references | 14 |
| appendix | 15+ |

Three body pages over. The instinct is to cut the RQ sections again, and that was the instruction
given on 2026-09-13 ("shorten rq parts a lot"). **It was carried out and it cannot be repeated,
because there is almost nothing left to cut.**

## Live prose, tables and comments stripped

| section | words |
|---|---|
| `intro-2` | 1302 |
| `rq1` | 623 |
| `setup` | 578 |
| `rq3` | 442 |
| `abstract` | 306 |
| `intro` | 347 |
| `rq2` | 298 |
| `rqs` | 249 |
| `threats` | 209 |
| `master` | 151 |
| `related` | 86 |
| **total** | **4,591** |

At the ~1,050 words per page an ACM two-column body holds, **all the prose in the paper is about 4.4
pages of a 13-page body.** The three RQ sections together are 1,363 words — **1.3 pages**. Deleting
every word of RQ1, RQ2 and RQ3 would still leave the paper 1.7 pages over the limit, with no results
text at all.

## The measurement that settles it

Removing one table — `master_abs_codellama7b`, the 74-row full-width grid that is Section 4 — and
rebuilding moves the references from page 14 to **page 13**, i.e. the body loses a page. Restored
and rebuilt to confirm the paper returns to 35 pages and references to 14, so the measurement is
reversible and was reversed.

**One table is worth a page. All the prose in three results sections is worth 1.3.**

## What this means for the decision

The page budget is a **table** decision, not a prose decision, and the user has already said the
tables are the part they want kept ("keep the big tables I like those"). The options are therefore:

1. **Move `master_abs_codellama7b` to the appendix** and keep a small summary in the body — buys
   ~1 page, and the appendix already holds per-model versions of exactly this table.
2. **Move the Setup tables** — `setup_stacks` (17 rows) and `setup_taxonomy` (13 rows) are full-width
   and describe the design rather than the results; together roughly another page.
3. **Accept a shorter body by dropping a results section**, which is the framing decision, not a
   layout one.

Nothing is done. This is measured so the choice is between known costs rather than guesses, and so
that no more effort goes into shortening prose that is already 4.4 pages across thirteen.
