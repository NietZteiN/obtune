### Target Date: 2026-09-07 (revised RQs adopted; end-to-end pipeline for everything planned)
- **Hypotheses / what we're testing:** An organisational/setup day. The user adopted the revised
  spine RQ1′–RQ4′ (`docs/RQ_SUMMARY.md` §6) and asked for "an end to end autonomous pipeline to run
  everything". The falsifiable content is the **pre-registration block** in `CLAUDE_SCRATCHPAD.md`
  ("REVISED RQs … PIPELINE PRE-REGISTRATION"), frozen before any submission: RQ-A/RQ-B at 13B/34B,
  RQ-C (depth 3/4), H-sat-L0 / H-sat-mono / H-tax-scales, H-family-unit / H-whole-ge-parts, H-E3 /
  H-E3-tax, H-E4-view / H-E4-teacher / H-E4-mono, H-E8 / H-E8-seen / H-E8-tax, H-attn-cons /
  H-attn-breadth, plus the REPORTED-only FDR and L0-cost analyses. No stage reads H1.
- **Setup:**
  - `scripts/pipeline/plan.yaml` — 47 stages over four RQs; `scripts/pipeline/run.py` (existing)
    submits them as `afterok`/`afterany` SLURM chains from a topological sort, records job ids in
    `runs/pipeline/state.json`, and treats `done_when` files as the idempotency key.
    `scripts/pipeline/report.py` assembles every `an_*` stage's JSON into
    `results/analysis/pipeline_report_<date>.md`; a missing JSON prints PENDING, never a number.
  - New configs: `eval/{composite_scale,composite_depth,x1_split,objectives_teacher,objectives_llama,saturation}.yaml`;
    `train/{grid_py_X1m,grid_py_X1s,obj_cons_tbase_codellama7b_py,obj_cons_tmono_codellama7b_py,obj_cons_llama31_8b_py}.yaml`.
  - New analysis: `scripts/analysis/cellkit.py` (shared cell loader — raises on H1 — bootstrap,
    BH, result schema) and `36_cons_arms.py`, `37_fdr_family.py`, `38_l0_cost.py`, `39_x1_split.py`,
    `40_saturation.py`, `41_attention_x1.py`; `35_composites.py` gained `--composites/--common/--ref-json`
    for the depth leg. All smoke-tested against existing cells before submission.
  - Corpus: X1m / X1s registered in `conditions.yaml`, `schema.py`, `obf/builder.py`, `obf/py/x1.py`,
    `paths.TRAINABLE_CONDITIONS`; depth-3/4 codes in `conditions_composite.yaml` and `schema.py`.
  - Resources: gpu stages h200 × 1, 2–7 h; cpu builds `normal` 16 cores; analysis `normal` 4 cores.
    Requested GPU walltime ≈ 45 h. External (hand-submitted) E3 jobs referenced as `ext:`:
    382139/382140 (13B ckpt-select + eval, done), 382141/382142 (34B, pending on 381405).
- **Results:** No new numbers today from the pipeline itself. `run.py --dry-run` resolves the full
  DAG (47 would-submit, 0 skipped after the dry-run placeholder fix); 382140 `ev_cons13b` completed
  in 316 s so the 13B half of E3 is ready for `an_e3` as soon as 34B lands.
- **What worked / hypothesis verdict:** N/A (setup). Verdicts arrive in
  `results/analysis/pipeline_report_<date>.md` and get their own dated entries per thread.
- **Observations:** (i) `run.py --dry-run` originally skipped every dependent stage as
  "unsubmitted" because only a real submit writes a job id — fixed by giving dry-run a `DRY:<name>`
  placeholder that is never saved. (ii) E5b (hard second family) and E10 (human alignment) are
  **disabled stages with a stated reason**, not silently absent: the first has no generator, the
  second has no tier_icse items and no script. (iii) `37_fdr_family` substitutes a program-cluster
  bootstrap p for the GLMM because neither statsmodels nor the R stack is installed on juno; it is
  labelled as such and gates nothing. (iv) `05_build_variants --dry-run` still builds everything
  before declining to write, so it is not a cheap check; the two corpus builds run as 6–8 h CPU jobs.
- **New questions / new hypotheses:** whether the strict `cons_lam3 > mono_all` reading on
  composites (grazing zero at 7B) resolves at 13B/34B is now RQ-B's scale leg, inside RQ1′/RQ3′.
- **Next Steps:** commit + push, `run.py` (submit), `run.py --status` daily; when the 34B chain
  finishes, `an_e3` fires automatically → write the transfer entry and master report rev 18.
