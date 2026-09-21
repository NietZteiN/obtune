# 2026-09-20 — JavaScript evaluation is runnable, and half of it is contaminated

**Thread:** transfer · **Data:** `results/cells/crosslang_generic/` on CodeLlama-7B and
Llama-3.1-8B (48 cells each, 4 arms × 12 conditions). Forward only.
Config `configs/eval/crosslang_fwd.yaml`, analysis `scripts/analysis/78_crosslang.py`.

## JavaScript was never as blocked as the charter says

CLAUDE.md §2 records that `node` is absent and that this blocks everything JavaScript, and
`threats.tex` carries it as a limitation. The block is real but narrower than written:

* **Regenerating** the corpus needs the H1/H2/H3 generators, which need `node`. Still blocked.
* **Backward** grading executes the predicted input through `obtune.exec.pool`, which shells out
  to `NODE_BIN`. Still blocked.
* **Forward** grading is `scoring.py`'s `javascript` branch, which is `json.loads` against the
  `output_repr` already present in the item files. **No interpreter is involved at any point.**

The corpus transferred intact. So the forward half of the cross-language experiment has been
runnable this whole time. Every adapter is Python-trained; evaluating them on JavaScript items is
the experiment, so the adapter paths hardcode `python` rather than using `{language}`.

## The contamination, and two wrong checks before the right one

CruxEval-X and HumanEval-X are **ports**. `cruxevalx_js_14` and `cruxeval_sample_14` are the same
program — same body, same arguments `("   OOP   ",)`, same output `"POO"`. Confirmed by reading
the pair side by side, not inferred from the numbering.

**87 of the 168 JavaScript test programs (51.8 %) have their Python twin in the Python `train`
split.** On those an adapter can reproduce a memorised program→output pair instead of reading the
JavaScript, so they cannot support a transfer claim.

Two checks failed before this one, and both failed silently in the reassuring direction:

1. Compared JavaScript eval ids against training ids: **zero overlap**, reported as clean. True
   and irrelevant — the ids differ by language, the programs do not.
2. Compared against every id in `data/train/**/python.jsonl`: **74 % contaminated**, and, applied
   to the Python panel, reported all 557 Python eval programs as trained-on. That tree is the full
   **pool**; the partition lives in `data/splits/python.json` and is applied at load time.

The authority is the split file. Against it: JavaScript 87/168 contaminated, and **the Python
panel is clean — 557 of 557 eval programs in `test`, none in `train`.** The main results are
unaffected; this is a JavaScript-only problem created by evaluating one language with adapters
trained on another.

## What survives, on the 81 uncontaminated programs

Percent of the untuned model's accuracy on clean JavaScript:

| model | group | base | clean | breadth | merge |
|---|---|---|---|---|---|
| CodeLlama-7B | `L0` | 100 | 152 | 166 | 154 |
| | singles | 80 | 142 | 164 | 148 |
| | d2 seen | 76 | 139 | 162 | 143 |
| Llama-3.1-8B | `L0` | 100 | 188 | 173 | 196 |
| | singles | 79 | 171 | 172 | 178 |
| | d2 seen | 63 | 158 | 172 | 167 |

**The recovery claim crosses the language boundary.** Every adapted arm reading *obfuscated*
JavaScript exceeds the untuned model reading *clean* JavaScript, on every condition group and both
models, with no adapter having seen a line of JavaScript. Against base: $+20.9$ to $+30.8$ points,
all significant.

## What is withdrawn

On the contaminated set I reported that pooled training transfers better across languages than the
merge, at $+12.92$ and $+11.71$ points, both significant. On the clean subset:

* CodeLlama-7B `+5.69 [+2.1, +9.3]` \*
* Llama-3.1-8B `-0.58 [-4.3, +2.7]`

Model-dependent, and null on one of two. **The claim is withdrawn.** The inflation is explained by
what contamination rewards: pooled training saw all six conditions of the twinned programs during
Python training, so it had the most to memorise.

## Consequences

* `threats.tex` and `evaluation.tex` both state that JavaScript "cannot be" evaluated. Both are
  wrong and need amending — but to a *narrower* claim than the full result suggested, and one that
  must state the 81-program subset and the forward-only restriction.
* The held-out obfuscator family has no JavaScript variant, so the unseen-family claim does not
  cross languages and was never attempted here.
* Any future cross-language work on these corpora must filter by twin. `78_crosslang.py` does it by
  default and prints the surviving program count so the subset cannot be silently assumed.

## Open

Two models. CodeLlama-13B and Granite-3.1-8B are queued. Nothing here is in the paper yet.
Nothing here reads H1.
