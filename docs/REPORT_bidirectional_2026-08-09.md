# Can a model that learns to scramble code learn to unscramble it?

**Report — 9 August 2026 · project `obtune` · Qwen2.5-Coder-1.5B-Instruct, Python**

**Answer: yes, but only if you show it both directions — and the clever method proposed
for this doesn't work.** Simply feeding the model the same training pairs backwards costs
nothing and produces the whole effect. A published contrastive-learning method, designed
for exactly this, produces *nothing* at this scale. And the ability that emerges is
confined to transformations where the destroyed information is actually recoverable.

*This report assumes no background. Every term is defined where it first appears.*

---

## 1. The setting

### 1.1 Obfuscation

**Obfuscation** rewrites a program so it still computes exactly the same thing but is
harder to read. It's used to protect intellectual property, and by malware to evade
analysis.

```python
# original                          # obfuscated (identifiers renamed)
def running_total(nums, start):     def f_2b71(v_9c04, v_31aa):
    total = start                       v_c7e2 = v_31aa
    for n in nums:                      for v_88ac in v_9c04:
        total = total + n                   v_c7e2 = v_c7e2 + v_88ac
    return total                        return v_c7e2
```

Both functions return the same value for every input. That property — **semantics
preserved, surface changed** — is what makes obfuscation a good scientific probe. Any
change in a model's behaviour must come from the surface, because the meaning is
identical by construction.

In this project every obfuscated variant is *verified* to preserve semantics: it is
executed against its original's inputs plus ~20 fuzzed ones, and discarded unless every
output matches byte for byte. Nothing here rests on assuming a transform is faithful.

### 1.2 The five transformations used

Each is a **single** transform applied to the clean original — never stacked — so any
effect can be attributed to one mechanism.

| code | family | what it does |
|---|---|---|
| `L1b` | identifier | **adversarial renaming** — names replaced with *misleading* ones (a Fibonacci function renamed `smoothArea`) |
| `L1r` | identifier | **random renaming** — names become meaningless hex (`v_a3f2`) |
| `L2` | identifier | **minification** — names become `a`, `b`, `c`… and type annotations are stripped |
| `S1` | structural | **control-flow flattening** — the body is rewritten as a dispatch loop over a state variable, so the original `if`/`for` structure disappears |
| `S2` | structural | **opaque predicates + dead code** — guards that always take the same branch, plus functions that are never called |

A sixth transformation, `H1` (string encoding + arithmetic rewriting), is deliberately
quarantined and never trained on anywhere in this project. It plays no part in this
report.

### 1.3 Forward and reverse

- **Forward** = obfuscate. Given clean code, produce the obfuscated version.
- **Reverse** = deobfuscate. Given obfuscated code, recover readable original-like code.

Nothing in this report trains the reverse direction *except* where explicitly stated —
that's the whole experiment.

---

## 2. The question, and the paper that raised it

Nikiema et al. (2025) asked: **when a model learns a transformation, does it understand
it, or has it memorised a one-way input→output mapping?**

Their test: if you genuinely understand *why* obfuscation preserves meaning, you should be
able to run it backwards, even having never been trained backwards. Understanding is
direction-agnostic; memorisation is not.

Their findings, on Java:

1. **Fine-tuning on the forward task destroys the reverse direction.** Models trained to
   obfuscate scored **0 %** at deobfuscating. They named this **cognitive
   specialization**.
2. **Their fix — Contrastive Fine-Tuning (CFT) — recovers it**, reaching **39–52 %**
   reverse performance with no reverse training data.

**Fine-tuning** means continuing to train a pretrained model on examples of one specific
task. **Contrastive** here means the model is additionally trained to *judge* whether two
programs mean the same thing, on top of learning to obfuscate.

### The gap this report addresses

