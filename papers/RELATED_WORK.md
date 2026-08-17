# Related work — LLM fine-tuning on obfuscated code

*Last updated: 2026-08-05*

The field obtune sits next to but is **not** in. [`REFERENCES.md`](REFERENCES.md) registers the three
foundational human-comprehension papers this project descends from; this file maps the *deobfuscation
fine-tuning* literature that [`../CLAUDE.md`](../CLAUDE.md) §3 defines the project against — "We never
train or evaluate on recovery/deobfuscation. That is the clean separation from the DOBF lineage."

That separation is a claim about what other people have done. This file is the evidence for it.

**Two literatures, one gap.** §§1–3 cover work on *obfuscation*; **§4** covers work on *obtune's task* —
fine-tuning a model to predict what a program outputs. The two barely cite each other, and they leave
exactly complementary holes: the obfuscation papers have obfuscation without output prediction, the
execution papers have output prediction without obfuscation. **obtune is the intersection**, which is
the sharpest one-line statement of its novelty available.

## How to read this

Every numeric claim carries a verification mark:

| Mark | Meaning |
|---|---|
| ✅ | Read out of the primary source (PDF in this folder, or the paper's own abstract/HTML) on 2026-08-05 |
| ⚠️ | Secondary source only — the paper is real and the claim is plausible, but the number was not located in an accessible primary source |
| ✗ | **Corrected** — a widely-circulated figure that the primary source contradicts. See §9 |

PDFs are named `<bibtexkey>.pdf` (the `translation/papers/` convention: filename *is* the citation key,
`<firstauthorlastname><year><keyword>`) and wired into [`references.bib`](references.bib) via the
non-standard `file = {…}` field. Two sources have **no PDF here** — MDPI (`taskin2026paradigms`, which
blocks automated fetch) and IEEE (`llm4dobf2026`, paywalled). Don't go looking for them; the bib carries
the DOI/URL. `beste2025exploring` is present as the author preprint rather than the Springer
camera-ready, and `rong2026codesteer`'s PDF lives in a sibling project (path in its bib note).

---

## 1. The recovery lineage — what obtune is *not*

Every system below maps *obfuscated input → recovered/simplified output*. obtune never does this: the
model sees obfuscated code and predicts the program's **output**, and the code stays obfuscated at
evaluation time. This is what makes obtune's held-out condition meaningful — a recovery model that has
memorised an obfuscator and one that understands the transform class both score well on recovery.

| Key | System | Mechanism | Headline |
|---|---|---|---|
| `roziere2021dobf` | **DOBF** (Roziere et al., NeurIPS 2021) | Pre-training objective: mask identifiers with placeholders, predict the originals | **+13 %** rel. on unsupervised code translation, **+24 %** on NL code search ✅ |
| `gong2024astt5` | **AST-T5** (Gong, Elhoushi, Cheung, ICML 2024) | AST-aware span corruption — masks functionally coherent subtrees, not random spans | Structure-aware pretraining; no obfuscation eval ✅ |
| `noh2025gmba` | **gMBA** (Noh, Paik, Kwon, Cho, ACL Findings 2025) | Computes the MBA expression's **truth table**, concatenates it to the syntactic embedding | **92.78 %** exact match / **95.53 %** BLEU vs vanilla Transformer **40.84 %** / **78.05 %** on NeuReduce ✅ |
| `beste2025exploring` | **CISPA / Beste et al.** (2025) | Fine-tune DeepSeek-Coder-6.7B, Code Llama 7B (+GPT-4 baseline) on Tigress chains | **89.21 %** avg Halstead length reduction on the hardest scenario ✅ |
| `tan2024llm4decompile` | **LLM4Decompile** (Tan et al.) | 1.3B–33B series trained on binary↔source pairs | Beats GPT-4o and Ghidra by **>100 %** re-executability; Ref adds **+16.2 %** over End ✅ |
| `mariano2024chisel` | **Chisel** (Mariano et al., **OOPSLA 2024**) | Trace-informed compositional program synthesis — **no LLM** | **86 %** of 546 benchmarks recovered *almost identical modulo renaming*; ~**150k LOC** in 20 min ✅ |
| `sudhir2026pushan` | **Pushan** (Sudhir et al., 2026) | VPC-sensitive constraint-free symbolic emulation for VM-obfuscated binaries | Full CFG recovery on 1,000+ VMProtect/Themida binaries ✅ |
| `llm4dobf2026` | **LLM4DOBF** | GPT-3.5-turbo SFT + technique-specific "Contextual Statements" prompts | SacreBLEU **54.66** ⚠️ |

**gMBA is the sharpest illustration of why obtune measures what it measures.** A vanilla Transformer
scores 78.05 BLEU and 40.84 % exact match on the *same outputs* — the syntactic metric says "almost
right" about answers that are wrong. §5 returns to this.

**Chisel deserves a specific caveat** because it is routinely miscited as a neural/hybrid system. It is
pure program synthesis, published at OOPSLA 2024, and its 86 % is a *structural equivalence* claim
("almost identical modulo variable renaming to the original"), not an execution pass rate.

---

## 2. Memorization vs. genuine transformation learning

**This is the section that matters.** obtune's 2026-08-05 pilot
([`../log/pilot/2026-08-05_l0-control-refutes-invariance.md`](../log/pilot/2026-08-05_l0-control-refutes-invariance.md))
concluded **transform memorization, not semantic invariance**. That phenomenon has independent prior
measurement, and it is not currently cited anywhere in the repo.

### 2.1 `nikiema2025contrastive` — the nearest prior work

*Using Contrastive Learning to Improve Two-Way Reasoning in LLMs: The Obfuscation Task as a Case Study*
(Nikiema, Samhi, Moumoula, Djiré, Kaboré, Klein, Bissyandé — University of Luxembourg, arXiv:2509.05553,
Sept 2025).

Proposes **bidirectional reasoning** as the test of genuine understanding: can a model apply a
transformation in both directions without explicit reverse training? Findings:

- Fine-tuning on the forward task **degrades** reverse performance — they name this **"cognitive
  specialization."** ✅
- Standard SFT yields **0 %** reverse success across all transformation types; outputs come back
  "nearly identical to the obfuscated input rather than recovering original structure." ✅
- **Contrastive Fine-Tuning (CFT)** — a triplet of semantically-equivalent positives, altered-semantics
  negatives, and forward-direction examples — recovers **39–52 %** reverse success ✗ **on variable
  renaming only**: GPT-4.1-Mini 52.03 %, GPT-3.5-Turbo 50.51 %, Qwen2.5-Coder 39 %. Dead-code insertion
  ("failed to remove any dead code") and string encryption remained failures. ✅
- **Pattern-replication hierarchy** — fine-tuned models reproduce the *training distribution's* naming
  scheme rather than reasoning: GPT-3.5 sequential 42 % / systematic 40 % / custom 16 %; GPT-4.1-Mini
  custom 47 % / systematic 33 % / sequential 19 %; mixed patterns <2 %. ✅
- Setup: Qwen2.5-7B, Qwen2.5-Coder-7B, DeepSeek-R1.5-7B, Mistral-7B, StarCoder-15B, GPT-3.5-Turbo,
  GPT-4.1-Mini. 10,000 Java programs from CodeNet; eval on 300 ConDefects samples; CFT training 30,000
  instances. ✅

**Relation to obtune.** Same disease, different diagnostic. Nikiema et al. detect memorization by
asking for the transform *backwards*; obtune detects it by holding out an entire obfuscator family and
keeping the task fixed. Their axis is direction, ours is transform identity — so the results are
complementary, not redundant, and CFT is the obvious candidate intervention if obtune's RQ1 grid
confirms the pilot. Note their honest scope limit: CFT worked on *renaming*, the one transform where a
consistent inverse mapping exists. Our `S1`/`S2`/`H1` are exactly the cases where it did not.

**Cross-reference to our numbers** (`../docs/PILOT_REPORT_2026-08-05.md`, quoted not paraphrased):
untuned base scores `.111` on H1; the `L1b` adapter reaches `.384` and the `L0` **control** adapter
reaches `.414`. Against the base that is **+27.3 pts** [+15.2, +41.1] and **+30.3 pts** [+16.5, +45.8] —
the clean-code control transfers to the held-out obfuscator *as well or better*. Control-relative, the
only significant cell is the trained condition itself (`L1b` **+16.2 pts** [+4.7, +28.5]); held-out `H1`
is **−3.0 pts** [−10.5, +3.9]. The gain was task acquisition, not invariance.

**We are replicating it** (started 2026-08-08). Design, condition mapping and the deviation list:
[`../docs/CFT_REPLICATION.md`](../docs/CFT_REPLICATION.md); ledger:
[`../log/cft-replication/`](../log/cft-replication/). Two findings about the *method* fell out of
building the data layer, before any GPU time, and both belong in a writeup that cites this paper:

- **The three-term objective is not three-way balanced.** `L_CFT = L_pos + L_neg + L_gen` (eq. 5) is
  balanced by *instance count* ("10 000 each", §5.0.2), but a `gen` target is a whole program and a
  `pos`/`neg` target is the single token YES or NO. Measured on our Python mixture with the
  Qwen2.5-Coder tokenizer, `gen` carries **97.7 %** of the supervised-token mass (mean tokens per
  instance: gen 196.7, pos 3.0, neg 3.0). Instance upsampling cannot repair it — equal token mass
  needs ~86× and a ~976 000-instance mixture.
- **The reverse-success criterion has no validity gate.** As stated (§4.3.2) it is two inequalities —
  similarity to the obfuscated input below threshold, readability restored — and an empty string
  satisfies the first perfectly. In a stub run of our evaluator the literal placeholder
  `<stub:a1b2c3>` scored **17–24 %** "reverse success" until we added a `parses` precondition. This
  does not touch their 0 % SFT figure, but their **39–52 %** CFT figures rest on it.

A third observation is about obfuscation metrics generally rather than about this paper: our
readability proxy scores adversarial renaming (`L1b`) *above* the original, because misleading names
are well-formed English. Any readability-based reverse criterion is structurally blind to the
`L1b` family — a metric-level echo of `guzman2026poisoned` below.

### 2.2 `guzman2026poisoned` — misleading names survive the attempt to remove them

*Poisoned Identifiers Survive LLM Deobfuscation: A Case Study on Claude Opus 4.6* (Guzmán Lorenzo,
arXiv:2604.04289). 192 inference runs, two JavaScript artifacts (force-directed graph simulation, A*
pathfinding), 50 conditions.

- Poisoned names persisted in **every** baseline run — physics 8/8, pathfinding 5/5. ✅
- In **15 of 17** runs the model wrote the wrong variable name *while correctly describing the actual
  operation in a comment* — semantic understanding and surface output decoupled. ✅
- Reframing the prompt from "deobfuscate this" to "write a fresh implementation" cut false-name
  propagation from **100 % to 0–20 %** (physics) and **0 %** (pathfinding), with algorithmic structure
  preserved. ✅

**Relation to obtune.** This is a direct hit on the `L1b` condition (adversarial/misleading renaming)
and independently corroborates Paper 2's finding that L1b collapses accuracy where semantic displacement
meets identifier spikes. The task-reframing result is also a free datapoint for the **RQ2 oracle-prompt
arm**: a prompt change, with no weight update, moved the failure from 100 % to near zero. That is the
"models know how but not when" shape the charter anticipates — and it is evidence the RQ2 comparison
should be taken seriously rather than treated as a formality.

### 2.3 `hu2026bindeobf` — scale is not the axis

*Can LLMs Deobfuscate Binary Code?* (Hu, Shang, Shi, Cheng, Zhang, Li, Yang, Zhang, Lo; arXiv:2604.08083,
Apr 2026). Two findings bear directly on obtune's design:

- **Task-specific SFT outperforms broad domain pre-training**; "deobfuscation performance depends more
  on reasoning capability and domain expertise than on model scale." ✅
- **The in-context-learning divergence.** Few-shot prompting lifts instruction-tuned models (CodeLlama
  **72.92 %** semantic preservation at 5-shot) but *plateaus or degrades* reasoning models (DeepSeek-R1
  **70.29 %**) — the examples interfere with the model's own chain-of-thought. ✅
- At Level-6 (all six transforms at once), reasoning-oriented models still reduce injected complexity by
  **nearly 60 %**. ✅

**Relation to obtune.** The ICL divergence is a warning for the RQ2 `oracle_prompt_1shot` arm: whether
one-shot conditioning helps is *model-family-dependent* in the published record, so the arm should be
read per-model rather than pooled. It also independently supports Paper 2's reasoning-vs-coder alignment
split (ρ = 0.30–0.47 vs ≈ 0).

---

## 3. Comprehension under obfuscation *without* recovery — the line obtune is actually in

### 3.1 `promon2026atr` — the field's best "how bad is it" table

Promon Security Research Team, *App Threat Report Q1 2026: The State of Code Obfuscation Against AI*.
Ten models (Claude Opus/Sonnet/Haiku 4.5, GPT-5, GPT-4o, DeepSeek Chat + Reasoner, Gemini 3 Pro/Flash,
Gemini 2.5 Pro) × OLLVM (SUB / FLA / BCF) × ARM and x86 × assembly and Ghidra pseudocode. Table 1,
reproduced in full — **average reconstruction success across all ten models** ✅:

| Obfuscation level | ARM pseudocode | ARM assembly | x86 assembly |
|---|---|---|---|
| No obfuscation (baseline) | ~79.0 % | ~63.7 % | ~74.0 % |
| Instruction Substitution only | 77.5 % | 51.6 % | 67.9 % |
| Bogus Control Flow only | 73.6 % | 45.2 % | 60.0 % |
| Control Flow Flattening only | 55.0 % | 33.9 % | 52.3 % |
| FLA + BCF | 42.4 % | 21.0 % | 32.8 % |
| **Full three-pass (SUB+FLA+BCF)** | **26.1 %** | **8.5 %** | **20.6 %** |

Supporting numbers, all ✅: no model exceeded **86 %** on clean unobfuscated code under any input type;
GPT-4o managed **48 %** on clean x86 assembly; Claude Opus 4.5 was strongest overall yet still failed on
16 % of clean ARM pseudocode and 28 % of clean ARM assembly. Under three-pass ARM, Opus 4.5 got **50 %**
from pseudocode but **24 %** from raw assembly; GPT-4o **10 %** vs **2 %**. x86 success is **2.4×** ARM
on average (individual gaps to 5×), attributed to training-data imbalance. FLA+BCF amplifies structural
complexity **4.18×** (x86) / **5.50×** (ARM) over BCF alone — layers compound multiplicatively, not
additively, reaching ~610 basic blocks on both architectures.

**Relation to obtune.** The single most useful external calibration we have: it establishes that (a)
there is a large **baseline error rate on unobfuscated code** — obfuscation pushes models down from
~64–79 %, not from 100 % — which is precisely the argument for obtune's `L0` control adapter being a
*required cell* rather than an ablation; and (b) the per-transform ordering (substitution mild →
flattening severe) is an independent, binary-level replication of the identifier-vs-structural split
obtune inherits from Paper 2. **Caveat:** the task is *reconstruction*, not output prediction, and the
substrate is compiled assembly, not source. Cite it for the ordering and the baseline-error argument,
never as a comparable accuracy number.

### 3.2 `li2025obfvuln` — obfuscation sometimes *helps*

*A Systematic Study of Code Obfuscation Against LLM-based Vulnerability Detection* (Li, Li, Wu, Zhang,
Zhang, Xu, Zhong — Nanjing University, arXiv:2512.16538, Dec 2025). The most thorough obfuscation
taxonomy in the current literature: 3 classes (layout / data flow / control flow), 11 subcategories, 19
concrete techniques × 15 LLMs across 4 families (7B–671B), 4 languages, four-level scoring (detected /
type correct / location correct). ✅

Key finding: obfuscation exerts a **dual** influence — degradation is common, but some transformations
*improve* detection by stripping misleading surface cues. Control-flow virtualization and
mixed-language transformations degrade most. ✅

**Relation to obtune.** The "upgrade" effect is the mirror image of `L1b`: if misleading identifiers hurt
and *removing* identifiers can help, then `L1r` (random hex) and `L2` (sequential minification) are not
simply "more obfuscated" than `L1b` — they may be *easier*. Our pilot is consistent with this: the base
model scores `.242` on `L1b` but `.202` on both `L1r` and `L2`, while the `L1b`-tuned adapter scores
*higher* on `L1r` (`.576`) than on `L1b` itself (`.515`). Worth citing when we explain a non-monotonic
tier ordering.

### 3.3 Adversarial and steering work

- `rao2026acoda` — **Acoda** (Rao, Dong, Zhao, Li, Wang, arXiv:2606.11755): genetic-algorithm search over
  8 semantics-preserving strategies, optimised to defeat LLM analysis. **ASR up to 70 %** across seven
  SOTA models, strong cross-model transferability. ✅ Relevant as the adversarial ceiling: obtune's `H1`
  is a *held-out* family, not an *adversarially optimised* one, and we should say so rather than
  overclaim robustness.
- **CodeSteer** `rong2026codesteer` (Rong, Yadavally, Nguyen, ASE '26; PDF at
  `../../allocation_replication/paper/Post_hoc_Attention_Steering_of_Large_Language_Models_for_Robust_Code_Understanding_under_Obfuscation.pdf`)
  — post-hoc attention steering for robust code understanding under obfuscation. The **training-free
  counterpart to the RQ2 conditioning arm**, and the closest neighbour to RQ3's anchoring-shift metric.

### 3.4 Registered but not yet load-bearing

Four PDFs are in this folder and in the bib because they are close enough to be worth having, but no
claim in this file rests on them. Recorded so a future session knows they were read and placed, not
overlooked.

- `tkachenko2025deconstructing` — *Deconstructing Obfuscation: A Four-Dimensional Framework…*
  (arXiv:2505.19887). **Same lab as `promon2026atr`** (Promon AS, Oslo) and its peer-reviewable
  precursor. Prefer citing *this* over the marketing-framed threat report wherever both would serve;
  the report is better only for its Table 1 breadth.
- `patsakis2024assessing` — *Assessing LLMs in Malicious Code Deobfuscation of Real-World Malware
  Campaigns* (Patsakis, Casino, Lykousas; *Expert Systems with Applications*). Real campaigns rather
  than synthetic benchmarks — the ecological-validity counterweight to every Tigress/OLLVM result here.
- `feng2025recover` — *Can LLMs Recover Program Semantics? A Systematic Evaluation with Symbolic
  Execution* (Feng & Saha, Penn State, arXiv:2511.19130). The "KLEE-augmented pair tuning" entry that
  [`REFERENCES.md`](REFERENCES.md) previously listed only as a bare arXiv id.
- `wang2026oasif` — **OASIF** (Wang et al., Nankai, arXiv:2606.29155): obfuscation-aware *self-improving*
  fine-tuning for assembly comprehension. The nearest thing in the literature to obtune's setup —
  it tunes for comprehension rather than recovery — but on assembly, and without a held-out obfuscator
  family. Read it properly before the RQ1 writeup.

---

### 3.5 The FSE-shaped gap: *repairing* comprehension under obfuscation, not measuring it

*Added 2026-08-13, while scoping an FSE submission.*

§3.1–§3.4 are, without exception, **measurement** papers. `promon2026atr` builds the field's best
"how bad is it" table; `li2025obfvuln` reports that obfuscation sometimes *helps* a downstream
task; the adversarial and steering work perturbs inputs and observes damage. Every one of them
establishes that models degrade under transformation. **None of them tries to fix it and then
tests whether the fix generalises to a transformation it never saw.**

That is the gap, and it is narrower and more defensible than "obfuscated code understanding is
unexplored" — which is not true and a reviewer of `promon2026atr` will say so. The accurate claim
has three parts, and obtune can support all three:

1. **Nobody has built a controlled ladder and trained on it.** The measurement papers use whatever
   an off-the-shelf obfuscator emits, usually one setting. obtune has six single-transform
   conditions with identical semantics in two languages, plus a quarantined seventh
   (§3.2 of the charter) that no training run may touch.
2. **Nobody reports a held-out-transform result.** This is the sharp end. Measuring degradation on
   the transformation you selected is a within-distribution claim. The question a maintainer
   actually has — *will this survive an obfuscator I have not seen?* — requires a held-out family
   and a control that isolates "was fine-tuned at all" from "was fine-tuned on obfuscation".
3. **Nobody has compared the repair strategies against each other on one ladder.** Prompting,
   per-condition adapters, a learned router, monolithic training and weight merging are all
   plausible; §6 registers the merging machinery as *tools*, never as an object of study on this
   task.

**What obtune can honestly claim here, and what it cannot.**

| claim | support | status |
|---|---|---|
| specialisation is close to worthless | own-condition gain 3–4 pts, p95 seed noise 3.61 | **supported**, both languages, both seeds |
| routing is solved and buys nothing | router 100 % accurate, entropy ~1e-6, recovers specialists only | **supported** |
| merging generalises to an unseen obfuscator better than any specialist or the monolith | `merge_dare_ties` .348 on `H1` vs `tuned_L0` .245 and `mono_all` .229 | **strongest positive**, but n=40, one seed, one model |
| it works at scale | — | **NOT supported.** RQ1/RQ2 are 1.5B only; the 7B runs exist solely in the CFT thread |
| it works out of distribution | the `H1` row above | **partially** — one held-out family, and `H1` is a *family*, not a distribution shift in the statistical sense |

The third row is the paper. It is a modularity-and-maintenance result — *combine the specialists,
do not choose between them* — which is an FSE-shaped finding rather than an ML-benchmark one. But
it currently rests on 40 programs at one model size, and two cheap runs would change that: the 12
missing Grid B control cells (~10 GPU-minutes, §8.2 of the master report) and a second seed for
the merge arms. Without those, a reviewer's first two questions are exactly the two the table
above marks as unsupported.

**Counterweight, stated because §8.4 requires one.** "Merging beats specialists on held-out data"
has a mundane competing explanation: merged weights are closer to the clean-code model, and §3's
`tuned_L0` control already shows most of the `H1` gain comes from tuning on clean code at all. A
merge that dilutes six obfuscation-specific updates may simply be *regressing toward the control*.
Distinguishing "merging composes skills" from "merging averages toward clean-code tuning" needs a
merge of N random-seed L0 adapters as a control, which has not been run and should be before this
claim is made in print.

## 4. Fine-tuning for execution reasoning and output prediction — obtune's actual task

Sections 1–3 cover work on *obfuscation*. This section covers work on *obtune's task*: training a model
to predict what a program outputs. It is a separate literature that barely cites the obfuscation one,
and the two leave exactly complementary gaps — **the deobfuscation papers have obfuscation without
output prediction; these have output prediction without obfuscation. obtune is the intersection.**

| Key | System | Method | Result |
|---|---|---|---|
| `nye2021scratchpads` | **Scratchpads** (Nye et al., 2021) | Emit intermediate execution state token-by-token before the answer, rather than predicting it in one pass | Beats direct execution prediction "significantly in both the few-shot and fine-tuning regimes" ✅ |
| `liu2023codeexecutor` | **CodeExecutor** (Liu et al., ACL Findings 2023) | Pre-train on execution *traces*; mutation-based data augmentation + curriculum learning | ~**94 %** of single-line transformations; **76.42 %** output accuracy vs Codex **13.07 %**; **48.06 %** on the harder CodeNetMut ✅ |
| `gu2024cruxeval` | **CRUXEval** (Gu, Rozière, Leather, Solar-Lezama, Synnaeve, Wang) | *The benchmark, not a method.* 800 Python functions, 3–13 lines, input prediction + output prediction | GPT-4 + CoT **81 %** pass@1 on CRUXEval-O; Code Llama 34B **46 %** ✅ |
| `ni2024next` | **NExT** (Ni, Allamanis, Cohan, Deng, Shi, Sutton, Yin — ICML 2024) | Self-training: bootstrap execution-aware CoT rationales from traces, no manual annotation | **+26.1 pts** absolute fix rate on MBPP, **+14.3 pts** on HumanEval (PaLM 2); generalizes when traces are absent at test time ✅ |
| `ding2024semcoder` | **SemCoder** (Ding, Peng, Min, Kaiser, Yang, Ray — NeurIPS 2024) | "Monologue reasoning" — verbalize execution effects in natural language, rubber-duck style; SFT at 6.7B | CRUXEval-O **63.9 %**, CRUXEval-I **63.6 %**, HumanEval **79.3 %** — beats GPT-3.5-turbo (**59.0** / **50.3** / **76.8**) at 6.7B ✅ |

### 4.1 The one methodological tension this exposes

Every gain in the table comes from making execution **explicit** — a trace, a scratchpad, a monologue.
That is the field's central lever, and **obtune has deliberately switched it off**: the v1 SFT format is
no-CoT, justified in [`REFERENCES.md`](REFERENCES.md) by Paper 3's finding that CoT length
*anticorrelates* with accuracy (ρ = −0.52) on obfuscated code.

Both positions are defensible and they are not actually in conflict — Paper 3 measured *unprompted,
inference-time* CoT on obfuscated code, while this literature *trains* on execution-grounded rationales.
But the writeup should state the choice rather than leave it implicit, because a reviewer who knows
`ding2024semcoder` and `ni2024next` will ask why obtune does not do the one thing that reliably works on
this task. The honest answer is that it is a scoped v1 decision, not a claim that traces do not help.

### 4.2 `ding2024semcoder` is the direct methodological neighbour

Same task (output prediction), comparable scale (6.7B vs our 1.5B and 7–8B), same metric family
(exact-match pass@1 on execution). It is the natural "what does the ceiling look like without
obfuscation" reference for RQ1, and the closest thing to a baseline obtune's numbers can be read
against — with the caveat that its evaluation code is clean and ours never is.

### 4.3 ⚠️ CRUXEval is a training source, so it cannot also be the external yardstick

CRUXEval-O is the obvious external validity check for obtune's task. But `cruxeval` is already a
**tier-1 Python training source** in [`../configs/sources.yaml`](../configs/sources.yaml), and
`cruxeval-x` feeds Dataset B of the test set. The `exclude_ids` contamination list covers overlap with
obtune's *own* test set; it does not make a reported CRUXEval-O number clean, because the training
corpus is drawn from the same pool. Either exclude CRUXEval from training in a dedicated run, or report
external validity on a benchmark obtune does not train on. Worth deciding deliberately now rather than
discovering it at writeup.

---

## 5. Benchmarks, datasets, metrics

| Benchmark / dataset | Size | Task | Metric | What it cannot measure |
|---|---|---|---|---|
| **BinDeObfBench** `hu2026bindeobf` | 2,092 source programs → 1,564,816 stripped binaries → **2,108,736** obfuscated programs; 6 levels, 63 configs, 256–8,000 tokens ✅ | Binary → pseudocode deobfuscation | Lexical consistency, semantic preservation, simplicity, readability | Whether the model *understood* vs. pattern-matched; recovery-only |
| **NeuReduce** (via `noh2025gmba`) | 80k train / 20k val / 10k test ✅ | MBA expression simplification | Exact match + BLEU | Anything beyond single expressions |
| **ExeBench** (via `beste2025exploring`) | 885,074 train / 2,134 test functions; 30,000 / 2,400 sampled ✅ | Source→source Tigress deobfuscation | Halstead length reduction + I/O semantic correctness | Semantic correctness declines with chain depth — the paper says so |
| **Chisel benchmarks** `mariano2024chisel` | 546 benchmarks, 6 obfuscation techniques ✅ | Control-flow deobfuscation | Structural equivalence modulo renaming | Not an execution metric |
| **DeBinVul** `manuel2024debinvul` | 150,872 samples ✅ | Vuln. identify / classify / describe / name recovery in decompiled binaries | Accuracy, F1 | Deobfuscation proper |
| **Promon ATR Q1 2026** `promon2026atr` | 10 models × 2 ISAs × 2 input types × 6 levels ✅ | Assembly → working source reconstruction | Reconstruction success rate | Source-level comprehension |

### The metric-divergence problem

The literature's own recurring complaint, and obtune's justification for **strict normalized exact
match**. A vanilla Transformer on NeuReduce scores **78.05 BLEU** alongside **40.84 % exact match** ✅ —
flipping one operator inside a large polynomial destroys functional equivalence while barely moving the
n-gram score. The corollary in our own repo is the grading audit in `../../LOG.md` §2026-06-09 that found
~3 % false positives from containment matching (`927` inside `9273`), which is why
[`../CLAUDE.md`](../CLAUDE.md) §4 forbids substring grading. Cite `noh2025gmba` and `hu2026bindeobf`
together when defending execution-grounded evaluation.

---

## 6. PEFT machinery for RQ2

| Key | What it gives RQ2 |
|---|---|
| `hu2022lora` | The adapter method itself (r=32, α=64 in `configs/train/_base_lora.yaml`) |
| `yadav2023ties` | TIES-merging — the `merge_ties` arm |
| `yu2024dare` | DARE — the `merge_dare_ties` / `merge_dare_linear` arms |
| `gravereaux2025tradeoffs` | LoRA-vs-full-FT trade-off on EMBER 2018 malware: full FT wins BLEU/ROUGE by **up to 10 %**, but LoRA at **15.5 % trainable parameters** cuts model footprint **~81 %** and training time **>80 %** ✅ — the empirical warrant for obtune being LoRA-only on a 4×A6000 box |
| `hajipour2024hexacoder` | Oracle-guided synthetic training pairs (CISPA); verifying pairs with an external oracle before the weight update cut broken/vulnerable generations **by up to 85 %** ✅. Methodological precedent for obtune's semantic-gate validation in `05_build_variants.py` |

---

## 7. What this means for each obtune RQ

**RQ1 — Generalization.** `nikiema2025contrastive` is the citation that makes the pilot result *expected*
rather than anomalous, and CFT is the named intervention if the full grid confirms it. `hu2026bindeobf`
supplies "task-specific SFT beats scale," which justifies the 1.5B→7–8B ladder rather than a scale sweep.
`promon2026atr` supplies the baseline-error-rate argument for keeping the `L0` control as a required cell.

**RQ2 — Modularity.** `guzman2026poisoned` is the strongest existing evidence that prompt reframing
alone can move a large failure (100 % → 0–20 %) — i.e. the oracle-prompt arm is a live hypothesis, not a
control. `hu2026bindeobf`'s ICL divergence says report the one-shot arm per model family, not pooled.
`yadav2023ties` / `yu2024dare` / `hu2022lora` are the machinery citations.

**RQ3 — Mechanism.** CodeSteer is the direct neighbour — post-hoc attention steering under obfuscation —
and the reason RQ3's anchoring-shift metric needs to be framed as *predictive* first. `li2025obfvuln`
supplies the transform taxonomy for grouping token classes by obfuscation family.

**Secondary — human alignment.** Nothing in this literature measures human alignment; that remains
Papers 1–3's territory and is a genuine gap obtune inherits rather than shares.

---

## 8. Gaps in the field — what is actually unclaimed

The openings this survey exposes, audited honestly. **Read §8.3 first if you are looking for the
novelty claim** — one of the three claims the earlier draft of this section made does not survive
contact with `nikiema2025contrastive`.

### 8.1 Status audit

| Claim obtune might make | Nearest prior work | Status |
|---|---|---|
| "Fine-tuning teaches transform memorization, not the transform class" | `nikiema2025contrastive` — *cognitive specialization*, 0 % reverse under standard SFT | ⚠️ **Largely taken.** Different task, same headline. Being second *without a fix* is the weak position |
| "Models must be evaluated on still-obfuscated code, not recovered code" | `wang2026oasif` tunes for comprehension (assembly); §4 tunes for output prediction (clean code) | ⚠️ **Narrower than it looks.** Survives only as *source-level output prediction under obfuscation* |
| "A clean-code control is required to interpret any transfer claim" | **nobody** | ✅ **Open, and obtune already has the result** |
| "Memorization is graded by transform-family distance, not binary" | `nikiema2025contrastive` has forward/reverse binary | ✅ **Open** |
| "Held-out obfuscator *family*, quarantine-enforced" | `hu2026bindeobf` trains and tests on the same six transforms | ✅ **Open** |
| "Execution-grounded training under obfuscation" | §4 papers do it on clean code; Paper 3 contradicts them on obfuscated code | ✅ **Open, with a real prior disagreement** |
| "Does tuning move models toward or away from human difficulty orderings?" | **nobody in either literature has human data** | ✅ **Open, and obtune uniquely equipped** |

### 8.2 The openings, ranked by (claim strength × what obtune already has)

**G1 — The clean-code control invalidates a methodology.** *The strongest thing in the project.*
No work in §§1–4 includes a control adapter trained on unobfuscated code. obtune's pilot shows the
`L0` control reaches the held-out obfuscator **as well or better** than the obfuscated-code adapter
(**+30.3** vs **+27.3** pts over base). The consequence generalises far beyond obtune: **every claim of
the form "we trained on obfuscation X and generalised to unseen Y" in this literature is uninterpretable
without a clean control, because task acquisition alone reproduces that pattern.** That is a transferable
critique of a methodology, not a result about one model. *Needs:* replication at grid scale across models
and languages — already a required cell. *Risk:* low. *This should lead the paper, not sit in §3 of it.*

**G2 — Nobody has tested whether a proposed fix survives past renaming.** `nikiema2025contrastive`'s CFT
reaches 39–52 % on *variable renaming* and roughly nothing on dead-code insertion and string encryption —
their own reported scope limit. No one has tested an invariance intervention against **structural**
transforms or a **held-out family**. obtune's `S1`/`S2`/`H1` are purpose-built for exactly that.
*Needs:* a CFT arm ported to output prediction. *Risk:* medium — CFT might work, which is equally
publishable. *This is the opening that converts "we replicated Nikiema" into "we bounded Nikiema."*

**G3 — Does execution-grounded training rescue invariance? (highest ceiling)** A genuine prior
disagreement, not just a gap. §4 says making execution explicit is *the* lever — `ding2024semcoder` beats
GPT-3.5-turbo on CRUXEval-O at 6.7B by verbalizing execution; `ni2024next` gets +26.1 pts from trace
rationales. Paper 3 says CoT length **anticorrelates** with accuracy on obfuscated code (ρ = −0.52).
Neither has tested the other's regime, and **nobody has run execution-grounded SFT on obfuscated code.**
*Needs:* a trace/monologue SFT format and trace generation. *Risk:* medium-high, and it is the only
opening that converts obtune's no-CoT decision from an unrun ablation into a tested arm — see §8.3.

**G4 — Conditioning vs. capacity, measured on one ladder.** `guzman2026poisoned` moved a 100 % → 0–20 %
failure by prompt reframing alone, **zero weight updates**. `hu2026bindeobf` shows in-context examples
help instruct models and *hurt* reasoning models. Nobody has compared prompting against adapters against
merging on a single controlled obfuscation ladder. RQ2 already is this experiment. *Risk:* low —
"models know how but not when" is publishable either way.

**G5 — Human alignment under tuning (unique, currently under-weighted).** Nothing in either literature
has item-level human data; obtune has the 98-cell Paper-2 anchor. A **dissociation** — accuracy rises
while alignment with human difficulty orderings falls — would be a striking and wholly unclaimed result.
*Needs:* nothing new; the data exists. *Risk:* power, at n=98 cells. *Currently labelled "secondary";
on this evidence it may deserve promotion.*

**G6 — When does obfuscation *help*?** `li2025obfvuln` found some transforms *improve* model performance
by stripping misleading surface cues. obtune's pilot is already consistent: base scores `.242` on `L1b`
but `.202` on `L1r` and `L2`, and the `L1b`-tuned adapter scores **higher** on `L1r` (`.576`) than on
`L1b` itself (`.515`). Nobody has characterised *when* the identifier channel is worse than no channel.
*Needs:* nothing — the grid already produces the data. Cheap to pre-register, and it makes a
non-monotonic tier ordering a predicted finding rather than a confusing one.

**G7 — Mechanism.** Nothing in §§1–4 opens the model. CodeSteer steers attention *without* training;
no one has asked what *tuning* changes internally under obfuscation. RQ3. *Risk:* high — the
attention-is-not-explanation problem is why the design keeps the claim predictive until knockout.

**G8 — There is no benchmark for comprehension under obfuscation.** CRUXEval is clean code;
BinDeObfBench and the rest are recovery. A released stimulus set with a quarantined held-out family
would be an artifact contribution independent of whether the RQ1 result is positive or negative.

### 8.3 What looks like an opening but is not

- **"We deliberately did not train on explicit execution."** This is an *unrun ablation*, not a finding.
  It becomes a contribution only under **G3**, where both arms are run and compared. Stated as a design
  choice it reads to any reviewer who knows `ding2024semcoder` as skipping the one lever known to work.
- **"We use output prediction rather than recovery."** A framing, not a result, until it produces a
  finding recovery-based evaluation could not have produced. **G1** is that finding; the framing alone
  is not.
- **"Fine-tuning teaches memorization, not invariance."** As a standalone claim this is a
  better-controlled replication of `nikiema2025contrastive` on a different task. Strong as a *section*;
  thin as a *paper*. What makes it a paper is G1 (the control), G2 (bounding their fix), or G3 (a
  different intervention).

### 8.4 Honest counterweight

obtune's evaluated scale is much smaller than BinDeObfBench's or Beste's, and the pilot's decisive
comparison rests on a **23-program common subset** (2,772–3,465 trials). The novelty is in the design,
not the scale, and the writeup should say so plainly.

Two further cautions. `../docs/design_doc_v0.1.md` §1 currently asserts "No existing work tests whether
fine-tuning improves reasoning on still-obfuscated code" — that needs narrowing to *source-level output
prediction*, since `wang2026oasif` tunes for assembly comprehension and §4 tunes for output prediction
on clean code. And if the RQ1 grid merely confirms the pilot while RQ2 and RQ3 come back null, the
project holds a partly-scooped negative result; **G1, G2 and G5 are the hedges against that, and all
three are cheap.** Better decided now than in the writeup phase.

---

## 9. Corrections to the source survey

This file was seeded from an AI-generated survey (`../../LLM Obfuscated Code Fine-Tuning.md`). Primary
sources contradict it in seven places. Recorded here so the errors are not re-imported later.

| # | Survey claim | What the primary source says |
|---|---|---|
| 1 | BinDeObfBench "2,108,736 programs aggressively filtered to a final set of 2,092" | **Inverted.** 2,092 *filtered source programs* → 1,564,816 stripped binaries → **2,108,736 obfuscated programs**. 2,092 is the input, not the output ✅ |
| 2 | Chisel is a "hybrid approach leveraging Program Synthesis alongside neural models"; 86 % "execution success" | Chisel (**OOPSLA 2024**) uses **no LLM at all**. Its 86 % is "almost identical *modulo variable renaming*" — structural, not execution ✅ |
| 3 | CFT reaches 39–52 % "across multiple transformation types" | **Variable renaming only.** Dead-code insertion ("failed to remove any dead code") and string encryption remained failures ✅ |
| 4 | DOBF gives "up to 12.2 %" on unsupervised code translation | **13 %** relative, plus **+24 %** on NL code search ✅ |
| 5 | LLM4Decompile: "the 22B V2 model outperformed its 6.7B predecessor by a massive 40.1 % on re-executability" | No such result. "22B" is **CodeStral-22B used as a backbone**, giving **+21.7 %** over smaller backbones (cf. Yi-Coder-9B +23.1 %). The paper's headline is **>100 %** over GPT-4o/Ghidra and **+16.2 %** for Ref over End ✅. The "200-instruction capability cliff" is not in this paper |
| 6 | DeBinVul "accuracy 0.85–0.91, F1 0.87–0.94" | Abstract reports **+19 % / +24 % / +21 %** detection gains for CodeLlama / Llama3 / CodeGen2 and **80–90 %** on vulnerability *classification*, over 150,872 samples ✅. The quoted ranges are not the paper's headline |
| 7 | "Qwen3.5-27B on AndroZoo, 0.982 F1" flagged as implausible during review | **The survey is right and the suspicion was wrong** — MDPI *Appl. Sci.* 16(11):5600, 12,000 APKs, RF baseline 0.975, RoBERTa 0.970 ✅. But it is Android malware *detection*, not deobfuscation: tangential, cite only in passing |

**Still unverified (⚠️, cite with care):** LLM4DOBF's SacreBLEU 54.66 (framework confirmed via IEEE
listing; number not in an accessible source).

