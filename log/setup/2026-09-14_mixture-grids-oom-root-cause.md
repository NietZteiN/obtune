# 2026-09-14 — Four mixture grids died the same way, and halving the batch was the wrong fix

**Thread:** setup · **Status:** root cause found, fixed in `HFEngine.generate`, every pending grid picks it up on start

## The pattern

| grid | card | batch | died at | in use |
|---|---|---|---|---|
| CodeLlama-7B forward | H100 80 GB | 32 | X1 | 78.2 GiB |
| CodeGemma backward | H100 NVL 93 GB | 32 | X1 | 89.0 GiB |
| CodeLlama-13B forward | H100 NVL 93 GB | 32 | L2 | 92.3 GiB |
| CodeLlama-13B forward, requeued | **H200 141 GB** | **16** | **S2** | **136.6 GiB** |

Four cards, two batch sizes, one shape: the grid runs for an hour or more and dies at the first
condition whose prompts are long. Halving the count bought one more condition on a card with
nearly twice the memory. That is not a batch-size problem.

## The cause

`HFEngine.generate` sorts prompts by length so batches pad to a similar width — correct — and then
cuts batches by **count**. The last batches of every cell are therefore 16 or 32 prompts of up to
2048 tokens, each run through **eight experts at once** for the per-token gate. On X1 with the 13B
tokenizer the longest prompt is over 2,000 tokens; sixteen of them padded together is 32k+ tokens of
activations across the expert bank. Short conditions never get there, which is why every death was
at X1, L2 or S2 and never at L0.

## The fix

Batches are now cut by a **token budget** (padded width × size, `engine.max_batch_tokens`, default
what batch 16 at the ladder's median length already used). Short prompts still fill a batch of 16;
long ones shrink it to whatever fits the budget. Replayed on X1's real prompt lengths under the 13B
tokenizer: the old scheme's worst batch was 16 × the maximum length; the new scheme's worst batch is
bounded by the budget and its batch sizes stay in the mid-teens for the ladder. The CUDA cache is
also emptied between cells so one long cell's fragmentation is not handed to the next.

The 13B forward grid is requeued for a third attempt at the head of the queue. The CodeGemma
backward, StarCoder2 forward, 34B forward and 34B backward grids all start after this change and
inherit it; the grids already running keep the old code and have passed their long conditions.

## And the seed-42 adapters need selecting

The first Llama-3.1-8B seed-42 specialist finished with three checkpoints and no `best/`. The
selection script hardwired `_s17` and would have reported every `_s42` adapter as "not trained
yet". It takes the seed as its second argument now and covers L0 and X1, which s42 also has to
select; it stays idempotent, so it runs once per model when enough adapters have landed.

**Addendum, same hour.** The first replay quoted a 20,320-token prompt; that prompt is dropped by
`run_cell`'s over-length filter before any engine sees it, and the replay had skipped the filter.
Re-run with it: see the numbers appended below by the same script.

| X1, 13B tokenizer, after the filter | old (count of 16) | new (token budget) |
|---|---|---|
| prompts | 1,205 kept, 10 dropped | same |
| longest prompt | 1,994 tokens | same |
| worst batch | 16 × 1,994 = **31,904** padded tokens | **9,552** padded tokens (30 % of old) |
| batch sizes | 16 throughout | min 2, median 12, max 16 across 107 batches |

The worst batch that reaches the eight-expert forward is a third of what it was, and the ladder's
short prompts still run at full batch, so the cost is a few percent more batches, not a slower grid.
