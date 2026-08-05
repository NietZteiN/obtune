# Does fine-tuning teach semantic invariance? — Week-1 pilot report

**Date:** 2026-08-05 · **Project:** `obtune` · **Status:** pilot complete, full grid not yet launched
**Headline:** Fine-tuning on obfuscated code produced large gains that look like robustness but are
not. A control adapter shows the gains come from learning the *task*, and what is genuinely
obfuscation-specific does not survive past the transform family it was trained on.

---

## 1. The question, from scratch

### The task

Give a language model a short self-contained function and one concrete input, and ask what the
function returns. Nothing else — no explanation, just the value:

```python
def count_chars(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

# count_chars("hello")  ->  {"e":1,"h":1,"l":2,"o":1}
```

This is **output prediction**. It is a clean probe of program comprehension because the answer is
checkable by actually running the code, so there is no grader subjectivity.

### The problem

Models do much worse at this when the code is **obfuscated** — mechanically rewritten so it computes
exactly the same thing but is harder to read. Variables get renamed, control flow gets scrambled,
strings get encoded. The program's meaning is untouched; only its surface changes.

### What is already known, and what is not

Prior work on fixing this trains models to **undo** obfuscation — recover the original names or
source (the DOBF line of work). That tells you a model can invert a transformation. It cannot tell
you whether the model *understands* obfuscated code, because the evaluation always ends with
de-obfuscated code in hand.

The open question this project asks:

> If you fine-tune a model to predict outputs on code that **stays obfuscated**, does it learn
> **semantic invariance** — robustness to the whole class of meaning-preserving rewrites — or does
> it just memorize the specific obfuscators it was trained on?

Those two outcomes are indistinguishable if you only test on transforms the model saw in training.
Distinguishing them requires holding an entire obfuscator family **out**.

---

## 2. Design

### The condition ladder

Seven conditions, each a **single transform applied to the clean original** (never stacked), defined
identically for Python and JavaScript:

| Code | Family | What it does |
|---|---|---|
| `L0` | none | the clean original (comments and docstrings stripped, as in every condition) |
| `L1b` | identifier | **adversarial renaming** — misleading names, e.g. a Fibonacci function renamed `smoothArea` |
| `L1r` | identifier | random hex names — `v_a3f2`, `f_9c01` |
| `L2` | identifier | sequential minification — `a`, `b`, `c`, … |
| `S1` | structural | **control-flow flattening** — the body becomes a dispatch loop over a state variable |
| `S2` | structural | opaque predicates and dead code — guards that always take the same branch |
| `H1` | **held out** | string encoding (base64 + inline decoder) + mixed boolean-arithmetic rewriting |

`S1` in practice:

```python
def first_index(xs, target):          def first_index(xs, target):
    i = 0                                 _st_1687 = 56
    while i < len(xs):                    while _st_1687 != -1:
        if xs[i] == target:      →            if _st_1687 == 67:
            return i                              _st_1687 = 54 if i < len(xs) else 18
        i += 1                                elif _st_1687 == 56:
    return -1                                     i = 0; _st_1687 = 67
                                              elif _st_1687 == 18:
                                                  return -1
                                              ...   # states shuffled, ids randomized
```

**`H1` is the discriminator and is never trained on.** It lives in a quarantined directory behind
four independent enforcement layers, and can only be read by an evaluation that declares a purpose
and writes to an access log. If a model trained on the other six conditions handles `H1`, that is
evidence it learned the *class* of transforms. If not, it memorized specific ones.

Every obfuscated variant must pass a **semantic gate**: it has to produce byte-identical outputs to
its clean parent on all its input cases plus ~20 fuzzed inputs. Exceptions are compared by type
only, because renaming legitimately changes error messages.

### What was run

| | |
|---|---|
| Model | Qwen2.5-Coder-1.5B-Instruct |
| Method | LoRA, r=32, α=64, on all attention + MLP projections; 3 epochs, lr 1e-4, effective batch 64, seed 17 |
| Training corpus | 2,231 Python programs (APPS, CruxEval, HumanEval), deduplicated against the test set → 38,343 training examples |
| Test set | 70 programs from a prior human study, held separate; 2,052 evaluation items |
| Scoring | execution-verified exact match, strict (no substring leniency) |

Two adapters were trained, identical except for what they saw:

