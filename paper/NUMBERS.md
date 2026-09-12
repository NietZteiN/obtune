# Where every number in `main.tex` comes from

*Last updated: 2026-09-12*

**No number is typed into a `.tex` by hand.** Every table under `tables/` is emitted by
[`../scripts/paper/gen_tables.py`](../scripts/paper/gen_tables.py) from a JSON under
`results/analysis/`, which is itself computed from the per-cell parquets in `results/cells/`.
`MASTER_REPORT.md` and `docs/` are an **index of where to look, not a source**; where a report and a
result file disagree, **the file wins** and the discrepancy is recorded here.

Regenerate everything with:

```
python scripts/paper/gen_tables.py
```

| table | file | generated from | analysis script |
|---|---|---|---|
| `tab:grid` | `grid_agreement.tex` | `pipeline/grid_agreement_panel_core.json` | `analysis/55_grid_agreement.py` |
| `tab:panel` | `panel_replication.tex` | `panel_replication_final.json` | `analysis/51_panel_replication.py` |
| `tab:ladder` | `divergence_ladder.tex` | `pipeline/f2_divergence_codellama7b.json`, `pipeline/composite_depth_codellama7b.json` | `analysis/53_f2_divergence.py`, `analysis/35_composites.py` |
| `tab:split` | `identifier_split.tex` | `pipeline/f2_divergence_codellama7b.json`, `pipeline/f3a_stack_identifier_*.json` | `analysis/53_f2_divergence.py`, `analysis/52_f3a_stack_identifier.py` |
| `tab:divmodels` | `divergence_by_model.tex` | `pipeline/f2_divergence{,_core}_*.json` | `analysis/53_f2_divergence.py` |
| `tab:geom` | `geometry.tex` | `f1b/geometry_codellama7b_*.json` | `merge/20_geometry_report.py` |

## Draft state

`\pending` marks a result that does not exist yet and **is never replaced with a plausible value**;
`\slot` marks a claim the argument needs and has not earned. The submission checklist is that both
reach zero:

```
grep -c 'slot{' paper/main.tex
grep -ho 'pending' paper/main.tex paper/tables/*.tex | wc -l
```

Currently **8 claim slots** and **2 tables carrying `\pending`** — the two divergence reads still
evaluating (CodeLlama-34B, Llama-3.1-8B) and the clean-code contrasts at level d0, which the
seen-composite run did not compute.

## Two macro names that matter

`\vok` / `\vrefuted` / `\vinc` carry the verdict marks. They are **not** `\ok` / `\ref` / `\inc`:
`\ref` is LaTeX's own cross-reference command, and defining a verdict macro over it makes every
`\ref{tab:...}` in the prose render as a superscript instead of a table number. The first draft did
exactly that and it was caught by structural validation, not by a compiler — there is no LaTeX
toolchain on this host.

## What the paper must not claim

Enforced by review against [`../docs/PAPER_DRAFT.md`](../docs/PAPER_DRAFT.md) §12, and repeated in
`main.tex`'s header:

1. **that merging fails through task-vector interference** — refuted on two lineages (`tab:geom`);
2. **that anchoring pays no clean-code cost** — 5 of 8 models (`tab:panel`);
3. **anything causal about model lineage** — $n=8$, Fisher $p=0.0714$ at best, and vendor is
   confounded with lineage;
4. **that what transfers within a family is its surface scaffolding** — the discriminating test
   returned undecided on all three of its pre-registered rules;
5. **"failures worsen with divergence"** as a level effect — the pooled interval spans zero; the
   significant version is the identifier-versus-structural split.
