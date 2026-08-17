# ATTRIB workshop paper — experiment plan

*Last updated: 2026-08-10*

Target: ATTRIB @ NeurIPS 2026, main track, 3–6 pp, non-archival. Deadline **Sept 1 AoE**,
freeze **Aug 28**. Paper: *The Free Flip*. This document plans the follow-up experiments in
`workshop_targets.md` against what the repo actually contains as of today.

**Headline of this plan: the critical path got much shorter.** E1's expensive branch does not
fire, E6 and E7 are already answered, E8 is answerable with zero GPU, and three trained arms
have never been evaluated. What was "1–3 training runs on the highest-risk item" is now a
reading task; what remains is ~11 training runs, none of them load-bearing.

---

## 0. What landed on 2026-08-10 (results, not plan)

Items E, F and G of §3 are **done**. Two evaluation passes over adapters that already existed
produced the paper's central attribution table and closed the budget objection at the headline
tier. Full write-up:
[`../log/cft-replication/2026-08-10_factorial-and-objective-verdict.md`](../log/cft-replication/2026-08-10_factorial-and-objective-verdict.md).

### The 2×2 — this is now the paper's headline table

`e2_factorial_qwen1.5b`, 300 programs, 18 000 trials, strict reverse success:

| | forward only | + reverse data |
|---|---|---|
| **no aux objective** | `sft` 0.3 % | `flip` 31.4 % |
| **contrastive aux** | `cft` 0.3 % | `cftflip` 31.1 % |

| effect | estimate (pp) | 95 % CI |
|---|---|---|
| **data direction** | **+30.9** | [+29.3, +32.6] |
| **contrastive objective** | **−0.2** | [−0.7, +0.3] |
| interaction | −0.3 | [−1.3, +0.7] |

The objective's contribution is not merely non-significant — it is **bounded under one percentage
point in either direction, at both levels of the data factor, with no interaction**. That is a
stronger statement than any pairwise comparison in the current draft, and it is stated in exactly
the vocabulary ATTRIB uses.

`base` scored 2.9 %, reproducing the published 2.9 % exactly — the program-set consistency anchor
held, so these numbers are directly comparable to the existing tables.

### The budget controls at 7B — `mix50`'s missing headline number

`e2_budget_qwen7b`, 300 programs, 21 000 trials, strict: `base` 12.9 · `sft` 0.0 · `cft` 0.1 ·
`fwd2x` 0.1 · `mix50` **32.8** · `rev` 32.9 · `flip` 33.5.

| contrast | Δ (pp) | 95 % CI |
|---|---|---|
| `mix50` − `sft` | **+32.8** | [+31.3, +34.4] |
| `flip` − `mix50` | +0.7 | [−0.3, +1.8] |
| `fwd2x` − `sft` | +0.1 | [+0.0, +0.2] |
| `sft` − `base` | **−12.9** | [−14.9, −10.9] |

`mix50` is matched to `sft` on instances, sequence tokens and optimizer steps while receiving
strictly *less* supervised signal, and `fwd2x` is forward-only at double the compute. **The
budget objection is closed on every axis at the paper's own model scale.** `cft` echoes its input
29.3 % of the time at 7B against `sft`'s 18.2 % — the method sold as the cure for echoing exhibits
it more than the disease does.

### Queued as of this writing

`mix5`/`mix10`/`mix25` at 1.5B (the dose ladder, training now on three GPUs) · `sft`/`cft` at
seed 42 (E2) · `forget7b` for `cft` and `mix50`.

Dose-ladder composition was verified on CPU before launch: **7 384 instances at every dose**
(identical to `fwd`), reverse share 5.0 / 10.0 / 25.0 / 50.1 %, and **zero programs appearing in
both directions** at any rung — so the curve varies exposure and nothing else.

---

## 1. Four findings that change the plan

### 1.1 E1 is resolved: our `cft` arm *is* their method

The gate question was whether Nikiema et al.'s contrastive objective operates at the loss level
(InfoNCE / triplet / margin in embedding space), in which case our judgment-as-SFT arm is not
their method and "CFT does nothing" collapses. **It does not.** From the paper:

