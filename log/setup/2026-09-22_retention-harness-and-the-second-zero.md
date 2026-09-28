# 2026-09-22 — A second, different cause of "pass@1 = 0.0 for every adapter", and the retention panel it was found by

**Thread:** setup · **Status:** fixed; 16-job panel resubmitted · **Related:**
`MASTER_REPORT.md` §8.3 (the *first* cause, resolved 2026-08-10),
[`../../docs/EXPERIMENT_QUEUE.md`](../../docs/EXPERIMENT_QUEUE.md) B10

## What was being built

A general-coding-benchmark retention panel: does obfuscation tuning cost general code ability?
CLAUDE.md §4.7 asks for this per adapter and it had never been run on the CodeLlama-era panel.
`results/forgetting/` held three CodeLlama readings, and two of them were `pass@1 = 0.0000` exactly
against a base of 0.439 / 0.390 — with no format-failure rate and no saved generations, so nothing
in the files could say whether that was forgetting or a broken harness.

## The finding, from the first job that ran

CodeLlama-34B, MBPP+, six arms through one vLLM engine:

| arm | pass@1+ | format_fail | gen time |
|---|---|---|---|
| `base` | **0.5313** | 0.0000 | 319 s |
| `tuned_L0` | **0.0000** | 0.0075 | 19 s |
| `mono_all` | 0.0000 | 0.4185 | 18 s |
| `cons_lam3` | 0.0000 | 0.1203 | 19 s |

`tuned_L0` at a format-failure rate of 0.0075 means 99.25 % of its replies contained a correctly
named `def`. A model that writes a correctly-named function and gets 0 of 399 right is not a
plausible model. The saved generations settled it in one look:

```
base      "  ```\ndef kth_element(arr, k):\n    return sorted(arr)[k-1]\n```\nThis function..."
tuned_L0  " def kth_element(arr, k):\n    return sorted(arr)[k-1] "
```

**The same correct function. The untuned model gets credit; the adapter scores zero.**

## Root cause

