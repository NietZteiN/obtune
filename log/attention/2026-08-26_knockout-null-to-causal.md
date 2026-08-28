### Target Date: 2026-08-26 (the knockout: a null, a manipulation check, and a causal result)

- **Hypotheses / what we're testing:** The 2026-08-18 sweep found `tuned_S2_s17` re-anchors
  attention off identifiers onto control/dataflow on the `S2` condition by +0.111 [+0.093, +0.131],
  2.6x the clean-code control and specific to `S2`. That is a correlation; CLAUDE.md §3 requires an
  intervention before any causal claim. Predictions were fixed in
  `scripts/attn/30_knockout.py`'s docstring BEFORE each arm ran:
  - **H1.** Suppressing attention to identifier keys should cost `tuned_S2_s17` LESS than it costs
    `base` on `S2` — the adapter already attends less to them, so removing them takes away less it
    was using.
  - **H2 (the falsifier).** On `L1r`, every adapter shifted attention TOWARD identifiers, so
    knockout should cost the adapters MORE than `base` — the opposite sign. A mechanism that only
    ever predicts "less damage" would be unfalsifiable.

- **Setup:** Host `csr-94608`, GPUs 0 and 2 (1 and 3 held by a neighbour throughout;
  `gpu_budget` 4 -> 3 on the user's instruction). Qwen2.5-Coder-1.5B, LoRA r32 s17, eager attention.
  150 items per cell from Grid A `heldout`. `KnockoutSpec(bias=-1e4)` — a hard mask, not a nudge.
  22 jobs across three rounds (accuracy knockout, manipulation check, log-prob readout), 0 failures.
  **No quarantined item was read at any point.**

- **Results:**

  **Round 1 — accuracy knockout (8 cells).** Damage = clean − knocked, in accuracy points:

  | cond | base | tuned_L0 | tuned_L1b | tuned_S2 |
  |---|---|---|---|---|
  | S2 | −0.7 | +2.7 | +2.0 | −0.7 |
  | L1r | 0.0 | +2.0 | +0.7 | −2.7 |

  Whole table inside −2.7..+2.7, i.e. ±4 items on 150 against a 3.61-pt seed band. H1 not confirmed
  (`tuned_S2` tied with `base`); H2 mixed.

  **Round 2 — manipulation check (6 cells + 2 all-layer).** Suppress classes the task provably needs:

  | suppressed | layers | keys | accuracy damage (base) |
  |---|---|---|---|
  | all 6 classes | 28 | 372 | **+2.7** |
  | all 6 classes | 6 | 372 | −2.0 |
  | literal | 6 | 49 | −1.3 |
  | dataflow_critical | 6 | 40 | −2.0 |

  Direct verification of the hook: attention mass at masked keys 0.0072/0.0247/0.0284 (layers
  4/14/27) -> **0.0000**. Output agreement clean vs knocked: **32 %** identical at 28 layers, 62 % at
  6 layers.

  **Round 3 — log P(gold) readout (6 cells).** Sensitivity control: all-6-classes/28-layers costs
  `base` **−1.590** nats, `tuned_S2` **−2.544**. Identifier knockout on `S2`, bootstrapped by
  program (50 programs):

  | system | Δ logP | 95 % CI |
  |---|---|---|
  | `base` | **−0.0892** | [−0.1578, −0.0230] |
  | `tuned_L1b_s17` | −0.0624 | [−0.1254, −0.0057] |
  | `tuned_L0` | −0.0321 | [−0.0819, +0.0187] |
  | `tuned_S2_s17` | **+0.0145** | [−0.0515, +0.0880] |

  Paired vs `base` (positive = less harmed): `tuned_S2` **+0.1037 [+0.0109, +0.2085] SIG**;
  `tuned_L0` +0.0571 [−0.0225, +0.1358] null; `tuned_L1b` +0.0269 [−0.0502, +0.1102] null.

- **What worked / hypothesis verdict:**
  - **H1 SUPPORTED, on the log-prob readout.** Not on accuracy, and the reason is a floor, not a
    failure — see Observations.
  - **H2 remains untested.** The `L1r` contrast masks only **17** keys against `S2`'s 132, because
    `v_a3f2`-style names are largely not classified as identifiers. The falsifying cell barely
    intervenes, so its null says nothing. This is a design flaw in my contrast, not a result.

- **Observations:**

  **The accuracy null was a floor effect, and it took a manipulation check to find that out.**
  Blinding the model to every code token in every layer changed accuracy by 4 items in 150 — but
  changed 68 % of its outputs, with a monotone dose-response in layer count. The intervention was
  always working. `base` sits at ~22 % on obfuscated `S2`, close enough to guessing that scrambling
  its input changes WHICH answers it emits and not how often they land. A binary hit/miss has no
  headroom there. Log-probability has none of that: continuous, no floor, defined on items the model
  gets wrong, and it measures the quantity the claim is about.

  **Two of my own diagnoses were wrong and both were caught by measurement, not reasoning.** I
  declared the instrument broken (it zeroes attention exactly), then blamed layer coverage (28
  layers gave +2.7 against 6 layers' −2.0 — coverage was never the issue). Recorded because the
  failure mode is instructive: the wrong conclusion was available and looked well-supported.

  **The result is corroborated from two independent directions.** The knockout rank order mirrors
  the sweep's anchoring order exactly (`tuned_S2` > `tuned_L0` > `tuned_L1b` > base in re-anchoring;
  the reverse in damage). And the deflationary reading — "the adapter just ignores code" — is
  refuted by the all-classes control, where `tuned_S2` is hurt MORE than base (−2.544 vs −1.590):
  it depends on the program more overall, on identifiers less specifically.

  **Sixth defect in the RQ3 chain**, all in never-executed code: `evaluate_with_knockout` called
  `grade(pred, gold)` against a three-argument signature AND unpacked two values from a six-field
  frozen dataclass — two independent breakages in one line. It also carried a silent fallback grader
  (strict string equality, not the project's normalized match), which I removed rather than repaired:
  a substituted grader is CLAUDE.md silent-failure #5, and it would have graded every knockout number
  by a different rule than every accuracy number it is compared against.

  **Compute note.** Two of three workers sat parked on the neighbour's cards while GPU 2 was idle —
  the exact scenario `compute.yaml` documents from 2026-08-12. Moved one onto the free card;
  throughput doubled for the remaining jobs. `launch_workers.sh --stop` is all-or-nothing (hardcoded
  `for i in 0 1 2 3`), so single-worker moves are manual.

- **New questions / new hypotheses:**
  - **Redo the `L1r` falsifier properly.** It needs a token classifier that recognises `v_a3f2` as an
    identifier, or a different contrast condition. Until then the mechanism has been supported but
    not yet given a fair chance to fail.
  - **Does the knockout effect scale with the anchoring shift across the whole matrix?** There are
    now 18 (system × condition) anchoring values and the machinery to knock out any of them; that
    regression is the RQ3 design's actual headline test.
  - **Is an `H1` attention read worth a quarantine access?** It is the only thing that would make the
    S2→H1 link direct rather than inferential.

- **Next Steps:**
  1. Fix the `L1r` contrast so H2 can actually be tested.
  2. Anchoring-shift ~ knockout-damage regression across the matrix.
  3. Decide on the `H1` attention read.
