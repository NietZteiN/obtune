# obtune — master results report

**12 August 2026 · everything run to date, in one frame.**

> **SUPERSEDED 2026-08-27** by [`MASTER_REPORT_2026-08-27.md`](MASTER_REPORT_2026-08-27.md), which
> is this document brought current: §2.2's master table regenerated from every cell (154 systems,
> `H1` split by grid), RQ2 closed (§12.12–§12.13), RQ3 run (§15), a new normalization thread (§16),
> the CFT thread's benchmark corrected (§7.8), and three measurement corrections (§8.9–§8.11).
> **Kept for provenance — every number below was true when written, but two are now known to be
> read the wrong way:** §12.10's *"the per-condition experts carry nothing distinct"* is **retired**,
> and §12.4's use of the pooled 3.61 seed band should be the **Python** row (0.63 / 1.46) that §8.4
> also reports. RQ2 alone is also covered self-contained in
> [`MASTER_REPORT_2026-08-27_router-and-merging.md`](MASTER_REPORT_2026-08-27_router-and-merging.md).

*Supersedes [`MASTER_REPORT_2026-08-11.md`](MASTER_REPORT_2026-08-11.md) and
[`MASTER_REPORT_2026-08-10.md`](MASTER_REPORT_2026-08-10.md), of which this is the direct
continuation — the Changelog records what each revision added. Since 10 August: §2.1 (how to read
every table), §5.3 (overtraining and merging), §5.4 (RouterLoRA), §7.7 (approximate unlearning and
its controls), §8.1 resolved, §8.7–§8.8 new.*

Scope: all **597** evaluation cells / **317,810** graded trials under `results/cells/`, plus the
CFT/bidirectional side thread. Every number below was recomputed from raw per-trial data by
[`scripts/make_master_report.py`](../scripts/make_master_report.py) → `results/analysis/master_report.json`;
none are copied from earlier documents. Where a number here disagrees with an earlier report,
**this document is the one to trust** and §8 says why.

Model: Qwen2.5-Coder-1.5B-Instruct for **every table below except where a row or section says
otherwise**. Two documented exceptions, both 7B: the CFT side thread (§7) and the zero-shot
baseline panel added 2026-08-13 (§9.3). Never mix them in one table — 7B roughly doubles
accuracy on every condition, so a stray 7B row would dominate any 1.5B comparison.

