# Generated results tables

Regenerate with:

```
python scripts/paper/gen_fse_tables.py
```

**No number in these files is typed by hand.** Each is computed from a JSON under
`results/analysis/`, which comes from the per-cell parquets in `results/cells/`. The header of
every `.tex` names its source, so a number traces back to a cell in two hops. Style matches the
hand-written tables already in `sections/`: caption above the tabular, `@{}`-trimmed column specs,
booktabs rules, `\texttt{}` for system names, signed numbers in math mode.

## Where each one goes

| file | section | `\input` line |
|---|---|---|
| `rq1_dissociation.tex` | RQ1, after the composition-strategies table | `\input{tables/rq1_dissociation}` |
| `rq2_identifier.tex` | RQ2, after the "identifier recognition" paragraph | `\input{tables/rq2_identifier}` |
| `rq3_panel.tex` | RQ3, after the objective is introduced | `\input{tables/rq3_panel}` |
| `rq4_ladder.tex` | RQ4, replacing or preceding the stress-test table | `\input{tables/rq4_ladder}` |
| `rq4_by_model.tex` | RQ4, after the ladder | `\input{tables/rq4_by_model}` |

All five are `table*` (full width) because the intervals do not fit one column.

## What they supersede in the current prose

These are not additions to numbers that already stand; several of the draft's figures predate the
eight-model panel and should be updated with them.

- **RQ1** says breadth gains *"+3.49, +2.90, and +3.05 points across three model scales"*. That is
  now **six models across four lineages**, and the claim is stronger stated as a **paired
  difference** — one interval being positive while another is negative is not a test of the
  difference between them, and on four of the six the unseen-side interval straddles zero alone.
  The difference is significant on **6 of 6**.
- **RQ2** says the gain drops *"from +6.6 for identifier-heavy stacks down to +1.1 for
  structural-only"*. That is an ordering, not a contrast. The measured difference is **+3.39** on
  seen stacks and **+5.85** out of sample, on a rule fixed before the out-of-sample stimulus existed.
- **RQ3** says the objective *"completely removes breadth's unseen-family costs"* and incurs *"no
  clean-code penalty"*. Across eight models the repair holds on **6 of 8 and reverses on one**
  (Granite), and the no-clean-cost half holds on **5 of 8**. Both claims need the qualifier.
- **RQ4**'s stress-test table has no row for stacks containing an unseen family, because that
  stimulus did not exist when it was written. It does now, and it is the experiment RQ4 turns on.

## One thing the tables make visible

`rq1_dissociation.tex` and `rq4_by_model.tex` together carry the paper's sharpest result:
**Granite's dissociation is +3.91 and significant while its anchoring advantage is negative.** RQ1's
finding survives on a model where RQ3's does not, which is why the panel should keep that model
rather than drop it for a cleaner table.
