# 2026-09-13 — A 256k vocabulary breaks the parameter-count rule for GPU placement

**Thread:** setup · **Status:** fixed; three trainings requeued · **Extends:** [`2026-09-13_a30-holds-7-8b-only.md`](2026-09-13_a30-holds-7-8b-only.md) and [`2026-09-13_a30-cannot-serve-what-it-can-train.md`](2026-09-13_a30-cannot-serve-what-it-can-train.md), neither of which is amended.

`tr_L2_codegemma-7b` OOM'd two minutes into training on `g-02-01`, at the vocabulary projection:

```
File "trl/trainer/sft_trainer.py", line 101, in _chunk
    logits = h.float() @ w.float().t()
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.93 GiB.
GPU 0 has a total capacity of 23.49 GiB of which 1008.25 MiB is free.
```

The rule I had just written — "a30 trains 7–8B, serves nothing above 7B" — is stated in parameters, and
parameters are not what ran out. CodeGemma-7B is 8.5B **with a 256,000-token vocabulary**; TRL upcasts
the logits to fp32 for the loss, so one chunk of the vocabulary projection alone asks for 2.93 GiB on
top of 22.5 GiB already resident. Llama-3.1-8B is the same parameter count with a 128k vocabulary and
trains there; CodeLlama-7B has 32k and is comfortable. The binding quantity is
`batch x seq x |V| x 4 bytes`, not the weight count.

**Fix.** The a30 training list is now `codellama-7b`, `llama31-8b`, `granite31-8b` by name — CodeGemma
is excluded and goes to h100/h200 with the larger models. `tr_L2`, `tr_S1` and `tr_S2` for CodeGemma are
requeued; `tr_L1b_codegemma-7b` had already completed on h200 and is unaffected.

**The general lesson,** worth more than the placement fix: a partition rule expressed in parameter
count silently mis-predicts for models with large vocabularies or long contexts. Three failures today
came from three different memory shapes on the same 23.5 GB card — 13B weights, an 8.5B model's KV
cache under vLLM, and an 8.5B model's fp32 logits under TRL. The list is by model name for that reason.
