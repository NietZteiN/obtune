# 2026-09-13 — obtune held three h200 jobs against an agreed share of two

**Thread:** setup · **Status:** fixed · **Related:** [`../../scripts/env.sh`](../../scripts/env.sh) `OBTUNE_H200_SHARE`, `scripts/slurm/submit.py::qos_pool`

The share with the sibling projects on this account is **two** concurrent jobs in the juno QOS pool.
`scripts/slurm/submit.py` enforces it and refuses past it. The checkpoint-select and merge jobs from
`scripts/merge/build_ready_merges.py` do **not** go through `submit.py` — they call `sbatch` directly —
so the partition choice I added to that script this morning had to count the share itself, and it
counted it wrong:

```python
q = squeue -h -u $USER -o "%q %Z"
held = sum(1 for l in q if l.startswith("juno ") ...)
```

`%q` is the **job's** QOS, which is `normal` for every job here; `QoS=juno` is a property of the
**partition** (`scontrol show partition`). The test therefore matched nothing, `held` was always 0,
and `gpu_partition()` always returned `h200`. Three obtune jobs were on h200 at once when
`submit.py` — counting correctly — refused a fourth and said so.

**Fix.** `gpu_partition()` now counts jobs whose **partition** is `h200` or `normal` (the pool
`qos_pool()` computes) and whose WorkDir is this project, the same ownership test `submit.py` uses.
With three held it now returns `h100`, as it should have all along.

**Nothing was cancelled.** The three running jobs are 10–30 minutes of work each and killing them to
come back under the cap would waste the compute without giving the neighbours their slot any sooner;
the count comes back to two as they finish, and no further h200 job is submitted until it does.

**The general fault** is that two places computed the same share and only one of them was the
authority. `submit.py::obtune_jobs_on` was already correct; the new code should have called it rather
than reimplementing it against a field that looked plausible. Worth remembering the next time a helper
needs to know the same thing the submitter knows.
