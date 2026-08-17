# Master Report — everything run, and everything that will run

*Last updated: **2026-08-12** (see §12, which corrects §6). Supersedes [`MASTER_REPORT_2026-08-10.md`](MASTER_REPORT_2026-08-10.md),
which covered 453 cells; this covers **597 cells / 317 810 trials** plus the five programmes that
live outside that grid.*

---

## 0. How to read this

Numbers here are regenerated from disk (`scripts/make_master_report.py`, run today) or read
directly out of the per-experiment result files. Nothing is quoted from memory or from the prior
report. Where a number differs from the 2026-08-10 report, the difference is more data, and it is
flagged.

Three things to hold onto before reading any table:

1. **Two evaluation grids exist and must never be pooled.** Grid A ("corpus") is 317 Python /
   91 JS programs on the held-out corpus split, all 7 conditions including H1. Grid B ("testset")
   is 33 Python / 30 JS ICSE test-set programs, and is where the router and the merges live. They
   are disjoint in programs; pooling them silently averages different populations.
2. **Seed noise is 1.32 pts mean, 3.61 pts at p95** (measured over 84 matched s17/s42 deltas). Any
   single-seed delta smaller than ~3.6 pts is inside noise. Several headline-looking deltas below
   are exactly at that boundary, and this report says so rather than rounding them up into effects.
3. **The metric is control-relative.** Deltas are against the `tuned_L0` adapter of the same seed
   and grid, not against `base`. The pilot's L0 control forced this: most of the apparent
   "obfuscation transfer" is just the gain from tuning on *clean* code at all.

---

## 1. Inventory — what has actually been run

| | |
|---|---|
| eval cells | **597** |
| graded trials | **317 810** |
| programs | 557 py / 168 js (corpus), 40 py / 30 js (testset) |
| queue | 164 done, 4 running, 3 queued, **0 failed** |
| H1 accesses | 24 625 py + 4 146 js trials, all `purpose=final_eval` |
| tests | 432 passing |
| preflight | 0 errors, 7 known warnings |

Five programmes have produced results:

| programme | status | where |
|---|---|---|
| RQ1 generalization (transfer matrix) | complete, both languages, 2 seeds | Grid A |
| RQ2 modularity (router, 3 merges) | complete at 1.5B | Grid B |
| CFT replication + refutation | complete at 1.5B **and** 7B | `results/2026-08-10_cft-bidirectional/` |
| Part IV approximate unlearning | λ-sweep complete both scales; **controls running now** | same |
| Part V overtraining / merge geometry | Stage 0 complete on two banks | `results/merge_geometry/` |

---

## 2. RQ1 — Generalization

**Grid A, Python, seed 17, n = 317 programs, 86 450 trials.** Accuracy by eval condition:

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| `base` | .201 | .165 | .164 | .176 | .187 | .147 | **.066** |
| `tuned_L0` *(control)* | .440 | .321 | .353 | .353 | .379 | .411 | **.259** |
| `tuned_L1b` | .427 | **.360** | .359 | .354 | .353 | .402 | .263 |
| `tuned_L1r` | .445 | .333 | **.383** | .381 | .375 | .422 | .260 |
| `tuned_L2` | .436 | .328 | .366 | **.363** | .366 | .419 | .254 |
| `tuned_S1` | .433 | .296 | .352 | .355 | **.414** | .418 | .266 |
| `tuned_S2` | .459 | .317 | .367 | .365 | .415 | **.445** | **.294** |
| `mono_all` | .392 | .355 | .341 | .359 | .372 | .390 | .228 |
| `oracle_prompt_1shot` | .243 | .180 | .197 | .213 | .202 | .226 | .158 |

**The specialist advantage is real but small.** Each expert beats the L0 control on its own
condition by:

| condition | own-condition gain vs `tuned_L0` | 95% CI |
|---|---|---|
| L1b | **+3.89 pts** | [1.48, 6.41] |
| S1 | **+3.47** | [0.74, 6.43] |
| S2 | **+3.47** | [1.26, 5.79] |
| L1r | **+3.05** | [0.84, 5.36] |
| L2 | +1.05 | [−0.95, 3.16] |

Four of five exclude zero; L2 does not. But **all four sit at or below the p95 seed-noise band of
3.61 pts**, so the honest statement is that specialization buys a few points, comparable in size to
re-running with a different seed. That is itself a finding for RQ2: there is very little for a
router to win.

**On the held-out H1 family, condition-specific training buys almost nothing.** `base` .066 →
`tuned_L0` .259. The L0-only control captures **+19.3 of the +22.8 points** that the best specialist
reaches (`tuned_S2` .294). Tuning on clean code recovers most of the H1 gain; the obfuscation
condition you train on adds ~3.5 points on top. The Invariance Index is therefore measuring
something much weaker than "learning the transform class".

**The one durable exception**: `tuned_S2` is the best system on H1 at both seeds in both languages.
S2 (opaque predicates + dead code) is the only condition whose training generalizes to the held-out
family beyond the clean-code baseline.

**Corrected from the 2026-08-10 report**: that report claimed "transfer into L1b genuinely fails".
It does not. That claim came from `core_subset`/`compute_is_core` grouping across experiments,
which collapsed the transfer matrix to 23 of 340 programs. At the correct n, all L1b cells are
significant (L0→L1b +15.2 [12.1, 18.5]). The bug is fixed; the claim is withdrawn.

---

## 3. RQ2 — Modularity

**Grid B, Python, n = 33 programs.** Small — treat as directional.

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| `tuned_L0` *(control)* | — | — | — | — | — | — | — |
| `router` | .503 | .483 | .483 | .517 | .435 | .483 | *n/a* |
| `merge_ties` | .407 | .310 | .359 | .400 | .386 | .310 | .293 |
| `merge_dare_ties` | **.503** | .407 | .435 | **.510** | .441 | .428 | **.374** |
| `merge_dare_linear` | .048 | .048 | .035 | .028 | .048 | .069 | .051 |

**The learned router is saturated and that is a ceiling, not a success.** Validation accuracy
0.9969, overall route accuracy 1.0, mean routing entropy ~1e-6 nats against a maximum of 2.079,
perfectly diagonal confusion matrix. It recovers the specialists and does not exceed them —
because, per §2, the specialists are only ~3.5 pts above the control. *Which adapter to pick* is
solved; there is nothing left to win on seen conditions.

**`merge_dare_ties` is the best system on H1 anywhere in the project** (.374 on Grid B), beating
`merge_ties` (.293) and, cross-grid, `mono_all` (.228). Prune-then-elect beats elect-alone.

**`merge_dare_linear` is a broken merge, not a data point.** Its collapse to .028–.069 is a
**7.175× ‖ΔW‖ scale artifact** — same direction as the working merge (cosine 0.83), wrong
magnitude. It is excluded from every comparison; a scale-corrected re-run is queued
(`t2_controls`).

**Still unanswered**: `routing_report.json` records `n_heldout: 0`. H1 was never actually routed, so
the out-of-distribution routing question remains open. Part III is the attempt on it.

---

## 4. CFT replication — the refutation

Replicating `nikiema2025contrastive` (arXiv:2509.05553), which claims forward-only fine-tuning
gives **0%** at deobfuscation ("cognitive specialization") while Contrastive Fine-Tuning recovers
**39–52%** with no reverse training data.

**7B, Python, 300 programs / 1500 trials per cell:**

| arm | forward (exec) | **reverse (strict)** | reverse (paper) | identity/echo |
|---|---|---|---|---|
| `base` | .929 | **.129** | .233 | .073 |
| `sft` (forward-only) | .971 | **.000** | .004 | .182 |
| `fwd2x` | .969 | **.001** | .019 | .071 |
| `cft` (contrastive) | .975 | **.001** | .002 | **.293** |
| `rev` (reverse-only) | .927 | **.329** | .351 | .000 |
| **`flip`** (forward+reverse) | .971 | **.335** | .353 | .000 |
| **`mix50`** | .961 | **.328** | .356 | .000 |

