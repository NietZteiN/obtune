### Target Date: 2026-08-10 (Master report — every cell run to date, in one frame)

- **Hypotheses / what we're testing:** Not a new experiment. Aggregation and audit day: pull every
  finished evaluation cell into one report and check whether the conclusions in the existing
  documents still hold once the *full* RQ1 matrix (both languages, both seeds) and the RQ2 arms are
  in the frame. Two questions carried in:
  **Q1** — does the diagonal-only ("memorization") profile from the pilot repeat for every train
  condition, or is it an `L1b` quirk (this is the `EXPERIMENT_2` question)?
  **Q2** — do the RQ2 arms (router, merges, oracle prompt) recover anything the monolithic arm lost?
- **Setup:** No GPU work; all four A6000s idle throughout, job queue empty (126 done, 0 queued,
  0 failed). New script [`../../scripts/make_master_report.py`](../../scripts/make_master_report.py)
  collates 453 cell parquets (294,908 trials) under `results/cells/` and writes
  `results/analysis/master_report.json`. Cluster bootstrap by `program_id`, 2000 resamples, seed 17,
  BH-FDR per delta family. Env `/data/jvl210002/conda_envs/obtune`. Evaluation git commit for the
  main grid: `469f857`. Report: [`../../docs/MASTER_REPORT_2026-08-10.md`](../../docs/MASTER_REPORT_2026-08-10.md).
  The script deliberately does **not** go through `obtune.trial_table` — see Observations.
- **Results:**
  - RQ1 Python (317-program common subset, both seeds, deltas vs the `L0`-only control, points):
    diagonal `L1b` +3.9/+6.0, `L1r` +3.1/+1.1, `L2` +1.1/+1.9, `S1` +3.5/+5.5, `S2` +3.5/+2.3.
    Mean off-diagonal transfer ratio **0.073** (s17, 16 defined cells), 0.043 (s42), −0.295 (JS s17).
  - Cross-family cells are negative: `L1b`→`S1` −2.6/−3.2, `S1`→`L1b` −2.5/−1.9 (both seeds).
  - **`S2`→`H1` = +3.5\*/+3.1\* (Python), +7.3\*/+7.7\* (JavaScript)** — the only arm anywhere that
    beats the clean-code control on the held-out obfuscator. `S2`→`S1` +3.6/+4.0 (py), +6.2/+2.2 (js).
  - Monolithic arm on `H1`: −3.1\* (r32), −1.6 (r64), −4.2\* (r128), −4.7\* (r192). Control at r64
    (noise floor) −1.6.
  - RQ2: router routing accuracy **1.000** in both languages (val 0.997 py / 1.000 js). Routed arm
    (JS, vs control) +9.0\* `L1b`, +11.9\* `S2`, ~0 elsewhere — cell-for-cell the specialists' own
    numbers. `merge_dare_ties` ≈ control except +8.2\* on `S2`; `merge_ties` 5–9 pts below control on
    identifier conditions; `merge_dare_linear` 5 % accuracy / 54 % format-fail (broken).
    `oracle_prompt_1shot` (untuned + told the type): .243/.180/.197/.213/.202/.226/.158 — ~20 pts
    below every adapter.
  - Seed noise (12 adapters × 7 conditions × 2 languages): mean |Δ| 1.32 pts, median 1.05, p95 3.61.
  - Base-model format-fail rate 17.3 % (py) / 13.7 % (js); oracle-prompt 15.3 %; adapters 2–6 %.
- **What worked / hypothesis verdict:**
  - **Q1 — the memorization profile is a property of the regime, not of `L1b`. SUPPORTED, with one
    exception.** Five of six specialists show spike-on-own-condition and nothing off it; mean
    off-diagonal TR 0.07. The exception is `S2`, which transfers to `S1` *and* to the held-out `H1`
    in four independent runs (2 seeds × 2 languages).
  - **Q2 — modularity recovers the specialists and nothing more. REFUTED as a rescue.** A perfect
    router yields exactly the specialists' gains; merges are at or below the control; oracle
    prompting is not competitive at 1.5B. The RQ2 design's "models know how but not when" branch
    does not apply here — at this scale the model does not know how.
  - The Aug-9 monolithic/rank-sweep conclusions survive re-derivation from raw trials unchanged.