> L_CFT = L_pos + L_neg + L_gen  (eq. 5)
> • L_pos: Learns to recognize when original and obfuscated code are functionally equivalent
> • L_neg: Learns to detect when code has different functionality
> • L_gen: Learns to generate obfuscated code

and, decisively, the data construction:

> CFT uses balanced triplet datasets across transformation types. For open-source models, we
> construct 30 000 instances (10 000 each for positive classification, negative classification,
> and obfuscation task generation). … **Positive classification involves semantically equivalent
> code pairs requiring binary equivalence decisions.**

Three independent confirmations that this is multi-task supervised fine-tuning, not metric
learning:

1. The three terms are described only as **instance pools with counts**. "Triplet" in this paper
   means *three tasks*, not triplet loss. The words InfoNCE, margin, cosine, temperature, and
   embedding do not appear anywhere in the paper.
2. Two of the three headline CFT numbers — GPT-4.1-Mini 52.03 %, GPT-3.5-Turbo 50.51 % — come
   from models fine-tuned through **"provider-optimized fine-tuning protocols"** (§3.1), i.e. the
   OpenAI fine-tuning API, which accepts only supervised input→output text pairs. A custom
   embedding-space loss is *impossible* on those models. Whatever produced the headline number is
   expressible as training instances.
3. Open-source models use plain **LoRA** (§3.4), with no mention of a modified objective.

**Consequence.** No faithful reimplementation is needed. `src/obtune/cft/` implements the paper's
method as described. E1 drops from 1–3 training runs plus a reading to **a documentation task
(~2 h)** — write the quotes above into §3.2 and the limitations so the objection is answered
before it is raised.

**What survives of E1 as a real vulnerability: the pool ratio.** The paper is 1 : 1 : 1
(10 000 each). Ours is:

| pool | rows | ratio |
|---|---|---|
| `gen` | 7 912 | 1.00 |
| `pos` | 7 912 | 1.00 |
| `neg` | 6 021 | **0.76** |

`neg` is 24 % short because mutants must survive execution verification (`min_ok_fraction: 0.5`).
This is the one place a reviewer can say "you starved the contrastive signal." The analytic
answer is already in hand — CFT's loss is **97.7 % L_gen / 1.13 % L_pos / 1.13 % L_neg** by token
share, so restoring `neg` to parity moves the auxiliary share from 2.26 % to ~2.6 % and cannot
plausibly produce a 30-point swing. **Recommendation: state the ratio and the token-share
arithmetic in-text; run the 2× `neg` sweep only if a GPU is idle.** It is insurance, not a
dependency.

### 1.2 E6 is done, and the branch fired the "honest reframe" way

The HumanEval+ harness described as broken in `MASTER_REPORT_2026-08-10.md` §8.3 was repaired and
run **this morning** (05:53–06:26). The old `pass@1 = 0.0` was a `KeyError` on `expected_output`
swallowed by a bare `except: continue`; `forgetting.py` now computes ground truth via
`get_groundtruth` and refuses to report if >10 % of tasks error. §8.3 is stale.

HumanEval+ pass@1, Qwen2.5-Coder-1.5B, all seven arms:

| arm | `base` split | `plus` split | Δ plus vs. untouched |
|---|---|---|---|
| `base` — untouched | .7134 | **.6463** | — |
| `sft` — forward only | .3720 | **.3293** | **−31.7** |
| `cft` — contrastive | .4085 | .3659 | −28.0 |
| `mix50` | .5427 | .4695 | −17.7 |
| `flipsym` | .6098 | .5427 | −10.4 |
| `flip` | .6159 | .5122 | −13.4 |
| `rev` — reverse only | .6280 | .5854 | −6.1 |

**At 1.5B the damage is general, not directional** — forward-only SFT costs ~32 points of
HumanEval+ while raising forward obfuscation accuracy. That reads as narrow-task overfitting
rather than a targeted suppression of the reverse direction.

