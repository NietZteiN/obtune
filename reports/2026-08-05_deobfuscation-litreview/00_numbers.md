# Fine-tuning LLMs on obfuscated code — what's been done, in numbers

*2026-08-05 · literature sweep for [`obtune`](../../) · full map in [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md)*

Verification marks: **✅** read out of the primary source (PDF in `papers/`) · **⚠️** secondary source
only · **✗** the widely-circulated number is wrong, see §4.

---

## 1. TL;DR

1. **Everyone fine-tunes toward recovery.** Every system below maps *obfuscated → clean*. Not one asks
   whether a model can **use** code it cannot clean. That is obtune's opening.
2. **The best results are not from bigger models — they are from injecting non-neural structure.** gMBA
   goes from **40.84 % → 92.78 %** exact match by concatenating a computed truth table to the embedding.
   Chisel hits **86 %** with *no LLM at all*. BinDeObfBench's own conclusion: task-specific SFT beats scale.
3. **Memorization is a named, measured phenomenon in this literature.** `nikiema2025contrastive` calls it
   **"cognitive specialization"**: standard SFT yields **0 %** reverse success. This is the same disease
   obtune's pilot found, diagnosed on a different axis — and it is the nearest prior work we have.
4. **Syntactic metrics lie.** A vanilla Transformer scores **78.05 BLEU** and **40.84 % exact match** on
   the same outputs. Justifies obtune's strict normalized exact match.
5. **Stacked obfuscation collapses everything.** Promon: 10 frontier models average **8.5 %** on
   three-pass ARM — but only **63.7 %** on *clean* ARM. Obfuscation pushes down from ~64 %, not 100 %.
6. **The supplied survey has 7 factual errors.** Corrected in §4; do not re-import them.

---

## 2. What's been done

| Framework / study | Target | Metric | Result | ✓ |
|---|---|---|---|---|
| **gMBA** `noh2025gmba` ACL-F'25 | Mixed Boolean-Arithmetic | Exact match | **92.78 %** (vanilla Transformer **40.84 %**) | ✅ |
| **gMBA** — same run | MBA | BLEU | **95.53 %** (vanilla **78.05 %**) | ✅ |
| **CISPA / Beste** `beste2025exploring` | Tigress, up to **7 chained** | Halstead length reduction | **89.21 %** avg, hardest scenario | ✅ |
| **Chisel** `mariano2024chisel` OOPSLA'24 | Control-flow extension | ≈original modulo renaming | **86.00 %** of 546 benchmarks · **no LLM** | ✅ |
| **BinDeObfBench** `hu2026bindeobf` | Binary → pseudocode | Semantic preservation | CodeLlama **72.92 %** (5-shot) | ✅ |
| **BinDeObfBench** — reasoning model | Binary → pseudocode | Semantic preservation | DeepSeek-R1 **70.29 %** — few-shot *hurts* it | ✅ |
| **CFT** `nikiema2025contrastive` | Variable renaming | Reverse pass rate | **0 %** baseline → **39–52 %** with CFT | ✗ |
| **CFT** — same paper | Dead code, string encryption | Reverse pass rate | **still ~0 %** — "failed to remove any dead code" | ✅ |
| **Poisoned identifiers** `guzman2026poisoned` | Misleading names (= our `L1b`) | False-name propagation | **100 %** persist · **8/8**, **5/5** baseline runs | ✅ |
| **Poisoned identifiers** — prompt reframed | Same code, new instruction | False-name propagation | **100 % → 0–20 %**, no weight update | ✅ |
| **Promon ATR Q1'26** `promon2026atr` | 3-pass OLLVM, ARM asm | Reconstruction success | **8.50 %** avg over 10 models | ✅ |
| **Promon** — clean baseline | *Unobfuscated* x86 asm | Reconstruction success | GPT-4o **48 %**; no model above **86 %** | ✅ |
| **DOBF** `roziere2021dobf` NeurIPS'21 | Identifier recovery (pretrain) | Rel. improvement | **+13 %** code translation · **+24 %** NL search | ✅ |
| **LLM4Decompile** `tan2024llm4decompile` | Binary → source | Re-executability | **>100 %** over GPT-4o/Ghidra · Ref **+16.2 %** | ✅ |
| **Acoda** `rao2026acoda` | Adversarial anti-LLM obfuscation | Attack success rate | **up to 70 %** across 7 models | ✅ |
| **Obfuscation vs vuln-detection** `li2025obfvuln` | 19 techniques × 15 LLMs | 4-level detection score | **Dual effect** — some transforms *help* | ✅ |
| **HexaCoder** `hajipour2024hexacoder` | Oracle-verified training pairs | Broken/vulnerable output | **−85 %** vs baseline generation | ✅ |
| **LoRA vs full FT** `gravereaux2025tradeoffs` | Malware explanation | Footprint / time / quality | **15.5 %** params → **−81 %** size, **−80 %** time, BLEU within **10 %** | ✅ |
| **DeBinVul** `manuel2024debinvul` | Vulns in decompiled binaries | Detection gain | **+19 / +24 / +21 %** (CodeLlama/Llama3/CodeGen2) | ✅ |
| **LLM4DOBF** `llm4dobf2026` | Tigress, OLLVM | SacreBLEU | **54.66** — *number not independently locatable* | ⚠️ |

