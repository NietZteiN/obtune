### Target Date: 2026-08-14 (Grid A resume aliasing; 7B, hardrouter and shot-count readouts)

- **Hypotheses / what we're testing:** Mostly a **readout and report-integrity day** — three
  result sets landed overnight and none had been read. Two falsifiable claims were tested against
  data already on disk:
  - **H1:** the ICL shot-count arms are on the same population as §2.2's Grid B rows and can be
    added to that table. CONFIRM if the snippet-id sets match cell-for-cell; REFUTE on any
    mismatch.
  - **H2:** "demos make the fine-tuned adapter worse" (§11.2) is a *format*-compliance effect —
    demonstrations push the adapter off the prompt distribution it was trained on, and the
    cheapest place for that to appear is a broken output format. CONFIRM if `format_fail_rate`
    rises with k and the accuracy penalty disappears once format-failed trials are dropped;
    REFUTE if the failure rate is flat in k and the penalty survives conditioning.

  Plus one question raised by the user and answered here: does anything downstream **filter on
  the parquet `dataset` column**, which does not mean what its name suggests?

- **Setup:** No GPU work. All four A6000s idle throughout; queue empty (201 done). Analysis run
  against the committed cell tree with the project env
  `/data/jvl210002/conda_envs/obtune/bin/python`. Cells read:
  `results/cells/baselines/qwen25c-{1.5b,7b}/python/` (`experiment_id` ∈ {`icl_cross_h1`,
  `icl_k_sweep`, `normalize_baseline`, `zeroshot_7b`, `baselines_gridA`, `baselines_gridA_7b`})
  and `results/cells/main/qwen25c-1.5b/python/` (`mole_*`, `merge_*`, `mono_*`, `tuned_*`).
  Grid identity was determined from `n_items` and `snippet_id` prefix, never from the `dataset`
  column. Report edited: [`../../docs/MASTER_REPORT_2026-08-12.md`](../../docs/MASTER_REPORT_2026-08-12.md)
  (rev 13).

