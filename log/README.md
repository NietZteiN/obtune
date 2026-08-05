# Research ledger — master index

*Last updated: 2026-08-04*

Protocol: [`../CLAUDE.md`](../CLAUDE.md) §6. One folder per research thread; one entry file per
working day per thread (`<thread>/YYYY-MM-DD_<slug>.md`), copied from [`TEMPLATE.md`](TEMPLATE.md).
**Entries are append-only** — corrections go into a new dated entry that references the old one.
Update both tables below on every new entry.

## By thread

| Thread | Purpose | Status | Entries |
|---|---|---|---|
| [`setup/`](setup/) | Scaffold, environment, data layer, obfuscation pipeline | active | 1 |
| [`pilot/`](pilot/) | Week-1 kill-switch pilot and its gate decision | done — gate passed; H1 gain shown to be task acquisition | 2 |
| [`transfer/`](transfer/) | RQ1 — per-condition adapters, transfer matrix, GLMMs | not started | 0 |
| [`modularity/`](modularity/) | RQ2 — router, merges, monolithic, oracle arms | not started | 0 |
| [`attention/`](attention/) | RQ3 — token classes, slicers, anchoring metrics, regression | not started | 0 |
| [`human-align/`](human-align/) | Secondary — Δρ vs human difficulty orderings | not started | 0 |
| [`holdout-final/`](holdout-final/) | The second and final H1 evaluation pass | not started | 0 |
| [`writeup/`](writeup/) | Figures, paper draft, artifact packaging | not started | 0 |

## Timeline

| Date | Thread | Entry | Headline |
|---|---|---|---|
| 2026-08-04 | setup | [`2026-08-04_scaffold-and-pipeline.md`](setup/2026-08-04_scaffold-and-pipeline.md) | Project created; contracts, obfuscation pipeline, training/eval stack built |
| 2026-08-05 | pilot | [`2026-08-05_kill-switch-pilot.md`](pilot/2026-08-05_kill-switch-pilot.md) | Kill-switch passed: L1b adapter +27.3 pts on held-out H1; L0 control is the next run |
| 2026-08-05 | pilot | [`2026-08-05_l0-control-refutes-invariance.md`](pilot/2026-08-05_l0-control-refutes-invariance.md) | L0 control reaches H1 as well as L1b training does — the H1 gain is task acquisition; Invariance Index redefined |