**Datasets in play.** NeuReduce 80k/20k/10k ✅ · ExeBench 885,074 train / 2,134 test, sampled to
30,000 / 2,400 ✅ · BinDeObfBench 2,092 source programs → 1,564,816 stripped binaries → **2,108,736**
obfuscated programs, 6 levels, 63 configs ✅ · Chisel 546 benchmarks ✅ · DeBinVul 150,872 samples ✅.

---

## 3. Promon ATR Q1 2026 — Table 1 in full

The single most useful external calibration. Average reconstruction success across **ten** models
(Claude Opus/Sonnet/Haiku 4.5, GPT-5, GPT-4o, DeepSeek Chat + Reasoner, Gemini 3 Pro/Flash, Gemini 2.5 Pro)
× OLLVM × two ISAs × two input types. ✅

| Obfuscation level | ARM pseudocode | ARM assembly | x86 assembly |
|---|---|---|---|
| No obfuscation (baseline) | ~79.0 % | **~63.7 %** | ~74.0 % |
| Instruction Substitution only | 77.5 % | 51.6 % | 67.9 % |
| Bogus Control Flow only | 73.6 % | 45.2 % | 60.0 % |
| Control Flow Flattening only | 55.0 % | 33.9 % | 52.3 % |
| FLA + BCF | 42.4 % | 21.0 % | 32.8 % |
| **Full three-pass (SUB+FLA+BCF)** | **26.1 %** | **8.5 %** | **20.6 %** |

Also: Claude Opus 4.5 best overall, yet fails **16 %** of *clean* ARM pseudocode and **28 %** of clean ARM
assembly · on three-pass ARM it gets **50 %** from pseudocode vs **24 %** from raw assembly; GPT-4o **10 %**
vs **2 %** · x86 is **2.4×** ARM on average (individual gaps to **5×**), attributed to training-data
imbalance · FLA+BCF amplifies complexity **4.18×** (x86) / **5.50×** (ARM) over BCF alone — layers
compound multiplicatively, reaching ~610 basic blocks. All ✅.

**Read the ordering, not the absolute numbers** — the task is assembly reconstruction, not output
prediction.

---

## 4. Corrections to the supplied survey

