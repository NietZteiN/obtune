### Target Date: 2026-09-11 (the h100 MIG node is usable for vLLM after all — `spawn` fixed the fork error; what remains is slowness, not breakage)
- **Revisits** the blanket `--exclude g-06-01` added on
  [`2026-09-10`](2026-09-10_vllm-fork-on-mig.md) after two checkpoint-select jobs died 28 minutes in
  with `RuntimeError: Cannot re-initialize CUDA in forked subprocess`. That exclusion was applied to
  every obtune job, including ones that never touch vLLM.
- **Why revisit it.** `h100` was 100 % allocated except g-06-01, whose **four 47 GB MIG slices sat
  idle**, while obtune's entire eight-job panel chain queued behind `(Resources)` and the juno QOS
  pool on the other partitions was full. The exclusion had become the binding constraint.
- **First result, free: the training jobs never needed it.** `tr_llama31-8b_X1` uses the HF path and
  no vLLM at all. Clearing its exclusion (`scontrol update JobId=... ExcNodeList=""`, which preserves
  the job id and its dependants) started it immediately on an otherwise unreachable node. It runs at
  **22 s/it against ~4–5 s/it on a full H200** — roughly 5× slower, matching the 5.7 vs 2.03 s/it
  measured on 2026-08-28 — but 5× slower is not a comparison with a full card, it is a comparison
  with *waiting indefinitely*.
- **Second result: `spawn` does fix the fork error.** A probe built a 7B vLLM engine on the node.
  `Cannot re-initialize CUDA` appears **0 times** in its log; CUDA reports healthy
  (`H100 NVL MIG 3g.47gb, 46.4 GiB`); both weight shards load in 2.3 s. It was cancelled at 28 min
  still in engine startup, so what is established is *the fork error is gone*, not *the engine is
  fast*. Startup on this node under contention is **> 25 min** against seconds on a full card.
- **The decision that follows.** g-06-01 is enabled for jobs whose walltime can absorb a 25-minute
  startup and excluded for those that cannot:

  | job class | walltime | g-06-01 | why |
  |---|---|---|---|
  | `tr_*` (training) | 4–6 h | **allowed** | no vLLM at all; the exclusion was never relevant |
  | `ev_*` (panel / F2 evals) | 6 h | **allowed** | 25 min of startup is 7 % of the budget |
  | `ck_*` (checkpoint select) | 2 h | **excluded** | 25 min is 21 % of the budget, and these are the jobs that died in the first place |

  Three panel evals and the F2 divergence eval had their exclusions cleared in place, and
  `ev_panel_codellama-7b` — blocked on `(Resources)` for hours — started within seconds of the
  change.
- **A probe bug worth recording, because it cost 19 minutes and looked exactly like the thing it was
  testing for.** The first probe had no `if __name__ == "__main__":` guard. Under `spawn` vLLM's
  engine-core subprocess **re-imports the entry module**, so an unguarded script builds another
  engine in every child, recursively. The tell was the probe's own first `print` appearing twice.
  `eval_vllm.py` and `objectives.py` both guard their mains and were never affected. Noted beside
  the setting in `scripts/env.sh`, since the symptom — a job that starts, reports a healthy GPU and
  then never finishes — reads as a broken node.
- **Not claimed:** that a vLLM eval completes successfully on this node. `ev_panel_codellama-7b` and
  `ev_f2_divergence` are running there now and are the real test; they produce cells the panel needs
  either way, which is why they supersede the probe.
- **Next Steps:** if either eval fails on the node, restore the exclusion for `ev_*` and record it.
