### Target Date: 2026-09-08 (Setup — RQ5′, the bidirectional stress test: does forward tuning help INPUT prediction?)
- **Hypotheses / what we're testing:** User request: *"add Bidirectional ty as another rq (does
  output prediction also help with input prediction — this is like a stress test for true
  understanding)"*. Every adapter in the campaign was trained on program + call → **value**. If the
  gain is a model of the program, it should survive asking the same items **backwards** (program +
  value → a call that returns it, CRUXEval-I style); if it is forward-task fitting, it should not.
  The ATTRIB replication (`paper_bidirectional/`, Nikiema et al. 2025) found tuning direction-specific
  for *code emission*; this is the value-level analogue. Pre-registered in `CLAUDE_SCRATCHPAD.md`
  ("2026-09-08 — RQ5′ BIDIRECTIONAL") and committed as `832a6cb` **before** submission:
  - **Format gate** (first): pooled-seen6 inverse `format_fail_rate` > 0.25 ⇒ arm NOT INTERPRETABLE, dependent hypotheses INCONCLUSIVE. `formatonly − base` reported as the format residue.
  - **H-inv-transfer**: CONFIRMED iff `tuned_L0 − base` @ seen6 ci_lo > 0 **and** `tuned_L0 − formatonly` @ seen6 ci_lo > 0; REFUTED iff TOST-equivalent at ±1.0 or ci_hi < 0 ("cognitive specialization" replicates at value level); else INCONCLUSIVE.
  - **H-inv-breadth** `mono_all − tuned_L0` @ obf; **H-inv-cons** `cons_lam3 − mono_all` @ obf; **H-inv-family** `tuned_X1 − tuned_L0` @ X1 — each ci_lo > 0 CONFIRMED / equivalent or ci_hi < 0 REFUTED / else INCONCLUSIVE.
  - **H-inv-diagonal**: specialists vs `tuned_L0` on their own condition, ≥ 3/5 CONFIRMED, 0/5 REFUTED, else PARTIAL.
  - **Direction ratio** DR(arm) = (inv_arm − inv_base)/(fwd_arm − fwd_base) pooled seen6, descriptive. BH-FDR over the five primary contrasts reported. **No H1.**
- **Setup:**
  - Prompt: `src/obtune/prompts.py` gained `SYSTEM_PROMPT_INVERSE` / `USER_TEMPLATE_INVERSE` behind `task="input"`; `prompt_id = inverse_1shot_v1` (one L0 demonstration for **every** arm, so no arm is asked to invent the answer format). `tests/test_inverse.py::test_forward_prompt_untouched_by_inverse_task` proves the forward template hash is unchanged.
  - Grading: **execution**, not string match — `src/obtune/inverse.py` (sha256 `7ba82900dd1f…`) parses a single-line `name(args)` with `ast.literal_eval`, runs it in the exec sandbox (`src/obtune/exec/pool.py`, 2 s / 512 MB) and scores correct iff the canonical output equals the gold `output_repr` (float tol 1e-6). The gold arguments are never the target; any call that returns the value counts. `format_fail` = not a parsable single-line call; `error_category` ∈ empty / multiline / unparseable / call_raised / exec_<status> / wrong_value. Verified on 80 real held-out items: the gold call reproduces 80/80, wrong args → `wrong_value`, prose → `unparseable`. Python only (JS raises).
  - Eval: `src/obtune/eval_vllm.py` `task: input` path (extra trial columns `task, exec_status, exec_output, called_name, args_exact`; `grade_method = exec`; `_assert_resume_same_grid` refuses to mix tasks in one cell; `run_grid` refuses `task: input` with H1). Config `configs/eval/inverse_generic.yaml`, phase `inverse_generic`, heldout items, `max_tokens 128`, conditions L0 L1b L1r L2 S1 S2 X1.
  - Arms (11, all forward-trained s17 adapters, never trained on the inverse task): `base`, `formatonly`, `tuned_L0`, `mono_all`, `cons_lam3`, `tuned_X1`, `tuned_{L1b,L1r,L2,S1,S2}`.
  - Stages added to `scripts/pipeline/plan.yaml`: `ev_inverse_core` **382620**, `ev_inverse_specialists` **382621** (h200, 3 h each), `an_inverse` **382622** (`scripts/analysis/42_inverse.py` → `results/analysis/pipeline/inverse_codellama7b.json`; afterok both). `an_inverse` added to `report`'s afterany list for future runs; the already-queued `report` 382561 does not wait on it and will be re-run with `--only report`.
  - Forward numbers for DR come from the existing Grid A cells (`x1_generic`, `rq1_generic`, `objectives_generic`, `baselines_generic`, `extra_generic`, `rq2_generic`, `formatonly_fix`); nothing forward is re-run.
- **Results:** none yet — both eval jobs pending on `QOSMaxJobsPerUserLimit`.
- **What worked / hypothesis verdict:** pending.
- **Observations:** Expectation stated before the read: base inverse accuracy will be well below the forward 0.21 (CRUXEval-I < CRUXEval-O for every published model), and `base` may fail the format gate outright — the gate and the `formatonly` control exist for that. The interesting reads are (i) whether `tuned_L0` clears `formatonly`, which is the reasoning-vs-format separation the forward grid cannot make, and (ii) whether the DR ordering matches the forward ordering — if `cons_lam3` keeps a larger fraction of its forward gain than `mono_all`, that is mechanism evidence RQ4′ does not otherwise have.
- **New questions / new hypotheses:** an adapter *trained* on the inverse task (or on both directions) would turn the stress test into a training-signal question; not pre-registered, not run.
- **Next Steps:** read `an_inverse` when 382622 lands; write the result entry; fill RQ_SUMMARY §6.3; re-run `report`.