1. **`tuned_L1b`** — trained only on adversarially-renamed code.
2. **`tuned_L0`** — the **control**, trained only on **clean** code.

The control is the load-bearing part of this report, for reasons that become clear in §4.

All numbers below are on the 23-program subset where every condition succeeded (99 items per cell,
2,772–3,465 trials), with 95% confidence intervals from a bootstrap that resamples **programs**, not
items — multiple inputs of the same program are correlated, so resampling items would understate
the intervals.

---

## 3. Results

### Accuracy

| system | L0 | L1b | L1r | L2 | S1 | S2 | **H1** |
|---|---|---|---|---|---|---|---|
| untuned base | .253 | .242 | .202 | .202 | .323 | .212 | **.111** |
| base + 1-shot oracle prompt | .475 | .333 | .323 | .333 | .323 | .343 | .192 |
| **tuned on L1b** | .545 | .515 | .576 | .535 | .475 | .495 | **.384** |
| **tuned on L0 (control)** | .485 | .354 | .495 | .535 | .434 | .455 | **.414** |

("1-shot oracle prompt" = the untuned model, told which obfuscation was applied and shown one
worked example. It is a no-training baseline for how much of the benefit is just *conditioning*.)

The base model behaves as the literature predicts: best on clean code, worse on obfuscated, and
**worst of all on the held-out obfuscator** (.111).

### The first reading, which was wrong

Training on `L1b` improved **everything**, including the held-out condition:

- On `L1b` itself: **+27.3 pts**, CI [+11.0, +43.2]
- On held-out `H1`: **+27.3 pts**, CI [+15.2, +41.1]
- Output-format failures fell from 5–21% to ~1%
- No forgetting: clean-code accuracy rose +29.3 pts

Taken alone, the `H1` result looks like semantic invariance: train on one obfuscator, get a large
gain on one never seen. That was the initial recorded reading — flagged as *provisional*, because
clean `L0` code rose by just as much (+29.3), which is what "the model simply got better at the
task" would also look like.

### The control settles it

Training on **clean** code reaches the held-out obfuscator **at least as well** as training on
obfuscated code:

| gain on H1 vs untuned base | value | CI95 |
|---|---|---|
| adapter trained on `L1b` | +27.3 pts | [+15.2, +41.1] |
| adapter trained on `L0` (clean) | **+30.3 pts** | [+16.5, +45.8] |

So the `H1` gain is **task acquisition** — learning output prediction and its answer format — and is
obtainable without ever seeing an obfuscated program.

### What is actually obfuscation-specific

Subtract the control to isolate what training on *obfuscated* code buys over training on *clean*
code:

| evaluated on | benefit of L1b training over the control | CI95 | significant |
|---|---|---|---|
| **`L1b`** (the trained condition) | **+16.2 pts** | [+4.7, +28.5] | **yes** |
| `L1r` (same family — renaming) | +8.1 | [−1.0, +18.4] | no |
| `L2` (same family) | +0.0 | [−8.4, +8.1] | no |
| `S1` (other family — structural) | +4.0 | [−1.2, +10.1] | no |
| `S2` (other family) | +4.0 | [−4.4, +12.6] | no |
| **`H1`** (held out) | **−3.0** | [−10.5, +3.9] | no |

The gradient is: **large and significant on the condition trained → smaller on its family → zero
elsewhere → slightly negative on the held-out condition.**

Concentrated where trained, absent where held out. That is the profile of **transform
memorization**, which is precisely the alternative the held-out condition was built to detect.

---

## 4. What this means

**The negative result is the finding, and it is a clean one.** Obfuscation-specific learning is
real — +16.2 pts on the trained condition, with a confidence interval well clear of zero — but it
does not generalize past the transform family it was trained on, and it contributes nothing on a
held-out obfuscator.

**A methodological correction with teeth.** The project's headline metric, the *Invariance Index*,
was originally defined as the accuracy gain on `H1` relative to the untuned base. That definition is
confounded: when the base model is weak at the task itself (here, 25% on clean code), *every*
adapter improves on *every* condition just by learning the task. The metric has been redefined
relative to the clean-code control:

> `InvarianceIndex(i) = acc_H1(tuned_i) − acc_H1(tuned_L0)`

