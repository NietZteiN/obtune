### Target Date: 2026-09-03 (A vLLM prefix-cache collision deflated every `tuned_L0` row that ran behind `formatonly` — including the H1 pilot's)

> **CORRECTS** [`2026-09-02_codellama-master-report-tranches.md`](2026-09-02_codellama-master-report-tranches.md)
> (§12 baselines, the RQ2 ladder's L0-only control row) and
> [`2026-09-02_h1-codellama-pilot.md`](2026-09-02_h1-codellama-pilot.md) (the `tuned_L0` H1 row),
> and **withdraws the interval on `tuned_L0 − mono_all` (H1)** from
> [`2026-09-03_cis-and-three-corrections.md`](2026-09-03_cis-and-three-corrections.md): that
> CI was computed on a contaminated cell. It also invalidates the Qwen floor cells behind
> [`2026-08-30_format-floor-and-a-collapsed-control.md`](2026-08-30_format-floor-and-a-collapsed-control.md).
> Nothing is edited in place (`../../CLAUDE.md` §6).

- **How it was found:** not by a test. While picking the strongest clean-code teacher for an
  alignment re-run, `tuned_L0` on `L0` read **0.4299** in `rq1_generic`, **0.4281** in
  `loto_generic`, and **0.3778** in `rq2_generic` — the same adapter (`L0_r32_s17/best`,
  identical sha256 in all three `cell_meta.json`), the same 1670 items, greedy decoding. The
  rq1 and loto cells agree on 96.9 % of raw outputs; rq2 agrees with them on 60.6 %, is
  3–6 points lower on **every** condition, and ran in about half the wall time (3.7 s vs
  7.0 s). Half the time on the same prompts means half the prefill, which means a cache hit.

- **Mechanism (verified in the installed source):** vLLM 0.26 hashes prefix-cache blocks on
  `LoRARequest.lora_name` (`v1/core/kv_cache_utils.py::_gen_lora_extra_hash_keys`), **not**
  on `lora_int_id`. `eval_vllm.py::Engine.lora_request` named adapters `<parent>/<leaf>`, so
  `runs/adapters/…/L0_r32_s17/best`, `runs/adapters_formatonly/…/L0_r32_s17/best` and
  `runs/adapters_overtrain/…/L0_r32_s17/best` were all **`L0_r32_s17/best`**. In any engine
  that evaluated `formatonly` and then `tuned_L0`, the second decoded the tuned adapter on
  top of the label-shuffled control's cached prompt KV. The int ids were distinct, so the
  weights were right; only the prefill was wrong — which is why nothing in the adapter-
  effective guard, the output-diversity check, or the sha provenance fired.

- **Blast radius (`scripts/audit_prefix_collisions.py`, 2,727 vLLM cells, write order by
  mtime within each `run_ts` group): 28 cells.**

  | phase | model | cells | prefill came from |
  |---|---|---|---|
  | `rq2_generic` | CodeLlama-7b | `tuned_L0` × 6 | `adapters_formatonly` |
  | `baselines_generic` | CodeLlama-7b | `tuned_L0` × 6 | `adapters_formatonly` |
  | `h1_codellama` | CodeLlama-7b | `tuned_L0` × H1 | `adapters_formatonly` |
  | `grid_rq1_7b` | Qwen-7B | `formatonly_lr20e6` × 6 | `adapters_formatonly_lr50e6` |
  | `formatonly_fix` | Qwen-1.5B | `formatonly_{orig,lr2e5,ep1}` × 3 | `adapters` (tuned_L0) |

  **Clean:** the RQ1 matrix (`formatonly` was written by the separate `ev_floor` job and
  `rq1_matrix` resumed past it), LOTO (no `formatonly` in the job), every merge, mono, MoLE,
  rank, sweep and extra-condition cell, and every RQ3/HF-path number. The `formatonly` rows
  in `rq2_generic`/`baselines_generic`/`h1_codellama` ran FIRST in their engines and are clean.

- **What the contaminated cells were load-bearing for:**
  1. **The H1 headline on CodeLlama.** "`tuned_L0` 0.238 vs `mono_all` 0.232" compared a
     contaminated cell against a clean one. Elsewhere the contamination cost `tuned_L0`
     3–6 points, so the true H1 value is plausibly ~0.27–0.29 — which would put the
     clean-code adapter **above** `mono_all` by a margin the CI would carry, and level with
     the specialists. That is a guess; it is not a number. The pilot read of that one cell
     never measured the adapter, and re-measuring it is a quarantine decision (§3.2), not a
     pipeline decision. **Not re-run. Referred to the human.**
  2. The RQ2 ladder's "against the L0-only control" column on CodeLlama used the deflated
     row, so every "merge X beats `tuned_L0`" margin on CodeLlama is overstated by ~5 pts.
  3. §12 baselines: "the best ICL arm recovers about half of fine-tuning's gain over the
     floor" measured fine-tuning's gain from the deflated row, so ICL recovers **less** than
     half; the direction of that claim survives, the fraction does not.
  4. The Qwen floor fractions ("2–14 % at 7B, 62–67 % at 1.5B") came from contaminated
     `formatonly` cells. Qwen cannot be re-evaluated on this cluster; those fractions are now
     **unverified** and the CodeLlama floor (clean, `ev_floor`) is the only one that stands.

- **Fix:** `lora_name` is now the resolved full path (unique by construction, still readable
  in vLLM's logs). `tests/test_lora_name_unique.py` pins it with a stub `vllm` so it runs on
  the login node. The 28 cells are moved — not deleted — to
  `results/cells/_contaminated_2026-09-03/` with a README, and `resume: true` will therefore
  re-evaluate them. Re-runs queued for the 12 non-H1 CodeLlama cells: `rerun_rq2_L0` (375905)
  and `rerun_base_L0` (375906).

- **Why the existing guards missed it:** every silent-failure check in `../../CLAUDE.md` §4
  compares a tuned cell against `base` or against itself (diversity, format, truncation).
  None compares the same adapter against itself **across jobs**. The audit script does, by
  construction of the collision; a general version — re-evaluate one canary adapter at the
  end of every eval job and assert ≥95 % raw-output agreement with its first evaluation —
  would have caught this on 2026-09-01 and is the right permanent guard. Filed under Open
  ideas in the thread README.

- **Next steps:** re-runs land → recompute the RQ2 control column and §12 fractions →
  human decision on the H1 `tuned_L0` re-read (one cell, `purpose=pilot_eval` repair, or
  wait for `final_eval`) → then the teacher choice for the alignment re-run, which is what
  started this.