**The paper's headline does not replicate, and it fails in the direction that matters.** CFT reaches
**0.1%**, not 39%. The untouched base model reaches 12.9% — *CFT is worse than doing nothing*.
Meanwhile the free flip of the training pairs reaches **33.5%**, and does so at no forward cost
(.971 vs base .929).

**`mix50` is the arm the argument turns on.** It replaces 50% of forward instances with their
reverse twins, partitioned by `program_id` so no program appears in both directions. It is
identical to forward-only SFT in instances, steps, FLOPs and wall-clock, with **strictly less**
supervised signal (0.76×), and it reaches **.328 against forward-only's .000**. Bidirectional
exposure produces reverse capability at *negative* budget cost. "Cognitive specialization" is a
property of the data the forward-only regime was given, not of the objective.

**The contrastive objective adds nothing over exposure.** At 1.5B, `cftflip` .311 vs `flip` .314 —
identical within noise. And `fwd2x` .006 rules out "flip just trained longer".

**Part of the reported 0% is an echo artifact.** `cft` emits the input unchanged 29.3% of the time
and `sft` 18.2%; `flip`/`rev`/`mix50` never do (.000). A scorer that credited echoes would report
a very different number, which is why the identity rate is tracked as a first-class diagnostic.

**Budget accounting** (measured, per epoch on the Python ALL5 train split): CFT costs **2.60×**
forward-only's sequence tokens to add **1.02×** supervised signal; FLIP costs 2.00× to add 1.52×.
CFT is dominated on every axis a practitioner pays for.

---

## 5. Catastrophic forgetting (HumanEval+ pass@1, 164 tasks)

The scorer was silently reporting 0.0 for every arm until it was repaired on 2026-08-10 (it read a
`expected_output` key that does not exist, and a bare `except` swallowed the `KeyError`). Repaired
numbers:

| arm | 1.5B `plus` | 7B `plus` |
|---|---|---|
| `base` | **.646** | **.805** |
| `rev` | .585 | — |
| `flipsym` | .543 | — |
| `flip` | .512 | .744 |
| `mix50` | .470 | .732 |
| `cft` | .366 | .799 |
| **`sft`** | **.329** | .817 |

**At 1.5B, forward-only SFT is the most destructive arm tested** — it loses 31.7 points of general
code ability, more than any bidirectional arm. At 7B the damage largely vanishes (`sft` .817 ≥ base
.805). Bidirectionality is not what costs you; scale is what protects you.

---

## 6. Part IV — approximate unlearning as the SRH probe

Exact unlearning cannot test the Shared Representation Hypothesis: exact removal of the forward
direction from FLIP *is* the REV arm, whose reverse performance is guaranteed to survive. The
signature relocates to **approximate unlearning over-removing relative to exact**. The operator is
`U(λ) = FLIP − λ·SFT` via `taskvec.combine` with `combination_type="cat"`, which is exact
weight-space arithmetic (`ΔW = (α/r)·B@A`, `use_dora`/`use_rslora` both false).

**7B** (base fwd .929, FLIP fwd .970, REV rev .329):

| λ | forward | reverse | reading |
|---|---|---|---|
| 0 | .970 | .337 | = FLIP |
| 0.5 | .944 | .322 | |
| **0.75** | **.919** | **.305** | **operating point** — forward ≈ base |
| 1.0 | .946 | .251 | |
| 1.5 | .825 | .212 | past the point; forward over-removed |

At the operating point, over-removal = **.329 − .305 = 2.4 pts**. HumanEval+ at λ=1.25 is .823,
*above* base .805. **Forward is removed surgically and reverse survives → the disjoint reading, SRH
refuted at 7B.**

**1.5B** (base fwd .868, FLIP fwd .921, REV rev .314):