| # | The survey says | The primary source says |
|---|---|---|
| 1 | BinDeObfBench: 2,108,736 programs "filtered to a final set of 2,092" | **Inverted.** 2,092 is the *input* — filtered source programs → 1,564,816 binaries → 2,108,736 obfuscated programs ✅ |
| 2 | Chisel is a "hybrid… Program Synthesis alongside neural models"; 86 % "execution success" | **No LLM at all** (OOPSLA 2024). 86 % is "almost identical *modulo variable renaming*" — structural, not execution ✅ |
| 3 | CFT reaches 39–52 % "across multiple transformation types" | **Variable renaming only.** Dead code and string encryption stayed failures ✅ |
| 4 | DOBF gives "up to 12.2 %" on code translation | **13 %**, plus **+24 %** on NL code search ✅ |
| 5 | LLM4Decompile: "22B V2 beat its 6.7B predecessor by 40.1 % on re-executability" | No such result. "22B" is **CodeStral-22B as a backbone** (+21.7 %). Headline is **>100 %** over GPT-4o/Ghidra ✅. The "200-instruction cliff" is not in this paper |
| 6 | DeBinVul "accuracy 0.85–0.91, F1 0.87–0.94" | Paper reports **+19/+24/+21 %** detection gains and **80–90 %** on *classification* ✅ |
| 7 | "Qwen3.5-27B, AndroZoo, 0.982 F1" — *I flagged this as implausible* | **The survey was right and I was wrong.** MDPI *Appl. Sci.* 16(11):5600, 12,000 APKs, RF 0.975 ✅. But it is Android malware *detection* — tangential |

Two author names in the first draft of `RELATED_WORK.md` were also invented and have been corrected:
the Elsevier malware paper is **Patsakis, Casino & Lykousas**, and the MDPI paper is **Taşkın & Doğru**.

---

## 5. What this means for obtune

**The pilot result is not an anomaly — it has a name and a prior measurement.**
`nikiema2025contrastive` found standard SFT gives **0 %** reverse success and coined *cognitive
specialization*: models learn the training distribution's transform, not the transform class. obtune's
pilot found the same shape on a different axis — control-relative, the only significant cell is the
trained condition (`L1b` **+16.2 pts** [+4.7, +28.5]) and the held-out obfuscator is **−3.0 pts**
[−10.5, +3.9] ([`PILOT_REPORT`](../../docs/PILOT_REPORT_2026-08-05.md)).

| | `nikiema2025contrastive` | obtune |
|---|---|---|
| Axis of the test | forward vs **reverse** direction | **held-out obfuscator family** (H1), direction fixed |
| Task at eval | recover the original | predict the output, code **stays obfuscated** |
| Fix proposed | Contrastive Fine-Tuning (works on renaming only) | — open; CFT is the obvious candidate |

**Per RQ.**
- **RQ1** — cite `nikiema2025contrastive` to make the pilot *expected*; `hu2026bindeobf` for
  "task-specific SFT beats scale" (justifies the 1.5B→7–8B ladder over a scale sweep); `promon2026atr`
  for the baseline-error-rate argument that keeps the `L0` control a **required cell**.
- **RQ2** — `guzman2026poisoned` is the strongest existing evidence that prompt reframing alone moves a
  large failure (**100 % → 0–20 %**), so the oracle-prompt arm is a live hypothesis, not a formality.
  `hu2026bindeobf`'s ICL divergence says report the one-shot arm **per model family**, never pooled.
- **RQ3** — CodeSteer is the direct neighbour; `li2025obfvuln` supplies the 19-technique taxonomy.
- **Human alignment** — nothing in this literature touches it. Genuine gap, inherited from Papers 1–3.

**The novelty claim that survives contact with the evidence:** no surveyed paper evaluates on
*still-obfuscated* code with a *quarantined held-out obfuscator family*. `wang2026oasif` comes closest
(tunes for comprehension, not recovery) but works on assembly and has no held-out family.

---

## 6. Caveats

- **Scale.** obtune's decisive comparison rests on a **23-program common subset** (2,772–3,465 trials)
  against BinDeObfBench's millions. The novelty is the design, not the scale — the writeup should say so.
- **Not comparable numbers.** Promon and BinDeObfBench measure *reconstruction* on binaries; we measure
  *output prediction* on source. Cite them for orderings and baselines, never as a rival accuracy.
- **One number remains unverified** (⚠️): LLM4DOBF's SacreBLEU 54.66 — the framework exists, the figure
  was not locatable in an accessible source. It is the only ⚠️ in the sweep.
- **`taskin2026paradigms` and `llm4dobf2026` have no local PDF** — MDPI blocks automated fetch and IEEE
  is paywalled. Don't go looking; the bib carries DOI/URL.
- **This is a two-day-old sweep of a fast-moving area.** Four 2026 arXiv preprints here are unrefereed.