Grid: **Grid B** (`testset`) for §12's baselines, **Grid A** (`heldout`) for the RQ1/RQ2
headlines. These are different program sets and CLAUDE.md forbids pooling them — `base` on
H1 reads 6.4 % on Grid A and 11.3 % on Grid B. Every table states its grid.
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
- [13. Glossary](#13-glossary)
- [14. Provenance](#14-provenance)

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
JavaScript). Modularity (RQ2) does not rescue the picture: a router that classifies the obfuscation
type with 100% accuracy buys exactly the specialists' own gains and nothing more, merges are at or
below the control, and simply *telling* the untuned model the obfuscation type is ~20 points worse
than any adapter. RQ3 (attention) has not been run.

*Added 12 Aug.* Three things have since been settled. **Overtraining does not explain the merge
failure** — sign conflict *falls* over our 3-epoch bank and only rises past epoch 3, so our experts
are under-trained relative to where interference appears (§5.3). **The bidirectional thread's
unlearning probe does not show shared representation** — its control collapses just as hard as the
treatment, which is what the control was built to detect (§7.7). And **a scoring bug failed six runs
in a way that looked like an adapter failure** (§8.7); it corrupted two reported fields but no
accuracy metric, and every table in this document predates it.

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

*Added 13 August 2026.* Accuracy, higher is better. `—` means not run for that pair, never zero.

**Model: `qwen25c-1.5b` (Qwen2.5-Coder-1.5B-Instruct), Python, every row.** No 7B row appears
here and none may be added: 7B roughly doubles accuracy on every condition (§9.3), so a single
7B row would dominate the table and invite differences that are model effects wearing a
system's name. 7B results live in their own sections.

**READ THE `grid` COLUMN BEFORE DIFFERENCING ANY TWO ROWS.** Grid A is 317–557 corpus programs;
Grid B is 33–40 ICSE test-set programs. They are disjoint (§2), so an A row and a B row are
measured on different populations and their difference is not interpretable. Within a grid,
comparisons are valid. The `C_*` columns are the stacked composite conditions (§5.4), which exist
only on Grid B and only for the arms that were run against them.

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
| `gate frozen …` / `trained gate` | RouterLoRA variants — the control gates vs the learned one (§5.4). |

**Every column, decoded** (*added 15 August 2026*). Each cell is the accuracy of the row's system
on the column's condition, so the columns are *evaluation* conditions — what the code being read
looked like — and never what the system was trained on (that is the `settings` column). Full
definitions live in §13; this is the self-contained version.

| column | what it is |
|---|---|
| `system` | The system that produced the row: the untuned model, one fine-tuned adapter, a merge of several adapters, or a mixture with a gate. Names are decoded by the `settings` column beside them. |
| `grid` | Which of the two disjoint program sets the row was measured on. **A** = 317–557 corpus programs, **B** = 33–40 ICSE test-set programs; an A number and a B number are measured on different populations and must never be differenced (§2). |
| `settings` | What the row actually is — rank, seed, training condition, merge algorithm, expert count, demo count — in the notation of the table just above. |
| `L0` | **Clean code, no obfuscation** (comments and docstrings stripped, as in every condition). The reference difficulty: whatever a system scores here is what it can do when nothing is hidden. |
| `L1b` | **Adversarial renaming.** Identifiers are replaced with actively misleading names — a Fibonacci function called `smoothArea` — so the names point at the wrong meaning rather than at none. Consistently the hardest of the identifier conditions. |
| `L1r` | **Random renaming.** Identifiers become meaningless hex (`v_a3f2`), which removes the naming signal without lying about it. The contrast with `L1b` separates "no information" from "false information". |
| `L2` | **Minification.** Identifiers become `a`, `b`, `c`… and type annotations are stripped — the transform a JS bundler applies in production. Like `L1r` but shorter and with the types gone too. |
| `S1` | **Control-flow flattening.** The function body is rewritten into a dispatch loop over a state variable, so the original `if`/`for` shape is gone even though every name is untouched. The first column where structure, not naming, is what was destroyed. |
| `S2` | **Opaque predicates + dead code.** Guards that provably always take the same branch, plus helper functions that are never called. The code grows and gains branches, but none of the additions change behaviour. |
| `S3` | **Dead code only** — the half of `S2` that just has to be *ignored*: 1–2 never-called helpers, no opaque predicates. |
| `S4` | **Opaque predicates only** — the half of `S2` that has to be *reasoned about*: 1–3 always-taken guards whose condition genuinely executes, no dead helpers. `S3` and `S4` exist so a drop on `S2` can be attributed to one of the two mechanisms rather than their fusion. |
| `H1` | **The held-out obfuscator** — string encoding + mixed boolean-arithmetic rewriting, and the only condition nothing is ever trained on (quarantined behind four enforcement layers, §3.2). It is the discriminator: score here means the model learned the *class* of meaning-preserving rewrites; failure here with high scores elsewhere means it memorised the specific transforms it saw. |
| `C_L1r_S1` | **Composite: random renaming, then flattening.** The headline stacked condition — one identifier transform and one structural transform in the same program, so no single specialist is the right expert for it. Composites exist only on Grid B and are deliberately outside the trainable ladder, so they cannot shift RQ1. |
| `C_S1_L1r` | **The same two transforms in the opposite order** — flatten first, then rename. Composition does not commute: `S1` emits `_st_`-prefixed state variables, and renaming them *second* destroys the surface cue a hard router keys on. A routing drop here but not on `C_L1r_S1` means the router was reading variable names, not structure. |
| `C_L1b_S1` | **Adversarial renaming, then flattening.** `L1b` is the one condition where a specialist beats the `L0` control (§3.5); this column asks whether that advantage survives having a structural transform stacked on top of it. |
| `C_L2_S4` | **Minification, then opaque predicates** — an identifier transform stacked with the *reason-about-it* half of `S2`. |
| `C_L1r_S3` | **Random renaming, then dead code** — the same shape as the column before it, but with the *ignore-it* half of `S2`. The pair decomposes which half of `S2` stacking actually costs. |
| `C_S4_S3` | **The positive control**: opaque predicates then dead helpers, which is `S2` reconstructed by composition. It should score near `S2` on adapters we already have numbers for; if it does not, the composite build machinery is wrong and no other `C_*` column can be trusted. |

Two rows to read carefully. **`tuned_L0` (A) and `tuned_L0_k0` (B) are the same adapter** — same
sha256, same prompt, zero demos — on the two different grids, which is why they differ by ~6
points with nothing about the system changed. And **`merge_dare_linear` is the broken arm**; its
repaired form is `dl_rescaled` (§5.2).

| system | grid | settings | L0 | L1b | L1r | L2 | S1 | S2 | S3 | S4 | H1 | C_L1r_S1 | C_S1_L1r | C_L1b_S1 | C_L2_S4 | C_L1r_S3 | C_S4_S3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Reference** | | | | | | | | | | | | | | | | | |
| `base` | A | untuned base model | 0.218 | 0.189 | 0.187 | 0.196 | 0.205 | 0.151 | 0.160 | 0.193 | 0.063 | 0.176 | 0.160 | 0.156 | 0.152 | 0.120 | 0.151 |
| `base` | B | untuned base model | 0.290 | 0.233 | 0.233 | 0.210 | 0.262 | 0.188 | 0.182 | 0.222 | 0.113 | 0.267 | 0.247 | 0.320 | 0.176 | 0.159 | 0.182 |
| `oracle_prompt_1shot` | A | 0 train · oracle label + 1 clean demo | 0.277 | 0.201 | 0.213 | 0.233 | 0.216 | 0.248 | — | — | 0.157 | — | — | — | — | — | — |
| `tuned_L0_s17` | A | r32 · s17 · L0 | 0.447 | 0.344 | 0.367 | 0.375 | 0.390 | 0.415 | 0.431 | 0.431 | 0.247 | 0.271 | 0.245 | 0.247 | 0.343 | 0.346 | 0.424 |
| `tuned_L0_s42` | A | r32 · s42 · L0 | 0.447 | 0.337 | 0.373 | 0.369 | 0.387 | 0.421 | 0.446 | 0.429 | 0.247 | 0.281 | 0.256 | 0.255 | 0.349 | 0.340 | 0.428 |
| `tuned_L0` | A | r32 · s17 · L0 | 0.450 | 0.342 | 0.365 | 0.374 | 0.391 | 0.414 | 0.431 | 0.432 | 0.247 | 0.271 | 0.246 | 0.248 | 0.344 | 0.345 | 0.423 |
| **RQ1 specialists (Grid A, seed 17 / 42)** | | | | | | | | | | | | | | | | | |
| `tuned_L1b_s17` | A | r32 · s17 · L1b | 0.438 | 0.384 | 0.381 | 0.385 | 0.357 | 0.409 | 0.435 | 0.433 | 0.250 | 0.275 | 0.250 | 0.285 | 0.362 | 0.353 | 0.418 |
| `tuned_L1b_s42` | A | r32 · s42 · L1b | 0.436 | 0.394 | 0.386 | 0.386 | 0.347 | 0.409 | 0.432 | 0.426 | 0.227 | 0.281 | 0.259 | 0.284 | 0.367 | 0.366 | 0.415 |
| `tuned_L1r_s17` | A | r32 · s17 · L1r | 0.453 | 0.355 | 0.396 | 0.394 | 0.383 | 0.427 | 0.440 | 0.445 | 0.247 | 0.294 | 0.263 | 0.267 | 0.362 | 0.376 | 0.425 |
| `tuned_L1r_s42` | A | r32 · s42 · L1r | 0.445 | 0.361 | 0.389 | 0.388 | 0.379 | 0.430 | 0.440 | 0.438 | 0.245 | 0.300 | 0.267 | 0.266 | 0.370 | 0.378 | 0.430 |
| `tuned_L2_s17` | A | r32 · s17 · L2 | 0.440 | 0.349 | 0.380 | 0.377 | 0.376 | 0.421 | 0.432 | 0.428 | 0.245 | 0.283 | 0.257 | 0.250 | 0.355 | 0.361 | 0.424 |
| `tuned_L2_s42` | A | r32 · s42 · L2 | 0.447 | 0.353 | 0.379 | 0.386 | 0.375 | 0.417 | 0.436 | 0.436 | 0.242 | 0.288 | 0.257 | 0.260 | 0.369 | 0.359 | 0.422 |
| `tuned_S1_s17` | A | r32 · s17 · S1 | 0.435 | 0.319 | 0.368 | 0.374 | 0.424 | 0.425 | 0.425 | 0.428 | 0.254 | 0.310 | 0.299 | 0.295 | 0.352 | 0.334 | 0.413 |
| `tuned_S1_s42` | A | r32 · s42 · S1 | 0.445 | 0.326 | 0.363 | 0.378 | 0.430 | 0.427 | 0.425 | 0.435 | 0.252 | 0.307 | 0.313 | 0.277 | 0.359 | 0.343 | 0.431 |
| `tuned_S2_s17` | A | r32 · s17 · S2 | 0.456 | 0.333 | 0.374 | 0.378 | 0.434 | 0.453 | 0.454 | 0.454 | 0.280 | 0.308 | 0.275 | 0.278 | 0.376 | 0.362 | 0.458 |
| `tuned_S2_s42` | A | r32 · s42 · S2 | 0.446 | 0.338 | 0.372 | 0.381 | 0.424 | 0.447 | 0.450 | 0.452 | 0.275 | 0.303 | 0.270 | 0.275 | 0.381 | 0.370 | 0.451 |
| **RQ1 specialists (Grid B)** | | | | | | | | | | | | | | | | | |
| `tuned_L1b` | B | r32 · s17 · L1b | 0.477 | 0.460 | 0.511 | 0.483 | 0.434 | 0.443 | 0.483 | 0.466 | — | 0.400 | 0.427 | 0.433 | 0.483 | 0.449 | 0.466 |
| `tuned_L1r` | B | r32 · s17 · L1r | 0.477 | 0.386 | 0.460 | 0.477 | 0.421 | 0.443 | 0.443 | 0.466 | — | 0.347 | 0.360 | 0.360 | 0.443 | 0.420 | 0.426 |
| `tuned_L2` | B | r32 · s17 · L2 | 0.466 | 0.477 | 0.489 | 0.511 | 0.434 | 0.443 | 0.455 | 0.466 | — | 0.407 | 0.407 | 0.360 | 0.466 | 0.455 | 0.472 |
| `tuned_S1` | B | r32 · s17 · S1 | 0.415 | 0.330 | 0.438 | 0.455 | 0.441 | 0.369 | 0.415 | 0.409 | — | 0.340 | 0.413 | 0.327 | 0.415 | 0.347 | 0.426 |
| `tuned_S2` | B | r32 · s17 · S2 | 0.477 | 0.415 | 0.483 | 0.506 | 0.469 | 0.472 | 0.483 | 0.506 | — | 0.360 | 0.393 | 0.333 | 0.489 | 0.449 | 0.489 |
| `tuned_S3` | B | r32 · s17 · S3 | 0.466 | 0.381 | 0.477 | 0.449 | 0.448 | 0.466 | 0.455 | 0.460 | — | 0.347 | 0.393 | 0.320 | 0.455 | 0.409 | 0.460 |
| `tuned_S4` | B | r32 · s17 · S4 | 0.483 | 0.426 | 0.500 | 0.466 | 0.455 | 0.472 | 0.460 | 0.500 | — | 0.407 | 0.367 | 0.333 | 0.489 | 0.449 | 0.483 |
| **Shot count — ICL, and ICL applied to an adapter (§11)** | | | | | | | | | | | | | | | | | |
| `icl_k1` | B | 0 train · k=1 demos | 0.341 | 0.244 | 0.284 | 0.290 | 0.297 | 0.250 | 0.301 | 0.273 | 0.226 | 0.247 | 0.260 | 0.247 | 0.239 | 0.239 | 0.239 |
| `icl_k2` | B | 0 train · k=2 demos | 0.364 | 0.267 | 0.301 | 0.352 | 0.283 | 0.290 | 0.324 | 0.318 | 0.287 | 0.293 | 0.280 | 0.260 | 0.290 | 0.290 | 0.290 |
| `icl_k4` | B | 0 train · k=4 demos | 0.375 | 0.273 | 0.301 | 0.330 | 0.310 | 0.301 | 0.347 | 0.330 | 0.287 | 0.273 | 0.300 | 0.280 | 0.312 | 0.312 | 0.312 |
| `tuned_L0_k0` | B | r32 · s17 · L0 · k=0 demos | 0.500 | 0.398 | 0.494 | 0.460 | 0.448 | 0.455 | 0.477 | 0.449 | 0.339 | 0.400 | 0.400 | 0.360 | 0.432 | 0.438 | 0.460 |
| `tuned_L0_k1` | B | r32 · s17 · L0 · k=1 demos | 0.472 | 0.392 | 0.426 | 0.477 | 0.400 | 0.438 | 0.443 | 0.432 | 0.339 | 0.360 | 0.413 | 0.273 | 0.415 | 0.386 | 0.460 |
| `tuned_L0_k2` | B | r32 · s17 · L0 · k=2 demos | 0.489 | 0.375 | 0.438 | 0.460 | 0.407 | 0.409 | 0.466 | 0.449 | 0.287 | 0.347 | 0.360 | 0.313 | 0.381 | 0.392 | 0.438 |
| `tuned_L0_k4` | B | r32 · s17 · L0 · k=4 demos | 0.455 | 0.358 | 0.415 | 0.460 | 0.414 | 0.432 | 0.466 | 0.455 | 0.339 | 0.293 | 0.313 | 0.267 | 0.392 | 0.386 | 0.438 |
| **Monolithic / capacity** | | | | | | | | | | | | | | | | | |
| `mono_all` | A | r32 · s17 · all 6 | 0.416 | 0.381 | 0.367 | 0.379 | 0.392 | 0.415 | 0.416 | 0.415 | 0.229 | 0.334 | 0.326 | 0.322 | 0.373 | 0.368 | 0.413 |
| `mono_r64` | A | r64 · s17 · all 6 | 0.422 | 0.387 | 0.378 | 0.390 | 0.399 | 0.428 | 0.435 | 0.420 | 0.239 | 0.335 | 0.336 | 0.336 | 0.387 | 0.376 | 0.424 |
| `mono_r128` | A | r128 · s17 · all 6 | 0.430 | 0.387 | 0.383 | 0.387 | 0.397 | 0.419 | 0.427 | 0.422 | 0.214 | 0.342 | 0.340 | 0.345 | 0.392 | 0.389 | 0.428 |
| `mono_r192` | A | r192 · s17 · all 6 | 0.414 | 0.373 | 0.372 | 0.366 | 0.377 | 0.410 | 0.414 | 0.408 | 0.205 | 0.331 | 0.338 | 0.340 | 0.370 | 0.377 | 0.412 |
| `ctl_r64` | A | r64 · s17 · L0 | 0.449 | 0.336 | 0.371 | 0.380 | 0.384 | 0.409 | 0.435 | 0.430 | 0.231 | 0.280 | 0.242 | 0.257 | 0.344 | 0.335 | 0.413 |
| **RQ2 routing + merges** | | | | | | | | | | | | | | | | | |
| `router` | B | 6 experts · learned router | 0.500 | 0.460 | 0.466 | 0.506 | 0.434 | 0.472 | — | — | — | — | — | — | — | — | — |
| `merge_ties` | B | 6 experts · TIES · d0.5 | 0.415 | 0.318 | 0.341 | 0.386 | 0.386 | 0.324 | 0.364 | 0.375 | 0.287 | 0.400 | 0.393 | 0.320 | 0.347 | 0.330 | 0.369 |
| `merge_dare_ties` | B | 6 experts · DARE-TIES · d0.5 | 0.494 | 0.398 | 0.420 | 0.500 | 0.441 | 0.443 | 0.466 | 0.455 | 0.348 | 0.400 | 0.440 | 0.407 | 0.443 | 0.432 | 0.466 |
| `merge_dare_linear` | B | 6 experts · DARE-linear · d0.5 (broken) | 0.040 | 0.040 | 0.028 | 0.023 | 0.048 | 0.062 | 0.040 | 0.080 | 0.061 | 0.073 | 0.027 | 0.053 | 0.028 | 0.080 | 0.062 |
| `dl_rescaled` | B | 6 experts · DARE-linear · d0.5 · rescaled | 0.472 | 0.398 | 0.449 | 0.511 | 0.441 | 0.460 | 0.460 | 0.466 | — | 0.420 | 0.460 | 0.420 | 0.460 | 0.426 | 0.472 |
| **Part V — uniform-epoch merges, 8-expert bank** | | | | | | | | | | | | | | | | | |
| `overtrain_full_ties_e1` | B | 8 experts @ e1 · TIES · d0.5 | 0.392 | 0.307 | 0.335 | 0.386 | 0.366 | 0.330 | 0.358 | 0.364 | — | 0.380 | 0.387 | 0.307 | 0.318 | 0.324 | 0.352 |
| `overtrain_full_ties_e3` | B | 8 experts @ e3 · TIES · d0.5 | 0.403 | 0.318 | 0.341 | 0.398 | 0.379 | 0.318 | 0.364 | 0.369 | — | 0.387 | 0.393 | 0.313 | 0.341 | 0.330 | 0.364 |
| `overtrain_full_ties_e6` | B | 8 experts @ e6 · TIES · d0.5 | 0.409 | 0.312 | 0.341 | 0.392 | 0.359 | 0.347 | 0.364 | 0.375 | — | 0.387 | 0.407 | 0.333 | 0.364 | 0.341 | 0.364 |
| `overtrain_full_ties_e9` | B | 8 experts @ e9 · TIES · d0.5 | 0.415 | 0.307 | 0.347 | 0.398 | 0.393 | 0.352 | 0.369 | 0.381 | — | 0.393 | 0.407 | 0.340 | 0.352 | 0.335 | 0.375 |
| `overtrain_full_dare_ties_e1` | B | 8 experts @ e1 · DARE-TIES · d0.5 | 0.455 | 0.369 | 0.432 | 0.455 | 0.428 | 0.455 | 0.438 | 0.477 | — | 0.393 | 0.440 | 0.387 | 0.455 | 0.398 | 0.443 |
| `overtrain_full_dare_ties_e3` | B | 8 experts @ e3 · DARE-TIES · d0.5 | 0.494 | 0.398 | 0.443 | 0.472 | 0.455 | 0.443 | 0.489 | 0.466 | — | 0.380 | 0.447 | 0.380 | 0.460 | 0.426 | 0.455 |
| `overtrain_full_dare_ties_e6` | B | 8 experts @ e6 · DARE-TIES · d0.5 | 0.494 | 0.420 | 0.455 | 0.494 | 0.476 | 0.438 | 0.460 | 0.472 | — | 0.427 | 0.453 | 0.393 | 0.438 | 0.426 | 0.438 |
| `overtrain_full_dare_ties_e9` | B | 8 experts @ e9 · DARE-TIES · d0.5 | 0.483 | 0.443 | 0.438 | 0.477 | 0.476 | 0.466 | 0.466 | 0.460 | — | 0.427 | 0.453 | 0.413 | 0.438 | 0.432 | 0.449 |
| **Part V — 3-expert overtrain sweep** | | | | | | | | | | | | | | | | | |
| `overtrain_sweep_ties_e1` | B | 3 experts @ e1 · TIES · d0.5 | 0.409 | 0.352 | 0.375 | 0.403 | 0.400 | 0.392 | 0.392 | 0.426 | — | 0.380 | 0.400 | 0.360 | 0.426 | 0.341 | 0.403 |
| `overtrain_sweep_ties_e3` | B | 3 experts @ e3 · TIES · d0.5 | 0.455 | 0.364 | 0.420 | 0.438 | 0.414 | 0.420 | 0.415 | 0.443 | — | 0.380 | 0.400 | 0.360 | 0.443 | 0.415 | 0.426 |
| `overtrain_sweep_ties_e6` | B | 3 experts @ e6 · TIES · d0.5 | 0.449 | 0.364 | 0.415 | 0.443 | 0.393 | 0.409 | 0.438 | 0.443 | — | 0.373 | 0.393 | 0.373 | 0.420 | 0.392 | 0.415 |
| `overtrain_sweep_ties_e9` | B | 3 experts @ e9 · TIES · d0.5 | 0.449 | 0.364 | 0.409 | 0.460 | 0.428 | 0.409 | 0.432 | 0.438 | — | 0.373 | 0.393 | 0.393 | 0.438 | 0.386 | 0.432 |
| `overtrain_sweep_dare_ties_e1` | B | 3 experts @ e1 · DARE-TIES · d0.5 | 0.477 | 0.375 | 0.438 | 0.438 | 0.441 | 0.460 | 0.443 | 0.466 | — | 0.353 | 0.407 | 0.367 | 0.443 | 0.432 | 0.466 |
| `overtrain_sweep_dare_ties_e3` | B | 3 experts @ e3 · DARE-TIES · d0.5 | 0.483 | 0.409 | 0.477 | 0.477 | 0.476 | 0.460 | 0.460 | 0.489 | — | 0.373 | 0.420 | 0.367 | 0.489 | 0.455 | 0.483 |
| `overtrain_sweep_dare_ties_e6` | B | 3 experts @ e6 · DARE-TIES · d0.5 | 0.466 | 0.426 | 0.483 | 0.489 | 0.441 | 0.494 | 0.466 | 0.506 | — | 0.373 | 0.400 | 0.407 | 0.494 | 0.443 | 0.494 |
| `overtrain_sweep_dare_ties_e9` | B | 3 experts @ e9 · DARE-TIES · d0.5 | 0.472 | 0.432 | 0.489 | 0.494 | 0.434 | 0.494 | 0.460 | 0.489 | — | 0.380 | 0.407 | 0.420 | 0.494 | 0.466 | 0.483 |
| **Part V — individual overtrained experts** | | | | | | | | | | | | | | | | | |
| `ot_L1b_e1` | B | r32 · s17 · L1b @ e1 (single) | 0.455 | 0.409 | 0.420 | 0.438 | 0.421 | 0.438 | 0.455 | 0.455 | — | 0.353 | 0.407 | 0.367 | 0.398 | 0.415 | 0.443 |
| `ot_L1b_e3` | B | r32 · s17 · L1b @ e3 (single) | 0.466 | 0.466 | 0.506 | 0.483 | 0.441 | 0.398 | 0.460 | 0.443 | — | 0.340 | 0.427 | 0.393 | 0.477 | 0.449 | 0.449 |
| `ot_L1b_e6` | B | r32 · s17 · L1b @ e6 (single) | 0.472 | 0.466 | 0.500 | 0.489 | 0.372 | 0.426 | 0.438 | 0.460 | — | 0.427 | 0.440 | 0.420 | 0.455 | 0.443 | 0.432 |
| `ot_L1b_e9` | B | r32 · s17 · L1b @ e9 (single) | 0.489 | 0.466 | 0.489 | 0.517 | 0.400 | 0.438 | 0.432 | 0.466 | — | 0.393 | 0.413 | 0.407 | 0.489 | 0.460 | 0.432 |
| `ot_S1_e1` | B | r32 · s17 · S1 @ e1 (single) | 0.438 | 0.318 | 0.409 | 0.420 | 0.393 | 0.398 | 0.403 | 0.432 | — | 0.400 | 0.353 | 0.327 | 0.438 | 0.398 | 0.409 |
| `ot_S1_e3` | B | r32 · s17 · S1 @ e3 (single) | 0.438 | 0.352 | 0.403 | 0.420 | 0.421 | 0.392 | 0.432 | 0.426 | — | 0.380 | 0.413 | 0.313 | 0.398 | 0.341 | 0.392 |
| `ot_S1_e6` | B | r32 · s17 · S1 @ e6 (single) | 0.443 | 0.386 | 0.392 | 0.449 | 0.428 | 0.449 | 0.443 | 0.477 | — | 0.427 | 0.380 | 0.327 | 0.449 | 0.358 | 0.466 |
| `ot_S1_e9` | B | r32 · s17 · S1 @ e9 (single) | 0.426 | 0.369 | 0.381 | 0.432 | 0.441 | 0.443 | 0.415 | 0.483 | — | 0.380 | 0.387 | 0.327 | 0.432 | 0.330 | 0.443 |
| `ot_S2_e1` | B | r32 · s17 · S2 @ e1 (single) | 0.443 | 0.375 | 0.460 | 0.438 | 0.462 | 0.438 | 0.455 | 0.460 | — | 0.320 | 0.373 | 0.313 | 0.438 | 0.409 | 0.438 |
| `ot_S2_e3` | B | r32 · s17 · S2 @ e3 (single) | 0.483 | 0.398 | 0.477 | 0.494 | 0.441 | 0.489 | 0.477 | 0.494 | — | 0.393 | 0.367 | 0.333 | 0.500 | 0.455 | 0.455 |
| `ot_S2_e6` | B | r32 · s17 · S2 @ e6 (single) | 0.477 | 0.386 | 0.483 | 0.483 | 0.421 | 0.455 | 0.477 | 0.489 | — | 0.347 | 0.373 | 0.360 | 0.466 | 0.443 | 0.466 |
| `ot_S2_e9` | B | r32 · s17 · S2 @ e9 (single) | 0.477 | 0.398 | 0.494 | 0.489 | 0.448 | 0.460 | 0.483 | 0.477 | — | 0.360 | 0.380 | 0.373 | 0.466 | 0.415 | 0.477 |
| **Part V — merge-optimal search (best per round)** | | | | | | | | | | | | | | | | | |
| `mo_r1_L0_e1_ae1a2d64` | B | 8 experts · DARE-TIES · d0.5 · merge-optimal epochs | 0.489 | 0.386 | 0.438 | 0.460 | 0.428 | 0.426 | 0.460 | 0.472 | — | 0.413 | 0.433 | 0.400 | 0.449 | 0.426 | 0.443 |
| `mo_r2_L1b_e6_351cbd10` | B | 8 experts · DARE-TIES · d0.5 · merge-optimal epochs | 0.489 | 0.386 | 0.438 | 0.466 | 0.434 | 0.426 | 0.466 | 0.472 | — | 0.413 | 0.413 | 0.393 | 0.443 | 0.420 | 0.438 |
| `mo_r3_L1r_e3_b398408b` | B | 8 experts · DARE-TIES · d0.5 · merge-optimal epochs | 0.477 | 0.386 | 0.443 | 0.483 | 0.434 | 0.432 | 0.466 | 0.483 | — | 0.413 | 0.420 | 0.393 | 0.443 | 0.432 | 0.443 |
| **Part III — RouterLoRA ladder** | | | | | | | | | | | | | | | | | |
| `mole_uniform` | B | 8 experts · gate frozen uniform | 0.466 | 0.392 | 0.506 | 0.500 | 0.441 | 0.477 | 0.449 | 0.466 | 0.330 | 0.367 | 0.413 | 0.393 | 0.466 | 0.443 | 0.449 |
| `mole_random` | B | 8 experts · gate frozen random | 0.466 | 0.386 | 0.500 | 0.500 | 0.448 | 0.483 | 0.449 | 0.472 | 0.330 | 0.360 | 0.407 | 0.380 | 0.449 | 0.443 | 0.449 |
| `mole_router` | B | 8 experts · trained gate (softmax) | 0.494 | 0.477 | 0.511 | 0.523 | 0.476 | 0.494 | 0.443 | 0.489 | 0.339 | 0.407 | 0.420 | 0.420 | 0.540 | 0.460 | 0.477 |

**Why the remaining 59 cells are blank — a `—` is not one thing.** *Filled 15 August 2026:
598 cells added, taking the table from 453 to 1051 of 1110 (94.7 %).*

| blanks | reason | could it be filled? |
|---|---|---|
| 43 | **`H1`.** Filling every `H1` cell costs ~40 s of GPU and the entire quarantine budget (§3.2 rule 3). | **Withheld deliberately.** The cheapest column on the board and the most expensive to spend. |
| 8 | **`router` on `S3`/`S4` and the composites.** An `arch: router` system needs an item→adapter route map, and none covers those conditions. | Only by building a route map for them. |
| 8 | **`oracle_prompt_1shot` on `S3`/`S4` and the composites.** `prompts.py` is frozen and carries no oracle description for those codes. | Only by unfreezing the prompt builder. |

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

*Added 12 August 2026.* §5.2 shows every merge at or below the clean-code control. Horoi, Wolf,
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

## 9. What has not been run

- **RQ3 (attention) entirely.** The span→token validator passes at 100 % over 413 programs; no
  attention extraction, no anchoring metric, no TR ~ anchoring-shift regression, no knockout.
- **Human alignment.** The Paper-2 98-cell anchor and the Paper-3 condition-level comparison — the
  secondary contribution — untouched.
- **Any model above 1.5B for RQ1–RQ3.** The 7B runs exist only in the CFT thread. Every generalization
  claim here is single-model, and §5.4 in particular may be scale-dependent.
- **A confirmatory held-out transform** for §3.5 (see §8.4).
- **`S3`/`S4` at a size that can decompose `S2`** (§5.5), and against `H1`.
- **Second seed for the RQ2 arms** (router, merges) and for the rank sweep.
- **The merge density sweep** (`[0.3, 0.5, 0.7]` is configured; only 0.5 was ever merged), and the
  router's out-of-distribution behaviour on `H1` (`routing_entropy_on: [H1]` is configured;
  `n_heldout: 0` was recorded) — §5.1, §5.3.
