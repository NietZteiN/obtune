### Target Date: 2026-08-10 (the 2×2 factorial, and the objective question settled at source)

- **Hypotheses / what we're testing:**
  - **F1 (fidelity gate).** Nikiema et al.'s CFT objective is *loss-level* (InfoNCE / triplet /
    margin in embedding space), in which case our `cft` arm is not their method and every null
    we have reported is a null about something adjacent. CONFIRM if the paper specifies an
    embedding-space term; REFUTE if the three loss terms are instance pools trained by ordinary
    next-token cross-entropy.
  - **F2 (the factorial).** The contrastive objective contributes nothing *at either level of
    the data factor*. The four cells `sft` / `cft` / `flip` / `cftflip` cross objective
    (absent/present) with data direction (forward/bidirectional). CONFIRM if the objective main
    effect and the interaction both have CIs containing zero while the data main effect does
    not; REFUTE if `cftflip` > `flip` (the objective adds something on top of exposure).
  - **F3 (budget, at the headline tier).** `mix50` at 7B reproduces the 1.5B result, and
    `fwd2x` (forward-only, 6 epochs) does not. CONFIRM if `mix50 − sft` is large and positive
    while `fwd2x − sft` is inside noise; REFUTE if extra compute alone recovers reverse ability.
  - **F4 (E6, general vs directional damage).** Forward-only SFT's damage is directional, not
    a general capability loss. CONFIRM if HumanEval+ pass@1 holds up under `sft` while reverse
    collapses; REFUTE if `sft` loses general coding ability too.

- **Setup:**
  - Two new eval configs, both extending existing ones so the recipe is untouched:
    [`../../configs/srh/eval/e2_factorial_qwen1.5b.yaml`](../../configs/srh/eval/e2_factorial_qwen1.5b.yaml)
    (extends `cft/eval/bidir_v1.yaml`; adds `flip`, `cftflip`, `fwd2x` to the inherited
    `base`/`sft`/`cft`) and
    [`../../configs/srh/eval/e2_budget_qwen7b.yaml`](../../configs/srh/eval/e2_budget_qwen7b.yaml)
    (extends `e1_qwen7b.yaml` — NOT `bidir_v1.yaml`, which would inherit 1.5B adapter paths onto
    a 7B base; adds `mix50`, `fwd2x`).
  - `cftflip` and `fwd2x` at 1.5B, and `mix50` at 7B, were **already trained and had never been
    evaluated**. `fwd2x` at 7B finished training this morning (696 steps, 6 epochs).
  - Both configs validated before launch: `scripts/preflight.py` (0 errors), then
    `--stub --limit 4` plumbing runs, then full runs. 300 programs × 5 conditions × 2 directions,
    greedy, `simple` reverse strategy, seed 17.
  - `e2_budget_qwen7b` ran in tmux `e2budget` on **GPU 1** (21 000 generations, ~35 min);
    `e2_factorial_qwen1.5b` ran via the file-queue scheduler on **GPU 2** (18 000 generations).
    The first launch attempt of the factorial on GPU 0 was refused by vLLM at engine startup
    (8.79 GiB free vs 0.8 utilization requested) because another thread's 7B unlearn eval claimed
    the card seconds earlier — the guard behaved exactly as intended.
  - New analysis code, no GPU:
    [`../../scripts/srh/23_metric_tables.py`](../../scripts/srh/23_metric_tables.py) (E7/E8) and
    [`../../scripts/srh/24_contrasts.py`](../../scripts/srh/24_contrasts.py) (paired contrasts +
    the 2×2). New enqueue path for evals:
    [`../../scripts/srh/22_enqueue_evals.py`](../../scripts/srh/22_enqueue_evals.py).
  - Paper text read from `../../papers/nikiema2025contrastive.pdf` via `pdftotext -layout`.

