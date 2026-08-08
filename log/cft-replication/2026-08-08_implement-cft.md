### Target Date: 2026-08-08 (Implement the CFT replication; data layer built, arms queued)

- **Hypotheses / what we're testing:** Setup day for a new thread, plus one hypothesis that
  turned out to be answerable with no GPU at all.
  - **C5 (testable from the data layer alone):** the paper's `L_CFT = L_pos + L_neg + L_gen`
    (eq. 5) is not a three-way balanced objective, because it balances pools by *instance
    count* while a `gen` target is a whole program and a `pos`/`neg` target is one token.
    CONFIRM if the measured `gen` share of supervised tokens exceeds 0.95; REFUTE if the three
    shares are comparable.
  - **C1–C4** (cognitive specialization reproduces; CFT recovers the reverse direction; any gain
    is renaming-only; prompting cannot substitute) are stated in
    [`README.md`](README.md) and need the trained arms. Not tested today.

- **Setup:**
  - Paper: `papers/nikiema2025contrastive.pdf` (arXiv:2509.05553). Design + full deviation list:
    [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).
  - New code: `src/obtune/cft/{__init__,prompts,mutate,dataset,metrics,train,evaluate}.py`;
    configs `configs/cft/{data_v1.yaml,train/*.yaml,eval/*.yaml}`;
    scripts `scripts/cft/{10_build_cft_data,11_enqueue_arms,12_report}.py`;
    tests `tests/test_cft_{prompts,mutate,dataset,metrics}.py`.
  - CodeBLEU: `codebleu==0.7.0` vendored to `env/vendor/` (project-local; `env/lock-obtune.txt`
    untouched). Its tree-sitter 0.22 pin was deliberately NOT vendored — it shadows the 0.26
    grammars `obf/base.py` needs — so `metrics.py` *appends* the vendor dir to `sys.path`.
  - Data build: `python scripts/cft/10_build_cft_data.py --config cft/data_v1.yaml`, seed 17,
    CPU only, ~14 min wall clock (48 executor workers, 96-core host, no GPU used).
  - Dry run: `python -m obtune.cft.train --config cft/train/cft_qwen1.5b_py.yaml --cpu --dry-run`.
  - Stub eval: `python -m obtune.cft.evaluate --config cft/eval/bidir_v1.yaml --stub --limit 6`.
  - Verification: `make check` OK (manifests rebuilt to include the new files; 32 files,
    98 919 rows, no H1 labels, no H1 markers, splits disjoint); `pytest tests/` 280 passed.

- **Results:**
  - **Instance pools** (`data/train/cft/<lang>/`), train+val splits, conditions L1b/L1r/L2/S1/S2:
    | language | gen | pos | neg | programs |
    |---|---|---|---|---|
    | python | 7 912 | 7 912 | 6 021 | 1 674 |
    | javascript | 2 522 | 2 522 | 1 857 | 506 |
    Paper's scale for comparison: 10 000 per task, 30 000 total.
  - **Negative-mutation program coverage** (share of programs that yielded an
    execution-verified semantics-altering mutant), Python:
    L1b .814 · L1r .816 · L2 .816 · S1 .844 · **S2 .537**.
  - **S2's rejection profile is an outlier:** 6 070 candidates rejected as *equivalent
    mutants* under S2, against ~430 under each identifier condition.
  - **Per-condition label prior, before the fix:** P(YES | S2) = **0.651** vs 0.542–0.551 for
    every other condition; pooled 0.568. After pairing: **0.500 in every condition**, pooled
    0.500. Paired Python mixture: gen 7 912 · pos 6 021 · neg 6 021 = 19 954.
  - **C5 measurement** (Qwen2.5-Coder tokenizer, paired Python train mixture, n = 18 605):
    `task_token_share` = **gen 0.977 · pos 0.0113 · neg 0.0113**;
    mean supervised tokens/instance = gen 196.7 · pos 3.0 · neg 3.0.
  - **Instance upsampling cannot repair that:** equal token mass with all `gen` kept needs
    ~484 000 instances of each classification task (86x), i.e. a ~976 000-instance mixture at
    ~15 200 optimizer steps/epoch — ~50x the SFT arm's cost.
  - **Length filtering** at `max_seq_len` 2560: drop rate **0.016 %** (3 of 18 608), p95 775
    tokens, max 2846. Loss mask verified on a real batch: shape (4, 601), 59 supervised tokens.
  - **Readability-proxy calibration** over 400 Python programs and their L2 variants: short-name
    ratio L0 mean .239 / p95 .500 versus L2 mean .663 / p05 .429. Operating points (share
    flagged as minified) — threshold 0.4: L0 17.2 % / L2 97.8 %; threshold **0.5**: L0 8.0 % /
    L2 89.0 % (max TPR − FPR); threshold 0.6: L0 3.0 % / L2 70.8 %. Set to 0.5.
  - **Condition-ordering sanity check** of the metrics on 60 Python programs (mean):
    | | R (proxy) | identifier_meaning | CodeBLEU(obf, orig) | identifier_recall |
    |---|---|---|---|---|
    | L0 | .818 | .815 | 1.000 | 1.000 |
    | L1b | .938 | .976 | .556 | .403 |
    | L1r | .580 | .341 | .556 | .389 |
    | L2 | .435 | .243 | .501 | .438 |
    | S1 | .810 | .748 | .556 | 1.000 |
    | S2 | .930 | .944 | .718 | 1.000 |
  - **Stub evaluation, before the non-code guard:** the placeholder string `<stub:a1b2c3>`
    scored **17.2–24.1 % `reverse_success_paper`** across the four prompting strategies. After
    the guard: **0.0 %** everywhere.
  - Both 1.5B arms enqueued at priority 60 (`runs/manifest/queued/cft__qwen25c-1.5b__python__{sft,cft}__s17.json`).
    Not yet run — all 4 GPUs busy (rank sweep on 0–1, `allocation_replication` RQ1 matrix on 2–3).