**But 7B inverts it, and 7B is the tier the headline lives at.** Run since:

| arm | 1.5B `plus` | 7B `plus` | 7B Δ vs base |
|---|---|---|---|
| `base` | .646 | .805 | — |
| `sft` | .329 (−31.7) | **.817** | **+1.2** |
| `cft` | .366 (−28.0) | .799 | −0.6 |
| `flip` | .512 (−13.4) | .744 | **−6.1** |
| `mix50` | .470 (−17.7) | .732 | **−7.3** |

At 7B, forward-only SFT keeps its general coding ability intact — slightly *improves* it — while
its reverse capability goes 12.9 % → 0.0 %. That is the stronger and stranger version of the
claim: **directional suppression, with general capability held**. The 1.5B collapse is a
small-model effect and must be reported as one, not generalized.

Two consequences the paper has to absorb honestly.

**First, §3.1 can claim directional suppression at 7B and must not claim it at 1.5B.** The
forward-only arms preserve general coding ability at the headline tier while losing the reverse
direction entirely.

**Second — and this one touches the title — the prescription is NOT free at 7B.** The
bidirectional arms cost 6–7 points of HumanEval+ (`flip` −6.1, `mix50` −7.3) where the
forward-only arms cost nothing. `mix50` is *not* cheaper than `flip` here, so the hoped-for
"cheapest on every axis" story does not hold: `mix50` is the cheapest arm on **training budget**
(instances, supervised tokens, FLOPs, steps) and the most expensive of the two on **retained
general capability**.

*The Free Flip* is therefore precise only if "free" is scoped to training cost. The paper must say
in §3 and again in limitations: **bidirectional data buys +32.8 pp of reverse capability at zero
training-budget cost and roughly −7 points of HumanEval+.** Stating that plainly is much stronger
than having a reviewer discover it — and the trade is still overwhelmingly favourable, which is
the argument to make.

Still open: MBPP (optional — HumanEval+ already carries the claim).

### 1.3 E7 is answered at 7B, from data already on disk

`bidir_qwen7b` ran base/sft/cft × 4 prompting strategies × 300 programs × 5 conditions
(22 500 generations) and stored `reverse_success_strict` per trial. Recomputed today, **strict**
reverse success:

| system | `simple` | `few_shot` | `cot` | `augmented` |
|---|---|---|---|---|
| `base` — untouched | 13.0 % | 17.7 % | **21.8 %** | 21.6 % |
| `sft` — forward only | 0.0 % | 2.0 % | 5.5 % | 4.8 % |
| `cft` — contrastive | 0.1 % | 0.5 % | 1.5 % | 1.3 % |

Two consequences, both good:

- **The sharpest sentence in the paper is now available:** the fine-tuned model under its *best*
  prompt (`sft`, cot, 5.5 %) is less than half the untouched model under its *worst* prompt
  (`base`, simple, 13.0 %). Prompting does not rescue what fine-tuning removed, and the removal is
  larger than the entire prompting range.
- **The headline survives the recontextualization.** `flip` at 7B scores 33.6 % strict under
  `simple`; the best any prompt buys the untouched base is 21.6 %. The flip effect is not an
  artifact of comparing against a badly-prompted baseline.

**Residual gap:** `flip`/`mix50` were only ever run under `simple`. A reviewer will ask why the
baseline got four strategies and the winning arm got one. One eval pass closes it (§3, item H).

### 1.4 E8's claim as written is not supported; the restated claim is stronger

§4 currently asserts the source paper's renaming "success" passes outputs with **near-zero**
identifier recall. Computed at 7B (`simple`, reverse):

| system | cond | paper criterion | strict | id-recall *among passes* | id-recall *among all* | n passes |
|---|---|---|---|---|---|---|
| `base` | `L1b` | 4.3 % | 2.3 % | 0.342 | 0.363 | 13 |
| `base` | `L1r` | 19.7 % | 11.0 % | **0.434** | **0.423** | 59 |
| `base` | `L2` | 19.3 % | 10.3 % | **0.430** | **0.419** | 58 |
| `base` | `S1` | 64.7 % | 33.3 % | **0.899** | — | 194 |
| `base` | `S2` | 10.0 % | 8.0 % | 0.739 | — | 30 |

