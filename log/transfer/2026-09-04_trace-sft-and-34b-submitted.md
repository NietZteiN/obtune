### Target Date: 2026-09-04 (Execution-trace SFT arm built and gated; CodeLlama-34b ladder submitted)

Setup day for two W6 levers (`CLAUDE_SCRATCHPAD.md` §2026-09-04: lever 3 execution-trace SFT,
lever 6 CodeLlama-34b). No accuracy numbers here — every result lands in a later entry. **H1 is
not read**; `final_eval` stays unspent. Everything is on the trainable grid.

- **Hypotheses / what we're testing:**
  - **H-trace (pre-registered here, before any eval):** supervising a per-line execution trace
    of the *still-obfuscated* program before the answer teaches execution rather than surface
    inversion, so it generalises across transforms better than direct-answer SFT. Concretely,
    on the six-condition heldout grid: (a) `trace_L0 − tuned_L0` > 0 pooled with an interval
    excluding zero, and (b) the gain is largest on `S1`/`S2` (the conditions whose obfuscation
    is *computation*, not renaming). CONFIRM if both; REFUTE if pooled ≤ 0 or the interval
    covers zero on every condition. Secondary: `trace_mono − trace_L0` reproduces the breadth
    fingerprint (L0 cost, L1b gain, pooled tie) or breaks it.
  - **H-trace-format (control):** the trace *prompt* on the untuned base (`base_trace`) is
    worth nothing or less — a 7B instruct model asked to trace without training should lose
    format. If `base_trace` gains over `base`, part of any trace-arm gain is prompt, not
    training, and is subtracted.
  - **H-34b:** the scale ladder keeps paying above 13b. `tuned_L0(34b) − tuned_L0(13b)` > 0
    with the tuned +20-over-base gap unchanged; CONFIRM if the interval excludes zero.