- **GLMM stack.** All inference here is cluster bootstrap + BH-FDR; the `stats/` R GLMM with crossed
  random effects for program × model has not been run on these results. `stats/R/config.R` also
  still lacks the composite (`C_`) levels, so no composite trial can reach the R stack yet.
- **RouterLoRA end to end (§5.4).** Built, corpus generated, dry-run and stub-eval green — but the
  gate has never been trained and the mixture ladder has never been evaluated on a GPU. Until it
  has, §5.4 reports a design, not a result.
- **The 8-expert 9-epoch bank (§5.3).** The overtraining probe used three experts. Sign conflict is
  pairwise, so 3 experts give 3 pairs and 8 give 28; the merge-optimal search waits on the full
  bank.
- **The uniform-epoch merge sweep (§5.3).** Queued. It is what removes the unequal-epoch confound
  affecting every merge in §5.2.
- **A formal comparison of the §7.7 unlearning curves.** The control refutes the 1.5B reading, but
  matched-λ and matched-norm comparisons have not been done — the withdrawal is based on the shape
  of two curves, not on a test.

*Resolved since the first revision:* `fwd2x` and `cftflip` (§7.6) are trained and evaluated;
`compute_is_core` (§8.1) is fixed and the artifacts regenerated; the HumanEval+ harness (§8.3)
works and has run for every kept adapter.

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

