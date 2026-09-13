# 2026-09-13 — a30 cannot *serve* the models it can *train*

**Thread:** setup · **Status:** fixed; one job requeued · **Extends:** [`2026-09-13_a30-holds-7-8b-only.md`](2026-09-13_a30-holds-7-8b-only.md), which is correct as far as it goes and is not amended here.

The earlier entry restricted the a30 queue pass to 7–8B models after a 13B training OOM'd. That was
the right bound for **training** and the wrong bound for **evaluation**. `ev_1shot_codegemma-7b`
(393506) then failed on `g-02-01` at engine start:

```
ValueError: To serve at least one request with the model's max seq len (8192), 3.5 GiB KV cache is
needed, which is larger than the available KV cache memory (0.92 GiB). Based on the available
memory, the estimated maximum model length is 2144.
```

CodeGemma-7B is 8.5B: ~17 GB of bf16 weights on a 23.5 GB card leaves under a gigabyte for the KV
cache, and vLLM refuses to start rather than silently truncating the context. LoRA **training** of the
same model fits, because training reserves no KV cache — the two workloads have different
memory shapes and the same partition bound does not serve both.

**Fix.** `runs/probe/drain_queue.sh`'s a30 pass now selects `tr_*` manifests only, still restricted to
the 7–8B models. Evaluations go to h100 and h200. `ev_1shot_codegemma-7b` is requeued.

**Rule of thumb, added to the size table in the earlier entry.** a30 (23.5 GB): trains 7–8B, serves
nothing above ~7B at an 8192-token context. Lowering `gpu_memory_utilization` does not help — the
weights are the floor, not the headroom. The eval path's real requirement is *weights plus a few GB
of KV*, so 8.5B needs a 40 GB card or larger.
