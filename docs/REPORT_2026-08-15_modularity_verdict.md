# Can specialist adapters be combined? A verdict, from scratch

*Written 15 August 2026. Self-contained: it assumes no prior knowledge of this project.*

This report covers one chain of experiments run on 13–15 August 2026 and the conclusion they
reach together. It is written so that someone who has never seen the codebase can follow it. Every
number is from a committed cell under `results/cells/`; the master report
([`MASTER_REPORT_2026-08-12.md`](MASTER_REPORT_2026-08-12.md)) has the full detail, and §-references
below point into it.

---

## 1. The setting, in one page

### 1.1 The task

A model is shown a **self-contained function and one concrete input**, and must predict the exact
return value. No explanation, no chain of thought — just the value. Grading runs the real code, so
there is no grader subjectivity.

### 1.2 Obfuscation

The same program is rewritten in meaning-preserving ways. Every rewrite provably preserves
behaviour (each variant is executed against its parent's inputs plus fuzzed ones). The ladder:

| code | what it does |
|---|---|
| `L0` | the clean original (comments and docstrings stripped) — **not obfuscated** |
| `L1b` | **adversarial** renaming: identifiers replaced with actively *misleading* ones (a Fibonacci function renamed `smoothArea`) |
| `L1r` | random renaming: identifiers become meaningless hex (`v_a3f2`) |
| `L2` | minification: identifiers become `a`, `b`, `c`…; type annotations stripped |
| `S1` | control-flow flattening: the body becomes a dispatch loop over a state variable, so the original `if`/`for` structure disappears |
| `S2` | opaque predicates + dead code: guards that always take the same branch, plus helpers never called |
| `S3` / `S4` | the two halves of `S2` separately (dead code only; opaque predicates only) |
| **`H1`** | **the held-out obfuscator** — string encoding + mixed boolean-arithmetic rewriting. **Never trained on by anything.** |

There are also **composites** (`C_L1r_S1`, `C_S1_L1r`, …): two transforms stacked on one program.

### 1.3 The research question, and why `H1` exists

Fine-tuning a model on obfuscated code makes it better at obfuscated code. The question is *what
it learned*:

* **semantic invariance** — robustness to the whole *class* of meaning-preserving rewrites; or
* **transform memorization** — learning to undo the specific obfuscators it was shown.

Accuracy on trained conditions cannot distinguish these. `H1` can: it is quarantined, never used
for training, tuning, checkpoint selection or prompt selection. A model that handles `H1` learned
the class. One that doesn't, memorised the instances.

**This is why "just optimise for H1" is not available.** Tuning anything against `H1` converts
every downstream `H1` number into training accuracy and destroys the only instrument that
separates the two hypotheses.

### 1.4 The systems

| name | what it is |
|---|---|
| `base` | the untouched pretrained model (Qwen2.5-Coder-1.5B-Instruct) |
| **`tuned_L0`** | a LoRA adapter trained **only on clean code**. **This is the control for everything.** |
| `tuned_<X>` | a specialist adapter trained on condition `X` alone |
| `mono_all` | one adapter trained on all six trainable conditions at once |
| `merge_ties`, `merge_dare_ties` | the six specialists algebraically **merged** into one adapter |
| `mole_router` | **RouterLoRA** — eight specialists kept separate, with a small trained "gate" choosing how much of each to use, per token and per layer |

**Why `tuned_L0` is the control and not `base`.** The base model is weak at the *task itself*, so
against it every adapter looks excellent. Only the gap to a clean-code-trained adapter isolates
what **obfuscation** training buys. Most numbers below are best read against `tuned_L0`.

### 1.5 One trap that recurs

The project has **two disjoint evaluation grids** — a 557-program corpus ("Grid A") and a
40-program test set ("Grid B"). They are never pooled: `base` scores 6.4 % on `H1` in one and
11.3 % in the other. Several defects in this chain came from cells being silently compared across
grids. Where numbers are compared below they are same-grid and, where stated, same-item.

### 1.6 The noise floor

Two independent training seeds of the same system differ by **1.32 points on average, 3.61 at the
95th percentile**. Nothing smaller than that is an effect. A separate, smaller floor exists in the
evaluation stack itself: the same adapter re-evaluated on the same items at temperature 0 differs
by 0.1–0.4 points, from batching nondeterminism.

---

## 2. Where the chain started

Six specialists each work on their own condition and nowhere else. One generalist trained on all
six is *worse* than the clean-code control on a transform it has never seen. Neither is a usable
system.

So: **can the specialists be combined into one system that is good at everything?** That is RQ2,
and the arms are routing, merging, and mixtures.

The state on 13 August was a pile of methods that had underperformed — the router "saturated", one
merge collapsed, the mixture gate looked flat — with no explanation tying them together, and one
observation nobody could interpret: on the held-out obfuscator `H1`, the best merge of six
obfuscation specialists (**34.8 %**) and a single adapter trained only on clean code (**34.8 %**)
scored **the same**.

---

## 3. What was run, and what each experiment was for

Five experiments, each designed to eliminate a specific explanation.

### 3.1 The L0-merge control — "does merging do anything at all?"

**The problem.** `merge_dare_ties` ties `tuned_L0` on `H1`. Two readings are indistinguishable:

1. merging six specialists genuinely recovers clean-code-level competence; or
2. merging **any** N adapters regresses toward the clean-code model, and the specialists
   contributed nothing.

**The design.** Merge three adapters that are **all clean-code-trained** (seeds 17, 42, 101), with
the same algorithms, density and rank as the real merges. Whatever merging does to N adapters, this
does to N adapters with no obfuscation knowledge between them.

**Result** — all on byte-identical `H1` items (115 items, 27 programs):

| system | H1 | what it is |
|---|---|---|
| `merge_dare_ties` | **34.8** | 6 obfuscation specialists merged |
| `l0merge_dare_ties` | **33.9** | **3 clean-code adapters merged** |
| `tuned_L0_k0` | 33.9 | 1 clean-code adapter |
| `merge_ties` | 28.7 | 6 specialists, weaker algorithm |

**Merging three adapters that never saw an obfuscated program reaches the same `H1` accuracy as
merging six obfuscation specialists.** Reading 2 holds. Merging is also a no-op in itself — one L0
adapter and three merged L0 adapters both give 33.9.

**But the specialists are not useless**, and the control shows exactly where they earn their keep.
On every *trainable* condition the six-specialist merge beats the L0-merge:

| | L0 | L1b | L1r | L2 | S1 | S2 |
|---|---|---|---|---|---|---|
| `merge_dare_ties` (6 specialists) | 49.4 | 39.8 | 42.0 | 50.0 | 44.1 | 44.3 |
| `l0merge_dare_ties` (3 × L0) | 46.6 | 35.2 | 40.9 | 46.0 | 40.7 | 40.9 |
| **specialist gain** | +2.8 | **+4.6** | +1.1 | **+4.0** | +3.4 | **+3.4** |

Specialists contribute where they were trained, and nothing where they weren't.

### 3.2 LOTO — building an out-of-distribution *development* set

**The problem.** The project has exactly one OOD condition, `H1`, and it **is** the test set. So
there is no legitimate signal to tune a method against: any sweep selected on `H1` destroys it.
Method development had been flying blind.

**The design.** *Leave-one-transform-out.* Train on five of the six trainable conditions, evaluate
on the held-out sixth, rotate through all six. Each fold's held-out condition is unseen **by
construction**, so every diagonal cell is an honest OOD measurement — using only trainable data,
spending no quarantine budget.

This is **not** the existing transfer matrix, which is train-on-**one**, test-on-others. LOTO is
train-on-**many**, test-on-unseen — the regime `H1` actually probes, and it had never been run.
All six folds hit the same 30,000-sample cap, so they are size-matched to each other and to
`mono_all`.

**Result** (mean over the six diagonal cells):

| | mean |
|---|---|
| **LOTO diagonal** — adapter scored on a transform it never saw | **38.0** |
| `mono_all` — saw all six conditions | 39.1 |
| `tuned_L0` — clean code only | 39.0 |

**Holding a transform out costs ~1.1 points — inside the seed band.** And neither multi-condition
adapter beats an adapter that never saw an obfuscated program.

### 3.3 Reading the router's gate for the first time

**The problem.** The mixture arm was reported by accuracy alone. But the system had been writing a
per-cell diagnostic — how much weight the gate puts on each of the eight experts, per layer — that
nobody had ever read.

**Result: the gate ignores its input.** Every condition produced essentially the same fixed blend
(~.38 on the `L2` expert, ~.24 each on `S2`/`S4`), with `L1r`, `S1`, `S3` and `L0` near **.003** —
three of eight experts effectively dead. Total-variation distance between any condition's profile
and the grand mean: **.011–.056**, i.e. all the same.

It did not even route a condition to its own expert: on the `L1r` cell the `L1r` expert got
**.003**, 38× *below* what uniform would give it.

**Composites did not decompose.** On `C_L1r_S1` — L1r and S1 stacked — the mass on those two
experts was **.019** against a chance level of .250. Thirteen times *below* chance.

> **A trap worth recording.** One composite, `C_L2_S4`, showed .605 — apparently strong
> compositional routing. It is an artifact: `L2` and `S4` are precisely the two experts the gate
> favours on *every* input, including `H1`. The informative row is `C_L1r_S1`, where the fixed
> preference and the hypothesis disagree. Reading the strongest-looking row alone would have
> produced the opposite conclusion.

**Why.** The gate was trained on the task loss **alone** — no load-balancing term, no entropy
regulariser, no routing supervision. Collapse is the *expected* optimum of that objective: a
constant blend minimises average loss and nothing rewards varying with the input. (Switch
Transformer and GShard both add an auxiliary balancing loss for exactly this reason.) The learned
temperature confirms it — it fell to .39–.51 across all 28 layers from an init of 1.0, i.e. the
gate became *more confident* about a preference that did not depend on its input.

So `mole_router` was never a router. It was a **learned static mixture weight**.

### 3.4 The probe — is the signal even there?

Before fixing the gate, one question had to be answered: is the obfuscation condition *available*
in what the gate reads? Two very different fixes follow.

**The design.** A linear probe on the decoder-layer **input** hidden states — exactly what the
gate's hook receives — predicting which condition the program is in. Split by `program_id` (every
condition of one program is a near-duplicate; a row split would inflate this to meaninglessness),
standardisation fitted on training data only, `H1` never loaded.