| λ | forward | reverse | HumanEval+ |
|---|---|---|---|
| 0 | .915 | .314 | .506 |
| 0.5 | .900 | .267 | |
| **0.75** | **.827** | **.126** | **.585** |
| 1.0 | .422 | .071 | .579 |
| 1.25 | .003 | .002 | |

At the operating point, over-removal = **.314 − .126 = 18.8 pts**. And precondition 2 holds:
HumanEval+ at λ=0.75 is **.585, higher than FLIP's own .512** — the model is not generically
damaged, it is *specifically* losing reverse. **That is the SRH signature at 1.5B.**

**The two scales disagree, and that dissociation is the most interesting unpublished result here.**
At 7B forward and reverse are separable; at 1.5B they are entangled. The natural reading —
representations disentangle with capacity — is a claim neither literature makes, and it is exactly
the kind of claim that needs its controls before anyone says it out loud.

**Those controls are running right now** on all four GPUs: `rev − λ·sft` and `mix50 − λ·sft` at both
scales. `rev` never saw forward data, so if reverse falls there too, the effect is the operator
damaging any adapter rather than entanglement. **No Part IV claim should leave this file until
those land.** Expected within hours.

**The asset**: forget and retain sets here are **content-identical** — same programs, same variants,
differing only in which side is the question. Every "the forget set was just harder/rarer" confound
is eliminated by construction. No capability-unlearning benchmark can currently claim that, and it
may be more publishable than the SRH result itself.

---

## 7. Part V — are our experts overtrained for merging?

Following Horoi et al. (arXiv:2506.14126v2): long fine-tuning that optimizes each expert's
*individual* performance degrades merging, via negative parameter interference. This describes
obtune's `run_ckpt_select` exactly — it picks `best` by held-in validation accuracy, and every
merge in the project is built from `best`.

**Stage 0 (CPU, zero GPU) on two banks:**

| | 8 experts × 3 epochs (standard bank) | 3 experts × 9 epochs (overtrain probe) |
|---|---|---|
| ‖ΔW‖ ep1 → last | 0.299 → 0.371 | 0.286 → **0.602** |
| cosine ep1 → last | 0.584 → 0.592 | 0.498 → **0.421** |
| **sign conflict** | 0.402 → **0.391** *(falls)* | 0.336 → **0.355** *(rises)* |
| TIES keep rate | .854 → .861 | .890 → .876 |
| `interference_grows` | **false** (Δ = −0.011) | **true** (Δ = +0.019) |

**The mechanism is real but does not reach our standard bank.** At 3 epochs sign conflict is still
*falling* — our experts are **under**-trained relative to where interference appears. Extend to 9
epochs and it reverses: the task vector doubles in norm, experts rotate apart (cosine 0.50 → 0.42),
and sign conflict rises monotonically to a plateau at ~epoch 6.

**But mechanism ≠ consequence.** Merged accuracy across the epoch sweep was flat within CIs. So the
current honest statement is: *Horoi's mechanism reproduces in the overtrained regime at LoRA r=32,
and does not measurably change merged accuracy at this scale with 3 experts.* Sign conflict is a
pairwise statistic — 3 experts give 3 pairs, 8 give 28 — which is why `t2_overtrain` completes the
8-expert 9-epoch bank before Stage 2 runs.

**A confound this uncovered, which affects every existing merge**: `ckpt_select` chose *different*
epochs per condition (L1r and S3 at epoch 1; L0/L1b at 2; L2/S2/S1/S4 at 3). Every merge in this
project therefore combines task vectors of unequal training. The uniform-epoch sweep
(`t2_epoch_sweep_full`) exists to remove that, and it has to be reported either way.

---

## 8. What will run

The pipeline is live (pid 284572, PPID 1, survives logoff), 11 stages complete, **12 remaining**.
All four GPUs are busy; 0 jobs have failed.

