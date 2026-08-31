### Target Date: 2026-08-30 (vLLM was never blocked by CUDA; three failures wearing one costume)

> Corrects the verdict in `2026-08-28_cuda-driver-and-vllm.md`, which is NOT edited
> (`../../CLAUDE.md` §6, append-only). That entry recorded **"NOT fixed for vLLM"** and
> `01_NEXT_STEPS.md` still carries it as a live constraint. It is wrong as of today, and the
> reasoning that produced it was sound on the evidence it had — the evidence was
> contaminated by the test harness.

- **Hypotheses / what we're testing:** **H-vllm — a vLLM engine can start and generate on
  juno under `envs/obtune-cu129`.** CONFIRM if an engine starts and returns a correct
  generation. REFUTE if it fails for a reason attributable to the CUDA 12.4 driver.

- **Setup:** `scripts/vllm_smoke.py` (new), submitted via
  `scripts/slurm/submit.py --partition a30`. Jobs 358029, 359038, 359040. Follow-up
  `eval_vllm` probe job 359041 on `eval/loto_qwen1.5b.yaml`, 2 systems x 2 conditions,
  `--limit 8`, `--out-root` under `$OBTUNE_SCRATCH` (never `results/cells`).

- **Results:**
  - **H-vllm CONFIRMED.** Job 359040, `a30`, COMPLETED 00:02:46:
    `VLLM OK -> '42\n\ndef g(x): return'` — engine start, greedy generate, correct answer
    for `f(21)` where `f(x) = x*2`.
  - **`eval_vllm` works end to end.** Job 359041, COMPLETED 00:02:30, 4 cells:
    `base__S2 n=8 acc=0.125 format_fail=0.000`, `loto_holdS2__S2 n=8 acc=0.500`. The
    engine log line `8 with a LoRA, 1 distinct adapter(s), uniform=True` confirms the
    multi-LoRA path, and base-vs-tuned divergence clears silent-failure check #2.
  - **The one real environment fault:** flashinfer JIT-compiles its sampling kernel on
    first use and needs `nvcc`/`CUDA_HOME`, which the compute nodes do not have —
    `RuntimeError: Could not find nvcc and default cuda_home='/usr/local/cuda' doesn't
    exist` (job 359038). Fixed by exporting `VLLM_USE_FLASHINFER_SAMPLER=0` in
    `scripts/env.sh`, so every job inherits it.

- **What worked / hypothesis verdict:** **H-vllm SUPPORTED.** The `libcudart.so.13` blocker
  from 08-28 is genuinely gone — the cu129 env fixed it. Everything after that was two
  harness bugs and one missing compiler, none of them the driver.

- **Observations:**
  - **The 08-28 verdict rested on a bug in the test script, not the environment.**
    `/work/jvl210002/migration/gputest.py:15` constructs `LLM(...)` at module top level with
    no `if __name__ == "__main__":` guard. vLLM starts its engine core with `spawn`, which
    re-imports the main module and re-executes that line, tripping
    `_check_not_importing_main`. The traceback is long, mentions CUDA nowhere, and reads as
    an engine failure. A test harness that cannot fail cleanly cannot certify an
    environment — `scripts/vllm_smoke.py` exists so the guard is not optional.
  - **`/tmp` is node-local on juno** (job 358029: `python: can't open file ... [Errno 2]`,
    exit 2 in 0 s). Anything a compute node must read lives on `/work`. This cost a
    submit-wait cycle and would silently cost more in any script that stages to `$TMPDIR`.
  - **Three failures in a row presented as the same symptom** — "vLLM does not start on
    juno" — with three unrelated causes. The cheap discriminator each time was reading the
    ACTUAL exception rather than the summary line; `RuntimeError: Engine core initialization
    failed` is a wrapper that says nothing.
  - **`h100` is heterogeneous and it silently costs runs.** `g-06-01` advertises
    `nvidia_h100_nvl_3g.47gb` MIG slices, not whole cards. On 08-28 `al_S2_mm_l10` landed
    there and ran 5.7 s/it against its siblings' 2.03 s/it on `g-04-02`, dying on walltime at
    step 217/222 — a lost run that read as a lambda effect. Re-run pinned to `g-04-02`
    (job 357710) it took 619.6 s against `mm_l3`'s 619.2 s: identical work, different node.
    `scripts/slurm/submit.py` now takes `--nodelist` / `--exclude`; there was previously no
    way to express node selection at all.

- **New questions / new hypotheses:** Does anything else in the stack JIT-compile at
  runtime? flashinfer was found only because it happens to sit on the sampling path that
  every generation touches. A second compiler dependency on a rarer path would surface as
  an intermittent failure much later.

- **Next Steps:** Correct the "vLLM still blocked" line in `../../continuation/01_NEXT_STEPS.md`
  — it currently gates plan ordering on a constraint that no longer exists. Consider folding
  the vLLM engine-start check into `scripts/smoke_env.py` so it is part of the standard gate
  rather than a separate script.
