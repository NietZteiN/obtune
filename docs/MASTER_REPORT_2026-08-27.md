# obtune — master results report

**27 August 2026 · everything run to date, in one frame.**

*Supersedes [`MASTER_REPORT_2026-08-12.md`](MASTER_REPORT_2026-08-12.md), of which this is the
direct continuation, and through it the 08-11 and 08-10 revisions — the Changelog records what
each revision added. **Since 12 August:** RQ2 closed negatively and in full (§12.10–§12.13, and
the standalone closing report); **RQ3 run for the first time and given a causal leg** (§15);
a **new `normalization` thread** that gives the project's one positive transfer a mechanism
(§16); the CFT side thread's two central claims overturned by a held-out benchmark (§7.8); and
two measurement problems found that affect how every number in this document should be read
(§8.9, §8.10).*

Scope: all **2,215** evaluation cells / **1,046,382** graded trials under `results/cells/`
(1,918 cells at 1.5B/Python, 227 at 1.5B/JavaScript, 70 at 7B/Python), plus the CFT/bidirectional
side thread (51 `results/forgetting/` probes), the RQ3 attention corpus (3,600 dumps under
`results/attn/`), and the zero-training normalization arms. Every number below was recomputed
from raw per-trial data — by [`scripts/make_master_report.py`](../scripts/make_master_report.py)
→ `results/analysis/master_report.json` for the tables inherited from the 08-12 revision, and
directly from the per-cell parquets for everything added since. **None are copied from earlier
documents.** Where a number here disagrees with an earlier report, **this document is the one to
trust** and §8 says why.

**Companion documents.** [`MASTER_REPORT_2026-08-27_router-and-merging.md`](MASTER_REPORT_2026-08-27_router-and-merging.md)
is the closing report for RQ2 alone, written self-contained for a reader who has never seen the
project; §5 and §12 here are the same content in its project context.
[`REPORT_2026-08-26_rq3-attention-mechanism.md`](REPORT_2026-08-26_rq3-attention-mechanism.md)
does the same for RQ3. [`RESULTS_BOOK_2026-08-11.md`](RESULTS_BOOK_2026-08-11.md) is the
tables-first sibling of this document and is **stale after 11 August**.

Model: Qwen2.5-Coder-1.5B-Instruct for **every table below except where a row or section says
otherwise**. Two documented exceptions, both 7B: the CFT side thread (§7) and the zero-shot
baseline panel added 2026-08-13 (§9.3). Never mix them in one table — 7B roughly doubles
accuracy on every condition, so a stray 7B row would dominate any 1.5B comparison.

Grid: **Grid B** (`testset`) for §12's baselines, **Grid A** (`heldout`) for the RQ1/RQ2
headlines. These are different program sets and CLAUDE.md forbids pooling them — `base` on
H1 reads 6.4 % on Grid A and 11.3 % on Grid B. Every table states its grid. **Grid B `H1` is
115 items over 27 programs and cannot support merge comparisons** — see §8.10.
Task: output prediction on **still-obfuscated** code, graded by execution-verified strict exact match.

---

## Contents