### Immediately (running now, ~1.5 GPU-h each)
`evalunlearn_revmsft` and `evalunlearn_mix50msft` at 7B and 1.5B — **the Part IV controls §6 is
blocked on.**

### Queued behind them (~3 GPU-h)
Three SRH evals: `e2_seeds` (seed-42 stability), `e3_dose` (bidirectional dose–response),
`e7_strategies` (7B prompting strategies).

### The ATTRIB chain — deadline-critical, owns the box first

| stage | what | GPU-h |
|---|---|---|
| `attrib_evals` | enqueue + drain the three SRH evals above | ~3 |
| `attrib_js_train` | the 4 JavaScript arms (`sft`, `cft`, `flip`, `mix50`) at 1.5B | ~10 |
| `attrib_js_eval` | JS bidirectional eval — **does the refutation hold cross-language?** | ~1 |
| `attrib_analysis` | contrasts + metric tables | 0 |

### Tier 2 — Part V completion

| stage | what | GPU-h |
|---|---|---|
| `t2_overtrain` | 5 more 9-epoch arms → completes the 8-expert bank (3 pairs → 28) | ~10 |
| `t2_geometry` | Stage 0 over the full bank | 0 |
| `t2_epoch_sweep_full` | uniform-epoch merges at epochs {1,3,6,9} — removes the §7 confound | ~5 |
| `t2_merge_optimal` | 3 greedy rounds of **merge-optimal** checkpoint selection | ~16 |
| `t2_controls` | remaining unlearning control + scale-corrected `dare_linear` | ~0.5 |

### Part III — RouterLoRA (queues last)

| stage | what | GPU-h |
|---|---|---|
| `p3_composites` | 6 stacked conditions, CPU only — built and verified today | 0 |
| `p3_mole_train` | train the gate (2.77M params; base + 8 experts frozen) | ~3 |
| `p3_mole_eval` | the mixture ladder: base / `mole_uniform` / `mole_random` / `mole_router` | ~1.5 |

**Total remaining ≈ 53 GPU-h ≈ 3–4 calendar days at 4 GPUs.** Comfortably inside the Aug 28 results
freeze, with ~2 weeks of slack for the Sept 1 AoE deadline.

### Built today and ready

Part III went from a plan to a working system: the mixture is in **activation space**
(`h = Wx + Σ a_e(x)·(α/r)·B_e A_e x`) — exact, no per-item merge rebuild, no rank growth. Gate
dry-run on the real mixture: 7384 instances, **0.000% truncation**, 2 766 876 trainable gate
parameters against a 295 436 288-parameter frozen bank, loss mask asserted at −100. The composite
corpus generates at **74% coverage (Python) / 99% (JS)**, above the 50% Gate-0 threshold. The HF
engine implements `eval_vllm.run_cell`'s contract, so mixture cells are schema-valid and collate
with no special-casing — verified with a stub run.

---

## 9. Gates ahead — where this can still stop

Sequenced cheapest-kill-first. Each is pre-registered so a negative result is publishable rather
than a disappointment.

| gate | cost | rule |
|---|---|---|
| **Part IV controls** | running | If reverse falls under `rev − λ·sft` too, the 1.5B entanglement result is an operator artifact. §6 is void. |
| **Part III Gate 1** | ~5 GPU-h, no training | `oracle_bestof8 − merge_dare_ties` on the composites. **≤2 pts ⇒ stop** and report the negative RQ2 finding. |
| **Part III Gate 1b** | free | If the S1 specialist drops as much on `C_L1r_S1` as on `L1r`, composites are merely *harder*, not compositional, and there is nothing to route. |
| **Part III Gate 2** | +3 GPU-h | `mole_router` must beat `mole_uniform` by ≥2 pts **and** gate entropy must be <0.9·log 8 in half the layers. |
| **`mole_random`** | ~1 GPU-h | **The control that decides the headline.** If `mole_router ≈ mole_random`, the gain is rank-256 residency, not routing, and the headline must say so. |
| **Part V Stage 2** | ~16 GPU-h | If merge-optimal ≈ accuracy-optimal, early stopping buys nothing here. Report and stop. |