**Result: 99.4 % at layer 4, against 16.7 % chance**, above 97 % at every layer sampled, on 200
programs.

The condition is almost perfectly linearly decodable. **The gate could have routed and didn't** —
a training failure, not a representation failure.

### 3.5 The fix — and the result that matters

`routerlora_balanced` = the same gate plus Switch-style load balancing (α = 0.01) and a temperature
floor (0.5). Same bank, same data, same prompt, same seed; only those two knobs differ.

**Routing became real:**

| | before | after |
|---|---|---|
| TV distance from the grand-mean profile | .011–.056 | **.074–.106** |
| `L1r` expert on the `L1r` cell | .003 | **.080** |
| `S1` expert on the `S1` cell | .013 | **.253** (its top expert) |
| `C_L1r_S1` on {L1r, S1} — chance .250 | .019 | **.332** |
| `C_L1b_S1` on {L1b, S1} | .149 | **.375** |
| normalised entropy | .151–.180 | .270–.289 |

The mass now tracks what is actually present: `S1` sits at .243–.253 on every condition containing
S1, and falls to .096–.103 on those without it. Four of six composites reach or exceed chance.
`C_L2_S4` correctly **fell** to .383, since its .605 was the artifact.

**And accuracy did not move: +0.4 points on average (range −1.1 to +1.7) — entirely inside the
1.32 / 3.61 seed band.**

