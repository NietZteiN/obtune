### Target Date: 2026-09-10 (the QOS every job has requested since the migration does not exist; HF cache moved to a 30 TB scratch allocation; twelve panel arms queued)
- **Hypotheses / what we're testing:** operational, not experimental. The task was "maximize GPU
  usage". What it turned into: finding out why obtune jobs wait for hours on a cluster with idle
  H200s.
- **Setup:** `sacctmgr show qos`, `scontrol show job`, and one control submission (`389017`).
- **Results:**
  - **`high-throughput` is not a QOS on this cluster.** `sacctmgr show qos` lists exactly: `normal`,
    `juno`, `hpcre`, `large`, `fio-bench`, `juno-dev`, `juno-pri`, `education`. `scripts/slurm/submit.py`
    had it as the **default** and `scripts/pipeline/plan.yaml` set it on all 47 stages, so **every
    obtune job since the juno migration has requested it.** Such jobs are accepted and then sit at
    `QOSMaxJobsPerUserLimit`.
  - **The control.** Job **389017**, an identical trivial job submitted with the account default,
    went from submit to RUNNING on `g-08-04` while five jobs holding the old default stayed pending
    behind it. After the change, zero of our pending jobs report a QOS reason; they report
    `(Priority)` and `(Resources)`, i.e. ordinary fair-share contention.
  - **The comment in the code asserted the opposite, in detail.** It described `high-throughput` as
    carrying `OverPartQOS` and `MaxJobsPU=8`, "so it overrides the partition cap and doubles the
    number of jobs we can hold", and explained why `large` and `juno-pri` were rejected in its
    favour. A confident, specific, checkable paragraph about a QOS that is not there.
  - **`CLAUDE.md` §1 is affected.** It records "queue waits are real, and they are the new planning
    constraint… `h200` had 41 running / 35 pending and estimated a 7-hour start for a 5-minute job"
    and the whole experiment plan was ordered around that. Some of that was the cluster; some was
    this flag. The charter should be corrected rather than left to mislead the next planner — **not
    done here**, because §1 is the human's document and the honest correction needs a measurement of
    the *residual* wait, which will come from the current batch.
- **What worked / hypothesis verdict:** n/a.
- **Observations:**
  - **Packing was the wrong reflex once the cap lifted.** `scripts/slurm/pack.py` runs two trainings
    in one `--gres=gpu:2` allocation and exists because the job cap, not the GPU count, was thought
    to bind. With the cap gone it is a liability: exactly **1 of 26** h200 nodes had both GPUs free,
    so four packs sat waiting for the scarcest resource on the cluster while single-GPU jobs slot
    into any of the twenty fragmented nodes. Four packs were cancelled and resubmitted as eight
    singles; utilisation rose immediately. `pack.py`'s docstring now says *when* it applies.
  - **A monitor that would have lied.** The utilisation watch counted `CANCELLED` as terminal, so
    cancelling those four packs would have made it announce "all training jobs terminal" with eight
    arms still queued. Re-armed against the real job set.
  - **Two of my own submissions were malformed and one was invisible.** The 34B recovery download
    asked for 3 h on `dev`, which caps at 2 h, and sat at `PartitionTimeLimit` where it would have
    waited forever. And an inline config validation before submitting three consistency arms silently
    did not run at all — bash expanded the Python format spec `{m:16s}` as a parameter expansion and
    errored — so three jobs were submitted against configs I had not actually checked. They were
    fine, but a check that prints nothing looks exactly like a check that passed.
  - **HF cache moved** to `/scratch/juno/$USER/hf_home` (§5c of `docs/MODEL_AND_DATA_SELECTION.md`):
    143.8 GB copied in ~7 min, every shard verified, both CodeLlama models a neighbour had deleted
    re-downloaded there at no `/work` cost. Scratch is a separate 30 TB quota and reads 11× faster.
    Only re-downloadable artifacts live there; the purge policy is unconfirmed.
- **New questions / new hypotheses:** none. One measurement worth taking before `CLAUDE.md` §1 is
  rewritten: the **residual** queue wait under the correct QOS, from this batch of thirteen arms.
- **Next Steps:** thirteen panel arms queued (`tuned_L0` / `tuned_X1` / `mono_all` / `cons_lam3` for
  gemma3-12b, codegemma-7b, starcoder2-15b, granite31-8b). Evals follow per model once ckpt-select
  lands. Human decisions still open: the final panel, and whether the two-part gate is adopted.