- **Observations:**
  - **`compute_is_core` has silently broken the committed analysis artifacts.** It intersects over
    every eval condition present for a (phase, model, language) group; once the 40-program `S3`/`S4`
    cells landed, the "core" subset collapsed to 23 programs. `results/analysis/transfer_*.json`
    (regenerated 05:28 today) accordingly reports `n_programs: 23`, `n_train_conditions: 2` and
    `mean_tr_offdiagonal: 0.926` — which reads as "transfer is nearly perfect" and is an artifact.
    `results/trials.parquet` has the same defect plus covers only 84 of 453 cells. Treat all of them
    as void until `compute_is_core` intersects within a grid.
  - **There are two disjoint evaluation grids** — corpus (`apps_*`/`cruxeval_sample_*`, 557 py/168 js)
    and ICSE test set (`A:`/`B:`, 40 py/30 js) — and the RQ2 arms live entirely on the second. In
    Python the `L0` control and `base` were never evaluated on the test-set grid at `L0…S2`, so RQ2
    deltas are computable only in JavaScript. 12 missing Python cells, ~10 GPU-minutes.
  - **HumanEval+ reports pass@1 = 0.0** for both the `cft` and `flip` adapters, base and plus splits.
    Not plausible; the forgetting harness (CLAUDE.md §4.7) has effectively never passed for any adapter.
  - **`H1` reads:** 3 `pilot_eval` + 88 `final_eval` events in `ACCESS_LOG.md`, spread over four
    sittings 08-07 → 08-09. No training contamination and the four enforcement layers held, but "one
    frozen final pass" is not what the log describes; any further `H1` evaluation is a third pass.
  - The `S2`→`H1` result is a post-hoc discovery in a 42-cell matrix. It survives FDR and replicates
    over seeds and languages, but the confirmatory test is a second held-out transform, not more
    analysis of this one.
  - Two RQ2 gaps surfaced while documenting the merge/router recipes for §5 of the report:
    (a) `configs/merge/ties_v1.yaml` declares `density_sweep: [0.3, 0.5, 0.7]`, but every merge
    manifest records a single merge at density 0.5 — the sweep never ran, so "merging
    underperforms" is a density-0.5 statement only; (b) `configs/router/router_v1.yaml` declares
    `routing_entropy_on: [H1]` as a reported RQ2 result, but `routing_report.json` has
    `n_heldout: 0` — `H1` was never routed, so how the router fails out-of-distribution is unknown.
  - Two CFT-thread arms are budgeted in `results/srh/budget_qwen7b_python.json` but were never
    trained or evaluated: `fwd2x` (forward-only at 6 epochs — the *compute*-matched control for
    `flip`, since `mix50` only matches on instances and steps) and `cftflip`. `fwd2x` is cheap and
    would close the last opening in the bidirectionality argument.
  - CFT's three-term loss measured by supervised-token share at 7B: **gen 97.7 %, pos 1.13 %,
    neg 1.13 %** — equal instance counts across the three pools do not mean equal loss weight.
  - All three merges share the same six ingredients (`L0,L1b,L1r,L2,S1,S2` specialists, r32, s17,
    `best`), uniform 1/6 weights, density 0.5, `majority_sign_method="total"`, via PEFT 0.20.0
    `add_weighted_adapter`; they differ only in `combination_type`. That both TIES variants retain
    `S2`'s gain and lose the rest is consistent with the `S2` update being the one that does not
    fight the others.
- **New questions / new hypotheses:**
  - **H-S2:** `S2` and `H1` both bury the computation under *inert* material (dead branches / opaque
    guards vs. encoded strings and MBA rewriting), and the transferable skill is "ignore what cannot
    affect the result" — whereas `S1` *rearranges* rather than adds and transfers to nothing.
    CONFIRM if a pre-registered `H2` of the inert-padding family is reached by the `S2` adapter and
    a rearranging `H3` is not; REFUTE if `S2`→`H2` is null.
  - **H-S2-half:** does the `H1` transfer come from dead code (`S3`) or opaque predicates (`S4`)?
    Built but never run at a size that can answer it (33 programs, never against `H1`).
  - Does oracle prompting become competitive at 7B+? The RQ2 "know how but not when" branch is a
    scale question and was only tested at 1.5B.
  - RQ3 now has a concrete hypothesis to test: does the `S2` adapter re-anchor attention away from
    inert spans, and does that shift predict the `H1` gain?
- **Next Steps:**
  1. Fix `compute_is_core` to intersect within an experiment/grid; regenerate the committed analysis
     artifacts. Everything downstream is currently misreported.
  2. Run the 12 missing Grid B Python cells (`tuned_L0`, `base` × `L0…S2` on the test set).
  3. Repair the HumanEval+ harness; run it for every kept adapter, base included.
  4. Decide on `S2`→`H1`: pre-register `H2`, or run `S3`/`S4` at full scale.
  5. Start RQ3 attention extraction against H-S2.