This outcome was written into the experiment's config *before it ran*, as the case to watch for:
if routing improves while accuracy doesn't, the gain was never about routing.

---

## 4. The verdict

The five experiments eliminate the explanations one at a time:

| candidate explanation | eliminated by |
|---|---|
| "the merge algorithm is wrong" | L0-merge control — merging clean-code adapters does just as well on `H1` |
| "the gate is badly trained" | balanced gate — fixed it; routing became real |
| "the condition isn't visible to the gate" | probe — 99.4 % vs 16.7 % chance |
| "routing is the missing piece" | balanced gate accuracy — +0.4, inside noise |
| "training on more transforms would generalise" | LOTO — holding one out costs ~1.1, inside noise |

**What is left is the only remaining explanation: the per-condition experts do not carry distinct,
transferable knowledge. No combination strategy can extract value that is not there.**

This is a considerably stronger claim than "our router underperformed", and it is reached by
elimination rather than assumption. Every combination arm — router, merges, mixture — is evidence
*for* it, not a method that fell short.

The positive half stands unchanged and is what the specialists are for: **on the conditions they
were trained on, specialists clearly help** (+1.1 to +4.6 over the clean-code merge). What they do
not do is transfer to a transform nobody trained on. That is the memorization-vs-invariance
question from §1.3, answered.

