### Target Date: 2026-09-12 (F1's routing arms were the BASE MODEL under four names, and the analysis read the resulting zero-width interval as CONFIRMED)
- **What happened.** `ev_f1_mole` evaluated four mixture arms (`mole_router`, `mole_hardrouter`,
  `mole_uniform`, `mole_random`) on ten composites and wrote 40 cells. **`obtune.eval_vllm` does not
  implement a mixture architecture at all.** It accepted `arch: mole_router`, applied **no adapter**,
  and wrote the untuned model's outputs under each arm's name.
- **The analysis then "confirmed" two hypotheses from it:**

  | contrast | reported | what it actually was |
  |---|---:|---|
  | `mole_router − mole_random` | **+0.00 [+0.00, +0.00]** | base minus base |
  | `mole_router − mole_uniform` | +0.00 [+0.00, +0.00] | base minus base |
  | `mole_uniform − base` | +0.00 [+0.00, +0.00] | base minus base |
  | `mole_router − mono_all` | −21.46 [−24.02, −18.92] | base minus breadth |

  **H-F1-route CONFIRMED** and **H-F1-route-vs-breadth CONFIRMED** are hereby **WITHDRAWN**. Both
  were satisfied by comparing the base model to itself.
- **THREE INDEPENDENT TELLS FIRED AND NONE WAS READ.**
  1. Every cell's telemetry: `[engine] 1253 prompt(s), 0 with a LoRA, 0 distinct adapter(s)`. That
     line exists **precisely for this failure** — it was added 2026-08-12 after six runs produced
     base-identical output, with the comment *"one line here answers 'was a LoRA applied, and to how
     many prompts' while the run is still going."* It answered. Nobody asked.
  2. `cell_meta.json` records `engine: vllm-0.26.0`; every sound routing cell on disk records
     `engine: hf-mole/...experts=8/rank=256/bs=32`.
  3. **A zero-width confidence interval over 2,000 bootstrap resamples is not a result, it is an
     identity.** `+0.00 [+0.00, +0.00]` cannot arise from two different systems.
- **Root cause is mine and was written down in advance.** The F1 pre-registration
  (`CLAUDE_SCRATCHPAD.md`, 2026-09-12) states: *"`mole_*` runs through the HF path, not vLLM, and is
  slower per cell. Budget 2× the vLLM rate."* I wrote that, then submitted the job with
  `-m obtune.eval_vllm`. The correct entry point is `obtune.mole.eval_mole`, which reuses
  `eval_vllm.run_cell` verbatim behind an `HFEngine`.
- **The merge half of the same experiment is SOUND and is not withdrawn.** Its telemetry reads
  `1253 with a LoRA, 1 distinct adapter(s)` on every cell. Those results stand:
  `merge_ties − tuned_L0` **−5.50** [−6.86, −4.13], `l0merge_dare_ties − tuned_L0` **−1.74**
  [−2.57, −0.91], `merge_dare_ties − tuned_L0` +0.52 [−0.15, +1.20] (H-F1-merge INCONCLUSIVE), and
  `mono_all − tuned_L0` +3.67 [+2.02, +5.24] as the sanity anchor.
- **The published single-transform routing numbers are NOT affected.** Their cells carry the
  `hf-mole` engine string and are not base-identical (`mole_router` 0.429 against `base` 0.258 on
  L0). Only the composite cells from this run are degenerate.
- **Fixes.**
  1. `eval_vllm.run_cell` now **raises** on any `arch` beginning `mole_`, naming
     `obtune.mole.eval_mole` as the correct entry point. It fires before generation.
  2. `scripts/validate_eval_configs.py` warns on every config carrying a mixture arch (22 of 115),
     so the mismatch is visible at commit time rather than after a GPU-hour.
  3. The 40 cells are **quarantined, not deleted**, under
     `results/_quarantine/2026-09-12_mole_vllm_base_only/` with a README, because they are the
     evidence for this entry.
  4. `ev_f1_mole` resubmitted through `obtune.mole.eval_mole` (job 392173), analysis re-chained.
- **The lesson, and it is not "add a guard".** I had already written the correct fact in the
  pre-registration and then contradicted it at submission. The guard helps the next person; what
  would have helped *me* is reading the engine telemetry that the run printed 40 times, or noticing
  that an interval of exactly zero width is impossible between two distinct systems. **A verdict
  should be distrusted when its interval is degenerate, before it is celebrated for being clean.**
- **Next Steps:** re-read F1 when 392173 lands. Until then RQ1's routing claim in
  `paper/paper_latex/sections/rq1.tex` rests on the *published single-transform* numbers only, which
  is what it currently cites.
