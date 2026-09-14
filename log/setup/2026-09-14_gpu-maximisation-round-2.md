# 2026-09-14 — GPU maximisation, round two: two OOMs requeued, a second seed on a second model

**Thread:** setup · **Asked by the user:** "continue running stuff for the paper, maximize GPU usage" · **Follows:** [`2026-09-14_gpu-maximisation.md`](2026-09-14_gpu-maximisation.md)

## What had landed and what had died

Landed: both seed-42 merges for CodeLlama-7B (CPU, 9 min each). Still pending: the four a30
trainings (behind the sibling project's queue), the StarCoder2 mixture requeue.

Died: **two mixture grids, both CUDA OOM on the 93 GB H100 NVL node at batch 32** — CodeGemma's
backward grid at X1 (88.97 GiB in use, needed 5.99 more) and CodeLlama-13B's forward grid at L2
(92.31 GiB in use, needed 1.26 more). Same class as this morning's CodeLlama-7B OOM. Batch 16 in
both configs, requeued; resume skips the cells already written. Three of eight models have now hit
this on the mixture path; the remaining grids are being left at 32 only because they have run
past their X1 cells already.

## What the free capacity is now doing

h100 shows three mixed nodes with room to backfill; obtune holds one of its two h200 slots. The
paper-relevant work that fits that shape is **a second seed on the panel's other router-measured,
backward-readable model, Llama-3.1-8B**. Ten trainings queued at seed 42 (L0, seven specialists,
X1, breadth) at priority 60, below every evaluation grid, so they take h100 only when the grids
leave it idle. Each was ~24 min at seed 17. The anchored arm and the two merges follow once L0 and
the six specialists exist; two eval configs (23 conditions, forward and backward, same phases as the
7B pair) are written and gated by the missing-adapter guard.

Rules registered in `CLAUDE_SCRATCHPAD.md`. One honest prediction there: Llama's anchored arm has
the *smallest* forward-collapse rate on the panel (0.025 against breadth's 0.021), so the collapse
ordering is the claim most likely to come out inconclusive on this model from seed noise alone —
which is the point of running it.

## Not done

The h200 share stays at two. No 8B model goes to a30. The Gemma-3 and CodeLlama-34B mixture grids
wait on their gates, which are training.
