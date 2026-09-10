### Target Date: 2026-09-09 (all five panel models on disk; first gate read — Gemma-3-12B is NO-GO by the registered rule, and a third of its failures are a missing pair of quotes)
- **Hypotheses / what we're testing:** the gate rule frozen in `CLAUDE_SCRATCHPAD.md` before any
  read: a candidate enters the panel iff untuned **`format_fail` ≤ 0.15 on L0** and untuned L0
  accuracy sits in a band where a ±4-pt contrast is visible. Every read is REPORTED whatever the
  verdict. No gate touches X1 or H1.
- **Setup:** downloads ran as a `dev`-partition chain after the quota cleanup (385666 StarCoder2 →
  385667 Granite → 385668 CodeGemma). `scripts/preflight_panel.py` verifies every shard named in
  each weight index resolves: **starcoder2-15b 29.7 GB / 7 shards, codegemma-7b 15.9 GB / 4,
  granite31-8b 15.2 GB / 4** — with codellama-7b/13b/34b, llama31-8b, llama31-8b-base and
  gemma3-12b, **all eleven non-barred models are complete**. Quota after: 993.9 GB used, 106.1 GB
  headroom. Gate jobs: 385500 gemma3-12b (done), 388497 llama31-8b-base, 388499 starcoder2-15b,
  388500 codegemma-7b, 388501 granite31-8b.
- **Results — Gemma-3-12B-it, untuned, `basecheck_panel`, same held-out items as every panel read:**

  | | L0 | L1b | L1r | L2 | S1 | S2 |
  |---|---:|---:|---:|---:|---:|---:|
  | accuracy | **0.3335** | 0.2630 | 0.2731 | 0.2689 | 0.2678 | 0.2903 |
  | `format_fail` | **0.2796** | 0.2865 | 0.2856 | 0.2814 | 0.2719 | 0.2867 |

  CodeLlama-7b untuned on the same items, for scale: L0 **0.2569** (ff 0.1293), L1r 0.2072
  (ff 0.1371), S2 0.1932 (ff 0.1614).
- **What worked / hypothesis verdict:** **GEMMA-3-12B — NO-GO on the rule as written.**
  `format_fail` 0.2796 on L0 against a 0.15 threshold, and 0.27–0.29 on every other condition.
  The verdict is recorded as registered and is not re-specified after the fact.
- **Observations — what the failures actually are, which changes what the NO-GO means:**
  - The unparsable outputs are **bare, unquoted strings**: `cba`, `dcbabdc`, `dxcba` against a
    required literal `"cba"`. Mean length 15 chars for failures against 7 for successes; nothing
    resembling prose, refusal or truncation.
  - Quantified across all six gate cells (9,582 trials, 2,706 failures): **942 of the failures —
    34.8 % of them, 9.8 points of accuracy — are the gold value with its quotes missing.**
    This was computed as a DIAGNOSTIC; the grader is untouched, and CLAUDE.md §4 #5 forbids
    loosening it (a containment/substring grader is exactly what the 2026-06-09 audit refuted).
  - So Gemma-3's floor is a **literal-syntax convention, not capability**: it already beats
    CodeLlama-7b's untuned L0 by +7.7 points while losing ~10 points to quoting. The `formatonly`
    control — an adapter trained on the answer format alone — measured that repair as worth +1.84
    on CodeLlama, where the floor was half as large.
  - This is the Llama-3.1 gate (2026-09-04) again, in the other direction. There the NO-GO was
    "its whole margin IS format, so conditional on a well-formed answer it is weaker"; here the
    margin survives the format correction. The registered rule cannot tell those two apart, which
    is an argument about the rule, not a reason to bend it for this model.
  - **Decision deferred to the human, deliberately.** The precedent set on 09-04 is that a NO-GO on
    an untuned read does not settle a model's place, because the question that matters is the tuned
    ceiling; a reduced probe (`tuned_L0` only, ~22 min) answers it for ~1 GPU-hour. Which of NO-GO
    and the probe governs is a scope decision, and taking it silently after seeing the number is
    exactly the selection freedom the pre-registration exists to remove.
- **New questions / new hypotheses:** **H-gate-format** (opened, not run): a base model's
  `format_fail` predicts nothing about its tuned ceiling once the failures are a single learnable
  convention. CONFIRM if `tuned_L0(gemma3-12b)` reaches or beats `tuned_L0(codellama-7b)` = 0.4275
  on L0 despite failing the gate; REFUTE if it lands at or below the untuned conditional rate.
  A cheap and decisive test of the gate rule itself.
- **Next Steps:** four gates queued (388497 / 388499 / 388500 / 388501); `dl_datasets` resubmitted
  as 388502 after two hub-side breakages (see the entry's Setup note in the fetcher). Nothing
  trains until each model's gate is read and `preflight_panel.py` exits 0.