**Correction, 2026-08-10.** An earlier version of this section said the paper "never ran the
obvious baseline". That is **wrong**, and the correct statement is stronger: the paper **names** the bidirectional baseline and reports **no result** for it. §5.0.2 declares the comparison — *"CFT effectiveness is assessed through comparison against Standard Fine-Tuning (SFT) ... and Bidirectional Fine-Tuning (BFT) using forward generation plus reverse deobfuscation tasks"* — and the string "BFT" occurs exactly once in the paper: Figure 4 carries only SFT and CFT columns, and no table, figure or sentence reports a BFT number. BFT *is* the `flip` arm. A declared-but-unreported baseline is a sharper gap than an unnoticed one, and "they never ran it" would be factually wrong.

**Reverse training data is free**: every `(original, obfuscated)` pair is also an
`(obfuscated, original)` pair — just swap which side is the question and which is the answer.
If simply training on both directions works as well as CFT, the contrastive machinery adds
nothing.

---

## 3. What was trained

Seven systems. All are the same base model with a small trainable add-on (a **LoRA
adapter** — a low-rank weight patch, ~0.5 % the size of the model, which is the standard
cheap way to fine-tune). Same recipe throughout: rank 32, 3 epochs, learning rate 1e-4,
effective batch 64. **The arms differ only in which examples they see.**

| name | what it was trained on | why it exists |
|---|---|---|
| `base` | nothing — the untouched model | the floor everything is measured against |
| `sft` | forward only (obfuscate) | the paper's "standard fine-tuning"; the thing said to score 0 % |
| `cft` | forward + equivalence judgements | the paper's proposed fix |
| `rev` | reverse only (deobfuscate) | the ceiling — how good can reverse get if you train it directly? |
| **`flip`** | forward **and** reverse | **the missing baseline** — the free swap |
| **`mix50`** | half the programs forward, half reverse | **the decisive arm** — see below |
| `flipsym` | same as `flip`, but both directions share one instruction wording | a control for a confound — see §6.3 |

### 3.0 What the training examples actually look like

This is the part that makes "trained on both directions" concrete. Everything below is a
**real training example**, copied verbatim from the pools, for one small program
(`cruxeval_sample_345`) under `S1` (control-flow flattening).

The original program, and its obfuscated form:

```python
# ORIGINAL                          # OBFUSCATED (S1: control-flow flattening)
def f(a, b):                        def f(a, b):
    if a < b:                           _st_e6f9 = 72
        return (b, a)                   while _st_e6f9 != -1:
    return (a, b)                           if _st_e6f9 == 72:
                                                _st_e6f9 = 22 if a < b else 21
                                            elif _st_e6f9 == 21:
                                                return (a, b)
                                            elif _st_e6f9 == 22:
                                                return (b, a)
                                            else:
                                                raise RuntimeError('invalid dispatch state')
```

Same behaviour, unrecognisable shape. The `if/else` has become a loop that jumps between
numbered states.

**A FORWARD training example** — given the original, produce the obfuscated version.
Used by `sft`, `cft`, `flip`, `mix50`:

> **SYSTEM**  You are a source-to-source code transformation tool. You rewrite programs
> exactly as instructed and never change what they compute. Reply with the transformed
> program only […]
>
> **USER**  Obfuscate the following Python code by **control-flow flattening** while
> preserving its functionality.
> ```python
> def f(a, b):
>     if a < b:
>         return (b, a)
>     return (a, b)
> ```
>
> **ASSISTANT** *(the answer the model is trained to produce)*
> ```python
> def f(a, b):
>     _st_e6f9 = 72
>     while _st_e6f9 != -1:
>         ...
> ```

**A REVERSE training example** — *the exact same two programs, swapped*. Used by `rev`,
`flip`, `mix50`:

> **SYSTEM**  You are a source-to-source code transformation tool. You are given an
> obfuscated program. You recover the original, readable source […]
>
> **USER**  The following Python code has been obfuscated. Recover the original, readable
> source code while preserving its functionality.
> ```python
> def f(a, b):
>     _st_e6f9 = 72
>     while _st_e6f9 != -1:
>         ...
> ```
>
> **ASSISTANT** *(the answer the model is trained to produce)*
> ```python
> def f(a, b):
>     if a < b:
>         return (b, a)
>     return (a, b)
> ```

