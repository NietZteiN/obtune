# 2026-09-13 — a30 fits CodeLlama-7B and nothing else

**Thread:** setup · **Status:** bound settled empirically · **Supersedes the bound in:** [`2026-09-13_a30-holds-7-8b-only.md`](2026-09-13_a30-holds-7-8b-only.md) and [`2026-09-13_codegemma-vocab-breaks-the-size-rule.md`](2026-09-13_codegemma-vocab-breaks-the-size-rule.md), neither of which is amended

I raised the a30 bound twice today on partial evidence and it was wrong both times:

1. "a30 holds 7–8B" — after CodeLlama-13B OOM'd. Wrong: it also excludes CodeGemma.
2. "a30 holds 7–8B but not CodeGemma (256k vocab)" — after CodeGemma OOM'd. Wrong: it excludes every
   8B model.

Today's fourth and fifth failures settle it. **Granite-3.1-8B and Llama-3.1-8B both OOM'd on a30
training S3**, two minutes in, in the dropout of the forward pass:

```
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 446.00 MiB.
GPU 0 has a total capacity of 23.49 GiB of which 428.25 MiB is free.
```

8.0–8.2 B in bf16 is ~16 GB of weights; with LoRA state, activations and the fp32 logits the remaining
7.5 GB is not enough, whatever the vocabulary size. Every specialist those two models trained
successfully today ran on h100 or h200 — I had simply never checked *where* the successes ran before
writing the rule from the failures.

**The bound, from evidence rather than inference: a30 trains CodeLlama-7B (6.7 B) and nothing else in
this panel.** It serves nothing above ~7 B under vLLM either. `drain_queue.sh` names that one model.

## The habit worth changing

Three entries today generalised from a failure without checking the successes. The cheap check —
`sacct ... | grep <model>` for where the same model's completed jobs ran — would have given the right
bound the first time and saved four cancelled or wasted jobs. When a job fails on a resource, look at
where the *working* runs of the same shape were placed before writing a rule about the resource.
