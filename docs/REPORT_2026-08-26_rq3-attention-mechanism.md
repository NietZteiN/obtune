# Does the model learn to *ignore* the junk? An attention mechanism for the one transfer that works

*Written 26 August 2026. Self-contained: assumes no prior knowledge of this project.*

---

## 1. The setting, in one page

**The task.** A model is shown a self-contained function and one concrete input, and must predict
the exact value the function returns. Nothing else — no explanation, no reasoning shown. Grading
runs the real program, so there is no grader subjectivity.

**Obfuscation.** The same program is then rewritten in ways that provably preserve its behaviour.
Six rewrites matter here, each applied on its own and each verified by executing the rewritten
program against the original's inputs:

| code | what it does to the program |
|---|---|
| `L0` | nothing — the clean original (comments stripped) |
| `L1b` | renames identifiers to **actively misleading** ones (a Fibonacci function becomes `smoothArea`) |
| `L1r` | renames identifiers to random hex (`v_a3f2`) |
| `L2` | renames identifiers to single letters, strips type annotations |
| `S1` | flattens control flow into a dispatch loop, so the original `if`/`for` structure disappears |
| **`S2`** | **inserts opaque predicates and dead code** — guards that always take the same branch, and helper functions that are never called |

**The project's question.** Does fine-tuning on obfuscated code teach *semantic invariance*
(robustness to the whole class of meaning-preserving rewrites), or merely *transform memorization*
(learning to undo the specific obfuscators it was shown)? A seventh rewrite, `H1`, is quarantined
and never trained on, and exists solely to tell those apart.

**The answer so far is memorization**, with one exception that has survived every attempt to
explain it away.

**The exception.** An adapter trained on `S2` alone is the only system anywhere in the project that
beats the control on the held-out `H1` — replicated at two seeds in two languages, and confirmed at
full power on 1,214 items (**+3.46** points, 95 % CI [+2.06, +4.86]). The control here is
`tuned_L0`, an adapter trained on *clean* code only; it is the right comparator because the base
model is weak at the task itself, so only the gap to a clean-code-trained adapter isolates what
*obfuscation* training buys.

**The proposed explanation.** `S2` and `H1` both bury the real computation under **inert
material** — dead branches and never-called helpers in one case, encoded strings and rewritten
arithmetic in the other. So perhaps `S2` teaches a genuinely transferable skill: *ignore the code
that cannot affect the result.* Learning to ignore is transferable; learning to invert a particular
renaming is not.

That was a story. This report tests it.

---

## 2. What "ignore the junk" would look like inside the model

If a model has learned to ignore inert material, that should be visible in **attention** — the
mechanism by which a transformer decides which parts of its input to read when producing each token.

Concretely, we take the model's attention at the moment it is about to emit the answer, and ask
where it is looking. Every token of the program is labelled by what it is:

- **identifier** — variable and function names (the dead helpers `S2` inserts carry their own junk names)
- **control_kw** — `if`, `for`, `return`, `while` …
- **dataflow_critical** — tokens on the path from input to output
- plus operators, literals, and everything else

The prediction: an adapter that has learned to ignore inert material should move attention **off
identifiers** and **onto control-flow and dataflow tokens** — and should do so specifically on `S2`,
the condition that actually contains inert material.

We call that quantity the **anchoring shift**:

> anchoring shift = Δ(attention on control + dataflow) − Δ(attention on identifiers)

measured against the untuned base model. Positive means attention moved off names and onto structure.

---

## 3. Measurement 1 — the adapter really does re-anchor

**The sweep.** 4 systems × 6 conditions × 6 layers × 150 programs = **3,600 attention dumps**.
Systems: `base` (untouched), `tuned_L0` (the clean-code control), `tuned_S2_s17` (the specialist in
question), and `tuned_L1b_s17` (a specialist that helps on its own condition and never reaches
`H1` — included so the result cannot be "any adapter does this").

Anchoring shift vs `base`, cluster-bootstrapped by program, 51 programs:

| system | L0 | L1b | L1r | L2 | S1 | **S2** |
|---|---|---|---|---|---|---|
| `tuned_L0` | +0.008 | −0.024 | −0.031 | −0.011 | −0.032 | **+0.044** |
| `tuned_L1b_s17` | −0.003 | −0.033 | −0.041 | −0.015 | −0.059 | **+0.030** |
| **`tuned_S2_s17`** | +0.014 | −0.015 | −0.044 | −0.008 | −0.013 | **+0.111** |