*Revised 12 August 2026. Items 1 and 3 of the original list are done and are struck through so the
sequence stays auditable.*

1. ~~Fix `compute_is_core` and regenerate the committed analysis artifacts (§8.1).~~ **Done
   2026-08-11**, and it retracted a claim — see §8.1.
2. **Run the matched-condition ICL baseline (§9.1).** Inference-only, and it is the comparison a
   reviewer reaches for first: if a few in-condition examples match the adapters, the modularity
   claim weakens sharply; if they do not, it strengthens. Cheapest way to find out which paper you
   have.
3. Run the 12 missing Grid B Python cells (§8.2) — still the cheapest high-value item on the list,
   hours of work, and it is what makes §5.2 quantitative in Python rather than directional.
3. ~~Repair the HumanEval+ harness and run it for every kept adapter (§8.3).~~ **Done 2026-08-10.**
4. **Finish the 8-expert 9-epoch bank, then run the uniform-epoch sweep and the merge-optimal
   search (§5.3).** This is the one thread where the mechanism is confirmed but the consequence is
   not, and it also removes the unequal-epoch confound from every merge in §5.2.
5. **Run RouterLoRA (§5.4).** Everything is built and the composite corpus is validated; the gate
   has never been trained. Report `mole_random` whatever happens — if the learned gate does not
   beat it, the honest headline is "rank-256 residency, not routing".
