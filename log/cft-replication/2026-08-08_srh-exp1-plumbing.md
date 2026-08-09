### Target Date: 2026-08-08 (SRH Experiment 1 built; the budget accounting alone answers one hypothesis)

Second entry today. The first ([`2026-08-08_implement-cft.md`](2026-08-08_implement-cft.md))
built the `nikiema2025contrastive` replication; this one builds the follow-up that tests the
**Shared Representation Hypothesis** — does bidirectional training make `T` and `T⁻¹` share
internal representations, or does it just produce two disjoint one-way circuits? Plan:
[`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md) and the approved plan file.

- **Hypotheses / what we're testing:** Experiment 1 asks whether CFT's reverse capability comes
  from the contrastive *objective* or merely from the fact that contrastive training exposes the
  model to both directions. The paper never ran the obvious baseline: reverse training data is
  free here, because every `(original, obfuscated)` pair is also an `(obfuscated, original)` pair.
  - **E1-A:** `r(REV) > 0` — reverse is learnable at all on this corpus. **The kill-gate.**
    If it fails, every other arm's null is uninterpretable and the experiment stops.
  - **E1-B:** `r(MIX50) > 0` while `r(FWD) ≈ r(FWD2x) ≈ 0` — bidirectional *exposure* alone
    produces reverse capability at no extra budget on any axis. CONFIRM if MIX50's
    cluster-bootstrap CI excludes FWD's; REFUTE if the two are indistinguishable.
  - **E1-C:** `r(FLIP) > r(CFT)` — the contrastive objective is dominated.
  - **E1-D (answerable with no GPU, tested today):** "same data budget" is not a well-defined
    quantity, and once measured it reframes the comparison. CONFIRM if CFT's compute ratio
    against forward-only SFT exceeds FLIP's while its supervised-signal ratio is lower.

- **Setup:**
  - New package `src/obtune/srh/` — `prompts.py` (the `rev` training task and the symmetric
    system prompt), `dataset.py` (`flip_to_reverse`, `split_directions`, `common_program_subset`,
    `load_mixture`), `arms.py` (the arm registry), `budget.py` (four-axis accounting),
    `train.py` (a 30-line wrapper over `cft.train.main`).
  - Additive edits to `cft/`: `train.main` gained keyword-only `load_mixture` / `build_example` /
    `run_id_prefix` hooks and a config-driven `adapter_root`; `dataset.to_sft_records` and
    `train.measure_lengths` gained an optional `build_example`; `mutate.verify` gained
    `collect_rejects`. `cft.prompts` is untouched and its `template_sha256()` is unchanged
    (asserted by test).
  - Configs `configs/srh/train/{rev,flip,mix50,fwd2x,cftflip,flipsym}_qwen{1.5b,7b}_py.yaml`
    + `_base_srh.yaml`; `configs/srh/eval/e1_qwen{1.5b,7b}.yaml`.
    Script `scripts/srh/21_enqueue_e1_arms.py`.
  - Budget table: `results/srh/budget_qwen7b_python.json`, Qwen2.5-Coder-7B tokenizer,
    `max_seq_len` 2560, effective batch 64, 3 epochs (6 for `fwd2x`).
  - Verification: `pytest tests/` **315 passed**; `make check` OK (32 files, 98 919 rows, no H1
    labels, no H1 markers, splits disjoint); CPU `--dry-run` of `flip` and `mix50`; `--stub` eval.

- **Results:**

  **Four-axis budget, totals over training, ratios against forward-only SFT (`fwd`):**

  | arm | instances | supervised tok | sequence tok (∝FLOPs) | steps |
  |---|---|---|---|---|
  | `fwd` | 22 149 (1.00×) | 4 357 299 (1.00×) | 7 757 502 (1.00×) | 346 (1.00×) |
  | `rev` | 22 149 (1.00×) | 1 868 457 (**0.43×**) | 8 462 805 (1.09×) | 346 (1.00×) |
  | `flip` | 44 298 (2.00×) | 6 225 756 (**1.43×**) | 16 220 307 (2.09×) | 692 (2.00×) |
  | `mix50` | 22 149 (**1.00×**) | 3 111 417 (**0.71×**) | 8 110 485 (**1.05×**) | 346 (**1.00×**) |
  | `fwd2x` | 44 298 (2.00×) | 8 714 598 (2.00×) | 15 515 004 (2.00×) | 692 (2.00×) |
  | `cft` | 55 815 (2.52×) | 4 458 297 (**1.02×**) | 20 523 372 (**2.65×**) | 872 (2.52×) |
  | `cftflip` | 77 964 (3.52×) | 6 326 754 (1.45×) | 28 986 177 (3.74×) | 1 218 (3.52×) |

  **Per-task share of supervised tokens:**
  `fwd` gen 1.000 · `rev` rev 1.000 · `flip` gen 0.700 / rev 0.300 ·
  `mix50` gen 0.694 / rev 0.306 · `cft` gen 0.977 / pos 0.011 / neg 0.011 ·
  `cftflip` gen 0.689 / rev 0.295 / pos 0.008 / neg 0.008.

  **Mean supervised tokens per instance:** gen **196.7** · rev **84.4** · pos/neg **3.0**.

  - **MIX50 assembles exactly as designed:** 7 383 instances against `fwd`'s 7 383, split
    gen 3 688 / rev 3 695, direction-disjoint by `program_id` (asserted).
  - **`structural_recovery` calibration**, 200 Python programs: dispatch-loop detector fires on
    **200/200 S1** and on **9/200** of L0, S2 and L1r — the *same nine* programs in each, whose
    originals already contain a `while` loop comparing one variable against several constants.
    `structural_recovery` accepts the true original **95.5 %** of the time, the echoed obfuscated
    input **0 %**, and an empty stub **47 %**.
  - **Length filtering** at 2560 tokens: drop rate **0.014 %** for `flip`, p95 766, max 2858.
    Loss mask verified on real batches (`flip` 433 supervised of 4×431; `mix50` 442 of 4×397).
  - **Two config bugs caught before they ran** (see Observations).
  - Stage 1 enqueued at priority 61 — 4 arms at 1.5B, behind the RQ1 grid and the replication.

- **What worked / hypothesis verdict:**
  - ✓ **E1-D SUPPORTED, and it reframes the whole comparison.** CFT costs **2.65×** forward-only
    SFT's compute (and 2.52× its instances, 2.52× its steps) to add **1.02×** its supervised
    signal. FLIP costs **2.09×** compute to add **1.43×** — and all of the addition is on the
    target direction. **CFT is dominated on the compute-for-signal trade before a single GPU-hour
    is spent.** So the honest frame for Experiment 1 is not budget-matching but *dominance*: if
    FLIP beats CFT in reverse, no budget account rescues CFT.
  - **MIX50 delivers the matched arm the design needs.** Identical instances and optimizer steps
    to `fwd`, 1.05× its sequence tokens, and **0.71×** its supervised signal. Any reverse
    capability it shows was bought at a *discount*, which makes it a conservative test.
  - **The replication's guarantee survives.** `cft.prompts.completion_for` still raises for the
    reverse direction, `cft.prompts.TASKS` still excludes it, and `template_sha256()` is
    unchanged at `1013093…` — all three asserted by tests, not by comment.

- **Observations:**
  - **The reverse direction is much cheaper than estimated.** A reverse target averages **84.4**
    supervised tokens against a forward target's 196.7 — a ratio of 0.43, not the ~0.5 assumed
    when planning. Forward targets are inflated obfuscations (S1 runs ~3.4× the original's
    length); reverse targets are the compact original. This is why `rev` and `mix50` come in
    *below* `fwd` on supervised tokens while matching it on compute.
  - **Two silent config failures, caught by a test rather than by a run.** Generating the 7B
    configs by appending a second `train:` block produced valid YAML in which the later key wins
    — so `mix50_qwen7b` lost its `direction_mix` (it would have trained as plain FWD) and
    `fwd2x_qwen7b` lost `epochs: 6` (also plain FWD). Both would have trained without error and
    produced a null that read as a finding. `tests/test_srh_dataset.py` now checks every arm
    config against the `arms.py` registry, and a companion test asserts all arms share one recipe.
  - **My own budget accounting had the same class of bug.** The first table computed `steps` with
    epochs applied but `sequence_tokens` without, so `fwd2x` — whose entire purpose is to match
    FLIP's compute — reported 1.00× compute. All four axes are now totals over training.
  - **`reverse_success_paper` really is vacuous for S1**, as suspected: S1 preserves identifiers,
    so the readability clause is free and the criterion reduces to one CodeBLEU inequality on the
    primary condition. `structural_recovery` is the replacement, and it must never be reported
    alone — an empty stub passes it 47 % of the time, which is exactly why the evaluator reports
    `reverse_success_structural = structural ∧ exec`.
  - **The `limit: 300` fix changes the replication's own numbers, not just the follow-up's.**
    A stub run over 8 programs now yields exactly 8 × 5 × 2 = 80 generations, where before the
    per-condition program sets differed.

- **New questions / new hypotheses:**
  - **E1-E:** does FLIP's forward accuracy drop relative to FWD? MIX50 halves forward supervision
    at matched compute, so the forward-accuracy delta between them is the *price* of
    bidirectionality — a headline number in its own right, and one the paper never reports.
  - The `rev`-vs-`gen` supervised-token asymmetry (0.43×) means FLIP is not a symmetric arm in
    loss terms even though it is in instance terms. Worth checking whether reverse performance
    tracks reverse *token* share rather than reverse *instance* share.
  - `flipsym` exists but is untested: if the mechanistic phase finds disjoint representations
    under FLIP, we cannot yet tell "forward-only training destroys shared structure" from
    "the two directions arrived under two different system prompts".

- **Next Steps:**
  1. Stage 1 (queued, priority 61): 1.5B `rev`, `flip`, `mix50`, `flipsym` — ~5 GPU-h once the
     RQ1 grid and the replication drain. **Read `r(REV)` first**; if it is ~0, stop.
  2. Stage 2 needs the 7B replication arms (`sft`/`cft`), which are **still not enqueued** —
     Experiment 1 uses them as its FWD and CFT arms at the headline scale.
  3. Run the forgetting check (`python -m obtune.forgetting --suite l0 --adapter <arm>/final`)
     on every arm before believing any accuracy number — FLIP and REV train the model to emit
     whole source programs, the likeliest thing here to damage obtune's own task.
  4. Seed 42 on FWD/REV/FLIP/MIX50 before claiming any effect, and because the CKA noise floor
     in Phase 2 needs a second seed of FWD and FLIP.