- **Setup:**
  - **Trace format** (`src/obtune/trace.py`, `src/obtune/exec/runner_py.py::_Tracer`): completion
    = one line per executed source line that changed a local (`L<n> name=value …`; bare
    line-number events merged onto one line; opaque values as `<TypeName>`; callables skipped;
    `repr` capped at 48 chars), a single `...` after `max_events`, then `=> <literal>`. The
    grader reads the last `=> ` line (`trace.extract_answer`); an empty extraction is a
    `format_fail`, exactly as for the greedy arms. Prompt: `SYSTEM_PROMPT_TRACE` +
    `USER_TEMPLATE_TRACE` (`prompts.py`; `prompt_id = trace_v1`, template sha
    `45207a33adb6000d…`). The greedy template hash is unchanged (`c1e8fe28c30873d7…`) — the
    trace fields enter the hash payload only when `trace=True`, verified equal to HEAD.
  - **Budget frozen after calibration** (200 rows/condition): `max_events 64, max_repr 48`;
    prompt+trace token maxima L0 1966 / S2 2265 / S1 3399 (S1 prompts alone p95 1520) →
    `max_seq_len 4096` (3072 truncates 3.5 % of S1 and the >1 % guard would abort), batch 8×8
    (effective 64, as every other arm), `ckpt_select.max_tokens 2048`, eval `max_tokens 2048`.
  - **Trace cache** `runs/trace_cache/python/v1_64_48.jsonl`, keyed by sha256(code, entry,
    args, cfg), built on the login node at 8 workers (32 hit `ulimit -u 300`). Full corpus:
    mono **26,832 / 26,841** rows kept (5 `trace_raised`, 4 `gold_mismatch`), mean cut
    fraction 0.112; L0 **4,688 / 4,689**, cut 0.083; val 1000 / 333 kept. A first build
    reported 81/603 `trace_ok` drops — stale ok-without-trace records from the calibration
    pass; the loader now treats those as misses and the rebuild kept the counts above.
  - **Configs:** `configs/train/trace_generic_py_L0.yaml` (`run_tag trace_py_L0`, adapters
    under `runs/adapters_trace/` — the adapter dir name encodes only conds/rank/seed and would
    otherwise overwrite the greedy bank), `configs/train/trace_generic_py_mono.yaml` (six
    conditions, `train_size 30000`), `configs/eval/trace_generic.yaml` (systems `trace_L0`,
    `trace_mono`, `base_trace`; six eval conditions; **no H1**). `eval_vllm` refuses trace
    combined with ICL / one-shot / baseline / normalize, and refuses `max_tokens < 512`.
  - **Gates passed before training was released:** `tests/test_trace.py` (5: roundtrip,
    template/hash separation, completion override, runner trace mode, budget cut) green; a
    stub end-to-end eval and ckpt-select on symlinked greedy checkpoints exercised the
    trace-aware extraction and `ckpt_select.json` (`prompt_id`, `max_tokens` recorded); the
    loss-mask gate `scripts/inspect_batch.py --model codellama-7b` ran as dev job **377801**
    and returned **PASS — prompt tokens are -100, completion tokens are supervised**, with the
    decoded completions showing trace lines then `=> `.
  - **Jobs (h200, one GPU each, chained `afterok`):** train **377802** `tr_L0` / **377803**
    `tr_mono` → ckpt-select **377804** / **377805** → eval **377806** / **377807**
    (`eval/trace_generic.yaml`). Pending at close.
  - **CodeLlama-34b:** `codellama/CodeLlama-34b-Instruct-hf` (48 layers × 8192, GQA 8 kv heads,
    67 GB bf16, 7 shards) fetched by CPU job **377810** via `scripts/hf_snapshot.py` after two
    failed attempts (login-node 8 GB vmem cap killed `hf_transfer`; a scratch script in the
    node-local `/tmp` was invisible to the compute node). Registered in `configs/models.yaml`
    with `per_device_batch 4 × grad_accum 16` (effective 64, unchanged; halved per-device
    for the 34b activations), `router_layer 24`, `max_seq_len 2048` (same tokenizer as 7b/13b).
    Jobs: **377812** `bc34` (`eval/basecheck_codellama34b.yaml`, load/format check on
    L0/L1r/S2), **377813** `tr34_L0` (`train/grid_py_L0.yaml`, 6 h wall), **377814** `tr34_mono`
    (`train/mono_generic_py.yaml`, 30 h wall — 13b mono took 5.16 h at 8×8; 34b is ~2.6× the
    FLOPs at half the per-device batch), → **377815** / **377816** ckpt-select → **377817**
    `ev34_grid` (`eval/rq2_generic.yaml --systems base,tuned_L0,mono_all`, `--mem 128G`).
  - Lever 1 (`llama31-8b` go/no-go) still pending as **377796** (Resources).
- **Results:** none yet — all GPU jobs pending at close. Trace cache statistics above are the
  only numbers.
- **What worked / hypothesis verdict:** H-trace, H-trace-format, H-34b all OPEN.
- **Observations:**
  - The trace budget interacts with `S1`: control-flow flattening lengthens both the prompt
    and the trace (every dispatch-loop iteration is an event), so the 64-event cap cuts S1
    traces most often. `cut_fraction` is logged per condition and a large S1-only gain or loss
    must be read against it.
  - Login-node limits shaped the day: `ulimit -u 300` (threads) and an 8 GB virtual-memory cap
    core-dump `torch`, `pytest`, `inspect_batch` and `hf_transfer` alike — everything heavier
    than a cache build now runs as a `dev`/`normal` CPU job (`submit.py --gres none`, added
    today). `submit.py --argv` prepends the interpreter, so `--argv python -m …` renders
    `python python -m …`; jobs 377787 / 377794 died that way and were resubmitted.
- **New questions / new hypotheses:** if `trace_L0` gains, is it the *trace* or the longer
  supervised completion (more gradient signal per row)? A length-matched control — a
  completion of the same token count with no execution content — would separate the two.
  Not scheduled unless H-trace confirms.
- **Next Steps:** when 377806/377807 land, `trace_L0 / trace_mono / base_trace` vs
  `tuned_L0 / mono_all / base` on paired items, cluster bootstrap by `snippet_id` (B = 2000,
  seed 17), plus `format_fail`, truncation rate, and a 50-trial hand audit of `output_raw`
  traces per condition. When 377817 lands, extend the 7b/13b/34b ladder table. Lever 1 grid
  on GO. Lever 7 (X1) design goes to the user before anything is generated.