Id-recall among paper-criterion passes is ~0.43, not ~0. **Do not write "near zero."** The
defensible — and sharper — claim is that **the criterion is uninformative**: on `L1r`, outputs
that pass it recover 0.434 of the original identifiers while outputs in general recover 0.423.
Passing the paper's test tells you essentially nothing about whether identifiers were recovered
(Δ = 0.011). Contrast the information-preserving transforms, where passes carry 0.899 id-recall
on `S1`. And the criterion inflates: 19.7 % vs 11.0 % strict on `L1r`, but 10.0 % vs 8.0 % on
`S2` — the gap between the two criteria is itself a function of whether the transform is
invertible.

**The floor has now been computed** (`scripts/srh/23_metric_tables.py`), and it is what makes the
table publishable. `floor` = `identifier_recall(obfuscated_source, original_source)` over the same
programs — what copying the input scores:

| cond | paper % | strict % | id-rec passes | id-rec all | **floor** | passes − floor |
|---|---|---|---|---|---|---|
| `L1r` | 19.7 | 11.0 | 0.434 | 0.423 | **0.349** | +0.085 |
| `L2` | 19.3 | 10.3 | 0.430 | 0.419 | **0.389** | +0.041 |
| `L1b` | 4.3 | 2.3 | 0.342 | 0.363 | **0.354** | −0.012 |
| `S1` | 64.7 | 33.3 | 0.899 | 0.907 | **1.000** | −0.101 |
| `S2` | 10.0 | 8.0 | 0.739 | 0.878 | **1.000** | −0.261 |

Corpus-computed and observed floors agree where both are estimable (`L1b`: 0.354 vs 0.356 over
76–179 echoed trials), so the floor is trustworthy.

Two things follow, and both belong in §4. **(a)** On `L1r`, outputs certified by the paper's
criterion recover 0.085 more of the original identifiers than copying the input does, and 0.011
more than the model's own average output — the criterion certifies almost nothing about recovery,
while passing at nearly double the strict rate. **(b)** Identifier recall is only a usable
instrument on renaming: the structural transforms have a floor of **1.000**, because flattening and
dead-code insertion preserve every original identifier. Do not report id-recall for `S1`/`S2` as
though it discriminated.

---

## 2. A framing correction that is not optional

The manuscript says the source paper "never ran the obvious baseline." That is **not accurate as
stated**, and Nikiema et al. may review this submission. From §5.0.2:

> Comparative Evaluation Framework. CFT effectiveness is assessed through comparison against
> Standard Fine-Tuning (SFT) using and **Bidirectional Fine-Tuning (BFT) using forward generation
> plus reverse deobfuscation tasks.**

BFT — forward + reverse — *is* our `flip` arm, and the paper names it in its evaluation framework.
It then **reports no BFT results anywhere**: the string appears exactly once in the paper, Figure 4
has only SFT and CFT columns, and no table, figure or sentence carries a BFT number.

The correct sentence is therefore: *the paper names bidirectional fine-tuning as a comparison
condition and reports no results for it.* This is more defensible than the current framing and
strictly better rhetoric — a declared-but-unreported baseline is a sharper gap than an unnoticed
one. Fix it in the abstract, §1 and §5 before anything else; it is a one-line change that removes
the single most embarrassing possible reviewer comment.

---

## 3. Revised work list

Ordered by value per GPU-hour, not by tier. Items A–D need **no GPU** and can start now while
`fwd2x` finishes.

### Zero-GPU (do first — ~1 day total)

| | item | effort | why now |
|---|---|---|---|
| **A** | Write the E1 fidelity documentation from §1.1 quotes into §3.2 + limitations | 2 h | Retires the desk-kill risk outright |
| **B** | Fix the BFT framing (§2) throughout | 20 min | Correctness; reviewer-facing |
| **C** | Build the E8 table with the echo-input floor row; restate the §4 claim per §1.4 | 3 h | Converts the sharpest paragraph to a demonstration, honestly |
| **D** | Write E6 (§1.2) and E7 (§1.3) into §3.1 and Table 2 | 3 h | Two planned experiments already have answers |

