# ATTRIB paper — status report

*Written 2026-08-17, for a reader starting from nothing.*

Paper: *The Free Flip*, `paper_bidirectional/`. Venue: ATTRIB @ NeurIPS 2026, main track,
non-archival, 3–6 pp. **Submission Sept 1 AoE; results freeze Aug 28.**

Supersedes the work list in [`ATTRIB_WORKSHOP_PLAN.md`](ATTRIB_WORKSHOP_PLAN.md) §3, which was
written 2026-08-10 and predates all four of the runs in §3 below. Every number here was read from
a result file, not from a summary report.

> **Where this stands.** Every experiment the paper needs has already run. The critical path is
> analysis and writing, not GPU time. Four evaluations completed on 2026-08-12 and none has been
> read into the manuscript, given confidence intervals, or written into the log. That gap — not any
> missing experiment — is what stands between the current draft and a submittable one.

---

## 1. What the paper argues

**Code obfuscation** rewrites a program so it still computes the same thing but is much harder to
read — renaming `total_price` to `v_a3f2`, flattening control flow into a dispatch loop, padding
with dead code. Two directions matter:

- **Forward** — given clean code, produce the obfuscated version.
- **Reverse** — given obfuscated code, recover something readable and equivalent. This is
  deobfuscation, and it is the direction people actually want.

A 2025 paper by Nikiema et al. (arXiv:2509.05553) observed that a model fine-tuned on the forward
task loses the reverse one almost entirely, and proposed a fix: **Contrastive Fine-Tuning (CFT)**,
which adds two auxiliary classification tasks to the training mixture. They report **39.0 %**
reverse success on Qwen2.5-Coder-7B.

This paper makes three claims against that.

1. **The contrastive objective does nothing.** Adding it changes reverse capability by
   **−0.2 pp**, CI **[−0.7, +0.3]** — not merely non-significant, but bounded under one point in
   either direction.
2. **What works is the data direction, and it is free.** Training on the same pairs read backwards
   buys **+30.9 pp** [+29.3, +32.6]. Every reverse example already exists — it is the forward
   example with its two halves swapped.
3. **The source paper's numbers are not separable from the untouched model.** An unmodified
   Qwen2.5-Coder-7B scores **38.7 %** [35.9, 41.5] under a reasonable prompt, statistically
   indistinguishable from the 39.0 % their method is credited with. They report no untouched
   baseline.

> **A framing rule that must survive editing.** The source paper *names* Bidirectional Fine-Tuning
> in its evaluation framework (§5.0.2) and reports no result for it. Do not write "they never ran
> the obvious baseline" — it is factually wrong, and Nikiema et al. may review this submission. A
> declared-but-unreported baseline is also the sharper criticism.

---

## 2. How to read every table below

Each result compares **arms** — models fine-tuned with the same recipe and budget, differing in
exactly one thing. All are LoRA adapters (rank 32) over Qwen2.5-Coder at 1.5B or 7B, trained across
five obfuscation conditions: three renaming transforms (`L1b`, `L1r`, `L2`) and two structural ones
(`S1`, `S2`). Registry: `src/obtune/srh/arms.py`.

| arm | training data | what it is for |
|---|---|---|
| `base` | none — untouched model | the control the source paper omits |
| `sft` | forward only | the source paper's Standard Fine-Tuning. The disease. |
| `cft` | forward + two auxiliary classification tasks | the source paper's proposed cure |
| **`flip`** | forward + the same pairs reversed | the free baseline; doubles the data at no labelling cost |
| **`mix50`** | half forward, half reverse — *replacing*, not adding | the decisive arm: identical instances, steps and tokens to `sft`, with strictly *less* supervision |
| `mix5`/`mix10`/`mix25` | 5 / 10 / 25 % reverse, same replacement rule | the dose ladder — how little reverse data suffices |
| `rev` | reverse only | ceiling, and the kill-gate: if this were ~0, no other arm's null would mean anything |
| `fwd2x` | forward only, double the epochs | compute control — rules out "the flip just trained longer" |
| `cftflip` | both the objective and the reversed data | completes a 2×2: objective × data direction |
| `flipsym` | as `flip`, one shared system prompt | confound control — stops "two personas" masquerading as "two circuits" |

### The metric

Every reverse number here is **strict reverse success**: the output must satisfy the source paper's
own criterion **and** execute to the original program's outputs on real test inputs. It is
deliberately harsher than the published criterion, and it is the number we would defend.