---

## 10. Defects found, and what they invalidated

Nine defects were found in the last three days. **Every one was silent**, and every one was the same
shape: *an identifier or code path that does not encode what actually varies.*

| defect | what it did | status |
|---|---|---|
| `compute_is_core` unscoped by experiment | transfer matrix on 23 of 340 programs; **invalidated an RQ1 claim that had been reported** | fixed, claim withdrawn (§2) |
| HumanEval+ scorer `KeyError` under a bare `except` | every forgetting number was 0.0 | fixed, §5 is the repaired table |
| `adapter_dir` ignored training length | 9-epoch configs would overwrite the 3-epoch bank | fixed before any checkpoint was lost |
| `eval_hf` rendered a different prompt from the accuracy grid | soft-vs-hard comparison across two prompt distributions | fixed |
| `grid_rq1.yaml` hard-coded Python merge paths under two languages | latent cross-language leak | fixed + guard |
| composite purity vacuous **and H1 content scan skipped** | mislabelled composites would enter training unscanned | fixed today |
| `base` through the mixture engine was not base | every ladder delta measured against a mixture | fixed today |
| `t2_merge_optimal` ran the epoch sweep | Stage 1 would have been reported as evidence for Stage 2 | renamed today |
| **`cft` arm in three 7B unlearning configs pointed at the 1.5B adapter** | a 1.5B LoRA loaded onto a 7B base, scored under a real arm's label | **found today, fixed** — see the correction below |
| **`_extends` merges `systems:`, injecting arms no config declares** | the root cause of the row above; ALL SIX unlearning runs carried an undeclared `cft` arm, and on 2026-08-11 it killed four evaluations outright | **found and fixed later the same day** |

The last one deserves emphasis because it is live. `configs/unlearn/negation_qwen25c-7b_*.yaml`
extends the **1.5B** `cft/eval/bidir_v1.yaml` and inherited its `cft` path unchanged. It did not
crash: it produced **86.5% base-identical outputs** and looked like a weak arm.
`assert_adapter_effective` did not fire, because 13.5% of outputs did differ. `e2_budget_qwen7b.yaml`
carries a comment explicitly warning about this trap — the fix was known and had simply not been
applied to `configs/unlearn/`.

Preflight missed it because **preflight only walks `/eval/` and `/train/` paths, and these live
under `configs/unlearn/`**. A `check_cross_model_adapters()` covering every config now exists and
was verified with a negative control (reintroduce the bug → 1 error; restore → 0 errors).

**Consequence for the results**: the `cft` row in the three unlearning runs is invalid and must be
regenerated. It is not load-bearing — Part IV's argument rests on `flip`/`rev`/`u_lam*`, all of
which pointed at correct 7B adapters — but any table reproducing that `cft` row is wrong.

> **Correction, later on 2026-08-11.** The account above identifies the symptom, not the cause,
> and understates the scope.
>
> The cause is not that a path was inherited unchanged; it is that **`_extends` merges `systems:`
> at all**. `load_config`'s `_deep_merge` recurses into dicts, and `systems:` is a dict, so a
> child's block UNIONS with its parent's. No unlearning config ever declared a `cft` arm — the
> parent `cft/eval/bidir_v1.yaml` did, and it was injected into all six.
>
> So the 1.5B runs are affected too, which the entry above misses. There the inherited path was a
> valid 1.5B adapter, so nothing looked wrong and no guard fired — but
> `results/2026-08-10_cft-bidirectional/qwen25c-1.5b/python/unlearn_negation_python/report.md`
> carries a `cft` row (8.6 % reverse) in an experiment whose config does not contain the word.
> **Every unlearning table with a `cft` row is wrong, at both scales**, and roughly 1/12 of every
> unlearning cell's GPU time went to an arm nobody asked for.
>
> The fix recorded above — overriding `cft:` in the 7B configs — was applied by hand to files
> headed *"Generated by scripts/unlearn/20_negation_sweep.py — do not hand-edit"*, and the
> generator did not emit it. The next regeneration would have silently restored the bug.
>
> `check_cross_model_adapters()` would not have caught the 1.5B case either: the adapter is the
> right model, it is the *arm* that is spurious. The real fix is at the loader —
> `_replace: [systems]` declares a block exhaustive (`src/obtune/config.py`), the generator now
> emits it, and `tests/test_config_extends.py` asserts no unlearning config resolves to an arm it
> does not declare. The SRH eval configs deliberately keep merge semantics: they declare only
> their new arms and inherit `base`/`sft`/`cft` as references, and their tables contain those arms.
>
> This surfaced because the CodeBLEU guard (§ same day) let the cells run far enough to reach the
> §4.2 adapter check, where the 1.5B `cft` arm produced base-identical output on all 3000 trials
> and killed the cell. Full account: `log/cft-replication/2026-08-11_codebleu-scoring-hang.md`.