### One eval pass, no training (highest value per GPU-minute)

| | item | cost | why |
|---|---|---|---|
| **E** | **`mix50` @ 7B — trained, never evaluated** | ~30 min | **The decisive arm is missing at the headline tier.** `runs/adapters_srh/qwen25c-7b/python/all5_mix50_r32_s17/final` exists; `configs/srh/eval/e1_qwen7b.yaml` omits it on a now-stale comment. §3.3's "same examples/steps/less supervision" claim currently has no 7B number. |
| **F** | `fwd2x` @ 7B eval | ~30 min | Finishes training in ~1 h (checkpoint 580/696). The compute-matched forward-only control — kills "flip just trained longer" on the FLOPs axis, which `mix50` does not cover. |
| **G** | **`cftflip` @ 1.5B eval — trained, never evaluated** | ~20 min | Completes a **2×2 factorial**: `sft` (neither) / `cft` (objective only) / `flip` (data only) / `cftflip` (both). This is literally ATTRIB's remit — isolating an algorithmic factor against a data factor — and it costs one eval. Promote it into §3 as a headline table. |
| **H** | `flip` + `mix50` × 4 prompting strategies @ 7B | ~1 h | Closes the asymmetry in §1.3: the baseline got four strategies, the winning arm one. |
| **I** | HumanEval+ on the 7B arms | ~2 h | Carries §1.2's general-damage result to the headline tier. Inference only. |

**Items E and G are the two highest-value actions in this document.** Both are trained adapters
sitting unevaluated on disk, and both fill gaps in claims the paper already intends to make.

### Training runs, in priority order

| | item | runs | est. GPU-h | notes |
|---|---|---|---|---|
| **J** | **E4 dose–response** — `mix5`, `mix10`, `mix25` @ 1.5B | 3 | ~8 | `direction_mix.reverse_fraction` is already a config knob (`srh/arms.py`). Three configs, no code. **This is Fig 1.** |
| **K** | E2 seeds — `sft` s42, `cft` s42 @ 1.5B | 2 | ~6 | s42 already exists for `rev`/`flip`/`mix50`/`flipsym`; only the two load-bearing forward arms are missing. |
| **L** | E4 anchor — one `mix10` @ 7B | 1 | ~10 | Optional; confirms the curve at the headline tier with a single point. |
| **M** | **E3 replication — JavaScript, not Java** | 4 | ~6 | See §4. `sft`/`cft` JS configs already exist; JS corpus is fully built and gate-validated. |
| **N** | E5 cross-transformation (train S1-only reverse, test S2) | 2 | ~6 | `_base_srh.yaml` already anticipates it (`program_subset: "common"`). Punt first if time runs out. |

Total: ~11 training runs, ~26 GPU-h at 1.5B (+10 optional at 7B). With two free GPUs that is
**~2 days of wall clock**, comfortably inside the window.

---

## 4. E3: substitute JavaScript for Java

**Java is not feasible in this window.** The box has a JRE (`/usr/bin/java`) but **no `javac`** —
a Java replication needs a JDK install, a CodeNet Java subset, obfuscators for Java, and a
compile-plus-test harness, against ~3 weeks minus a Kyoto presentation and an intercontinental
move. The plan's own timebox (~Aug 27) would almost certainly expire.

**JavaScript costs almost nothing and answers most of the question.** The JS corpus is fully
built: 168 programs, all six conditions, semantics-gated, with `javascript-obfuscator` installed
and `configs/cft/train/{sft,cft}_qwen1.5b_js.yaml` already written. `configs/cft/data_v1.yaml`
already lists `javascript`. Four 1.5B runs (`sft`, `cft`, `mix50`, `flip`) plus one eval reuses
the entire pipeline.

