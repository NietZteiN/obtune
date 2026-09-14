# 2026-09-14 — The gate auto-queue regenerated a manifest and silently reset its walltime

**Thread:** setup · **Status:** fixed · **Related:** [`2026-09-13_walltime-kill-filed-as-done.md`](2026-09-13_walltime-kill-filed-as-done.md)

`tr_gate_codellama-34b` timed out at **06:00:26** having written nothing. It should have had twelve
hours: after its first OOM I requeued it with `est_gpu_h: 6.0`, and `submit.py` computes the walltime
as `2 × est`.

The estimate was not there when the job was submitted. `drain_queue.sh`'s mixture block **recreates**
the manifest whenever it sees eight experts and no `gate.pt`:

```sh
printf '{"job_id":"tr_gate_%s",...,"est_gpu_h":3.0,...}' "$m" "$m" > "$mf"
```

So a hand-set estimate survives only until the next tick. The manifest I edited was replaced by a
fresh one at 3 h, the job was submitted with a 6 h limit, and it died 26 seconds past it.

**Two things made this expensive rather than annoying.** The job predates the periodic-checkpoint
commit, so six hours of H200 produced no artefact. And 6 h is too tight for *any* gate in this panel:
Granite took 5h00, CodeGemma 5h48, CodeLlama-13B was still short of the line at 6h18. The default was
wrong for every model, not just the largest.

**Fix.** The auto-queue block writes `est_gpu_h: 6.0` (12 h walltime) with a comment recording why,
and the 34B manifest is set back to 6.0 for its resubmission. The generated manifest is still the
single source of truth — the lesson is that a block which *regenerates* state must carry the right
defaults, because a hand edit upstream of it is not durable.

**The general shape, third time today.** `build_ready_merges.py` computed the share with the wrong
squeue field; the merge- and mixture-eval blocks wrote 34B manifests into the partition-agnostic
queue; and now the gate block hardcodes an estimate. Each is a helper that regenerates something the
authoritative path already knows how to compute. Worth folding these into `submit.py` rather than
maintaining parallel defaults in a shell script.
