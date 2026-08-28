### Target Date: 2026-08-18 (RQ3 first sweep: the S2 adapter does re-anchor, on exactly the condition predicted)

- **Hypotheses / what we're testing:** The pre-registered RQ3 hypothesis that §3.5 hands us. `S2`
  (opaque predicates + dead code) is the project's one replicated positive transfer, now confirmed
  at power (`tuned_S2_s17` +3.46 [+2.06, +4.86] over the clean-code control on 1,214 `H1` items).
  The proposed mechanism is that `S2` teaches "ignore code that cannot affect the result".
  - **H1.** If so, the `S2` adapter should move attention OFF inert material (identifiers of dead
    helpers) and ONTO control-flow / dataflow tokens, and should do so MORE than adapters that do
    not carry that skill. CONFIRM if the anchoring shift on the `S2` condition is largest for
    `tuned_S2_s17` and clearly above `tuned_L0` and `tuned_L1b_s17`; REFUTE if it is flat or if
    every adapter shifts equally.

- **Setup:** Host `csr-94608`, all 4 GPUs, detached. 24 jobs = 4 systems x 6 conditions,
  `obtune.eval_hf --mode attn`, layers [4, 9, 14, 19, 23, 27] (4 = the probe's peak at 99.4 %,
  14 = `router_layer`), 150 usable items per cell, Grid A `heldout` items.
  **No `H1` in this sweep, by design**: it is exploratory, and `H1` reads are reserved for
  confirmation. Systems: `base` (the pre), `tuned_L0` (clean-code control), `tuned_S2_s17`,
  `tuned_L1b_s17` (a specialist that helps its own condition and never reaches `H1`).
  3,600 dumps; metrics in `results/attn/rq3_sweep_metrics.parquet`.
  Ran under `scripts/keepalive.sh` (new, see below) with 4 detached workers.

- **Results:** anchoring_shift = D[control_kw + dataflow_critical] − D[identifier] against `base`,
  cluster-bootstrapped by `program_id`, 51 programs in the common subset, pooled over 6 layers.
  Positive = attention moved off identifiers onto control/dataflow.

  | system | L0 | L1b | L1r | L2 | S1 | **S2** |
  |---|---|---|---|---|---|---|
  | `tuned_L0` | +0.008 | −0.024 | −0.031 | −0.011 | −0.032 | **+0.044** |
  | `tuned_L1b_s17` | −0.003 | −0.033 | −0.041 | −0.015 | −0.059 | **+0.030** |
  | **`tuned_S2_s17`** | +0.014 | −0.015 | −0.044 | −0.008 | −0.013 | **+0.111** |

  `tuned_S2_s17` on `S2`: **+0.1113 [+0.0930, +0.1313]** — the largest cell in the table by 2.6x.
  Raw masses on `S2`: identifier 0.178 (base) → 0.134 (`tuned_S2`), anchor 0.230 → 0.297.

- **What worked / hypothesis verdict:** **H1 SUPPORTED.** The `S2` adapter re-anchors attention away
  from inert material specifically on the condition that contains inert material, **2.6x more than
  the clean-code control and 3.7x more than the `L1b` specialist**. The effect is also specific: on
  the three renaming conditions and `S1`, `tuned_S2`'s shift is small, null, or negative.

- **Observations:**

  **`S2` is the only condition with much inert material to ignore, and the profile shows it.**
  Identifier mass under `base` is 0.15–0.18 on `S2` against 0.03–0.04 everywhere else, because the
  dead helpers `deadcode.py` inserts carry their own junk identifiers. So `S2` is the one condition
  where "ignore what cannot affect the result" has a large target, which is exactly why it is the
  condition where the skill is learnable and transferable.

  **Every adapter shifts attention TOWARD identifiers on the renaming conditions** (L1b, L1r, L2 all
  negative, most significant). That is the expected mirror image: on a renaming transform the
  identifiers are what changed, so attending to them more is the adaptation.

  **What this does NOT yet establish.** The link to `H1` is inferential: `tuned_S2` anchors hardest
  on `S2`, and `tuned_S2` is the only adapter that beats the control on `H1`. Connecting the two
  requires either an attention read on `H1` (a quarantine cost) or the knockout intervention
  (`knockout.evaluate_with_knockout`), which is what would make the claim causal rather than
  correlational. CLAUDE.md §3 is explicit that causal claims wait for the knockout. 51 programs,
  one seed, pooled over 6 layers; the per-layer breakdown is in the parquet and unexamined.

  **Two defects fixed to get here, both in the never-run RQ3 chain.**
  (a) `eval_hf.dump_attention` tokenized with NO `truncation` and NO `max_length`, while the
  parallel `capture.py` caps at 1536. Eager attention materializes a [heads, T, T] fp32 softmax, so
  a single pathological APPS program (`apps_1615_0`, ~20,000 tokens, present in EVERY condition,
  0.7 % of a 150-item slice against a median of 339–750) tried to allocate 17.9 GB and
  **OOM-killed all 24 jobs of the first batch**. Fixed by SKIPPING over-long prompts and reporting
  the count, not truncating: `code_span` is a CHARACTER span resolved to token indices downstream,
  so truncation would silently drop part of the very region the metric is computed over.
  `eval_vllm` already drops this same item; the HF path now matches. Batch 2: 24/24 done, 0 failed.
  (b) The loader/format mismatch fixed the previous day (see 2026-08-17 entry).

  **New infrastructure: `scripts/keepalive.sh`.** Three self-healing components exist and none
  covers an ad-hoc queue: `pipeline.sh::ensure_infra` only runs while the pipeline does (and it
  exits when its stage list is complete), `supervise.sh` exits on
  `! grid_work_left && sweep complete` so any non-grid batch reads as finished, and `watchdog.sh`
  restarts `pipeline.sh`, which with all stages done exits immediately. Workers are `setsid` with
  PPID 1 so they survive a logout, but nothing restarted them. `keepalive.sh` re-runs
  `launch_workers.sh`, requeues claims held by dead workers, and exits after N consecutive empty
  polls. It does not choose GPUs or override policy: card selection stays with `launch_workers.sh`
  (`allowed_gpus` / `gpu_budget`) and the per-worker idle check.

- **New questions / new hypotheses:**
  - **Is the anchoring causal?** `knockout.evaluate_with_knockout` masks identifier keys; if
    knocking out identifier attention hurts `tuned_S2` on `S2` less than it hurts `base`, the
    re-anchoring is load-bearing rather than incidental.
  - **Does anchoring predict transfer across the matrix?** The RQ3 design's regression is
    TR ~ anchoring-shift. There are now 18 (system x condition) shift values against a measured
    transfer matrix.
  - **Per-layer structure** is in the parquet and unlooked-at; layer 4 (probe peak) versus 27 may
    separate lexical from semantic re-anchoring.

- **Next Steps:**
  1. The knockout, which is the only thing that makes this causal.
  2. TR ~ anchoring-shift regression across the matrix.
  3. Decide whether an `H1` attention read is worth a quarantine access, or whether the knockout
     plus the trainable-condition regression carries the mechanism claim without one.
