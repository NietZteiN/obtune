# What is in `failed/`, and which entries are real

`pipeline.sh`'s completion summary prints a count from this directory and says to inspect it
before trusting any table that depends on those jobs. That is the right default — but neither
entry currently here is a code failure, and both are kept rather than deleted so the record of
why stays auditable.

| file | date | real failure? | what actually happened |
|---|---|---|---|
| `015_evalksweep__qwen25c-1.5b_python.json` | 2026-08-13 | **no** | A duplicate claim killed by hand while the k-sweep was mid-flight. The surviving process ran to completion — its log ends with `n_cells: 56`. The k-sweep results are in `results/cells/baselines/` and are the source of §11 Table 39. |
| `080_gridArefill__qwen25c-1.5b.json` | 2026-08-14 | **no** | Killed deliberately during the pipeline-hardening audit. The job was not failing, it was *spinning*: `pick_demos` re-loaded and pydantic-validated the whole ~31k-row training pool once per evaluation item, so a Grid A ICL cell took ~14 minutes at 98 % CPU and 0 % GPU. It was killed so it would restart against the fixed (cached) demo pool — see `log/setup/2026-08-14_pipeline-hardening.md`. The job re-ran and completed; the Grid A panel is in `results/cells/baselines_gridA/`. |

**How to tell a real failure from these.** A real one leaves a traceback in
`runs/logs/worker_gpu*.log` at the matching timestamp and has no successor job that completed the
same work. Both entries above have a successor that did.

Neither file is deleted, because deleting them would erase the evidence that a human intervened —
which is the thing a reader of `failed/` most needs to know.
