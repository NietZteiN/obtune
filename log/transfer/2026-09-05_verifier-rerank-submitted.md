### Target Date: 2026-09-05 (lever 2b — trained verifier / best-of-n reranker, submitted)
- **Hypotheses / what we're testing:** The self-consistency read
  ([`2026-09-04_self-consistency-and-seed-band.md`](2026-09-04_self-consistency-and-seed-band.md))
  left a 10–16 pt gap between `tuned_L0`'s greedy accuracy (0.43) and its any-of-8 (0.53–0.59)
  while plurality vote sat *below* greedy. So the correct answer is usually in the sample set and
  the model's own agreement cannot find it. Two falsifiable claims, no RL (user excluded lever 4):
  - **H-verifier:** a LoRA trained to answer *yes/no* on (prompt, candidate) pairs sampled from
    `tuned_L0` itself picks the right candidate more often than greedy. CONFIRM if
    `verifier − greedy` on heldout is > 0 with the program-cluster CI excluding zero **and** it beats
    both likelihood controls; REFUTE if it sits inside the CI of greedy or under the controls.
  - **H-self-judge (the control that says what a positive means):** the *untuned* base asked the
    same yes/no question already ranks candidates as well as the trained verifier. If base ≈
    trained, the model can judge but not pick — the "know how, not when" reading again; if
    trained ≫ base, the verifier learned something the generator does not expose.
  - Zero-training controls: rerank by cumulative log-prob and by per-token log-prob.
- **Setup:**
  - `scripts/28_sample_candidates.py --model codellama-7b --adapter runs/adapters/codellama-7b/python/L0_r32_s17/best --tag tuned_L0 --split {heldout,val,train} --n 8`
    (T 0.7, top_p 0.95, seed 17, max_tokens 64, stop `\n\n`/```; plus one greedy row as
    `sample_idx = −1`; every row graded with `scoring.grade` and stamped with vLLM's
    `cumulative_logprob`). Trainable conditions only — the script refuses H1. Jobs `cand_heldout`
    377858, `cand_val` 377859, `cand_train` 377860 (h200). Output `runs/candidates/codellama-7b/tuned_L0/*.parquet` (gitignored).
  - `src/obtune/verifier.py`: the generator's own prompt (`prompts.build_prompt`, unchanged) +
    the candidate as the assistant turn + `Is the return value above exactly correct? Answer yes
    or no.` → one-token completion. Verifier version `v1`.
  - `scripts/29_train_verifier.py --config train/verifier_generic_py.yaml --model codellama-7b`:
    r32 LoRA (same targets as `_base_lora`), 2 epochs, lr 1e-4, 16×4, dedup on
    `(item_id, pred_norm)`, class-balanced by downsampling, cap 40k rows, val 1000; completion-only
    loss; adapter `runs/adapters_verifier/codellama-7b/python/tuned_L0_r32_s17/`. Job `tr_verif`
    377861 (afterok 377859, 377860).
  - `scripts/30_rerank.py --model codellama-7b --candidates-tag tuned_L0 --adapters none --adapter-root <verifier dir>`:
    scores every *distinct* candidate (greedy included) with logsumexp P(yes-tokens) − logsumexp
    P(no-tokens) at the first generated position (vLLM, max_tokens 1, logprobs 20) under each epoch
    checkpoint, `final`, and the untuned base; selectors greedy / vote / logprob / logprob_norm /
    verifier:* / any_of_n; program-cluster bootstrap (B = 2000, seed 17) of each selector − greedy
    per condition; checkpoint chosen on **val** rerank accuracy, heldout reported for all. Job
    `rerank` 377862 (afterok 377858, 377861) → `results/analysis/rerank/codellama-7b/tuned_L0/rerank_report.json`.
  - Commit `c0403c1`.
- **Results:** none yet — all five jobs pending on h200 (queue ~25 obtune jobs deep).
- **What worked / hypothesis verdict:** pending.
- **Observations:** The selfcons parquets store only summary columns, so the sample sets had to be
  regenerated; 28 stores them, which also makes the sampled answers auditable (grader FP check on
  the candidates is a follow-up). H1 is never sampled, so no candidate, verifier or selector ever
  sees the held-out family; the H1 read of a verifier-reranked system is part of the campaign-end
  `final_eval` batch only if the verifier wins on the trainable grid.
- **New questions / new hypotheses:** if H-verifier holds, does it also lift `mono_all` and the
  breadth adapters, or only the specialist whose samples it was trained on? (Rerank is cheap; the
  sampling is one job per system.)
- **Next Steps:** read 377862; if positive, sample from `mono_all` and the trace arm and rerank with
  the same verifier (transfer of the judge), then decide the campaign winner on the trainable grid.
