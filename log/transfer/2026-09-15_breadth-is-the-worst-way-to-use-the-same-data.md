# 2026-09-15 — On the unseen family, the monolithic breadth adapter loses to everything built from the same specialists — and to an adapter that never saw obfuscation

**Thread:** transfer · **Prompted by:** user, "what is our story? what are the best methods?" ·
**Test:** forward accuracy on X1 (the held-out family), paired by program, cluster bootstrap (2000
resamples, seed 17), format gate 0.25, eight models. Points, 95 % CI, \* = CI excludes 0.

| model | breadth − clean LoRA | breadth − merge | breadth − mixture |
|---|---|---|---|
| CodeLlama-7B | −3.71 [−5.9, −1.6] \* | −4.45 [−6.7, −2.3] \* | −4.78 [−6.9, −2.6] \* |
| CodeLlama-13B | −4.04 [−6.3, −1.9] \* | −5.19 [−7.3, −3.0] \* | −5.93 [−8.1, −3.8] \* |
| CodeLlama-34B | −2.72 [−5.0, −0.5] \* | −2.97 [−5.2, −0.8] \* | −4.61 [−6.8, −2.3] \* |
| Llama-3.1-8B | −2.72 [−4.7, −0.9] \* | −4.45 [−6.6, −2.5] \* | −5.85 [−8.1, −3.8] \* |
| StarCoder2-15B | −2.72 [−4.9, −0.6] \* | −2.31 [−4.6, +0.1] | −3.29 [−5.5, −1.2] \* |
| Gemma-3-12B | −4.70 [−6.9, −2.5] \* | −4.78 [−7.1, −2.6] \* | −5.11 [−7.3, −3.0] \* |
| CodeGemma-7B | −1.98 [−4.0, +0.2] | −2.31 [−4.4, −0.2] \* | −4.94 [−7.1, −2.8] \* |
| Granite-3.1-8B | −0.91 [−3.0, +1.2] | −2.39 [−4.5, −0.4] \* | −3.71 [−6.0, −1.5] \* |

**Negative on 8/8 in every column.** Significant against clean LoRA on 6/8, against the merge on 7/8,
against the mixture on 8/8.

## What this says

The breadth adapter is one LoRA trained on the union of all six seen conditions. The merge and the
mixture are built from six per-condition LoRAs trained on exactly the same rows. Same data, same rank,
same base model; the only difference is whether the conditions were learned in one set of weights or in
six and then composed. On the family none of them saw, composing wins by 2–6 points on every model.

And the monolithic adapter is beaten, on six of eight models, by an adapter trained on **clean code
only** — one that has never seen an obfuscated program. Training on more transforms made the model
worse at an unseen one. That is transform memorisation, which is the RQ1 question in one line.

## For the paper

This is the generalisation leg of the story and it is the same shape as the backward leg
(`2026-09-14_merge-backward-all-eight.md`): the arm that trains one set of weights on everything is
the one that locks — to the transforms it saw, and to the direction it was trained in — and the arms
that compose per-transform specialists do not. Two independent measurements, eight models each, one
mechanism.
