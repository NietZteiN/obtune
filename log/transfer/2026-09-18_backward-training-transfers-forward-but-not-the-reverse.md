# 2026-09-18 — Inversion is learnable, and the transfer between directions is one-way

**Thread:** transfer · **Data:** `results/cells/invtrained_{generic,inverse}/codellama-7b/`
(92 cells) · sixteen conditions, paired by program, cluster bootstrap 2,000 resamples.

## The control, and why it was needed

Every arm in the panel is trained **forwards** and asked backwards. That design cannot separate two
explanations of the backward failures: *forward training surface-fits the forward mapping*, or
*inversion is simply not reachable by training at all*. The backward-trained control settles it. It
is breadth's recipe exactly --- same six conditions, same rows, same rank, same seed --- with one
change, `prompt.task = input`, so the model is trained **on** the inverse prompt. It is evaluated in
both directions: backwards, its own task, and forwards, what that costs.

## CodeLlama-7B

| | trained backwards | untuned | contrast |
|---|---|---|---|
| **backward** (its own task) | 0.388 | 0.285 | **+10.30** [+8.5, +12.1] \* |
| **forward** (what it costs) | 0.267 | 0.170 | **+9.63** [+7.8, +11.4] \* |
| exact-argument recovery | 0.129 | 0.085 | --- |

## Two results

**Inversion is learnable, and by a wide margin.** Training on it yields +10.3 points, against +3.56
for the best forward-trained arm read backwards (the DARE-TIES merge) and negative values for the
single-adapter arms. So the backward failures reported throughout this project are *not* the task
being out of reach; they are a consequence of what forward training does to the model.

**The transfer is one-way, which is the surprise.** Training backwards does not cost forward
accuracy --- it *improves* it by 9.63 points. Training forwards, by contrast, damages backward
accuracy on most models and arms. The same pair of tasks, the same programs, the same rank and data
budget, and the asymmetry is stark: input prediction generalises to output prediction, output
prediction does not generalise to input prediction.

That is a sharper statement of the paper's mechanism than forward-collapse alone. Forward training
is not merely narrow; it is narrow *in a direction*, and the direction it narrows into is the one
it was trained on.

## Scope

One model. Llama-3.1-8B's backward-trained adapter exists and is checkpoint-selected, but its evals
were never queued --- only CodeLlama's were --- and are now running. Until they land this is a
single-model result and should be reported as one.