- **What worked / hypothesis verdict:**
  - ✓ **C5 SUPPORTED.** `gen` carries **0.977** of the supervised-token mass, far above the 0.95
    threshold. The paper's "balanced triplet datasets" balances instances, not loss, so
    `L_CFT = L_pos + L_neg + L_gen` is in practice ≈ `L_gen` plus a 2 % perturbation. This
    was established from the data layer and a CPU dry run, before any GPU time.
  - **Execution-verified negatives work.** 81–84 % of programs yield a hard negative under the
    identifier and S1 conditions — single-token edits that still run and provably differ.
  - **Pairing pos/neg removes the label shortcut exactly**, not approximately: every condition
    lands at P(YES) = 0.500.
  - **The stub run earned its keep.** It is the only reason we know the paper's reverse-success
    criterion, taken literally, awards ~20 % to output that is not code.

- **Observations:**
  - **S2's equivalent-mutant rate is a measurement, not a nuisance.** 6 070 rejections versus
    ~430 elsewhere says most of what S2 inserts is semantically inert — which is precisely what
    "opaque predicates and dead code" is supposed to mean. The mutation harness independently
    confirms the S2 transform does what `configs/conditions.yaml` claims. The cost is fewer S2
    negatives, which is what created the label imbalance.
  - **The paper's reverse-success criterion is satisfiable by non-code.** As written (§4.3.2) it
    is two inequalities: similarity to the obfuscated input below a threshold, and readability
    restored. An empty string satisfies the first perfectly. We added a `parses` precondition;
    it can only lower a reported number, never manufacture one. Worth flagging in any writeup:
    the paper's 0 % SFT figure is unaffected (0 stays 0), but its 39–52 % CFT figures rest on a
    criterion with no validity gate.
  - **Readability cannot see adversarial renaming.** L1b scores R = .938, *above* L0's .818,
    because misleading names are well-formed English. `identifier_recall` catches it (.403).
    Any readability-only reverse criterion is blind to the L1b family — a metric-level echo of
    `guzman2026poisoned`'s finding that misleading identifiers survive deobfuscation.
  - The first readability calibration inverted L2 entirely (`identifier_meaning` = 1.00 for
    fully-minified code) because single letters sat on an idiomatic whitelist. Fixed by deciding
    "short names are idiom" per *program*, from the share of short names, rather than per token.
  - `verify_rate` in the mutation stats is per-*proposal* and deflated by design (verification
    stops once a program has its quota). `program_coverage` is the number to read; both are
    reported now so the trap is visible rather than latent.

- **New questions / new hypotheses:**
  - **C6 (new, from C5):** is a null CFT result attributable to the objective's weighting rather
    than to contrastive supervision itself? Cannot be answered with `task_weights` — see the
    86x arithmetic above. It needs a per-task loss coefficient in a custom `compute_loss`, which
    is *our* variant and not a replication of the paper. Only worth building if C2 comes back null.
  - **C7:** does the paper's own `clean_mutant` negative construction measurably differ from our
    `obfuscated_mutant` one? One extra arm turns "their design has a shortcut" from an argument
    into a measurement.
  - How much does the `parses` guard change a *real* model's reverse numbers, as opposed to the
    stub's? Report both gated and ungated `reverse_success_paper` on the first real run.

- **Next Steps:**
  1. Wait for the queue. Both 1.5B arms sit at priority 60, behind the RQ1 grid (90 jobs,
     ~21 GPU-h) — deliberately, so a replication of someone else's paper does not preempt the
     project's own experiments.
  2. When they land: `python -m obtune.cft.evaluate --config cft/eval/bidir_v1.yaml --gpu <idle>`
     then `python scripts/cft/12_report.py results/<date>_cft-bidirectional/python`.
  3. Treat 1.5B strictly as a pipeline check. The headline number runs on `qwen25c-7b`
     (`configs/cft/train/{sft,cft}_qwen7b_py.yaml`) — the paper's own "QwenCoder" row, 39.00 %
     reverse under CFT — because the paper reports an architectural capacity hierarchy and a
     null at 1.5 B would be uninformative.
  4. Vary the seed before believing any arm difference (CLAUDE.md §4: one run is a data point).