**That is the entire "free flip".** No new data was collected, nothing was labelled. The
question and the answer changed places. This is why the baseline costs nothing — and why
the paper not running it is the gap this report fills.

#### What `cft` sees instead

The contrastive method keeps the forward examples and adds a *second kind* of example: a
yes/no judgement about whether two programs mean the same thing.

> **SYSTEM**  You are a program equivalence checker […] Reply with exactly one word: YES
> if they are semantically equivalent, NO if they are not.
>
> **USER**  Program A: *(the original)* … Program B: *(the obfuscated version)* … Do
> Program A and Program B compute the same result for every input?
>
> **ASSISTANT**  `YES`

and the negative, which is the same pair with **one character changed** — `21` became
`22` in the dispatch table:

> **USER**  Program A: *(the original)* … Program B:
> ```python
>         if _st_e6f9 == 72:
>             _st_e6f9 = 22 if a < b else 22     # <- was 21
> ```
>
> **ASSISTANT**  `NO`

That single-token edit was *executed* against the program's test inputs and kept only
because it genuinely changes the output on 4 of 12 cases. (The source paper says only
"functionally different code" and doesn't say how it verifies that; here every negative is
a verified fact, not an assumption.)

Notice the shape of these: **two whole programs in the question, a one-word answer.** They
are as expensive to process as a forward example but carry almost no learning signal —
which is exactly what the cost table in §3.1 shows.

#### What `mix50` sees

The same *number* of examples as forward-only training, but each **program** contributes
one side or the other — never both:

```
program apps_391_0           ->  REVERSE (deobfuscate)
program apps_4402_0          ->  FORWARD (obfuscate)
program cruxeval_sample_537  ->  REVERSE
program cruxeval_sample_262  ->  REVERSE
program apps_148_0           ->  FORWARD
...
totals: 3,688 forward + 3,696 reverse = 7,384     (forward-only: 7,384 forward)
```

Verified: no program appears in both directions. So `mix50` cannot be accused of having
seen more — it saw the *same programs*, the *same number of times*, just half of them from
the other side.

#### What `flipsym` sees

Identical examples to `flip`, with one change: the forward and reverse tasks are given
**the same system instruction**, so the wording carries no clue about which direction is
being asked. That tests whether the model is really learning a shared skill or just
switching between two behaviours cued by two different prompts (§6.3).

### 3.1 Why `mix50` is the arm that matters

An obvious objection to `flip` is that it simply saw more data. `mix50` removes that
objection: each program contributes **either** its forward example **or** its reverse
example, never both. So `mix50` trains on exactly as many examples as `sft`, for exactly
as many optimisation steps, in the same wall-clock — while learning *less* in total.

Measured cost of each arm relative to forward-only training:

| arm | examples | **supervised tokens** | compute | steps |
|---|---|---|---|---|
| `sft` | 1.00× | 1.00× | 1.00× | 1.00× |
| `mix50` | **1.00×** | **0.71×** | **1.05×** | **1.00×** |
| `flip` | 2.00× | 1.43× | 2.09× | 2.00× |
| `cft` | 2.52× | **1.02×** | **2.65×** | 2.52× |

**Supervised tokens** = how many tokens the model actually gets a learning signal on.
This is the surprise in the table: CFT costs **2.65× the compute** to add **1.02× the
signal**. Its equivalence-judgement examples each contain two entire programs in the
question but only require a one-word answer, so they are expensive to process and teach
almost nothing per example. `flip` costs 2.09× for 1.43×.

`mix50` therefore tests the strongest possible version of the claim: it gets **less**
supervision than plain forward-only training, at the same cost on every axis.

---

## 4. How reverse performance is measured

This is where most of the care went, because the obvious measure is badly broken.

### 4.1 The trap: "does the output run correctly?" is not enough