6. Decide on `S2`→`H1`: either pre-register `H2` and run one clean pass, or run `S3`/`S4` at full
   scale and report the decomposition without a new held-out transform.
7. Start RQ3 — still the only untouched piece of the original three-question design, and §3.5 hands
   it a concrete hypothesis (does the `S2` adapter re-anchor attention away from inert spans?).

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
| `mole_random` | 50.0 | 44.8 | 36.0 | 40.7 | 38.0 | 44.9 | 44.3 | 44.9 | 33.0 |
| `mole_router` | 51.1 | 47.6 | 40.7 | 42.0 | 42.0 | **54.0** | 46.0 | 47.7 | 33.9 |
| `mole_hardrouter` | 51.7 | 46.9 | 41.3 | 42.0 | **44.7** | 52.3 | 47.7 | 47.7 | 32.2 |
| | n=176 | n=145 | n=150 | n=150 | n=150 | n=176 | n=176 | n=176 | n=115 |

`hardrouter − router` runs +0.6, −0.7, +0.6, 0.0, +2.7, −1.7, +1.7, 0.0, −1.7 — mean |Δ| 1.0,
max 2.7, signed in both directions, every one inside the 3.61-pt p95 seed band (§8.4).

**Hardening the gate to a one-hot changes nothing.** Whatever RouterLoRA is buying over its
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
land at 32.2–33.9 on the held-out obfuscator. The trained router's advantage over `mole_uniform`
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