The paper's own criterion is two inequalities — break similarity to the obfuscated input, recover
readability toward the original — and as written, *any* reply that is not the input satisfies the
first. A stub run in which every "generation" was the literal placeholder `<stub:a1b2c3>` scored
17–25 % "reverse success" before a parses-as-code guard was added
(`src/obtune/cft/metrics.py:500`). Strict success typically runs 10–20 points below the paper
criterion on the same outputs.

Intervals are 95 % **paired cluster bootstraps** over `program_id`, 2000 resamples — paired because
both arms are scored on the same programs, and clustered because several test inputs per program
are correlated.

---

## 3. The ledger at a glance

| state | count | meaning |
|---|---|---|
| ✅ **In the draft** | 8 | run, analysed, and written into `main.tex` |
| ⚠️ **Run, unread** | 4 | completed 08-12; on disk, absent from the paper, the log and `NUMBERS.md` |
| ⬜ **Never run** | 6 | optional; the paper is complete without every one of them |

---

## 4. Evidence already in the draft

Eight result sets carry the manuscript. The two that matter most:

### The 2×2 — objective versus data direction (1.5B, 18 000 trials)

| | forward only | + reverse data |
|---|---|---|
| **no aux objective** | `sft` 0.3 % | `flip` 31.4 % |
| **contrastive objective** | `cft` 0.3 % | `cftflip` 31.1 % |

Decomposed: data direction **+30.9** [+29.3, +32.6]; contrastive objective **−0.2** [−0.7, +0.3];
interaction −0.3 [−1.3, +0.7]. The objective's contribution is bounded under one point at *both*
levels of the data factor, with no interaction — a stronger statement than any single pairwise
comparison, and stated in exactly the vocabulary an attribution workshop uses.

### Budget controls at 7B (21 000 trials)

| contrast | Δ (pp) | 95 % CI | what it rules out |
|---|---|---|---|
| **`mix50` − `sft`** | **+32.8** | [+31.3, +34.4] | "the flip just used more data" |
| `fwd2x` − `sft` | +0.1 | [+0.0, +0.2] | "the flip just trained longer" |
| `flip` − `mix50` | +0.7 | [−0.3, +1.8] | doubling the data adds nothing |
| `sft` − `base` | −12.9 | [−14.9, −10.9] | forward-only tuning is *below* doing nothing |

`mix50` is matched to `sft` on instances, sequence tokens and optimizer steps while receiving
**0.71×** the supervised signal. The budget objection is closed on every axis, at the paper's own
model scale.

Also in the draft: the four-strategy prompting sweep for `base`/`sft`/`cft`; HumanEval+ retention
at both tiers; the measured token-budget accounting (`cft` 2.65× sequence tokens for 1.02×
supervised); and the metric-artifact analysis showing the source paper's success criterion has
near-zero lift over simply echoing the input (`L1r` passes recover 0.434 of identifiers against a
0.349 echo floor and 0.423 unconditioned).

> **The honest cost, already in the body.** Bidirectional data is free on *training budget* and
> costs ~7 points of HumanEval+ at 7B (`flip` .744, `mix50` .732 against `base` .805), where the
> forward-only arms cost nothing. "Free" is scoped to training cost everywhere it appears, and the
> trade-off is stated in §8 rather than buried in limitations. Stating it plainly is far stronger
> than letting a reviewer find it.

---

## 5. Run on 2026-08-12, still unread

All four live in `results/2026-08-12_cft-bidirectional/`. Each was listed as "queued" or "failed"
in the last status document; each has in fact completed. Two produce claims the plan did not
anticipate.

### 5.1 The dose ladder — and it is not a dose effect

How much reverse data is actually needed? The plan assumed a gradient and budgeted a figure for it.
What the run shows is a **step**.

*1.5B · 300 programs · 1500 trials per arm · strict reverse success*

| arm | reverse share | strict % | share of `mix50`'s effect |
|---|---|---|---|
| `base` | — | 2.7 | — |
| `sft` | 0 % | 0.3 | — |
| `cft` | 0 % | 0.3 | — |
| **`mix5`** | 5 % | **26.1** | **85 %** |
| `mix10` | 10 % | 28.1 | 92 % |
| `mix25` | 25 % | 29.5 | 97 % |
| `mix50` | 50 % | 30.5 | 100 % |