---

## Changelog
- **2026-08-13** — §3.5 added: the FSE-shaped gap is *repairing* comprehension under obfuscation
  and testing it on a held-out transform, not measuring degradation (which §3.1–§3.4 already do).
  Records what obtune can and cannot claim, marks "works at scale" as unsupported (RQ1/RQ2 are
  1.5B only), and adds the merge-toward-control counterweight that must be ruled out first.

- **2026-08-05** — File created. Seeded from a supplied AI-generated survey, then every load-bearing
  number re-checked against primary sources. 20 open-access PDFs fetched into this folder. Seven survey
  errors corrected (§8). Four papers the survey missed were added: `guzman2026poisoned`, `li2025obfvuln`,
  `patsakis2024assessing`, `tkachenko2025deconstructing`.
- **2026-08-05 (same day, second pass)** — Closed the gap between this file and the bibliography. The
  first pass cited 18 keys that did not exist in `references.bib`; **22 entries were added**, so every
  key here now resolves. Renamed 7 PDFs to the `<firstauthorlastname><year><keyword>` convention and
  repointed the citations: `hexacoder2024`→`hajipour2024hexacoder`, `nanjing2025obfvuln`→`li2025obfvuln`,
  `poisoned2026identifiers`→`guzman2026poisoned`, plus `klee2025recover`→`feng2025recover`,
  `oasif2026`→`wang2026oasif`, `deconstructing2025obfuscation`→`tkachenko2025deconstructing`,
  `debinvul2024`→`manuel2024debinvul`. Corrected two keys invented in the first pass:
  `assaf2024malware` is really **Patsakis, Casino & Lykousas** (`patsakis2024assessing`, and the PDF *is*
  here — it was wrongly listed as paywalled), and `benmoussa2026paradigms` is really **Taşkın & Doğru**
  (`taskin2026paradigms`).