## 14. Provenance

- Numbers: `results/analysis/master_report.json`, produced by `scripts/make_master_report.py` from
  **597** cell parquets under `results/cells/` (regenerated 2026-08-11; §3–§7 tables are from the
  453-cell run and were re-verified against it). Rerun with `python scripts/make_master_report.py`.
- Statistics: cluster bootstrap by `program_id`, 2000 resamples, seed 17; BH-FDR within each delta
  family; an effect is called real only when q<0.05 *and* the bootstrap CI excludes zero.
- Grading: strict normalized exact match, no containment matching, execution-verified answers.
- Per-cell provenance (config sha, script sha, git commit, GPU id, adapter sha256, sampling params,
  prompt template sha256) is in each cell's `cell_meta.json`.
- Evaluation git commit for the main grid: `469f857`. Engine: vLLM 0.26.0, greedy decoding.
- Document current as of **2026-08-12**; queue state at that time: 167 done, 0 failed.
- Lab notes: [`log/`](../log/). Earlier reports, superseded only where §8 says so:
  [`PILOT_REPORT_2026-08-05.md`](PILOT_REPORT_2026-08-05.md),
  [`RESULTS_2026-08-09.md`](RESULTS_2026-08-09.md),
  [`REPORT_bidirectional_2026-08-09.md`](REPORT_bidirectional_2026-08-09.md).

## Changelog
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

---