The natural check is **execution**: take what the model produced, run it, see whether it
returns the same values as the original. Call this **`exec`**.

It fails. A model that simply **copies the obfuscated input back out** passes `exec`
perfectly — because the obfuscated program *is* semantically correct. It deobfuscated
nothing.

This is not hypothetical. The untouched `base` model scores **83.3 % on `exec`**, and
separately we can see it is echoing: on the forward task it reproduces its input verbatim
**69.7 %** of the time.

### 4.2 The measures actually used

**`S(a, b)` — syntactic similarity.** CodeBLEU, a standard 0–1 code-similarity score
(published implementation, not reimplemented). `S(deobf, obf)` near 1.0 means the model's
answer still looks like the obfuscated input — i.e. it changed nothing.

**Readability.** A 0–1 score for how human-readable code is, dominated by whether
identifiers are real words. *This is a substitute for the instrument the paper used* (a
Java-only tool with no Python equivalent), so its absolute values are not comparable to
theirs — only comparisons within this report are.

**`paper` criterion** — the source paper's own definition of reverse success: the answer
must stop looking like the obfuscated input (`S(deobf, obf) < 0.4`) **and** recover
readability. We added one requirement the paper leaves implicit: the answer must be
*parseable code*. Without that, an empty reply satisfies the first condition perfectly —
in a dry run, the literal placeholder string `<stub:a1b2c3>` scored 17–24 %.

**`strict`** — **the headline measure**: `exec` **and** `paper` together. The recovered
program must both compute the right answers *and* actually have undone the obfuscation.
This is the number to read; it is the only one that can't be gamed by echoing.

**`identifier recall`** — of the meaningful names in the original, what fraction reappear
in the answer. A direct check on whether names were genuinely recovered.

All figures below are on **300 held-out programs** — never trained on, never used to
select anything — with 95 % confidence intervals from a **cluster bootstrap by program**
(resampling programs, not individual test items, because several items from one program
are correlated and treating them as independent would understate the uncertainty).

---

## 5. Results

### 5.1 Headline

| system | **`strict`** (95 % CI) | `exec` alone | `S(deobf,obf)` | id-recall |
|---|---|---|---|---|
| `base` | 2.7 % [1.9, 3.5] | 83.3 % | 0.836 | 0.591 |
| `sft` — forward only | **0.4 %** [0.1, 0.7] | 74.1 % | 0.597 | 0.416 |
| `cft` — contrastive | **0.3 %** [0.1, 0.7] | 74.6 % | 0.578 | 0.394 |
| `rev` — reverse only | 31.7 % [30.0, 33.3] | 89.2 % | 0.441 | 0.718 |
| **`flip`** | **31.4 %** [29.7, 33.1] | 90.3 % | 0.444 | 0.721 |
| **`mix50`** | **30.7 %** [28.9, 32.3] | 88.9 % | 0.442 | 0.719 |
| `flipsym` | 30.8 % [29.1, 32.5] | 91.7 % | 0.447 | 0.724 |

Note how `exec` alone would have told you the base model is the second-best system in the
table. It is in fact the one doing the least work.

### 5.2 The four conclusions, with intervals

Differences in percentage points. An interval excluding 0 means the difference is real at
this sample size.

| comparison | difference | verdict |
|---|---|---|
| `cft` − `sft` | −0.1 [−0.5, +0.3] | **no effect.** The contrastive objective adds nothing |
| `flip` − `cft` | **+31.1** [+29.3, +32.8] | **the free swap beats the published method outright** |
| `mix50` − `sft` | **+30.3** [+28.5, +31.9] | **the entire effect, at no extra cost on any axis** |
| `flip` − `mix50` | +0.7 [−0.1, +1.7] | doubling the data adds nothing detectable |
| `sft` − `base` | **−2.3** [−3.1, −1.4] | **forward-only training actively damages the reverse direction** |