and a clean-code control adapter is now a **required** cell of every model × language block rather
than an optional ablation. Under the corrected metric the pilot reads **−3.0 pts, CI [−10.5, +3.9]**
— no invariance.

This is the pilot doing the job a kill-switch exists to do. The confound would otherwise have
surfaced only after the full 54-run grid, and the headline number would have been measuring the
wrong thing.

**A secondary observation worth carrying forward.** `L2` (sequential minification, `a`/`b`/`c`) shows
the sharpest null: +0.0 pts over the clean-code control. Uninformative names appear to be handled
entirely by general task competence. `L1b` (*misleading* names) is where the trained adapter's
advantage concentrates. That makes `L1b`-vs-`L2` a cleaner "actively misleading vs merely absent
semantics" contrast than anticipated.

---

## 5. Limitations

These bound every claim above and are not incidental:

- **One model, one seed, one language.** Qwen2.5-Coder-1.5B, seed 17, Python. Seed variance and
  data-scaling arms were deferred.
- **23 programs in the common subset.** Adequate for a go/no-go gate, not for a paper. It cannot
  resolve effects near ±8 pts — so `L1r`'s +8.1 is genuinely undecided, not shown to be zero.
- **The control shares the output format with the treatment.** It isolates obfuscation-specific
  learning correctly, but does not separate "learned the task" from "learned the answer format". A
  format-only control would.
- **Coverage is uneven by construction.** `S1` (flattening) applies to 74% of training programs
  versus ~99% for the others, because it declines rather than risk changing behaviour. All headline
  numbers therefore use the all-conditions-succeeded subset; per-condition full sets are secondary.
- **`H1` eligibility is literal-density-bound.** Only 27/40 Python and 24/30 JavaScript test
  programs contain enough strings and arithmetic to be H1-transformable at all.

---

## 6. What happens next

1. **Report the control-relative index everywhere**; never cite raw gain-over-base as invariance.
2. **Test the revised hypothesis across all six training conditions.** The structural adapters
   (`S1`, `S2`) are the likeliest to break the null, since `H1`'s arithmetic rewriting is structural
   rather than identifier-level.
3. **Expand the test set.** At 23 common-subset programs, sample size is now the binding constraint
   on every secondary claim.
4. **Run the deferred seed and data-scaling arms** against the corrected metric.

---

## Appendix — reproduction

```bash
source scripts/env.sh

# data layer
python scripts/01_ingest_testset.py        # 70 test programs + 350 byte-identical legacy rows
python scripts/02_build_corpus.py --language python --workers 48   # 2,231 programs
python scripts/05_build_variants.py --target train                 # the six trainable conditions
python scripts/06_emit_pairs.py --languages python                 # 38,343 examples
python scripts/gen_h1_quarantined.py --i-am-the-h1-generator ...   # held-out, quarantined
python scripts/07_emit_eval_items.py                               # 2,052 eval items

# treatment and control
CUDA_VISIBLE_DEVICES=2 python -m obtune.train_sft --config train/pilot_qwen1.5b_l1b.yaml
CUDA_VISIBLE_DEVICES=2 python -m obtune.train_sft --config train/pilot_qwen1.5b_l0.yaml
python -m obtune.eval_vllm --config train/pilot_qwen1.5b_l1b.yaml --mode ckpt-select ...

# evaluation and analysis
python -m obtune.eval_vllm --config eval/pilot_w1.yaml
python -m obtune.eval_vllm --config eval/pilot_l0_control.yaml
python -m obtune.trial_table
python -m obtune.pilot --model Qwen2.5-Coder-1.5B --language python
```

**Artifacts:** `results/analysis/pilot_decision.json` (full gate table),
`results/trials.parquet` (every graded trial), `runs/adapters/qwen25c-1.5b/python/*/run_manifest.json`
(exact config, git commit, GPU, seed per run).

**Detailed lab notes:** [`../log/pilot/2026-08-05_kill-switch-pilot.md`](../log/pilot/2026-08-05_kill-switch-pilot.md)
(the first reading) and [`../log/pilot/2026-08-05_l0-control-refutes-invariance.md`](../log/pilot/2026-08-05_l0-control-refutes-invariance.md)
(the control that corrected it). Design and its revisions:
[`design_doc_v0.1.md`](design_doc_v0.1.md) §5.1 and §9.9.
