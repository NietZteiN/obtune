# Quarantined: routing cells that are the BASE MODEL wearing four arm names

**2026-09-12.** These 40 cells (4 MoLE arms x 10 composites, CodeLlama-7b, phase `mole_generic`,
`experiment_id: rq1_mole_composite`) were produced by `obtune.eval_vllm`, which **does not implement
the mixture architectures at all**. It accepted `arch: mole_router` and friends, applied **no
adapter**, and wrote cells labelled as routing arms whose contents are the untuned model.

**The tells, all present and all ignored at the time:**

* every cell's telemetry reads `[engine] 1253 prompt(s), 0 with a LoRA, 0 distinct adapter(s)` --
  a line that exists *precisely* for this failure (added 2026-08-12 after six runs produced
  base-identical output);
* `cell_meta.json` records `engine: vllm-0.26.0`, where every sound routing cell on disk records
  `engine: hf-mole/...experts=8/rank=256/bs=32`;
* the analysis reported `mole_router - mole_random` as `+0.00 [+0.00, +0.00]` -- a **zero-width
  interval over 2,000 bootstrap resamples**, which is not a result, it is an identity.

**The spurious verdicts these produced**, now withdrawn: H-F1-route CONFIRMED and
H-F1-route-vs-breadth CONFIRMED. Both were "confirmed" by comparing the base model to itself.

**The merge arms from the same experiment are SOUND** and are not quarantined: their telemetry reads
`1253 with a LoRA, 1 distinct adapter(s)`, and `merge_ties - tuned_L0` at $-5.50$ is a real number.

**Root cause was mine, and it was written down beforehand.** The F1 pre-registration says in terms:
*"`mole_*` runs through the HF path, not vLLM."* I then submitted the job with `-m
obtune.eval_vllm`. The correct entry point is `obtune.mole.eval_mole`.

Kept rather than deleted: they are the evidence for
`log/modularity/2026-09-12_routing-cells-were-the-base-model.md`.