Five percent reverse data buys 25.7 pp over `sft` [+23.9, +27.7] — **85 % of what fifty percent
buys**, at one tenth the exposure.

> **Corrected 2026-08-17 after computing the intervals.** An earlier version of this section
> called the ladder a *step*. It is not: `mix50` − `mix5` = **+4.5 pp [+3.2, +5.8]**, a CI that
> excludes zero, so the climb from 5 % to 50 % is real — just small. What is genuinely flat is
> the top of the ladder: `mix50` − `mix25` = **+1.1 pp [+0.0, +2.1]**, which does not exclude
> zero. The defensible claim is a **saturating curve**: most of the effect arrives by a 5 %
> share and there is no detectable further gain past 25 %. Writing this up from point estimates
> alone would have put an overclaim in the paper.

### 5.2 Prompting strategies at 7B — the winning arm is prompt-insensitive

Reverse capability can be coaxed with prompt engineering, so a fair comparison has to try several
prompts on every arm. Until this run only the baseline arms had all four.

*7B · 1500 trials per cell · strict reverse success*

| arm | simple | few_shot | cot | augmented | range |
|---|---|---|---|---|---|
| `base` | 13.2 | 18.1 | 21.9 | 21.4 | 8.7 |
| `sft` | 0.0 | 1.6 | 5.3 | 5.1 | 5.3 |
| `cft` | 0.1 | 0.5 | 1.5 | 1.2 | 1.4 |
| **`flip`** | **33.7** | 32.6 | 32.8 | 32.6 | **1.1** |
| **`mix50`** | 32.8 | 31.3 | 30.3 | 31.7 | 2.5 |
| `rev` | 32.9 | 32.5 | 32.5 | 32.9 | 0.4 |

Two sentences become available. **The bidirectional arms are prompt-insensitive** — `flip` varies
1.1 points across four strategies where the untouched model varies 8.7. Capability that came from
data does not depend on how you ask; the little the base model has, does. And **the winning arm
beats the base under the base's own best prompt** (32.6 vs 21.9), so the headline is not an
artefact of comparing against a badly-prompted baseline — the plan hoped for this and it holds.

The sharpest line in the paper also survives: the fine-tuned model under its *best* prompt (5.3)
still scores below the untouched model under its *worst* (13.2). Prompting does not rescue what
fine-tuning removed.

Pooled over strategies: `flip` − `base` **+14.3** [+12.0, +16.5]; `cft` − `base` −17.8
[−19.9, −15.8].

### 5.3 JavaScript replication — retires the language limitation

Everything above is Python. A reviewer will ask whether the effect is a property of the language.
Four arms retrained on a JavaScript corpus, 167 programs, 835 trials per arm, 1.5B:

| arm | strict % | contrast | Δ (pp) | 95 % CI |
|---|---|---|---|---|
| `base` | 3.8 | — | — | — |
| `sft` | 0.0 | `sft` − `base` | −3.8 | [−5.6, −2.4] |
| `cft` | 0.4 | `cft` − `sft` | +0.4 | [+0.0, +0.8] |
| **`flip`** | **30.4** | `flip` − `sft` | **+30.4** | [+28.4, +32.5] |
| **`mix50`** | 30.3 | `flip` − `mix50` | +0.1 | [−0.2, +0.5] |

The whole pattern reproduces. In JavaScript the budget-matched arm is *exactly* as good as the
doubled one — the `flip` − `mix50` gap that was +0.7 in Python is +0.1 and not significant.

> **Keep this limitation sentence honest.** JavaScript answers "is this Python-specific?" It does
> not answer "is this Java-specific?", which is the literal form of the objection, since the source
> paper's setting is Java. The limitation must say so. ~~No JDK on this host~~ and a Java
> replication does not fit the window.
>
> **Corrected 2026-08-17:** the JDK claim is false — one `conda create openjdk=21` away. The real
> reasons are in `ATTRIB_WORKSHOP_PLAN.md` §4: CodeNet Java is stdin/stdout `main` programs and
> cannot enter this project's `entry_point(args) → value` contract, there is no Babel equivalent
> for a Java binding graph, and a third canonicaliser would need byte-parity that already failed
> twice on Python↔JS. Decision unchanged; the reasoning was wrong and would not have survived a
> reviewer who knows conda. The paper's limitation now also states what a Java-specific rescue of
> the objective claim would have to look like, which puts the burden on that explanation.