- **Results:**

  **F1 — the paper's objective, quoted.** §5.0.2: `L_CFT = L_pos + L_neg + L_gen` (eq. 5), with
  the three terms described only as instance pools — *"we construct 30 000 instances (10 000 each
  for positive classification, negative classification, and obfuscation task generation)"*,
  *"Positive classification involves semantically equivalent code pairs requiring binary
  equivalence decisions"*. The strings InfoNCE, margin, cosine, temperature and embedding do not
  occur in the paper. Two of the three headline CFT numbers (GPT-4.1-Mini 52.03, GPT-3.5 50.51)
  come from models fine-tuned through *"provider-optimized fine-tuning protocols"* (§3.1) — the
  OpenAI API, which accepts only supervised text pairs. Open-source models use plain LoRA (§3.4).
  Realized pool ratio in our build: `gen` 7 912 / `pos` 7 912 / `neg` 6 021 = 1 : 1 : 0.76 against
  the paper's 1 : 1 : 1.

  **F2 — the 2×2 at 1.5B** (`e2_factorial_qwen1.5b`, 300 programs, 18 000 trials, strict):

  | | forward only | + reverse data |
  |---|---|---|
  | **no aux objective** | `sft` 0.3 % | `flip` 31.4 % |
  | **contrastive aux** | `cft` 0.3 % | `cftflip` 31.1 % |

  | effect | estimate (pp) | 95 % CI |
  |---|---|---|
  | data direction | **+30.9** | [+29.3, +32.6] |
  | contrastive objective | **−0.2** | [−0.7, +0.3] |
  | interaction | −0.3 | [−1.3, +0.7] |

  Also: `fwd2x − sft` = +0.3 [−0.2, +0.8]; `sft − base` = −2.5 [−3.4, −1.7]; `base` = 2.9 %,
  reproducing the published 2.9 % exactly (the program-set consistency anchor).

  **F3 — the budget controls at 7B** (`e2_budget_qwen7b`, 300 programs, 21 000 trials, strict):
  `base` 12.9, `sft` 0.0, `cft` 0.1, `fwd2x` 0.1, `mix50` 32.8, `rev` 32.9, `flip` 33.5.
  `mix50 − sft` = **+32.8** [+31.3, +34.4]; `flip − mix50` = +0.7 [−0.3, +1.8];
  `fwd2x − sft` = +0.1 [+0.0, +0.2]; `sft − base` = **−12.9** [−14.9, −10.9].
  Echo rates: `cft` 29.3 %, `sft` 18.2 %, `flip`/`mix50`/`rev` 0.0 %.

  **F4 — HumanEval+ pass@1 (`plus` split).** 1.5B: base .646, `sft` .329, `cft` .366,
  `mix50` .470, `flip` .512, `flipsym` .543, `rev` .585. 7B: base .805, **`sft` .817**,
  `flip` .744 (`cft`/`mix50` queued).

  **E7 (7B, strict, from existing `bidir_qwen7b` trials, no GPU):** `base` 13.0 / 17.7 / 21.8 /
  21.6 across simple / few_shot / cot / augmented; `sft` 0.0 / 2.0 / 5.5 / 4.8; `cft` 0.1 / 0.5 /
  1.5 / 1.3.

  **E8 (7B, `simple`), with the echo floor now computed:** on `L1r`, the paper's criterion passes
  19.7 % against 11.0 % strict; id-recall among passes 0.434, among all outputs 0.423, and the
  **copy-the-input floor is 0.349**. `L2`: 19.3 / 10.3, passes 0.430, floor 0.389. `L1b`: 4.3 /
  2.3, passes 0.342, floor 0.354. Structural conditions have a floor of **1.000** (S1, S2) —
  flattening and dead-code insertion preserve every original identifier. Corpus-computed and
  observed floors agree where both are estimable (L1b: 0.354 vs 0.356 over 76–179 echoed trials).

  **Dose ladder built and verified (CPU).** `mix5`/`mix10`/`mix25` added to the arm registry and
  configs written. Composition check: **7 384 instances at every dose** (identical to `fwd`),
  reverse share 5.0 / 10.0 / 25.0 / 50.1 %, and **zero programs appearing in both directions** at
  any dose.

- **What worked / hypothesis verdict:**
  - **F1 REFUTED — and this is the good outcome.** The objective is instance-level multi-task
    SFT, so `src/obtune/cft/` *is* the paper's method. The expensive branch of the planned E1
    (faithful loss-level reimplementation, 1–3 training runs on the critical path) does not fire.
  - **F2 SUPPORTED.** The objective main effect is −0.2 pp with a CI of [−0.7, +0.3] — not merely
    "no significant effect" but an effect bounded under a percentage point in either direction,
    at *both* levels of the data factor, with no interaction. The data main effect is +30.9.
  - **F3 SUPPORTED.** `mix50` — matched to `sft` on instances, sequence tokens and optimizer
    steps, with strictly less supervised signal — buys +32.8 pp at the paper's own model scale,
    while `fwd2x` at double the compute buys +0.1. The budget objection is closed on every axis.
  - **F4 SPLIT BY SCALE, and the split is the finding.** At 1.5B the damage is general: `sft`
    loses 31.7 pts of HumanEval+. At **7B it is purely directional** — `sft` is *above* base on
    HumanEval+ (.817 vs .805) while its reverse capability goes 12.9 % → 0.0 %. The stronger,
    stranger version of the claim is the one that holds at the headline tier.