---

## 11. Open items needing a human decision

1. **12 orphaned duplicate merge cells** (`ties_e6/e9`, `dare_ties_e6/e9`) await deletion approval
   per CLAUDE.md §2. Nothing will touch them until you say so.
2. **The invalid `cft` cells** from the three 7B unlearning runs need regeneration, which means
   deleting those cell directories so `resume` does not skip them. Same rule — your call.
3. **`stats/R/config.R` needs the composite levels** before any `C_` trial reaches the R stack;
   `01_schema_validate.R` would reject them today.
4. **H1 access budget.** Part III's natural home is H1, where no expert is correct, but the two
   granted passes are both open. The stacked conditions carry the headline without it, and the
   current plan spends no further H1 access. Recorded here so the decision is explicit.

---

## 12. Update — 2026-08-12

Two things happened today that change what this report says. Read this section before §6.

### 12.1 The Part IV controls landed, and they argue AGAINST the entanglement reading

§6 reported an 18.8 pt over-removal at 1.5B as "the SRH signature", and flagged that it was
**blocked** pending the `rev − λ·sft` and `mix50 − λ·sft` controls. Those controls have now run
to completion. `REV` never saw forward data, so if its reverse collapses under the same
operator, the effect is the operator damaging whatever adapter it is pointed at rather than
evidence of shared representation.

**Reverse collapses in the REV arm too.**

| λ | `rev−λ·sft` fwd | `rev−λ·sft` **rev** | `mix50−λ·sft` fwd | `mix50−λ·sft` **rev** |
|---|---|---|---|---|
| 0 | .887 | **.313** | .901 | **.306** |
| 0.25 | .876 | .297 | .885 | .305 |
| 0.5 | .872 | .243 | .800 | .285 |
| **0.75** | .784 | **.164** | .807 | **.177** |
| 1.0 | .118 | .107 | .794 | .119 |
| 1.25 | .003 | .015 | .013 | .021 |

At the λ=0.75 operating point, `rev−λ·sft` falls **.313 → .164**. The FLIP arm in §6 falls
**.314 → .126**. Those are the same collapse, and REV has no forward direction to remove.

**Reading:** the 1.5B "entanglement" signature is most likely the negation operator degrading
any adapter it is applied to, not the collateral removal of a shared representation. §6's
1.5B conclusion should be treated as **not supported** until the curves are compared formally
(matched-λ, matched-norm). The 7B result in §6 — surgical removal, reverse survives — is
unaffected by this, since it was already the *disjoint* reading.

This is the control doing exactly its job, before the claim went anywhere.

### 12.2 A scoring bug failed six runs and corrupted two fields

`score_trials` builds a `prepared` list in a pre-pass (so CodeBLEU can be batched) and walks it
in a second loop. The row construction read `"output_raw": raw`, but `raw` was **not** in the
tuple that loop unpacks — so it resolved to the enclosing scope and held the *last* generation
of the pre-pass. Every row stored the same string.