**`tuned_S2_s17` on `S2`: +0.1113 [+0.0930, +0.1313]** — the largest cell in the table by 2.6×, and
**specific**: small, null or negative on every other condition.

Two sanity checks that make this coherent rather than a curiosity:

- **`S2` is the only condition with much junk to ignore.** Under `base`, identifier attention mass
  is 0.15–0.18 on `S2` against 0.03–0.04 everywhere else, because the dead helpers bring their own
  names. So `S2` is precisely where "ignore what cannot matter" has a large target.
- **The renaming conditions go the other way.** Every adapter shifts attention *toward* identifiers
  on `L1b`/`L1r`/`L2`. That is the expected mirror image: under a renaming transform, the
  identifiers are what changed, so attending to them more is the adaptation.

**But this is a correlation.** The adapter attends differently and it also performs differently;
nothing so far shows the attention is *why*. The project's charter is explicit that RQ3's causal
claims wait for an intervention.

---

## 4. The intervention, and two false starts

**The knockout.** We can test necessity directly: suppress attention to identifier tokens — add a
large negative number to the attention scores at those positions, so the model literally cannot read
them — and see how much accuracy each system loses. If `tuned_S2` has learned to ignore those
tokens, taking them away should cost it *less* than it costs `base`.

### False start 1 — the null that meant nothing

Eight conditions, 150 items each. Every cell landed between **−2.7 and +2.7** accuracy points, which
on 150 items is ±4 items against a seed-to-seed noise floor of 3.61 points. `tuned_S2` and `base`
were *identical*. Read naively: the re-anchoring is incidental and the mechanism is dead.

We did not read it naively, because `base` lost nothing either — and a manipulation that moves
*no one's* accuracy has not been shown to be a manipulation at all.

### The manipulation check

So we suppressed things the task provably needs and asked whether *anything* moved. Suppress all six
token classes — every code token in the program — across all 28 layers:

| what is suppressed | layers | keys masked | accuracy damage |
|---|---|---|---|
| all 6 classes | 28 | 372 | **+2.7** |
| all 6 classes | 6 | 372 | −2.0 |
| identifiers | 28 | 132 | −0.7 |
| literals | 6 | 49 | −1.3 |

**Blinding the model to the entire program changed its accuracy by 4 items out of 150.** At that
point either the intervention is broken, or accuracy is the wrong thing to measure.

### False start 2 — my diagnosis was wrong

The natural conclusion was a broken hook. It was not. Measured directly, attention mass at masked
key positions goes from 0.0072 / 0.0247 / 0.0284 (layers 4 / 14 / 27) to **exactly 0.0000**. The
intervention is complete. And it visibly changes behaviour: under the full knockout, **68 % of the
model's outputs change** (only 48/150 identical), with a clean dose-response — 62 % identical at 6
layers, 32 % at 28.

**The instrument was fine. The *measure* was insensitive.** `base` scores ~22 % on obfuscated `S2`,
close enough to guessing that scrambling what it can read changes *which* answers it gives without
changing how often they happen to land. Exact-match accuracy is a binary hit/miss with no headroom
on a 22 %-accurate task.

---

## 5. Measurement 2 — the causal test, with a measure that can see

Instead of asking "did it still get the right answer", ask **how strongly the model believed the
right answer**: teacher-force the gold output and record its log-probability, clean versus knocked
out. This is continuous, has no floor, and is defined even on items the model gets wrong. It
measures the thing the mechanism claim is about — how much the answer *depends* on reading those
tokens.

**Sensitivity check first.** Suppressing all six classes across all 28 layers costs `base`
**−1.590** nats and `tuned_S2` **−2.544**. The readout has roughly 100× the dynamic range of the
effect we are looking for, so a null in this measure is a real null.

**The result.** Identifier knockout on `S2`, 150 items, 50 programs, bootstrapped by program.
Negative means the knockout hurt.

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

**The pre-registered prediction — "identifier knockout costs `tuned_S2` less than it costs `base`" —
is confirmed.**

Three things make this more than one significant number:

1. **The rank order matches the sweep, from an independent measurement.** Re-anchoring on `S2` ran
   `tuned_S2` (+0.111) > `tuned_L0` (+0.044) > `tuned_L1b` (+0.030) > base. Knockout damage runs the
   mirror image: `tuned_S2` (+0.014) < `tuned_L0` (−0.032) < `tuned_L1b` (−0.062) < base (−0.089).
   More re-anchoring, less dependence on identifier attention.
2. **The obvious deflationary explanation is ruled out.** "The adapter just ignores the code" would
   predict it is hurt *less* when everything is suppressed. It is hurt **more** (−2.544 vs base's
   −1.590). `tuned_S2` depends on the program *more* overall and on identifiers *less* specifically —
   which is the shape the mechanism predicts and a trivial explanation does not.
3. **A specialist that does not transfer does not show it.** `tuned_L1b` re-anchors least and is
   hurt nearly as much as `base`.

---

## 6. What this licenses, and what it does not

**Licensed.** On the `S2` condition, at 1.5B, the `S2` adapter's attention re-anchoring is
**load-bearing rather than incidental**: it attends less to inert identifiers, and it depends less
on being able to read them.

**Not licensed.** Anything about `H1`. No quarantined item was read in any of this work. The step
from "ignores inert material on `S2`" to "therefore transfers to the held-out obfuscator" remains
**inferential** — the two facts are consistent and mutually suggestive, and that is all.

**Caveats that travel with the result.** 50 programs; a single seed; one model scale; six of
twenty-eight layers for the headline knockout. `tuned_S2`'s own interval spans zero — the
significant claim is the *paired difference against base*, not that the knockout helps it.

---

## 7. How much of this was infrastructure

Worth recording, because it is most of the elapsed effort. RQ3's code had been written months
earlier and **never executed end to end**. Running it surfaced six defects, each of which would have
produced a confident wrong answer:

| # | defect | what it would have caused |
|---|---|---|
| 1 | the analysis loader read a format no writer emits | every analysis raised `KeyError` on the first file |
| 2 | a silent fallback prompt template | attention measured on a different distribution than accuracy |
| 3 | no length guard on the attention dump | one 20,000-token program OOM-killed all 24 sweep jobs |
| 4 | grader called with 2 args against a 3-arg signature | knockout died on the first item |
| 5 | that same call unpacked 2 values from a 6-field dataclass | second, independent breakage in the same line |
| 6 | a silent fallback grader (strict string equality) | knockout graded by a different rule than every number it is compared to |

Plus two wrong diagnoses of my own, both caught by the manipulation check rather than by reasoning:
I declared the intervention broken when it was zeroing attention perfectly, and blamed layer
coverage when the real problem was a floor in the dependent variable.

**The manipulation check is the load-bearing methodological lesson.** Without it, the honest-looking
write-up would have been *"the knockout shows attention re-anchoring is not causal"* — which is
false, and which the data would have appeared to support.

---

## 8. Provenance

- Sweep: 3,600 dumps under `results/attn/rq3_sweep/`, metrics cached at
  `results/attn/rq3_sweep_metrics.parquet`. 4 systems × 6 conditions × layers [4, 9, 14, 19, 23, 27]
  × 150 items, Grid A `heldout` programs.
- Knockout and log-prob: `results/attn/knockout/qwen25c-1.5b/S2/`, driver
  `scripts/attn/30_knockout.py` (`--mode score` for the log-prob readout), intervention
  `src/obtune/attention/knockout.py`.
- Model: Qwen2.5-Coder-1.5B-Instruct, LoRA rank 32, seed 17, eager attention (required — SDPA and
  flash-attention return no attention weights).
- Statistics: cluster bootstrap by `program_id`, 1,500–3,000 resamples, seed 17. Grading is strict
  normalized exact match, execution-verified.
- Predictions for every knockout arm were fixed in the driver's docstring **before** it ran.
- Lab notes: `log/attention/2026-08-18_rq3-first-sweep.md`,
  `log/attention/2026-08-26_knockout-null-to-causal.md`.

## Changelog

- **2026-08-26** — Created. Covers the attention sweep, the accuracy-knockout null, the manipulation
  check that explained it, and the log-probability readout that produced the causal result.
