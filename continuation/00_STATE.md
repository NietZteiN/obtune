# 00 — Where the research stands (as of 2026-08-27)

Everything here is recomputed from `results/cells/` and cross-checked against
[`../docs/MASTER_REPORT_2026-08-27.md`](../docs/MASTER_REPORT_2026-08-27.md). Section references
(`§n`) are to that document.

**Scale of evidence:** 2,215 evaluation cells / 1,046,382 graded trials at
`results/cells/` — 1,918 at 1.5B/Python, 227 at 1.5B/JavaScript, 70 at 7B/Python. Plus 3,600
attention dumps (`results/attn/`) and 51 forgetting probes (`results/forgetting/`).

**Model:** Qwen2.5-Coder-1.5B-Instruct for everything except the CFT side thread and one 7B
baseline panel. **This is the project's biggest scope liability** — see "Known weaknesses" below.

---

## The condition ladder

| code | transform | trainable |
|---|---|---|
| `L0` | clean original, comments/docstrings stripped | yes |
| `L1b` | **adversarial** renaming — names made to *lie* | yes |
| `L1r` | random hex renaming | yes |
| `L2` | minification + annotation stripping | yes |
| `S1` | control-flow flattening (dispatch loop) | yes |
| `S2` | opaque predicates + dead code | yes |
| `S3` / `S4` | the two halves of `S2` (dead code only / predicates only) | yes |
| `C_X_Y` | composites — two transforms stacked | no (eval only) |
| **`H1`** | **held out** — string encoding + mixed boolean-arithmetic | **never** |

---

## RQ1 — Generalization: **memorization, with one exception**

Each per-condition adapter helps on its own condition (+3 to +8 over the clean-code control) and
essentially nowhere else. Mean off-diagonal transfer ratio near zero; several cross-family cells
negative. Training on all five obfuscations at once is *worse* than clean-code-only on `H1`, and
more adapter capacity does not fix it (§4: `mono_r32/64/128/192` are flat).

### The exception, and it is the project's main asset

**`tuned_S2` → `H1`.** The only system anywhere that beats the clean-code control on the held-out
obfuscator:

| | control `tuned_L0` | `tuned_S2` | Δ |
|---|---|---|---|
| Python s17 | 24.55 | **28.01** | **+3.46** [+2.06, +4.94] |
| Python s42 | 24.71 | **27.51** | **+2.97** [+1.40, +4.63] |
| JavaScript s17 | 23.8 | **31.1** | **+7.3** |
| JavaScript s42 | 24.9 | **32.6** | **+7.7** |

Two seeds × two languages, confirmed at n=1,214. It also transfers to `S1` (+4.41 [+2.48, +6.41]),
the only other unseen condition any specialist wins.

**Why:** `S2` and `H1` both bury the computation under material that cannot affect the result. The
skill is *ignore what can't matter* — which travels. Inverting a renaming does not, which is why
`L1b`/`L1r`/`L2` transfer nowhere.

---

## RQ2 — Modularity: **CLOSED, negative** (thread will not be reopened)

Full account: [`../docs/MASTER_REPORT_2026-08-27_router-and-merging.md`](../docs/MASTER_REPORT_2026-08-27_router-and-merging.md).
110 combination systems, 1,208 cells, 393,997 trials, 05–17 August.

**No combination of specialists beats a clean-code adapter on `H1`** — not a perfect hard router
(1.000 dispatch accuracy), not three merge algorithms across three densities and two seed banks,
not an eight-expert learned mixture, not monolithic training, not leave-one-transform-out, not
three pre-registered repairs.

**Grid A `H1`, n=1,214**, paired cluster bootstrap by `program_id`:

| system | `H1` % | vs control | 95 % CI |
|---|---|---|---|
| `tuned_S2_s17` — one specialist | **28.01** | **+3.46** | [+2.06, +4.94] |
| **`tuned_L0` — THE CONTROL** | **24.55** | — | — |
| `merge_dare_ties` — best merge | 23.89 | −0.66 | [−1.89, +0.66] |
| `mono_all` | 22.90 | −1.65 | [−3.79, +0.49] |
| `l0merge_dare_ties` — 3× clean-code merge | 21.42 | **−3.13** | [−4.78, −1.40] |
| `base` | 6.43 | −18.12 | — |

**The mechanism, which is the transferable part.** Two offsetting effects of nearly equal size:
merging *costs* −3.13 [−4.78, −1.40] while specialists *contribute* +2.47 [+1.32, +3.70]. Net: a
wash. And the systems are **redundant at the item level** — an oracle over ten of them sits
**52.9 points below** a marginal-preserving permutation null; 61 % of items are solved by nothing.
There is no hidden complementary capability for a better combiner to find.

> Do not repeat the earlier phrasing *"the per-condition experts carry nothing distinct"* — it was
> read off an underpowered grid and is **retired** (§8.10). They carry ~2.5 points; merging cancels it.

