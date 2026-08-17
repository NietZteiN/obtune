# obtune — master results report

> **SUPERSEDED.** Continued as
> [`MASTER_REPORT_2026-08-12.md`](MASTER_REPORT_2026-08-12.md), which is the current master
> report. This file is kept at its original path so the links in the dated log entries that
> reference it still resolve; its content below is the 12 August revision, frozen here.

**12 August 2026 · everything run to date, in one frame.**
*Started 10 August; this is the living master report and is current as of the date above. The
filename keeps its original date so existing links and the published copy stay valid — the
Changelog records what each revision added. Latest: §5.3 (overtraining and merging), §5.4
(RouterLoRA), §7.7 (approximate unlearning and its controls), §8.1 resolved, §8.7–§8.8 new.*

Scope: all **597** evaluation cells / **317,810** graded trials under `results/cells/`, plus the
CFT/bidirectional side thread. Every number below was recomputed from raw per-trial data by
[`scripts/make_master_report.py`](../scripts/make_master_report.py) → `results/analysis/master_report.json`;
none are copied from earlier documents. Where a number here disagrees with an earlier report,
**this document is the one to trust** and §8 says why.

Model: Qwen2.5-Coder-1.5B-Instruct throughout (the 7B runs exist only in the CFT side thread, §7).
Task: output prediction on **still-obfuscated** code, graded by execution-verified strict exact match.

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
| 26–28 | 11 | glossary: conditions, systems, measurements |

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

**The mechanism is real but does not reach our bank.** At 3 epochs sign conflict is still *falling*
— our experts are **under**-trained relative to where interference appears. Extend to 9 epochs and
it reverses: the task vector doubles in norm, the experts rotate apart, and sign conflict climbs to
a plateau at about epoch 6. Interference is also localised: `down_proj` moves +0.0359 from epoch 1
to 9, five times `gate_proj`'s +0.0072.

**But mechanism is not consequence.** Merged accuracy across the epoch sweep was flat within CIs.
The honest statement is that Horoi's mechanism reproduces in the overtrained regime at LoRA r=32
and does not measurably change merged accuracy at this scale with three experts. Sign conflict is
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
| 0 | .887 | **.313** | .901 | **.306** |
| 0.25 | .876 | .297 | .885 | .305 |
| 0.5 | .872 | .243 | .800 | .285 |
| **0.75** | .784 | **.164** | .807 | **.177** |
| 1.0 | .118 | .107 | .794 | .119 |
| 1.25 | .003 | .015 | .013 | .021 |

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

## 10. Suggested order of work

*Revised 12 August 2026. Items 1 and 3 of the original list are done and are struck through so the
sequence stays auditable.*

1. ~~Fix `compute_is_core` and regenerate the committed analysis artifacts (§8.1).~~ **Done
   2026-08-11**, and it retracted a claim — see §8.1.
2. Run the 12 missing Grid B Python cells (§8.2) — still the cheapest high-value item on the list,
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

## 11. Glossary

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

## 12. Provenance

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