- **Observations:**
  - The factorial is the cleanest attribution artifact this thread has produced, and it cost one
    evaluation pass because every adapter already existed. `cftflip` had been sitting trained and
    unevaluated since 2026-08-08; `mix50` at 7B likewise. Worth a standing check for
    trained-but-unevaluated adapters before planning any new run.
  - **E8's original claim was wrong as written.** "The paper's criterion passes outputs with
    near-zero identifier recall" is false — passes run ~0.43. The defensible claim needs the
    floor: on `L1r` the criterion's passes sit 0.085 above what copying the input scores, and
    only 0.011 above the model's own average output. The criterion is *uninformative*, not
    satisfied-by-nothing. Separately, id-recall is only a usable instrument on renaming: the
    structural conditions have a floor of 1.000, so it cannot discriminate there at all.
  - **A framing error to fix in the manuscript.** The paper *does* name the bidirectional
    baseline — §5.0.2: *"comparison against Standard Fine-Tuning (SFT) ... and Bidirectional
    Fine-Tuning (BFT) using forward generation plus reverse deobfuscation tasks"* — and then
    reports no BFT number anywhere (the string occurs once; Figure 4 has only SFT and CFT
    columns). "They never ran the control" is not accurate; "they name it and report nothing" is,
    and is the sharper claim.
  - `cft` at 7B echoes its input 29.3 % of the time — more than `sft`'s 18.2 %. The method sold as
    the cure for input-echoing exhibits it more strongly than the disease.
  - The 1.5B-vs-7B inversion on HumanEval+ is a caution against generalizing any capability-cost
    claim from the kill-gate tier. `flip` costs 6.1 pts of HumanEval+ at 7B while `sft` costs
    none — so the prescription is not free at the headline tier, and saying so is required.

- **New questions / new hypotheses:**
  - **F5:** does `mix50` at 7B carry the same HumanEval+ cost as `flip` (queued), or is the
    lower-supervision arm also the cheaper one in general capability? If `mix50` costs less than
    `flip`, it is the recommended arm on two axes rather than one.
  - **F6 (dose–response):** at what reverse share does the curve saturate? If 5–10 % recovers most
    of +30.9, the headline becomes a prescription rather than a refutation.
  - **F7:** is the 1.5B general-capability collapse a property of scale, or of the corpus being
    proportionally larger relative to the model? Not answerable with what is queued.

- **Next Steps:**
  - Queued now: `mix5`/`mix10`/`mix25` at 1.5B (training, GPUs 0/2/3); `sft`/`cft` at seed 42
    (E2); `forget7b` for `cft` and `mix50`.
  - After the dose arms land: one eval pass over the four rungs + `sft` + `base` → Fig 1.
  - Fix the BFT sentence and the E8 claim in the manuscript before drafting §4.
  - Stale documentation to correct: `MASTER_REPORT_2026-08-10.md` §8.3 (HumanEval+ harness is
    repaired and run) and §7.6 (`cftflip` and `fwd2x` are trained, and now evaluated);
    the `e1_qwen7b.yaml` comment claiming `mix50` at 7B is untrained.

---

#### Addendum, same day (appended after the queued `forget7b` jobs landed)

7B HumanEval+ `plus` completed for all five arms: `base` .805 · `sft` **.817** · `cft` .799 ·
`flip` .744 · `mix50` .732.

**F5 REFUTED.** `mix50` does not carry a *lower* general-capability cost than `flip` — it carries
a slightly higher one (−7.3 vs −6.1 pts). So `mix50` is the cheapest arm on training budget and
the more expensive of the two on retained capability; there is no arm that dominates on both.

This sharpens F4 into its final form: at 7B, forward-only training (`sft`, `cft`) preserves
general coding ability while destroying the reverse direction, and bidirectional training buys the
reverse direction back at a cost of 6–7 points of HumanEval+. **The effect is free on every
training-budget axis and is not free in capability**, and the paper's framing has to carry that
distinction explicitly — it currently does not.