- [1. The one-paragraph answer](#1-the-one-paragraph-answer)
- [1.5 Where this sits in the literature — and what routing does *not* show](#15-where-this-sits-in-the-literature--and-what-routing-does-not-show)
  - [1.5.1 The gap this work occupies](#151-the-gap-this-work-occupies)
  - [1.5.2 Our advantages, stated as a reviewer would test them](#152-our-advantages-stated-as-a-reviewer-would-test-them)
  - [1.5.3 Routing is **not** a failure — it is a ceiling, and its real test has not been run](#153-routing-is-not-a-failure--it-is-a-ceiling-and-its-real-test-has-not-been-run)
  - [1.5.4 What would have to be true for the merging claim to survive review](#154-what-would-have-to-be-true-for-the-merging-claim-to-survive-review)
- [2. What exists — the inventory](#2-what-exists--the-inventory)
  - [2.1 How to read every table in this report](#21-how-to-read-every-table-in-this-report)
  - [2.2 Every system, every obfuscation level, one table](#22-every-system-every-obfuscation-level-one-table)
- [3. RQ1 — the transfer matrix](#3-rq1--the-transfer-matrix)
  - [3.5 The `S2` exception — the most interesting result in the project](#35-the-s2-exception--the-most-interesting-result-in-the-project)
  - [3.6 Cross-language: the same shape, with larger swings](#36-cross-language-the-same-shape-with-larger-swings)
  - [3.7 Seed stability](#37-seed-stability)
- [4. Breadth does not help, and capacity is not the reason](#4-breadth-does-not-help-and-capacity-is-not-the-reason)
- [5. RQ2 — modularity: can six specialists be combined into one system?](#5-rq2--modularity-can-six-specialists-be-combined-into-one-system)
  - [5.0 The question, in plain terms](#50-the-question-in-plain-terms)
  - [5.1 What was actually built](#51-what-was-actually-built)
  - [5.2 The results](#52-the-results)
  - [5.3 Does over-training the experts explain why merging fails?](#53-does-over-training-the-experts-explain-why-merging-fails)
  - [5.4 RouterLoRA — the arm §5.2's saturated router implies](#54-routerlora--the-arm-52s-saturated-router-implies)
- [6. What the base model's weakness does to every number](#6-what-the-base-models-weakness-does-to-every-number)
- [7. Side thread — CFT / bidirectionality (complete)](#7-side-thread--cft--bidirectionality-complete)
  - [7.0 The question and why it exists](#70-the-question-and-why-it-exists)
  - [7.1 The seven arms](#71-the-seven-arms)
  - [7.2 Why measuring this is hard](#72-why-measuring-this-is-hard)
  - [7.3 Results at 1.5B](#73-results-at-15b)
  - [7.4 The per-transformation result inverts the paper](#74-the-per-transformation-result-inverts-the-paper)
  - [7.5 It holds at the paper's own model (7B)](#75-it-holds-at-the-papers-own-model-7b)
  - [7.6 What is left open in this thread](#76-what-is-left-open-in-this-thread)
  - [7.7 Approximate unlearning — and why its control matters more than its result](#77-approximate-unlearning--and-why-its-control-matters-more-than-its-result)
  - [7.8 A held-out benchmark overturns two of the thread's central claims](#78-a-held-out-benchmark-overturns-two-of-the-threads-central-claims)
- [8. Data-quality issues that must be resolved before any of this is written up](#8-data-quality-issues-that-must-be-resolved-before-any-of-this-is-written-up)
- [9. What has not been run](#9-what-has-not-been-run)
  - [9.1 The ICL baseline that has not been run — and why it matters most for FSE](#91-the-icl-baseline-that-has-not-been-run--and-why-it-matters-most-for-fse)
- [10. Suggested order of work](#10-suggested-order-of-work)
- [11. Shot count, and what happens when ICL meets a fine-tuned adapter](#11-shot-count-and-what-happens-when-icl-meets-a-fine-tuned-adapter)
  - [11.1 ICL saturates at two examples](#111-icl-saturates-at-two-examples)
  - [11.2 ICL and fine-tuning do not compose — demos make the adapter worse](#112-icl-and-fine-tuning-do-not-compose--demos-make-the-adapter-worse)
  - [11.3 The control adapter beats every zero-training baseline on held-out data](#113-the-control-adapter-beats-every-zero-training-baseline-on-held-out-data)
- [12. The zero-training baselines, the 7B ladder, and the hardened router](#12-the-zero-training-baselines-the-7b-ladder-and-the-hardened-router)
  - [12.1 The Grid A baseline panel is incomplete, and it is incomplete silently](#121-the-grid-a-baseline-panel-is-incomplete-and-it-is-incomplete-silently)
  - [12.2 What the Grid A panel does show, where it is complete](#122-what-the-grid-a-panel-does-show-where-it-is-complete)
  - [12.3 The 7B result constrains how the whole project may be framed](#123-the-7b-result-constrains-how-the-whole-project-may-be-framed)
  - [12.4 `mole_hardrouter`: the mixture is a selection, not a blend](#124-mole_hardrouter-the-mixture-is-a-selection-not-a-blend)
  - [12.5 The demo penalty on the adapter is not a formatting artifact](#125-the-demo-penalty-on-the-adapter-is-not-a-formatting-artifact)
  - [12.6 Where the remaining headroom is, in the order it is worth spending GPU on](#126-where-the-remaining-headroom-is-in-the-order-it-is-worth-spending-gpu-on)
  - [12.7 Optimising for out-of-distribution — the programme, and the rule that makes it reportable](#127-optimising-for-out-of-distribution--the-programme-and-the-rule-that-makes-it-reportable)
  - [12.8 What the RouterLoRA gate actually attends to — it is not routing](#128-what-the-routerlora-gate-actually-attends-to--it-is-not-routing)
  - [12.9 Why the gate does not route, and how to fix it](#129-why-the-gate-does-not-route-and-how-to-fix-it)
  - [12.10 The overnight run (14–15 August): routing was fixed, and it changed nothing](#1210-the-overnight-run-1415-august-routing-was-fixed-and-it-changed-nothing)
  - [12.11 Two attempted repairs (15–17 August), and both are null](#1211-two-attempted-repairs-1517-august-and-both-are-null)
  - [12.12 Redundancy, geometry, and the third repair (15–17 August)](#1212-redundancy-geometry-and-the-third-repair-1517-august)
  - [12.13 RQ2, closed](#1213-rq2-closed)
- [13. Glossary](#13-glossary)
- [14. Task-vector geometry — the whole thread, and what it turned out to measure](#14-task-vector-geometry--the-whole-thread-and-what-it-turned-out-to-measure)
  - [14.1 What a task vector is here, and how it is computed](#141-what-a-task-vector-is-here-and-how-it-is-computed)
  - [14.2 Every bank measured](#142-every-bank-measured)
  - [14.3 Within a fixed seed, the relative geometry is still meaningful](#143-within-a-fixed-seed-the-relative-geometry-is-still-meaningful)
  - [14.4 The test that matters: does geometry predict merged accuracy?](#144-the-test-that-matters-does-geometry-predict-merged-accuracy)
  - [14.5 The over-training hypothesis, in its final state](#145-the-over-training-hypothesis-in-its-final-state)
  - [14.6 Geometry as evidence *for* the RQ2 conclusion](#146-geometry-as-evidence-for-the-rq2-conclusion)
  - [14.7 What to carry forward](#147-what-to-carry-forward)
- [15. RQ3 — attention, and the mechanism for the one transfer that works](#15-rq3--attention-and-the-mechanism-for-the-one-transfer-that-works)
  - [15.1 The adapter really does re-anchor attention](#151-the-adapter-really-does-re-anchor-attention)
  - [15.2 The knockout, and two false starts worth recording](#152-the-knockout-and-two-false-starts-worth-recording)
  - [15.3 The causal result](#153-the-causal-result)
  - [15.4 What this licenses, and what it does not](#154-what-this-licenses-and-what-it-does-not)
- [16. Symbolic normalization — a second, independent instrument on the same mechanism](#16-symbolic-normalization--a-second-independent-instrument-on-the-same-mechanism)
  - [16.1 The design, and the two pre-registered readings](#161-the-design-and-the-two-pre-registered-readings)
  - [16.2 Saturated — and the gradient is the result](#162-saturated--and-the-gradient-is-the-result)
  - [16.3 Better static analysis pays off only where the old pass was blind](#163-better-static-analysis-pays-off-only-where-the-old-pass-was-blind)
  - [16.4 The format objection, bounded from existing cells](#164-the-format-objection-bounded-from-existing-cells)
  - [16.5 Steering: the mechanism is attention allocation, but only at full depth](#165-steering-the-mechanism-is-attention-allocation-but-only-at-full-depth)
- [17. Provenance](#17-provenance)

---

## 1. The one-paragraph answer

Fine-tuning on obfuscated code does **not** teach semantic invariance, with one specific and
replicated exception. Each per-condition adapter helps on the condition it was trained on
(+3 to +8 points over a clean-code control) and essentially nowhere else; the mean off-diagonal
transfer ratio is near zero and several cross-family cells are *negative*. Training on all five
obfuscation types at once is worse than training on clean code alone on the held-out obfuscator,
and more adapter capacity does not fix it. **The exception is `S2` (opaque predicates + dead code):
the `S2` specialist is the only arm anywhere that beats the clean-code control on the held-out
`H1`, and it does so in both languages and at both seeds** (+3.5/+3.1 pts Python, +7.3/+7.7 pts
JavaScript; confirmed at full power on 1,214 items at **+3.46** [+2.06, +4.94]). Modularity (RQ2)
does not rescue the picture: a router that classifies the obfuscation type with 100 % accuracy buys
exactly the specialists' own gains and nothing more, merges are at or below the control, and simply
*telling* the untuned model the obfuscation type is ~9 points *worse* than the clean-code adapter.

*Rewritten 27 Aug.* **The project's centre of gravity has moved from the negative result to the
exception.** Three things changed since 12 August.

**RQ2 is closed, negatively, and by elimination rather than assumption** (§12.10–§12.13; full
account in [`MASTER_REPORT_2026-08-27_router-and-merging.md`](MASTER_REPORT_2026-08-27_router-and-merging.md)).
Every combination strategy was built and measured — perfect hard dispatch, three merge algorithms
across three densities and two seed banks, an eight-expert learned mixture, monolithic training,
leave-one-transform-out, and three pre-registered repairs. None beats the clean-code control on
`H1`. The mechanism is now measured: **merging costs −3.13 pts [−4.78, −1.40] while the specialists
contribute +2.47 [+1.32, +3.70]** — two offsetting effects of nearly equal size — and the systems
are **redundant at the item level**, with an oracle over ten of them sitting **52.9 points below**
a marginal-preserving permutation null. There is no hidden complementary capability for a better
combiner to find. *This retires §12.10's stronger phrasing, "the per-condition experts carry
nothing distinct", which was read off an underpowered grid (§8.10).*

**RQ3 has now run, and it gives the `S2` exception a causal mechanism** (§15). A 3,600-dump
attention sweep shows `tuned_S2` re-anchors attention off inert identifiers and onto control and
dataflow, specifically on `S2` (**+0.111** [+0.093, +0.131], 2.6× the next system and null or
negative everywhere else). An attention-knockout intervention then shows the re-anchoring is
**load-bearing**: suppressing identifier attention costs `base` −0.089 nats of log P(gold) and
`tuned_S2` **+0.015**, a paired difference of **+0.104 [+0.011, +0.209]** — the pre-registered
prediction, confirmed.

**And a second, independent instrument agrees** (§16). A purely symbolic dead-code-elimination pass,
no training at all, is worth **+4.74** pts [+3.12, +6.24] to `base` on `S2`, **+1.56** [+0.30, +2.88]
to `tuned_L0`, and **+0.06** [−0.96, +1.08] to `tuned_S2` — a monotone dose-response in how much
inert material each system was trained on, with the specialist's interval an equivalence result
rather than a failure to reach significance. **The skill `tuned_S2` acquired *is* dead-code
elimination, implemented in attention.** Neither instrument supports that alone; together they do.

Two caveats travel with all of it. The step from "ignores inert material on `S2`" to "therefore
transfers to `H1`" remains **inferential** — no quarantined item was read in the RQ3 or
normalization work. And everything outside §7 and §9.3 is **1.5B and single-seed**, at a scale
where five of seven obfuscation penalties still cost the model something; by 7B only `L1b`, `S1`
and `H1` survive (§12.3).

*Added 12 Aug, still current.* **Overtraining does not explain the merge failure** — sign conflict
*falls* over our 3-epoch bank and only rises past epoch 3, so our experts are under-trained relative
to where interference appears (§5.3). **The bidirectional thread's unlearning probe does not show
shared representation** — its control collapses just as hard as the treatment, which is what the
control was built to detect (§7.7). And **a scoring bug failed six runs in a way that looked like an
adapter failure** (§8.7); it corrupted two reported fields but no accuracy metric.

---

## 1.5 Where this sits in the literature — and what routing does *not* show

*Added 13 August 2026. Companion to [`papers/RELATED_WORK.md`](../papers/RELATED_WORK.md) §3.5.*

### 1.5.1 The gap this work occupies

The prior literature on obfuscated-code comprehension is a **measurement** literature.
`promon2026atr` builds the field's best "how bad is it" table; `li2025obfvuln` finds obfuscation
sometimes *helps* a downstream task; the adversarial and steering work perturbs inputs and records
the damage. All of it establishes that models degrade. **None of it attempts a repair and then
tests whether the repair survives a transformation the model never saw.**

That is a narrower claim than "the area is unexplored" — which is not true, and the first reviewer
who knows `promon2026atr` will say so. The defensible version has three parts, and this project
supports all three:

| what is missing from the field | what obtune has |
|---|---|
| a controlled transformation ladder to train on | six single-transform conditions, identical semantics in Python and JavaScript, plus a quarantined seventh no training run may touch |
| a **held-out-transform** result | `H1`, never trained on under any circumstance, four independent enforcement layers |
| a head-to-head of repair strategies on one ladder | prompting vs per-condition adapters vs learned router vs monolithic vs four merge algorithms, all on the same programs |

### 1.5.2 Our advantages, stated as a reviewer would test them

| advantage | evidence | how it would be attacked |
|---|---|---|
| **The control is right.** Deltas are against an adapter trained on *clean* code, not against `base` | `base` .064 → `tuned_L0` .247 on `H1`: the control captures most of the achievable gain | hard to attack; this is the methodological contribution most likely to be adopted |
| **The held-out family is genuinely held out** | four enforcement layers, an access log, a content scan in `make check` | "did it leak?" — answerable with the log |
| **Merging generalises where specialists do not** | `merge_dare_ties` .348 on `H1` vs `tuned_L0` .245 and `mono_all` .229 | n=40, one seed, one model — see §1.5.4 |
| **Negative results are powered enough to state** | seed noise measured at 1.32 mean / 3.61 p95 over 84 matched pairs | "underpowered" — pre-empted by reporting the noise floor rather than hiding it |

### 1.5.3 Routing is **not** a failure — it is a ceiling, and its real test has not been run

Earlier drafts of this report called the router a failure. That is wrong and is corrected here.

**The router works.** Validation accuracy 0.9969, overall route accuracy **1.000**, a perfectly
diagonal confusion matrix, routing entropy ~1e-6 nats against a maximum of 2.079. As a classifier
of "which transformation is this", it is solved.

What it *cannot* do is exceed the thing it routes to. It recovers the specialists exactly, and the
specialists are only ~3.5 points above the clean-code control (§3) — so a perfect router inherits a
3.5-point ceiling. **The limiting factor is the value of specialisation, not the quality of
routing.** Those are different claims and only the first is supported.

**And the case that matters most has never been run.** `routing_report.json` records
`n_heldout: 0`: the router has never been asked to route a **held-out** transformation. Its entire
evaluation is in-distribution, where a 100 % accurate classifier is unsurprising. Three specific
tests are missing, and none of them is expensive:

| missing test | what it would settle | cost |
|---|---|---|
| route `H1` and report the entropy | does the router *know* it is out of distribution, or does it confidently pick a wrong expert? | one eval pass; `routing_entropy_on: [H1]` is already configured |
| `oracle_bestof8` — per-item best of the eight experts | the true per-item headroom any hard router could ever reach | **zero GPU** — computable from cells already on disk |
| route the composites | a stacked variant contains two mechanisms, so a hard router *must* be wrong; this is where routing should visibly break | one eval pass; composite cells exist |

Until those run, the honest statement is: **routing is solved in-distribution and untested out of
it.** The interesting question — what a router does when no expert is right — is exactly what
Part III's mixture arm was built to probe, and the hard router has not been measured on the same
ground.

### 1.5.4 What would have to be true for the merging claim to survive review

The strongest positive result here is that merging generalises to an unseen obfuscator better than
any specialist or the monolith. Before it is written up, one competing explanation has to be
eliminated:

> Merged weights sit closer to the clean-code model. Since `tuned_L0` alone already captures most
> of the `H1` gain, a merge that dilutes six obfuscation-specific updates may simply be
> **regressing toward the control** rather than composing skills.

The control that separates these is a **merge of N random-seed `L0` adapters**. If that also lands
near .35 on `H1`, the claim is about dilution, not composition, and should not be made. The merge
machinery and the `L0` adapters both exist, so this is hours, not days. Together with the 12
missing Grid B control cells (§8.2) and a second seed for the merge arms, it is the shortest path
from "suggestive" to "publishable".

---

### 1.6 Prior work, with the numbers they actually report

*Added 13 August 2026.* Every paper below measures comprehension of transformed code. The point of
the table is what they **report**, so our numbers can be read against something rather than in
isolation. Full annotations in [`papers/RELATED_WORK.md`](../papers/RELATED_WORK.md).

**Read the last two columns first.** Almost none of this work trains on obfuscated code, and none
of it evaluates on a transformation held out from training — which is the gap §1.5.1 describes.

| paper | input | task | headline result they report | trains on obfuscated code? | held-out transform? |
|---|---|---|---|---|---|
| `promon2026atr` | ARM/x86 assembly + pseudocode | malware behaviour comprehension | clean **~79 %** (ARM pseudocode) → three-pass obfuscation **26.1 %**; ARM assembly **63.7 % → 8.5 %**; no model exceeded **86 %** on clean code | no — prompting only | no |
| `nikiema2025contrastive` | Python source | deobfuscation (reverse) | standard SFT **0 %** reverse; contrastive fine-tuning **39–52 %** (GPT-4.1-Mini 52.03, GPT-3.5 50.51, Qwen2.5-Coder 39) — **variable renaming only** | yes (contrastive triplets) | no |
| `guzman2026poisoned` | Python source | algorithmic reasoning | misleading identifiers move accuracy **100 % → 0–20 %** (physics) and **0 %** (pathfinding); a prompt change alone restores it | no — prompting only | no |
| `hu2026bindeobf` | binaries | binary deobfuscation | in-context examples help instruct models (**72.92 %** semantic preservation at 5-shot) but *degrade* reasoning models (**70.29 %**); best overall **~60 %** | no — ICL only | no |
| `li2025obfvuln` | source | vulnerability detection | obfuscation sometimes **improves** detection | no | no |
| `ding2024semcoder` | clean Python | output prediction (our task) | beats GPT-3.5-turbo on CRUXEval-O at 6.7B by verbalising execution | no — clean code only | n/a |
| **obtune (this work)** | **Python + JavaScript source** | **output prediction on still-obfuscated code** | **see §2.2** | **yes — six-condition ladder** | **yes — `H1`, four enforcement layers** |

**Three things this table makes visible.**

1. **The degradation numbers are enormous and ours are not comparable to them.** `promon2026atr`
   reports 79 % → 26 % because it asks for *behaviour summaries of malware assembly* judged by a
   rubric. We ask for an exact output value on source code, graded by execution-verified strict
   match, where the untuned 1.5B baseline is **.217 on clean code** (§2.2). Different task,
   different metric, different model scale — the shape (structural transforms hurt most) matches,
   the magnitudes must not be pooled.
2. **`nikiema2025contrastive` is the only one we can compare against directly**, because we
   reproduced their setup at their model size — and their headline does not replicate (§7).
3. **The last two columns are the contribution.** One paper trains on obfuscated code; none holds
   a transform out. That is why the `tuned_L0` control and the `H1` quarantine are the
   methodological core rather than housekeeping.

---

## 2. What exists — the inventory

The two evaluation grids, side by side. They are **disjoint in programs** and are never pooled: a
number from one is never compared with a number from the other, because they would be averaging
different populations. "Conditions" lists which obfuscation types were evaluated on that grid.

| | Grid A — "corpus" | Grid B — "testset" |
|---|---|---|
| programs | 557 Python / 168 JavaScript, held-out split | 40 Python / 30 JavaScript, ICSE test set |
| snippet ids | `apps_*`, `cruxeval_sample_*` | `A:…`, `B:…` |
| conditions | L0, L1b, L1r, L2, S1, S2, **H1** | L0…S2 (+S3/S4, +H1 for merges only) |
| systems | `base`, `tuned_<c>_s17`, `tuned_<c>_s42`, `mono_all`, `mono_r64/r128/r192`, `ctl_r64`, `oracle_prompt_1shot` | `router`, `merge_ties`, `merge_dare_ties`, `merge_dare_linear`, `tuned_<c>`, `tuned_S3`, `tuned_S4` |
| answers | RQ1, monolithic-vs-specialist, rank sweep | RQ2 (routing, merging), the S2 decomposition |

**The two grids are disjoint in programs and must never be pooled.** They were built by different
manifests and evaluate different populations; averaging them silently mixes an easy 40-program
test set with a 557-program held-out split.

Common-subset sizes used for headline numbers (programs surviving *every* condition, so no cell is
confounded by a different program set): **Python 317**, **JavaScript 91**.

Threads: RQ1 complete (both languages, both seeds). RQ2 complete but weakly powered and missing a
control in Python (§8.2). RQ3 attention — only the span→token validator has run (100 % span
resolution over 413 programs, `results/attn/span_validation.json`); no attention results exist.
Human-alignment — not started. CFT side thread — complete at 1.5B and 7B (§7).

---

### 2.1 How to read every table in this report

Conventions are constant throughout. If you jump straight to a table, this decodes it.

| notation | meaning |
|---|---|
| `.440` | An **accuracy**: fraction of trials graded correct, 0–1. Higher is better. |
| `+3.9` / `−2.6` | A **difference in accuracy points** (percentage points), not a ratio. `+3.9` means the system scored 3.9 points above its reference on the same items. |
| `s17 \| s42` | The same quantity at **seed 17** and **seed 42**. Two independent training runs; the spread between them is the noise floor (§3.7). |
| `*` | Passed **BH-FDR q<0.05 AND** the cluster-bootstrap CI excludes zero. Both conditions, not either. Unmarked cells are not claimed as effects. |
| **bold** in a transfer matrix | The **diagonal** — the specialist evaluated on the condition it was trained on. |
| `—` or blank | Not run, or the statistic is undefined (e.g. a transfer ratio whose denominator is under 3 points). Never "zero". |
| `~~struck~~` in §8 | A data-quality issue that has since been resolved; the original text is kept so the correction is auditable. |

**The reference matters more than the number.** Almost every delta in this report is against the
**`L0`-only control** — an adapter trained on *clean* code — not against the untuned base model.
Training on clean code already recovers most of the achievable gain on obfuscated inputs, so a
system that merely beats `base` has shown nothing. Where a table is against `base` instead, it
says so.

**Two program sets, never pooled.** Grid A (317 Python / 91 JS programs) and Grid B (33 / 30) are
disjoint. A number from one is never compared with a number from the other; §2 gives the split.

**What the tables contain, in order:**

| # | § | shows |
|---|---|---|
| 1 | 2 | inventory: what exists in each of the two grids |
| 2–3 | 3 | RQ1 Python — absolute accuracy, then deltas vs the control at both seeds |
| 4 | 3.5 | the `S2`→`H1` exception, the one replicated positive result |
| 5–6 | 3.6 | RQ1 JavaScript, same two views |
| 7–9 | 3.7 | seed stability: per-adapter s42−s17, and the summary that defines the noise floor |
| 10 | 4 | monolithic training and rank sweep — breadth and capacity both fail |
| 11 | 5.1 | what each merge algorithm actually does to the six adapters |
| 12–13 | 5.2 | RQ2 results: router, merges, oracle routing |
| 14 | 5.3 | task-vector geometry across epochs — the overtraining mechanism |
| 15–16 | 7.1 | the seven CFT arms and their measured cost on four axes |
| 17 | 7.2 | the four reverse-direction measures and why `exec` alone is broken |
| 18–20 | 7.3–7.4 | CFT at 1.5B, then broken out per transformation |
| 21–22 | 7.5 | CFT at 7B, including the prompting-strategy sweep |
| 23 | 7.7 | approximate unlearning — treatment and **control** |
| 24 | 8.3 | catastrophic forgetting (HumanEval+) once the harness was fixed |
| 25 | 8.7 | which fields the scoring bug corrupted, and which it did not |
| 26–28 | 13 | glossary: conditions, systems, measurements |

---

### 2.2 Every system, every obfuscation level, one table

*Added 13 August 2026 · regenerated in full 27 August 2026.* Accuracy, higher is better. `—` means
not run for that pair, never zero. **This is the one table in the project that contains every
system.** If you want one place to see what exists, it is here; everything else in this document
is a slice of it with statistics attached.

**Model: `qwen25c-1.5b` (Qwen2.5-Coder-1.5B-Instruct), Python, every row.** No 7B row appears
here and none may be added: 7B roughly doubles accuracy on every condition (§9.3), so a single
7B row would dominate the table and invite differences that are model effects wearing a
system's name. 7B results live in their own sections.

**READ THE `grid` COLUMN BEFORE DIFFERENCING ANY TWO ROWS.** Grid A is 317–557 corpus programs;
Grid B is 33–40 ICSE test-set programs. They are disjoint (§2), so an A row and a B row are
measured on different populations and their difference is not interpretable. Within a grid,
comparisons are valid. The `C_*` columns are the stacked composite conditions (§5.4). *They no
longer exist only on Grid B* — 114 Grid A composite cells were filled on 15 August after the
"composites are testset-only" belief turned out to be a build defect, not a structural limit (see
the note below the table).

**The `settings` column** (*added 14 August 2026*) says what each row actually is, so a row can
be read without reverse-engineering its name. Notation:

| token | meaning |
|---|---|
| `r32`, `r64`, `r128`, `r192` | LoRA rank — the size of the adapter's low-rank bottleneck. |
| `s17`, `s42`, `s101` | Training seed. Two seeds of one system bound the noise floor (§3.7). |
| `L0`, `S2`, `all 6` | The condition(s) the adapter was **trained** on. `all 6` = the full trainable ladder. |
| `N experts` | How many adapters went into the merge or mixture. |
| `TIES`, `DARE-TIES`, `DARE-linear` | Merge algorithm. `d0.5` is the density (the fraction of task-vector entries kept). |
| `@ eN` | The expert checkpoint used, in epochs. `e1` is early-stopped, `e9` heavily over-trained (§5.3). |
| `k=N demos` | In-context examples in the prompt. `0 train` marks an arm that trained nothing at all. |
| `gate frozen …` / `trained gate` | RouterLoRA variants — the control gates vs the learned one (§5.4). `+ load balancing` is the Switch-style auxiliary loss and temperature floor that made the gate actually route (§12.10). |
| `holding out X` | A leave-one-transform-out fold: trained on five of the six trainable conditions, so its own `X` column is an honest unseen-transform measurement (§12.10). |
| `3× clean-code adapters` | The merge control — N adapters with no obfuscation knowledge between them, merged by the same algorithm (§12.10). |
| `each a different seed` | The cross-seed merge control: same six conditions, seed assignment altered, so the bank's task-vector geometry changes and adapter quality does not (§12.12). |
| `residual-preserving` | A merge that keeps the condition-specific residuals at full magnitude instead of diluting them — the third attempted repair (§12.12). |
| `+ symbolic DCE` / `+ norm_inert` | An adapter with a zero-training symbolic dead-code-elimination pass applied to the program *before* the model sees it (§16). |
| `labels shuffled` | The format-acquisition control. **Void as designed** — it collapsed to one degenerate string under greedy decoding (§8.11). |

**Every column, decoded** (*added 15 August 2026*). Each cell is the accuracy of the row's system
on the column's condition, so the columns are *evaluation* conditions — what the code being read
looked like — and never what the system was trained on (that is the `settings` column). Full
definitions live in §13; this is the self-contained version.

| column | what it is |
|---|---|
| `system` | The system that produced the row: the untuned model, one fine-tuned adapter, a merge of several adapters, or a mixture with a gate. Names are decoded by the `settings` column beside them. |
| `grid` | Which of the two disjoint program sets the row was measured on. **A** = 317–557 corpus programs, **B** = 33–40 ICSE test-set programs; an A number and a B number are measured on different populations and must never be differenced (§2). |
| `settings` | What the row actually is — rank, seed, training condition, merge algorithm, expert count, demo count — in the notation of the table just above. |
| **`‖ΔW‖`** | *(added 27 August 2026)* The **task-vector norm** — the mean Frobenius norm per adapted module of ΔW = (α/r)·B·A, i.e. how far this adapter moved the model from base. Computed on CPU from safetensors already on disk (§14.1); **136 of 169 rows**, blank where a row has no single adapter (`base`, the ICL and normalization arms) or is a resident bank rather than one merged tensor (`mole_*`, rank 256). Read it against a single specialist's **0.30–0.38**: a merge far below that band has discarded most of its ingredients, and §14.4 shows that is what actually tracks merged accuracy. |
| `L0` | **Clean code, no obfuscation** (comments and docstrings stripped, as in every condition). The reference difficulty: whatever a system scores here is what it can do when nothing is hidden. |
| `L1b` | **Adversarial renaming.** Identifiers are replaced with actively misleading names — a Fibonacci function called `smoothArea` — so the names point at the wrong meaning rather than at none. Consistently the hardest of the identifier conditions. |
| `L1r` | **Random renaming.** Identifiers become meaningless hex (`v_a3f2`), which removes the naming signal without lying about it. The contrast with `L1b` separates "no information" from "false information". |
| `L2` | **Minification.** Identifiers become `a`, `b`, `c`… and type annotations are stripped — the transform a JS bundler applies in production. Like `L1r` but shorter and with the types gone too. |
| `S1` | **Control-flow flattening.** The function body is rewritten into a dispatch loop over a state variable, so the original `if`/`for` shape is gone even though every name is untouched. The first column where structure, not naming, is what was destroyed. |
| `S2` | **Opaque predicates + dead code.** Guards that provably always take the same branch, plus helper functions that are never called. The code grows and gains branches, but none of the additions change behaviour. |
| `S3` | **Dead code only** — the half of `S2` that just has to be *ignored*: 1–2 never-called helpers, no opaque predicates. |
| `S4` | **Opaque predicates only** — the half of `S2` that has to be *reasoned about*: 1–3 always-taken guards whose condition genuinely executes, no dead helpers. `S3` and `S4` exist so a drop on `S2` can be attributed to one of the two mechanisms rather than their fusion. |
| **`H1`** | **The held-out obfuscator** — string encoding + mixed boolean-arithmetic rewriting, the only condition nothing is ever trained on (quarantined behind four enforcement layers, §3.2). It is the discriminator: score here means the model learned the *class* of meaning-preserving rewrites; failure here with high scores elsewhere means it memorised the specific transforms it saw. **Read it off the row's `grid`:** on Grid A it is n = 1,214 items over 405 programs and is what every `H1` claim in this document rests on; on Grid B it is n = 115 over 27 programs, **too small for merge comparisons**, reads ~10 points higher for every arm, and *reorders* them (§8.10). Fifteen systems have both, on separate rows. |
| `C_L1r_S1` | **Composite: random renaming, then flattening.** The headline stacked condition — one identifier transform and one structural transform in the same program, so no single specialist is the right expert for it. Composites exist only on Grid B and are deliberately outside the trainable ladder, so they cannot shift RQ1. |
| `C_S1_L1r` | **The same two transforms in the opposite order** — flatten first, then rename. Composition does not commute: `S1` emits `_st_`-prefixed state variables, and renaming them *second* destroys the surface cue a hard router keys on. A routing drop here but not on `C_L1r_S1` means the router was reading variable names, not structure. |
| `C_L1b_S1` | **Adversarial renaming, then flattening.** `L1b` is the one condition where a specialist beats the `L0` control (§3.5); this column asks whether that advantage survives having a structural transform stacked on top of it. |
| `C_L2_S4` | **Minification, then opaque predicates** — an identifier transform stacked with the *reason-about-it* half of `S2`. |
| `C_L1r_S3` | **Random renaming, then dead code** — the same shape as the column before it, but with the *ignore-it* half of `S2`. The pair decomposes which half of `S2` stacking actually costs. |
| `C_S4_S3` | **The positive control**: opaque predicates then dead helpers, which is `S2` reconstructed by composition. It should score near `S2` on adapters we already have numbers for; if it does not, the composite build machinery is wrong and no other `C_*` column can be trusted. |

Three rows to read carefully. **`tuned_L0` (A) and `tuned_L0_k0` (B) are the same adapter** — same
sha256, same prompt, zero demos — on the two different grids, which is why they differ by ~6
points with nothing about the system changed. **`merge_dare_linear` is the broken arm**; its
repaired form is `dl_rescaled` (§5.2). And **`formatonly` is void**, not zero: it is the
label-shuffled control, and it collapsed to a single degenerate output string (§8.11) — its 0.000
cells are an artifact of greedy decoding, not a measurement.

*Regenerated 27 August 2026 from every per-cell parquet — **154 systems in 169 rows, all 15
evaluation conditions**, up from 73 systems in 74 rows at the 08-12 revision. Every row of that
revision is still here; new since then are the LOTO folds, the merge controls (`l0merge_*`,
`crossseed_*`), the density sweep, the residual merges, the three attempted repairs, the balanced
RouterLoRA gate, the symbolic-normalization arms, and every Grid A `H1` read.*

**One row per system PER GRID.** Fifteen systems were measured on both grids and now get two rows
each, the way `base` always has. This is the change that matters: **every cell in a row belongs to
the grid its `grid` column names**, including `H1`, so the column is authoritative rather than
approximate. Before this, a system evaluated on Grid B throughout but given a Grid A `H1` read —
which is true of `merge_ties`, `merge_dare_ties`, both `l0merge_*` and both `residual_n6_*` — had
its two grids sharing one row. That is how the RQ2 conclusion came to rest on 115 items (§8.10).
A sparse `A` row carrying only an `H1` value is therefore informative, not a gap: it says the
system was read at power on the discriminator and nowhere else.

**Where two cells exist for the same system, grid and condition, the table applies a documented
source preference** rather than whichever the glob returned first — *prefer vLLM over the `hf-mole`
mixture engine, except for `mole_*` rows, which must be read through it; then larger n; then newer.*
This matters: **41 cells have duplicates that disagree, 27 of them by more than 0.5 points**, and
5 are settled by the engine rule alone. The `base` composite cells are the worst case — `main`
(hf-mole) reads `C_L2_S4` at .216 against `baselines` (vLLM) at .176, a 4-point engine offset that
would be folded into every delta computed against that reference. The remaining disagreements are
the re-evaluation spread of §8.9 and are resolved to the newest read.

**Verified against the 08-12 revision.** All **74** of its rows are present and **every one of its
values reproduces exactly — 0 differences, 0 blanks where it previously had a number.** The 95 added
rows are new systems and the second grid of systems that had only one row before. *(Getting there
took three attempts: a first pass collapsed `base`'s two grid rows into one and re-imported the
4-point `hf-mole` engine offset the 08-12 revision had already found and fixed; a second
double-rounded 0.4085 → 0.408. Both are the reason this note exists — a regenerated table that
silently disagrees with the one it replaces is worse than no regeneration.)*


| system | grid | settings | **‖ΔW‖** | L0 | L1b | L1r | L2 | S1 | S2 | S3 | S4 | **H1** | C_L1r_S1 | C_S1_L1r | C_L1b_S1 | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Reference** | | | | | | | | | | | | | | | | | | |
| `base` | A | no adapter, no demos | — | 0.218 | 0.189 | 0.187 | 0.196 | 0.205 | 0.151 | 0.160 | 0.193 | 0.063 | 0.176 | 0.160 | 0.156 | 0.152 | 0.120 | 0.151 |
| `base` | B | no adapter, no demos | — | 0.290 | 0.233 | 0.233 | 0.210 | 0.262 | 0.188 | 0.182 | 0.222 | 0.113 | 0.267 | 0.247 | 0.320 | 0.176 | 0.159 | 0.182 |
| `tuned_L0` | A | r32 · s17 · L0 | 0.363 | 0.450 | 0.342 | 0.365 | 0.374 | 0.391 | 0.414 | 0.431 | 0.432 | 0.247 | 0.271 | 0.246 | 0.248 | 0.344 | 0.345 | 0.423 |
| `tuned_L0` | B | r32 · s17 · L0 | 0.363 | 0.494 | 0.369 | 0.460 | 0.500 | 0.434 | 0.489 | 0.483 | 0.455 | 0.400 | — | — | — | — | — | — |
| `tuned_L0_s17` | A | r32 · s17 · L0 | 0.363 | 0.447 | 0.344 | 0.367 | 0.375 | 0.390 | 0.415 | 0.431 | 0.431 | 0.247 | 0.271 | 0.245 | 0.247 | 0.343 | 0.346 | 0.424 |
| `tuned_L0_s42` | A | r32 · s42 · L0 | 0.365 | 0.447 | 0.337 | 0.373 | 0.369 | 0.387 | 0.421 | 0.446 | 0.429 | 0.247 | 0.281 | 0.256 | 0.255 | 0.349 | 0.340 | 0.428 |
| `ctl_r64` | A | r64 · s17 · L0 | 0.292 | 0.449 | 0.336 | 0.371 | 0.380 | 0.384 | 0.409 | 0.435 | 0.430 | 0.231 | 0.280 | 0.242 | 0.257 | 0.344 | 0.335 | 0.413 |
| **RQ1 specialists — Grid A, seeds 17 / 42** | | | | | | | | | | | | | | | | | | |
| `tuned_L1b_s17` | A | r32 · s17 · L1b | 0.369 | 0.438 | 0.384 | 0.381 | 0.385 | 0.357 | 0.409 | 0.435 | 0.433 | 0.250 | 0.275 | 0.250 | 0.285 | 0.362 | 0.353 | 0.418 |
| `tuned_L1b_s42` | A | r32 · s42 · L1b | 0.371 | 0.436 | 0.394 | 0.386 | 0.386 | 0.347 | 0.409 | 0.432 | 0.426 | 0.227 | 0.281 | 0.259 | 0.284 | 0.367 | 0.366 | 0.415 |
| `tuned_L1r_s17` | A | r32 · s17 · L1r | 0.301 | 0.453 | 0.355 | 0.396 | 0.394 | 0.383 | 0.427 | 0.440 | 0.445 | 0.247 | 0.294 | 0.263 | 0.267 | 0.362 | 0.376 | 0.425 |
| `tuned_L1r_s42` | A | r32 · s42 · L1r | 0.368 | 0.445 | 0.361 | 0.389 | 0.388 | 0.379 | 0.430 | 0.440 | 0.438 | 0.245 | 0.300 | 0.267 | 0.266 | 0.370 | 0.378 | 0.430 |
| `tuned_L2_s17` | A | r32 · s17 · L2 | 0.378 | 0.440 | 0.349 | 0.380 | 0.377 | 0.376 | 0.421 | 0.432 | 0.428 | 0.245 | 0.283 | 0.257 | 0.250 | 0.355 | 0.361 | 0.424 |
| `tuned_L2_s42` | A | r32 · s42 · L2 | 0.369 | 0.447 | 0.353 | 0.379 | 0.386 | 0.375 | 0.417 | 0.436 | 0.436 | 0.242 | 0.288 | 0.257 | 0.260 | 0.369 | 0.359 | 0.422 |
| `tuned_S1_s17` | A | r32 · s17 · S1 | 0.331 | 0.435 | 0.319 | 0.368 | 0.374 | 0.424 | 0.425 | 0.425 | 0.428 | 0.254 | 0.310 | 0.299 | 0.295 | 0.352 | 0.334 | 0.413 |
| `tuned_S1_s42` | A | r32 · s42 · S1 | 0.320 | 0.445 | 0.326 | 0.363 | 0.378 | 0.430 | 0.427 | 0.425 | 0.435 | 0.252 | 0.307 | 0.313 | 0.277 | 0.359 | 0.343 | 0.431 |
| `tuned_S2_s17` | A | r32 · s17 · S2 | 0.380 | 0.456 | 0.333 | 0.374 | 0.378 | 0.434 | 0.453 | 0.454 | 0.454 | 0.280 | 0.308 | 0.275 | 0.278 | 0.376 | 0.362 | 0.458 |
| `tuned_S2_s42` | A | r32 · s42 · S2 | 0.380 | 0.446 | 0.338 | 0.372 | 0.381 | 0.424 | 0.447 | 0.450 | 0.452 | 0.275 | 0.303 | 0.270 | 0.275 | 0.381 | 0.370 | 0.451 |
| **RQ1 specialists — Grid B** | | | | | | | | | | | | | | | | | | |
| `tuned_L1b` | B | r32 · s17 · L1b | 0.369 | 0.477 | 0.460 | 0.511 | 0.483 | 0.434 | 0.443 | 0.483 | 0.466 | 0.383 | 0.400 | 0.427 | 0.433 | 0.483 | 0.449 | 0.466 |
| `tuned_L1r` | B | r32 · s17 · L1r | 0.301 | 0.477 | 0.386 | 0.460 | 0.477 | 0.421 | 0.443 | 0.443 | 0.466 | — | 0.347 | 0.360 | 0.360 | 0.443 | 0.420 | 0.426 |
| `tuned_L2` | B | r32 · s17 · L2 | 0.378 | 0.466 | 0.477 | 0.489 | 0.511 | 0.434 | 0.443 | 0.455 | 0.466 | — | 0.407 | 0.407 | 0.360 | 0.466 | 0.455 | 0.472 |
| `tuned_S1` | B | r32 · s17 · S1 | 0.331 | 0.415 | 0.330 | 0.438 | 0.455 | 0.441 | 0.369 | 0.415 | 0.409 | — | 0.340 | 0.413 | 0.327 | 0.415 | 0.347 | 0.426 |
| `tuned_S2` | B | r32 · s17 · S2 | 0.380 | 0.477 | 0.415 | 0.483 | 0.506 | 0.469 | 0.472 | 0.483 | 0.506 | — | 0.360 | 0.393 | 0.333 | 0.489 | 0.449 | 0.489 |
| `tuned_S3` | B | r32 · s17 · S3 | 0.308 | 0.466 | 0.381 | 0.477 | 0.449 | 0.448 | 0.466 | 0.455 | 0.460 | — | 0.347 | 0.393 | 0.320 | 0.455 | 0.409 | 0.460 |
| `tuned_S4` | B | r32 · s17 · S4 | 0.376 | 0.483 | 0.426 | 0.500 | 0.466 | 0.455 | 0.472 | 0.460 | 0.500 | — | 0.407 | 0.367 | 0.333 | 0.489 | 0.449 | 0.483 |
| **Shot count — ICL, and ICL applied to an adapter (§11)** | | | | | | | | | | | | | | | | | | |
| `icl_k1` | B | 0 train · k=1 demos | — | 0.341 | 0.244 | 0.284 | 0.290 | 0.297 | 0.250 | 0.301 | 0.273 | 0.226 | 0.247 | 0.260 | 0.247 | 0.239 | 0.239 | 0.239 |
| `icl_k2` | B | 0 train · k=2 demos | — | 0.364 | 0.267 | 0.301 | 0.352 | 0.283 | 0.290 | 0.324 | 0.318 | 0.287 | 0.293 | 0.280 | 0.260 | 0.290 | 0.290 | 0.290 |
| `icl_k4` | B | 0 train · k=4 demos | — | 0.375 | 0.273 | 0.301 | 0.330 | 0.310 | 0.301 | 0.347 | 0.330 | 0.287 | 0.273 | 0.300 | 0.280 | 0.312 | 0.312 | 0.312 |
| `tuned_L0_k0` | B | r32 · s17 · L0 · k=0 demos | 0.363 | 0.500 | 0.398 | 0.494 | 0.460 | 0.448 | 0.455 | 0.477 | 0.449 | 0.339 | 0.400 | 0.400 | 0.360 | 0.432 | 0.438 | 0.460 |
| `tuned_L0_k1` | B | r32 · s17 · L0 · k=1 demos | 0.363 | 0.472 | 0.392 | 0.426 | 0.477 | 0.400 | 0.438 | 0.443 | 0.432 | 0.339 | 0.360 | 0.413 | 0.273 | 0.415 | 0.386 | 0.460 |
| `tuned_L0_k2` | B | r32 · s17 · L0 · k=2 demos | 0.363 | 0.489 | 0.375 | 0.438 | 0.460 | 0.407 | 0.409 | 0.466 | 0.449 | 0.287 | 0.347 | 0.360 | 0.313 | 0.381 | 0.392 | 0.438 |
| `tuned_L0_k4` | B | r32 · s17 · L0 · k=4 demos | 0.363 | 0.455 | 0.358 | 0.415 | 0.460 | 0.414 | 0.432 | 0.466 | 0.455 | 0.339 | 0.293 | 0.313 | 0.267 | 0.392 | 0.386 | 0.438 |
| **Zero-training baselines — prompting and symbolic normalization (§12.2, §16)** | | | | | | | | | | | | | | | | | | |
| `oracle_prompt` | B | 0 train · told the transform · 0 demos | — | 0.273 | 0.250 | 0.205 | 0.170 | 0.234 | 0.239 | — | — | 0.087 | — | — | — | — | — | — |
| `oracle_prompt_1shot` | A | 0 train · told the transform · 1 clean demo | — | 0.277 | 0.201 | 0.213 | 0.233 | 0.216 | 0.248 | — | — | 0.157 | — | — | — | — | — | — |
| `oracle_prompt_1shot` | B | 0 train · told the transform · 1 clean demo | — | 0.398 | 0.261 | 0.256 | 0.290 | 0.255 | 0.284 | — | — | 0.209 | — | — | — | — | — | — |
| `icl_k1_clean` | A | 0 train · k=1 demos · clean | — | 0.272 | 0.223 | 0.232 | 0.243 | 0.233 | 0.227 | — | — | 0.152 | — | — | — | — | — | — |
| `icl_k1_clean` | B | 0 train · k=1 demos · clean | — | 0.341 | 0.244 | 0.256 | 0.312 | 0.241 | 0.273 | 0.290 | 0.284 | 0.235 | 0.247 | 0.267 | 0.227 | 0.278 | 0.256 | 0.273 |
| `icl_k1_cross` | A | 0 train · k=1 demos · cross | — | 0.284 | 0.226 | 0.228 | 0.247 | 0.251 | 0.239 | — | — | 0.145 | — | — | — | — | — | — |
| `icl_k1_cross` | B | 0 train · k=1 demos · cross | — | 0.352 | 0.233 | 0.284 | 0.341 | 0.297 | 0.284 | 0.284 | 0.295 | 0.217 | 0.240 | 0.240 | 0.253 | 0.278 | 0.233 | 0.267 |
| `icl_k4_cross` | A | 0 train · k=4 demos · cross | — | 0.331 | 0.264 | 0.273 | 0.272 | 0.277 | 0.285 | — | — | 0.182 | — | — | — | — | — | — |
| `icl_k1_matched_struct` | B | 0 train · k=1 demos · matched struct | — | 0.312 | 0.239 | 0.261 | 0.273 | 0.262 | 0.250 | 0.278 | 0.261 | 0.252 | 0.267 | 0.247 | 0.253 | 0.250 | 0.227 | 0.239 |
| `norm_alpha` | B | 0 train · symbolic `alpha` pass | — | 0.222 | 0.233 | 0.250 | 0.210 | 0.193 | 0.165 | 0.148 | 0.193 | 0.052 | 0.253 | 0.227 | 0.267 | 0.159 | 0.148 | 0.102 |
| `norm_reformat` | B | 0 train · symbolic `reformat` pass | — | 0.284 | 0.227 | 0.216 | 0.210 | 0.269 | 0.193 | 0.193 | 0.222 | 0.113 | 0.253 | 0.240 | 0.313 | 0.188 | 0.153 | 0.176 |
| `norm_full` | A | 0 train · symbolic `full` pass | — | 0.212 | 0.189 | 0.195 | 0.198 | 0.178 | 0.180 | — | — | 0.099 | — | — | — | — | — | — |
| `norm_full` | B | 0 train · symbolic `full` pass | — | 0.227 | 0.244 | 0.244 | 0.210 | 0.186 | 0.222 | 0.227 | 0.188 | 0.139 | 0.247 | 0.227 | 0.253 | 0.148 | 0.244 | 0.182 |
| `norm_structural` | A | 0 train · symbolic `structural` pass | — | 0.220 | 0.188 | 0.189 | 0.197 | 0.200 | 0.199 | — | — | 0.129 | — | — | — | — | — | — |
| `norm_structural` | B | 0 train · symbolic `structural` pass | — | — | — | — | — | — | — | — | — | — | 0.260 | 0.240 | 0.313 | 0.182 | 0.227 | 0.216 |
| `norm_structural_fixed` | A | 0 train · symbolic `structural_fixed` pass | — | 0.218 | — | 0.190 | — | 0.201 | 0.199 | 0.220 | 0.190 | — | — | — | — | — | — | — |
| `norm_inert` | A | 0 train · symbolic `inert` pass | — | 0.219 | — | 0.189 | — | 0.202 | 0.206 | 0.219 | 0.205 | — | — | — | — | — | — | — |
| `tuned_L0_norm` | A | r32 · s17 · L0 **+ symbolic DCE** | 0.363 | 0.449 | — | 0.365 | — | — | 0.430 | — | — | — | — | — | — | — | — | — |
| `tuned_S2_norm` | A | r32 · s17 · S2 **+ symbolic DCE** | 0.380 | 0.457 | — | 0.378 | — | — | 0.454 | — | — | — | — | — | — | — | — | — |
| `tuned_L0_inert` | A | r32 · s17 · L0 **+ `norm_inert`** | 0.363 | 0.450 | — | 0.369 | — | 0.387 | 0.435 | 0.447 | 0.438 | — | — | — | — | — | — | — |
| `formatonly` | A | r32 · s17 · L0 · **labels shuffled** — void, §8.11 | 0.328 | 0.000 | — | 0.000 | — | — | 0.000 | — | — | — | — | — | — | — | — | — |
| **Monolithic / capacity (§4)** | | | | | | | | | | | | | | | | | | |
| `mono_all` | A | r32 · s17 · all 6 | 0.744 | 0.416 | 0.381 | 0.367 | 0.379 | 0.392 | 0.415 | 0.416 | 0.415 | 0.229 | 0.334 | 0.326 | 0.322 | 0.373 | 0.368 | 0.413 |
| `mono_r64` | A | r64 · s17 · all 6 | 0.684 | 0.422 | 0.387 | 0.378 | 0.390 | 0.399 | 0.428 | 0.435 | 0.420 | 0.239 | 0.335 | 0.336 | 0.336 | 0.387 | 0.376 | 0.424 |
| `mono_r128` | A | r128 · s17 · all 6 | 0.889 | 0.430 | 0.387 | 0.383 | 0.387 | 0.397 | 0.419 | 0.427 | 0.422 | 0.214 | 0.342 | 0.340 | 0.345 | 0.392 | 0.389 | 0.428 |
| `mono_r192` | A | r192 · s17 · all 6 | 1.063 | 0.414 | 0.373 | 0.372 | 0.366 | 0.377 | 0.410 | 0.414 | 0.408 | 0.205 | 0.331 | 0.338 | 0.340 | 0.370 | 0.377 | 0.412 |
| **Leave-one-transform-out — honest unseen-transform folds (§12.10)** | | | | | | | | | | | | | | | | | | |
| `loto_holdL0` | A | r32 · s17 · 5 of 6, **holding out L0** | 0.682 | 0.417 | 0.384 | 0.374 | 0.384 | 0.391 | 0.419 | — | — | — | — | — | — | — | — | — |
| `loto_holdL1b` | A | r32 · s17 · 5 of 6, **holding out L1b** | 0.677 | 0.429 | 0.365 | 0.375 | 0.385 | 0.391 | 0.430 | — | — | — | — | — | — | — | — | — |
| `loto_holdL1r` | A | r32 · s17 · 5 of 6, **holding out L1r** | 0.678 | 0.411 | 0.376 | 0.366 | 0.371 | 0.386 | 0.417 | — | — | — | — | — | — | — | — | — |
| `loto_holdL2` | A | r32 · s17 · 5 of 6, **holding out L2** | 0.802 | 0.413 | 0.376 | 0.375 | 0.367 | 0.391 | 0.415 | — | — | — | — | — | — | — | — | — |
| `loto_holdS1` | A | r32 · s17 · 5 of 6, **holding out S1** | 0.805 | 0.419 | 0.379 | 0.379 | 0.387 | 0.373 | 0.417 | — | — | — | — | — | — | — | — | — |
| `loto_holdS2` | A | r32 · s17 · 5 of 6, **holding out S2** | 0.684 | 0.422 | 0.381 | 0.375 | 0.381 | 0.393 | 0.393 | — | — | — | — | — | — | — | — | — |
| **RQ2 — routing and the six-specialist merges (§5.2)** | | | | | | | | | | | | | | | | | | |
| `router` | B | 6 experts · classifier dispatch | — | 0.500 | 0.460 | 0.466 | 0.506 | 0.434 | 0.472 | — | — | — | — | — | — | — | — | — |
| `merge_ties` | A | 6 experts · TIES · d0.5 | 0.069 | — | — | — | — | — | — | — | — | 0.195 | — | — | — | — | — | — |
| `merge_ties` | B | 6 experts · TIES · d0.5 | 0.069 | 0.415 | 0.318 | 0.341 | 0.386 | 0.386 | 0.324 | 0.364 | 0.375 | 0.287 | 0.400 | 0.393 | 0.320 | 0.347 | 0.330 | 0.369 |
| `merge_dare_ties` | A | 6 experts · DARE-TIES · d0.5 | 0.226 | — | — | — | — | — | — | — | — | 0.239 | — | — | — | — | — | — |
| `merge_dare_ties` | B | 6 experts · DARE-TIES · d0.5 | 0.226 | 0.494 | 0.398 | 0.420 | 0.500 | 0.441 | 0.443 | 0.466 | 0.455 | 0.348 | 0.400 | 0.440 | 0.407 | 0.443 | 0.432 | 0.466 |
| `merge_ties_s42` | B | 6 experts · TIES · d0.5 · s42 bank | 0.070 | 0.415 | 0.324 | 0.330 | 0.392 | 0.379 | 0.330 | — | — | 0.278 | — | — | — | — | — | — |
| `merge_dare_ties_s42` | A | 6 experts · DARE-TIES · d0.5 · s42 bank | 0.231 | — | — | — | — | — | — | — | — | 0.249 | — | — | — | — | — | — |
| `merge_dare_ties_s42` | B | 6 experts · DARE-TIES · d0.5 · s42 bank | 0.231 | 0.506 | 0.403 | 0.438 | 0.489 | 0.434 | 0.466 | — | — | 0.383 | — | — | — | — | — | — |
| `merge_dare_linear` | B | 6 experts · DARE-linear · d0.5 — **defect** | 2.024 | 0.040 | 0.040 | 0.028 | 0.023 | 0.048 | 0.062 | 0.040 | 0.080 | 0.061 | 0.073 | 0.027 | 0.053 | 0.028 | 0.080 | 0.062 |
| `dl_rescaled` | B | 6 experts · DARE-linear **rescaled** (repair) | 0.282 | 0.472 | 0.398 | 0.449 | 0.511 | 0.441 | 0.460 | 0.460 | 0.466 | — | 0.420 | 0.460 | 0.420 | 0.460 | 0.426 | 0.472 |
| **RQ2 merge controls (§12.10, §12.12)** | | | | | | | | | | | | | | | | | | |
| `l0merge_ties` | A | **3× clean-code adapters** s17/42/101 · TIES · d0.5 | 0.197 | — | — | — | — | — | — | — | — | 0.213 | — | — | — | — | — | — |
| `l0merge_ties` | B | **3× clean-code adapters** s17/42/101 · TIES · d0.5 | 0.197 | 0.466 | 0.347 | 0.375 | 0.438 | 0.400 | 0.386 | — | — | 0.304 | — | — | — | — | — | — |
| `l0merge_dare_ties` | A | **3× clean-code adapters** s17/42/101 · DARE-TIES · d0.5 | 0.457 | — | — | — | — | — | — | — | — | 0.214 | — | — | — | — | — | — |
| `l0merge_dare_ties` | B | **3× clean-code adapters** s17/42/101 · DARE-TIES · d0.5 | 0.457 | 0.466 | 0.352 | 0.409 | 0.460 | 0.407 | 0.409 | — | — | 0.339 | — | — | — | — | — | — |
| `crossseed_ties` | B | 6 experts, **each a different seed** · TIES · d0.5 | 0.089 | 0.415 | 0.330 | 0.324 | 0.381 | 0.379 | 0.318 | — | — | 0.287 | — | — | — | — | — | — |
| `crossseed_dare_ties` | B | 6 experts, **each a different seed** · DARE-TIES · d0.5 | 0.245 | 0.455 | 0.369 | 0.409 | 0.449 | 0.400 | 0.398 | — | — | 0.313 | — | — | — | — | — | — |
| **RQ2 merge density sweep and the residual-preserving merge (§12.12)** | | | | | | | | | | | | | | | | | | |
| `sweep_ties_d0p3` | B | 6 experts · TIES · d0.3 — density sweep | 0.066 | 0.415 | 0.312 | 0.341 | 0.369 | 0.366 | 0.330 | — | — | — | — | — | — | — | — | — |
| `sweep_ties_d0p5` | B | 6 experts · TIES · d0.5 — density sweep | 0.069 | 0.409 | 0.324 | 0.341 | 0.381 | 0.386 | 0.312 | — | — | — | — | — | — | — | — | — |
| `sweep_ties_d0p7` | B | 6 experts · TIES · d0.7 — density sweep | 0.064 | 0.415 | 0.312 | 0.341 | 0.398 | 0.393 | 0.318 | — | — | — | — | — | — | — | — | — |
| `sweep_dare_ties_d0p3` | B | 6 experts · DARE-TIES · d0.3 — density sweep | 0.566 | 0.483 | 0.426 | 0.494 | 0.489 | 0.441 | 0.489 | — | — | 0.322 | — | — | — | — | — | — |
| `sweep_dare_ties_d0p5` | B | 6 experts · DARE-TIES · d0.5 — density sweep | 0.226 | 0.483 | 0.381 | 0.420 | 0.489 | 0.455 | 0.455 | — | — | — | — | — | — | — | — | — |
| `sweep_dare_ties_d0p7` | B | 6 experts · DARE-TIES · d0.7 — density sweep | 0.115 | 0.460 | 0.312 | 0.392 | 0.443 | 0.421 | 0.403 | — | — | — | — | — | — | — | — | — |
| `uniform_n8_s17_d0p5` | A | 8 experts · uniform weights · d0.5 | 0.168 | — | — | — | — | — | — | — | — | 0.231 | — | — | — | — | — | — |
| `uniform_n8_s17_d0p5` | B | 8 experts · uniform weights · d0.5 | 0.168 | — | — | — | — | — | — | — | — | 0.357 | — | — | — | — | — | — |
| `residual_ties_d0p3` | B | 6 experts · **residual-preserving** · TIES · d0.3 | 0.081 | 0.409 | 0.324 | 0.341 | 0.364 | 0.372 | 0.341 | — | — | — | — | — | — | — | — | — |
| `residual_ties_d0p5` | B | 6 experts · **residual-preserving** · TIES · d0.5 | 0.082 | 0.409 | 0.324 | 0.347 | 0.386 | 0.386 | 0.352 | — | — | 0.296 | — | — | — | — | — | — |
| `residual_dare_ties_d0p3` | B | 6 experts · **residual-preserving** · DARE-TIES · d0.3 | 0.721 | 0.443 | 0.364 | 0.455 | 0.466 | 0.379 | 0.432 | — | — | — | — | — | — | — | — | — |
| `residual_dare_ties_d0p5` | B | 6 experts · **residual-preserving** · DARE-TIES · d0.5 | 0.267 | 0.472 | 0.392 | 0.460 | 0.500 | 0.448 | 0.477 | — | — | 0.417 | — | — | — | — | — | — |
| `residual_n6_s17_d0p5` | A | 6 experts · **residual-preserving** · s17 · TIES · d0.5 | 0.362 | — | — | — | — | — | — | — | — | 0.259 | — | — | — | — | — | — |
| `residual_n6_s17_d0p5` | B | 6 experts · **residual-preserving** · s17 · TIES · d0.5 | 0.362 | — | — | — | — | — | — | — | — | 0.374 | — | — | — | — | — | — |
| `residual_n6_s42_d0p5` | A | 6 experts · **residual-preserving** · s42 · TIES · d0.5 | 0.359 | — | — | — | — | — | — | — | — | 0.256 | — | — | — | — | — | — |
| `residual_n6_s42_d0p5` | B | 6 experts · **residual-preserving** · s42 · TIES · d0.5 | 0.359 | — | — | — | — | — | — | — | — | 0.417 | — | — | — | — | — | — |
| `residual_n8_s17_d0p5` | A | 8 experts · **residual-preserving** · s17 · TIES · d0.5 | 0.168 | — | — | — | — | — | — | — | — | 0.253 | — | — | — | — | — | — |
| **RQ2 attempted repairs — all null (§12.11)** | | | | | | | | | | | | | | | | | | |
| `s2fam` | A | r32 · s17 · S2+S3+S4 · 14,037 rows | 0.633 | 0.444 | 0.320 | 0.366 | 0.368 | 0.414 | 0.438 | — | — | 0.266 | — | — | — | — | — | — |
| `composite_trained` | A | r32 · s17 · 6 stacked C_* · 22,152 rows | 0.804 | 0.398 | 0.379 | 0.378 | 0.373 | 0.383 | 0.397 | — | — | 0.194 | — | — | — | — | — | — |
| `composite_ablation` | A | r32 · s17 · same 6 mechanisms **unstacked** | 0.682 | 0.423 | 0.386 | 0.377 | 0.379 | 0.395 | 0.428 | — | — | 0.237 | — | — | — | — | — | — |
| **RouterLoRA ladder, including the balanced gate (§5.4, §12.8–§12.10)** | | | | | | | | | | | | | | | | | | |
| `mole_uniform` | B | 8 experts · gate frozen uniform | — | 0.466 | 0.392 | 0.506 | 0.500 | 0.441 | 0.477 | 0.449 | 0.466 | 0.330 | 0.367 | 0.413 | 0.393 | 0.466 | 0.443 | 0.449 |
| `mole_random` | B | 8 experts · gate frozen at random init | — | 0.466 | 0.386 | 0.500 | 0.500 | 0.448 | 0.483 | 0.449 | 0.472 | 0.330 | 0.360 | 0.407 | 0.380 | 0.449 | 0.443 | 0.449 |
| `mole_router` | B | 8 experts · trained gate | — | 0.494 | 0.477 | 0.511 | 0.523 | 0.476 | 0.494 | 0.443 | 0.489 | 0.339 | 0.407 | 0.420 | 0.420 | 0.540 | 0.460 | 0.477 |
| `mole_hardrouter` | B | 8 experts · trained gate, argmax one-hot | — | 0.489 | 0.477 | 0.517 | 0.517 | 0.469 | 0.483 | 0.438 | 0.494 | 0.322 | 0.413 | 0.420 | 0.447 | 0.523 | 0.477 | 0.477 |
| `mole_router_bal` | B | 8 experts · trained gate **+ load balancing** | — | — | — | 0.517 | — | 0.483 | — | — | — | — | 0.413 | 0.413 | 0.427 | 0.528 | 0.466 | 0.494 |
| `mole_hardrouter_bal` | B | 8 experts · balanced gate, argmax one-hot | — | — | — | 0.523 | — | 0.469 | — | — | — | — | 0.407 | 0.420 | 0.447 | 0.528 | 0.472 | 0.489 |
| **Uniform-epoch merges, 8-expert bank (§5.3)** | | | | | | | | | | | | | | | | | | |
| `ties_e1` | B | 8 experts · TIES · @ e1 | 0.058 | 0.392 | 0.324 | 0.341 | 0.381 | 0.379 | 0.318 | — | — | — | — | — | — | — | — | — |
| `ties_e2` | B | 8 experts · TIES · @ e2 | 0.070 | 0.415 | 0.324 | 0.341 | 0.398 | 0.386 | 0.318 | — | — | — | — | — | — | — | — | — |
| `ties_e3` | B | 8 experts · TIES · @ e3 | 0.071 | 0.415 | 0.324 | 0.341 | 0.381 | 0.379 | 0.312 | — | — | — | — | — | — | — | — | — |
| `ties_e6` | B | 8 experts · TIES · @ e6 | — | — | 0.369 | — | — | 0.400 | 0.392 | — | — | — | — | — | — | — | — | — |
| `ties_e9` | B | 8 experts · TIES · @ e9 | — | — | 0.358 | — | — | 0.428 | 0.403 | — | — | — | — | — | — | — | — | — |
| `dare_ties_e1` | B | 8 experts · DARE-TIES · @ e1 | 0.190 | 0.466 | 0.386 | 0.426 | 0.460 | 0.434 | 0.460 | — | — | — | — | — | — | — | — | — |
| `dare_ties_e2` | B | 8 experts · DARE-TIES · @ e2 | 0.230 | 0.494 | 0.381 | 0.426 | 0.477 | 0.434 | 0.466 | — | — | — | — | — | — | — | — | — |
| `dare_ties_e3` | B | 8 experts · DARE-TIES · @ e3 | 0.236 | 0.477 | 0.403 | 0.449 | 0.500 | 0.448 | 0.460 | — | — | — | — | — | — | — | — | — |
| `dare_ties_e6` | B | 8 experts · DARE-TIES · @ e6 | — | — | 0.420 | — | — | 0.441 | 0.489 | — | — | — | — | — | — | — | — | — |
| `dare_ties_e9` | B | 8 experts · DARE-TIES · @ e9 | — | — | 0.443 | — | — | 0.441 | 0.483 | — | — | — | — | — | — | — | — | — |
| `overtrain_full_ties_e1` | B | 8-expert bank · TIES · uniform @ e1 | 0.056 | 0.392 | 0.307 | 0.335 | 0.386 | 0.366 | 0.330 | 0.358 | 0.364 | — | 0.380 | 0.387 | 0.307 | 0.318 | 0.324 | 0.352 |
| `overtrain_full_ties_e3` | B | 8-expert bank · TIES · uniform @ e3 | 0.101 | 0.403 | 0.318 | 0.341 | 0.398 | 0.379 | 0.318 | 0.364 | 0.369 | — | 0.387 | 0.393 | 0.313 | 0.341 | 0.330 | 0.364 |
| `overtrain_full_ties_e6` | B | 8-expert bank · TIES · uniform @ e6 | 0.119 | 0.409 | 0.312 | 0.341 | 0.392 | 0.359 | 0.347 | 0.364 | 0.375 | — | 0.387 | 0.407 | 0.333 | 0.364 | 0.341 | 0.364 |
| `overtrain_full_ties_e9` | B | 8-expert bank · TIES · uniform @ e9 | 0.121 | 0.415 | 0.307 | 0.347 | 0.398 | 0.393 | 0.352 | 0.369 | 0.381 | — | 0.393 | 0.407 | 0.340 | 0.352 | 0.335 | 0.375 |
| `overtrain_full_dare_ties_e1` | B | 8-expert bank · DARE-TIES · uniform @ e1 | 0.186 | 0.455 | 0.369 | 0.432 | 0.455 | 0.428 | 0.455 | 0.438 | 0.477 | — | 0.393 | 0.440 | 0.387 | 0.455 | 0.398 | 0.443 |
| `overtrain_full_dare_ties_e3` | B | 8-expert bank · DARE-TIES · uniform @ e3 | 0.326 | 0.494 | 0.398 | 0.443 | 0.472 | 0.455 | 0.443 | 0.489 | 0.466 | — | 0.380 | 0.447 | 0.380 | 0.460 | 0.426 | 0.455 |
| `overtrain_full_dare_ties_e6` | B | 8-expert bank · DARE-TIES · uniform @ e6 | 0.383 | 0.494 | 0.420 | 0.455 | 0.494 | 0.476 | 0.438 | 0.460 | 0.472 | — | 0.427 | 0.453 | 0.393 | 0.438 | 0.426 | 0.438 |
| `overtrain_full_dare_ties_e9` | B | 8-expert bank · DARE-TIES · uniform @ e9 | 0.387 | 0.483 | 0.443 | 0.438 | 0.477 | 0.476 | 0.466 | 0.466 | 0.460 | — | 0.427 | 0.453 | 0.413 | 0.438 | 0.432 | 0.449 |
| **3-expert overtrain sweep (§5.3)** | | | | | | | | | | | | | | | | | | |
| `overtrain_sweep_ties_e1` | B | 3-expert probe · TIES · uniform @ e1 | 0.107 | 0.409 | 0.352 | 0.375 | 0.403 | 0.400 | 0.392 | 0.392 | 0.426 | — | 0.380 | 0.400 | 0.360 | 0.426 | 0.341 | 0.403 |
| `overtrain_sweep_ties_e3` | B | 3-expert probe · TIES · uniform @ e3 | 0.191 | 0.455 | 0.364 | 0.420 | 0.438 | 0.414 | 0.420 | 0.415 | 0.443 | — | 0.380 | 0.400 | 0.360 | 0.443 | 0.415 | 0.426 |
| `overtrain_sweep_ties_e6` | B | 3-expert probe · TIES · uniform @ e6 | 0.226 | 0.449 | 0.364 | 0.415 | 0.443 | 0.393 | 0.409 | 0.438 | 0.443 | — | 0.373 | 0.393 | 0.373 | 0.420 | 0.392 | 0.415 |
| `overtrain_sweep_ties_e9` | B | 3-expert probe · TIES · uniform @ e9 | 0.228 | 0.449 | 0.364 | 0.409 | 0.460 | 0.428 | 0.409 | 0.432 | 0.438 | — | 0.373 | 0.393 | 0.393 | 0.438 | 0.386 | 0.432 |
| `overtrain_sweep_dare_ties_e1` | B | 3-expert probe · DARE-TIES · uniform @ e1 | 0.331 | 0.477 | 0.375 | 0.438 | 0.438 | 0.441 | 0.460 | 0.443 | 0.466 | — | 0.353 | 0.407 | 0.367 | 0.443 | 0.432 | 0.466 |
| `overtrain_sweep_dare_ties_e3` | B | 3-expert probe · DARE-TIES · uniform @ e3 | 0.575 | 0.483 | 0.409 | 0.477 | 0.477 | 0.476 | 0.460 | 0.460 | 0.489 | — | 0.373 | 0.420 | 0.367 | 0.489 | 0.455 | 0.483 |
| `overtrain_sweep_dare_ties_e6` | B | 3-expert probe · DARE-TIES · uniform @ e6 | 0.674 | 0.466 | 0.426 | 0.483 | 0.489 | 0.441 | 0.494 | 0.466 | 0.506 | — | 0.373 | 0.400 | 0.407 | 0.494 | 0.443 | 0.494 |
| `overtrain_sweep_dare_ties_e9` | B | 3-expert probe · DARE-TIES · uniform @ e9 | 0.680 | 0.472 | 0.432 | 0.489 | 0.494 | 0.434 | 0.494 | 0.460 | 0.489 | — | 0.380 | 0.407 | 0.420 | 0.494 | 0.466 | 0.483 |
| **Individual over-trained experts (§5.3)** | | | | | | | | | | | | | | | | | | |
| `ot_L1b_e1` | B | r32 · s17 · L1b · @ e1 | 0.295 | 0.455 | 0.409 | 0.420 | 0.438 | 0.421 | 0.438 | 0.455 | 0.455 | — | 0.353 | 0.407 | 0.367 | 0.398 | 0.415 | 0.443 |
| `ot_L1b_e3` | B | r32 · s17 · L1b · @ e3 | 0.526 | 0.466 | 0.466 | 0.506 | 0.483 | 0.441 | 0.398 | 0.460 | 0.443 | — | 0.340 | 0.427 | 0.393 | 0.477 | 0.449 | 0.449 |
| `ot_L1b_e6` | B | r32 · s17 · L1b · @ e6 | 0.622 | 0.472 | 0.466 | 0.500 | 0.489 | 0.372 | 0.426 | 0.438 | 0.460 | — | 0.427 | 0.440 | 0.420 | 0.455 | 0.443 | 0.432 |
| `ot_L1b_e9` | B | r32 · s17 · L1b · @ e9 | 0.629 | 0.489 | 0.466 | 0.489 | 0.517 | 0.400 | 0.438 | 0.432 | 0.466 | — | 0.393 | 0.413 | 0.407 | 0.489 | 0.460 | 0.432 |
| `ot_S1_e1` | B | r32 · s17 · S1 · @ e1 | 0.262 | 0.438 | 0.318 | 0.409 | 0.420 | 0.393 | 0.398 | 0.403 | 0.432 | — | 0.400 | 0.353 | 0.327 | 0.438 | 0.398 | 0.409 |
| `ot_S1_e3` | B | r32 · s17 · S1 · @ e3 | 0.458 | 0.438 | 0.352 | 0.403 | 0.420 | 0.421 | 0.392 | 0.432 | 0.426 | — | 0.380 | 0.413 | 0.313 | 0.398 | 0.341 | 0.392 |
| `ot_S1_e6` | B | r32 · s17 · S1 · @ e6 | 0.541 | 0.443 | 0.386 | 0.392 | 0.449 | 0.428 | 0.449 | 0.443 | 0.477 | — | 0.427 | 0.380 | 0.327 | 0.449 | 0.358 | 0.466 |
| `ot_S1_e9` | B | r32 · s17 · S1 · @ e9 | 0.547 | 0.426 | 0.369 | 0.381 | 0.432 | 0.441 | 0.443 | 0.415 | 0.483 | — | 0.380 | 0.387 | 0.327 | 0.432 | 0.330 | 0.443 |
| `ot_S2_e1` | B | r32 · s17 · S2 · @ e1 | 0.300 | 0.443 | 0.375 | 0.460 | 0.438 | 0.462 | 0.438 | 0.455 | 0.460 | — | 0.320 | 0.373 | 0.313 | 0.438 | 0.409 | 0.438 |
| `ot_S2_e3` | B | r32 · s17 · S2 · @ e3 | 0.528 | 0.483 | 0.398 | 0.477 | 0.494 | 0.441 | 0.489 | 0.477 | 0.494 | — | 0.393 | 0.367 | 0.333 | 0.500 | 0.455 | 0.455 |
| `ot_S2_e6` | B | r32 · s17 · S2 · @ e6 | 0.622 | 0.477 | 0.386 | 0.483 | 0.483 | 0.421 | 0.455 | 0.477 | 0.489 | — | 0.347 | 0.373 | 0.360 | 0.466 | 0.443 | 0.466 |
| `ot_S2_e9` | B | r32 · s17 · S2 · @ e9 | 0.629 | 0.477 | 0.398 | 0.494 | 0.489 | 0.448 | 0.460 | 0.483 | 0.477 | — | 0.360 | 0.380 | 0.373 | 0.466 | 0.415 | 0.477 |
| **Merge-optimal search — every round's candidates (§5.2)** | | | | | | | | | | | | | | | | | | |
| `mo_r1_L0_e1_ae1a2d64` | B | merge-optimal round 1 · L0 @ e1 | 0.272 | 0.489 | 0.386 | 0.438 | 0.460 | 0.428 | 0.426 | 0.460 | 0.472 | — | 0.413 | 0.433 | 0.400 | 0.449 | 0.426 | 0.443 |
| `mo_r1_L0_e2_062a66bb` | B | merge-optimal round 1 · L0 @ e2 | 0.280 | 0.483 | 0.381 | 0.432 | 0.477 | 0.421 | 0.432 | 0.466 | 0.472 | — | 0.407 | 0.420 | 0.407 | 0.438 | 0.432 | 0.443 |
| `mo_r1_L0_e3_d6c84724` | B | merge-optimal round 1 · L0 @ e3 | 0.285 | 0.477 | 0.381 | 0.426 | 0.472 | 0.434 | 0.432 | 0.466 | 0.477 | — | 0.413 | 0.427 | 0.393 | 0.449 | 0.426 | 0.449 |
| `mo_r1_L0_e4_275dd9db` | B | merge-optimal round 1 · L0 @ e4 | 0.288 | 0.483 | 0.375 | 0.432 | 0.477 | 0.428 | 0.426 | 0.455 | 0.477 | — | 0.413 | 0.427 | 0.393 | 0.432 | 0.426 | 0.443 |
| `mo_r1_L0_e5_93c15bdc` | B | merge-optimal round 1 · L0 @ e5 | 0.290 | 0.477 | 0.381 | 0.426 | 0.477 | 0.428 | 0.432 | 0.466 | 0.472 | — | 0.420 | 0.413 | 0.393 | 0.443 | 0.420 | 0.443 |
| `mo_r1_L0_e6_7db432a5` | B | merge-optimal round 1 · L0 @ e6 | 0.290 | 0.472 | 0.381 | 0.432 | 0.466 | 0.434 | 0.432 | 0.460 | 0.477 | — | 0.413 | 0.413 | 0.400 | 0.438 | 0.409 | 0.449 |
| `mo_r1_L0_e7_05d4a760` | B | merge-optimal round 1 · L0 @ e7 | 0.291 | 0.477 | 0.386 | 0.432 | 0.466 | 0.428 | 0.426 | 0.466 | 0.466 | — | 0.413 | 0.413 | 0.387 | 0.432 | 0.415 | 0.449 |
| `mo_r1_L0_e8_a70f0773` | B | merge-optimal round 1 · L0 @ e8 | 0.291 | 0.483 | 0.381 | 0.420 | 0.483 | 0.441 | 0.432 | 0.466 | 0.472 | — | 0.420 | 0.413 | 0.393 | 0.443 | 0.426 | 0.443 |
| `mo_r1_L0_e9_bd8a806c` | B | merge-optimal round 1 · L0 @ e9 | 0.291 | 0.477 | 0.381 | 0.432 | 0.477 | 0.434 | 0.432 | 0.460 | 0.466 | — | 0.420 | 0.413 | 0.400 | 0.426 | 0.420 | 0.432 |
| `mo_r2_L1b_e1_e0656264` | B | merge-optimal round 2 · L1b @ e1 | 0.272 | 0.472 | 0.369 | 0.438 | 0.477 | 0.434 | 0.432 | 0.455 | 0.472 | — | 0.413 | 0.420 | 0.393 | 0.455 | 0.426 | 0.449 |
| `mo_r2_L1b_e2_ae58e683` | B | merge-optimal round 2 · L1b @ e2 | 0.280 | 0.483 | 0.375 | 0.438 | 0.466 | 0.434 | 0.438 | 0.466 | 0.466 | — | 0.420 | 0.427 | 0.393 | 0.449 | 0.426 | 0.449 |
| `mo_r2_L1b_e3_9e8b75f6` | B | merge-optimal round 2 · L1b @ e3 | 0.285 | 0.483 | 0.381 | 0.432 | 0.472 | 0.428 | 0.432 | 0.466 | 0.472 | — | 0.413 | 0.433 | 0.393 | 0.455 | 0.426 | 0.443 |
| `mo_r2_L1b_e4_126c69e4` | B | merge-optimal round 2 · L1b @ e4 | 0.288 | 0.466 | 0.375 | 0.438 | 0.477 | 0.428 | 0.432 | 0.466 | 0.472 | — | 0.420 | 0.427 | 0.393 | 0.438 | 0.426 | 0.438 |
| `mo_r2_L1b_e5_7e95cee8` | B | merge-optimal round 2 · L1b @ e5 | 0.290 | 0.483 | 0.381 | 0.438 | 0.477 | 0.428 | 0.432 | 0.466 | 0.472 | — | 0.413 | 0.420 | 0.400 | 0.426 | 0.420 | 0.443 |
| `mo_r2_L1b_e6_351cbd10` | B | merge-optimal round 2 · L1b @ e6 | 0.290 | 0.489 | 0.386 | 0.438 | 0.466 | 0.434 | 0.426 | 0.466 | 0.472 | — | 0.413 | 0.413 | 0.393 | 0.443 | 0.420 | 0.438 |
| `mo_r2_L1b_e7_4b624330` | B | merge-optimal round 2 · L1b @ e7 | 0.291 | 0.477 | 0.392 | 0.438 | 0.477 | 0.434 | 0.438 | 0.466 | 0.466 | — | 0.413 | 0.413 | 0.400 | 0.426 | 0.415 | 0.443 |
| `mo_r2_L1b_e8_70780f97` | B | merge-optimal round 2 · L1b @ e8 | 0.291 | 0.477 | 0.386 | 0.426 | 0.483 | 0.434 | 0.432 | 0.466 | 0.477 | — | 0.413 | 0.413 | 0.400 | 0.438 | 0.432 | 0.443 |
| `mo_r2_L1b_e9_a70f0773` | B | merge-optimal round 2 · L1b @ e9 | 0.291 | 0.472 | 0.381 | 0.426 | 0.477 | 0.434 | 0.438 | 0.466 | 0.472 | — | 0.413 | 0.413 | 0.400 | 0.443 | 0.415 | 0.443 |
| `mo_r3_L1r_e1_63242db2` | B | merge-optimal round 3 · L1r @ e1 | 0.272 | 0.483 | 0.392 | 0.420 | 0.477 | 0.428 | 0.432 | 0.466 | 0.455 | — | 0.413 | 0.427 | 0.393 | 0.443 | 0.426 | 0.443 |
| `mo_r3_L1r_e2_e0652d4c` | B | merge-optimal round 3 · L1r @ e2 | 0.279 | 0.472 | 0.381 | 0.432 | 0.483 | 0.428 | 0.426 | 0.466 | 0.472 | — | 0.413 | 0.427 | 0.393 | 0.455 | 0.438 | 0.443 |
| `mo_r3_L1r_e3_b398408b` | B | merge-optimal round 3 · L1r @ e3 | 0.285 | 0.477 | 0.386 | 0.443 | 0.483 | 0.434 | 0.432 | 0.466 | 0.483 | — | 0.413 | 0.420 | 0.393 | 0.443 | 0.432 | 0.443 |
| `mo_r3_L1r_e4_7118282b` | B | merge-optimal round 3 · L1r @ e4 | 0.288 | 0.477 | 0.381 | 0.432 | 0.472 | 0.434 | 0.426 | 0.460 | 0.483 | — | 0.413 | 0.420 | 0.393 | 0.438 | 0.432 | 0.449 |
| `mo_r3_L1r_e5_390562f2` | B | merge-optimal round 3 · L1r @ e5 | 0.289 | 0.477 | 0.386 | 0.426 | 0.472 | 0.434 | 0.432 | 0.466 | 0.472 | — | 0.413 | 0.413 | 0.387 | 0.432 | 0.426 | 0.443 |
| `mo_r3_L1r_e6_ac4dd90b` | B | merge-optimal round 3 · L1r @ e6 | 0.290 | 0.483 | 0.375 | 0.432 | 0.477 | 0.428 | 0.426 | 0.460 | 0.477 | — | 0.413 | 0.420 | 0.407 | 0.438 | 0.420 | 0.438 |
| `mo_r3_L1r_e7_d137d7e6` | B | merge-optimal round 3 · L1r @ e7 | 0.290 | 0.489 | 0.386 | 0.432 | 0.472 | 0.434 | 0.432 | 0.466 | 0.472 | — | 0.413 | 0.413 | 0.400 | 0.426 | 0.415 | 0.443 |
| `mo_r3_L1r_e8_15c7bd7d` | B | merge-optimal round 3 · L1r @ e8 | 0.291 | 0.483 | 0.381 | 0.432 | 0.472 | 0.434 | 0.432 | 0.466 | 0.477 | — | 0.413 | 0.427 | 0.393 | 0.432 | 0.415 | 0.443 |
| `mo_r3_L1r_e9_4b624330` | B | merge-optimal round 3 · L1r @ e9 | 0.291 | 0.483 | 0.386 | 0.426 | 0.483 | 0.434 | 0.432 | 0.466 | 0.466 | — | 0.420 | 0.413 | 0.387 | 0.438 | 0.415 | 0.443 |


**Why the blanks are blank — a `—` is not one thing.** *Coverage at the 27 August regeneration:
**1,779 of 2,464** cells (154 systems × 16 columns) = **72.2 %**. The apparent drop from the 08-12
revision's 94.7 % is entirely composition — 54 systems were added, most of them merge and sweep
variants that were only ever run on the six trainable conditions.*

| column | filled | why the rest are blank |
|---|---|---|
| `L0`–`S2` (the six trainable) | 138–148 of 154 | Near-complete. Missing only where an arm is defined for one condition (`ot_*`, `mo_r*` rounds). |
| `S3`, `S4` | 105 | The two `S2` halves were added late (§3.5's decomposition) and the merge/sweep families predate them. |
| **`H1`** | **37 Grid A, 37 Grid B** | **Withheld deliberately.** Every `H1` read spends quarantine budget (§3.2 rule 3), so `H1` is read in batched confirmatory passes, not per-arm. The 37 that exist are the systems a claim actually rests on. |
| six `C_*` composites | 105 | Same as `S3`/`S4` — the composite grid postdates most merge arms. `router` and `oracle_prompt_1shot` are blank here for structural reasons: the first needs an item→adapter route map that covers composites, the second needs `prompts.py` unfrozen to carry an oracle description for them. |

*The 08-12 revision's blank accounting is preserved below, since the composite fill it describes is
the reason Grid A composites exist at all.*

~~114 composite × Grid A cells were previously listed here as **undefined** — "composite variants
exist only on the test set".~~ **That was wrong, and it was wrong twice in this document.** The
`p3_composites` stage built the stacked variants for BOTH `--target train` and `--target testset`,
then called `07_emit_eval_items.py` with no `--source`, which defaults to `testset`. So 1,660–2,228
heldout composite variants per condition had been on disk since 12 August with no eval items emitted
from them, and that absence was mistaken for a structural limit. One CPU command fixed it.

The Grid A composites are the **better** measurement: 1,254–1,671 items over 418–557 programs,
against the 150 items Grid B carries — 8–10× the statistical power on precisely the condition where
a mixture-over-experts is supposed to have headroom. The `S1`-bearing composites carry 418 programs
rather than 557 because `S1` bails on short bodies by design, the same coverage limit `S1` alone has.

**Two errors this fill exposed in the table itself, both now corrected.**

1. **The `base` Grid A row carried Grid B numbers in its six composite columns** (n=150/176
   values under an `A` label). That is the "never difference an A row against a B row" rule being
   broken *inside a single row*, and it survived because those cells were populated — so no blank
   ever drew attention to them. The Grid A values are markedly lower: `C_L1r_S1` .267 → **.176**,
   `C_L1b_S1` .313 → **.156**.
2. **`base` was being read through two different engines.** `main/base__C_*` was written by the
   HF mixture engine (`hf-mole`) as part of the RouterLoRA ladder, while every other `base` cell
   comes from vLLM. Same prompt sha, same n — and up to **4 points apart** (`C_L2_S4` .216 vs
   .176). That is the 2026-08-11 "`base` through the mixture engine is not base" hazard, showing
   up as a reference row rather than a system row.

The table is therefore now built from a **documented source preference**, not from whichever cell
a glob happened to return first: match the row's grid; prefer vLLM over `hf-mole` for every row
*except* `mole_*`, which are the mixture and must be read through it; then larger *n*, then newer.
A `base` reference taken from `hf-mole` while every system row is vLLM would fold a 4-point engine
offset into every delta computed against it.

Everything filled was eval-only — every adapter, merge and gate already existed. `norm_*` on
composites was soundness-gated first (2,355 items × 4 profiles, 0 unsound): that arm scores a
*rewritten* program against the *original's* output, and the gate had only ever covered the
single-transform ladder.

**What to look at first.**

* **`base` vs `tuned_L0`** — the untuned model gets .217 on clean code and .064 on held-out `H1`;
  training on *clean code alone* lifts `H1` to .247. That single row is why every delta in this
  report is control-relative rather than measured against `base`.
* **The specialist diagonal is shallow.** On Grid A the own-condition cells (`tuned_L1b` on `L1b`
  = .384, `tuned_S2` on `S2` = .453) sit only 3–4 points above the control row, which is the
  p95 seed-noise band (§3.7).
* **`merge_dare_linear`** is the broken merge (.023–.062); `dl_rescaled` is the scale-corrected
  re-run of it and lands where the working merges do (.398–.511), confirming §5.2's diagnosis that
  the collapse was a magnitude artifact, not a method result.
* **`overtrain_full_dare_ties_e1 → e9`** rises on five of six conditions — the Part V result that
  runs opposite to the paper's prediction (§5.3).
* **`mole_router` beats both of its controls on all six composites** (§5.4), and `mole_uniform` vs
  `mole_random` differ, which is what makes that comparison mean anything.
* **The two `base` rows are the grid warning made concrete.** Same model, same prompt, no
  training — `.217` vs `.290` on L0 and `.064` vs `.113` on H1, purely because Grid B's 40 ICSE
  programs are easier than Grid A's 557. The H1 gap alone (4.9 pts) exceeds most effects in this
  report, which is why an A row and a B row are never differenced.

**Notes on the shot-count block** (*added 14 August 2026*; numbers are §11 Table 39 re-expressed
as accuracies, from `results/cells/baselines/qwen25c-1.5b/python/`, `experiment_id=icl_k_sweep`).

* `tuned_L0_k0` **is** `tuned_L0` evaluated on Grid B — identical adapter (sha
  `82329cd…`), identical prompt template (sha `c1e8fe2…`), zero demonstrations. It is listed
  under its run name rather than merged into the `tuned_L0` row because that row is Grid A. The
  pair `tuned_L0` (A) / `tuned_L0_k0` (B) is therefore the same system on both grids and is the
  cleanest available illustration of how much the grid alone is worth: `.447 → .506` on L0 and
  `.245 → .348` on H1, with nothing about the system changed.
* Every row in this block is matched item-for-item: 176 items / 40 programs on
  L0/L1b/L1r/L2/S2, 145 / 33 on S1, 115 / 27 on H1 — the same populations as the Grid B
  specialist and merge rows above, verified by snippet-id set comparison.
* `icl_k1` here is the k-sweep's own 1-shot arm, run inside the same job as k2/k4. It is *not*
  the same arm as `icl_k1_clean` / `icl_k1_cross` (§12), which differ in where demos are drawn
  from. S3/S4 are absent because the sweep did not evaluate them.

---

## 3. RQ1 — the transfer matrix

Accuracy on the 317-program Python common subset, seed 17. Higher is better; the row that matters
is the **`L0`-only control**, not the base model.

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| untuned base | .201 | .165 | .164 | .176 | .187 | .147 | .066 |
| **`L0`-only control (the reference)** | **.440** | **.321** | **.353** | **.353** | **.379** | **.411** | **.259** |
| `L1b` specialist | .427 | **.360** | .359 | .354 | .353 | .402 | .263 |
| `L1r` specialist | .445 | .333 | **.383** | .381 | .375 | .422 | .260 |
| `L2` specialist | .436 | .328 | .366 | **.363** | .366 | .419 | .254 |
| `S1` specialist | .433 | .296 | .352 | .355 | **.414** | .418 | .266 |
| `S2` specialist | .459 | .317 | .367 | .365 | .415 | **.445** | **.294** |
| all-conditions (mono, r32) | .392 | .355 | .341 | .359 | .372 | .389 | .228 |
| oracle prompt (untuned + told the type) | .243 | .180 | .197 | .213 | .202 | .226 | .158 |

**Difference from the `L0`-only control, in accuracy points.** `*` = BH-FDR q<0.05 *and* the
cluster-bootstrap CI excludes zero. Seed 17 / seed 42 given as `s17 | s42`; the specialist's own
condition is bold.

| trained on | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| `L1b` | −1.3 \| −0.9 | **+3.9\* \| +6.0\*** | +0.6 \| +1.2 | +0.1 \| +2.0* | −2.6* \| −3.2* | −0.8 \| −0.7 | +0.4 \| −2.0* |
| `L1r` | +0.5 \| −0.6 | +1.2 \| +2.4* | **+3.1\* \| +1.1** | +2.8* \| +2.6* | −0.4 \| −0.2 | +1.2 \| +0.8 | +0.1 \| −0.4 |
| `L2` | −0.4 \| +0.2 | +0.7 \| +1.4 | +1.4 \| +0.1 | **+1.1 \| +1.9** | −1.3 \| −0.8 | +0.8 \| +0.4 | −0.5 \| −0.6 |
| `S1` | −0.7 \| −0.5 | −2.5* \| −1.9 | −0.1 \| −2.1 | +0.2 \| +0.7 | **+3.5\* \| +5.5\*** | +0.7 \| +0.4 | +0.7 \| +0.5 |
| **`S2`** | +1.9 \| +0.6 | −0.4 \| +0.4 | +1.5 \| −0.5 | +1.3 \| +2.0* | +3.6* \| +4.0* | **+3.5\* \| +2.3** | **+3.5\* \| +3.1\*** |
| all-conditions r32 | −4.8* | +3.4* | −1.2 | +0.6 | −0.7 | −2.1 | **−3.1\*** |

Read across the rows:

**3.1 The diagonal is real and small.** Every specialist beats the clean-code control on its own
condition, by +1.1 to +6.0 points. `L2` is the weakest and does not clear significance at either
seed — sequential minification is apparently learnable from general competence.

**3.2 Off the diagonal, almost nothing transfers.** Within the identifier family the `L1r`↔`L2`
pair leaks a little (+2.6 to +2.8 points, significant at both seeds) — unsurprising since both
destroy names without falsifying them. `L1b` gets nothing back from either. Every other
same-family and cross-family cell is inside noise. As a transfer ratio — the fraction of the
specialist's own gain that a foreign adapter reproduces — the **mean off-diagonal TR is 0.073**
(Python s17, 16 cells with a usable denominator; 0.043 at s42, −0.295 in JavaScript). Zero is the
memorization prediction and one is the invariance prediction.

**3.3 Cross-family transfer is negative.** `L1b`→`S1` is −2.6/−3.2 (significant at both seeds) and
`S1`→`L1b` is −2.5/−1.9. Training on adversarial renaming makes a model *worse* at flattened
control flow than training on clean code does. This is the sharpest evidence against a shared
"invariance" representation: the two families actively interfere.

**3.4 The Invariance Index is ~0.** The project's headline quantity — mean control-relative
transfer ratio onto `H1` — has no valid value, because the denominator (an `H1` specialist) cannot
exist by construction; using the raw `H1` column instead, four of five specialists sit inside ±0.7
points of the clean-code control, and the monolithic arm sits 3.1 points below it. Obfuscation
training buys **no** general robustness to an unseen transform.

### 3.5 The `S2` exception — the most interesting result in the project

`S2` (opaque predicates + dead code) is the one arm that behaves like a general skill rather than a
memorized inversion:

| | Python s17 | Python s42 | JS s17 | JS s42 |
|---|---|---|---|---|
| `S2`→`H1` | **+3.5\*** | **+3.1\*** | **+7.3\*** | **+7.7\*** |
| `S2`→`S1` | +3.6* | +4.0* | +6.2* | +2.2 |
| `S2`→own | +3.5* | +2.3 | +8.4* | +6.6* |

Four independent runs (2 seeds × 2 languages) agree, and the effect on `H1` is as large as the
effect on `S2` itself. Seed-to-seed variation of that exact cell is 0.4 points (Python) — far below
the effect. Nothing else in the matrix reaches `H1`.

A plausible mechanism, testable and not yet tested: `S2` and `H1` both bury the real computation
under *inert* material (dead branches / opaque guards vs. encoded strings and MBA-rewritten
arithmetic). Learning "ignore the code that cannot affect the result" is a transferable skill;
learning to invert a renaming is not. The `S1` result cuts the same way in reverse — flattening
*rearranges* rather than *adds*, and `S1` transfers to nothing (and in JavaScript actively damages
`S2`, −12.8 points).

**Caveat that has to travel with this finding:** the S2→H1 direction was measured on the same `H1`
data as everything else, i.e. it is a post-hoc discovery in a 42-cell matrix, not a pre-registered
hypothesis. It survives FDR correction across the matrix and replicates over seeds and languages,
which is a lot — but the confirmatory test would be a *second* held-out transform of the same
"inert padding" family, and the `H1` read budget is now spent (§8.4).

### 3.6 Cross-language: the same shape, with larger swings

The whole matrix again, in JavaScript. Accuracy on the 91-program common subset, seed 17:

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| untuned base | .289 | .223 | .223 | .253 | .245 | .110 | .124 |
| **`L0`-only control (the reference)** | **.527** | **.443** | **.509** | **.527** | **.480** | **.429** | **.238** |
| `L1b` specialist | .527 | **.516** | .505 | .527 | .469 | .392 | .253 |
| `L1r` specialist | .531 | .451 | **.520** | .535 | .491 | .388 | .209 |
| `L2` specialist | .531 | .447 | .509 | **.546** | .491 | .443 | .212 |
| `S1` specialist | .505 | .425 | .465 | .491 | **.502** | .300 | .202 |
| `S2` specialist | .520 | .443 | .516 | .520 | .542 | **.513** | **.311** |
| oracle prompt (untuned + told the type) | .289 | .220 | .238 | .282 | .267 | .264 | .183 |

Difference from the `L0`-only control, in points, `s17 | s42`; `*` = significant; the specialist's
own condition is bold:

| trained on | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| `L1b` | 0.0 \| 0.0 | **+7.3\* \| +7.7\*** | −0.4 \| +2.2 | 0.0 \| −0.4 | −1.1 \| −2.6 | −3.7 \| −9.9* | +1.5 \| +0.7 |
| `L1r` | +0.4 \| +1.8 | +0.7 \| −1.1 | **+1.1 \| +2.9** | +0.7 \| −0.4 | +1.1 \| +1.1 | −4.0 \| −5.5* | −2.9 \| 0.0 |
| `L2` | +0.4 \| +0.4 | +0.4 \| −1.1 | 0.0 \| +1.8 | **+1.8 \| −1.5** | +1.1 \| +2.9* | +1.5 \| −2.2 | −2.6 \| −0.4 |
| `S1` | −2.2 \| −2.9 | −1.8 \| −1.8 | −4.4* \| −3.7 | −3.7 \| −5.5 | **+2.2 \| −2.9** | −12.8* \| −4.8 | −3.7 \| −0.7 |
| **`S2`** | −0.7 \| +0.7 | 0.0 \| +1.5 | +0.7 \| +2.2 | −0.7 \| −2.9 | +6.2* \| +2.2 | **+8.4\* \| +6.6\*** | **+7.3\* \| +7.7\*** |

Compared against the Python matrix (§3.2), four things carry over and two do not:

- **Carries over:** the `L1b` diagonal (+7.3/+7.7 vs Python's +3.9/+6.0); the `S2` diagonal
  (+8.4/+6.6); **`S2`→`H1` as the only route to the held-out transform** (+7.3/+7.7, the largest
  and most consistent effect in either language); and a null-to-negative off-diagonal everywhere else.
- **Does not carry over:** the `L1r`↔`L2` identifier-family leak, which is Python-only — in
  JavaScript those cells flip sign between seeds. And **the `S1` diagonal fails entirely**: the
  `S1` specialist is +2.2 on its own condition at seed 17 and −2.9 at seed 42, i.e. no better than
  clean-code training. `S1` is also the most destructive row (−4.4 on `L1r`, −12.8 on `S2` at s17).
  Control-flow flattening in JavaScript appears not to be learnable as a specialisation at this scale.

Magnitudes run roughly 2× the Python ones because JavaScript accuracies are higher throughout
(control `L0` .527 vs .440), and the intervals are wider because the common subset is 91 programs
rather than 317. Read the JavaScript column for *direction*, not for effect size.

### 3.7 Seed stability

Every adapter retrained from scratch at seed 42 and re-evaluated on the same items. Entries are
**seed 42 minus seed 17, in accuracy points** — so they measure run-to-run noise, not any effect.

**Python** (317-program common subset):

| adapter | L0 | L1b | L1r | L2 | S1 | S2 | H1 | max \|Δ\| |
|---|---|---|---|---|---|---|---|---|
| `L0` control | −0.1 | −0.3 | +0.9 | −0.6 | −0.6 | +0.4 | 0.0 | 0.9 |
| `L1b` | +0.2 | +1.8 | +1.5 | +1.3 | −1.2 | +0.5 | −2.4 | 2.4 |
| `L1r` | −1.3 | +0.9 | −1.1 | −0.8 | −0.4 | +0.1 | −0.5 | 1.3 |
| `L2` | +0.5 | +0.3 | −0.3 | +0.2 | −0.2 | 0.0 | −0.1 | 0.5 |
| `S1` | +0.1 | +0.3 | −1.1 | −0.1 | +1.4 | +0.1 | −0.2 | 1.4 |
| `S2` | −1.4 | +0.5 | −1.1 | +0.1 | −0.2 | −0.7 | −0.4 | 1.4 |

**JavaScript** (91-program common subset):

| adapter | L0 | L1b | L1r | L2 | S1 | S2 | H1 | max \|Δ\| |
|---|---|---|---|---|---|---|---|---|
| `L0` control | −1.5 | −1.5 | −2.6 | 0.0 | +2.9 | +3.7 | +1.1 | 3.7 |
| `L1b` | −1.5 | −1.1 | 0.0 | −0.4 | +1.5 | −2.6 | +0.4 | 2.6 |
| `L1r` | 0.0 | −3.3 | −0.7 | −1.1 | +2.9 | +2.2 | +4.0 | 4.0 |
| `L2` | −1.5 | −2.9 | −0.7 | −3.3 | +4.8 | 0.0 | +3.3 | 4.8 |
| `S1` | −2.2 | −1.5 | −1.8 | −1.8 | −2.2 | **+11.7** | +4.0 | 11.7 |
| `S2` | 0.0 | 0.0 | −1.1 | −2.2 | −1.1 | +1.8 | +1.5 | 2.2 |

Summary over the 42 cells per language:

| | mean \|Δ\| | median \|Δ\| | p95 \|Δ\| | max \|Δ\| | within 1.5 pts | within 4 pts |
|---|---|---|---|---|---|---|
| Python | **0.63** | 0.48 | 1.46 | 2.42 | 95 % | 100 % |
| JavaScript | **2.01** | 1.47 | 4.03 | 11.72 | 52 % | 90 % |
| pooled | 1.32 | 1.05 | 3.61 | 11.72 | 74 % | 95 % |

**Practical rule for reading every table in this report: in Python, differences under ~1.5 points
are not differences; in JavaScript the bar is ~4 points.** Python is genuinely tight — 95 % of
cells move by less than 1.5 points, and the control adapter itself moves by at most 0.9. JavaScript
is roughly 3× noisier, which is what 91 programs buys.

Two consequences:

- **Two starred Python cells fail the bar at the other seed** and should be treated as
  unreplicated: `L1r`→`L1r` (+3.1 at s17, +1.1 at s42) and `L1b`→`L2` (+0.1 at s17, +2.0 at s42).
  Every other starred Python effect, including all three `S2` rows, clears it at both seeds.
- **The single worst cell in the project is `S1`→`S2` in JavaScript, at 11.7 points.** That is the
  cell §3.6 quotes as −12.8, so the *magnitude* of the `S1`→`S2` interference is not a reportable
  number — only its sign, which is negative at both seeds (−12.8, −4.8). The `S2`→`H1` cell, by
  contrast, moves 1.5 points across seeds in JavaScript and 0.4 in Python — far below its own
  effect size, which is what makes §3.5 trustworthy.

---

## 4. Breadth does not help, and capacity is not the reason

The monolithic ("all-conditions") adapter and the rank sweep, against the same `L0` control, on the
317-program Python subset:

| arm | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| mono r32 | −4.8* | +3.4* | −1.2 | +0.6 | −0.7 | −2.1 | **−3.1\*** |
| mono r64 | −3.5* | +4.1* | −0.1 | +1.1 | +0.4 | +0.7 | −1.6 |
| mono r128 | −2.3 | +4.0* | +0.6 | +1.1 | +0.3 | −0.8 | **−4.2\*** |
| mono r192 | −4.5* | +2.8 | +0.1 | +0.1 | −1.9 | −2.0 | **−4.7\*** |
| *control at r64 — the noise floor* | *+0.3* | *−0.4* | *+0.1* | *+0.2* | *−0.1* | *0.0* | *−1.6* |

Training on all five obfuscation types buys `L1b` and costs clean code, and **r=192 — parameter-matched
to six r=32 specialists — is the worst arm on `H1`**. Raising the *control's* own rank changes nothing
(bottom row), which rules out "capacity helps everything uniformly". Training was not the limit either:
the monolithic adapter's validation exact-match is flat across three epochs (0.3698 → 0.3704 → 0.3678)
while its train loss collapses to 0.004 and eval loss nearly doubles — see
[`RESULTS_2026-08-09.md`](RESULTS_2026-08-09.md) §2 for the curves, which this report does not supersede.

Note the contrast that the full matrix makes visible and the monolithic result alone did not:
**a single `S2` specialist reaches `H1` (+3.5) while a generalist trained on `S2` *and* four other
things loses it (−3.1).** Breadth is not neutral; it is actively destructive to the one transfer
that works.

---

## 5. RQ2 — modularity: can six specialists be combined into one system?

> **RE-SCOPED 15 August 2026 — read this before the sections below.** Everything in §5 was written
> as a sequence of combination methods that underperformed: the router saturates, TIES collapses,
> DARE-linear breaks, the mixture gate is flat. §12.10 shows that framing is wrong, and the
> corrected one is stronger.
>
> Four experiments (§12.7–§12.10) eliminate the alternatives in turn. The obfuscation condition
> **is** almost perfectly identifiable from the model's residual stream (linear probe, 99.4 % vs
> 16.7 % chance). The gate **can** be made to use it — adding a load-balancing term revives the
> dead experts and pushes composite routing above chance. And doing so **still** buys +0.4 points,
> inside seed noise. Independently, merging three *clean-code* adapters reaches the same `H1`
> accuracy as merging six specialists (§12.7 control), and holding a transform out of a
> multi-condition adapter costs ~1.1 points — also inside noise (LOTO, §12.10).
>
> So the sections below do not document a series of methods that failed. They document the
> evidence that **there is nothing distinct in the expert bank for a combination method to
> combine.** The negative result is a property of the experts, not of the router, the merge
> algorithm, or the gate. Read §5.2–§5.4 as measurements supporting that claim rather than as
> attempts that fell short.
>
> Two caveats that survive the re-scope: the merge ranking is real (`dare_ties` beats `ties` by
> ~9 points, reproduced on an independent seed-42 expert bank), and merge **density** was never
> swept — d=0.3 beats the d=0.5 default used throughout §5 by 2.3 points on `dare_ties`.

### 5.0 The question, in plain terms

§3 and §4 leave a practical problem. Six separate specialists each work on their own obfuscation
type and nowhere else, and one generalist trained on all six is worse than a clean-code control on
the transform it has never seen. Neither is a usable system. So: **is there a way to combine the
six specialists that keeps each one's benefit?**

Some vocabulary first, because the rest of this section depends on it.

- **LoRA adapter.** Fine-tuning all 1.5 billion weights of the model for each obfuscation type
  would be expensive and would produce six full copies of the model. Instead each specialist is a
  *LoRA adapter*: a small patch of extra weights (here ~0.5 % the size of the model) that sits
  alongside the frozen base model and shifts its behaviour. Six specialists = one base model +
  six small patches. Mathematically each patch is a pair of low-rank matrices whose product is
  added to a base weight matrix; "rank 32" is the size of that low-rank bottleneck, and the six
  specialists here are all rank 32, trained with seed 17, using the checkpoint that scored best on
  validation.
- **Two ways to combine adapters.** You can keep all six patches and *pick one per input*
  (**routing**), or you can mathematically *average the six patches into a single patch*
  (**merging**). Routing needs a decision at inference time and keeps six patches in memory;
  merging produces one patch and needs no decision. Both are tested here.
- **Oracle prompting** is the cheap alternative to both: don't fine-tune at all, just *tell* the
  untuned model in the prompt which obfuscation was applied, and see if it can compensate on its
  own.

The RQ2 design registered a specific conditional in advance: if oracle prompting matches the
routed system, the finding becomes "models know *how* to handle obfuscation but not *when*" — which
is publishable either way, so the comparison is reported regardless of outcome.

### 5.1 What was actually built

**The routed system** (`router`). A separate small classifier looks at the incoming program and
predicts which obfuscation type it is; the matching specialist adapter is then applied to that
item. Concretely (`configs/router/router_v1.yaml`):

- **Features:** the *base* model's hidden state at layer 14 of 28 (mid-depth), mean-pooled over the
  non-special prompt tokens. The base model is frozen and used purely as a feature extractor.
- **Classifier:** a one-hidden-layer MLP (512 units, GELU, dropout 0.1) over those features,
  8 output classes — `L0, L1b, L1r, L2, S1, S2, S3, S4`. **`H1` is never a class**, by design; the
  router must never be trained to recognise the held-out transform.
- **Training:** lr 1e-3, batch 256, up to 50 epochs with early stopping (patience 5), 5,000 items
  per class, seed 17. Best epoch: 1.
- **At inference:** each eval item is routed independently (`results/router/*/route_map.json` is a
  literal item-id → adapter-path map), and the chosen adapter is served through vLLM's multi-LoRA
  path.

**The merged systems** (`merge_ties`, `merge_dare_ties`, `merge_dare_linear`). All three merge
**the same six ingredients** — the `L0`, `L1b`, `L1r`, `L2`, `S1` and `S2` specialists, rank 32,
seed 17, `best` checkpoint — into **one** adapter, with **uniform weights (1/6 each)** and
**density 0.5**, via PEFT 0.20.0's `LoraModel.add_weighted_adapter`
(`configs/merge/ties_v1.yaml`, driver in `src/obtune/merge_adapters.py`). They differ only in the
combination algorithm:

| arm | algorithm | what it does to the six patches |
|---|---|---|
| `merge_ties` | **TIES** | For each weight, keep only the largest-magnitude 50 % of the six proposed updates (`density: 0.5`), then resolve *sign conflicts*: if three adapters want a weight to go up and three want it to go down, take the side with the larger total magnitude (`majority_sign_method: "total"`) and discard the losers before averaging. The point is that naive averaging lets opposed updates cancel to nothing. |
| `merge_dare_ties` | **DARE + TIES** | First DARE: randomly *drop* 50 % of each adapter's updates and rescale the survivors by 1/0.5 so the expected update is unchanged; then apply the TIES sign-consensus step above. The randomness is what `seed: 17` fixes. |
| `merge_dare_linear` | **DARE + linear** | The same random drop-and-rescale, then a plain weighted average with **no** sign-consensus step. This is the ablation that isolates what TIES's conflict resolution contributes. |

Three implementation details that matter for reading the numbers:

1. **Merging happens in LoRA space, not in the base weights.** mergekit was tried and rejected: its
   LoRA path merges each adapter into the base model and re-extracts a LoRA by SVD, which changes
   the rank and injects reconstruction error *before* the merge algorithm runs (and it pins an
   incompatible `accelerate`). PEFT's method operates on the adapters directly.
2. **Each ingredient's own scaling is accounted for.** The specialists are r=32/α=64, i.e. scaling
   2.0; PEFT folds that in internally, and the merged adapter is written with `lora_alpha = r`
   (scaling 1.0) with the factor baked into the weights. This is the classic place where a merge
   silently halves every ingredient, and it is not happening here.
3. **`H1` cannot be an ingredient.** `_assert_no_h1` rejects any non-trainable condition by label
   *and* any adapter whose path touches the quarantine tree. A merge that included an `H1`-trained
   adapter would turn every downstream `H1` number into a train-on-test result with nothing in the
   trial table to reveal it.

**What was not run:** `configs/merge/ties_v1.yaml` declares a `density_sweep: [0.3, 0.5, 0.7]`,
but each merge manifest records exactly one merge at density 0.5. The sweep never happened, so
"merging underperforms" is a statement about density 0.5 only.

### 5.2 The results

Raw accuracy on Grid B — the 33-program Python common subset (30 in JavaScript). These are small
samples; see the caveat at the end of the section.

| system (Python) | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|
| `router` — six specialists + a classifier | .503 | .483 | .483 | .517 | .434 | .483 | — |
| `merge_dare_ties` — one merged patch | .503 | .407 | .434 | .510 | .441 | .428 | .374 |
| `merge_ties` — one merged patch | .407 | .310 | .359 | .400 | .386 | .310 | .293 |
| `merge_dare_linear` — one merged patch | .048 | .048 | .034 | .028 | .048 | .069 | .050 |

Python has no matched clean-code control on this grid (§8.2), so differences can only be quoted in
JavaScript, where the control was run. Points relative to the `L0`-only control; `*` = significant:

| system vs `L0` control (JS) | L0 | L1b | L1r | L2 | S1 | S2 |
|---|---|---|---|---|---|---|
| `router` | 0.0 | **+9.0\*** | −3.7 | +3.7 | +0.7 | **+11.9\*** |
| `merge_dare_ties` | 0.0 | −0.7 | −2.2 | +1.5 | −1.5 | **+8.2\*** |
| `merge_ties` | −7.5 | −6.7 | −9.0 | −6.0 | −5.2 | **+9.7\*** |
| `merge_dare_linear` | −26.9* | −29.1* | −34.3* | −36.6* | −32.1* | −26.1* |
| *for reference: the matching specialist alone, no router* | *0.0 (is the control)* | *+9.7\** | *−3.7* | *+3.0* | *+0.7* | *+11.9\** |

**5.3 The router is perfect, which makes it uninformative.** It classifies the obfuscation type
with **100.0 % accuracy** on every evaluated item in both languages (held-out validation accuracy
0.997 Python / 1.000 JavaScript), and it is *confident*: per-condition mean predictive entropy runs
from 4×10⁻⁷ to 0.007 nats against a maximum of 2.08, i.e. it puts ≥99.9 % probability on its chosen
class in every condition, and essentially 100 % on `L1b`, `L1r`, `S1` and `S2`. That is not
surprising on inspection — the conditions leave unmistakable surface fingerprints (`_st_e6f9`
dispatch variables for `S1`, `v_a3f2` hex names for `L1r`, single-letter `a`/`b`/`c` for `L2`), and
a mid-depth hidden state separates them trivially.

The consequence is that **"learned routing" and "oracle routing" are the same system here**, so
this arm cannot tell us anything about whether a router is learnable — it only tells us what
perfect dispatch is worth. And the answer is visible in the last row of the table: the routed
system's numbers are, cell for cell, the numbers of whichever specialist it dispatched to
(+9.0 vs +9.7 on `L1b`; +11.9 vs +11.9 on `S2`). **Routing recovers exactly what the specialists
already knew and adds nothing on top.** Since the specialists individually transfer nowhere (§3),
a perfect router inherits that limitation.

One planned RQ2 result is missing: the config declares `routing_entropy_on: [H1]` — the idea being
that `H1` forces the router into an out-of-distribution decision, and *how* it fails (confidently
wrong vs. uncertain) is itself informative. The routing report records `n_heldout: 0`. **`H1` was
never routed**, so that analysis has not been done.

**5.4 Merging is a lossy router at best.** `merge_dare_ties` — the best of the three — matches the
control almost everywhere and gains only on `S2` (+8.2), i.e. it retains roughly *one* of the six
specialists' skills. `merge_ties` (no DARE dropout) is 5–9 points *below* the control on every
identifier condition while still capturing the `S2` gain (+9.7). Neither approaches the routed
system, which is the expected direction — a single averaged patch has to serve all six conditions
at once, while the router gets to pick — but the size of the loss is the finding: collapsing six
adapters into one destroys most of what they individually knew. That the surviving skill is `S2`'s
in both merges is consistent with §3.5: the `S2` update appears to be the one that does not fight
the others.

**5.5 `merge_dare_linear` is a broken arm, not a result.** ~5 % accuracy with a **53.5 %
format-failure rate** in Python and 37.9 % in JavaScript — i.e. on half its inputs the model stops
emitting a parseable answer at all. (The other two merges sit at 1.8–3.2 %, in line with every
adapter in the project.) The dropped-and-rescaled updates without TIES's sign-consensus
step evidently produce an incoherent patch, but a −27 to −37 point collapse also looks like it
could be a bug rather than an algorithmic result. **Do not report this as evidence about DARE.**
It needs either a diagnosis (inspect the merged weight norms; try density 0.3/0.7) or removal.

**5.6 Oracle prompting is not competitive.** Telling the *untuned* model exactly which obfuscation
was applied (`oracle_prompt_1shot`, measured on Grid A at full scale, 317 programs) gives
.243 / .180 / .197 / .213 / .202 / .226 / .158 across `L0…H1`. That is about **+4 points over the
untuned base and ~20 points below every single adapter**, including the clean-code control. The
pre-registered conditional does not fire: at 1.5B the model does not "know how but not when" — it
does not know how. Given a perfect label it still cannot execute obfuscated code. Whether that
holds at 7B+ is untested and is the version of this question worth running, because the conditional
was written with larger models in mind.

**5.7 The `S2` decomposition (`S3`/`S4`) cannot yet answer §3.5.** `S3` (dead-code insertion only)
and `S4` (opaque predicates only) split `S2` into its two halves, precisely to ask which half
produces the `H1` transfer. Both exist as eval conditions and as trained specialists — but only on
the 33-program Grid B slice, and **never evaluated against `H1`**. On what was run, `S3`- and
`S4`-trained adapters land within ±3 points of the control on everything, and `S2`'s edge over them
is inside noise at this sample size. The experiment is built; it has not been run at a size that
can answer the question.

**Power caveat for this whole section.** Grid B is 33 programs (Python) / 30 (JavaScript) against
Grid A's 317 / 91. The confidence intervals are correspondingly wide, and the JavaScript deltas
above sit on 30 programs, where §3.7's seed-noise estimate was ±4 points. Read the router-vs-merge
*ordering* as solid and the individual cell values as indicative.

---

### 5.3 Does over-training the experts explain why merging fails?

*Added 12 August 2026. **The complete geometry thread — every bank, the cross-seed control, the
four probes of whether geometry predicts merged accuracy, and what to carry forward — is
consolidated in [§14](#14-task-vector-geometry--the-whole-thread-and-what-it-turned-out-to-measure).**
This section is the original over-training result and is kept for its accuracy sweep.* §5.2 shows every merge at or below the clean-code control. Horoi, Wolf,
Belilovsky & Dziugaite (arXiv:2506.14126v2) offer a mechanism: fine-tuning an expert to its
*individual* optimum is dominated, late in training, by memorisation of a few hard examples, which
produces **negative parameter interference** and degrades merging. Their recommendation is
task-dependent aggressive early stopping.

That describes this project's own procedure exactly. `eval_vllm.run_ckpt_select` picks `best` by
held-in validation accuracy — each expert's individual optimum — and every merge in §5.2 is built
from `best`. So the hypothesis is that our merges were handicapped by our own checkpoint-selection
objective.

The diagnostic is **sign conflict**: the fraction of weight coordinates where two experts disagree
in sign. TIES discards exactly those, so rising sign conflict means more of the update is thrown
away at merge time. It is computable from safetensors on CPU, with no GPU and no new training.

Each row is a property of the **task vectors** ΔW = (α/r)·B·A — the weight change each adapter
represents — measured across training epochs. `‖ΔW‖` is the mean Frobenius norm per module (how far
the expert moved). `cosine` is the mean pairwise angle between two experts' task vectors (1.0 =
identical direction, 0 = orthogonal). **Sign conflict** is the fraction of weight coordinates where
two experts disagree in sign — TIES deletes exactly those, so higher means more of the update is
discarded at merge time. `TIES keep rate` is the fraction of magnitude surviving that election.
Arrows are first epoch → last.

| | 8 experts × 3 epochs (the bank §5.2 merges) | 3 experts × 9 epochs (overtrain probe) |
|---|---|---|
| ‖ΔW‖ first → last | 0.299 → 0.371 | 0.286 → **0.602** |
| cosine(ΔWᵢ, ΔWⱼ) | 0.584 → 0.592 | 0.498 → **0.421** |
| **sign conflict** | 0.402 → **0.391** *(falls)* | 0.336 → **0.355** *(rises)* |
| TIES keep rate | .854 → .861 | .890 → .876 |
| verdict | `interference_grows: false` (Δ −0.011) | `interference_grows: true` (Δ +0.019) |

> **CAVEAT ADDED 15 AUGUST — every number in this table is SAME-SEED, and that changes what it
> measures.** Cosine and sign conflict between LoRA task vectors are dominated by **shared
> initialization**, not by learned content. Measured directly (`results/merge_geometry/l0seeds_*`,
> `scripts/merge/20_geometry_report.py --seeds`):
>
> | bank | mean cosine | sign conflict |
> |---|---|---|
> | `L0` at seeds {17, 42, 101} — **byte-identical training data** | **0.053** | **0.487** |
> | 8 specialists at seed 17 — **completely different transforms** | 0.592 | 0.391 |
>
> LoRA initializes `A` randomly and `B` at zero, so each seed selects a different rank-32
> subspace; same-seed adapters share it and drift together, different-seed adapters do not. Three
> adapters trained on the same data are therefore *near-orthogonal* while eight trained on
> different transforms are 0.59-aligned. **This table measures drift within one shared subspace,
> not how different the experts' knowledge is** — which is how the Horoi framing above reads it.
> The observations stand; the interpretation does not.
>
> **And sign conflict demonstrably does not bound merged accuracy.** The L0-merge control (§12.10)
> is built from exactly that near-orthogonal bank — cosine 0.05, sign conflict 0.487, TIES keep
> 0.765, the worst geometry in the project — and it merges *fine*: `l0merge_dare_ties` = .339 on
> `H1`, identical to `tuned_L0`, and within ~3 pts of the six-specialist merge on every trainable
> condition. A merge at maximal sign conflict lost nothing. That is a stronger statement than
> "the mechanism reproduces but the consequence does not": the diagnostic's premise fails.
> The controlled test — same six conditions, same recipe, only the seed assignment altered so
> mean cosine drops 0.563 → 0.246 — is `scripts/merge/24_crossseed_control.py`, built and awaiting
> one eval pass. Detail: [`../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md`](../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md).

**The mechanism is real but does not reach our bank.** At 3 epochs sign conflict is still *falling*
— our experts are **under**-trained relative to where interference appears. Extend to 9 epochs and
it reverses: the task vector doubles in norm, the experts rotate apart, and sign conflict climbs to
a plateau at about epoch 6. Interference is also localised: `down_proj` moves +0.0359 from epoch 1
to 9, five times `gate_proj`'s +0.0072.

**But mechanism is not consequence — and the accuracy goes the wrong way for the paper.**
Merged accuracy across the sweep, Grid B (40 testset programs), on the three conditions the
overtrain bank covers. Higher is better; the first two rows are the status quo (§5.2's merges,
built from the 8-expert bank at `best`).

| system | L1b | S1 | S2 |
|---|---|---|---|
| `merge_ties` *(status quo)* | .318 | .386 | .324 |
| `merge_dare_ties` *(status quo, best merge in §5.2)* | .398 | .441 | .443 |
| `overtrain_sweep_ties` @ epoch 1 | .352 | .400 | .392 |
| `overtrain_sweep_ties` @ epoch 3 | .364 | .414 | .420 |
| `overtrain_sweep_ties` @ epoch 6 | .364 | .393 | .409 |
| `overtrain_sweep_ties` @ epoch 9 | .364 | .428 | .409 |
| `overtrain_sweep_dare_ties` @ epoch 1 | .375 | .441 | .460 |
| `overtrain_sweep_dare_ties` @ epoch 3 | .409 | .476 | .460 |
| `overtrain_sweep_dare_ties` @ epoch 6 | .426 | .441 | **.494** |
| `overtrain_sweep_dare_ties` @ epoch 9 | **.432** | .434 | **.494** |
| **epoch 9 − epoch 1** (`dare_ties`) | **+5.7** | −0.7 | **+3.4** |
| **epoch 9 − epoch 1** (`ties`) | +1.2 | +2.8 | +1.7 |

**Training the experts longer made the merge better, not worse**, on five of six method×condition
pairs. Horoi et al. predict the opposite. So the geometry above is real — the task vectors do
diverge and sign conflict does rise — but at LoRA r=32 with three experts that interference does
not cost merged accuracy; if anything the extra training buys more than the interference costs.

**Two caveats that stop this being a refutation.** The sweep merges **three** experts while §5.2's
merges combine six to eight, so the two status-quo rows are not a controlled comparison — only the
within-sweep epoch deltas (the last two rows) hold expert count fixed. And **there is no Grid B
base or `L0` control for these conditions in Python** (§8.2), so no absolute "points above base"
can be quoted here; that missing control is precisely what §10 item 2 exists to fix.

A corrected statement, then: Horoi's *mechanism* reproduces in the overtrained regime, its
*consequence* does not, and the direction of the accuracy effect is opposite to the paper's. Sign conflict is
pairwise — 3 experts give 3 pairs, 8 give 28 — so the 8-expert 9-epoch bank is being completed
before the merge-optimal search runs.

**A confound this uncovered, affecting every merge in §5.2.** `ckpt_select` chose *different*
epochs per condition — `L1r`/`S3` at epoch 1, `L0`/`L1b` at 2, `L2`/`S2`/`S1`/`S4` at 3. Every
merge in this report therefore combines task vectors of unequal training. A uniform-epoch sweep is
queued to remove it, and the heterogeneity has to be reported either way.

### 5.4 RouterLoRA — the arm §5.2's saturated router implies

*Added 12 August 2026. Built, not yet run.* §5.2's router classifies the obfuscation type with
100% accuracy and mean routing entropy ~1e-6 nats. That is not a success, it is a ceiling: picking
the right specialist is solved, and it buys only the specialists' own ~3.5 pt gains. The remaining
headroom is entirely where **no single expert is correct**.

Stacked conditions manufacture exactly that. A composite variant (`C_L1r_S1` = rename then flatten)
contains *two* mechanisms, so a hard router must be wrong and a mixture can be right. Six composites
were generated and gate-validated: Python **1656/2231 (74%)** and JavaScript **665/674 (99%)**
common subset; `make check` clean at 64 files / 184,803 rows with no H1 labels or markers.

The mixture is in **activation space** — `h = Wx + Σ aₑ(x)·(α/r)·Bₑ Aₑ x` — which is exact, needs
no per-item merge rebuild, and does not grow rank. Only a 2.77 M-parameter gate trains, against a
frozen 295 M expert bank. The ladder is ordered so each term is interpretable: `mole_uniform`
(weights pinned at 1/8) is the primary fixed-mixture contrast because it differs from the learned
gate in exactly one way, and **`mole_random`** — the same module with its gate frozen at random
init — decides what the headline may say. If `mole_router ≈ mole_random`, the gain is rank-256
residency, not routing.

**What the ladder has to beat.** No composite condition has been evaluated by *any* system yet, so
the bar on the conditions that carry the headline is currently unmeasured — that is the first thing
the run produces. For the two single-transform conditions also in the ladder, the existing
references are:

| reference | L1r | S1 | the six composites |
|---|---|---|---|
| untuned `base` (Grid A) | .164 | .187 | **not measured** |
| `L0`-only control (Grid A) | .353 | .379 | **not measured** |
| best single specialist (Grid A) | .383 | .414 | **not measured** |
| `merge_dare_ties` (Grid B — *different program set*) | .435 | .441 | **not measured** |

Read the first three rows as a set (same grid, same programs); the fourth is on Grid B and must not
be differenced against them (§2). The point of the table is the last column: **every composite cell
is empty**, so `mole_router` will be the first system ever scored there, and `mole_uniform` /
`mole_random` are what make that number mean something rather than merely exist.

Two design defects were caught before any GPU time: the gate would have been **trained on a
different task from the one it is scored on** (code rewriting vs output prediction — it would have
converged and produced a plausible meaningless number), and merge-optimal candidate names did not
encode the other experts' epochs, so a restart mid-search would have silently scored the wrong
merge.

---

## 6. What the base model's weakness does to every number

The untuned base has a **17.3 % format-failure rate** in Python (13.7 % JS), and the oracle-prompt
arm 15.3 %. Adapters run at 2–6 %. So a large part of the base→tuned gap is the model learning the
answer *format*, not the task — which is exactly why the `L0` control exists and why every headline
number in this report is control-relative. Any base-relative number anywhere in the project
(including the pilot's original +27.3 on `H1`) is inflated by this and should not be quoted.

---

## 7. Side thread — CFT / bidirectionality (complete)

This thread answers a *different* question from RQ1–RQ3, on the same corpus and infrastructure. It
is the most finished work in the project, and it is a clean refutation of a published method. Full
detail: [`REPORT_bidirectional_2026-08-09.md`](REPORT_bidirectional_2026-08-09.md).

### 7.0 The question and why it exists

RQ1–RQ3 evaluate on code that **stays obfuscated** — the model reads obfuscated code and predicts
what it computes. This thread instead asks about **direction**:

- **Forward** = obfuscate. Given clean code, produce the obfuscated version.
- **Reverse** = deobfuscate. Given obfuscated code, recover readable original-like source.

Nikiema et al. (2025) asked: when a model learns a transformation, does it *understand* it or has
it memorised a one-way input→output mapping? Their test is that genuine understanding should be
direction-agnostic — you should be able to run the transform backwards without ever having been
trained backwards. On Java they report (a) models fine-tuned to obfuscate score **0 %** at
deobfuscating, which they name *cognitive specialization*, and (b) their fix, **Contrastive
Fine-Tuning (CFT)**, recovers **39–52 %** reverse performance with no reverse training data. CFT
keeps the forward examples and adds a second kind of example: a YES/NO judgement about whether two
programs are semantically equivalent.

This thread exists for two reasons. It is the nearest prior work to the pilot's memorization
finding (`papers/RELATED_WORK.md` §2.1), and CFT is named in the design doc §7 as a candidate RQ1
intervention — so before adopting it, check that it reproduces.

**The gap the thread targets:** the paper **names** the bidirectional baseline and reports **no result** for it. §5.0.2 declares the comparison — *"CFT effectiveness is assessed through comparison against Standard Fine-Tuning (SFT) ... and Bidirectional Fine-Tuning (BFT) using forward generation plus reverse deobfuscation tasks"* — and the string "BFT" occurs exactly once in the paper: Figure 4 carries only SFT and CFT columns, and no table, figure or sentence reports a BFT number. BFT *is* the `flip` arm. A declared-but-unreported baseline is a sharper gap than an unnoticed one, and "they never ran it" would be factually wrong. Reverse training data is **free** — every
`(original, obfuscated)` pair is also an `(obfuscated, original)` pair, just swap which side is the
question. If training on both directions works as well as CFT, the contrastive machinery adds
nothing.

**Scope limit that cannot be worked around:** the paper's third transformation is string
encryption, which maps onto this project's quarantined `H1`. So the replication covers renaming
(`L1b`/`L1r`/`L2`) and dead code (`S2`), and adds control-flow flattening (`S1`), which the paper
lacks. The paper's hardest arm is the one that cannot be run here.

### 7.1 The seven arms

All are the same base model plus a rank-32 LoRA adapter, 3 epochs, lr 1e-4, effective batch 64,
seed 17. **They differ only in which examples they see.**

| arm | trained on | why it exists |
|---|---|---|
| `base` | nothing — the untouched model | the floor everything is measured against; the paper reports no such baseline |
| `sft` | forward only (obfuscate) | the paper's "standard fine-tuning" — the arm said to score 0 % |
| `cft` | forward + equivalence judgements | the paper's proposed fix |
| `rev` | reverse only (deobfuscate) | the ceiling — how good can reverse get if trained directly? |
| **`flip`** | forward **and** reverse | **the missing baseline** — the free swap |
| **`mix50`** | half the programs forward, half reverse, never both | **the decisive arm**, see below |
| `flipsym` | as `flip`, but both directions share one instruction wording | controls for the model merely switching behaviour on a prompt cue |

`mix50` is what makes the comparison airtight. An obvious objection to `flip` is that it simply saw
more data; `mix50` removes it — each program contributes *either* its forward example *or* its
reverse example (verified: no program appears in both), so it trains on exactly as many examples as
`sft`, for exactly as many optimiser steps, while learning strictly *less*.

The measured cost of each arm, from `results/srh/budget_qwen7b_python.json` (7B, Python), relative
to forward-only SFT:

| arm | instances | **supervised tokens** | sequence tokens (≈compute) | steps |
|---|---|---|---|---|
| `sft` (forward-only baseline) | 1.00× | 1.00× | 1.00× | 1.00× |
| `mix50` | **1.00×** | **0.71×** | **1.05×** | **1.00×** |
| `flip` | 2.00× | 1.43× | 2.09× | 2.00× |
| `cft` | 2.52× | **1.02×** | **2.65×** | 2.52× |

*Supervised tokens* = tokens the model actually receives a learning signal on. **CFT costs 2.65×
the compute to add 1.02× the signal.** Its equivalence-judgement examples contain two whole programs
in the question but require a one-word answer, so they are expensive to process and teach almost
nothing per example. Measured directly: CFT's three-term loss is **97.7 % L_gen**, 1.13 % L_pos,
1.13 % L_neg by token share — equal *instance* counts across the three pools (the paper's balancing)
do not mean equal loss weight, and the "three-term loss" is close to gen-only plus a rounding error.

### 7.2 Why measuring this is hard

The natural measure — does the produced program *run* and return the original's outputs (`exec`) —
is broken. **A model that copies the obfuscated input straight back out passes `exec` perfectly**,
because the obfuscated program is semantically correct. It deobfuscated nothing. This is not
hypothetical: the untouched `base` scores 83.3 % on `exec` while echoing its input 47.7 % of the
time on the reverse task.

Four measures are therefore reported:

| measure | definition |
|---|---|
| `exec` | the produced program runs and reproduces the original's outputs — **gameable by echoing** |
| `paper` | the source paper's own reverse-success criterion: the answer must stop resembling the obfuscated input (CodeBLEU `S(deobf, obf) < 0.4`) **and** recover readability. One requirement was added that the paper leaves implicit — the answer must be *parseable code*, without which an empty reply satisfies the first condition (in a dry run the literal placeholder `<stub:a1b2c3>` scored 17–24 %) |
| **`strict`** | **`exec` AND `paper` — the headline.** Must both compute correctly and have genuinely undone the transform. The only measure that cannot be gamed by echoing |
| identity rate | how often the output is a verbatim copy of the input — the diagnostic that explains the rest |

CodeBLEU is the published implementation (`codebleu==0.7.0`, vendored). Readability is a *labelled
substitute* for the paper's Java-only instrument, so absolute values are not comparable across the
two papers — only comparisons within this thread are. All figures below are 300 held-out programs,
greedy decoding, 95 % CIs from a cluster bootstrap by program.

### 7.3 Results at 1.5B

Reverse direction, all five transformations pooled, `simple` instruction
(`results/2026-08-09_cft-bidirectional/qwen25c-1.5b/python/e1_qwen1.5b/summary.json`):

| system | **`strict`** | `paper` | `exec` alone | echoes input | id-recall |
|---|---|---|---|---|---|
| `base` — untouched | 2.9 % | 9.6 % | 83.3 % | 47.7 % | 0.591 |
| `sft` — forward only | **0.4 %** | 7.1 % | 74.0 % | 1.7 % | 0.415 |
| `cft` — contrastive | **0.3 %** | 8.7 % | 74.3 % | 1.1 % | 0.393 |
| `rev` — reverse only | 31.5 % | 36.1 % | 88.8 % | 0.0 % | 0.718 |
| **`flip`** — the free swap | **31.5 %** | 35.7 % | 90.5 % | 0.0 % | 0.722 |
| **`mix50`** — same cost as `sft` | **30.6 %** | 35.5 % | 89.0 % | 0.0 % | 0.719 |
| `flipsym` — shared instruction | 30.5 % | 34.7 % | 91.5 % | 0.0 % | 0.723 |

Four conclusions, with intervals from the original report:

| comparison | difference | verdict |
|---|---|---|
| `cft` − `sft` | −0.1 [−0.5, +0.3] | **no effect** — the contrastive objective adds nothing |
| `flip` − `cft` | **+31.1** [+29.3, +32.8] | **the free swap beats the published method outright** |
| `mix50` − `sft` | **+30.3** [+28.5, +31.9] | **the entire effect, at no extra cost on any axis** |
| `flip` − `mix50` | +0.7 [−0.1, +1.7] | doubling the data adds nothing detectable |
| `sft` − `base` | **−2.3** [−3.1, −1.4] | **forward-only training actively damages the reverse direction** |
| `flipsym` − `flip` | −0.6 [−1.4, +0.1] | the effect is **not** an instruction-wording artifact |

Cognitive specialization reproduces — and is worse than the paper could show, since both fine-tuned
forward arms land *below* the untouched model, which the paper could not observe having run no
baseline. Bidirectionality is not paid for in forward performance either: forward execution
accuracy is `sft` 90.3 %, `flip` 91.9 %, `mix50` 89.9 %, `cft` 92.3 %, all above `base` (86.7 %).

### 7.4 The per-transformation result inverts the paper

`strict`, broken out by transformation (1.5B):

| system | `L1b` | `L1r` | `L2` | **`S1`** | **`S2`** |
|---|---|---|---|---|---|
| `base` | 1.3 % | 0.7 % | 4.3 % | 7.7 % | 0.3 % |
| `sft` | 0.0 % | 1.3 % | 0.0 % | 0.3 % | 0.3 % |
| `cft` | 0.3 % | 0.0 % | 0.0 % | 1.0 % | 0.0 % |
| `rev` | 0.7 % | 1.0 % | 1.7 % | **74.7 %** | **79.3 %** |
| `flip` | 0.7 % | 0.3 % | 3.0 % | **74.3 %** | **79.0 %** |
| `mix50` | 0.3 % | 1.3 % | 2.0 % | **70.3 %** | **79.0 %** |
| `flipsym` | 0.3 % | 0.3 % | 1.3 % | **71.7 %** | **79.0 %** |

**Everything happens on the structural transformations; renaming stays at the floor.** The paper
reports the opposite profile — its method working on renaming and failing on dead code.

The explanation was predicted before the run. **Renaming destroys information and is therefore not
invertible**: once `totalPrice` becomes `a3x9` the original name is gone and no amount of training
can conjure it back. **Structural transforms preserve information**: a flattened dispatch loop
still contains every branch of the original control flow, and dead code is still identifiable as
dead. Models learn to invert exactly the transformations whose information survives them. The
paper's apparent success on renaming follows from a criterion that rewards *plausible, readable*
names rather than the *original* ones.

### 7.5 It holds at the paper's own model (7B)

Scale was the single biggest threat to §7.3 — the paper used 7–15 B and explicitly reports its
method working only at the larger sizes. So the comparison was re-run on **Qwen2.5-Coder-7B**, the
paper's own "QwenCoder" row, reported there at 39.00 %.

Reverse success under **the paper's own criterion**, 300 programs × 5 transformations, all four
prompting strategies (`bidir_qwen7b`, 22,500 generations):

| system | `simple` | `few_shot` | `cot` | `augmented` |
|---|---|---|---|---|
| `base` — untouched | 23.6 % | 32.7 % | 34.7 % | **38.7 %** |
| `sft` — forward only | 0.3 % | 6.8 % | 11.0 % | 12.5 % |
| `cft` — contrastive | 0.2 % | 1.9 % | 3.0 % | 2.6 % |

Pooled over strategies, **`cft` − `sft` = −5.7 points [−6.4, −5.0]**: at the scale where the method
is supposed to work, it is significantly *worse* than the training it is meant to repair. Three
things follow.

1. **The paper's "0 %" reproduces exactly, and only under its weakest prompt.** `sft` with `simple`
   scores 0.3 %; the same adapter under `augmented` scores 12.5 %. A result reported as a property
   of the model is substantially a property of the prompt used to elicit it.
2. **CFT does not recover it** — never above 3.0 % under any strategy, against a reported 39.00 %.
3. **The untouched base model reaches the paper's headline number.** `base` scores 38.7 % under
   `augmented`, statistically indistinguishable from the 39.00 % the paper attributes to its
   method. Without a baseline, a number that is simply *what the model could already do* is
   indistinguishable from a number the method produced.

And the positive half holds at 7B too (`e1_qwen7b`, all systems under the paper's `simple`
instruction):

| system | `strict` | `paper` | `exec` alone | echoes input |
|---|---|---|---|---|
| `base` — untouched | 13.1 % | 23.5 % | 80.7 % | 7.1 % |
| `sft` — forward only | 0.0 % | 0.4 % | 89.5 % | 18.1 % |
| `cft` — contrastive | 0.1 % | 0.3 % | 91.2 % | 28.8 % |
| `rev` — reverse only | 32.9 % | 35.1 % | 93.7 % | **0.0 %** |
| **`flip`** — the free swap | **33.6 %** | **35.6 %** | 93.8 % | **0.0 %** |

The echo column is the mechanism in one number. `cft` is the **best** system by execution
equivalence (91.2 %) while being the worst by every measure that requires the output to actually be
deobfuscated — it achieves that by reproducing its input 28.8 % of the time. This is the same
failure the paper itself describes for SFT ("outputs nearly identical to the obfuscated input");
what is new is that CFT exhibits it *more* strongly than SFT does.

**So at 7B the conclusion is not merely negative: CFT is dominated on every axis a practitioner pays
for — less capability, more compute, more instances, more steps — by swapping the pairs, which is
free.**

### 7.6 What is left open in this thread

- **Single seed.** Every arm is seed 17. The differences carrying the conclusions are 30+ points and
  the nulls are tight (±0.5), so seed noise is very unlikely to overturn them, but a second seed is
  queued and should run before publication.
- **~~Two budgeted arms were never trained.~~ RESOLVED 2026-08-10.** `fwd2x` (forward-only at
  6 epochs — the *compute*-matched control) and `cftflip` (CFT plus the reverse direction) are both
  trained and now evaluated, together with `mix50` at 7B, which had also been trained and never
  scored. Strict reverse success: at 1.5B `fwd2x` 0.6 % and `cftflip` 31.1 % (against `flip`
  31.4 %); at 7B `fwd2x` 0.1 % and `mix50` 32.8 % (against `sft` 0.0 %). So doubling forward-only
  compute buys +0.3 pp [−0.2, +0.8] at 1.5B and +0.1 pp [+0.0, +0.2] at 7B, and adding the
  contrastive objective *on top of* bidirectional data buys −0.3 pp [−1.2, +0.5]. With `cftflip`
  in hand the four arms form a 2×2 (objective × data direction) whose objective main effect is
  **−0.2 pp [−0.7, +0.3]**. Runs: `results/2026-08-10_cft-bidirectional/*/python/e2_*`.
- **String encryption is untestable here** (§7.0) — it is `H1`, and `H1` is quarantined.
- **Readability is a substitute instrument**, so absolute `paper`-criterion values are not
  comparable to the source paper's; only within-thread comparisons are.
- **Catastrophic forgetting is unmeasured for these adapters** — the HumanEval+ harness returns
  pass@1 = 0.0 for both `cft` and `flip` (§8.3). On the L0 output-prediction check they are fine
  (`base` .217, `cft` .201, `flip` .235).
- **A data-loss incident, resolved.** The 7B evaluation once wrote to a path that carried the date
  and language but not the model, destroying the 1.5B per-trial file (21,000 rows). It was re-run
  and reproduces §7.3 within ≤0.2 points (decoding is greedy, so the residual is vLLM batch
  numerics). `scripts/preflight.py` now fails any two eval configs that resolve to the same
  directory.

---

### 7.7 Approximate unlearning — and why its control matters more than its result

*Added 12 August 2026.* §7 establishes behaviourally that `flip` reaches 33.5% reverse where `cft`
reaches 0.1%. Behaviour cannot distinguish **one shared mechanism** from **two disjoint one-way
circuits** that happen to coexist. Unlearning can: delete the forward direction from `flip` and see
what happens to reverse.

*Exact* unlearning cannot test this — exact removal of forward from FLIP *is* the `rev` arm, whose
reverse performance is guaranteed to survive. So the signature relocates to **approximate unlearning
over-removing relative to exact**, using `U(λ) = FLIP − λ·SFT` via `taskvec.combine` with
`combination_type="cat"` (exact weight-space arithmetic; `use_dora`/`use_rslora` both false).

At 1.5B the treatment looked like a strong positive: reverse fell **.314 → .126** at the λ=0.75
operating point where forward reaches base, an 18.8 pt over-removal, with HumanEval+ *higher* than
FLIP's own — so not generic damage. At 7B the same sweep showed surgical removal, reverse surviving
(.329 → .305), which is the disjoint reading.

**The control refutes the 1.5B reading.** `rev − λ·sft` applies the same operator to an arm that
never saw forward data, so its reverse has nothing to lose collaterally:

`λ` is how much of the forward task vector is subtracted (λ=0 is the untouched arm). `fwd` is
`forward_success_exec` — can the model still do the forward task, which is what is *meant* to be
removed. `rev` is `reverse_success_strict` — the reverse capability, which is *not* being targeted
and should survive if the two directions are separable. The operating point is the λ where `fwd`
first reaches the untuned base level (~.87 here): that is where forward has been removed and the
question about reverse becomes meaningful. Both columns are fractions, 0–1.

| λ | `rev−λ·sft` fwd | `rev−λ·sft` **rev** | `mix50−λ·sft` fwd | `mix50−λ·sft` **rev** |
|---|---|---|---|---|
| *untuned base* | *.866* | *.027* | *.871* | *.027* |
| *`sft` (forward-only)* | *.905* | *.005* | *.907* | *.003* |
| 0 | .887 | **.313** | .901 | **.306** |
| 0.25 | .876 | .297 | .885 | .305 |
| 0.5 | .872 | .243 | .800 | .285 |
| **0.75** | .784 | **.164** | .807 | **.177** |
| 1.0 | .118 | .107 | .794 | .119 |
| 1.25 | .003 | .015 | .013 | .021 |

The two italic rows are the reference points: the untuned model gets **.027** on reverse, and
forward-only `sft` gets **.005** — reverse is essentially absent without reverse data, which is §7's
whole finding. Every λ row should be read against those. At λ=0 the arms sit ~29 points above base
on reverse; by λ=0.75 they have given back more than half of it.

`rev−λ·sft` falls **.313 → .164** — the same collapse as FLIP's **.314 → .126**, in an arm with no
forward direction to remove. The most likely reading is that the negation operator degrades whatever
adapter it is applied to. **The 1.5B entanglement result is not supported**, pending a formal
matched-λ, matched-norm comparison. The 7B result is unaffected; it was already the disjoint reading.

**What survives regardless.** The design's real asset is that forget and retain sets here are
*content-identical* — the same programs, the same variants, differing only in which side is the
question. Every "the forget set was harder / rarer / differently distributed" confound is eliminated
by construction, which no capability-unlearning benchmark can currently claim. That is worth
reporting even though the effect it was built to measure did not survive its own control.

---

### 7.8 A held-out benchmark overturns two of the thread's central claims

*Added 27 August 2026. Lab notes `log/cft-replication/2026-08-{17,18}_*.md`; the manuscript is
`paper_bidirectional/`, now at draft v4.*

Every general-ability number in §7 came from **HumanEval+**, and HumanEval is one of the corpus's
three sources. **H-M1: is the selectivity claim an artifact of benchmark contamination?** Verified
rather than assumed — `data/manifests/corpus_python.json` records `tiers: ['tier1']`; MBPP is
declared only under `tier2` and was never built; the provenance histogram over the 2,231 training
rows is **apps 1,584 / cruxeval 543 / humaneval 104 / mbpp 0**. So MBPP+ is genuinely held out.
Seven 7B cells, 399 tasks, adapter paths byte-identical to those the published HumanEval+ cells
used. Paired bootstrap, 10,000 resamples, seed 17; sign confirmed by exact McNemar. Base MBPP+
`plus` = .714.

| arm | MBPP+ Δ vs base | 95 % CI | McNemar p | HumanEval+ Δ |
|---|---|---|---|---|
| `sft` | **−5.3** | [−9.0, −1.5] | 8.6e−3 | **+1.2** |
| `fwd2x` | −2.5 | [−6.3, +1.3] | 0.23 | +0.0 |
| `cft` | −5.0 | [−8.8, −1.3] | 1.2e−2 | −0.6 |
| `rev` | −6.0 | [−10.0, −2.0] | 5.6e−3 | −0.6 |
| `flip` | −6.3 | [−10.3, −2.3] | 3.5e−3 | −6.1 |
| `mix50` | −5.5 | [−9.3, −1.8] | 5.4e−3 | −7.3 |

**Two claims died.**

1. **"A general coding benchmark does not fall at all" was false on held-out data.** `sft` scores
   **+1.2 above** base on the benchmark 74 of whose problems it trained on, and **−5.3 below** it on
   the one it never saw. The surviving statement is the *disproportion*: reverse goes to **zero**, a
   total loss, while general ability gives up about a fourteenth of its value.
2. **The one-direction / both-directions grouping does not replicate.** both − one = **−1.2 pp**
   [−3.8, +1.5], where HumanEval+ gave −6 to −7. Every arm-vs-arm contrast is null (`mix50`−`sft`
   −0.3 [−4.0, +3.5], p = 1.00). Replaced by the simpler true statement: **fine-tuning costs ~5 pts
   whatever the direction mix** (pooled −5.1 [−8.0, −2.1]). **This makes the prescription stronger**
   — bidirectional data costs no more than the forward-only training a practitioner would run
   anyway, so the flip is free against the baseline that matters.

A correction fell out of the same check: the draft said "104 of the 164 HumanEval+ problems", but
104 is the **corpus** count and the arms train on the train split — `data/splits/python.json` puts
those 104 at **74 train / 25 test / 5 val**. **74/164** is both defensible and the stronger contrast
against MBPP+'s 0/399.

**Two further controls closed the thread's remaining openings.** The **paper-literal `clean_mutant`
negatives**, promised in `CFT_REPLICATION.md` and never run, reach **0.5 %** strict reverse against
`cft` 0.2 % and `sft` 0.2 % (+0.3 pp [−0.1, +0.7]) and sit **2.3 pp below the untouched model**
[−3.3, −1.4] — on a setup *more* favourable to the objective (pools 6,058 vs 5,611) at an
essentially identical training loss (0.3537 vs 0.3544). **H-N1 refuted: our deviation from the
paper's negative-sampling scheme is not what produced the contrastive null.** And the **readability
substitution** — our proxy in place of Scalabrino et al.'s model in the reverse criterion — moves no
arm by more than 0.6 pp and the `mix50`−`sft` contrast by 0.2 pp; execution plus the similarity
bound do the deciding, so the substitution cannot account for any conclusion.

**Data quality across these runs:** 0 scorer errors, 0.0 format-fail, 0 entry-point mismatches in
all 7 MBPP+ cells; 69–84 of 399 tasks discordant vs base in every tuned cell, so no adapter silently
failed to load (§4.2's adapter-applied check).

---

## 8. Data-quality issues that must be resolved before any of this is written up

Ordered by how much damage they do if ignored.

**8.1 ~~The committed analysis artifacts are stale and wrong.~~ RESOLVED 2026-08-11.**
`results/analysis/transfer_*.json` (regenerated 2026-08-10 05:28) reports `n_programs: 23`,
`n_train_conditions: 2`, and `mean_tr_offdiagonal: 0.926` — a number that would read as "transfer
is nearly perfect". It is an artifact of `trial_table.compute_is_core`, which intersects over
*every* eval condition present for a (phase, model, language) group. Once the 40-program `S3`/`S4`
cells landed, that intersection collapsed to 23 programs and silently redefined what "core" means.
`results/trials.parquet` has the same problem and additionally covers only 84 of 453 cells (Python
only). **Fix `compute_is_core` to intersect within an experiment/grid, then regenerate.** Until
then, treat `results/analysis/transfer_*.json`, `accuracy_*.parquet` and `trials.parquet` as void.

*Resolved 2026-08-11.* `core_subset`/`compute_is_core` now group by `experiment_id`, restoring
n_programs 23 → 340, and the artifacts were regenerated over all 597 cells. **This retracted a
claim**: a 2026-08-11 report stated "transfer into L1b genuinely fails". It does not — at the
correct n every L1b cell is significant (L0→L1b +15.2 [12.1, 18.5]). §3's tables here were always
computed per-grid and were never affected.

**8.2 Grid B has no control in Python.** `tuned_L0` was evaluated on the corpus grid instead of the
test-set grid for `L0…S2`, so the router and merge arms have no matched clean-code control on their
own items (JavaScript does). Missing: 6 Python cells (`tuned_L0__{L0,L1b,L1r,L2,S1,S2}` on the test
set) and, for the same reason, 6 `base` cells. Cheap to run — ~10 GPU-minutes — and it is what makes
§5 quantitative in Python.

**8.3 ~~The catastrophic-forgetting check is not working.~~ RESOLVED 2026-08-10.** The harness
reported **pass@1 = 0.0** for every adapter. Root cause: `problems[tid]["expected_output"]` raised
`KeyError` for all 164 tasks (expected outputs are computed by `get_groundtruth`, not stored on the
problem dict) and a bare `except: continue` swallowed every one. `forgetting.py` now calls
`get_groundtruth` and raises rather than reporting a rate when >10 % of tasks error — a gate that
cannot score is not a model result.

Re-run for all seven CFT-thread arms at 1.5B and for `base`/`sft`/`flip` at 7B. `plus` split:

| arm | 1.5B | 7B |
|---|---|---|
| `base` | .646 | .805 |
| `sft` | **.329** | **.817** |
| `cft` | .366 | queued |
| `mix50` | .470 | queued |
| `flip` | .512 | .744 |
| `flipsym` | .543 | — |
| `rev` | .585 | — |

**The two scales disagree, and the disagreement is a finding.** At 1.5B forward-only SFT loses
31.7 points of HumanEval+ — general damage. At 7B it loses nothing (it is 1.2 points *above* base)
while its reverse capability goes 12.9 % → 0.0 %, i.e. the damage is purely directional at the
tier the headline claims live at. No capability-cost claim should be generalized from the 1.5B
tier. Detail: [`../log/cft-replication/2026-08-10_factorial-and-objective-verdict.md`](../log/cft-replication/2026-08-10_factorial-and-objective-verdict.md).

**8.4 The `H1` read budget is spent, and was spent incrementally.** `ACCESS_LOG.md` records 3
`pilot_eval` and **88** `final_eval` read events across 2026-08-07 → 08-09. Per-cell logging is fine
bookkeeping, but the reads were spread over at least four sittings while arms were still being
chosen, which is materially different from "one frozen final pass". Nothing here is provably
contaminated — no `H1` data entered training, and the four enforcement layers held — but the
*epistemic* guarantee is weaker than the protocol claims. Any new `H1` evaluation from here is a
third pass and should be declared as such. A pre-registered `H2` transform is the clean way to
confirm §3.5.

**8.5 `merge_dare_linear` is broken** (§5.3) — diagnose or drop, but do not average it into anything.

**8.6 Coverage is uneven by construction and matters here.** `S1` covers 74 % of programs and `H1`
73 % (literal-density bound, deliberately). All headline numbers use the all-conditions common
subset, which is why n = 317 of 557 Python and 91 of 168 JavaScript. Per-condition full-set numbers
are secondary and are not in this report.

---

**8.7 A scoring bug failed six runs and corrupted two reported fields. RESOLVED 2026-08-12.**
`cft/evaluate.score_trials` builds a `prepared` list in a pre-pass (so CodeBLEU can be batched) and
walks it in a second loop. The row construction read `"output_raw": raw`, but `raw` was **not** in
the tuple that loop unpacks — so it resolved to the enclosing scope and held the *last* generation
of the pre-pass. Every row stored the same string.

`assert_adapters_effective` compares `output_raw` between systems, so it compared a constant against
itself and reported **every** system as identical to base. Six runs were failed by the comparison,
not by the model; the adapters were never at fault (verified on GPU that vLLM applies per-prompt
LoRA correctly, including the mixed `[None, lora]` list this code passes). Introduced by the
CodeBLEU parallelisation on 2026-08-11, which is what split that loop.

| corrupted | unaffected |
|---|---|
| `output_raw` — one constant per run | `exec_pass_rate`, `forward_success_exec`, `reverse_success_*` |
| `identity_output` (derived from it) | CodeBLEU (`codebleu_target` / `_other`) |
| `assert_adapters_effective` verdicts | readability, identifier recall |

The metric columns are computed from `pred`, which was always correct. **Every table in this
document predates the refactor and is unaffected**, including the echo/identity rates in §7.3–§7.5.
Any identity rate from a 2026-08-11-or-later `cft/evaluate` run should be discarded. Fixed, pinned
by a regression test, and the seven falsely-failed jobs were requeued.

**8.8 Two fields in `results/2026-08-12_cft-bidirectional/` predate the §8.7 fix.** The runs written
between 2026-08-11 and 2026-08-12 09:44 carry the constant `output_raw`. Their accuracy and CodeBLEU
columns are valid; `output_raw` and `identity_output` are not. The Part IV control numbers in §7.7
were generated *after* the fix and are clean.

**8.9 The evaluation stack is 2–15× noisier than this document records, on the control everything is
read against.** *Found 27 August 2026.* `tuned_L0` on Grid B `H1` was evaluated three times with the
**same adapter path, same prompt (sha `c1e8fe28…`), same 115 items, same engine (vllm-0.26.0), same
sampling (T = 0, top-p 1.0, max_tokens 64)**:

| cell | date | git commit | GPU | accuracy |
|---|---|---|---|---|
| `pilot/tuned_L0__H1` | 2026-08-05 | `4927d65` | 2 | **40.0** |
| `baselines/tuned_L0_k0__H1` | 2026-08-13 | `469f857` | 1 | **34.8** |
| `main/tuned_L0_k0__H1` | 2026-08-14 | `469f857` | 1 | **33.9** |

The last two are identical in **every** recorded field including commit and GPU, and still differ on
**12 of 115 generations**, flipping 5 graded trials — 0.9 points. Across the commit boundary the
spread is **6.1 points** and 31 of 115 generations differ (`["Hi","my","name","is","John"]` vs a
per-character split; `20` vs `46214` vs `-4` on one item). **This exceeds §12.10's recorded
"0.1–0.4 points from batching nondeterminism" by 2–15×.**

Grid A's n = 1,214 damps it, and every headline contrast in §12.13 is paired at the item level so a
shifted control does not move a paired delta. **But every Grid B `H1` comparison in this document is
within one re-evaluation of its neighbour** — including the "merge ties the control at 34.8 vs 33.9"
reading that opened the RQ2 chain. *Actions owed:* a determinism note in `CLAUDE.md` §4, and an
`ACCESS_LOG.md` reconcile — one `pilot_eval` plus two `final_eval` passes on the same quarantined
items is more `H1` exposure than §3.2 rule 3 sanctions.

**8.10 The pooled seed band has been applied to Python-only contrasts throughout.** *Found 27 August
2026.* §3.7 reports the noise floor three ways — **Python 0.63 mean / 1.46 p95**, **JavaScript 2.01 /
4.03**, **pooled 1.32 / 3.61** — and states the correct rule. Downstream, the **pooled** figure is
what propagated: it is the operative threshold in `REPORT_2026-08-15_modularity_verdict.md`,
`REPORT_2026-08-17_geometry-and-attempted-repairs.md`, four log entries, and the docstrings of
`scripts/merge/24_crossseed_control.py`, `scripts/merge/25_residual_merge.py` and
`scripts/attn/30_knockout.py`. **Every experiment in RQ2 and RQ3 is Python**, so the bar has been
~2.5× too permissive. Recomputed 27 August over 42 matched Python s17/s42 pairs: **mean 0.52,
median 0.49, p95 0.96, max 2.22.**

What this changes is **one secondary claim, not any verdict.** §12.4's "`mole_hardrouter` reproduces
`mole_router` to max 2.7, every cell inside the 3.61-pt band" is the argument that "mixture" is the
wrong word for the system. At the Python bar of ~1.5 the max |Δ| of **2.67** (on `C_L1b_S1`) does
*not* clear it, and neither does 1.7 on `H1` or `C_L2_S4`. Restate as **"11 of 15 cells inside the
Python noise bar, mean |Δ| 0.88, signed both ways"** — still a strong argument for selection over
blending, but not the blanket equivalence it was written as. Nothing in §12.13, §15 or §16 depends on
the band; those carry bootstrap CIs.

**A second consequence, and the reason 8.9 and 8.10 belong together.** Grid B `H1` — 115 items over
27 programs — **cannot support merge comparisons.** It produced one q = 0.048 "survivor" that shrank
to a third of its size at power; every arm dropped ~10 points between grids; and the *ordering*
changed (`residual_n6_s42` was top on Grid B at 41.7 and is mid-pack on Grid A at 25.6). Every
future `H1` claim should be made on Grid A, and every published Grid B `H1` number should carry an
explicit power caveat.

**8.11 The label-shuffled format control is void as designed, not merely negative.** *Found 27
August 2026.* `formatonly` trains `tuned_L0`'s recipe with `train.shuffle_labels`, to ask how much of
the adapter's gain is "learned to emit a canonical literal". Training was clean and the manipulation
check textbook — identical 4,689 rows and 222 steps, train loss 0.448 → **1.933**, exactly the
plateau expected when the input carries no information about the target. But at eval it emitted **the
same unterminated string on every item**, giving accuracy 0.000 and `format_fail` **0.999** on all
three conditions.

This is a **design fault, not a bug**: with labels shuffled the loss-minimizing policy is the
*marginal* answer distribution, and greedy decoding reads off the mode of a product of per-position
marginals — a generic "average answer" that never terminates. The arm cannot measure what it was
built to measure. **Its cells in §2.2 must be read as void, not as zero.** The question it was for is
answered instead, from existing cells and with no GPU, in §16.4. The `format_fail` gate written into
the eval config is what caught this, and it was written in precisely because 0.0 accuracy alone would
have been ambiguous between "clean floor" and "degenerate adapter".

**8.12 `train_size: 30000` never bound in the LOTO configs.** The folds reason from 38,346 rows,
which is *all* splits. Realised: folds **22,152–23,373**, `mono_all` **26,841** (+21 %). So §12.10's
"LOTO diagonal 38.0 vs `mono_all` 39.2" is **not like-for-like**, and the true cost of holding a
transform out is *smaller* than the reported 1.1 pts — favourable to the conclusion. **Correction
owed in its own commit.**

**8.14 `norm_structural` was silently miscompiling ~1 % of programs, and the gate built to catch
that did not.** *Found 27 August 2026.* The normalizer feeds the model a REWRITTEN program and scores
the answer against the ORIGINAL program's stored output, so the arm is valid only if the rewrite
preserves behaviour. `_pass_fold` collapses `(-1)` to `Constant(-1)`, and `ast.unparse` re-emits
`BinOp(Constant(-1), Pow, Name('r'))` as `-1 ** r` — which Python parses as `-(1 ** r)`, because `**`
binds tighter than unary minus. A term that alternated sign became the constant `-1`. Two of 200 `L0`
programs (`apps_123_0`, `apps_1661_0`) were handed to the model with part of the computation changed.

**This reached a published arm.** `norm_structural` is the strongest zero-training result in the
project (`H1` 12.9 against base 6.3) and every `norm_*` number predating this fix is affected. The
effect is small and biased *against* the arm (a corrupted program can only lose), so no conclusion
in §16 reverses; but the existing `norm_structural` cells are now known to be slight
under-estimates.

**Why `scripts/analysis/21_validate_normalized.py` missed it.** That gate exists for exactly this
failure mode and executes normalized programs against stored outputs — but it had not been re-run
across the full trainable grid since the passes last changed, and the bug fires only on programs
containing a negative literal as the base of `**`. The lesson is not "write a gate" (one existed) but
**re-run the gate whenever a pass changes**; an accuracy loss from a corrupted program is
indistinguishable from "normalization does not help", which is precisely why this survived.

**Fixed generally rather than locally.** `_emit` now re-parses its own output and refuses to return
text that does not mean the tree it was given (`UnparseUnfaithful`, a `Bail` subclass), so *any* pass
tripping the same class of precedence bug reverts to the un-normalized program instead of shipping a
wrong one. A first version of the guard over-fired on **78/200** programs, because folding
legitimately represents `x[-1]`'s slice as `Constant(-1)`, which round-trips to
`UnaryOp(USub, Constant(1))` — structurally different, identically meaningful. The comparison now
canonicalizes negative literals on both sides, which still catches the real bug because in `-1 ** r`
the `USub` operand is a `BinOp`, not a `Constant`. Re-runs are on disk as `norm_structural_fixed`
under a new system name rather than overwriting the published cells, so before/after stays
measurable. Regression tests: `tests/test_inert_spans.py`.

**8.13 `build_manifest.py --eval` silently drops any system whose `arch` starts with `merge`.** A
config mixing merge and non-merge systems queues some and drops the rest without saying so. `--rq2`
is **not** the workaround — it *rebuilds* the standard merges and would overwrite
`runs/adapters/.../merge_*`. Documented, not fixed; the density sweep and the cross-seed control
both used a hand-written queue entry instead.


## 9. What has not been run

*Rewritten 27 August 2026. Nine of the fourteen items in the 08-12 revision have since been
resolved; they are listed at the bottom rather than deleted, because what a project stopped needing
is part of its record.*

**Still open, ordered by what each would settle:**

- **A second held-out obfuscator family.** `H1` is one obfuscator, it is partly burned (§8.4, §8.9),
  and *every* invariance claim in this document rests on it. A virtualization-based `H2` and a
  rearranging `H3` would test the claim far harder; stacking existing generators (`H1∘S1`) is the
  cheap version. **This is the only remaining item that could overturn a verdict rather than qualify
  it** — specifically, if §15/§16's inert-material skill reaches an inert-family `H2` but not a
  rearranging `H3`, the framing changes from "combination fails" to "there is one real skill and it
  is narrow".
- **Any model above 1.5B for RQ1–RQ3.** The 7B runs exist only in the CFT thread and the §9.3
  baseline panel. Every generalization claim here is single-model, and §12.3 shows five of seven
  obfuscation penalties largely dissolve by 7B — so all of RQ2 and RQ3 must be scoped as *"at a
  scale where these transforms still cost the model something"*.
- **Human alignment.** The Paper-2 98-cell anchor and the Paper-3 condition-level comparison — the
  secondary contribution — still untouched.
- **The matched-condition ICL baseline** (§9.1). Inference-only, and it is the comparison a reviewer
  will ask for first.
- **The GLMM stack.** All inference here is cluster bootstrap + BH-FDR; the `stats/` R GLMM with
  crossed random effects for program × model has not been run on these results. `stats/R/config.R`
  also still lacks the composite (`C_`) levels.
- **`S3`/`S4` against `H1` at full size** — §16.3 now gives a reason to want it: `S4` is where
  symbolic analysis was blind and where a stronger pass paid off, so it is the half of `S2` whose
  `H1` behaviour is least predictable.
- **Supervised routing** — training the RouterLoRA gate with the correct expert as an explicit
  target. Deliberately not run: a gate *taught* to decompose is a weaker result than one that
  learned to, and given §12.10's +0.4 it would most likely improve routing and not accuracy again.
- **The invariance-loss arm** — the only attempted repair that optimizes invariance as an
  *objective* rather than through the data. Designed, never built; needs `invariance` added to
  `schema.TrialRow.adapter_arch` first or it fails at the first row written.
- **Second seeds for the RouterLoRA arms.** Every `mole_*` number is n = 1. The specialists have
  s42 banks; the gate does not.
- **A formal comparison of the §7.7 unlearning curves.** The control refutes the 1.5B reading, but
  matched-λ and matched-norm comparisons have not been done — the withdrawal rests on the shape of
  two curves, not on a test.

**Resolved since the 08-12 revision** (each was a bullet above; the section that closed it is named):

| was open | closed by |
|---|---|
| RQ3 (attention) **entirely** — no extraction, no anchoring metric, no knockout | §15 — 3,600 dumps, the anchoring sweep, and a causal knockout with a pre-registered prediction |
| RouterLoRA end to end — "reports a design, not a result" | §12.8–§12.10 — gate trained, ladder evaluated, gate diagnostic read, balanced variant run |
| The merge density sweep (`[0.3, 0.5, 0.7]` configured, only 0.5 ever merged) | §12.12 — swept, and the best density's `H1` read landed |
| The router's OOD behaviour on `H1` (`n_heldout: 0`) | §12.13 — it is *undefined*, not unmeasured: a router over per-transform experts has no correct answer on an unseen transform |
| Second seed for the RQ2 arms | §12.12 — `merge_*_s42` and `residual_n6_s42` exist; the mixture arms remain n = 1 |
| The 8-expert 9-epoch bank | §5.3 — run; Horoi's mechanism reproduces, its consequence does not |
| The uniform-epoch merge sweep, removing the unequal-epoch confound | §5.3 — run; both §5.3 caveats removed |
| A confirmatory held-out-transform read for §3.5 | §12.13 — `+3.46` [+2.06, +4.94] on 1,214 items |
| `fwd2x` / `cftflip`; `compute_is_core`; the HumanEval+ harness | §7.6, §8.1, §8.3 (resolved before 12 August) |
| The geometry→accuracy regression over ~45 merge points, stratified by seed | §14.4 — **resolved by showing it should not be run.** The merges occupy four distinct geometric regimes and are near-constant within each, so a fitted line would be identified from four effective observations. Reported as a four-row table instead |

**And one item was resolved in a way that changed the question.** §7's general-ability claim rested
on HumanEval+; §7.8 shows that benchmark was contaminated, and the held-out replacement overturned
two of the thread's central claims. *A baseline that has "already run" is not the same as a baseline
that is valid.*

---

### 9.1 The ICL baseline that has not been run — and why it matters most for FSE

*Added 13 August 2026.*

**What exists today is the weak form.** `oracle_prompt_1shot` combines an oracle label ("this code
was transformed by X") with **one demonstration drawn from `ONE_SHOT_DEMOS[language]`, which is
clean `L0` code**. It scores `H1` **.157** against the `tuned_L0` control's **.247** and `base`'s
**.064** — better than nothing, far below any adapter.

That is not the baseline a reviewer means by "did you try prompting". The practitioner's move, and
the one `hu2026bindeobf` actually tested, is **k demonstrations in the same obfuscation condition
as the query**. Nothing in this project has measured that.

**Why it is the highest-value remaining baseline.** Every claim in §5 is of the form "adapters /
merges beat the control by N points". If matched-condition ICL closes most of that gap at zero
training cost, the modularity story is far less interesting — and a reviewer will ask. If it does
not, the fine-tuning result is much stronger than it currently looks. Either outcome is worth
knowing before the write-up, and it is **inference-only**: no training, roughly one eval pass per
(k, condition) cell.

**Design.**

| arm | demo source | oracle label | tests |
|---|---|---|---|
| `icl_k1_matched` … `icl_k4_matched` | k examples in the *same* condition, from the train split, never the eval program | off | pure ICL — can examples substitute for weights? |
| `icl_k4_matched_oracle` | as above | on | does naming the transform add anything once examples show it? |
| `icl_k4_clean` | k clean `L0` examples | off | isolates "examples of the task" from "examples of the transformation" |
| *(existing)* `oracle_prompt_1shot` | 1 clean example | on | already run — the weak form |

`H1` is included, and it is the sharp cell: ICL there requires no training on the held-out family,
so it is the one baseline that can legitimately be compared against the merge result without the
"was it trained on?" objection.

**One implementation constraint.** `src/obtune/prompts.py` is frozen — its template sha256 is
pinned in every run manifest, and the charter forbids editing it. `build_prompt` already accepts a
single custom `demo=`, so k=1 matched is reachable today; **k>1 needs a new composing module**
(`src/obtune/icl/prompts.py`), following the precedent of `cft/prompts.py` and `srh/prompts.py`,
which add task formats without touching the frozen builder. Budget the arm accordingly: the eval
is cheap, the plumbing is a day.

## 10. Suggested order of work

*Rewritten 27 August 2026. The 08-12 list is preserved at the bottom with its outcomes, because
five of its seven items landed and two of them changed a conclusion.*

**The project's centre of gravity has moved.** RQ2 is closed and no further RQ2 run is recommended
(§12.13). The live question is now the one §15 and §16 opened: **`tuned_S2` learned dead-code
elimination and does it in attention — does that skill reach an obfuscator nobody trained on?**
Everything below is ordered against that.

1. **Pre-register and build `H2` (inert-family) and `H3` (rearranging).** This is the decisive
   experiment the project does not have. §15 and §16 establish the mechanism *on `S2`*; the step to
   `H1` is inferential and will stay inferential no matter how many more `S2` measurements are
   taken. `H2`/`H3` is the only design that converts it, and it does so **without spending more
   `H1` budget** — which §8.9 shows is a live concern. The cheap first version is stacking existing
   generators (`H1∘S1`).
2. **Promote `H1` to a development set and mint a fresh frozen family.** §8.4 and §8.9 together
   make this less a purity question than an accuracy one: `H1` has been read more than the two
   sanctioned passes, and the control it is read against moves by up to 6 points across passes.
   Doing this *with* item 1 costs almost nothing extra.
3. **Run the matched-condition ICL baseline (§9.1).** Still inference-only, still the comparison a
   reviewer reaches for first, and now cheaper to interpret: the question is no longer "does ICL
   match the merges" (nothing beats the control, so that bar is low) but "does ICL reach
   `tuned_S2`'s +3.46 on `H1`". If a few in-condition demos do, the mechanism story has a
   zero-training rival and needs to say so.
4. **Take the mechanism to 7B.** §12.3 shows five of seven obfuscation penalties largely dissolve
   at 7B while **`H1`'s does not** — so 7B is where the inert-material skill would be most cleanly
   isolated, with the surface-obscurity conditions no longer competing for the explanation. It is
   also the scope caveat every §15/§16 claim currently carries.
5. **Fill the corrections owed** — §8.12's LOTO `train_size`, §8.10's seed-band constant in three
   script docstrings, the §8.9 determinism note in `CLAUDE.md` §4, and the `ACCESS_LOG.md`
   reconcile. None is a run; all are one commit each.
6. **Fill `paper_modularity/main.tex`'s thesis slot with Branch A** (§12.13). The manuscript has
   been waiting on a run that is now known not to be worth doing.
7. **Human alignment** — the secondary contribution, still untouched, and the only part of the
   original design with no result at all.

<details><summary>The 12 August list, and what happened to each item</summary>

1. ~~Fix `compute_is_core` and regenerate the analysis artifacts (§8.1).~~ **Done 2026-08-11**, and
   it retracted a claim.
2. **Run the matched-condition ICL baseline (§9.1).** *Still open* — carried forward as item 3.
3. ~~Run the 12 missing Grid B Python cells (§8.2).~~ **Superseded.** The Grid A panel was completed
   instead, which is the better measurement and is what §12.13 rests on.
4. ~~Finish the 8-expert 9-epoch bank, then the uniform-epoch sweep and merge-optimal search
   (§5.3).~~ **Done.** Horoi's mechanism reproduces; its consequence does not; both §5.3 caveats
   removed.
5. ~~Run RouterLoRA (§5.4). "Report `mole_random` whatever happens — if the learned gate does not
   beat it, the honest headline is *rank-256 residency, not routing*."~~ **Done, and the
   pre-registration held.** The gate collapsed (§12.8), the fix made routing real and changed
   nothing (§12.10), and `mole_random` turned out to be behaviourally a second uniform gate.
6. ~~Decide on `S2`→`H1`.~~ **Both branches taken.** `S3`/`S4` ran, and the confirmatory `H1` read
   landed at +3.46 [+2.06, +4.94]. `H2` was *not* pre-registered — it is now item 1.
7. ~~Start RQ3.~~ **Done, and it produced the project's only causal result** (§15).

</details>

---

## 11. Shot count, and what happens when ICL meets a fine-tuned adapter

**Model: Qwen2.5-Coder-1.5B-Instruct. Grid B (`testset`), n=115–176.** Every arm on identical
items, `base` and `tuned_L0_k0` regenerated inside the same run so no delta crosses a grid.

Two gaps closed at once. Every ICL number before this was **k=1** — not because one example is a
natural operating point, but because it was the only shot count the frozen `prompts.build_prompt`
could express. And every ICL arm had run on the untuned base while every adapter arm ran
zero-shot, so "adapters beat ICL" compared two things that had never been combined.

### Table 39 — accuracy %, base vs k-shot vs the L0 adapter with and without demos

| condition | `base` | `icl_k1` | `icl_k2` | `icl_k4` | **`tuned_L0`** | `tuned_L0`+k1 | +k2 | +k4 |
|---|---|---|---|---|---|---|---|---|
| **H1** (held out) | 11.3 | 22.6 | **28.7** | 28.7 | **34.8** | 33.9 | 28.7 | 33.9 |
| L0 | 29.0 | 34.1 | 36.4 | 37.5 | **50.6** | 47.2 | 48.9 | 45.5 |
| L1b | 23.3 | 24.4 | 26.7 | 27.3 | 38.6 | **39.2** | 37.5 | 35.8 |
| L1r | 23.3 | 28.4 | 30.1 | 30.1 | **49.4** | 42.6 | 43.8 | 41.5 |
| L2 | 21.0 | 29.0 | **35.2** | 33.0 | 46.0 | **47.7** | 46.0 | 46.0 |
| S1 | 26.2 | 29.7 | 28.3 | 31.0 | **45.5** | 40.0 | 40.7 | 41.4 |
| S2 | 18.8 | 25.0 | 29.0 | 30.1 | **46.0** | 43.8 | 40.9 | 43.2 |

Demos are drawn from trainable conditions only; `icl.demos.pick_demos` refuses H1 as a source
outright (CLAUDE.md §3.2 rule 2 — a demo is prompt conditioning), so H1 is only ever the query.

### 11.1 ICL saturates at two examples

k=1 → k=2 is worth **+6.1 pts on H1** (22.6 → 28.7); k=2 → k=4 is worth nothing. The same shape
holds on every condition. **The fair ICL comparator is therefore 2-shot, not 1-shot**, and every
k=1 figure quoted earlier in this report understates the baseline by roughly 6 points on H1.
Corrected here rather than in place, per the never-alter-an-entry rule.

### 11.2 ICL and fine-tuning do not compose — demos make the adapter worse

`tuned_L0` alone is the best cell in **6 of 7 conditions**. Adding demonstrations costs between
0.9 and 6.8 points; the worst is L1r, 49.4 → 42.6. Only L1b (+0.6) and L2 (+1.7) gain at all,
both inside seed noise (1.32 pts mean, 3.61 p95 over 84 matched pairs, §8.4).

This was pre-registered as one of three possible outcomes and was the least expected: **the
adapter is prompt-format-sensitive.** It was trained zero-shot, and demonstrations push it off
the distribution it was fitted on.

Two readings the data cannot separate:

1. fine-tuning has already internalised what a demonstration supplies, so the demo adds nothing
   and its format cost dominates; or
2. the format shift costs more than the demo adds, whatever the demo contributes.

Distinguishing them needs an adapter trained *with* demonstrations in context, which does not
exist and is not queued. **Do not report this as "fine-tuning subsumes ICL"** — that is reading 1
asserted without its alternative excluded.

The practical claim is safe and worth stating on its own: **few-shot prompting a fine-tuned
adapter degrades it here.** No adapter arm had ever been run with demos, so this would not have
surfaced otherwise.

### 11.3 The control adapter beats every zero-training baseline on held-out data

`tuned_L0` reaches **34.8 % on H1** against the best zero-training arm's 28.7 % — and `tuned_L0`
is the *control*, trained on clean code with no obfuscation exposure at all. Task acquisition
alone transfers to an unseen obfuscator better than any amount of in-context demonstration.

~~**Caveat that limits how far this goes.** Grid B only. The merge and mixture headlines are Grid A
(§5, §6), so `tuned_L0` 34.8 here is **not** comparable to `merge_dare_ties` .348 there — the two
grids differ by ~5 points on the H1 floor alone. The Grid A baseline panel (§12, pending) is what closes
that gap; until those numbers are read, no baseline-vs-merge sentence belongs in this report.~~

**Correction, 14 August 2026 — the caveat above was wrong, and it was blocking a claim that is
legal.** `merge_dare_ties` on `H1` is **Grid B**, not Grid A: `results/cells/main/qwen25c-1.5b/
python/merge_dare_ties__H1` is n=115 over 27 programs. So is every merge and mixture arm's `H1`
cell. §2.2 labels them `B` correctly; the mistaken "Grid A" came from the header comment in
`configs/eval/baselines_gridA_qwen1.5b.yaml`, which was written from memory and never checked.

The comparison is not merely same-grid, it is **same-item**: the `H1` cells of `base`,
`norm_full`, `oracle_prompt_1shot`, `icl_k1`, `icl_k2`, `merge_ties`, `mole_router`,
`merge_dare_ties` and `tuned_L0_k0` all carry byte-identical `item_id` sets (115 items, 27
programs), verified by set comparison. The whole ladder can therefore be read in one column:

| system | H1 % | kind |
|---|---|---|
| `base` | 11.3 | untrained |
| `norm_full` | 13.9 | zero-training, symbolic |
| `oracle_prompt_1shot` | 20.9 | zero-training, oracle-described |
| `icl_k1` | 22.6 | zero-training, 1 demo |
| `icl_k2` | 28.7 | zero-training, 2 demos |
| `merge_ties` | 28.7 | 6 experts merged |
| `mole_router` | 33.9 | RouterLoRA mixture, 8 experts |
| `merge_dare_ties` | **34.8** | 6 experts merged, the best merge |
| `tuned_L0_k0` | **34.8** | **one adapter, trained on clean code only** |

**The best merge of six obfuscation specialists exactly ties a single adapter that never saw an
obfuscated program.** The eight-expert RouterLoRA mixture lands 0.9 below both. This is the
sharpest statement of §5's negative result available anywhere in this report, and it needed no
new GPU time — only the recognition that these cells were always on the same items.

Two guards on how far it goes. The tie is a tie *on this grid*: 27 programs is small, and 0.9
points is well inside the 3.61-pt p95 seed band (§8.4), so `mole_router` ≈ `merge_dare_ties` ≈
`tuned_L0_k0` is the honest reading rather than a ranking. And it is `H1` only; on the trainable
conditions the merges and the mixture do beat `tuned_L0_k0` in places (§2.2).


---

## 12. The zero-training baselines, the 7B ladder, and the hardened router

*Added 14 August 2026.* Three result sets landed on the night of 13–14 August. This section reads
them out. **One of the three is partly unusable and the reason is a defect, not a shortfall of
compute** — §12.1 states it before any number, because the affected cells look complete.

### 12.1 The Grid A baseline panel is incomplete, and it is incomplete silently

`configs/eval/baselines_gridA_{qwen1.5b,7b}.yaml` were built to move the zero-training baselines
onto Grid A. They ran, they reported success, and they wrote fewer than half the cells they name.

The cause is the **phase-namespace defect of 2026-08-13 recurring one level down**. A cell's path
is `results/cells/{phase}/{model}/{language}/{system}__{condition}` — it encodes the phase but
**not `eval_source`**. Both the Grid B baseline configs and the Grid A ones declare
`phase: baselines` and share system names (`base`, `norm_full`, `icl_k1_cross`, `icl_k1_clean`).
So the Grid A run, under `output.resume: true`, found Grid B cells sitting at the paths it wanted
and skipped them — exactly the failure its own header comment warns about ("Matched floor,
regenerated here — never resumed from another grid. That mistake is the whole reason this file
exists.").

What that leaves on disk, by system (`A` = Grid A written, `B` = Grid B cell left in place):

| model | system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
|---|---|---|---|---|---|---|---|---|
| 1.5B | `base` | B | B | B | B | B | B | B |
| 1.5B | `icl_k1_clean` | **A** | B | B | B | B | B | B |
| 1.5B | `icl_k1_cross` | **A** | B | B | B | B | B | B |
| 1.5B | `icl_k4_cross` | A | A | A | A | A | A | A |
| 1.5B | `norm_full` | B | B | B | B | B | B | B |
| 1.5B | `norm_structural` | A | A | A | A | A | A | A |
| 1.5B | `tuned_L0` | A | A | A | A | A | A | A |
| 7B | `base` | B | B | B | B | B | B | B |
| 7B | `icl_k1_clean` / `icl_k1_cross` / `icl_k4_cross` | A | A | A | A | A | A | A |
| 7B | `norm_full` | B | B | B | B | B | B | B |
| 7B | `norm_structural` | A | A | A | A | A | A | A |

**Nothing was destroyed** — the skipped writes left valid Grid B cells untouched, and the two
`icl_k1_*__L0` cells had no Grid B counterpart to overwrite (that config never evaluated `L0`).
The damage is that `icl_k1_clean` and `icl_k1_cross` are now **single rows spanning two grids**:
`L0` from Grid A at n=1670 beside six conditions from Grid B at n=176. A row like that averages
to a number and prints without complaint.

Missing Grid A cells: **19 at 1.5B** (`icl_k1_clean` ×6, `icl_k1_cross` ×6, `norm_full` ×7) and
**14 at 7B** (`base` ×7, `norm_full` ×7).

**The floor, at least, is recoverable for free at 1.5B.** `results/cells/main/…/base__{cond}` are
Grid A cells over exactly the populations the Grid A baseline arms used — verified by snippet-id
set comparison, identical for all seven conditions. The `base` row below is taken from there. **At
7B there is no such fallback**: `main` holds no 7B RQ1 cells, so the 21 Grid A ICL and
normalization cells at 7B currently have **no matched floor and cannot be interpreted at all**.

The fix is a path change, not GPU time: `eval_source` must appear in the cell path (or in the
resume key) so that two grids cannot alias. Until then, `phase` is doing work it was never
designed to do, and this is the second incident from the same root cause in two days.

### 12.2 What the Grid A panel does show, where it is complete

1.5B, accuracy %, n = 1214–1670, all rows on identical program sets. `base` from `main/`, per
above; trained rows included so the baselines can be read against what they are meant to threaten.

| system | L0 | L1b | L1r | L2 | S1 | S2 | H1 | kind |
|---|---|---|---|---|---|---|---|---|
| `base` | 21.7 | 18.8 | 18.7 | 19.8 | 20.7 | 15.3 | 6.4 | untrained |
| `norm_structural` | 22.0 | 18.8 | 18.9 | 19.7 | 20.0 | 19.9 | 12.9 | zero-training |
| `icl_k4_cross` | 33.1 | 26.4 | 27.3 | 27.2 | 27.7 | 28.5 | 18.2 | zero-training |
| `mono_all` | 41.6 | 38.1 | 36.7 | 37.9 | 39.2 | 41.5 | 22.9 | trained, all conditions |
| `mono_r128` | 43.0 | 38.7 | 38.3 | 38.7 | 39.7 | 41.9 | 21.4 | trained, rank 128 |
| `tuned_L0` | 45.0 | 34.2 | 36.5 | 37.4 | 39.1 | 41.4 | 24.7 | **the control** |
| `tuned_S2_s17` | 45.6 | 33.3 | 37.4 | 37.8 | 43.4 | 45.3 | 28.0 | best specialist |

**The headline the panel was built to produce survives, with room to spare.** On `H1` the best
zero-training arm reaches 18.2 against the control adapter's 24.7 and the best specialist's 28.0.
Four-shot ICL closes roughly 60 % of the control's gain over base (11.8 of 18.3 points) — a much
larger fraction than the 1-shot Grid B arms suggested, and large enough that **the ICL baseline
must be reported at k=4, not k=1**, or the contribution is overstated.

**`norm_structural` is the interesting zero-cost arm and it is condition-selective.** It is inert
on the four renaming conditions (−0.7 to +0.3, all inside noise) and moves only where its `dce`
pass has something to delete: **S2 +4.6** (opaque predicates + dead code) and **H1 +6.5**. It more
than doubles base accuracy on the held-out obfuscator for zero GPU-hours. That is not a threat to
the fine-tuning story — 12.9 against 24.7 — but it is a real effect on the paper's discriminator,
produced by a rewriter that was deliberately never tuned against H1 (log 2026-08-13), so it is an
honest OOD measurement and belongs in the write-up rather than a footnote.

**A free reproducibility number.** `tuned_L0` was regenerated on Grid A by this run while `main`
already held the same adapter (identical sha `82329cd…`), same seed, same prompt, greedy decoding,
same items. The two disagree by **0.1–0.4 points** (max 0.36 on S2). That is the eval stack's own
nondeterminism floor — vLLM batching, not seed variance — and it sits *under* the 1.32-pt mean
seed noise of §8.4 rather than replacing it. Worth quoting whenever a sub-half-point difference is
discussed.

### 12.3 The 7B result constrains how the whole project may be framed

Base model, no adapters, Grid B, n = 115–176 — the same items at both scales:

| condition | 1.5B | 7B | gain | 7B penalty vs its own L0 |
|---|---|---|---|---|
| L0 | 29.0 | 57.4 | +28.4 | — |
| L1b | 23.3 | 49.4 | +26.1 | **−8.0** |
| L1r | 23.3 | 56.2 | +33.0 | −1.2 |
| L2 | 21.0 | **58.0** | +36.9 | **+0.6** |
| S1 | 26.2 | 50.3 | +24.1 | **−7.1** |
| S2 | 18.8 | 55.7 | +36.9 | −1.7 |
| S3 | 18.2 | 56.8 | +38.6 | −0.6 |
| S4 | 22.2 | 57.4 | +35.2 | 0.0 |
| H1 | 11.3 | 36.5 | +25.2 | **−20.9** |

At 1.5B the trainable ladder spans 18.2–29.0 and every condition costs the model something. At 7B
it spans 49.4–58.0, and **`L2` — sequential minification, the most aggressive renaming in the
ladder — scores above clean code.** Of the seven obfuscations, only three still carry a penalty
worth the name: `L1b` (−8.0), `S1` (−7.1) and `H1` (−20.9). `L1r`, `L2`, `S2`, `S3` and `S4` land
within 1.7 points of `L0`, which is inside the seed band.

**This has to change the framing, not just add a row.** "Obfuscation costs comprehension" is a
claim about models, and at 7B it is mostly false for this ladder. The defensible version is
narrower and more interesting:

* **What dissolves with scale is the *surface* penalty.** Random and sequential renaming, opaque
  predicates and dead code all stop mattering once the model is large enough to read past them.
  A 1.5B-only paper would have reported five robust obfuscation effects that are substantially
  artifacts of model capacity.
* **What survives is semantic, not syntactic.** `L1b` is the one renaming condition that still
  hurts at 7B — and it is the one whose names are *actively misleading* rather than merely
  uninformative. The penalty is not "identifiers were removed", it is "identifiers were made to
  lie", which a bigger model is not immune to and may even be more susceptible to. `S1` survives
  because control-flow flattening genuinely destroys structure rather than obscuring it. This
  pairs directly with §3.5's `S2` result and is the sharper story.
* **`H1` survives hardest, and that is the discriminator working.** −20.9 points at 7B, against
  −17.7 at 1.5B: the held-out obfuscator is the *only* condition whose penalty does not shrink
  with scale. Every conclusion in this report that rests on `H1` is therefore strengthened by the
  7B result, not weakened by it.
* **The scope sentence the write-up now owes the reader.** All adapter, merge and mixture results
  are 1.5B. Since five of seven obfuscation penalties largely vanish by 7B, the modularity and
  transfer findings must be scoped as "at a scale where these transforms still cost the model
  something", and the question of whether merging fails the same way at 7B is open and unrun.

`norm_full` at 7B (Grid B, matched) shows the same selectivity from the other side: **L1b +5.7**
and L1r +1.7 — normalization recovers part of the one renaming penalty that scale does not — while
**S1 −12.4**, where canonicalizing a flattened dispatch loop destroys what little structure is
left. H1 −2.6.

### 12.4 `mole_hardrouter`: the mixture is a selection, not a blend

`HardenedGate` is the trained RouterGate with its softmax replaced by a one-hot argmax — identical
weights, so the pair isolates *blending* from *per-token selection* (log 2026-08-13 addendum).
Grid B, n as marked:

| system | L1r | S1 | C_L1r_S1 | C_S1_L1r | C_L1b_S1 | C_L2_S4 | C_L1r_S3 | C_S4_S3 | H1 |
|---|---|---|---|---|---|---|---|---|---|
| `mole_uniform` | 50.6 | 44.1 | 36.7 | 41.3 | 39.3 | 46.6 | 44.3 | 44.9 | 33.0 |
| `mole_random` † | 50.0 | 44.8 | 36.0 | 40.7 | 38.0 | 44.9 | 44.3 | 44.9 | 33.0 |
| `mole_router` | 51.1 | 47.6 | 40.7 | 42.0 | 42.0 | **54.0** | 46.0 | 47.7 | 33.9 |
| `mole_hardrouter` | 51.7 | 46.9 | 41.3 | 42.0 | **44.7** | 52.3 | 47.7 | 47.7 | 32.2 |
| | n=176 | n=145 | n=150 | n=150 | n=150 | n=176 | n=176 | n=176 | n=115 |

† **`mole_random` is a weaker control than its name suggests** (*added 27 August 2026*). It is a
`RouterGate` frozen at random init, and at random init the softmax over eight experts is
essentially flat: its mean normalised entropy is **1.000** and its per-expert mass is uniform to
three decimals — behaviourally a *second uniform gate*. It differs from `mole_uniform` on only
3–11 generations per condition and by ≤1.7 accuracy points. So `router − random` and
`router − uniform` measure the same contrast, and **the ladder has three rungs but two distinct
controls.** This is what kills `CLAIM_LADDER.md` Branch B (§12.13): the residency confound is
controlled, but "non-uniform-but-uninformative weighting" never was.

`hardrouter − router` runs +0.6, −0.7, +0.6, 0.0, +2.7, −1.7, +1.7, 0.0, −1.7 — mean |Δ| 1.0,
max 2.7, signed in both directions.

> **Corrected 27 August 2026.** This originally read *"every one inside the 3.61-pt p95 seed
> band (§8.4)"*. **3.61 is the Python + JavaScript *pooled* band; the Python-only bar that applies
> here is 0.63 mean / 1.46 p95** (§8.10). Recomputed over all 15 cells, `hardrouter − router` has
> mean |Δ| **0.88** and max |Δ| **2.67**, and **four cells do not clear the Python bar** —
> `C_L1b_S1` (+2.67), `C_L2_S4` (−1.70), `C_L1r_S3` (+1.70) and `H1` (−1.70). The defensible
> statement is **"11 of 15 cells inside the Python noise bar, mean |Δ| 0.88, signed both ways"**,
> which still supports the conclusion below — the deviations are small, unsigned and concentrated
> on the composites — but it is not the blanket equivalence originally written.

**Hardening the gate to a one-hot changes nothing of consequence.** Whatever RouterLoRA is buying over its
uniform and random controls, it is not buying it by *mixing* experts — a single argmax-selected
expert per token reproduces the result. Two consequences:

0. **Read §12.8 with this.** The gate reports say the mechanism is narrower still: the gate's
   output barely depends on the input at all, so hardening it *cannot* change which expert wins.
   What follows is right, and §12.8 gives the reason.
1. **"Mixture" is the wrong word for this system** and should not be used in the write-up.
   `mole_router` is a learned per-token *selector* over eight adapters; its accuracy is fully
   explained by which expert it picks, not by how it weights them.
2. It makes the arm cheaper to defend and cheaper to run. A one-hot gate is a discrete routing
   decision, which is inspectable and ablatable in ways a soft blend is not — the natural next
   question (which expert does it choose, and does that choice track the true condition?) is now
   answerable, and was not before.

**The H1 column is the more important finding in this table, and it is negative.** All four arms
land at 32.2–33.9 on the held-out obfuscator — and note (§8.9) that the *control* on this grid,
the same clean-code adapter, itself reads 33.9–40.0 across three re-evaluations, so this whole
column is inside its own measurement noise. The trained router's advantage over `mole_uniform`
and `mole_random` — worth 3–5 points on the composites — is **exactly zero on H1**, where the gate
has no expert that matches the input. Routing gains do not transfer to an unseen transform. This
belongs beside §5.2's saturated-router result: routing is a ceiling on the conditions it was
trained over, and not even a ceiling outside them. *(The gate-entropy readout the config
specifies is written per-cell as `gate_report.json` but has not been analysed; that is the
outstanding piece of this arm.)*

### 12.5 The demo penalty on the adapter is not a formatting artifact

§11.2 left two readings of "demos make the adapter worse" undistinguished, and named a
3-GPU-hour experiment to separate them. One of the two can be **partly excluded from data already
on disk**, at no cost.

Untrained arms fail the constrained output format far more often than adapters do: mean
`format_fail_rate` is 6.7 % for `base` on Grid B (18.1 % on Grid A) against 1.8–2.3 % for every
`tuned_L0_k*` arm. If demonstrations hurt the adapter by pushing it off the prompt distribution it
was fitted on, the cheapest place for that to show up is broken output format. It does not:

| arm | raw acc % | acc among format-OK % | format-fail % |
|---|---|---|---|
| `base` | 21.8 | 23.2 | 6.7 |
| `icl_k1` | 27.6 | 29.6 | 6.9 |
| `icl_k2` | 30.6 | 32.0 | 4.1 |
| `icl_k4` | 31.1 | 31.7 | 1.9 |
| `tuned_L0_k0` | **44.4** | **45.2** | 1.8 |
| `tuned_L0_k1` | 42.1 | 42.8 | 1.9 |
| `tuned_L0_k2` | 40.9 | 41.8 | 2.3 |
| `tuned_L0_k4` | 41.0 | 41.8 | 1.9 |

The adapter's format-failure rate is **flat across k** (1.8 → 1.9 → 2.3 → 1.9), and conditioning
on format-OK trials moves every arm by under 1.5 points while preserving the k0 > k1, k2, k4
ordering. So the demos are not knocking the adapter out of format; they are making it answer
*wrong*. The crude form of reading 2 — "the format shift costs more than the demo adds" — is
excluded. A subtler distributional-shift account survives, and the adapter-trained-with-demos
experiment is still the one that settles §11.2.

The same table kills a symmetric objection to the ICL arms: demonstrations do teach the base model
the output format (6.7 % → 1.9 % from k0 to k4), but ICL's accuracy gain survives conditioning
(23.2 → 31.7), so it is not merely format compliance either.

*Caveat: conditioning on format success is post-treatment conditioning, so these columns are a
diagnostic, not an estimate of a causal effect. The flat format-failure rate across k is the
load-bearing observation and needs no conditioning at all.*

### 12.6 Where the remaining headroom is, in the order it is worth spending GPU on

*Added 14 August 2026, and queued as pipeline stages the same day.*

`tuned_L0_k0` topping the `L0` and `H1` columns has been read as "the control wins, there is
nothing left to improve". That reading is wrong in a specific way worth stating: it tops **2 of
7** Grid B columns and is mid-pack on the rest — clearly beaten on `L1b` (.386 vs `tuned_L2`'s
.477), `L2`, `S1` and `S2`. The shape is the thesis, not a ceiling: **systems win on the
conditions they were trained for, and the clean-code control wins on clean code and on the
held-out obfuscator.** What follows is where that leaves real headroom.

| # | item | cost | why it is in this order |
|---|---|---|---|
| 1 | **L0-merge control** — merge N random-seed `L0` adapters | ~3 GPU-h | **The gate.** If merging three clean-code adapters also reaches ~.348 on `H1`, then merging regresses toward the control, the specialists contributed nothing, and items 2–4 are answering a settled question. Nothing else on this list should be believed before it runs. |
| 2 | **Under-trained experts** | e1–e9 bank exists | §5.3's open idea: over-specialised experts are trivially routable *and* mutually interfering — one cause, two symptoms. `overtrain_full_dare_ties` already *rises* e1→e9 on five of six conditions, which runs opposite to the paper's prediction and is unexplained. |
| 3 | **Merge density sweep** | ~1 GPU-h | `[0.3, 0.5, 0.7]` has been configured since day one; only 0.5 was ever merged. Density is the one merge hyperparameter that changes the answer to RQ2, and every §5.2 conclusion rests on an unexamined default. |
| 4 | **Second seed for the RQ2 arms** | ~1 GPU-h | Every merge and mixture number is n=1 against a 3.61-pt p95 seed band (§8.4). The six `_s42` specialists already exist, so this needs no training — and some of §2.2's Grid B ranking is probably noise. |

**The router is not on this list, deliberately.** It is already saturated at 100 % route accuracy
(§5.2), and §12.4 shows that hardening its gate to a one-hot argmax changes nothing. There is no
headroom in a component that already selects correctly every time; the headroom is in the experts
it selects among.

---

### 12.7 Optimising for out-of-distribution — the programme, and the rule that makes it reportable

*Added 14 August 2026.*

The project's stated goal is a system that generalizes to unseen obfuscation. The instinct is to
tune against `H1`. **That specific move is the one thing that destroys the ability to claim the
result**: `H1` is the only evidence separating semantic invariance from transform memorization, so
selecting on it converts every downstream `H1` number into training accuracy (§3.2 rule 2). The
constraint is not caution — it is what makes `.348` quotable at all.

The real problem is structural: **the project has one OOD condition and it is the test set.** There
has never been an OOD *dev* set to tune against. Everything below follows from fixing that.

### The three-tier design

| tier | conditions | may be used for |
|---|---|---|
| trainable | `L0`…`S2`, `S3`, `S4` | training, everything |
| **OOD-dev** | LOTO folds; `H2`, `H3` when built | **method selection, sweeps, tuning** — reported as such |
| **OOD-test** | `H1` (+ a fresh family if `H1` is ever promoted) | one confirmatory read, never tuned against |

### Stage 1 — LOTO, the free unlock *(queued 2026-08-14)*

Train on five trainable conditions, evaluate on the held-out sixth, rotate: six folds, six honest
OOD estimates, **no quarantine budget spent**. `configs/train/loto_qwen1.5b_py_hold*.yaml` and
`configs/eval/loto_qwen1.5b.yaml`; ~15 GPU-h for the six mixture adapters plus one eval pass.

This is *not* the §3 transfer matrix, which is train-on-**one**, test-on-others. LOTO is
train-on-**many**, test-on-unseen — the regime `H1` actually probes, and it has never been run. §4
found breadth does not help *within* the trained set; LOTO measures whether it buys anything
*outside* it. The 6-fold diagonal mean then becomes the statistic that merge density, expert
training length, router design and any invariance loss are selected against.

### Stage 2 — more held-out families

`H1` is string encoding + guarded MBA, i.e. **data/arithmetic encoding**. More of the same family
tests little. The families that span the space:

| new | mechanism | what it tests that nothing else does |
|---|---|---|
| `H2` | **virtualization** — body compiled to a bytecode VM + interpreter loop | The strongest real-world obfuscation, maximally distant from every trainable condition. |
| `H3` | **exception-driven / CPS control flow** | Structural, but a mechanism `S1`'s dispatch loop never exhibits — separates "learned that control flow can be rewritten" from "learned dispatch loops". |
| `H4` | variable splitting / array-index data encoding | Data family, novel mechanism; the natural frozen final test if `H1` is promoted to dev. |

**Cheapest expansion by far: composition.** `H1∘S1`, `H1∘L1b` reuse generators that already exist
and already pass a soundness gate, and the composite eval machinery was built for the mixture
ladder. They test whether penalties compound or saturate. New *families* are not cheap — each needs
a generator, a semantic soundness gate, quarantine plumbing and an access log; budget 1–2 days of
engineering each plus CPU gate time.

### Stage 3 — training for invariance rather than for per-condition accuracy

Every arm so far trains for accuracy on specific conditions and hopes invariance follows. §4 says
it does not. The direct approaches, in order of how much existing infrastructure they reuse:

1. **Consistency / contrastive loss across transform pairs of the same program** — penalize the
   model for representing `L1b(p)` and `S1(p)` differently. This optimizes semantic invariance as
   an *objective* rather than as a side effect. The `cft/` contrastive infrastructure already
   exists, and `nikiema2025contrastive` — whose CFT fix worked on **renaming only** — is the
   nearest prior work, so extending it across the structural family is a contribution rather than
   a re-run.
2. **Train on composites, not single transforms.** Every trainable condition is single-transform
   from `L0` by construction; `H1` is not. Stacked conditions are a much closer proxy for what OOD
   looks like, and the composite generators exist.
3. **Randomize transform parameters** within each condition, so the model cannot fit one
   obfuscator's fingerprint — closing off the memorization route the paper exists to rule out.

### On promoting `H1`

Worth recording honestly: **`H1` is already partly burned.** The ACCESS_LOG has multiple reads, the
2026-08-13 entry documents nine rows in a single day, and it has since been evaluated across the
baseline, merge, mixture and k-sweep arms. Treating it as pristine is generous.

So there is a legitimate version of "optimise for `H1`": **promote it to OOD-dev, tune against it
freely, and mint a fresh frozen family as the final test.** That is a real option, not a
consolation prize. It should be decided only once `H2` exists — the decision is irreversible and
costs nothing to defer.

---

### 12.8 What the RouterLoRA gate actually attends to — it is not routing

*Added 14 August 2026.* `mole/eval_mole` has written a per-cell `gate_report.json` (per-layer
expert mass and per-token routing entropy over the 8-expert bank) since the mixture ladder first
ran, and nothing had read them. `scripts/analysis/22_gate_routing_report.py` does;
`results/analysis/gate_routing.json` is the artifact.

**Expert mass, `mole_router`, mean over 28 layers. Uniform would be .125.**

| condition | L0 | L1b | L1r | L2 | S1 | S2 | S3 | S4 | entropy |
|---|---|---|---|---|---|---|---|---|---|
| `L1r` | .015 | .111 | **.003** | .387 | .012 | .215 | .001 | .256 | .157 |
| `S1` | .012 | .109 | .004 | .390 | **.013** | .252 | .001 | .219 | .162 |
| `C_L1r_S1` | .015 | .107 | .003 | .398 | .016 | .224 | .001 | .236 | .178 |
| `C_S1_L1r` | .010 | .104 | .004 | .411 | .011 | .253 | .001 | .205 | .154 |
| `C_L1b_S1` | .016 | .132 | .003 | .371 | .018 | .208 | .001 | .252 | .174 |
| `C_L1r_S3` | .013 | .105 | .003 | .380 | .011 | .248 | .001 | .239 | .151 |
| `C_L2_S4` | .016 | .101 | .001 | .377 | .005 | .270 | .001 | .228 | .161 |
| `C_S4_S3` | .015 | .116 | .002 | .342 | .008 | .228 | .001 | .289 | .180 |
| `H1` | .011 | .111 | .003 | .400 | .010 | .232 | .001 | .232 | .157 |

**The rows are the same row.** Total-variation distance between each condition's profile and the
grand mean is **0.011–0.056** — every input produces essentially one fixed distribution: ~.38 on
`L2`, ~.24 each on `S2` and `S4`, ~.11 on `L1b`, and **near-zero on `L1r`, `S1`, `S3` and `L0`**.
Three of the eight experts are effectively dead regardless of input.

**It does not route a condition to its own expert.** On the `L1r` cell the `L1r` expert receives
**.003** — 38x *below* what uniform would give it. On `S1`, the `S1` expert gets .013. The gate
does not merely fail to specialise; it actively avoids the matching expert.

**Composites do not decompose.** Mass on the experts whose transforms are actually present,
against a chance level of 2/8 = .250:

| composite | relevant experts | chance | `mole_router` | verdict |
|---|---|---|---|---|
| `C_L1r_S1` | L1r, S1 | .250 | **.019** | 13x below chance |
| `C_S1_L1r` | S1, L1r | .250 | **.016** | 16x below chance |
| `C_L1r_S3` | L1r, S3 | .250 | **.004** | 60x below chance |
| `C_L1b_S1` | L1b, S1 | .250 | .149 | below chance |
| `C_S4_S3` | S4, S3 | .250 | .290 | ~chance |
| `C_L2_S4` | L2, S4 | .250 | .605 | **above chance — but see below** |

**`C_L2_S4` is the trap in this table.** It looks compositional at .605, and it is not: `L2` and
`S4` are precisely the two experts the gate favours on *every* input, including `H1` and `L1r`. The
arm that separates "detects the transforms present" from "always picks L2 and S4" is `C_L1r_S1`,
whose relevant experts are ones the gate never uses — and it scores .019. Reading `C_L2_S4` alone
would have produced a compositionality claim that the rest of the table refutes.

**Order has no effect either**, which follows: `C_L1r_S1` and `C_S1_L1r` differ by .003 in relevant
mass, i.e. by nothing.

**Consequences.**

* **"Router" is the wrong word, and so was "mixture".** §12.4 showed the trained gate argmaxed to
  one-hot changes nothing; this says why — the gate output barely depends on the input, so
  hardening it cannot change which expert wins. What RouterLoRA learned is a **fixed static
  mixture weight** over the bank, not a routing function. Its edge over `mole_uniform` is the edge
  of a tuned constant blend over an untuned one.
* **It explains the H1 result mechanically.** §12.4 found the router's 3–5 pt composite advantage
  falls to zero on `H1`. Of course it does: the gate emits the same blend on `H1` as everywhere
  else (TV = .016 from the grand mean), with the same entropy (.157). It is not "confidently
  wrong" and it does not "go uniform" — it is simply not looking at the input.
* **The `S2` decomposition thread is untouched by this.** §3.5's `S2`→`H1` result is a
  per-condition adapter finding and does not route.

**Limitation, stated because it bounds the claim.** `MoLEModel._captured[layer]` is *overwritten*
on each forward, so `gate_report.json` describes the **final batch** of a cell rather than all its
items. The cross-condition comparison survives that — a batch of pure `L1r` items still puts .003
on the `L1r` expert — but the per-condition estimates are noisier than the decimals suggest, and
per-item routing variation within a condition is invisible. Changing that overwrite to an
accumulate is a one-line fix and would give whole-cell routing statistics at no extra GPU cost;
it is not done.

### 12.9 Why the gate does not route, and how to fix it

*Added 14 August 2026.* §12.8 is a symptom. The cause is in the training setup, and it is not
subtle.

**The gate is trained on the task loss alone.** `mole/train_mole.py` steps
`loss = holder.model(**batch).loss` and nothing else. Grepping `src/obtune/mole/` and
`configs/mole/` for `load_balanc`, `aux_loss`, `z_loss`, `importance` or `entropy_reg` returns
**nothing**. There is no load-balancing term, no entropy regularizer, and no supervision on which
expert to select.

**Collapse is therefore the expected outcome, not a surprise.** Switch Transformer and GShard both
introduce an auxiliary load-balancing loss precisely because a gate trained on task loss alone
converges to a constant: a fixed blend that minimises average loss is a perfectly good optimum, and
nothing in the objective rewards *varying* with the input. What we built optimises exactly what we
asked it to.

**The learned temperature confirms it.** `gate.report()` shows tau falling to **0.39–0.51 across
all 28 layers**, uniformly, from an init of 1.0. The gate learned to be *more confident* about its
fixed preference — sharpening a decision that does not depend on the input.

#### The fix, in the order worth running

**Step 0 — the diagnostic that decides everything else (~1 GPU-h + CPU).** Fit a linear probe on
the residual stream at the layers the gate reads, predicting condition identity.

* Probe decodes the condition → the signal is present and the gate is a **training** failure.
  Fixes 1–3 apply.
* Probe is at chance → no gate architecture can route on that input, and the fix is a different
  gate *input* (fix 4), not a better loss.

This is "Part I Phase 2 (probes + CKA)" from the plan file. It stops being a side quest and becomes
the load-bearing diagnostic: without it, fixes 1–3 are guesses about which failure this is.

**Fix 1 — load-balancing auxiliary loss.** Switch-style `L_aux = E · Σ_i f_i · P_i` at α ≈ 0.01,
where `f_i` is the fraction of tokens routed to expert *i* and `P_i` the mean gate probability. One
term, directly penalises the dead-expert pattern (`L1r`, `S1`, `S3`, `L0` at ~.003). This alone
usually revives dead experts.

**Fix 2 — supervise the routing. The strongest fix for the composition question specifically.**
The condition labels already exist. Add an auxiliary cross-entropy on the gate: for condition `X`,
target one-hot on expert `X`; for composite `C_X_Y`, target two-hot (.5/.5) on `X` and `Y`. That
teaches decomposition directly, which is the property §12.8 shows is absent.
*Quarantine-safe*: only trainable conditions are ever supervised and `H1` is never a training
input, so no leakage. *State it honestly in the write-up*: with fix 2 the claim becomes "a gate
**taught** to decompose does/does not transfer to `H1`", which is weaker than "a gate **learned**
to decompose" — but it is a real and cleaner question, and the current arm answers neither.

**Fix 3 — stop the gate sharpening before it can discriminate.** Freeze `tau` at 1.0, or add an
entropy bonus with a floor. Nearly free, and it removes the confound where an over-confident gate
cannot recover from an early bad preference.

**Fix 4 — route per SEQUENCE, not per token.** Obfuscation type is a property of the whole program;
the current gate makes a fresh decision for every token at every layer. That is a far harder and
noisier problem than the task requires. A pooled sequence representation with one routing decision
per program is better matched to the structure, and it makes the routing decision inspectable
(one vector per program, not 28 × T).

**Fix 5 — if the probe says the signal is there but routing still does not pay, the problem is not
the gate.** The L0-merge control (§12.7 sequencing, run 14 August) found that merging six
obfuscation specialists reaches the same `H1` accuracy as merging three clean-code adapters. If the
experts contribute little that is *distinct*, routing has nothing to gain and no gate can create
it. The fix is then upstream — more differentiated experts (§12.6 item 2) — and "routing does not
help" becomes a statement about the expert bank rather than about routing.

**Suggested order:** Step 0 probe → fixes 3 + 1 together in one retrain (~3 GPU-h) → fix 2 only if
the composite-decomposition question is being made a headline. Before any of it, apply the
one-line capture fix from §12.8 (accumulate instead of overwrite) so the re-run reports whole-cell
routing rather than a final batch.

**What may be said today, without any of this.** `mole_router` is a **learned static mixture
weight** over an 8-expert bank, not a router: it beats an untuned uniform blend and is
indistinguishable from its own one-hot. That is a defensible, if modest, claim. What may *not* be
said is anything about routing, mixture-of-experts behaviour, or compositional specialisation.

### 12.10 The overnight run (14–15 August): routing was fixed, and it changed nothing

*Added 15 August 2026.* 42 stages, 0 skipped, 224 jobs, ~17.5 h on two GPUs, unattended.
Four experiments landed. Read together they close RQ2 in a way none of them closes alone.

#### The probe: the gate could have routed

§12.9 named two candidate causes for the collapsed gate and they demand different fixes — a
**training** failure (signal present, objective never asked for it) or a **representation**
failure (condition not linearly available in what the gate reads). A linear probe on the
decoder-layer input hidden states settles it:

| | |
|---|---|
| probe accuracy, best layer (4) | **99.4 %** |
| chance (6 conditions) | 16.7 % |
| every layer sampled | > 97 % |

200 programs, **split by `program_id`** (every condition of one program is a near-duplicate, so a
row split would have inflated this to meaninglessness), standardisation fitted on train only.
Condition identity is almost perfectly linearly available. **Training failure. Fixes 1–3 apply;
fix 4 — changing the gate input — is not needed.**

#### The fix worked: routing became real

`routerlora_balanced` = v1 + Switch-style load balancing (α=0.01) + temperature floor (0.5).
Nothing else differs — same bank, data, prompt, seed.

| | v1 | balanced |
|---|---|---|
| TV distance from the grand-mean profile | .011–.056 | **.074–.106** |
| `L1r` expert on the `L1r` cell | .003 | **.080** |
| `S1` expert on the `S1` cell | .013 | **.253** (its top expert) |
| `C_L1r_S1` mass on {L1r, S1} — chance .250 | .019 | **.332** |
| `C_L1b_S1` mass on {L1b, S1} | .149 | **.375** |
| `C_S1_L1r` mass on {S1, L1r} | .016 | **.313** |
| normalised entropy | .151–.180 | .270–.289 |

The mass now tracks what is present rather than a fixed preference: `S1` sits at .243–.253 on
every condition containing S1 and falls to .096–.103 on those without it. Four of six composites
reach or exceed chance. The reports are whole-cell (2.1–4.4 M tokens each), not a final batch.

`C_L2_S4` **fell**, .605 → .383, and that is the correct direction: v1's .605 was the artifact of
L2 and S4 being its fixed favourites on every input. .383 is the honest number.

Not everything recovered. `S3` stays weak (.042–.055) and `L1r` self-routing (.080) is still below
uniform, leaving `C_L1r_S3` (.124) and `C_S4_S3` (.237) under chance.

#### And it bought nothing

**`mole_router_bal` − `mole_router` = +0.4 pts mean, range −1.1 to +1.7** — entirely inside the
1.32 / 3.61 p95 seed band (§8.4).

This was pre-registered in `configs/eval/mole_balanced_qwen1.5b.yaml` as the outcome to watch for,
and it is the one that landed. **Routing correctly is worth nothing on this bank.**

#### LOTO says why

Train on five trainable conditions, evaluate on the held-out sixth, rotate. The diagonal is an
adapter scored on a transform it has never seen.

| | mean over the 6 cells |
|---|---|
| **LOTO diagonal** (never saw that transform) | **38.0** |
| `mono_all` (saw all six) | 39.1 |
| `tuned_L0` (clean code only) | 39.0 |

Holding a transform out costs **~1.1 points — inside seed noise** — and neither multi-condition
adapter beats an adapter that never saw an obfuscated program. §4 found breadth does not help
*within* the trained set; LOTO shows it buys nothing *outside* it either.

#### The merge headroom, for completeness

* **Density was never swept and the default was not optimal.** `dare_ties` runs **47.0 / 44.7 /
  40.5** at d = 0.3 / 0.5 / 0.7 — monotone across all six conditions, so the +2.3 for d=0.3 over
  the long-standing default is a pattern rather than a single lucky cell. `ties` is flat
  (35.5 / 35.9 / 36.3). Every merge conclusion in §5.2 rests on d=0.5.
* **The merge ranking is real.** Rebuilt from the independent seed-42 expert bank:
  `merge_ties` s42−s17 = **−0.0**, `merge_dare_ties` = **+0.6**. The ~9-point gap between the two
  algorithms reproduces across banks — it was never n=1 noise.
* Sanity check: `sweep_dare_ties_d0p5` (44.7) vs `merge_dare_ties` (45.0) are the same merge built
  twice; 0.3 pts apart, consistent with the eval nondeterminism floor of §12.2.

#### What this means for RQ2

The four results eliminate the explanations one at a time. The transform **is** identifiable
(probe, 99.4 %). The gate **can** be made to route on it (balanced, composites above chance). And
routing on it **still** does not pay (+0.4, inside noise). Add yesterday's L0-merge control —
three clean-code adapters merged reach the same `H1` accuracy as six specialists merged — and LOTO,
where holding out a transform costs nothing.

> **The L0-merge control is CROSS-SEED and the arm it controls for is not — added 15 August.**
> Three `L0` adapters can only differ by seed, so that control is built from a near-orthogonal
> bank (cosine 0.05), while `merge_dare_ties` is built from a same-seed bank (0.59). That
> asymmetry is not free: a controlled test — same six conditions, same recipe, only the seed
> assignment altered so mean cosine falls 0.563 → 0.246 — costs `dare_ties` **−3.6 pts**
> [−6.95, −0.30] against the s17 bank and **−4.3** [−7.51, −1.07] against s42, McNemar p<0.001,
> negative on all six conditions, while `ties` is unaffected (−0.4, CI spans zero). Both *pure*
> banks score the same (45.0 s17 / 45.6 s42), so it is the mixing, not adapter quality
> (`configs/eval/crossseed_merge_qwen1.5b.yaml`).
>
> **This makes the claim below conservative, not fragile.** The clean-code control was running
> ~4 points handicapped; seed-matched, it would land *above* the six-specialist merge on `H1`
> rather than level with it. The specialists contribute even less than the headline says. Stated
> explicitly because a reviewer who notices the control is cross-seed will otherwise read it as a
> defect rather than as a bias against our own conclusion.

**The conclusion is not about gates or merge algorithms. The per-condition experts do not carry
distinct transferable knowledge, so no combination strategy can extract value that is not there.**

That is fix 5 of §12.9's ladder, reached by eliminating 1–4 rather than by assuming it, and it is a
considerably stronger claim than "our router underperformed". §5 should be re-scoped around it:
the negative modularity result is a property of the **expert bank**, and the router and merge arms
are the evidence that establishes it rather than the thing that failed.

---

### 12.11 Two attempted repairs (15–17 August), and both are null

*Added 17 August 2026.* §12.10 closed RQ2 negatively by elimination. The obvious objection is that
five things were measured and nothing was attempted as a fix. Two fixes were attempted. Neither
works, and the nulls are tight rather than underpowered.

**The arms.** Both at 1.5B/Python, r32/s17, 3 epochs, selected on their own held-in val slice, then
scored on Grid A (`heldout`, n=1,667) — the same items as `mono_all`, `tuned_L0` and the LOTO folds.

| arm | trained on | rows | why |
|---|---|---|---|
| `s2fam` | S2, S3, S4 | 14,037 | §3.5's `S2`→`H1` is the one replicated positive transfer and was found by accident. This trains for it deliberately: `S3`/`S4` are the two halves of `S2`, so this is the whole inert-material family and nothing else (§4: breadth destroys this transfer). |
| `composite_trained` | 6 stacked `C_*` | 22,152 | Every trainable condition is single-transform; `H1` is not. Stacked variants are the closest proxy for "unseen transform = unfamiliar combination of familiar mechanisms". |
| `composite_ablation` | L1b, L1r, L2, S1, S3, S4 | 22,152 | The same six mechanisms **unstacked**. Without it, "trained on composites" is confounded with "trained on more mechanisms" and the arm answers nothing. |

| system | L0 | L1b | L1r | L2 | S1 | S2 | **mean** |
|---|---|---|---|---|---|---|---|
| `base` | 21.7 | 18.8 | 18.7 | 19.8 | 20.7 | 15.3 | 19.18 |
| `tuned_L0` — **4,689 rows** | 44.7 | 34.3 | 36.7 | 37.8 | 39.0 | 41.8 | **39.04** |
| `mono_all` — 26,841 rows | 41.6 | 38.1 | 36.7 | 37.9 | 39.2 | 41.5 | **39.15** |
| `s2fam` | 44.4 | 32.0 | 36.6 | 36.8 | **41.4** | **43.8** | **39.16** |
| `composite_trained` | 39.8 | 37.9 | 37.8 | 37.3 | 38.3 | 39.7 | **38.46** |
| `composite_ablation` | 42.3 | **38.6** | 37.7 | 37.9 | 39.5 | 42.8 | **39.81** |

Cluster bootstrap by `program_id`, 2000 draws, seed 17:

| contrast | Δ pts | 95 % CI | verdict |
|---|---|---|---|
| **stacked − unstacked** (the B2 question) | **−1.36** | [−2.63, +0.04] | null, and the sign runs *against* the hypothesis |
| **`s2fam` − `tuned_L0`** (the B1 question) | **+0.02** | [−0.95, +1.02] | null, and unusually tight |
| `composite_ablation` − `tuned_L0` | +0.77 | [−0.46, +2.03] | null |
| `s2fam` − `mono_all` | −0.07 | [−1.39, +1.12] | null |

**Three things to take from it.**

1. **Most of these columns are OOD, so this is a generalization result.** `s2fam` never saw
   L0/L1b/L1r/L2/S1; `composite_trained` never saw *any* single transform. The means are honest
   unseen-transform measurements, not in-distribution accuracy.
2. **The per-condition shape reproduces the thesis exactly.** `s2fam` tops the `S2` column (43.8)
   and the `S1` column (41.4) — the structural family it trained on — and is the *worst* row on
   `L1b` (32.0). Wins where it trained, nowhere else, net zero. Training *for* the mechanism
   reproduces the mechanism's locality rather than escaping it.
3. **`tuned_L0` at 4,689 rows is still indistinguishable from every multi-condition adapter**,
   including one with 5.7× the data. Whatever binds this task, it is not training-set size and it
   is not obfuscation exposure.

**What this does NOT show.** §3.5's `S2`→`H1` is a claim about `H1`, and `H1` is deliberately unread
here (CLAUDE.md §3.2 rule 2 — these arms were still being selected). So the curriculum is flat on
the *trainable* ladder; whether it reaches the held-out obfuscator is the question it was built for
and is still open. That read is the decisive remaining item and belongs in the one batched
confirmatory pass, alongside the density-sweep and seed-42 reads already owed.

**Caveats.** Single seed per arm, so ~1-point differences sit inside the 1.32-pt mean seed band.
`s2fam` carries a 37 % data deficit (14,037 vs 22,152) because that is the realised S2+S3+S4 train
pool — pre-registered as making a *win* interpretable and a *loss* unattributable; the observed
result is neither, it is flat.

---

### 12.12 Redundancy, geometry, and the third repair (15–17 August)

*Added 27 August 2026.* §12.10 closed RQ2 by elimination and §12.11 showed two repairs are null.
Two soft spots remained: nobody had checked whether the systems fail on the **same items**, and the
geometry diagnostics §5.3 rests on had only ever been computed on two of six adapter banks.

**Experiment 1 — the systems are redundant, not complementary.** On `H1`, the best merge and a
single clean-code adapter score the same. A tie in the *margin* says nothing about the *overlap*: if
they succeed on different items, distinct capability exists and merely isn't extractable, which
would soften the whole conclusion. `scripts/analysis/24_item_agreement.py` computes pairwise 2×2
concordance, exact McNemar, Jaccard, and the oracle-of-k.

**The trap this had to avoid.** An oracle-of-k rises mechanically with k — *k* independent coins at
1/3 each cover 1−(2/3)^k of the items — so a raw "oracle headroom" invites exactly the wrong
conclusion. The script therefore computes a **permutation null that preserves every system's
marginal accuracy exactly and destroys only the item-difficulty coupling.** Real systems are
positively coupled, so the observed oracle should sit *below* that null; how far below is the
measure of redundancy.

| | Grid A `H1` (n=1,214, 10 systems) | Grid B `H1` (n=115, 7 systems) |
|---|---|---|
| best single | 28.0 % (`tuned_S2_s17`) | 34.8 % (`merge_dare_ties`) |
| oracle-of-k | 39.0 % | 48.7 % |
| raw "headroom" | +11.0 pts | +13.9 pts |
| **independence null** | **91.9 %** [90.5, 93.2] | **93.6 %** [89.6, 97.4] |
| **observed − null** | **−52.9 pts** | **−44.9 pts** |
| mean pairwise φ | +0.621 | +0.625 |
| items solved by **no** system | 740 / 1214 (61 %) | 59 / 115 (51 %) |
| items solved by **every** system | 40 | 17 |

The headline pair is a clean null on its own: `merge_dare_ties` × `tuned_L0_k0` is
both-34 / merge-only-5 / L0-only-6 / neither-70, **McNemar p = 1.000**. The distribution is bimodal
— items are solved by everything or by nothing. **This hardens the negative result rather than
softening it, and the raw headroom must never be quoted without the null.** One signal survives:
`tuned_S2_s17` is both the most accurate system on `H1` and the specialist with the most sole-solved
items (16), which is what pointed at §15 and §16.

**Experiment 2 — the geometry diagnostic measures initialization, not knowledge.** Covering the
remaining four adapter banks (CPU only; the script needed one additive `--seeds` flag) produced the
result that reframes §5.3. *(Full treatment, including the cross-seed bank's sign conflict and the
four probes of geometry-as-predictor, is [§14](#14-task-vector-geometry--the-whole-thread-and-what-it-turned-out-to-measure).)*

| bank | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
|---|---|---|---|---|
| `L0` at seeds {17, 42, 101} — **byte-identical training data** | **0.053** | **0.487** | 0.765 | 0.374 |
| 8 specialists at seed 17 — **completely different transforms** | **0.592** | 0.390 | 0.861 | 0.371 |
| 6 specialists at seed 42 | 0.575 | 0.388 | 0.845 | 0.370 |
| 6 LOTO folds at seed 17 | 0.576 | 0.382 | 0.849 | 0.804 |

Individual `L0` cross-seed pairs: 0.0533 / 0.0531 / 0.0539. Same-seed `L0|S3`: 0.697.

**Three adapters trained on identical data are near-orthogonal, while eight adapters trained on
completely different transforms are 0.59-aligned.** LoRA initialises `A` randomly and `B` at zero,
so each seed selects a different rank-32 subspace; same-seed adapters share it and drift together.
Three consequences:

1. **Every §5.3 geometry figure is same-seed**, so it measures *drift within one shared subspace*,
   not how different the experts' knowledge is — which is how the Horoi framing reads it. The
   observations stand; the interpretation does not.
2. **Sign conflict demonstrably does not bound merged accuracy.** The L0-merge control is built
   from that near-orthogonal bank — the worst geometry in the project — and merges *fine*. A merge
   at maximal sign conflict lost nothing, so the diagnostic's premise fails.
3. **Any geometry→accuracy regression must be stratified by seed.** Same-seed and cross-seed merge
   points live in different geometric regimes; pooling them fits a line through an artifact.

**The LOTO folds are effectively one vector.** Each trains on five of six transforms; mean cosine to
the other five spans only **0.565–0.583** and norms 0.7998–0.8099. *Dropping an entire transform
from a five-condition mixture moves the update less than the spread between folds* — §12.10's
conclusion visible directly in weight space, which nothing had shown before.

**Experiment 3 — merging is algorithm-specifically sensitive to geometry.** Rebuild the merge with
each specialist drawn from a *different* seed (mean cosine 0.563 → 0.246), everything else held:
**`dare_ties` loses 3.6–4.3 pts** (CI excludes zero, McNemar p<0.001, negative on all six
conditions) while **`ties` loses 0.4** (CI spans zero). Both *pure* banks are equivalent (45.0 at
s17 vs 45.6 at s42), so it is the mixing, not adapter quality. **Consequence: the L0-merge control
is necessarily cross-seed and was therefore ~4 pts handicapped against the same-seed arm it
controls for** — which makes §12.10's reading *conservative*.

**Experiment 4 — the third repair, and the density that was never swept.** Merge density had never
been swept and 0.5 is not optimal: `dare_ties` scores **47.0 / 44.7 / 40.5** as a mean over the six
trainable conditions at density **0.3 / 0.5 / 0.7**, monotone across all six. **But the headroom
does not reach `H1`** — the `d=0.3` merge reads **32.2** on Grid B `H1` against `merge_dare_ties`'
34.8. The condition it was tuned on improves; the held-out one does not.

The `residual_*` arms preserve the condition-specific residuals at full magnitude instead of
diluting them. On Grid A `H1`, recomputed 27 August:

| contrast | Δ | 95 % CI | |
|---|---|---|---|
| `residual_n6_s17_d0p5` − `uniform_n8_s17_d0p5` | **+2.80** | [+1.07, +4.69] | significant |
| `residual_n6_s42_d0p5` − `uniform_n8_s17_d0p5` | **+2.55** | [+0.99, +4.13] | significant |
| `residual_n6_s17_d0p5` − **`tuned_L0`** | +1.32 | [+0.00, +2.80] | marginal |
| residual weighting, same-bank s42 replicate (pre-registered contrast) | +0.74 | [−0.74, +2.06] | **null** |

**The verdict is three-part and none of it changes the thesis.** The residual weighting is *real and
small*; it **does not replicate** on an independent expert bank; and it **does not beat the
clean-code control** by more than a marginal point, while `tuned_S2_s17` (28.0) still beats every
merge in the project. A ~2-point improvement to *merging* that leaves the invariance question
untouched — the "bounded rather than promising" reading, registered in advance.

---

### 12.13 RQ2, closed

*Added 27 August 2026.* The thread ran 2026-08-05 → 2026-08-17: **110 combination systems, 1,208
cells, 393,997 graded trials.** Full self-contained account in
[`MASTER_REPORT_2026-08-27_router-and-merging.md`](MASTER_REPORT_2026-08-27_router-and-merging.md);
this is the summary in project context.

Each candidate explanation for the failure was eliminated by a purpose-built experiment rather than
argued away:

| candidate explanation | eliminated by | the number |
|---|---|---|
| "the merge algorithm is wrong" | three algorithms + density sweep + cross-seed control | best merge −0.66 vs control; best density does not transfer to `H1` |
| "merging is the wrong operator; route instead" | perfect hard router | 1.000 dispatch accuracy, gain on 1 of 6 conditions, **undefined on `H1`** |
| "the gate is badly trained" | balanced gate | routing became real (TV .056 → .106), **accuracy +0.4** |
| "the condition isn't visible to the gate" | linear probe on the gate's own input | **99.4 %** vs 16.7 % chance |
| "training on more transforms would generalise" | LOTO, six folds | holding one out costs ~1.1 pts, inside noise |
| "the experts are over-trained and interfere" | uniform-epoch geometry sweep | mechanism reproduces (0.401 → 0.425), accuracy *improves* on 11/12 pairs |
| "geometry is the constraint" | L0-merge bank | worst geometry in the project merges fine |
| "capability exists but isn't extractable" | item agreement + permutation null | oracle-of-10 **52.9 pts below** the null; 61 % of items solved by nothing |
| "the training side can repair it" | three pre-registered repairs | +0.02, −1.36, +0.74 |

**The headline panel, Grid A `H1`, n = 1,214 (recomputed 27 August; paired cluster bootstrap by
`program_id`, 2,000 resamples, seed 17):**

| system | `H1` % | vs `tuned_L0` | 95 % CI | |
|---|---|---|---|---|
| `tuned_S2_s17` — **one specialist** | **28.01** | **+3.46** | [+2.06, +4.94] | **beats the control** |
| `s2fam` | 26.61 | +2.06 | [+0.08, +4.13] | marginal |
| `residual_n6_s17_d0p5` | 25.86 | +1.32 | [+0.00, +2.80] | marginal |
| `merge_dare_ties_s42` | 24.88 | +0.33 | [−1.07, +1.73] | null |
| **`tuned_L0` — THE CONTROL** | **24.55** | — | — | |
| `merge_dare_ties` — headline merge | 23.89 | −0.66 | [−1.89, +0.66] | null |
| `mono_all` | 22.90 | −1.65 | [−3.79, +0.49] | null |
| `l0merge_dare_ties` — 3× clean-code merge | 21.42 | **−3.13** | [−4.78, −1.40] | **worse** |
| `merge_ties` | 19.52 | **−5.02** | [−7.26, −2.72] | **worse** |
| `composite_trained` | 19.36 | −5.19 | — | |
| `base` | 6.43 | −18.12 | — | |

**The mechanism, and the sentence that replaces §12.10's.** Two offsetting effects of nearly equal
size that Grid B could not separate:

1. **Merging costs ~3.1 pts** — three clean-code adapters merged score 21.4 against a single one's
   24.5. In a bank with no specialist knowledge to lose, this isolates the cost of the *operation*.
2. **Specialists recover ~2.5 of it** — the six-specialist merge beats that control by +2.47
   [+1.32, +3.70], q = 0.0001.

Net: −0.66, null. **"The per-condition experts carry nothing distinct" is too strong and is
retired.** They carry something worth +2.5 points into a merge; it is simply cancelled by what
merging costs. The defensible statement is narrower and more interesting:

> **Combination methods pay a dilution cost that is about the size of the specialist contribution
> they are trying to exploit, so the net is a wash — and the specialists are redundant at the item
> level, so no combination strategy recovers more than the best single member.**

**What survives.** Three results and two artifacts. (1) `S2`→`H1` is real, replicated, confirmed at
power, and **every combination method destroys it** — the best merge is 4.12 points below the `S2`
specialist [+2.55, +5.77]. (2) The two offsetting effects in merging, measured separately — a
transferable statement about LoRA merging with nothing to do with obfuscation. (3) Task-vector
geometry is dominated by LoRA initialization. Artifacts: the **CPU-only task-vector diagnostic**
(`⟨ΔWᵢ,ΔWⱼ⟩ = sᵢsⱼ·tr((BᵢᵀBⱼ)(AⱼAᵢᵀ))`, verified against dense to 5.6e-16) and the **permutation
null for oracle-of-k**.

**Consequences for `paper_modularity/`.** `CLAIM_LADDER.md` Branches **B, C and D are dead** — B
needed the composite gate effect to survive at corpus scale and the mixture ladder turned out to
carry two copies of the same control (§12.10); C needed geometry to predict merged accuracy and
§12.12 refutes the premise; D needed under-trained experts to be harder to route and easier to
merge, and the uniform-epoch sweep shows merged accuracy *rising* with training. **The draft's empty
thesis slot should be filled with Branch A**, "modularity does not rescue robustness", which is
fully supported by what is on disk.

---

## 13. Glossary

Everything the tables above assume, in one place.

**The task and the conditions**

| term | meaning |
|---|---|
| **output prediction** | Given a self-contained function and one concrete input, predict the exact return value. No explanation, just the value. Graded by running the code, so there is no grader subjectivity. |
| **condition** | One obfuscation applied to the clean original. Always a *single* transform, never stacked, and verified to preserve semantics by executing the variant against its parent's inputs plus ~20 fuzzed ones. |
| **`L0`** | The clean original (comments and docstrings stripped). Not obfuscated. |
| **`L1b`** | *Adversarial* renaming — identifiers replaced with actively misleading ones (a Fibonacci function renamed `smoothArea`). |
| **`L1r`** | Random renaming — identifiers become meaningless hex (`v_a3f2`). |
| **`L2`** | Minification — identifiers become `a`, `b`, `c`…, type annotations stripped. |
| **`S1`** | Control-flow flattening — the function body becomes a dispatch loop over a state variable, so the original `if`/`for` structure disappears. |
| **`S2`** | Opaque predicates + dead code — guards that always take the same branch, plus helpers that are never called. |
| **`S3` / `S4`** | The two halves of `S2` on their own: dead code only (`S3`), opaque predicates only (`S4`). |
| **`H1`** | **The held-out obfuscator** — string encoding + mixed boolean-arithmetic rewriting. Never trained on by anything, quarantined behind four enforcement layers. It is the discriminator: a model that handles `H1` learned the *class* of meaning-preserving rewrites; one that doesn't, memorised the specific transforms it saw. |

**The systems**

| term | meaning |
|---|---|
| **base** | The untouched pretrained model, no fine-tuning. |
| **LoRA adapter** | A small trainable weight patch (~0.5 % of model size) added to the frozen base model — the cheap standard way to fine-tune. "Rank 32" is the size of its low-rank bottleneck; more rank = more capacity. |
| **specialist** (`tuned_<c>`) | An adapter trained on one condition only. |
| **`L0`-only control** | An adapter trained only on *clean* code. **The reference for every number in this report.** Against the untuned base every adapter looks excellent, because the base is weak at the task itself — only the gap to a clean-code-trained adapter isolates what *obfuscation* training buys. |
| **monolithic / `mono_*`** | One adapter trained on all five obfuscation types at once. `mono_r64/r128/r192` are the same thing at larger rank. |
| **`ctl_r64`** | The `L0`-only control at rank 64 — used as a noise floor, since raising the control's own capacity should change nothing. |
| **routed / merged / oracle prompt** | The three RQ2 combination strategies — see §5.0. |

**The measurements**

| term | meaning |
|---|---|
| **control-relative delta** | Accuracy of a system minus accuracy of the `L0`-only control, on the same items, in percentage points. The headline metric everywhere in this report. |
| **transfer ratio (TR)** | For an adapter trained on *i* and evaluated on *j*: the fraction of condition *j*'s own specialist's gain that adapter *i* reproduces. TR = 1 means "transfers perfectly"; TR = 0 means "transfers nothing". Undefined when the denominator is under 3 points, because that is noise divided by noise. |
| **Invariance Index** | The project's headline quantity — mean TR onto `H1`. It has no valid value here, since an `H1` specialist cannot exist by construction (§3.4). |
| **common subset** | The programs that survived *every* condition. Used for all headline numbers so that no cell is confounded by a different set of programs — `S1` and `H1` decline some programs by design ("correctness beats coverage"), so per-condition full sets differ. |
| **cluster bootstrap by program** | The confidence-interval method: resample whole *programs* with replacement, not individual items. Several eval items come from the same program and are correlated; bootstrapping items would understate the intervals. |
| **BH-FDR** | Benjamini–Hochberg false-discovery-rate correction, applied across a whole family of comparisons at once (e.g. the entire transfer matrix), so that testing 42 cells doesn't manufacture significance. |
| **`*` in a table** | The effect passed BH-FDR at q<0.05 *and* its bootstrap interval excludes zero. Both, not either. |
| **format-failure rate** | Fraction of answers that could not be parsed into a candidate value at all — a system failing to answer, as distinct from answering wrongly. |
| **Grid A / Grid B** | The two disjoint evaluation program sets — see §2. Never pooled. |
| **task vector (ΔW)** | The weight change an adapter represents, ΔW = (α/r)·B·A. Exact for vanilla LoRA (no DoRA, no rsLoRA), which is what makes the arithmetic in §5.3 and §7.7 valid rather than approximate. |
| **sign conflict** | Fraction of weight coordinates where two experts' task vectors disagree in sign. TIES resolves such conflicts by deleting the losing side, so a higher rate means more of the update is thrown away when merging. The mechanism Horoi et al. blame for merge failure (§5.3). |
| **TIES keep rate** | Fraction of task-vector magnitude that survives TIES' sign election. The complement of what merging discards. |
| **operating point (λ\*)** | In §7.7, the amount of forward task vector subtracted at which forward performance falls back to the untuned base level. Only at that point is "what happened to reverse" a meaningful question — before it, forward has not actually been removed. |
| **over-removal** | Reverse capability lost beyond what exact unlearning would cost: `Rev(REV) − Rev(FLIP→U)`. The proposed shared-representation signature. Its control (§7.7) shows the same loss in an arm with no forward direction to remove, which is why the reading was withdrawn. |
| **composite condition (`C_`)** | A variant built by stacking two transforms (e.g. `C_L1r_S1` = rename, then flatten). Deliberately outside the trainable ladder so it cannot shift RQ1. Used in §5.4 because it is the only case where no single expert is correct. |
| **activation-space mixture** | Combining experts at inference as `h = Wx + Σ aₑ(x)·(α/r)·Bₑ Aₑ x` rather than by averaging weights. Exact, needs no per-item merge, and does not grow rank — see §5.4. |

---

## 14. Task-vector geometry — the whole thread, and what it turned out to measure

*Added 27 August 2026.* Geometry appears three times in this report — §5.3 (the over-training
hypothesis), §12.12 (the initialization finding), §12.13 (the reusable artifact) — because it was
run three times for three different reasons. This section consolidates all of it, adds the
cross-seed bank's sign conflict and the stratified geometry→accuracy comparison that §9 listed as
owed, and states plainly what the diagnostic does and does not measure.

**The short version.** The project adopted task-vector geometry as a *predictor* of merge quality,
on the strength of a published mechanism. The mechanism reproduces. The prediction fails in every
direction it was tested: **sign conflict** does not bound merged accuracy, it correlates with accuracy
in the **wrong sign** within a bank, and the one algorithm it is supposed to describe (TIES, which
deletes sign-conflicting coordinates) is the one that is *insensitive* to it. And what the diagnostic
actually measures, in its usual same-seed form, is **shared LoRA initialization**.

**But the direction is not a dead end, because a different quantity works.** The **surviving
task-vector norm** ‖ΔW‖ predicts merged accuracy at **Spearman ρ = +0.86** over 17 merges (§14.4b),
explains the 9-point TIES vs DARE-TIES gap that §5.2 left open, and diagnoses the DARE-linear
catastrophe from the weights alone. It costs less to compute than sign conflict. **The problem was
never that geometry cannot predict merge quality; it is that the field measures the wrong thing.**

### 14.1 What a task vector is here, and how it is computed

A LoRA adapter stores two low-rank factors. The weight change it represents — its **task vector** —
is

> ΔW = (α / r) · B · A

for each of the 196 adapted modules (28 layers × 7 projections). Four quantities are reported:

| quantity | definition | why it is here |
|---|---|---|
| **‖ΔW‖** | mean Frobenius norm per module | how far the expert moved from base |
| **cosine(ΔWᵢ, ΔWⱼ)** | mean pairwise angle between two experts' task vectors | 1.0 = same direction, 0 = orthogonal |
| **sign conflict** | fraction of weight coordinates where two experts disagree in sign | **TIES deletes exactly these**, so it is the mechanistically motivated one |
| **TIES keep rate** | fraction of update *magnitude* surviving the sign election | what actually reaches the merged adapter |

**The computational trick that made the sweep possible.** Materialising ΔW densely for 8 experts ×
9 epochs × 196 modules is intractable on CPU. But Frobenius inner products need no dense ΔW:

> ⟨ΔWᵢ, ΔWⱼ⟩ = sᵢ·sⱼ·tr( (Bᵢᵀ Bⱼ)(Aⱼ Aᵢᵀ) )

which contracts through the **r × r** bottleneck instead of the full weight matrix. Verified against
the dense computation to **5.6 × 10⁻¹⁶**. That turns the entire sweep into seconds of CPU and no
GPU, and it is the reason the geometry study cost nothing — every checkpoint was already on disk.
`src/obtune/merge_geometry.py`, driver `scripts/merge/20_geometry_report.py`.

**One quantity resists it.** Sign conflict is coordinate-wise, so it *does* need a materialised ΔW.
It is therefore computed on a representative slice — layers **{0, 7, 14, 21, 27}**, 35 modules —
rather than all 196. Every sign-conflict number in this report carries that sampling.

### 14.2 Every bank measured

Six banks, all at the final checkpoint, `qwen25c-1.5b` / Python / r32.

| bank | what it is | pairs | mean cosine | sign conflict | TIES keep | ‖ΔW‖ |
|---|---|---|---|---|---|---|
| **8 specialists @ s17** | the bank §5.2's merges are built from | 28 | **0.592** | 0.390 | 0.861 | 0.371 |
| 6 specialists @ s42 | the independent replicate bank | 15 | 0.575 | 0.388 | 0.845 | 0.370 |
| 6 specialists @ s17 | the same-seed arm the cross-seed control targets | 15 | 0.563 | 0.394 | 0.840 | 0.354 |
| **6 specialists, alternating s17/s42** | the **cross-seed control** — same conditions, same recipe, only the seed assignment altered | 15 | **0.246** | **0.565** | **0.638** | 0.353 |
| **3 × `L0` @ s17/s42/s101** | **byte-identical training data**, three seeds | 3 | **0.053** | **0.487** | 0.765 | 0.374 |
| 6 LOTO folds @ s17 | each trained on five of six conditions | 15 | 0.576 | 0.382 | 0.849 | **0.804** |

*(The cross-seed row's sign conflict and TIES keep were computed 27 August 2026 and are new — the
15 August readout reported only its cosine. They are the numbers §14.4 turns on.)*

**The line that reframes everything below it:** three adapters trained on *byte-identical data* are
near-orthogonal (**0.053**), while eight adapters trained on *completely different transforms* are
**0.59**-aligned. LoRA initialises `A` randomly and `B` at zero, so each seed selects a different
rank-32 subspace. Same-seed adapters share that subspace and drift together; different-seed adapters
never enter the same one. **Same-seed cosine measures a shared subspace plus common drift, not
shared knowledge.** Individual `L0` cross-seed pairs: 0.0533 / 0.0531 / 0.0539 — a tight, boring
band, which is what an initialization artifact looks like.

### 14.3 Within a fixed seed, the *relative* geometry is still meaningful

The absolute level is initialization, but the ordering is not noise. On the 8-expert s17 bank
(28 pairs, range 0.457–0.698):

| closest pairs | cosine | | furthest pairs | cosine |
|---|---|---|---|---|
| `S2 \| S3` | **0.698** | | `L1b \| S1` | **0.457** |
| `L0 \| S3` | 0.697 | | `L2 \| S1` | 0.465 |
| `L0 \| S4` | 0.694 | | `L1r \| S1` | 0.465 |
| `S2 \| S4` | 0.691 | | `S1 \| S3` | 0.516 |

**The inert-material family is the tightest cluster in the bank, and it is the closest to the
clean-code direction.** `S2`, `S3` and `S4` sit at 0.69–0.70 with each other and with `L0` — which
is exactly the family §15 and §16 show is learning "ignore what cannot matter", a skill that leaves
clean-code behaviour intact. And **`S1` is the outlier from every identifier transform** (0.457–0.465
against `L1b`/`L1r`/`L2`): control-flow flattening moves the model somewhere the renaming conditions
do not go. The `s42` bank reproduces the same shape — `L1b|S1` 0.453, `L2|S1` 0.469, `L1r|S1` 0.471.

`S1` also has the smallest norm in the bank (**0.331** against 0.372–0.381 for everything else),
which is a data-volume effect rather than a geometric one: `S1` bails on short function bodies by
design, so it trains on fewer rows.

**Where in the network the conflict lives.** Sign conflict is not uniform across projections:

| projection | sign conflict (s17 bank) | TIES keep | drift e1 → e9 |
|---|---|---|---|
| `q_proj` | **0.426** (highest) | 0.834 | +0.0153 |
| `k_proj` | 0.408 | 0.847 | +0.0251 |
| `down_proj` | 0.407 | 0.850 | **+0.0531** (largest) |
| `gate_proj` | 0.399 | 0.856 | **+0.0044** (smallest) |
| `up_proj` | 0.378 | 0.870 | +0.0170 |
| `o_proj` | 0.364 | 0.880 | +0.0289 |
| `v_proj` | **0.352** (lowest) | **0.888** | +0.0267 |

Attention query/key projections disagree most between experts; value and output projections agree
most. Under prolonged training the interference concentrates in `down_proj` — it drifts **12×** as
much as `gate_proj` over nine epochs.

### 14.4 The test that matters: does geometry predict merged accuracy?

Four independent probes, and the diagnostic fails all four.

**Probe 1 — the cross-seed control (the cleanest test in the section).** Take the same six
conditions, the same merge recipe, the same density; change *only* which seed each expert is drawn
from. Geometry moves a long way; adapter quality does not (the two pure banks are equivalent, 45.0
at s17 vs 45.6 at s42). Grid B, mean over the six trainable conditions:

| | same-seed s17 | cross-seed | change |
|---|---|---|---|
| mean cosine | 0.563 | 0.246 | **−56 %** |
| sign conflict | 0.394 | 0.565 | **+43 %** |
| TIES keep rate | 0.840 | 0.638 | **−20 pts of magnitude discarded** |
| **`ties` merged accuracy** | 36.17 | 35.77 | **−0.40** |
| **`dare_ties` merged accuracy** | 44.95 | 41.33 | **−3.62** |

**Read the last two rows against the third.** One fifth of the update magnitude is additionally
thrown away by the sign election, and **TIES — the algorithm that performs that election — loses
0.4 points.** DARE-TIES, which randomly drops 50 % of coordinates and rescales *before* the
election, loses 3.6. So the algorithm the diagnostic is a theory of is the one that does not care,
and the sensitivity lives in the stochastic-dropout stage instead. Whatever cross-seed mixing costs,
it is not the mechanism sign conflict names.

**Probe 2 — the `L0`-seed bank merges at maximal disorder.** The three-clean-code-adapter control
has the worst geometry in the project: cosine 0.053, sign conflict 0.487 (a coin flip), TIES keep
0.765. It merges **fine** — `l0merge_dare_ties` scores 33.9 on Grid B `H1`, identical to a single
`tuned_L0`, and 40.2–41.7 as a mean over the trainable ladder, *above* both same-seed `ties` merges.
A merge at near-maximal sign conflict lost nothing.

**Probe 3 — within-bank, across training length, the correlation has the wrong sign.** The 8-expert
bank merged at four checkpoints, with the bank's own geometry at each:

| epoch | cosine | sign conflict | TIES keep | ‖ΔW‖ | `ties` acc | `dare_ties` acc |
|---|---|---|---|---|---|---|
| 1 | 0.580 | 0.401 | 0.853 | 0.291 | 35.26 | 43.21 |
| 3 | 0.533 | 0.417 | 0.840 | 0.517 | 35.96 | 45.09 |
| 6 | 0.514 | 0.425 | 0.834 | 0.610 | 36.00 | 46.28 |
| 9 | 0.514 | 0.425 | 0.834 | 0.617 | 36.85 | 46.38 |

Correlation between sign conflict and merged accuracy: **+0.84** (`ties`), **+0.998**
(`dare_ties`). Interference rises monotonically and accuracy rises with it.

> **The honest caveat, and it is a real one.** Epoch drives both sign conflict *and* ‖ΔW‖ (0.291 →
> 0.617), so this is confounded and the correlation with norm would be equally strong. It does
> **not** establish that conflict helps. What it does establish is the weaker, sufficient claim:
> **sign conflict does not bound merged accuracy**, because accuracy went up while it rose.

**Probe 4 — the stratified regression, and why it should not be run.** §12.12 asked for a
geometry→accuracy regression over the ~45 merge points on disk, stratified by seed. Assembling the
points shows the request cannot be met: the merges cluster into **four** distinct geometric regimes
(same-seed s17, same-seed s42, cross-seed, `L0`-seeds), and *within* the two same-seed regimes the
geometry is nearly constant (cosine 0.563 vs 0.575, sign conflict 0.394 vs 0.388) while accuracy
varies by 9 points between algorithms. A line fitted across regimes would be estimated almost
entirely from the between-bank contrast — i.e. from **four** effective observations, three of which
differ in what they merge as well as how. **The comparison is a four-row table, not a regression,
and this section reports it as one.** Recording that is the resolution of the open item; pretending
otherwise would produce a slope with a confidence interval and no identification behind it.

### 14.4b The quantity that *does* predict merged accuracy is the surviving norm

*Added 27 August 2026, and it resolves two open items.* Every probe above tests **sign conflict**,
because that is what the literature's mechanism is about. Computing ‖ΔW‖ for all 136 adapters that
have one — a few minutes of CPU on safetensors already on disk — shows the predictive signal was in
the other quantity all along.

A single specialist sits at **0.30–0.38**. The merges do not:

| merge | ‖ΔW‖ | × a single expert | Grid B mean (6 trainable) |
|---|---|---|---|
| `sweep_dare_ties_d0p3` | 0.567 | 1.56× | **47.03** |
| `dl_rescaled` (the repaired DARE-linear) | 0.282 | 0.78× | 45.52 |
| `residual_dare_ties_d0p5` | 0.267 | 0.74× | 45.82 |
| `merge_dare_ties_s42` | 0.231 | 0.64× | 45.59 |
| **`merge_dare_ties`** | **0.226** | **0.62×** | **44.95** |
| `crossseed_dare_ties` | 0.245 | 0.67× | 41.33 |
| `sweep_dare_ties_d0p7` | 0.115 | 0.32× | 40.53 |
| `l0merge_ties` | 0.197 | 0.54× | 40.19 |
| `residual_ties_d0p5` | 0.082 | 0.22× | 36.74 |
| **`merge_ties`** | **0.069** | **0.19×** | **36.17** |
| `sweep_ties_d0p3 / d0p5 / d0p7` | 0.066 / 0.069 / 0.064 | ~0.18× | 35.54 / 35.89 / 36.29 |
| `crossseed_ties` | 0.089 | 0.24× | 35.77 |

**Over the 17 well-scaled merges: Spearman ρ = +0.86 (p = 9.5 × 10⁻⁶), Pearson r = +0.78.** Sign
conflict predicts nothing across the same points; the surviving magnitude predicts almost everything.

**This closes the ~9-point TIES vs DARE-TIES gap that §5.2 recorded as unexplained.** TIES keeps
0.19× a single expert's update; DARE-TIES keeps 0.62× — **3.3× more surviving signal** — and the
accuracy ordering follows. It also closes the 2026-08-10 open item recorded verbatim as *"Election
retains 86 % of mass, but `merge_ties`' ‖dW‖ is 0.19× a single expert's. Still unexplained."* The
two numbers are not in tension: the sign election retains 86 % of *magnitude per surviving
coordinate*, but averaging six experts whose task vectors are only 0.56-aligned cancels most of the
vector sum. Retention and magnitude are different quantities, and only the second one matters.

**The density sweep is the within-algorithm confirmation.** For `dare_ties`, density 0.3 / 0.5 / 0.7
gives ‖ΔW‖ 0.567 / 0.226 / 0.115 and accuracy 47.03 / 44.71 / 40.53 — **monotone in both, together.**
For `ties`, the norm barely moves across densities (0.066 / 0.069 / 0.064) and neither does accuracy
(35.54 / 35.89 / 36.29). The algorithm whose norm responds to the knob is the algorithm whose
accuracy responds to it.

**And the relationship is not "bigger is better" — it is "match a single expert's scale."**
`merge_dare_linear` has ‖ΔW‖ = **2.024**, *5.6× a single expert*, and scores **4.02** — the
catastrophic arm of §5.2. Include it and Pearson r flips to −0.75. That is the boundary condition
that makes the story coherent rather than a fitted line: the repair, `dl_rescaled`, works precisely
by bringing the norm back to 0.282 (0.78×), whereupon accuracy recovers to 45.52. **A merged adapter
has to land at roughly the magnitude of one expert; both far below and far above are broken.**

> **What this is and is not.** It is descriptive, not causal — norm and accuracy are both downstream
> of "how much of the experts survived the merge", and the density knob moves both by construction.
> It does **not** overturn §12.13: the best-normed merge still does not beat the clean-code control
> on `H1` (`sweep_dare_ties_d0p3` reads **32.2** on Grid B `H1` against `merge_dare_ties`' 34.8), so
> retaining more magnitude buys accuracy on the *trained* conditions and nothing on the held-out
> one. What it changes is §14's verdict on the diagnostic: **it is not that task-vector geometry
> fails to predict merge quality — it is that the field's chosen statistic is the wrong one.** A
> quantity that takes seconds to compute, needs no pairs, and correlates at ρ = 0.86 was sitting
> beside the one that correlates at nothing.

### 14.5 The over-training hypothesis, in its final state

Horoi, Wolf, Belilovsky & Dziugaite (arXiv:2506.14126v2) argue that training an expert to its
*individual* optimum is dominated late in training by memorisation, producing negative parameter
interference that degrades merging; their recommendation is aggressive early stopping. That
described this project's procedure exactly — `run_ckpt_select` picks `best` by held-in validation
accuracy, and every merge in §5.2 is built from `best`.

**Verdict: the mechanism reproduces and the consequence inverts.**

- **Mechanism, present.** On the 8-expert bank with epochs held uniform, sign conflict rises
  0.401 → 0.425 over nine epochs, the task vector doubles in norm (0.291 → 0.617), and the experts
  rotate apart (cosine 0.580 → 0.514). It plateaus around epoch 6.
- **Not present in our operating regime.** On the 3-epoch bank the same statistic *falls*
  (0.402 → 0.391) and TIES retention *rises*. `trainer_state.json` says why — training loss is still
  falling steadily at epoch 2.5 (0.90 → 0.31 over 219 steps). **Our experts are under-trained
  relative to where the effect appears**, so the bank §5.2 merges cannot test the claim at all.
- **Consequence, inverted.** Merged accuracy *improves* on 11 of 12 method × condition pairs as the
  experts train longer; pooled e9 − e1 = **+3.1 [+0.0, +6.1]** for `dare_ties`. Training the experts
  longer made the merge better.

**A confound this uncovered, which affects every merge in §5.2.** `ckpt_select` chose *different*
epochs per condition — `L1r`/`S3` at epoch 1, `L0`/`L1b` at 2, `L2`/`S2`/`S1`/`S4` at 3. Every merge
in the original RQ2 grid therefore combines task vectors of unequal training. The uniform-epoch
sweep was run specifically to remove it, and both of §5.3's original caveats (3-vs-8 experts,
unequal epochs) are now discharged.

### 14.6 Geometry as evidence *for* the RQ2 conclusion

One geometry result is not a null, and it is the most direct evidence in the project for the
redundancy claim. The six **LOTO folds** each train on five of the six conditions. Their pairwise
cosine spans only **0.559–0.607** and their norms **0.7998–0.8099**:

> **Dropping an entire transform from a five-condition mixture moves the task vector less than the
> spread between folds.**

That is §12.13's "the experts are redundant" visible directly in weight space, arrived at
independently of any accuracy measurement. The fold norms are ~2× the single-condition specialists
(0.80 vs 0.33–0.38) — five conditions of data moves the model further — but they are no better
aligned to each other than the specialists are, and the ordering does not track accuracy:
`holdS1` is the most geometrically distinct fold yet mid-pack on accuracy (37.3), while `holdL0` is
the least distinct and the highest (41.7).

### 14.7 What to carry forward

1. **Never report a same-seed LoRA cosine as a measure of task similarity.** At r=32 the
   initialization dominates: identical data gives 0.05, different transforms give 0.59. Any
   geometry→accuracy analysis must be **stratified by seed**, and pooling regimes fits a line
   through an artifact. This is a correction to how a slice of the model-merging literature reads
   its own diagnostics, and it is cheap to reproduce anywhere.
2. **Sign conflict does not bound merged accuracy**, on four independent probes — and least of all
   for TIES, the algorithm it is a theory of. Report it as a description of the merge operation,
   never as a predictor of its outcome.
2b. **Report ‖ΔW‖ instead.** The surviving task-vector norm predicts merged accuracy at **ρ = +0.86**
   over 17 merges (§14.4b), explains the TIES/DARE-TIES gap, and identifies the DARE-linear defect
   from the weights alone. It is cheaper than sign conflict — no pairs, no dense ΔW, no sampled
   layer slice — and it is the one geometry quantity in this project with predictive value. The
   operating rule it implies: **a merged adapter should land near the magnitude of a single
   expert**; 0.19× and 5.6× are both broken.
3. **The relative geometry within a fixed seed is interpretable** and recovers real structure: the
   inert-material family clusters at 0.69–0.70, `S1` sits apart from every renaming condition at
   0.46, and both reproduce on an independent seed. Use it to describe *what the experts learned*,
   not to predict *how well they will merge*.
4. **The r × r contraction is the reusable artifact.** ⟨ΔWᵢ,ΔWⱼ⟩ = sᵢsⱼ·tr((BᵢᵀBⱼ)(AⱼAᵢᵀ)),
   verified to 5.6e-16, makes the whole diagnostic free. Sign conflict is the one quantity that
   still needs a dense ΔW, and it is sampled over five layers.

**Provenance.** `results/merge_geometry/{adapters, adapters_s42, adapters_overtrain, l0seeds,
loto}_qwen25c-1.5b_python.json`; the cross-seed row computed 2026-08-27 via
`src/obtune/merge_geometry.py` against the `24_crossseed_control.py` bank map
(`L0`:17, `L1b`:42, `L1r`:17, `L2`:42, `S1`:17, `S2`:42). Accuracy points are Grid B means over the
six trainable conditions, from `results/cells/`. Lab notes:
[`../log/modularity/2026-08-10_overtraining-and-merge-geometry.md`](../log/modularity/2026-08-10_overtraining-and-merge-geometry.md)
and [`../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md`](../log/modularity/2026-08-15_item-agreement-and-seed-geometry.md).

---

## 15. RQ3 — attention, and the mechanism for the one transfer that works

*Added 27 August 2026. Full self-contained account:
[`REPORT_2026-08-26_rq3-attention-mechanism.md`](REPORT_2026-08-26_rq3-attention-mechanism.md);
lab notes `log/attention/2026-08-{17,18,26}_*.md`.*

Every earlier revision of this document said **"RQ3 (attention) has not been run."** It has now run,
and it is the first section of this report that explains *why* something works rather than measuring
that it does not.

### 15.0 The question RQ3 exists to answer

§3.5's `S2`→`H1` transfer is the project's one positive result and it was found by accident. The
proposed explanation is that `S2` (opaque predicates + dead code) and `H1` (string encoding + MBA)
both bury the real computation under **inert material**, so what `S2` teaches is a genuinely
transferable skill: *ignore the code that cannot affect the result*. Learning to ignore transfers;
learning to invert a particular renaming does not. **That was a story.** RQ3 tests it.

The charter is explicit that RQ3's causal claims wait for an intervention, so this ran in two
stages: a predictive sweep, then a knockout.

### 15.1 The adapter really does re-anchor attention

Take the model's attention at the moment it is about to emit the answer and ask where it is looking.
Every program token is labelled — **identifier**, **control_kw** (`if`/`for`/`return`),
**dataflow_critical** (on the path from input to output), plus operators and literals. Define

> **anchoring shift** = Δ(attention on control + dataflow) − Δ(attention on identifiers),

measured against the untuned base. Positive means attention moved off names and onto structure.

**The sweep:** 4 systems × 6 conditions × 6 layers × 150 programs = **3,600 attention dumps**.
`tuned_L1b_s17` is in the panel deliberately — a specialist that helps on its own condition and
never reaches `H1` — so the result cannot be "any adapter does this".

Anchoring shift vs `base`, cluster-bootstrapped by program, 51 programs:

| system | L0 | L1b | L1r | L2 | S1 | **S2** |
|---|---|---|---|---|---|---|
| `tuned_L0` | +0.008 | −0.024 | −0.031 | −0.011 | −0.032 | **+0.044** |
| `tuned_L1b_s17` | −0.003 | −0.033 | −0.041 | −0.015 | −0.059 | **+0.030** |
| **`tuned_S2_s17`** | +0.014 | −0.015 | −0.044 | −0.008 | −0.013 | **+0.111** |

**`tuned_S2_s17` on `S2`: +0.1113 [+0.0930, +0.1313]** — the largest cell by 2.6×, and **specific**:
small, null or negative on every other condition. Two checks make this coherent rather than a
curiosity. **`S2` is the only condition with much junk to ignore** — under `base`, identifier
attention mass is 0.15–0.18 on `S2` against 0.03–0.04 everywhere else, because the dead helpers
bring their own names. And **the renaming conditions go the other way**: every adapter shifts
attention *toward* identifiers on `L1b`/`L1r`/`L2`, which is the expected mirror image, since under
a renaming transform the identifiers are what changed.

### 15.2 The knockout, and two false starts worth recording

**The intervention.** Suppress attention to identifier tokens — add a large negative number to the
attention scores at those positions — and measure how much each system loses. If `tuned_S2` has
learned to ignore those tokens, taking them away should cost it *less* than it costs `base`.

**False start 1 — the null that meant nothing.** Eight conditions, 150 items each, every cell
between **−2.7 and +2.7** points. `tuned_S2` and `base` were identical. Read naively: the
re-anchoring is incidental and the mechanism is dead. We did not read it naively, **because `base`
lost nothing either** — and a manipulation that moves *no one's* accuracy has not been shown to be a
manipulation at all.

**The manipulation check.** Suppress all six token classes — every code token — across all 28 layers:

| what is suppressed | layers | keys masked | accuracy damage |
|---|---|---|---|
| all 6 classes | 28 | 372 | **+2.7** |
| all 6 classes | 6 | 372 | −2.0 |
| identifiers | 28 | 132 | −0.7 |
| literals | 6 | 49 | −1.3 |

**Blinding the model to the entire program changed its accuracy by 4 items out of 150.** Either the
intervention is broken, or accuracy is the wrong measure.

**False start 2 — my diagnosis was wrong.** The natural conclusion was a broken hook. It was not:
attention mass at masked key positions goes from 0.0072 / 0.0247 / 0.0284 (layers 4 / 14 / 27) to
**exactly 0.0000**, and under the full knockout **68 % of outputs change** (48/150 identical), with a
clean dose-response (62 % identical at 6 layers, 32 % at 28). **The instrument was fine; the
*measure* was insensitive.** `base` scores ~22 % on obfuscated `S2`, close enough to guessing that
scrambling what it can read changes *which* answers it gives without changing how often they land.

### 15.3 The causal result

Ask instead **how strongly the model believed the right answer**: teacher-force the gold output and
record its log-probability, clean versus knocked out. Continuous, no floor, defined even on items the
model gets wrong. Sensitivity check first: suppressing all six classes across 28 layers costs `base`
**−1.590** nats and `tuned_S2` **−2.544**, so the readout has ~100× the dynamic range of the effect
being looked for and a null in it is a real null.

Identifier knockout on `S2`, 150 items, 50 programs, bootstrapped by program. Negative = hurt.

| system | Δ log P(gold) | 95 % CI | |
|---|---|---|---|
| `base` | **−0.0892** | [−0.1578, −0.0230] | significantly hurt |
| `tuned_L1b_s17` | −0.0624 | [−0.1254, −0.0057] | significantly hurt |
| `tuned_L0` | −0.0321 | [−0.0819, +0.0187] | null |
| **`tuned_S2_s17`** | **+0.0145** | [−0.0515, +0.0880] | **not hurt at all** |

Paired item-by-item against `base`:

| system | less harmed than base by | 95 % CI | |
|---|---|---|---|
| **`tuned_S2_s17`** | **+0.1037** | **[+0.0109, +0.2085]** | **CI excludes zero** |
| `tuned_L0` | +0.0571 | [−0.0225, +0.1358] | null |
| `tuned_L1b_s17` | +0.0269 | [−0.0502, +0.1102] | null |

**The pre-registered prediction is confirmed.** Three things make it more than one significant
number:

1. **The rank order matches the sweep, from an independent measurement.** Re-anchoring ran
   `tuned_S2` (+0.111) > `tuned_L0` (+0.044) > `tuned_L1b` (+0.030) > base; knockout damage runs the
   mirror image, `tuned_S2` (+0.014) < `tuned_L0` (−0.032) < `tuned_L1b` (−0.062) < base (−0.089).
2. **The deflationary explanation is ruled out.** "The adapter just ignores the code" predicts it is
   hurt *less* when everything is suppressed. It is hurt **more** (−2.544 vs −1.590). `tuned_S2`
   depends on the program *more* overall and on identifiers *less* specifically — the shape the
   mechanism predicts and a trivial explanation does not.
3. **A specialist that does not transfer does not show it.** `tuned_L1b` re-anchors least and is
   hurt nearly as much as `base`.

### 15.4 What this licenses, and what it does not

**Licensed.** On `S2`, at 1.5B, the `S2` adapter's attention re-anchoring is **load-bearing rather
than incidental**: it attends less to inert identifiers and depends less on being able to read them.

**Not licensed. Anything about `H1`.** No quarantined item was read in any of this work. The step
from "ignores inert material on `S2`" to "therefore transfers to the held-out obfuscator" remains
**inferential** — the two facts are consistent and mutually suggestive, and that is all. Caveats
that travel with it: 50 programs, a single seed, one model scale, six of twenty-eight layers for the
headline knockout, and `tuned_S2`'s own interval spans zero — the significant claim is the *paired
difference against base*.

### 15.5 How much of this was infrastructure

RQ3's code had been written months earlier and **never executed end to end**. Running it surfaced
**six defects, each of which would have produced a confident wrong answer**: an analysis loader that
read a format no writer emits; a silent fallback prompt template (attention measured on a different
distribution than accuracy); no length guard on the dump (one 20,000-token program OOM-killed all 24
sweep jobs); a grader called with 2 args against a 3-arg signature; the same call unpacking 2 values
from a 6-field dataclass; and a silent fallback grader using strict string equality.

**The manipulation check is the load-bearing methodological lesson.** Without it the honest-looking
write-up would have been *"the knockout shows attention re-anchoring is not causal"* — which is
false, and which the data would have appeared to support.

---

## 16. Symbolic normalization — a second, independent instrument on the same mechanism

*Added 27 August 2026. Lab notes `log/normalization/2026-08-{26,27}_*.md`.*

A thread that did not exist at the 08-12 revision. It exists because §15's conclusion invited an
obvious test: if what `tuned_S2` learned **is** dead-code elimination, then handing it code with the
dead material *already removed* should be worth nothing.

### 16.1 The design, and the two pre-registered readings

`norm_structural` is a symbolic dead-code-elimination pass — pure static analysis, **zero training**
— and the strongest zero-training arm in the project (`H1` 12.9 against base 6.3). It had never been
combined with an adapter. `normalize` is a per-system field in `eval_vllm.SystemSpec`, so an arm can
carry an adapter *and* a normalizer with no new machinery.

Written before the run:

* **additive** → independent routes to one skill; stacking is a free improvement.
* **saturated** → the same skill twice, i.e. the learned re-anchoring is approximately dead-code
  elimination and not something else. *A sharper mechanistic claim than either result alone.*

Conditions `L0`, `L1r`, `S2` — **no `H1`**, deliberately: the question is answerable for free on
`S2`, which carries the same inert material by construction, and spending a quarantine read to learn
what the trainable grid already answers is what §3.2 rule 2 exists to prevent.

### 16.2 Saturated — and the gradient is the result

Grid A, n = 1,667–1,670. Cluster bootstrap by `program_id`, 4,000 resamples, seed 17; exact McNemar.

| system | L0 | L1r | S2 |
|---|---|---|---|
| `base` | 21.8 | 18.7 | 15.1 |
| `norm_structural` | 22.0 | 18.9 | **19.9** |
| `tuned_L0` | 45.0 | 36.5 | 41.4 |
| `tuned_L0_norm` | 44.9 | 36.5 | **43.0** |
| `tuned_S2_s17` | 45.6 | 37.4 | 45.3 |
| `tuned_S2_norm` | 45.7 | 37.8 | **45.4** |

What the symbolic pass **buys** each system:

| condition | system | gain from symbolic DCE | 95 % CI | McNemar p | b/c |
|---|---|---|---|---|---|
| **S2** | `base` | **+4.74** | [+3.12, +6.24] | 4.2e−11 | 113/34 |
| **S2** | `tuned_L0` | **+1.56** | [+0.30, +2.88] | 1.5e−02 | 66/40 |
| **S2** | `tuned_S2_s17` | **+0.06** | [−0.96, +1.08] | 1.00 | 35/34 |
| L0 | `tuned_S2_s17` | +0.12 | [−0.42, +0.66] | 0.83 | 12/10 |
| L0 | `tuned_L0` | −0.12 | [−0.60, +0.36] | 0.82 | 8/10 |
| L1r | `tuned_S2_s17` | +0.36 | [−0.12, +0.84] | 0.21 | 11/5 |

**The benefit of pre-cleaned code falls monotonically with how much inert material the system was
trained on**: +4.74 for a model that has never seen any, +1.56 for one trained on clean code only,
+0.06 for the `S2` specialist. `tuned_S2`'s interval is ±1.1 pts — inside the Python seed band — so
this is a genuine **equivalence** result, not a failure to reach significance.

**The controls hold.** On `L0` and `L1r`, which contain no dead code, normalization does nothing for
anybody (|Δ| ≤ 0.36, all null). The `S2` gradient is therefore specific to the material the pass
removes, not a generic "normalized code is easier to read" effect.

**This closes the loop with §15.** The knockout said `tuned_S2` learned to stop attending to inert
identifiers. This says whatever it learned leaves *nothing further* for a symbolic DCE pass to
contribute. **Two independent instruments — a causal attention intervention and a symbolic program
transformation — agree that the skill `tuned_S2` acquired is dead-code elimination, implemented in
attention.** Neither supports that alone; together they do.

It also bounds the negative result usefully: **`tuned_L0` retains +1.56 pts of headroom**, so the
clean-code adapter has *most* but not all of the skill. That is the first quantity in this project
separating `tuned_L0` from a specialist on a **mechanism** rather than on aggregate accuracy.

### 16.3 Better static analysis pays off only where the old pass was blind

If a zero-training arm's ceiling is set by how much the analysis can *prove* dead, a stronger
analysis should buy accuracy. `norm_inert` adds dead-store elimination. `norm_structural` proves
only 0.4 % of `S4` dead.

| condition | Δ (`inert` − `structural`) | 95 % CI | McNemar p |
|---|---|---|---|
| **S4** | **+1.50** | [+0.18, +2.88] | **0.022** |
| S2 | +0.66 | [−0.48, +1.74] | 0.30 |
| S3 | −0.06 | [−0.48, +0.36] | 1.00 |
| L0 | +0.06 | [−0.18, +0.36] | 1.00 |
| L1r | −0.18 | [−0.54, +0.12] | 0.45 |
| S1 | +0.08 | [−0.40, +0.56] | 1.00 |

**`S4` is the only significant cell — the one condition the old pass was blind on.** On `S3`, where
the old pass already removed everything, the difference is −0.06. All four control conditions are
null, which is the evidence that the extra removals are inert code and not live code: a bad analysis
would have *cost* accuracy there.

**But the gain is far smaller than the code removed.** `norm_inert` cuts `S2` programs to 58.4 % of
original against `structural`'s 81.3 %, and `S4` to 67.9 % against 98.7 % — roughly doubling and
thirty-times-ing the material removed — for +0.66 and +1.50 points. **On `S2` the returns to better
static analysis are already flat**: the first pass captured nearly all the accessible benefit, and
the remaining inert material was not what was costing the model. The ceiling on the zero-training arm
is *not* mainly set by analysis strength.

(What `norm_inert` buys `tuned_L0`: **S2 +2.10** [+0.60, +3.66] p=0.005, **S3 +1.56** [+0.12, +3.05]
p=0.033, S4 +0.60 ns; controls `L0` +0.00, `L1r` +0.42, `S1` −0.40, all null.)

### 16.4 The format objection, bounded from existing cells

`base` fails the output format on 13–28 % of items and every adapter on 2–6 %. How much of
`tuned_L0`'s gain is "learned to emit a canonical literal" rather than task learning? Grid A, no new
GPU:

| cond | n | `base` | fmt-fail | loose ceiling | `base` \| fmt-ok | `tuned_L0` |
|---|---|---|---|---|---|---|
| L0 | 1670 | 21.7 | 19.0 | 40.7 | 26.8 | 44.7 |
| S2 | 1667 | 15.3 | 13.2 | 28.5 | 17.6 | 41.8 |
| S3 | 1670 | 16.0 | 14.3 | 30.3 | 18.7 | 43.1 |
| S4 | 1667 | 19.3 | 16.7 | 35.9 | 23.1 | 43.2 |
| **H1** | 1214 | **6.4** | **28.3** | **34.8** | **9.0** | **24.5** |

Granting `base` a win on every item it lost to a format failure is a loose ceiling that on `H1`
(34.8) exceeds `tuned_L0` outright — but it is uninformative, since it assumes a 100 % hit rate on
items where `base` hit 9.0 % when it *did* format correctly. **The conditional estimate is the
informative one: if format were free, `base` reaches 9.0 % on `H1` against `tuned_L0`'s 24.5 %, so
format acquisition accounts for at most ≈2.6 of the 18.1-point gain** and ~15.5 points are task
capability. The conditioning is on a post-treatment variable and selects the items `base` found easy
enough to format, so 9.0 % is if anything *optimistic* — which pushes the conclusion the safe way.

**One number deserves its own line: `base`'s format-failure rate on `H1` is 28.3 %**, against 13–19 %
on every trainable condition. **The held-out obfuscator breaks the base model's ability to follow an
output format roughly twice as often as anything it was trained on.** That is a separate phenomenon
from accuracy and it is not reported anywhere else in this document.

### 16.5 Steering: the mechanism is attention allocation, but only at full depth

§16.2 showed that *deleting* inert code helps a lot. Deletion changes two things at once, and every
normalization result in this document — and, as far as we can tell, the deobfuscation literature's
normalization baselines generally — confounds them:

  (a) the distracting tokens are **gone**, so no attention can land on them; and
  (b) the sequence is **shorter**, so every live token sits closer to the answer position.

**Masking separates them.** The model is shown the byte-identical original program; every token keeps
its position and its neighbours; the only thing that changes is that attention to the inert KEY
positions is suppressed (`attention.knockout.inert_key_mask`, driven by the *same* spans
`normalize.inert` deletes, so the two arms differ in exactly one respect by construction). Readout is
teacher-forced log P(gold), per §15.2's floor lesson. n=150 items per cell, `heldout`, seed 17.

**Pre-registered direction, and note the sign is the OPPOSITE of §15.3's knockout.** There the
suppressed tokens were ones the answer depends on, and suppressing them *hurt* `base` (−0.089
[−0.158, −0.023]). Here they are provably irrelevant, so a distracted model should get **better**.

| system | cond | 6 layers (4,9,14,19,23,27) | **all 28 layers** |
|---|---|---|---|
| `base` | **L0** | **+0.0000** | **+0.0000** |
| `base` | S2 | +0.0033 (75/75) | **+0.2172** (94/56) |
| `base` | S4 | +0.0110 (78/63) | **+0.0788** (92/49) |
| `tuned_L0` | L0 | +0.0000 | — |
| `tuned_L0` | S2 | −0.0103 (96/54) | — |
| `tuned_L0` | S4 | +0.0058 (86/55) | — |
| `tuned_S2_s17` | **L0** | **+0.0000** | **+0.0000** |
| `tuned_S2_s17` | S2 | −0.0293 (76/74) | **+0.1352** (80/70) |
| `tuned_S2_s17` | S4 | −0.0182 (69/72) | +0.0246 (61/80) |

*(Δ log P(gold), knocked − clean; POSITIVE = suppressing attention to inert code helped. Parenthesis
= items improved/worsened.)*

**Depth is the whole story, and the six-layer result is a trap.** At 6 of 28 layers every cell is
inside ±0.03 with better/worse splits near 50/50 — a flat null that invites the conclusion that
attention allocation is *not* the mechanism and that deletion works purely through (b), sequence
length. **That conclusion was drawn during this session and was wrong.** At full depth `base` on `S2`
moves **+0.2172**, roughly 2.4× the magnitude of the §15.3 knockout that established RQ3's causal
leg, in the predicted direction. Attention suppressed at 6 layers simply reaches the inert keys at
the other 22; the null measured a partial intervention, not an absent effect. **Any future knockout
or steering result in this project must report its layer coverage, and a null at partial depth is not
evidence of no effect.**

**The `L0` control is what makes the null interpretable.** All five `L0` cells are *exactly* 0.0000
with 0/150 items carrying inert code — the mask is provably empty on clean code. So the small-effect
cells are genuine nulls rather than a mask that quietly stopped firing, and a non-zero value there
would have voided the arm outright.

**The ordering matches the mechanism.** `base` gains most (+0.2172), `tuned_S2` less (+0.1352) — the
specialist already declines to attend to this material, so forbidding it buys less. That is the same
ordering §15.3 and §16.2 produce by two other routes.

**What this settles and what it does not.** Training-free attention steering **works**: a static
analysis plus an inference-time mask improves the log-probability of the correct answer with no
training and no rewriting of the program. It is a third independent instrument agreeing that inert
material is what costs the model on this family. It does **not** yet show an accuracy gain — the
readout here is log-probability, and a confirmatory `--mode generate` pass is owed before any claim
that steering improves answers rather than confidence. It also does not decompose (a) against (b):
masking recovers *some* of deletion's benefit, but the two are on different scales (log-prob vs
points) and a length-matched control — replacing inert spans with equal-length neutral filler — is
the missing arm that would identify how the +4.74 divides.

*Instrument: `scripts/attn/31_steer.py`, `attention.knockout.inert_key_mask`, spans from
`normalize.inert.inert_spans` (execution-gated at 1200/1200 parity,
`scripts/analysis/25_validate_inert.py`). Cells: `results/attn/steer/`. No `H1` item was read.*

---

## 17. Provenance

- Numbers: `results/analysis/master_report.json`, produced by `scripts/make_master_report.py` from
  **597** cell parquets under `results/cells/` (regenerated 2026-08-11; §3–§7 tables are from the
  453-cell run and were re-verified against it). Rerun with `python scripts/make_master_report.py`.
- Statistics: cluster bootstrap by `program_id`, 2000 resamples, seed 17; BH-FDR within each delta
  family; an effect is called real only when q<0.05 *and* the bootstrap CI excludes zero.
- Grading: strict normalized exact match, no containment matching, execution-verified answers.
- Per-cell provenance (config sha, script sha, git commit, GPU id, adapter sha256, sampling params,
  prompt template sha256) is in each cell's `cell_meta.json`.
- Evaluation git commit for the main grid: `469f857`. Engine: vLLM 0.26.0, greedy decoding.
- Document current as of **2026-08-27**; queue state at that time: 332 done, 0 new failures
  (the 31 in `runs/manifest/failed/` are the 18 Aug attention-dump OOM batch, diagnosed and fixed).
- Lab notes: [`log/`](../log/). Earlier reports, superseded only where §8 says so:
  [`PILOT_REPORT_2026-08-05.md`](PILOT_REPORT_2026-08-05.md),
  [`RESULTS_2026-08-09.md`](RESULTS_2026-08-09.md),
  [`REPORT_bidirectional_2026-08-09.md`](REPORT_bidirectional_2026-08-09.md).

## Changelog

- **2026-08-27 (rev 13)** — **Re-dated and brought current: this supersedes the 08-12 revision and
  is the living master report.** §2.2's master table **regenerated in full from every per-cell
  parquet — 154 systems in 169 rows (up from 73 in 74), one row per system PER GRID**, so the `grid`
  column is authoritative for every cell in a row including `H1`; fifteen systems were on both grids
  and had been sharing one row, which is how the RQ2 conclusion came to rest on 115 items. Duplicate
  cells are now resolved by a **documented source preference** (vLLM over `hf-mole` except for
  `mole_*`; then larger n; then newest) — 41 cells have disagreeing duplicates, 27 by >0.5 pt.
  **Verified: all 74 rows of the 08-12 table reproduce exactly, 0 value differences.**
  **§14 added** — the task-vector geometry thread consolidated from §5.3/§12.12 and extended: the
  cross-seed bank's sign conflict and TIES keep rate computed for the first time (0.565 / 0.638
  against the same-seed arm's 0.394 / 0.840), the four probes of whether geometry predicts merged
  accuracy, the per-projection breakdown, the within-seed pair structure, and the resolution of the
  owed geometry→accuracy regression — which is that it should not be run.
  New sections: **§15 (RQ3 — attention, the anchoring sweep and the causal knockout)**, which
  replaces "RQ3 has not been run" everywhere it appeared; **§16 (symbolic normalization)**, a thread
  that did not exist at the last revision and which gives §3.5's transfer a second, independent
  instrument; **§7.8** (MBPP+ as a held-out benchmark overturns two of the CFT thread's central
  claims); **§12.12** (item-level redundancy, task-vector geometry as an initialization artifact,
  the cross-seed control, the residual merge) and **§12.13** (RQ2 closed, with the elimination table
  and the corrected mechanism). §1, §9 and §10 rewritten. **Three corrections that change how earlier
  numbers should be read** — §8.9 the evaluation-stack determinism spread on the `tuned_L0` `H1`
  control (40.0 / 34.8 / 33.9 across three passes, two identical in every recorded field), §8.10 the
  pooled-vs-Python seed band (applied ~2.5× too permissively in five documents and three scripts;
  §12.4 corrected in place), §8.11 the label-shuffled format control is **void, not zero**. Plus
  §8.12 (LOTO `train_size` never bound) and §8.13 (`build_manifest.py --eval` silently drops merge
  systems). **§12.10's "the per-condition experts carry nothing distinct" is retired** in favour of
  the offsetting-effects statement in §12.13.
- **2026-08-17 (rev 15)** — §12.11 added: the two attempted repairs to §12.10's negative result,
  and both are null. Training deliberately for the inert-material family (`s2fam`, S2+S3+S4)
  lands **+0.02 pts** [−0.95, +1.02] on the clean-code control; training on stacked composites is
  **−1.36** [−2.63, +0.04] against the same mechanisms unstacked, i.e. the sign runs against the
  hypothesis. Most columns are OOD for these arms, so these are generalization nulls. `s2fam`
  still tops the `S2` and `S1` columns and is worst on `L1b` — wins where it trained, nowhere
  else. `H1` deliberately unread, so §3.5 is untouched and its confirmatory read is now the
  decisive open item.
- **2026-08-15 (rev 14)** — §5.3 gains a **caveat that changes how its geometry table may be
  read**: cosine and sign conflict between LoRA task vectors are dominated by shared
  initialization, not learned content. Three `L0` adapters trained on byte-identical data are
  near-orthogonal (0.053, sign conflict 0.487 — a coin flip) while eight adapters trained on
  different transforms are 0.59-aligned, because a seed fixes the rank-32 subspace. Every §5.3
  figure is same-seed and therefore measures drift within one subspace. The L0-merge control is
  built from that near-orthogonal bank and merges fine, so **sign conflict does not bound merged
  accuracy** — the diagnostic's premise fails, not just its consequence. Also recorded from the
  same zero-GPU pass: the six LOTO fold task-vectors are effectively one vector (mean-cosine
  range 0.018), and the `H1` system ladder is **redundant, not complementary** — the oracle sits
  45–53 pts *below* a marginal-preserving permutation null on both grids, so the raw
  "oracle headroom" is an oracle-of-k artifact.
- **2026-08-14 (rev 13)** — **Numbering pass**: sections now run 1–14 in file order. The shot-count
  section moved from §13 (where it sat after Glossary and Provenance because 11 and 12 were taken)
  to **§11**; Glossary → **§13**, Provenance → **§14**; the new §12 holds the 13–14 August results.
  All internal cross-references and the table of contents were updated and anchor-checked.
  §2.2 gained the seven Grid B shot-count rows (`icl_k1/k2/k4`, `tuned_L0_k0/k1/k2/k4`) and a
  **Grid B `base` row**, without which those rows have no floor in the table — population match
  verified by snippet-id set comparison (176/40, 145/33, 115/27), values reconciled cell-by-cell
  against Table 39. **§11.3's grid caveat is struck**: `merge_dare_ties` on H1 is Grid B, not
  Grid A, so the merge/mixture/baseline ladder was always same-item — the best merge (34.8) ties
  the clean-code control adapter (34.8) on H1. §12 added: the Grid A baseline panel and the
  resume-aliasing defect that left it 33 cells short, the 7B ladder and what it does to the
  framing, `mole_hardrouter`, and a format-failure decomposition that partly closes §11.2.
- **2026-08-13 (rev 12)** — §9.1 added: the matched-condition k-shot ICL baseline, which has never
  been run. Records that the existing `oracle_prompt_1shot` uses a CLEAN demo and is therefore the
  weak form, that `prompts.py` is frozen so k>1 needs a composing module, and promotes ICL to item
  2 of §10 because it is inference-only and decides how strong the modularity claim really is.
- **2026-08-13 (rev 11)** — Table of contents added. §1.6 added: prior work with the numbers each
  paper actually reports, plus columns for "trains on obfuscated code?" and "held-out transform?" —
  which is where the contribution sits. Flags explicitly that `promon2026atr`'s 79 %→26 % is a
  different task and metric and must not be pooled with ours.
- **2026-08-13 (rev 10)** — §1.5 added: literature positioning, the advantages stated as a reviewer
  would attack them, and a **correction** — the router is not a failure but a ceiling, and its
  out-of-distribution behaviour has never been measured (`n_heldout: 0`). Lists the three cheap
  tests that would settle it, and the random-seed-`L0`-merge control that must rule out
  "merging regresses toward the clean-code model" before the merging claim is published.
- **2026-08-13 (rev 9)** — §2.2 added: one table with every system evaluated on Python at 1.5B
  against all nine single-transform conditions and all six composites, grouped by programme and
  labelled by grid so rows are not differenced across disjoint program sets.
- **2026-08-12 (rev 8)** — Accuracy tables added to the three new sections so each can be judged
  against a reference rather than on mechanism alone. §5.3 gains the merged-accuracy sweep and a
  **corrected conclusion**: more training made merges *better* on five of six method×condition
  pairs, the opposite of the paper's prediction — the earlier "flat within CIs" wording was wrong.
  §5.4 gains the reference table whose point is that every composite cell is empty. §7.7 gains
  untuned-base and `sft` rows, without which the λ curve has no floor.
- **2026-08-12 (rev 7)** — Dated to today: this is the living master report, not a 10 August
  snapshot. §9 rewritten (RouterLoRA, the 8-expert bank, the uniform-epoch sweep and a formal
  §7.7 comparison are the open items; `fwd2x`/`cftflip`, `compute_is_core` and HumanEval+ moved to
  resolved). §10 re-ordered around what is actually next, with the two completed items struck
  rather than deleted.
- **2026-08-12 (rev 6)** — Made the document self-contained: §2.1 added, decoding every notation
  (`s17 \| s42`, `*`, bold diagonals, points-vs-accuracy) and indexing all 30 tables; column
  definitions added for the geometry and unlearning tables; eight glossary terms added for the
  concepts §5.3/§5.4/§7.7 introduce.
- **2026-08-12 (rev 5)** — §5.3 added: task-vector geometry on two banks shows Horoi et al.'s
  overtraining mechanism is *absent* from our 3-epoch bank (sign conflict falls) and appears only
  past epoch 3, with merged accuracy flat regardless; records the unequal-epoch confound affecting
  every merge in §5.2. §5.4 added: RouterLoRA built, composite corpus generated and gate-validated,
  two design defects caught before any GPU time. §7.7 added: approximate unlearning at both scales
  **and its control**, which collapses as hard as the treatment — the 1.5B entanglement reading is
  withdrawn. §8.1 resolved (and the "transfer into L1b fails" claim it caused is retracted); §8.7
  and §8.8 added for the `output_raw` scoring bug and its blast radius. Header scope updated to
  597 cells / 317,810 trials.
- **2026-08-10** — Created. First aggregation of all 453 cells across both languages, both seeds,
  and both evaluation grids; documents the `S2`→`H1` transfer, the RQ2 arms, and the six data-quality
  issues in §8.
- **2026-08-10 (rev 2)** — §5 (RQ2) rewritten to be readable without background: what routing and
  merging are, the exact router architecture and training recipe, which six adapters go into each
  merge and with what algorithm, weights and density, and what TIES and DARE actually do. Added §11
  glossary; recorded that the configured density sweep never ran and that `H1` was never routed.
- **2026-08-10 (rev 3)** — §3.6 and §3.7 converted from prose to full tables (the JavaScript matrix
  at both seeds; per-adapter seed-42-minus-seed-17 tables per language with summary statistics).
  §7 (CFT side thread) expanded from a bullet list into a full section: the question and the gap,
  the seven arms and their measured cost, why `exec` is a broken measure, the 1.5 B and 7 B result
  tables, the per-transformation inversion, and what the thread leaves open — including two
  budgeted-but-never-trained arms (`fwd2x`, `cftflip`).
- **2026-08-10 (rev 4)** — §8.3 resolved: the HumanEval+ harness bug is diagnosed and fixed, and
  the check has now run for every CFT-thread arm at 1.5B and three at 7B; records that the two
  scales disagree about whether forward-only SFT causes general or purely directional damage.
  §7.6 resolved: `fwd2x`, `cftflip` and `mix50`@7B are trained and evaluated, giving the
  objective × data-direction 2×2.

- **2026-08-27 (rev 17)** — Two gaps closed before the session ended.
  **§8.14** records a silent miscompilation in the PUBLISHED `norm_structural` arm: `fold` +
  `ast.unparse` rewrote `(-1) ** r` as `-1 ** r` (= `-(1 ** r)`), corrupting ~1 % of programs, which
  the arm then scored against the original's answer. Fixed generally with a round-trip guard in
  `_emit`; no §16 conclusion reverses, but every pre-fix `norm_*` number is a slight under-estimate.
  Also records *why* the existing soundness gate missed it — it had not been re-run since the passes
  changed.
  **§16.5** adds the attention-steering arm, and with it a methodological correction that matters
  beyond this section: masking attention to provably-inert tokens at **6 of 28 layers** is a flat
  null (|Δ| ≤ 0.03, better/worse ≈ 50/50), and at **all 28 layers** `base` on `S2` moves
  **+0.2172** — ~2.4× the §15.3 knockout, in the pre-registered direction, with `tuned_S2` gaining
  less (+0.1352) exactly as the mechanism predicts. The six-layer null was a partial intervention,
  not an absent effect; it was briefly concluded otherwise during the session and is corrected here.
  **Every knockout or steering result in this project must now report its layer coverage.** All five
  `L0` control cells are exactly 0.0000 with an empty mask, which is what makes the nulls readable.