Be precise about what this buys. JavaScript answers **"is the effect Python-specific?"** It does
*not* answer **"is the effect Java-specific?"**, which is the literal form of the reviewer
objection. The limitations sentence must say so: *we replicate in a second language; the source
paper's Java setting remains untested here.* That is a weaker but honest claim, and it is a
markedly better position than a limitations paragraph with no second language at all.

Keep Java as a stretch goal only if a JDK turns out to be one `conda install` away.

---

## 5. Two decisions for you

**(1) Which tier carries the dose–response figure?** Recommendation: **1.5B for the curve, one 7B
anchor point.** The flip effect is nearly identical across tiers (31.5 % at 1.5B, 33.6 % at 7B),
so the curve's *shape* is not tier-sensitive, and 1.5B costs ~8 GPU-h against ~30. Item L adds a
single 7B `mix10` point to show the curve is not a small-model artifact. Override if you want
Fig 1 to live entirely at the headline tier.

**(2) E3 language** — JavaScript per §4, unless you want to spend the Java toolchain cost.

---

## 6. Schedule

| Date | Work |
|---|---|
| **Aug 10 (today)** | Items A–D (zero GPU). Queue E–G as GPUs free; `fwd2x` finishes ~11:30. |
| **Aug 11–13** | Items H, I. Launch J (dose–response) and K (seeds) — 2 GPUs, ~1.5 days. ATTRIB OpenReview verification checklist. LaTeX skeleton with current numbers. |
| **Aug 14–18** | Full draft v1 from `story.md`, limitations written first. Launch M (JS replication) and N (cross-transform) behind J/K. Freeze before Kyoto prep. |
| **Aug 19–21** | Kyoto. No paper work. |
| **Aug 22–24** | Fold in J/K/M results. Draft v2. Pack. |
| **Aug 25–26** | Travel. |
| **Aug 27–28** | **Results freeze.** Anything unlanded becomes a limitation. Draft v3. |
| **Aug 29–31** | Polish: every strong claim carries its CI in-sentence, tone audit, page compression, anonymization. |
| **Sept 1 AoE** | Submit; register reciprocal reviewer same day. |

**Freeze rule unchanged:** whatever has not landed by **Aug 28** ships as a limitation, not a
delay. With E1 resolved, there is no longer any single experiment the paper cannot survive losing.

---

## 7. Documentation debt created by today's findings

- `MASTER_REPORT_2026-08-10.md` **§8.3** — stale. The HumanEval+ harness is repaired and run;
  numbers in §1.2 above.
- `MASTER_REPORT_2026-08-10.md` **§7.6** — stale. `cftflip` is trained at 1.5B; `fwd2x` is
  training at 7B now. Both listed as "never trained".
- `configs/srh/eval/e1_qwen7b.yaml` — the comment "`mix50` and `flipsym` are NOT listed: their 7B
  arms are not trained" is stale for `mix50`, whose 7B adapter is complete.
- `CFT_REPLICATION.md` — should record the §1.1 verdict (the objective is instance-level, not
  loss-level) and the §2 BFT correction, since both are replication-fidelity facts.
- A dated log entry under `log/cft-replication/` for today's E1 verdict and the E6/E7/E8 analyses.

---

## Changelog

- **2026-08-10** — Created. Resolves the E1 fidelity gate against the source paper (objective is
  instance-level, not loss-level); records that E6 and E7 are already answered and E8 is
  answerable without GPU; corrects the BFT framing; substitutes JavaScript for Java in E3;
  identifies `mix50` @ 7B and `cftflip` @ 1.5B as trained-but-unevaluated arms.
- **2026-08-10 (rev 2)** — §0 added with the results of items E/F/G: the 2×2 factorial at 1.5B
  (objective effect −0.2 pp [−0.7, +0.3]) and the 7B budget controls (`mix50` − `sft` = +32.8 pp).
  §1.2 corrected — 7B **inverts** the 1.5B general-capability finding, so the damage is
  directional at the headline tier and the prescription is not free there. §1.4 completed with
  the measured echo floor, which is what makes the E8 claim publishable.
