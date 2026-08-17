### Target Date: 2026-08-17 (ATTRIB draft v2 from the 08-12 runs; the cross-pass determinism floor)

- **Hypotheses / what we're testing:** Mostly a fold-in day, with one real hypothesis that
  arose mid-task.
  - **H-D1 (unplanned, decisive for how tables are sourced):** the several different
    `base` reverse rates across 1.5B passes (2.9 % in three runs, 2.7 % in two) are
    **program-set drift**, as `configs/srh/eval/e2_seeds_qwen1.5b.yaml` asserts in its
    header. CONFIRM if the `program_id` sets differ between passes; REFUTE if the sets are
    identical, in which case the movement is generation- or scorer-level and the config's
    gate is testing the wrong thing.
  - The rest of the day is not hypothesis-driven: compute the missing dose-ladder CIs,
    build Fig. 1, and fold the four evals that completed 2026-08-12 into the manuscript.

- **Setup:** No GPU (all four cards busy: 0/2/3 held by the borrower's sglang +
  `steer_run`/`transfer_gate` jobs, 1 by obtune's own `composite_qwen1.5b_py` training).
  Env `/data/jvl210002/conda_envs/obtune`, `TMPDIR=/data/jvl210002/tmp_pip`. LaTeX via
  tectonic 0.17.0 at `/data/jvl210002/conda_envs/tex`.

  Commands:
  ```bash
  # dose-ladder contrasts (the default contrast list has no mix5/mix10/mix25 rows)
  python scripts/srh/24_contrasts.py \
    --run results/2026-08-12_cft-bidirectional/qwen25c-1.5b/python/e3_dose_qwen1.5b \
    --contrast cft-sft --contrast mix5-sft --contrast mix10-sft --contrast mix25-sft \
    --contrast mix50-sft --contrast mix10-mix5 --contrast mix25-mix5 \
    --contrast mix50-mix5 --contrast mix50-mix25 --contrast sft-base \
    --contrast cft-base --contrast mix5-base --contrast mix50-base

  # Figure 1, generated from the run rather than hand-typed
  python scripts/srh/25_fig_dose.py \
    --run results/2026-08-12_cft-bidirectional/qwen25c-1.5b/python/e3_dose_qwen1.5b \
    --out paper_bidirectional/fig_dose.tex

  cd paper_bidirectional && tectonic -X compile main.tex
  ```

  New file: [`../../scripts/srh/25_fig_dose.py`](../../scripts/srh/25_fig_dose.py).
  Runs read: `e3_dose_qwen1.5b`, `e2_seeds_qwen1.5b`, `e7_strategies_qwen7b`,
  `e3_javascript_qwen1.5b` (all under `results/2026-08-12_cft-bidirectional/`), plus
  `e1_qwen1.5b`, `e1_qwen1.5b_s42`, `e2_factorial_qwen1.5b` for the determinism check.

- **Results:**

  **Dose ladder, with the intervals it was missing** (1.5B, 300 programs, strict):

  | contrast | Δ (pp) | 95 % CI | excludes 0 |
  |---|---|---|---|
  | `mix5` − `sft` | **+25.7** | [+23.9, +27.7] | yes |
  | `mix10` − `mix5` | +2.1 | [+1.0, +3.1] | yes |
  | `mix25` − `mix5` | +3.4 | [+2.1, +4.7] | yes |
  | `mix50` − `mix5` | **+4.5** | [+3.2, +5.8] | yes |
  | `mix50` − `mix25` | +1.1 | [+0.0, +2.1] | **no** |
  | `mix50` − `sft` | +30.2 | [+28.5, +31.9] | yes |

  Arm rates: `sft` 0.3 · `mix5` 26.1 · `mix10` 28.1 · `mix25` 29.5 · `mix50` 30.5 ·
  `base` 2.7.

  **H-D1 — cross-pass determinism.** `base` arm, 1500 reverse trials, five 1.5B passes:

  | pair | generations differing | strict flips |
  |---|---|---|
  | `e1_qwen1.5b` vs `e1_qwen1.5b_s42` | **0 / 1500** | 0 |
  | `e1_qwen1.5b` vs `e2_factorial` | 116 (7.7 %) | 4 |
  | `e1_qwen1.5b` vs `e2_seeds` | 112 (7.5 %) | 4 |
  | `e1_qwen1.5b` vs `e3_dose` | 118 (7.9 %) | 5 |
  | `e2_factorial` vs `e2_seeds` | 102 (6.8 %) | 8 |
  | `e2_seeds` vs `e3_dose` | 87 (5.8 %) | 7 |

  `program_id` sets: **identical (300/300) in all five passes.** `base` strict spans
  2.67–2.87 %.

  **Appendix numbers recomputed** (per-arm cluster-bootstrap CIs over `trials.jsonl`):
  App. B is now six arms × four strategies from `e7_strategies_qwen7b` alone; App. D is
  six arms × two seeds plus a `base` anchor row; App. E is the JavaScript table.

  **Draft v2 compiles**, 10 pp total: body p1–p7, references p8, appendices A–E p8–p10.

- **What worked / hypothesis verdict:**

  **H-D1 REFUTED, and the config's gate is mis-specified.** The program sets are
  byte-identical, so nothing drifted. The movement is **batch nondeterminism**: greedy
  decoding is not bitwise reproducible across passes because the engine batches
  continuously, so which arms share a pass changes reduction order and occasionally an
  argmax. Three independent confirmations: (i) the only pair with the same arm list is
  identical on all 1500 generations, (ii) two *same-day* passes disagree with each other,
  ruling out a code change between 08-10 and 08-12, (iii) the diverging trials have
  different `output_raw`, so it is generation and not scoring.

  The practical rule the paper already followed — one pass per table — was right, but it
  was justified by a wrong story ("different 300-program draws"). It is now justified by
  a measurement, with a stated resolution of ±0.3 pp on any cross-pass comparison.

  **The dose claim needed correcting before it reached the paper.** The 08-15 status doc
  called the ladder a "step" on the strength of `mix5` reaching 86 % of `mix50`'s effect.
  With CIs computed, `mix50` − `mix5` = **+4.5 pp [+3.2, +5.8]**, which excludes zero —
  the climb is real, just small. What *is* flat is the top: `mix50` − `mix25` = +1.1
  [+0.0, +2.1], CI touching zero. The figure and §3 now say "saturating", not "step".
  Had the ladder been written up from point estimates alone, the paper would have
  overclaimed.

- **Observations:**
  1. **Three stale `adapter_effectiveness.FAILED.json` files** sit beside good results
     (`e3_dose`, `e2_seeds`, `unlearn_rev_minus_sft_python`), each written 08:37–09:05 on
     08-12 by a guard that tripped on a first attempt, each superseded by a `summary.json`
     written ~2 h later with `identical_rate` ≈ 0 for every arm. The failure files claim
     **1.0 for every arm**. Because the results dir is keyed on `run_tag`, a re-run lands
     in the same directory and nothing but mtime distinguishes current from superseded.
     `evaluate.py` now unlinks the marker on a successful guard pass. The three existing
     files are left in place pending human approval (CLAUDE.md §2 destructive-command rule).
  2. **`24_contrasts.py` overwrites `contrasts.md` wholesale**, so `--contrast` must carry
     the full desired set, not just the additions — passing only the ladder rows would have
     silently dropped the `cft`−`sft` null from the dose run's table.
  3. Adding the four runs pushed the body from ~6.4 pp to ~7.5 pp. After the three trims in
     `paper_bidirectional/README.md` plus moving the fidelity block and the arm table to an
     appendix, the body is **7.0 pp against a 3–6 pp allowance** — still ~1 pp over. The
     remaining candidates (Table 3 budget, Table 4 by-condition, §1) are content decisions,
     not mechanical trims, so they are left for the author.
  4. `base` at 7B now has a third value (13.2 %, `e7_strategies`) alongside 12.9 and 13.0 —
     same phenomenon, larger absolute spread at the larger model.

- **New questions / new hypotheses:**
  - **H-D2:** does the cross-pass floor scale with model size? 1.5B spans 0.2 pp, 7B spans
     0.3 pp on `base`. If it grows, the 7B single-seed arms need the same anchor treatment
     App. D gives the 1.5B ones. Cheap to test from data already on disk.
  - **H-C1 (the strongest remaining GPU run):** the benefit saturates by a 5 % reverse
     share, but does the *cost* — 6–7 pts of HumanEval+ at 7B — saturate too? If cost is
     roughly linear in reverse share while benefit is not, `mix5` dominates `mix50` and
     the paper gains a prescription. CONFIRM if HumanEval+ on `mix5`/`mix10`/`mix25`
     rises monotonically toward `base` as the reverse share falls; REFUTE if flat.

- **Addendum (same day): H-C1 wired into the scheduler, not launched.**
  [`../../scripts/srh/26_enqueue_forgetting.py`](../../scripts/srh/26_enqueue_forgetting.py)
  enqueues the five cells as a named preset. It follows `22_enqueue_evals.py` in asserting
  the preconditions the queue cannot express, because the hand-written manifests these
  cells were previously created from skip all of them: adapter-exists, adapter-belongs-to-
  model (the `preflight.py` defect), no duplicate job id, and one new to forgetting —
  **the result file must not already exist**, since `obtune.forgetting` overwrites
  `results/forgetting/humanevalplus_<model>_<tag>.json` silently and Table 5 quotes several
  of those. All four guards were exercised by dry run; the overwrite guard correctly blocks
  a re-run of `flip`, the model guard blocks a 1.5B adapter under a 7B model, and the
  adapter guard blocks `mix10 @ 7B`, which is the §7 dose anchor and is not trained.

  Default priority is **59**, which sits behind the five modularity jobs at 10–20 rather
  than jumping them — the documented ladder reserves 10–50 for the RQ1/modularity grid.
  Going first requires typing `--priority 5`, which costs the FSE paper and is a human call.

  **Nothing was enqueued and no GPU was touched** (all four cards busy at the time).
  The standalone `26_forget_attrib_gaps.sh` written earlier the same day was deleted: two
  launch paths to the same result files, with no shared duplicate detection and a hand-run
  job racing the worker for the same idle card, is precisely the class of defect this
  thread keeps finding.

- **Next Steps:**
  1. Run H-C1 when a card frees: `python scripts/srh/26_enqueue_forgetting.py --preset
     attrib-gaps --write`. Inference only, ~10–30 min for all five cells.
  2. Decide the last ~1 pp of trim (Table 3 or Table 4 to appendix).
  3. Delete the three stale FAILED markers once approved.
  4. Venue style file, anonymisation, OpenReview checklist before Aug 28.