- **Results:**

  **The `dataset` column.** It is not inverted and it is not a grid label. `EvalItem.dataset` is
  the ICSE study's dataset arm, filled by `scripts/07_emit_eval_items.py:84-90` from the
  `program_id` prefix, with an unconditional `else: return "B"` fallback. Grid A corpus programs
  (`apps_*`, `cruxeval_*`) have no `A:`/`B:` prefix, so they all take that fallback and read `B`;
  Grid B testset programs carry a genuine per-snippet `A`/`B`. The letters collide with the
  report's Grid A/Grid B by coincidence. **Nothing filters on it**: across `stats/R/`,
  `scripts/analysis/` and `src/obtune/trial_table.py` the only occurrence is the required-column
  list at `stats/R/01_schema_validate.R:10`. Grid A and Grid B are not inverted anywhere
  downstream.

  **H1 — population match.** Confirmed exactly. `icl_k1/k2/k4` and `tuned_L0_k0/k1/k2/k4` carry
  176 items / 40 programs on L0, L1b, L1r, L2, S2; 145 / 33 on S1; 115 / 27 on H1 — identical
  snippet-id sets to the Grid B specialist, merge and mixture rows. `tuned_L0_k0` uses the same
  adapter sha (`82329cd…`) and the same prompt-template sha (`c1e8fe2…`) as the normal
  zero-shot evals, i.e. it *is* `tuned_L0` on Grid B.

  **The Grid A baseline panel is 33 cells short.** `baselines_gridA_{qwen1.5b,7b}.yaml` ran and
  reported success while writing under half the cells they name. Cell paths are
  `results/cells/{phase}/{model}/{lang}/{system}__{cond}` and encode **`phase` but not
  `eval_source`**; both grids' baseline configs declare `phase: baselines` and share system names,
  so `resume: true` found Grid B cells at the target paths and skipped them.
  - written on Grid A: 1.5B `icl_k4_cross`, `norm_structural`, `tuned_L0` (7/7 each), plus
    `icl_k1_clean__L0` and `icl_k1_cross__L0` only; 7B `icl_k1_clean`, `icl_k1_cross`,
    `icl_k4_cross`, `norm_structural` (7/7 each).
  - missing: **19 at 1.5B** (`icl_k1_clean` ×6, `icl_k1_cross` ×6, `norm_full` ×7), **14 at 7B**
    (`base` ×7, `norm_full` ×7).
  - `icl_k1_clean` and `icl_k1_cross` are now single rows spanning two grids — `L0` at n=1670
    beside six conditions at n=176.
  - Nothing was overwritten: the skipped writes left valid Grid B cells intact, and the two
    `icl_k1_*__L0` cells had no Grid B counterpart (that config never evaluated `L0`).

  **Grid A panel, where complete** (1.5B, n=1214–1670, `base` taken from `main/`, whose Grid A
  populations match the baseline cells' snippet sets exactly for all seven conditions):

  | system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
  |---|---|---|---|---|---|---|---|
  | `base` | 21.7 | 18.8 | 18.7 | 19.8 | 20.7 | 15.3 | 6.4 |
  | `norm_structural` | 22.0 | 18.8 | 18.9 | 19.7 | 20.0 | 19.9 | 12.9 |
  | `icl_k4_cross` | 33.1 | 26.4 | 27.3 | 27.2 | 27.7 | 28.5 | 18.2 |
  | `tuned_L0` | 45.0 | 34.2 | 36.5 | 37.4 | 39.1 | 41.4 | 24.7 |
  | `tuned_S2_s17` | 45.6 | 33.3 | 37.4 | 37.8 | 43.4 | 45.3 | 28.0 |

  **H1 on Grid B is one same-item ladder** (115 items / 27 programs, byte-identical `item_id`
  sets across all nine arms): `base` 11.3 · `norm_full` 13.9 · `oracle_prompt_1shot` 20.9 ·
  `icl_k1` 22.6 · `icl_k2` 28.7 · `merge_ties` 28.7 · `mole_router` 33.9 · `merge_dare_ties`
  **34.8** · `tuned_L0_k0` **34.8**.

  **7B base, Grid B, same items as 1.5B:** L0 57.4, L1b 49.4, L1r 56.2, L2 58.0, S1 50.3,
  S2 55.7, S3 56.8, S4 57.4, H1 36.5 (1.5B: 29.0, 23.3, 23.3, 21.0, 26.2, 18.8, 18.2, 22.2,
  11.3). Penalty vs its own L0 at 7B: L1b −8.0, S1 −7.1, H1 −20.9; every other condition within
  1.7 points, `L2` at **+0.6**.

  **`mole_hardrouter` − `mole_router`**, across L1r, S1 and the six composites and H1:
  +0.6, −0.7, +0.6, 0.0, +2.7, −1.7, +1.7, 0.0, −1.7. Mean |Δ| 1.0, max 2.7. On H1 all four
  ladder arms sit at 32.2–33.9.

  **H2 — format decomposition** (Grid B, mean over 7 conditions, raw acc / acc among format-OK /
  format-fail %): `base` 21.8 / 23.2 / 6.7 · `icl_k1` 27.6 / 29.6 / 6.9 · `icl_k2` 30.6 / 32.0 /
  4.1 · `icl_k4` 31.1 / 31.7 / 1.9 · `tuned_L0_k0` 44.4 / 45.2 / 1.8 · `k1` 42.1 / 42.8 / 1.9 ·
  `k2` 40.9 / 41.8 / 2.3 · `k4` 41.0 / 41.8 / 1.9.

  **Free reproducibility number.** `tuned_L0` exists twice on Grid A (`main/` and the
  `baselines_gridA` re-run) — same adapter sha, seed, prompt, greedy decoding, same items. The
  two disagree by 0.1–0.4 pts (max 0.36 on S2).

- **What worked / hypothesis verdict:**
  - **H1 — SUPPORTED.** Added to §2.2 as seven Grid B rows plus a Grid B `base` floor row, which
    the table lacked; every value reconciles cell-by-cell with Table 39.
  - **H2 — REFUTED.** The adapter's format-failure rate is **flat in k** (1.8 → 1.9 → 2.3 → 1.9)
    and conditioning on format-OK trials moves every arm by under 1.5 points while preserving the
    k0 > k1, k2, k4 ordering. Demos are not knocking the adapter out of format, they are making it
    answer wrong. The crude reading of §11.2's alternative 2 is excluded; a subtler
    distributional-shift account survives and still needs the trained-with-demos adapter.
    Symmetrically, demos *do* teach the base model the format (6.7 % → 1.9 %) but ICL's gain
    survives conditioning (23.2 → 31.7), so the ICL arms are not format artifacts either.

- **Observations:**

  **§11.3's caveat was wrong, and it was blocking a legal claim.** It asserted that the merge and
  mixture headlines are Grid A and therefore not comparable to the Grid B baselines. They are not:
  every merge/mixture `H1` cell is n=115 over 27 programs — Grid B — and §2.2 labelled them `B`
  correctly all along. The error propagated from the header comment of
  `configs/eval/baselines_gridA_qwen1.5b.yaml`, written from memory and never checked, which also
  formed part of the stated justification for spending an H1 `final_eval` access. That access is
  still justified for the `mono_*` and RQ1 comparisons, which genuinely are Grid A — but not for
  the merge comparison, which never needed it.

  With the caveat struck, the result reads directly: **the best merge of six obfuscation
  specialists (34.8) exactly ties a single adapter trained only on clean code (34.8) on the
  held-out obfuscator**, with the eight-expert RouterLoRA mixture 0.9 below both. Same items, no
  new GPU time. That is the sharpest form of §5's negative result in the project, and it was
  sitting in cells that had been on the same grid the whole time. Guard: 27 programs, and 0.9 pts
  is inside the 3.61-pt p95 seed band — the honest reading is a three-way tie, not a ranking.

  **The 7B result constrains the framing rather than adding a row.** Five of seven obfuscation
  penalties largely dissolve at 7B; only `L1b`, `S1` and `H1` survive. The pattern is not random:
  what dissolves is *surface* obscurity (random/sequential renaming, opaque predicates, dead
  code), and what survives is either semantically adversarial (`L1b` names actively lie, rather
  than merely failing to inform) or genuinely structure-destroying (`S1`). `H1` is the only
  condition whose penalty does not shrink with scale (−20.9 at 7B vs −17.7 at 1.5B), which
  strengthens every `H1`-based conclusion here. The cost is a scope sentence the write-up now
  owes: all adapter, merge and mixture results are 1.5B, i.e. at a scale where these transforms
  still cost the model something, and whether merging fails the same way at 7B is unrun.

  **`mole_hardrouter` says "mixture" is the wrong word.** Replacing the gate's softmax with a
  one-hot argmax — same weights — changes nothing (mean |Δ| 1.0 pt, signed both ways, all inside
  seed noise). RouterLoRA's advantage over its uniform and random controls is entirely in *which*
  expert it picks, not in how it blends them. That makes the arm cheaper to defend and opens the
  obvious next question (does the chosen expert track the true condition?), which a soft blend
  could not be asked. The more important column is `H1`, where all four arms land at 32.2–33.9:
  the trained router's 3–5 point edge on the composites is **exactly zero** on an unseen
  transform. Routing is a ceiling on the conditions it was trained over, and not even a ceiling
  outside them — which is §5.2's saturated-router finding arriving from a second direction.

  **The resume-aliasing defect is the second incident from one root cause in two days.** On
  13 August the same mechanism operated at the `phase` level and was fixed by renaming the phase;
  that fix moved the collision down one level to `eval_source` rather than removing it. `phase` is
  being asked to serve as a general output namespace, which it was not designed to be. The
  structural fix is to put `eval_source` in the cell path or in the resume key, so two grids
  cannot alias regardless of how configs are named. A test asserting that no two committed eval
  configs can produce the same cell path with different `eval_source` would catch the whole class.

  **A prompt-independent nondeterminism floor exists and is worth quoting.** 0.1–0.4 pts between
  two identical Grid A runs of the same adapter at temperature 0. It sits *under* §8.4's 1.32-pt
  mean seed noise rather than replacing it, but it means sub-half-point differences are not
  interpretable even before seed variance is considered.

  **Format-failure rates deserve a line in any baseline table.** Untrained arms fail the
  constrained format at 6.7 % on Grid B and 18.1 % on Grid A, against 1.8–2.3 % for adapters —
  well outside CLAUDE.md §4.6's 2 % target. It does not explain the adapter's advantage (see H2),
  but a zero-training-vs-adapter comparison that does not report it invites the objection.

- **New questions / new hypotheses:**
  - **Does the hardened gate's chosen expert track the true condition?** Now answerable, because
    the gate is a discrete selector. `gate_report.json` is written per cell and has never been
    analysed; the entropy readout the routing config specifies is still outstanding.
  - **Does merging fail the same way at 7B?** Unrun, and the 7B base result makes it the natural
    challenge to the modularity claim's scope.
  - **Is `L1b`'s survival at 7B really about adversarial semantics?** Testable against `L1r`/`L2`
    at 7B, which are the same operation without the misleading content.

- **Next Steps:**
  1. Fix the aliasing: `eval_source` into the cell path or resume key, plus the config-collision
     test. Nothing else should be re-run first, or it will alias again.
  2. Re-run the 33 missing Grid A cells under the fix — inference-only. The 14 at 7B are the
     priority: without a Grid A `base` at 7B, the 21 Grid A cells already collected there have no
     matched floor and cannot be interpreted.
  3. Restart the idle workers to activate the duplicate-claim guard (written, tested, inert in the
     currently-loaded `worker.py`). Zero cost while the queue is empty.
  4. `tuned_L0` on Grid B for L0–S2 is **already done** — `tuned_L0_k0` is the same adapter sha on
     the same items — so `oracle_bestof8` can be unblocked for those conditions without the
     ~1 GPU-h that item was budgeted. Only S3/S4 are genuinely missing.