- **2026-08-05 (third pass)** — Added **§4**, the execution-reasoning / output-prediction literature. The
  first two passes mapped only the *obfuscation* field; obtune's actual task is output prediction, and
  that has its own fine-tuning line (`nye2021scratchpads`, `liu2023codeexecutor`, `gu2024cruxeval`,
  `ni2024next`, `ding2024semcoder` — 5 papers, 5 PDFs, bib now 34 entries). Records two things the
  earlier passes could not see: the **no-CoT tension** (§4.1 — every gain in that literature comes from
  making execution explicit, which obtune's v1 format switches off) and the **CRUXEval contamination
  caveat** (§4.3 — `cruxeval` is already a tier-1 training source, so CRUXEval-O is not a clean external
  yardstick). Sections 4–8 renumbered to 5–9; this incidentally repaired two cross-references
  ("See §9", "§5 returns to this") that had been off-by-one since the first pass. **Note for anyone
  following an older pointer: the corrections table moved from §8 to §9.**
- **2026-08-05 (fourth pass)** — Rewrote **§8** from a three-item novelty claim into an audited openings
  list (G1–G8), after a full read of `nikiema2025contrastive` §§1–4 prompted by the question *"do we
  actually have novelty over them?"* **The audit says: not on the headline claim.** Their cognitive
  specialization result and obtune's memorization result are the same claim on different tasks, and they
  have a fix where obtune has a negative result. §8.1 now marks each candidate claim taken / narrower /
  open; §8.2 ranks the real openings (G1 the clean-code control is the strongest and obtune already has
  the result; G2 bounding CFT past renaming; G3 execution-grounded training under obfuscation);
  §8.3 records three things that *look* like openings and are not — including "we deliberately did not
  train on explicit execution", which is an unrun ablation rather than a finding. §8.4 flags that
  `../docs/design_doc_v0.1.md` §1's "no existing work tests…" claim needs narrowing to *source-level*
  output prediction, given `wang2026oasif` and §4.
