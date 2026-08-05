### Target Date: 2026-08-05 (Week-1 kill-switch pilot)

- **Hypotheses / what we're testing:** The gate question from the design doc §6 — does LoRA
  tuning on output prediction under ONE obfuscation condition (L1b, adversarial renaming)
  produce gains that transfer, and in particular does anything reach the held-out obfuscator
  H1? Pre-registered predictions:
  - **H1a-trainable:** self-gain on L1b ≥ +5 pts with CI excluding 0. CONFIRM ⇒ the task is
    learnable at all; REFUTE ⇒ fix capacity or data before spending the grid.
  - **H1a (family structure):** transfer to the identifier family (L2) exceeds transfer to
    the structural family (S1).
  - **H1c (the discriminator):** Δ accuracy on H1 > 0 with CI excluding 0 ⇒ semantic
    invariance; Δ ≈ 0 ⇒ transform memorization.
  - **H2c (conditioning vs capability):** if prompt-only oracle conditioning recovers ≥50 %
    of the tuning gain, the failure is conditioning, not capacity.

- **Setup:**
  - Corpus: `scripts/02_build_corpus.py --language python --workers 48` → **2,231 programs**
    (APPS call-based + CruxEval + HumanEval; 3,668 raw → 3,664 normalized → 2,720 static-filtered
    → 2,260 with usable cases → 2,231 after dedup vs the test set). Then
    `05_build_variants.py --target train` and `06_emit_pairs.py` → **38,343 SFT pairs**.
  - Test set: `01_ingest_testset.py` (70 L0 parents, 350 byte-identical legacy rows) →
    `05_build_variants.py --target testset` → `gen_h1_quarantined.py` → `07_emit_eval_items.py`
    → **2,052 eval items**.
  - Train: `CUDA_VISIBLE_DEVICES=2 python -m obtune.train_sft --config train/pilot_qwen1.5b_l1b.yaml`
    — Qwen2.5-Coder-1.5B-Instruct, LoRA r=32 α=64 on q,k,v,o+gate,up,down, bf16, seq 1536,
    effective batch 64, lr 1e-4 cosine, 3 epochs, seed 17. 297 steps, 2,357 s. Truncation 0 %.
    train_loss 0.4555, eval_loss 0.8119, eval token-accuracy 0.778.
  - Checkpoint selection (`--mode ckpt-select`, held-in val EM): ckpt-99 0.339, **ckpt-198 0.378**,
    ckpt-297 0.345, final 0.351 → `best -> checkpoint-198`. Epoch 2 wins, as the design's
    early-stop rule anticipated.
  - Eval: `CUDA_VISIBLE_DEVICES=3 python -m obtune.eval_vllm --config eval/pilot_w1.yaml`
    (vLLM 0.26.0, greedy, max_tokens 64), 28 cells = 4 systems × 7 conditions.
  - Analysis: `python -m obtune.trial_table` → `python -m obtune.pilot --model Qwen2.5-Coder-1.5B`.
    23-program common subset, 99 items/cell, 2,772 trials, cluster bootstrap over `program_id`,
    2,000 resamples, seed 17.
  - GPUs 2 and 3 (0 and 1 were another user's). Commit at run time: `6887f57`.
  - H1 read once with `purpose=pilot_eval`; appended to `data/quarantine/h1/ACCESS_LOG.md`.

- **Results:** accuracy on the common subset —

  | system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
  |---|---|---|---|---|---|---|---|
  | base | .253 | .242 | .202 | .202 | .323 | .212 | **.111** |
  | oracle prompt | .232 | .313 | .202 | .192 | .263 | .253 | .081 |
  | oracle prompt + 1-shot | .475 | .333 | .323 | .333 | .323 | .343 | .192 |
  | **tuned on L1b** | **.545** | **.515** | **.576** | **.535** | **.475** | **.495** | **.384** |

  Gates: self_gain **+27.3** pts CI [11.0, 43.2] (≥5 ✅) · format_fail **1.0 %** (<2 % ✅) ·
  forget_L0 **+29.3** pts CI [14.0, 44.9] (>−3 ✅) · cond_recovery **0.333** (1-shot) /
  **0.259** (bare) — inconclusive band · **h1_delta +27.3 pts CI [16.1, 40.9], excludes 0** ·
  h1 gain beyond 1-shot oracle **+19.2** pts · transfer_L2 **+33.3** > transfer_S1 **+15.2** ✅.
  All 7 cells significant under BH-FDR at .05. TR undefined for all 6 off-diagonal cells
  (denominator guard: no `tuned_j` exists for j ≠ L1b in a single-adapter pilot).

- **What worked / hypothesis verdict:**
  - **H1a-trainable — SUPPORTED.** +27.3 pts, CI excludes 0.
  - **H1a (family structure) — SUPPORTED.** Identifier-family transfer (L2 +33.3) is more
    than double structural-family transfer (S1 +15.2), the direction predicted.
  - **H1c — provisionally SUPPORTED, with a caveat that outranks the result.** H1 rose
    +27.3 pts with a CI excluding zero, and the 1-shot oracle — which also teaches the answer
    format — recovers only +8.1, leaving +19.2 pts that prompt-level conditioning does not
    explain. But L0 also rose +29.3 pts, i.e. *as much as H1*. That is the signature of the
    model learning **the task** (output prediction, answer format) rather than obfuscation
    robustness specifically. Until the L0-trained control adapter exists, "invariance" and
    "task acquisition" are not separated, and I am not willing to call H1c settled.
  - **H2c — INCONCLUSIVE by design.** 0.26–0.33 sits in the band the design reserved for
    running both arms. Conditioning is real but partial; the RQ2 oracle comparison stays a
    headline arm.
  - **Verdict: PROCEED to the full arc.** No gate failed.

- **Observations:**
  - The base model is weak at the task itself (L0 .253), and its format-failure rate is
    strongly condition-dependent: 21.2 % on H1 versus 0–8 % elsewhere. Tuning collapses that
    to ~1 % everywhere. So a real part of every gain is "learned to answer in the required
    form on weird-looking code". The `raw_exact` grading-sensitivity column exists for exactly
    this and should be reported in the paper.
  - S1 is the outlier in the other direction: the highest BASE accuracy (.323) and the lowest
    transfer (+15.2). Flattened code is verbose but locally simple to trace, whereas
    adversarial names actively mislead — consistent with the two distinct failure routes
    Paper 2 identified (atom-level interference vs relational overload).
  - The bare oracle prompt *hurt* on H1 (.111 → .081). Telling a model that code is
    "string-encoded with MBA rewriting" without showing it what that looks like appears to be
    worse than saying nothing.
  - Coverage at scale: S1 reached only 74 % of training programs (1,655/2,231) versus ~99–100 %
    for every other condition, and the all-conditions common subset is 1,630/2,231 (73 %).
    On the 70-program test set the common subset is 33/40 Python and 30/30 JavaScript. The
    headline-numbers-on-the-common-subset rule is doing real work, not hypothetical work.
  - H1 eligibility is literal-density-bound: 27/40 Python and 24/30 JavaScript test parents
    could be H1-transformed at all.

- **New questions / new hypotheses:**
  - **The control that matters most now: an L0-trained adapter.** If tuning on *clean* code
    lifts H1 by roughly the same +27 pts, then the pilot measured task acquisition and the
    invariance claim collapses. If the L0 adapter lifts H1 markedly less than the L1b adapter
    does, invariance survives. This should run before anything else in the grid.
  - Is the +19.2 pts "beyond conditioning" stable when the oracle demo is drawn from the same
    condition as the eval (a stronger oracle)?
  - Does S1's low transfer persist for an S1-trained adapter (i.e. is flattening simply
    harder to learn), or is it specific to transferring *from* a rename adapter?
  - Data scaling (8k vs 24k) and seed variance were deferred; both re-parameterize the grid
    and are cheap on the 1.5B.

- **Next Steps:**
  1. Train the **L0 control adapter** and re-run the H1 column — the single highest-value run.
  2. Add the seed-42 repeat and the 8k data-scaling arm on the 1.5B before committing grid compute.
  3. Pre-register H1a–H3 (OSF) now that the pilot has shown the measurement works; the pilot
     stays labelled `phase=pilot` and exploratory.
  4. Build the JavaScript corpus so the cross-language arm (H1b) becomes runnable.