**1. Cognitive specialization reproduces — and is worse than the paper could show.** Both
fine-tuned forward arms land *below* the untouched model. Training only to obfuscate
doesn't merely fail to teach deobfuscation; it removes an ability the base model had. The
paper couldn't state this, because it never ran an untouched baseline.

**2. The contrastive method does nothing here.** `cft` (0.3 %) is statistically
indistinguishable from `sft` (0.4 %). This is the paper's central claim, and it does not
reproduce at this scale.

**3. The free flip does all the work, for free.** `mix50` reaches 30.7 % while training on
the same number of examples, for the same number of steps, with **less** total supervision
than forward-only. Whatever produces the reverse ability is *exposure to both directions*,
not any special objective.

**4. Bidirectionality is not paid for in forward performance.** Forward execution
accuracy: `sft` 90.7 %, `flip` 91.5 %, `mix50` 90.6 %, `cft` 92.5 % — all within noise of
each other, all above `base` (86.6 %).

### 5.3 The per-transformation result inverts the paper

`strict`, broken out by transformation:

| system | `L1b` | `L1r` | `L2` | **`S1`** | **`S2`** |
|---|---|---|---|---|---|
| `base` | 0.7 % | 0.7 % | 3.7 % | 8.0 % | 0.3 % |
| `sft` | 0.0 % | 1.3 % | 0.0 % | 0.3 % | 0.3 % |
| `cft` | 0.3 % | 0.3 % | 0.0 % | 1.0 % | 0.0 % |
| `flip` | 0.7 % | 0.3 % | 3.0 % | **74.0 %** | **79.0 %** |
| `mix50` | 0.3 % | 1.7 % | 1.7 % | **70.7 %** | **79.0 %** |

**Everything happens on the structural transformations. Renaming stays at the floor.**

The paper reports the *opposite* profile — its method working on renaming and failing on
dead code.

There is a clean explanation, and it was predicted before the run. **Renaming is
information-destroying and therefore not invertible.** Once `totalPrice` becomes `a3x9`,
the original name is gone; nothing in the program can recover it, and no amount of
training can conjure it back. **Structural transforms are information-preserving**: a
flattened dispatch loop still contains every branch of the original control flow, and dead
code is still identifiable as dead. Models learn to invert exactly the transformations
where the information survives.

This also suggests why the paper reports success on renaming: its criterion rewards
producing *plausible, readable* names, not the *original* ones. Our `strict` measure
requires the recovered program to match the original's behaviour and to have genuinely
undone the transform, which renaming cannot satisfy.

---

## 6. Threats to these conclusions

### 6.1 Scale — resolved: the refutation holds at the paper's own model

The results above are from a 1.5-billion-parameter model, and the paper used 7–15 B and
explicitly reports that its method only worked at the larger sizes. That was the single
biggest threat to everything above, so the comparison was run on **the paper's own model,
Qwen2.5-Coder-7B**, which it reports at 39.00 % (Fig. 4).

It does not reproduce. Reverse success under **the paper's own criterion**, 300 test
programs × 5 transformations, all four prompting strategies:

| system | `simple` | `few_shot` | `cot` | `augmented` |
|---|---|---|---|---|
| `base` — untouched | 23.6 % | 32.7 % | 34.7 % | **38.7 %** [35.9, 41.5] |
| `sft` — forward only | 0.3 % | 6.8 % | 11.0 % | 12.5 % |
| `cft` — contrastive | 0.2 % | 1.9 % | 3.0 % | 2.6 % |

Pooled over strategies, **`cft` − `sft` = −5.7 points [−6.4, −5.0]**. At the scale where the
method is supposed to work, the contrastive objective does not merely fail to help — it is
significantly *worse* than the forward-only training it is meant to repair.

Three things follow, and the third is the one that matters most.

1. **The paper's "0 %" reproduces exactly, and only under its weakest prompt.** `sft` with
   the `simple` instruction scores 0.3 % [0.1, 0.7]. Move to `augmented` and the same
   adapter scores 12.5 %. A result reported as a property of the model is substantially a
   property of the prompt used to elicit it.