### 5.4 Second seed for the two load-bearing arms

A single training run is a data point, not a result. Seed 42 now exists for all six arms: `sft`
**0.4** and `cft` **0.4**, against 0.3 and 0.3 at seed 17. The `cft` − `sft` contrast is **+0.0**
[−0.5, +0.5] — the null the whole paper turns on replicates at a second seed. The bidirectional
arms move by at most 0.9 pp across seeds.

---

## 6. Required before submission — zero GPU

This is the entire remaining delta between draft v1 and a submittable paper. All analysis and
writing.

**All nine were executed on 2026-08-17** except where noted. Detail:
[`../log/cft-replication/2026-08-17_attrib-v2-and-determinism.md`](../log/cft-replication/2026-08-17_attrib-v2-and-determinism.md).

| | task | status |
|---|---|---|
| **1** | **Dose-ladder CIs.** `DEFAULT_CONTRASTS` in `scripts/srh/24_contrasts.py` had no `mix5`/`mix10`/`mix25` rows. | ✅ done — 13 contrasts recomputed; **changed the claim** (see §5.1) |
| **2** | **Draw Fig. 1.** No plotting script existed and `main.tex` had no `figure` environment. | ✅ done — new [`scripts/srh/25_fig_dose.py`](../scripts/srh/25_fig_dose.py) emits pgfplots from `trials.jsonl`, so no number is hand-typed and the figure regenerates with the run |
| **3** | **Fold all four runs into `main.tex`** → v2. | ✅ done — Fig. 1 + dose ¶, JS ¶ + App. E, App. B rebuilt to 6 arms, App. D rebuilt with an anchor row, prompt-insensitivity ¶, limitations rewritten |
| **4** | **Trim to the page limit.** | ⚠️ partial — body cut from ~7.5 pp to **7.0 pp** against a 3–6 pp allowance. All three README trims applied, plus the fidelity block and arm table moved to App. A. **~1 pp still over**; see §6a |
| **5** | **State the source run under every table.** | ✅ done — and the *reason* was wrong (see §6b) |
| **6** | **Update `NUMBERS.md`.** | ✅ done — 4 runs added, 4 new section rows, exclusions table rewritten |
| **7** | **Write the log entry.** | ✅ done — entry + thread README + master timeline |
| **8** | **Remove misleading artefacts.** | ⚠️ partial — `evaluate.py` now unlinks the marker on a successful guard pass, so it cannot recur. **Three** stale files exist (not two: `unlearn_rev_minus_sft_python` has one too); left in place pending approval per CLAUDE.md §2 |
| **9** | **Submission mechanics.** | ⬜ not started — venue style, anonymisation, OpenReview checklist |

### 6a. The residual page overrun

Body now ends exactly at p7; references p8; appendices A–E p8–10. Getting under 6 pp needs
roughly one more page, and the remaining candidates are **content decisions, not mechanical
trims** — which is why they are left for you:

- Table 3 (budget ratios) → appendix ≈ 0.3 pp
- Table 4 (per-condition reverse) → appendix ≈ 0.25 pp
- §1 Introduction + contributions list ≈ 0.3 pp

`paper_bidirectional/README.md` says explicitly *do not* buy pages by cutting §8 (the
HumanEval+ cost) or the CI-in-sentence convention, so those are off the table.

### 6b. Item 5's premise was wrong — and the correction is worth more than the item

The draft and `NUMBERS.md` both explained the multiple `base` numbers as *"different
300-program draws from the same split."* That is not what happened. The `program_id` sets are
**byte-identical across all five 1.5B passes**. The real cause is **batch nondeterminism**:
greedy decoding is not bitwise reproducible, because the inference engine batches continuously
and which arms share a pass changes reduction order and occasionally an argmax.

| evidence | value |
|---|---|
| the one pass-pair sharing an arm list | **0 / 1500** generations differ |
| every other pass-pair | 6–8 % of generations differ, 4–8 graded trials flip |
| two *same-day* passes | also disagree → not a code change |
| resulting spread on `base` | 2.7–2.9 % at 1.5B, 12.9–13.2 % at 7B |