---

## 5. Secondary findings worth keeping

* **Merge density was never swept, and the default is not optimal.** `dare_ties` scores
  **47.0 / 44.7 / 40.5** at density 0.3 / 0.5 / 0.7 — monotone across all six conditions. Every
  merge conclusion in the project used 0.5.
* **The merge ranking is real, not noise.** Rebuilt from an independent seed-42 expert bank,
  `merge_ties` moves −0.0 and `merge_dare_ties` +0.6. The ~9-point gap between the two algorithms
  reproduces.
* **Obfuscation penalties largely dissolve at 7B.** The base model's spread across the trainable
  ladder is 18.2–29.0 at 1.5B but 49.4–58.0 at 7B, where `L2` (aggressive renaming) actually
  scores *above* clean code. Only `L1b` (−8.0), `S1` (−7.1) and `H1` (−20.9) survive. What
  dissolves is *surface* obscurity; what survives is either semantically adversarial (`L1b` names
  actively lie) or genuinely structure-destroying (`S1`). `H1` is the only penalty that does not
  shrink with scale — which strengthens every `H1`-based conclusion here.
* **All adapter, merge and mixture results are 1.5B.** Since five of seven penalties largely vanish
  by 7B, these findings must be scoped as "at a scale where these transforms still cost the model
  something". Whether combination fails the same way at 7B is open and unrun.

---

## 6. What is still open

* **`S3` did not fully revive** under load balancing (.042–.055), and `L1r` self-routing (.080) is
  still below uniform, leaving two composites under chance.
* **Supervised routing** — training the gate with the correct expert as an explicit target — was
  deliberately not run. It is the strongest fix for compositional decomposition, but it changes
  what may be claimed: a gate *taught* to decompose is a weaker result than one that learned to.
* **More held-out families.** `H1` is one obfuscator. A virtualization-based `H2` and a
  control-flow `H3` would test the invariance claim far harder; stacking existing generators
  (`H1∘S1`) is the cheap version.
* **`H1` is partly burned.** It has been read more than the two sanctioned passes. Promoting it to
  a development set and minting a fresh frozen family is a legitimate, and arguably more honest,
  option.
* **The 7B question**, above.

---

## 7. How this was produced

42 pipeline stages, 224 jobs, ~17.5 hours unattended on two GPUs of a shared four-GPU host, with
the other two in use by another group throughout. 0 stages skipped.

Seven infrastructure defects were found and fixed during the run; four shared one signature —
**a failure that leaves the pipeline reporting success**. The most expensive was a demonstration
that a diagnostic can be the cheapest experiment: a routine progress check showed a job at 98 % CPU
and 0 % GPU, which turned out to be an O(items × pool) recomputation costing 13.7 minutes per cell
where 0.17 seconds sufficed — a 4857× speedup, found by noticing that two numbers disagreed.

Detail: [`../log/modularity/2026-08-14_ood-programme-and-continuous-pipeline.md`](../log/modularity/2026-08-14_ood-programme-and-continuous-pipeline.md)
and [`../log/setup/2026-08-14_pipeline-hardening.md`](../log/setup/2026-08-14_pipeline-hardening.md).

## Changelog

- **2026-08-15** — Created, covering the 13–15 August chain: the L0-merge control, LOTO, the gate
  routing analysis, the probe, the balanced-gate fix, and the merge headroom sweep.