---

## RQ3 — Mechanism: **run, and causal**

Full account: [`../docs/REPORT_2026-08-26_rq3-attention-mechanism.md`](../docs/REPORT_2026-08-26_rq3-attention-mechanism.md).

**Attention re-anchoring.** 3,600 dumps, 4 systems × 6 conditions × 6 layers. `tuned_S2` moves
attention off identifiers onto control/dataflow, specifically on `S2`: **+0.111 [+0.093, +0.131]**,
2.6× the next system, null or negative on every other condition.

**And it is load-bearing, not incidental.** Suppress attention to identifier tokens and measure
log P(gold):

| system | Δ log P(gold) | 95 % CI |
|---|---|---|
| `base` | −0.0892 | [−0.1578, −0.0230] |
| `tuned_L0` | −0.0321 | [−0.0819, +0.0187] |
| **`tuned_S2_s17`** | **+0.0145** | [−0.0515, +0.0880] |

Paired against `base`: **+0.1037 [+0.0109, +0.2085]** — the pre-registered prediction, confirmed.
The deflationary reading is ruled out: `tuned_S2` is hurt *more* under full knockout (−2.544 vs
−1.590), so it depends on the program more overall and on identifiers less specifically.

> **Methodological lesson worth carrying:** the first accuracy-based knockout was a clean null. It
> was a *floor*, not a null — `base` scores ~22 % on obfuscated `S2`, so exact-match had no dynamic
> range. A manipulation check (attention at masked keys → exactly 0.0000; 68 % of outputs change)
> is what caught it. Without it the write-up would have said "re-anchoring is not causal," which is
> false and which the data appeared to support.

---

## Normalization thread — a second, independent instrument agreeing

A purely symbolic dead-code-elimination pass, **zero training**, applied before the model sees the
program. On `S2`, Grid A:

| system | gain from symbolic DCE | 95 % CI |
|---|---|---|
| `base` | **+4.74** | [+3.12, +6.24] |
| `tuned_L0` | **+1.56** | [+0.30, +2.88] |
| `tuned_S2_s17` | **+0.06** | [−0.96, +1.08] |

A monotone dose-response in how much inert material each system trained on, with the specialist's
interval an **equivalence** result. Controls hold: on `L0`/`L1r`, which contain no dead code,
normalization does nothing for anybody. **Two independent instruments — a causal attention
intervention and a symbolic program transformation — agree the skill `tuned_S2` acquired *is*
dead-code elimination, implemented in attention.** Neither supports that alone.

---

## Side thread — CFT / bidirectionality (`paper_bidirectional/`, ATTRIB draft v4)

A replication that refutes its target. Two of the original paper's central claims were shown to be
**benchmark contamination artifacts** by testing on MBPP+ (genuinely held out — provenance verified
as apps 1584 / cruxeval 543 / humaneval 104 / **mbpp 0**): "a general coding benchmark does not fall
at all" is false on held-out data (`sft` is +1.2 on the contaminated benchmark, **−5.3** on the
clean one), and the one-direction/both-directions grouping does not replicate (−1.2 pp
[−3.8, +1.5]). Reframed around the surviving disproportion. **Lesson: a baseline that has already
run is not the same as a baseline that is valid.**

---

## Known weaknesses — a reviewer will find these first

1. **Everything outside the CFT thread is 1.5B and mostly single-seed.** And §12.3 argues against
   the project: five of seven obfuscation penalties largely dissolve at 7B (`L2` scores *above*
   clean code). Only `L1b` (−8.0), `S1` (−7.1) and **`H1` (−20.9)** survive. `H1` is the *only*
   penalty that does not shrink with scale, which strengthens every `H1`-based conclusion — but
   all RQ2/RQ3 findings must be scoped as "at a scale where these transforms still cost the model
   something."
2. **The matched-condition ICL baseline has never been run.** "Did you try just prompting with a
   few examples in the same obfuscation?" is the first reviewer question. `icl_k4_cross` (demos
   from a *different* condition) is the strongest ICL arm measured and loses to fine-tuning by
   +9.8 to +16.9 points — but that is an upper bound, not a measurement.
3. **One held-out family, partly burned.** Every invariance claim rests on `H1`, and §8.9 shows the
   control reads 40.0 / 34.8 / 33.9 across three passes — two of which are identical in *every*
   recorded field (adapter path, prompt sha, items, engine, sampling, commit, GPU) and still differ
   on 12 of 115 generations. Grid A contrasts are paired and unaffected, but Grid B `H1` readings
   were never resolvable.
4. **The step from "ignores inert material on `S2`" to "therefore transfers to `H1`" is still
   inferential.** No quarantined item was read in the RQ3 or normalization work. This is the single
   biggest gap and `01_NEXT_STEPS.md` Phase 1 exists to close it.
