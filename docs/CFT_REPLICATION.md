# Replicating `nikiema2025contrastive` on the obtune corpus

*Last updated: 2026-08-08*

Nikiema, Samhi, Moumoula, Djiré, Kaboré, Klein & Bissyandé (2025), *"Using Contrastive
Learning to Improve Two-Way Reasoning in Large Language Models: The Obfuscation Task as a
Case Study"*, arXiv:2509.05553 — PDF at [`../papers/nikiema2025contrastive.pdf`](../papers/nikiema2025contrastive.pdf),
positioned in [`../papers/RELATED_WORK.md`](../papers/RELATED_WORK.md) §2.1.

## Why obtune runs this

The paper is the **nearest prior work** to obtune's pilot finding. It names the same
disease — fine-tuning on a forward code transformation produces a model that cannot run
the transformation backwards, which the authors call **cognitive specialization** — and
proposes **Contrastive Fine-Tuning (CFT)** as the cure. `RELATED_WORK.md` §7 names CFT as
the candidate intervention for obtune's RQ1 if the full grid confirms the pilot. Before
adopting an intervention we should know whether its result reproduces on our corpus, in
our languages, with our obfuscators.

The two projects measure the same disease on **different axes**:

| | axis of generalization | held-out thing | task |
|---|---|---|---|
| Nikiema et al. | direction (forward vs reverse) | the reverse *direction* | emit code |
| obtune | transform identity | the `H1` obfuscator *family* | emit a return value |

They are complementary, not redundant. This replication answers *their* question on *our*
data; it does not change obtune's own RQ1–RQ3.

## What the paper claims

| Claim | Paper's number | §
|---|---|---|
| Standard SFT gives zero reverse capability | **0 %** across all models and transforms | §4.3.3, Fig. 4 |
| ...while forward performance is high | P(T) > 0.85 | §4.3.3 |
| Fine-tuned models echo the obfuscated input back | S(C_deobf, C_obf) ∈ [0.61, 0.79] | §4.3.3 |
| Prompting cannot fix it | ΔR ≈ 0.01–0.05 across simple / few-shot / CoT / augmented | §4.3.3 |
| CFT recovers the reverse direction | **39–52 %** (GPT-4.1-Mini 52.03, GPT-3.5 50.51, QwenCoder 39.00) | §5.0.3, Fig. 4 |
| ...but only for variable renaming | dead code and string encryption still fail | §5.0.3 |
| CFT keeps forward performance | S(C_forward, C_orig) ∈ [0.42, 0.51] vs SFT's [0.42, 0.50] | §5.0.3 |

## The implementation

```
src/obtune/cft/
  prompts.py    the four task formats: gen / pos / neg (trained) + deobf (eval only)
  mutate.py     execution-verified semantics-ALTERING mutations -> the L_neg pool
  dataset.py    builds the three instance pools from data/train/ -> data/train/cft/
  metrics.py    CodeBLEU (vendored, official) + readability proxy + execution checks
  train.py      LoRA, one config key apart between the SFT and CFT arms
  evaluate.py   bidirectional eval: forward obfuscation + reverse deobfuscation
configs/cft/    data_v1.yaml · train/{sft,cft}_qwen1.5b_{py,js}.yaml · eval/bidir_v1.yaml
scripts/cft/    10_build_cft_data.py · 11_enqueue_arms.py
tests/          test_cft_prompts.py · test_cft_mutate.py · test_cft_dataset.py · test_cft_metrics.py
```

The objective, `L_CFT = L_pos + L_neg + L_gen` (paper eq. 5), is realised as joint
next-token cross-entropy over the union of three equally-sized pools — which is what a sum
of per-task losses over balanced datasets *is*. The two arms differ in exactly one config
key (`tasks`), so any gap between them comes from the extra two losses and not from a
different recipe.

## Condition mapping

The paper uses three transformations from a Java GUI obfuscator. Ours come from
`src/obtune/obf/` under a semantic gate, and the ladder is finer:

| Paper's transformation | obtune condition(s) | Note |
|---|---|---|
| Variable Renaming | `L1b` (adversarial), `L1r` (random hex), `L2` (sequential minify) | three resolutions of the paper's one |
| Dead Code Insertion | `S2` (opaque predicates + dead code) | |
| String Encryption | `H1` | **out of scope — quarantined** |
| — | `S1` (control-flow flattening) | we have it, the paper does not |

`H1` is the discriminator for obtune's own headline claim and is never trained on under
any circumstances (`../CLAUDE.md` §3.2, four enforcement layers). The paper's hardest
transformation is therefore the one arm this replication cannot run. That is a real
scope limit and every result table must say so rather than quietly reporting four
conditions where the paper reports three.

