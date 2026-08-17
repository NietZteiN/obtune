### Target Date: 2026-08-17 (does substituting the readability model change any result?)

Second entry for this thread today; the first is
[`2026-08-17_attrib-v2-and-determinism.md`](2026-08-17_attrib-v2-and-determinism.md).

- **Hypotheses / what we're testing:** Formalising the metrics for the ATTRIB draft surfaced an
  undisclosed deviation. Eq. (1) of the paper, the reimplementation of
  `nikiema2025contrastive`'s reverse-success criterion, contains a readability conjunct
  $R(\hat y) \ge R(x) - 0.1$. The original measures $R$ with Scalabrino et al.'s comprehension
  model; we use `metrics.readability_proxy`, a weighted proxy. A substituted measure inside a
  reimplemented criterion is exactly the kind of deviation that can carry a result silently.
  - **H-R1:** the substitution is load-bearing. CONFIRM if varying the readability treatment
    moves strict reverse success enough to change a reported contrast; REFUTE if strict success
    is insensitive to it.

- **Setup:** No GPU, CPU only, recomputed from `trials.jsonl` already on disk. Run read:
  `results/2026-08-10_cft-bidirectional/qwen25c-7b/python/e2_budget_qwen7b/`, reverse direction,
  `simple` strategy, 10 500 trials, 1 500 per arm. Four treatments of the conjunct were
  compared: tolerance 0.1 (what the paper reports), the term removed entirely, tolerance 0.0
  (strictest) and tolerance 0.3 (loosest). Recomputation reused the row fields
  `parse_ok`, `codebleu_other`, `readability_pred`, `readability_original` and `exec_status`,
  so the only thing varying is the conjunct.

- **Results:** strict reverse success (%), 7B.

  | arm | tol 0.1 (reported) | term removed | tol 0.0 | tol 0.3 | spread |
  |---|---|---|---|---|---|
  | `base` | 12.9 | 13.5 | 10.6 | 13.5 | 2.9 |
  | `sft` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
  | `cft` | 0.1 | 0.1 | 0.0 | 0.1 | 0.1 |
  | `fwd2x` | 0.1 | 0.1 | 0.0 | 0.1 | 0.1 |
  | `rev` | 32.9 | 32.9 | 32.1 | 32.9 | 0.8 |
  | `flip` | 33.5 | 33.6 | 32.3 | 33.5 | 1.3 |
  | `mix50` | 32.8 | 33.0 | 31.9 | 33.0 | 1.1 |

  Dropping the conjunct entirely changes no arm by more than **0.6 pp** and changes the
  `mix50` − `sft` contrast by **0.2 pp**. The conjunct is the deciding factor on **0.2 %** of
  trials for `flip`/`mix50` and **1.0 %** for `base`.

  The *published* criterion (same test without the execution term) is more exposed, spreading
  1.1–1.9 pp on the trained arms but **17.6 % to 24.3 %** on `base`.

- **What worked / hypothesis verdict:** **H-R1 REFUTED for every claim the paper makes.**
  Strict reverse success is insensitive to the readability measure, because once an output must
  parse, sit below the CodeBLEU bound against the obfuscated input, *and* execute to the
  original's outputs, it is essentially always at least as readable as the original on any
  reasonable scale. Execution and the similarity bound do the deciding; readability is nearly
  redundant with them.

  The one quantity with real exposure is the **untuned model's published-criterion rate**
  (17.6–24.3 % across treatments). The paper places no claim on that number, and this is now
  stated rather than left implicit.

- **Observations:**
  1. This inverts how the deviation should be written up. The draft had an apologetic hedge
     ("not their scale, so read our numbers comparatively"), which invites a reviewer to wonder
     how much it matters. It now carries the measurement instead, with the sensitivity table in
     Appendix A. A bounded deviation is stronger than an acknowledged one.
  2. It also retro-justifies a design choice. `readability_proxy` returns **0** for a
     non-parsing output rather than a middling value, which is what stopped the stub run from
     scoring 17–25 % "reverse success". That guard matters far more than the proxy's exact
     weights, and the sensitivity table is why we can now say so with numbers.
  3. Obtaining Scalabrino et al.'s model was not attempted and is not needed for the
     conclusions, given the above. It would only refine `base`'s published-criterion rate,
     which is not load-bearing.

- **New questions / new hypotheses:**
  - **H-R2:** the same redundancy argument should apply to the CodeBLEU threshold of 0.4, which
    is the other borrowed constant in Eq. (1). Sweeping it is the same zero-GPU recomputation
    and would close the last free parameter inherited from the original criterion. CONFIRM if
    strict success is flat over a threshold range of roughly 0.3 to 0.5; REFUTE if any reported
    contrast moves.

- **Next Steps:**
  1. Sweep the CodeBLEU threshold per H-R2, same method, no GPU.
  2. Remaining ATTRIB items are unchanged: pick a title consistent with the reframe, and decide
     whether to run the 7B paired-statistics pass for §5.