`assert_adapters_effective` compares `output_raw` between systems, so it was comparing a
constant against itself and reported **every** system as identical to base. Six runs were
failed by the comparison, not by the model. The adapters were never at fault — verified on GPU
that vLLM applies per-prompt LoRA correctly, including the mixed `[None, lora]` list this code
passes.

**Introduced by the CodeBLEU parallelisation on 2026-08-11**, which is what split that loop.

| affected | not affected |
|---|---|
| `output_raw` — one constant per run | `exec_pass_rate`, `forward_success_exec`, `reverse_success_*` |
| `identity_output` (derived from it) | CodeBLEU (`codebleu_target`/`_other`) |
| `assert_adapters_effective` verdicts | readability, identifier recall |
| — | **every table in §2–§7 of this report** (those runs predate the refactor) |

The metric columns are computed from `pred`, which was always correct. **The echo/identity rates
in §4.2 and §4.8 come from the 2026-08-10 runs and therefore stand**; any identity rate from a
2026-08-11-or-later `cft/evaluate` run does not.

Fixed, pinned by a regression test, and the seven jobs it falsely failed were requeued — the
first two have since completed cleanly (1299 s and 1311 s).

### 12.3 Infrastructure: three failures that cost a day

| failure | consequence | fix |
|---|---|---|
| eval raised, then hung in multiprocessing's atexit joining a vLLM `EngineCore` | claim never left `running/`; **18 h with both GPUs idle** | hard exit after printing the traceback |
| dead job stranded its engine (~41 GB, ppid 1) | GPUs unusable, nothing self-healed | `worker --reap-stranded-gpus`, in `ensure_infra` |
| nothing restarted the pipeline itself | remaining ~53 GPU-h would never run | `scripts/watchdog.sh`, tested against `kill -9` |
| a stalled job blocked the queue | 18 h, again | `worker --kill-stalled` (CPU-tree based) |

Two bugs **in those fixes**, both found and corrected: `kill_stalled` watched the *worker* pid
(which blocks in `subprocess.run()` and burns no CPU), making it a blanket 30-minute timeout on
all work — it was minutes from killing a healthy job generating at 99% GPU; and it sent only
SIGTERM, which a process wedged in interpreter shutdown ignores, leaving the engine holding the
card. Both now measure/kill the whole process tree.

### 12.4 Part III — corpus built, two design bugs caught before any GPU time

The composite corpus is **built and verified**: Python **1656/2231 (74%)** and JavaScript
**665/674 (99%)** common subset across all six stacked conditions; `make check` clean at 64
files / 184,803 rows with no H1 labels or markers. `train_mole --dry-run` now runs on the real
input — 60,639 train / 4,329 val, 0.000% truncation.

Two defects were found in code that had never executed:

1. **The gate would have been trained on the wrong task** — `cft.prompts.build_gen_messages`
   ("Obfuscate the following code" → a program) while `eval_mole` scores output prediction
   ("Return value:" → a value). It would have trained cleanly and produced a number answering
   no question. Now routed through `data.build_sft_splits`, the path the eight experts used.
2. **Merge-optimal candidate names did not encode the other experts' epochs**, so a restart
   mid-search would have silently scored the wrong merge.

Test suite is now **529 passing** (was 432 on 2026-08-11).

---

## Changelog

- **2026-08-12** — Added §12. Corrects §6: the Part IV controls argue against the 1.5B
  entanglement reading. Records the `output_raw` scoring bug (six runs falsely failed; two
  fields corrupted, metrics unaffected), the four infrastructure fixes, and the Part III
  corpus build.

- **2026-08-11** — Rewritten over 597 cells (was 453). Adds §4 (7B refutation), §6 (Part IV
  unlearning at both scales, incl. the scale dissociation), §7 (Part V geometry on two banks),
  §8 (forward schedule), and §10's cross-model adapter defect found while assembling this report.
  Withdraws the 2026-08-10 "transfer into L1b fails" claim.