2. **CFT does not recover it.** 0.2 % under `simple`, never above 3.0 % under any strategy,
   against a reported 39.00 %.
3. **The untouched base model reaches the paper's headline number.** `base` scores 38.7 %
   under `augmented` — statistically indistinguishable from the 39.00 % the paper
   attributes to its contrastive method. The paper reports no untouched baseline. Without
   one, a number that is simply *what the model could already do* is indistinguishable from
   a number the method produced.

The `exec`-alone column shows the mechanism, and it is the trap of §4.1 in its purest form:
`cft` is the **best** system by execution equivalence (91.7 % vs `base`'s 80.9 %) while
being the worst by every measure that requires the output to be *deobfuscated*. It achieves
this by echoing its input — the identity rate reaches 43–90 % in the `cot` and `simple`
reverse cells. An echoed obfuscated program is trivially execution-equivalent to the
original and is not a deobfuscation. This is the same failure the paper itself describes
for SFT (§4.3.3, "outputs nearly identical to the obfuscated input"); what is new is that
CFT exhibits it *more* strongly than SFT does.

**The positive half now holds at 7 B too.** The `rev` and `flip` arms finished overnight and
were evaluated against the same items under the paper's own `simple` instruction:

| system | `strict` | paper criterion | `exec` alone | echoes its input |
|---|---|---|---|---|
| `base` — untouched | 13.1 % | 23.5 % | 80.7 % | 7.1 % |
| `sft` — forward only | 0.0 % | 0.4 % | 89.5 % | 18.1 % |
| `cft` — contrastive | 0.1 % | 0.3 % | 91.2 % | 28.8 % |
| `rev` — reverse only | 32.9 % | 35.1 % | 93.7 % | **0.0 %** |
| **`flip` — the free swap** | **33.6 %** | **35.6 %** | 93.8 % | **0.0 %** |

At the paper's own model, the trivially-free direction swap reaches **33.6 %** where the
contrastive method reaches **0.1 %** — and it does so for *less* compute (2.00× forward-only
SFT versus CFT's 2.60×, §3.1). `flip` also matches `rev` (33.6 % vs 32.9 %), so training both
directions costs nothing against training the reverse alone.

The echo column is the mechanism in one number. `cft` and `sft` reproduce their input 28.8 %
and 18.1 % of the time; `flip` and `rev` never do. An echoed program is execution-equivalent
to the original and is not a deobfuscation, which is why `exec` alone ranks `cft` above
`base` while every meaningful measure ranks it last.

So at 7 B the conclusion is no longer only negative. **CFT is dominated on every axis a
practitioner pays for — less capability, more compute, more instances, more steps — by
swapping the pairs, which is free.**

Sources: `results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b/report.md`
(base/sft/cft, four strategies, 22,500 generations) and `.../e1_qwen7b/summary.json`
(base/sft/cft/rev/flip, `simple`). 300 programs, single seed 17.

### 6.2 Different transformations

The paper's third transformation is string encryption, which in this project maps onto the
quarantined `H1` and cannot be trained on. So the comparison covers renaming and dead code
but not string encryption, and adds control-flow flattening, which the paper does not have.

### 6.3 Could the effect be an artifact of the instructions?

The forward and reverse tasks are introduced by different instruction wordings. A model
might be switching between two unrelated behaviours cued by the wording, rather than
sharing anything. `flipsym` tests this by giving both directions **one identical
instruction**, so the wording carries no information about direction. It scores 30.8 %
versus `flip`'s 31.4 % — a difference of −0.6 points [−1.4, +0.1], i.e. nothing. **The
effect is not an instruction artifact.**

### 6.4 Single seed

Every arm was trained once. Run-to-run variation is unmeasured. The differences that carry
the conclusions are 30+ points and the null results are tight (±0.5), so seed noise is very
unlikely to overturn them — but a replication at a second seed is queued and should be run
before publication.

### 6.5 The 1.5 B per-trial data was overwritten, and has been regenerated

The §5 tables were computed from the 1.5 B run's `summary.json`, which is intact. The
per-trial file it was derived from is not: the 7 B evaluation wrote to a results path that
carried the date and language but not the model, and destroyed the 1.5 B `trials.jsonl`
(21,000 rows) on completion. The output path now includes model and run tag, and
`scripts/preflight.py` fails any two evaluation configs that resolve to the same directory.

**Resolved.** The 1.5 B evaluation was re-run and reproduces §5 within decoding noise:

| system | §5 as reported | re-run | system | §5 as reported | re-run |
|---|---|---|---|---|---|
| `base` | 2.7 % | 2.9 % | `flip` | 31.4 % | 31.5 % |
| `sft` | 0.4 % | 0.4 % | `mix50` | 30.7 % | 30.6 % |
| `cft` | 0.3 % | 0.3 % | `flipsym` | 30.8 % | 30.5 % |
| `rev` | 31.7 % | 31.5 % | | | |

Every difference is ≤0.2 points. Decoding is greedy, so the residual is vLLM batch-numerics
rather than sampling. §5 is now backed by raw per-trial data again
(`results/2026-08-09_cft-bidirectional/qwen25c-1.5b/python/e1_qwen1.5b/`).

### 6.6 Readability is a substitute measure

As noted in §4.2, the readability component of the `paper` criterion is not the instrument
the source paper used. Absolute values are not comparable across the two papers; the
comparisons *within* this report are unaffected, since every system is scored identically.

---

## 7. What this means

For anyone fine-tuning a model on a reversible transformation, the practical finding is
blunt:

> **If you want the reverse direction, put the reverse examples in the training set. They
> are free — you already have them, written backwards. No specialised objective was needed,
> and the one that was proposed did not help.**

And a caution that generalises past this task: **forward-only fine-tuning removed an
ability the base model already had.** Narrow training is not purely additive. If a
capability matters, measuring it before and after is not optional.

The scientific finding is narrower and more interesting than "training on both directions
works". It is that models learn to invert **exactly the transformations whose information
survives them** — and no amount of training data taught them to invert one that destroys
information. That is a statement about what is learnable in principle, not about this
model.

---

## 8. Reproducing this

```bash
# the four bidirectional arms (1.5B)
python scripts/srh/21_enqueue_e1_arms.py --stage 1 --write

# the evaluation reported above
python -m obtune.cft.evaluate --config srh/eval/e1_qwen1.5b.yaml --gpu <idle>
```

Raw per-trial records: `results/2026-08-09_cft-bidirectional/python/trials.jsonl`
(21,000 rows). Cell summaries and provenance — including the exact prompt hash and the
CodeBLEU implementation version — in `summary.json` and `run_manifest.json` alongside it.
Budget accounting: `results/srh/budget_qwen7b_python.json`.

## Glossary

| term | meaning |
|---|---|
| **arm** | one trained system in the comparison |
| **base** | the untouched pretrained model |
| **LoRA adapter** | a small trainable weight patch; the cheap standard way to fine-tune |
| **fine-tuning** | further training of a pretrained model on task-specific examples |
| **forward / reverse** | obfuscate / deobfuscate |
| **SFT** | supervised fine-tuning — plain training on input→output pairs |
| **CFT** | contrastive fine-tuning — the source paper's proposed method |
| **`exec`** | the produced program runs and returns the original's outputs |
| **`paper`** | the source paper's reverse-success criterion (dissimilar to input + readable) |
| **`strict`** | `exec` **and** `paper` — the headline measure |
| **`S(a,b)`** | CodeBLEU syntactic similarity, 0–1 |
| **identifier recall** | fraction of the original's meaningful names that reappear |
| **supervised tokens** | tokens the model actually receives a learning signal on |
| **cluster bootstrap** | resampling whole programs to get honest confidence intervals |
| **held-out** | never trained on and never used to choose anything |