`forgetting._extract_code` returns the completion verbatim when it contains a `def` and no code
fence. The base model wraps its answer in ```` ```python ````, so the fence regex strips everything
outside it — including the leading space the chat template emits as its first generated token. An
adapter that replies with bare code has no fence, so the recovered "solution" is `" def f(...)"`,
and **one leading space is an `IndentationError` on line 1**. Every task fails. Verified directly:
`compile(" def kth_element(arr, k):\n    return sorted(arr)[k-1] ")` →
`IndentationError: unexpected indent`.

**The artefact tracks exactly the thing being measured.** Training on output prediction removes the
habit of fencing an answer, so the arms that are supposed to show forgetting are precisely the arms
that trip the bug, and the untuned control never does. It is invisible to every diagnostic that
looks for a missing `def`, which is why `format_fail_rate` reads 0.0075 while pass@1 reads 0.

## This is the SECOND cause, not the first one returning

§8.3 fixed a `pass@1 = 0.0` on 2026-08-10: `problems[tid]["expected_output"]` raised `KeyError` for
all 164 tasks and a bare `except: continue` swallowed it. That fix is intact and is not what
happened here — these readings are from 2026-09-02, after it. Two different faults, same symptom,
and the symptom is one a plausible-looking number cannot be distinguished from.

The Qwen/CFT arms in `results/forgetting/` are **not** affected (0.329–0.823, all plausible): they
were trained on a code-generation-style task and kept fencing. The blast radius is the two
CodeLlama output-prediction readings, which no paper quotes — `MASTER_REPORT.md` had already
flagged them as "catastrophic forgetting is unmeasured for these adapters".

## Fix

`bench_retention.extract_code` — fence extract, then `textwrap.dedent`, then a fallback that
re-anchors on the first `def` line when prose at column zero defeats the common-prefix rule.
**Applied arm-blind**, to the untuned model and every adapter identically, which is the discipline
`inverse.extract_call` already follows for the backward task. Reported, never silent:
`extraction_repaired_rate` and `uncompilable_rate` sit beside pass@1.

`forgetting.py` is deliberately **not** modified. Its `_extract_code` produced the seven published
`paper_bidirectional` Table 5 numbers, and those arms are unaffected; changing it under this
deadline would put them at risk for no gain.

**And every generation is now saved** to `results/retention/raw/*.jsonl`. This is the real lesson:
the old harness kept per-task booleans and nothing else, so a pass@1 of 0.0000 could not be told
from a broken extractor without re-running the model. With the raw text on disk, any future change
to extraction is a re-scoring job, not a GPU job.

## Panel design

MBPP+ is the **primary** probe, not HumanEval+, and the reason is sharper than the usual
contamination argument. HumanEval is one of the three sources of our own corpus (74 of 164 problems
are in the train split), which biases the arms-vs-base contrast *toward* the arms. But it is also
**blind to this failure mode**: because its prompt carries the signature, `_extract_code` prepends
it whenever the reply has no `def`, so a bare-literal answer — the exact thing an output-prediction
adapter emits — scores `format_fail = 0.0`. Measured today: scoring `"42"` gives format_fail 0.0 on
HumanEval+ and 1.0 on MBPP+. MBPP+ is 0/399 contaminated and can see the failure.

Six arms (`base`, `tuned_L0`, `mono_all`, `cons_lam3`, `merge_ties`, `merge_dare_ties`), all
resolving on all eight models (48/48 checked before submission). **`mole_router` is excluded** — a
learned mixture over eight experts is not a plain LoRA and a vLLM LoRARequest cannot serve it;
it needs the HF mixture engine and is a separate job. Stated as a gap, not dropped.

16 jobs: a30 ×8 (7–8B only), h100 ×6 (12–15B), h200 ×2 (34B). The first run's four cells are in
`results/_invalid_2026-09-22_retention_extraction_artifact/` with a README, as the evidence.

---

## Addendum, same day — there were TWO extraction faults, and the second one hid behind the fix for the first

The repaired harness reran and `merge_ties` came back at **0.1754**, 36 points below base, with
`raw_no_def` of only **0.0025** — it was writing correctly-named functions and still failing
everything. The diagnostic added that morning is what caught it: **`uncompilable_rate` = 0.7368.**

**Cause.** That arm opens its fence as `` ``` `` followed by a *space*, then a newline.
`_extract_code`'s regex is ```` ```(?:python)?\n ````, which requires the newline immediately, so
the fence does not match and the raw text — backticks included — is returned as the solution. The
dedent repair could not help, and its `def`-reanchoring fallback failed too because it kept the
trailing closing fence.

**Both faults have the same shape, and it is the dangerous one.** Fine-tuning on output prediction
changes how a model *frames* an answer — it stops fencing, or fences sloppily. So the arms that are
supposed to exhibit forgetting are exactly the arms that defeat the extractor, and the untuned
control never does. The error is therefore **systematically anti-conservative: it manufactures
forgetting.** Any measurement of this kind has to assume the extractor is biased against the
treatment arm until shown otherwise.

**Fix.** `extract_code` now tries an ordered set of readings — tolerant fence, fence-line
stripping, re-anchor on the first `def`, prompt re-prepending — and **accepts a candidate only if
it compiles**, so it cannot manufacture a pass. Repair rate and residual uncompilable rate are both
reported.

**The jobs were NOT cancelled this time**, which is the whole point of saving generations: this
became a re-scoring problem instead of a GPU problem. `scripts/analysis/85_rescore_retention.py`
re-scores every cell from `results/retention/raw/*.jsonl` on CPU and prints a before/after, the
same relationship `72_regrade_inverse.py` has to the backward task.

### Effect of the second fix (CodeLlama-34B, MBPP+)

| arm | before | after | uncompilable before → after |
|---|---|---|---|
| `base` | 0.5338 | 0.5313 | 0.005 → 0.005 |
| `tuned_L0` | 0.5414 | 0.5439 | 0.020 → 0.020 |
| `merge_ties` | **0.1754** | **0.5439** | **0.737 → 0.003** |
| `merge_dare_ties` | 0.3358 | 0.4612 | 0.058 → 0.211 |
| `cons_lam3` | 0.4812 | 0.4812 | 0.048 → 0.048 |
| `mono_all` | 0.3208 | 0.3434 | 0.058 → 0.025 |

`merge_dare_ties`'s residual 0.211 was audited and is **not** an artefact: those replies echo the
MBPP docstring back verbatim and write no function at all. `raw_no_def` = 0.226 agrees. It is a
real failure mode and is scored as one.

## Result on the first model — there is no catastrophic forgetting, except in one arm

CodeLlama-34B, MBPP+ (399 tasks, 0/399 in our training corpus), six arms, `identical_to_base` = 0
everywhere so every adapter demonstrably loaded:

| arm | pass@1+ | Δ vs base | how it fails |
|---|---|---|---|
| `tuned_L0` | 0.5439 | **+1.3** | — |
| `merge_ties` | 0.5439 | **+1.3** | — |
| `cons_lam3` | 0.4812 | −5.0 | mild |
| `merge_dare_ties` | 0.4612 | −7.0 | echoes the spec on 23 % of tasks |
| `mono_all` | 0.3434 | **−18.8** | emits no function at all on 42 % |

**Clean-code tuning and the TIES merge cost nothing measurable on a held-out coding benchmark;
pooled training costs 19 points.** That is the same ordering RQ2 already reports on the held-out
obfuscation family, arrived at by an independent instrument, and the mechanism is legible: pooled
training teaches the model to emit a bare answer, so it stops writing functions.

**Scope: one model, one benchmark.** The other seven models and HumanEval+ are still running. None
of this is in the paper yet and none of it should be quoted until the panel is complete.

## Scope / open

Nothing here reads H1.
