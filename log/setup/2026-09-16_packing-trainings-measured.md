# 2026-09-16 — Packing trainings into one allocation works, but two per GPU is slower than one

**Thread:** setup · **Why:** the juno QoS caps obtune at four RUNNING jobs per user across h200 and
normal, and h200 has 52 GPUs behind that door. The cap counts jobs, not GPUs, so several trainings
in one allocation get past it. First measurement of what that costs.

## The batch

`runs/probe/train_batch.sh granite31-8b 42 2 L0 L1b L1r L2 S1 S2 L0-L1b-L1r-L2-S1-S2` — seven
seed-42 trainings, one job, two H200 NVL, two trainings per GPU (four concurrent).

It ran correctly: **no OOM, no error, and six of the seven specialists completed**, with the breadth
adapter at 1123/1257 steps when this was written. Memory was never the constraint — a 7–8B LoRA at
the panel's 16×4 shape fits twice over in 141 GB.

## Compute is the constraint, and the arithmetic is against per_gpu=2

| condition | packed (4 concurrent, 2/GPU) | comparable solo run |
|---|---|---|
| `L0` | 55 min | ~21 min |
| `L1b` | 60 min | ~23 min |
| `S1` | 168 min | ~36 min |

About **2.75× slower per training**. Four concurrent at 2.75× is ≈1.45× the throughput of running
them one after another; **two concurrent at full speed would be ≈2×**. So two per GPU is slower in
aggregate than one per GPU, and it also converts one OOM into a dead batch rather than one dead
training.

`per_gpu=1` is now documented as the right default and the script prints a warning above it.

## What the script is actually for

Not density. Its value is that N trainings occupy **one job slot**: seven Granite trainings were
seven jobs queued behind a four-slot door, and became one job on the partition with the capacity.
That part worked exactly as intended and is worth keeping — with one training per GPU and more GPUs
per allocation.

---

## Postscript: I killed the batch job by editing its script mid-run

The batch finished all seven trainings and then **exited 2 with a bash syntax error at line 63** --
a line that is syntactically fine. The cause was not the code: I edited `train_batch.sh` (to document
`per_gpu=1`) **while job 408686 was still executing it**. Bash reads a script incrementally from a
file offset, so rewriting the file under a running shell resumes the parse at a byte position that no
longer aligns with a statement boundary.

This repository already knows this. `runs/probe/drain_queue.sh` carries the note "a `while true` loop
that never re-reads itself -- edit then restart", written after the same mistake. I made it again,
three hours after writing a commit message about a rule that lives only in someone's memory not being
a rule.

**Nothing was lost.** All seven Granite seed-42 adapters carry `training_summary.json`; only the
script's own verification-and-exit ran on the corrupted parse. The damage was the exit code: SLURM
marked the job FAILED, and `cks42_granite318b --dependency afterok:408686` became
DependencyNeverSatisfied, which silently stopped the whole Granite chain. Re-chained without a
dependency, since the adapters demonstrably exist.

**The rule, stated where it will be read:** never edit a shell script while a job is executing it.
Copy it, edit the copy, and submit that -- or wait.

## Second fault found in the same sweep: the inverse adapter root was never selected

`ckpt_select_batch.sh` iterates `runs/adapters/$M/python/`. The backward-trained control is
deliberately rooted at `runs/adapters_inverse/` so it cannot collide with `mono_all`'s directory --
which also means the selection loop never saw it. Both models trained to completion (checkpoint-1260
plus `final`) and neither had a `best/`; it surfaced as `FileNotFoundError: system 'inverse_trained'`
when the eval tried to load one, three and a half minutes into a job. The script now covers that root
explicitly, and the two selections are queued.
