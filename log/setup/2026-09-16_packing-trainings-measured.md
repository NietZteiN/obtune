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
