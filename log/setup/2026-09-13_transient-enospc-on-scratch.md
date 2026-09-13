# 2026-09-13 — A transient ENOSPC on /scratch killed an eval that never needed the network

**Thread:** setup · **Status:** job requeued; hardening proposed, not applied

`ev_invmerge_llama31-8b` (h100 `g-05-01`) died five minutes in, inside vLLM's engine start:

```
OSError: [Errno 28] No space left on device:
'/scratch/juno/jvl210002/hf_home/hub/models--meta-llama--Llama-3.1-8B-Instruct/refs/main.5312752a.tmp'
```

Minutes later `/scratch` reported **27 T free of 30 T**, 1 % of inodes used, and a 50 MB test write
completed at 2.7 GB/s. So the filesystem was briefly full and recovered. `/scratch/juno` is shared
across every project on this account — the account's usage there is 2.6 T, of which this project's
model cache is 285 G and a sibling project's `probing/` tree is 1.6 T — and `scripts/env.sh` already
records a sibling deleting 87 G of our weights from the old shared cache to make room for its own
data. A neighbour filling it for a few minutes is the same failure class, one layer down.

**What makes this avoidable rather than unlucky.** The write that failed was
`hub/.../refs/main.tmp` — the hub client refreshing a *revision pointer* for a model whose weights
were already local. Nothing about this evaluation needed the network or a hub write. Setting
`HF_HUB_OFFLINE=1` for evaluation jobs would skip the refresh entirely and make the run independent
of both the network and free space on the cache volume.

**Not applied.** `scripts/env.sh` is sourced by every job including the ones that legitimately
download, and offline mode turns a missing cache entry from a download into a hard failure. The right
place is the eval path specifically, and the right time is after the current backfill drains rather
than mid-flight across sixteen running jobs. Recorded here so the decision is deliberate.

Job requeued; nothing else was affected, and no result depended on the failed run.
