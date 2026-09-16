# Master-table coverage

*Last updated: 2026-09-16 — computed by `scripts/analysis/70_coverage.py`, not written by hand.*

**The panel is complete.** All eight models carry every cell the master tables read, in both
directions: 184/184 forward and 161/161 backward each.

| codellama-7b | 184 | 161 | complete |
| codellama-13b | 184 | 161 | complete |
| codellama-34b | 184 | 161 | complete |
| llama31-8b | 184 | 161 | complete |
| starcoder2-15b | 184 | 161 | complete |
| gemma3-12b | 184 | 161 | complete |
| codegemma-7b | 184 | 161 | complete |
| granite31-8b | 184 | 161 | complete |

The last gaps closed on 2026-09-16 and were all mixture cells. Three faults had to be fixed to get
there, each recorded in `log/setup/`: a dataless expert bank on the meta device (which only the 34B
was large enough to trigger), token-budget batching plus an OOM retry in the mixture engine, and an
exec-pool timeout handler that could raise out of itself and kill a whole grid.

435 cells across the eight tables remain format-gated (failure rate above 0.25) and are excluded from
every mean. They are marked, not hidden: `$\dagger$` where the replies are unparseable and
`$\ddagger$` where they are predominantly the gold *forward* answer, which is a result rather than a
broken template.