Consequences, all applied: a methods sentence in §2 and the measurement in App. A; a `base`
anchor row in the seed table so a reader can see the floor; and the rule *never quote a
cross-pass difference finer than 0.5 pp*. Nothing in the paper depends on it — the effects are
30 pp — but the seed table quotes Δs of a few tenths, which is exactly where it would have bitten.

The gate in `configs/srh/eval/e2_seeds_qwen1.5b.yaml` asserted the wrong diagnosis ("if `base`
≠ 2.9 %, the program set has drifted") and would have sent the next person hunting corpus drift
that never happened. Rewritten to separate the two tests: compare `program_id` sets for drift
(exact, free), and hold `base` to a 2.6–3.0 % tolerance band for the anchor.

---

## 7. Never run — would strengthen, not complete

Ranked by value. None is a dependency; the paper as drafted is supported end to end by finished
runs.

> **⚠️ Corrected 2026-08-17, later in the day. The first two rows of this table have run, and
> the last row has run.** All five `attrib-gaps` cells (`mix5`/`mix10`/`mix25` @ 1.5B,
> `rev`/`fwd2x` @ 7B) were enqueued at the default priority 59 and completed 11:24–11:33 UTC;
> results are on disk in `results/forgetting/` and are already folded into the paper's Table 5
> and Appendix D. MBPP+ then ran across all seven 7B arms the same evening. Do not treat this
> section as a work list — the rows below marked ✅ are done, and §8's timeline is likewise
> written against a queue that has since drained.
>
> The MBPP+ cost estimate here was also wrong by an order of magnitude: measured forgetting
> cells run 100–160 s, not the ~2 h guessed below.

| run | cost | what it would buy |
|---|---|---|
| ✅ **HumanEval+ on the dose arms** (`mix5`/`mix10`/`mix25` @ 1.5B) | ~1 h, inference | **DONE 2026-08-17 11:24–11:28 UTC.** §8 says bidirectional data costs 6–7 pts of general coding ability. Outcome: the retained capability is **not** monotone in reverse share (`mix5` .537, `mix10` .555, `mix25` .494, `mix50` .469, `rev` .585), so no dose-response conclusion is drawn on this axis at 1.5B. Now Appendix D. |
| ✅ HumanEval+ for 7B `rev` and `fwd2x` | ~1 h, inference | **DONE 2026-08-17 11:30–11:33 UTC.** Both rows of Table 5's 7B column are filled: `rev` .799, `fwd2x` .805. |
| ✅ **MBPP+ @ 7B, all seven arms** | measured ~5–6 min/cell | **DONE 2026-08-17 evening; not in any earlier plan and worth more than everything below it.** The abstract's selectivity claim rested on HumanEval+, and HumanEval is one of the corpus's three sources — 74 of its 164 problems are in the train split. MBPP is **0/399**: the corpus was built `tiers: ['tier1']` and MBPP sits only under `tier2`, never built. New `mbpp_plus()` in `src/obtune/forgetting.py`, new `mbpp-7b` preset. |
| `mix10` @ 7B — dose anchor | ~10 GPU-h + eval | Confirms the ladder's shape is not a small-model artefact. Worth more now that the shape is a step rather than a slope. **Not yet trained.** |
| `neg`-pool parity sweep | ~3 GPU-h | Insurance against "you starved the contrastive signal" — our `neg` pool is 24 % short of parity. The token-share arithmetic already bounds it: parity moves the auxiliary share from 2.3 % to ~2.6 %, which cannot produce a 30-point swing. Already stated in §9. |
| Cross-transformation generalisation (train S1-only reverse, test S2) | ~6 GPU-h | Never started; was the plan's designated punt. Punt it. |
| ~~MBPP~~ | ~~~2 h~~ | Superseded by the ✅ MBPP+ row above. The "HumanEval+ already carries the claim" reasoning was wrong: HumanEval+ cannot carry it, because it is the contaminated probe. |

> **⚠️ The compute paragraph below is superseded. As of ~20:00 UTC 2026-08-17 all four A6000s
> are idle (1 MiB, 0 % each), the queue is empty, four workers are polling it, `allowed_gpus`
> is `[0, 1, 2, 3]` and `gpu_budget` is 4.** The modularity grid that was gating everything
> drained by 07:03 UTC, and the borrower's 38 GB sglang holding on GPU 3 turned out to be
> obtune's *own* `forget__qwen25c-7b__7b_rev` job. Nothing needed `--priority 5`; every cell
> below ran at the default 59. **Re-read `nvidia-smi` and the queue rather than trusting this
> block** — that is the recurring lesson of this file.
>
> One toolchain trap worth recording, since it cost a failed run: `obtune.forgetting` needs
> both `PYTHONPATH=src` and the conda env's `bin` on `PATH`. vLLM's flashinfer sampler
> JIT-compiles on first use and shells out to `ninja`, which lives in
> `/data/jvl210002/conda_envs/obtune/bin`. Invoking the interpreter by absolute path without
> that on `PATH` fails deep inside engine startup as
> `RuntimeError: Engine core initialization failed`, whose root cause is nine frames down.
> The workers set both, so queued jobs are unaffected — this only bites manual invocation.
>
> ~~**Compute reality — updated 2026-08-17, later in the day.** **No GPU is free.** GPU 1 runs
> obtune's own `composite_qwen1.5b_py` training; GPUs 0, 2 and 3 are held by the borrower's
> sglang servers and `steer_run`/`transfer_gate` jobs. Note GPU 0 reads 0 % util while holding
> 38 GB — an idling sglang server is **not** a free card. `gpu_budget: 1` and the shared queue
> has six modularity jobs pending.~~
>
> ~~The top two runs are **wired into the pipeline and validated, but not enqueued**~~:
> [`scripts/srh/26_enqueue_forgetting.py`](../scripts/srh/26_enqueue_forgetting.py)
> `--preset attrib-gaps` covers all five cells (`mix5`/`mix10`/`mix25` at 1.5B,
> `rev`/`fwd2x` at 7B). ~~It is a dry run unless you pass `--write`, and nothing has been
> written.~~ **All five were written and have completed.** Existing forgetting cells took 105 s
> each at 1.5B, so the set is ~10–30 min of GPU.
>
> ```bash
> python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps          # dry run
> python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps --write  # enqueue
> ```
>
> **The scheduling decision is yours.** The default priority 59 sits *behind* the five
> modularity jobs at priority 10–20, per the documented ladder ("the RQ1 grid is not this
> thread's to delay") — so these will not start until that grid drains, possibly hours. To
> put ATTRIB first, add `--priority 5`, which costs the FSE paper directly and is therefore
> not something the script will do on its own.

---

## 8. Nine working days to freeze

| when | work |
|---|---|
| **Aug 15–16** | §6 items 1, 2, 5, 6 — dose CIs, Fig. 1, table provenance, `NUMBERS.md`. Launch the two inference runs by hand if a card is free. |
| **Aug 17–18** | §6 items 3, 4 — draft v2 with all four runs folded in, trims applied, recompiled and page-checked. Item 7 (log entry). Decide on the 7B anchor. |
| *Aug 19–21* | *Kyoto. No paper work.* |
| **Aug 22–24** | Draft v3. Fold in the retention runs if they landed. Item 8. Tone audit: every strong claim carries its interval in-sentence. |
| *Aug 25–26* | *Travel.* |
| **Aug 27–28** | **Results freeze.** Item 9 — venue style, anonymisation, checklist. Anything unlanded ships as a limitation, not a delay. |
| **Aug 29–31** | Polish, page compression, final read. |
| **Sept 1 AoE** | Submit; register as reciprocal reviewer the same day. |

The freeze rule is unchanged and comfortable: **nothing on this page is a dependency.** §6 makes
the paper correct; §7 would make it stronger.

---

## Sources

Every number read from a result file, not from a summary report:
`results/2026-08-09_cft-bidirectional/`, `results/2026-08-10_cft-bidirectional/`,
`results/2026-08-12_cft-bidirectional/`, `results/forgetting/`,
`results/srh/budget_qwen7b_python.json`.

Superseded plan: [`ATTRIB_WORKSHOP_PLAN.md`](ATTRIB_WORKSHOP_PLAN.md) (2026-08-10, predates all
four completed runs).

## Changelog

- **2026-08-17** — Created. Records that `e3_dose`, `e2_seeds`, `e7_strategies` and
  `e3_javascript` all completed 2026-08-12 and are absent from the manuscript, the log and
  `NUMBERS.md`. Notes that the dose curve **saturates at 5 %** rather than sloping, that the
  bidirectional arms are prompt-insensitive at 7B, and that HumanEval+ on the dose arms — not in
  the original plan — is now the highest-value remaining run.