## Deliberate deviations, and why

**1. Negative construction (the one that could change a conclusion).**
The paper pairs a clean original against *clean* code with different semantics, while
every positive pairs clean against *obfuscated* code (§5.0.2). Under that design the
question "is program B obfuscated?" predicts the label perfectly, so a model can score
well on L_pos/L_neg without comparing semantics at all. Our default,
`negative_style: obfuscated_mutant`, makes the negative *the obfuscated variant with one
token changed* — positives and negatives are then equally obfuscated and surface
obfuscation-ness carries zero label information. The paper-literal `clean_mutant` style
is kept as a config option so the confound can be measured rather than argued about.

**2. Negatives are executed, not assumed.**
The paper says only "functionally different code". We generate single-operator mutations
(AOR / ROR / LCR / ICR, the standard mutation-testing families) and **run** each against
its parent's own input cases, keeping it only if an output genuinely differs *and* it
still runs cleanly on at least half the cases. The first check rules out equivalent
mutants — which would train the model that equivalent programs differ. The second keeps
negatives hard: a mutant that crashes on every input is spottable from the traceback
alone and teaches nothing semantic.

**3. Readability is a labelled substitute.**
The paper scores with Scalabrino et al.'s readability model, a Java tool with no
Python/JavaScript equivalent. `metrics.readability_proxy` is a weighted mean of four
components (identifier meaningfulness 0.55, identifier length 0.15, line length 0.15,
nesting 0.15), reported with its components so any movement can be attributed. **Absolute
values are not comparable to the paper's R**; only within-run contrasts are.

Its one non-obvious threshold was set by measurement, not taste: short identifiers are
read as minification rather than idiom above a 0.5 share of unique names, which over 400
Python programs separates clean code from `L2` at 8 % false positives / 89 % detection.

**4. Execution is added.**
obtune has a sandboxed executor and canonical outputs; the paper's setup does not. So
every generated program is also *run*. Forward: does the obfuscated program the model
wrote still compute the original's outputs? Reverse: does the recovered program? These
are reported alongside the paper's purely-syntactic criteria as
`forward_success_exec` / `reverse_success_exec`, and where the two disagree the report
says so instead of picking one.

**5. CodeBLEU is the published implementation, not a reimplementation.**
`codebleu==0.7.0`, vendored under `env/vendor/` so the pinned conda env in
`env/lock-obtune.txt` is untouched. It runs against the project's own tree-sitter
grammars (the distribution's incompatible tree-sitter pin is deliberately not vendored).
A home-grown CodeBLEU would make every threshold in the paper incomparable to ours.

**6. Scale.**
The paper uses 10 000 CodeNet Java programs and 30 000 CFT instances; our corpus has
1 563 Python / ~640 JavaScript training programs. Pools are capped at what the corpus
supports rather than resampled up to the paper's headline number. The models are also
smaller — Qwen2.5-Coder-1.5B-Instruct is obtune's pilot model, against the paper's 7–15 B
open-source panel — so a **null CFT result here is weaker evidence than a positive one**:
the paper itself reports that only the larger commercial models showed strong bidirectional
emergence ("architectural capacity hierarchy", §5.0.3).

## Running it

```bash
# 1. Build the three instance pools (CPU; the executor verifies every negative)
python scripts/cft/10_build_cft_data.py --config cft/data_v1.yaml
make check                     # new files enter the SHA manifest + H1-marker scan

# 2. Train both arms — enqueued, so they start when a GPU is genuinely idle
python scripts/cft/11_enqueue_arms.py --language python --write

# 3. Bidirectional evaluation, once both adapters exist
python -m obtune.cft.evaluate --config cft/eval/bidir_v1.yaml --gpu <idle>
```

## What a result would mean for obtune

* **CFT reproduces (reverse success rises from ~0 to tens of percent on renaming).**
  Then it is a live intervention for RQ1, and the next question is whether the same
  auxiliary losses move obtune's own metric — transfer to a *held-out obfuscator* under
  output prediction. That is a different experiment and it would need a decision about
  the `H1` read budget (`../CLAUDE.md` §3.2 rule 3 allows exactly two passes).
* **CFT does not reproduce at 1.5 B.** Consistent with the paper's own capacity
  hierarchy, and an argument for testing it at 7 B before drawing any conclusion — not
  an argument that CFT does not work.
* **Either way**, the SFT arm's reverse performance is a directly comparable
  replication of the paper's headline 0 %, and the forward/reverse asymmetry it produces
  is a second, independent measurement of the memorization that obtune's pilot found on
  the transform-identity axis.

## Changelog

- **2026-08-08** — Written alongside the implementation. Records the condition mapping,
  the six deviations from the paper, and the `H1` scope limit.
