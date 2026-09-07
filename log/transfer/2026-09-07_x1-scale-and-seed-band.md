### Target Date: 2026-09-07 (E1/E2 — the headline replicates at three scales and three seeds on X1, and the X1↔H1 proxy is validated at 34B for free)

The two eval-only experiments Tier 1 of [`docs/PAPER_EXPERIMENTS.md`](../../docs/PAPER_EXPERIMENTS.md)
opens with. Decision rules frozen at commit `a75b5fc` **before submission**; jobs 381290 (7B seed
band), 381291 (13B), 381292 (34B), 201/234/301 s. No adapter was trained — all six already existed —
and **no H1 cell was read**.

- **Hypotheses / what we're testing:** C1 (breadth training hurts on an unseen obfuscator) is the
  paper's central claim and rests on H1, whose budget is **fully spent**. It therefore cannot gain
  another replicate on the column it was established on. X1 reproduces H1's level at r = 0.9992 and
  is the only held-out column still readable, so both experiments ask whether C1 survives on X1.
  - **E1 / H-C1-scale-X1** — CONFIRM if `tuned_L0 − mono_all` on X1 excludes zero above at **both**
    13B and 34B; PARTIAL if one; REFUTE if neither.
  - **E2 / H-C1-seed-X1** — CONFIRM if the same contrast excludes zero above at **both** s42 and
    s101 at 7B.
  - Format-fail **reported, not gated** (H-format-gate is open and deliberately un-respecified).

- **Setup:** `configs/eval/x1_scale.yaml` (13B, 34B: `tuned_L0`, `mono_all`) and
  `configs/eval/x1_seedband_codellama7b.yaml` (7B: `tuned_L0_s42`, `tuned_L0_s101`), both
  `eval_conditions: [X1]`, Grid A heldout, greedy, vLLM. `mono_all` already had X1 reads at all
  three seeds from objectives round 2. Contrasts: `bootstrap_delta` clustered by `snippet_id`,
  n_boot 2000, seed 17, on the 1,214 items / 405 programs every X1 cell shares. Numbers →
  `results/analysis/x1_scale_seedband_2026-09-07.json`.

- **Results — E1: CONFIRMED at every scale.**

  | model | `tuned_L0` | `mono_all` | Δ pts [95 % CI] |
  |---|---:|---:|---:|
  | 7B | 0.2702 | 0.2323 | **+3.79 [+1.65, +6.09]** |
  | 13B | 0.2965 | 0.2537 | **+4.28 [+2.06, +6.50]** |
  | 34B | 0.3262 | 0.2998 | **+2.64 [+0.25, +5.10]** |

  Three scales, three intervals clearing zero. The effect does not shrink monotonically with
  capacity — it is largest at 13B — but the 34B interval is the widest and only just clears, so the
  honest statement is **"present at every scale tested, magnitude not resolved by scale"**, not
  "decreasing with scale".

- **Results — E2: CONFIRMED at every seed.**

  | seed | `tuned_L0` | `mono_all` | Δ pts [95 % CI] |
  |---|---:|---:|---:|
  | s17 | 0.2702 | 0.2323 | **+3.79 [+1.56, +5.93]** |
  | s42 | 0.2702 | 0.2348 | **+3.54 [+1.48, +5.60]** |
  | s101 | 0.2685 | 0.2331 | **+3.54 [+1.73, +5.60]** |

  `tuned_L0` on X1 spans **0.16 pts** across seeds (0.2702 / 0.2702 / 0.2685) — tighter than
  `mono_all`'s 0.25 and much tighter than `cons_lam3`'s 0.91 (§27.7). The contrast the paper is
  built on is not a seed draw, and this is the seed band H1 can never supply.

- **Results — the X1 scale ladder** (`tuned_L0` on X1): 13B − 7B **+2.64 [+0.41, +4.94]**,
  34B − 7B **+5.60 [+3.37, +7.90]**, 34B − 13B **+2.97 [+0.91, +5.27]**. Scale buys held-out
  accuracy monotonically and every step clears zero — the §27.3 scale result, now on a held-out
  family rather than the trainable grid.

- **Unplanned result — the X1↔H1 proxy is validated at 34B.** The proxy was established at **7B**
  (r = 0.9992 over six arms). These 34B X1 cells can be compared against the 34B H1 cells that
  already existed from the 09-05 final read — **no new H1 access, nothing selected on H1**:

  | 34B arm | X1 | H1 | \|Δ\| |
  |---|---:|---:|---:|
  | `tuned_L0` | 0.3262 | 0.3213 | **0.49 pts** |
  | `mono_all` | 0.2998 | 0.2965 | **0.33 pts** |

  The proxy holds at 4.9× the parameters it was calibrated on, to within half a point. That was not
  something E1 was designed to test and it materially strengthens every future use of X1: the
  substitute for the spent budget is now known to travel across scale, not just across arms at one
  scale.

- **What worked / hypothesis verdict:** **H-C1-scale-X1 CONFIRMED**, **H-C1-seed-X1 CONFIRMED**.
  C1 now stands on two independent held-out columns (H1 at 7B/34B, X1 at 7B/13B/34B), three model
  scales and three seeds. For ~12 minutes of GPU on adapters that already existed, this is the
  cheapest evidence in the campaign — the cost was entirely in noticing the gap, not in filling it.

- **Observations:**
  - `tuned_L0`'s format-fail on these X1 cells is 0.041–0.044, i.e. above the 2 % threshold, **on
    the control arm of the contrast being tested** — a third independent demonstration that
    H-format-gate is miscalibrated rather than detecting anything. Reported, not acted on.
  - The first submission (381287–381289) failed in seconds: `--argv` already prepends `python` and
    I passed it again, so SLURM tried to execute a file named `python`. No compute lost; worth a
    line in the submit script's help text.
  - 13B had never been read on any held-out column before today.

- **Next steps:** E1/E2 are closed. Next in the Tier-1 list is **E3** (H-cons-scale — does paired
  consistency survive at 13B/34B, ~20 GPU-h) and **E5** (a second family pair, the generality test
  for C2). `MASTER_REPORT.md` §27 should gain these numbers at its next revision.
