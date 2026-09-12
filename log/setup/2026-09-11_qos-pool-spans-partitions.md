### Target Date: 2026-09-11 (the 4-job cap is a QOS pool spanning `h200` AND `normal`, not a per-partition h200 limit)
- **Corrects** the operating assumption behind
  [`2026-09-10_h200-share-guard.md`](2026-09-10_h200-share-guard.md) and the `share_limits` block
  in `configs/compute.yaml`, both of which treat the cap as belonging to `h200`. Per CLAUDE.md §6
  those entries stand unaltered; this one carries the corrected picture.
- **What happened.** Six CPU jobs were submitted to `normal` on the reasoning that CPU analysis is
  free while the GPU partitions are saturated — the F2 composite build and three task-vector
  geometry runs. Within a minute SLURM reported **`QOSMaxJobsPerUserLimit`** on
  `tr_codellama-13b_X1`, the h200 training job the eight-model panel grid depends on, and on the
  neighbour's `nla_lsweep`.
- **The fact.**

  | partition | `QoS=` | pool | cap |
  |---|---|---|---|
  | `h200` | `juno` | **shared with `normal`** | MaxJobsPU=4 |
  | `normal` | `juno` | **shared with `h200`** | MaxJobsPU=4 |
  | `dev` | `juno-dev` | its own | MaxJobsPU=1, 2 h walltime |
  | `h100`, `a30` | none | uncapped | — |

  So the four slots are ONE budget covering a GPU partition and the CPU partition. A CPU analysis
  job blocks a GPU training job, and **moving work from `h200` to `normal` frees nothing** — which
  is exactly the remedy the old wording invites.
- **Why it went unnoticed.** `submit.py::obtune_jobs_on` counted jobs *on the named partition*. With
  two obtune jobs on `h200` and two on `normal` it reported **2 of 2 on h200, 0 of no-limit on
  normal** — both readings green — while the pool was full. The guard was not wrong about its own
  arithmetic; it was measuring the wrong set.
- **Fixes.**
  1. New `submit.py::qos_pool(partition)` reads `scontrol show partition`, groups partitions by
     their `QoS=`, and `obtune_jobs_on` now counts the whole group. A partition with no QOS returns
     itself, so `h100`/`a30` stay uncapped exactly as before.
  2. A job PENDING on an unmet **dependency** is no longer counted. It cannot start, so it is not
     contesting the neighbour's slot; counting it made the guard refuse everything the moment three
     chained analyses were queued — a false positive whose remedy (submit to `normal`) is the very
     move that does not help. Every other pending reason still counts: `Priority`, `Resources` and
     `QOSMaxJobsPerUserLimit` all mean "ready, waiting for a slot".
  3. The refusal message now names the pool and its partitions and says outright that moving to
     `normal` does not free a slot.
  4. `configs/compute.yaml` and `scripts/env.sh` rewritten to describe a pool.
- **Immediate action taken.** The two queued geometry jobs were cancelled and resubmitted to `dev`
  (`juno-dev`, a genuinely separate pool, and the jobs are ~1 h against its 2 h limit), which
  returned the slot to `tr_codellama-13b_X1`.
- **Observation worth keeping.** `dev` is the only free lunch on this account: one short CPU job at
  a time, on its own QOS. Long CPU builds still have to be paid for out of the same four slots as
  the GPU work, so "run the analysis while the GPUs are busy" is not free and should be scheduled,
  not assumed.
- **Next Steps:** none blocking. The monitor's idle-share alarm reads `h200` only and should be
  widened to the pool the next time it is touched.
