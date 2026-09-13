# Master tables

*Generated 2026-09-13 04:19 UTC by `scripts/analysis/59_master_tables.py`. Every number is read from a cell or a config; `--` means the cell does not exist yet.*

## 1. Master grid — every model × every obfuscation type, forward and backward

Forward = output prediction (the task adapters were trained on). Backward = input prediction on the same programs, graded by execution; no adapter is trained on it. `base` columns are the untuned model's accuracy; every intervention column is its **change in points vs base** in that direction. In-context learning has no backward run. Stacks have no backward run. **`fmt`** marks a cell whose format-failure rate exceeds 0.25: its responses are mostly unparseable, so it measures the prompt contract rather than the task and is excluded from every mean. The backward task and the in-context run both use a one-shot template written for CodeLlama-7B, which passes the gate on every cell; most of the other panel models do not.


### CodeLlama-7B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 0.257 | 0.285 | +4.5 | +17.0 | +3.9 | +15.6 | -0.8 | +16.5 | +1.3 | +15.6 | +2.7 |
| L1b | 0.198 | 0.265 | +5.7 | +16.0 | -1.3 | +19.0 | +1.4 | +20.4 | +2.9 | +14.8 | +0.1 |
| L1r | 0.207 | 0.315 | +5.8 | +17.1 | +1.1 | +18.0 | -3.9 | +18.8 | -2.3 | +15.3 | +1.1 |
| L2 | 0.202 | 0.282 | +7.0 | +18.0 | +4.2 | +17.7 | -0.6 | +19.6 | -0.7 | +15.2 | +4.2 |
| S1 | 0.168 | 0.261 | +4.7 | +21.0 | fmt | +22.1 | +0.1 | +23.2 | +1.9 | +20.2 | +1.8 |
| S2 | 0.193 | 0.330 | fmt | +19.6 | fmt | +20.9 | -3.6 | +22.2 | +0.2 | +19.0 | +0.0 |
| X1 | 0.119 | 0.257 | -- | +14.9 | fmt | +11.2 | -2.0 | +16.6 | +2.5 | +19.7 | +3.4 |
| seen stacks (6) | 0.157 | -- | -- | +17.1 | -- | +20.8 | -- | +22.1 | -- | -- | -- |
| unseen-containing stacks (3) | 0.117 | -- | -- | +14.0 | -- | +12.1 | -- | +15.7 | -- | +19.2 | -- |

### CodeLlama-13B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 0.252 | 0.418 | fmt | +21.7 | -1.3 | +19.3 | fmt | +21.0 | fmt | +21.1 | fmt |
| L1b | 0.222 | 0.385 | fmt | +17.6 | +0.6 | +20.1 | fmt | +21.7 | fmt | +15.7 | fmt |
| L1r | 0.225 | 0.433 | fmt | +19.0 | -1.6 | +19.5 | fmt | +21.4 | fmt | +18.1 | fmt |
| L2 | 0.228 | 0.396 | fmt | +17.8 | -0.6 | +18.9 | fmt | +20.4 | fmt | +17.3 | fmt |
| S1 | 0.213 | 0.408 | +0.2 | +19.5 | +1.6 | +20.0 | fmt | +22.1 | fmt | +19.6 | fmt |
| S2 | 0.184 | 0.303 | fmt | +23.8 | +9.2 | +26.0 | fmt | +28.4 | fmt | +23.8 | fmt |
| X1 | 0.149 | 0.264 | -- | +14.5 | +0.3 | +10.5 | fmt | +14.3 | fmt | +20.4 | fmt |
| seen stacks (6) | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| unseen-containing stacks (3) | 0.140 | -- | -- | +13.6 | -- | +13.2 | -- | +15.9 | -- | +19.3 | -- |

### CodeLlama-34B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | fmt | 0.466 | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | -14.1 |
| L1b | 0.205 | 0.381 | fmt | +21.2 | fmt | +26.4 | fmt | +28.9 | fmt | +19.6 | fmt |
| L1r | 0.220 | 0.414 | fmt | +25.0 | fmt | +23.8 | fmt | +26.8 | fmt | +24.0 | fmt |
| L2 | 0.231 | 0.417 | fmt | +23.5 | -4.5 | +23.5 | -12.0 | +24.7 | fmt | +22.6 | -10.3 |
| S1 | 0.222 | 0.405 | fmt | +24.9 | fmt | +24.5 | fmt | +27.3 | fmt | +23.9 | -8.7 |
| S2 | 0.191 | 0.434 | fmt | +29.3 | fmt | +29.3 | -11.3 | +33.5 | fmt | +28.7 | -12.4 |
| X1 | 0.135 | 0.320 | -- | +19.0 | fmt | +16.3 | fmt | +19.9 | fmt | +24.5 | fmt |
| seen stacks (6) | 0.180 | -- | -- | +22.1 | -- | +25.2 | -- | +27.9 | -- | +22.4 | -- |
| unseen-containing stacks (3) | 0.139 | -- | -- | +16.6 | -- | +15.9 | -- | +20.1 | -- | +20.9 | -- |

### Llama-3.1-8B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 0.258 | 0.424 | +6.2 | +19.0 | -3.2 | +16.8 | fmt | +18.7 | fmt | +20.1 | -1.7 |
| L1b | 0.222 | 0.322 | +5.4 | +13.9 | +0.7 | +16.5 | fmt | +18.5 | fmt | +14.7 | +1.1 |
| L1r | 0.242 | 0.369 | +4.3 | +14.6 | +1.6 | +14.5 | fmt | +16.3 | fmt | +13.7 | +0.6 |
| L2 | 0.215 | 0.363 | +6.3 | +17.6 | +2.3 | +17.1 | fmt | +19.4 | fmt | +17.2 | -0.5 |
| S1 | 0.213 | 0.348 | +4.3 | +18.2 | +5.4 | +17.7 | fmt | +20.0 | fmt | +19.6 | +5.3 |
| S2 | 0.205 | 0.368 | +6.7 | +20.8 | +2.2 | +20.8 | fmt | +23.9 | fmt | +23.3 | +4.1 |
| X1 | 0.132 | 0.279 | -- | +11.7 | +3.1 | +9.0 | fmt | +12.4 | fmt | +20.0 | +6.4 |
| seen stacks (6) | 0.182 | -- | -- | +15.1 | -- | +18.6 | -- | +20.6 | -- | +16.4 | -- |
| unseen-containing stacks (3) | 0.134 | -- | -- | +11.1 | -- | +9.6 | -- | +12.5 | -- | +17.2 | -- |

### StarCoder2-15B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| L1b | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| L1r | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| L2 | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| S1 | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| S2 | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| X1 | fmt | fmt | -- | fmt | fmt | fmt | fmt | fmt | fmt | fmt | fmt |
| seen stacks (6) | fmt | -- | -- | fmt | -- | fmt | -- | fmt | -- | fmt | -- |
| unseen-containing stacks (3) | fmt | -- | -- | fmt | -- | fmt | -- | fmt | -- | fmt | -- |

### Gemma-3-12B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | fmt | 0.491 | fmt | fmt | -14.7 | fmt | -3.9 | fmt | fmt | fmt | -1.7 |
| L1b | fmt | 0.411 | fmt | fmt | fmt | fmt | +2.8 | fmt | fmt | fmt | +0.6 |
| L1r | fmt | 0.440 | fmt | fmt | -9.0 | fmt | -1.7 | fmt | fmt | fmt | -0.1 |
| L2 | fmt | 0.409 | fmt | fmt | -7.5 | fmt | +0.4 | fmt | fmt | fmt | +3.1 |
| S1 | fmt | 0.417 | fmt | fmt | fmt | fmt | +2.7 | fmt | fmt | fmt | +2.8 |
| S2 | fmt | 0.458 | fmt | fmt | -7.0 | fmt | +0.5 | fmt | fmt | fmt | +1.4 |
| X1 | 0.152 | 0.317 | -- | +15.7 | -2.7 | +11.0 | +2.3 | +13.7 | fmt | +22.3 | +5.7 |
| seen stacks (6) | fmt | -- | -- | fmt | -- | fmt | -- | fmt | -- | fmt | -- |
| unseen-containing stacks (3) | 0.158 | -- | -- | +13.5 | -- | +11.7 | -- | +13.7 | -- | +19.3 | -- |

### CodeGemma-7B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 0.237 | 0.289 | fmt | +22.9 | fmt | +20.2 | fmt | +20.8 | fmt | +22.6 | fmt |
| L1b | 0.185 | 0.230 | fmt | +19.7 | fmt | +24.0 | fmt | +25.1 | fmt | +16.0 | fmt |
| L1r | 0.213 | 0.286 | fmt | +18.6 | fmt | +20.4 | fmt | +20.4 | fmt | +17.7 | fmt |
| L2 | 0.208 | 0.263 | fmt | +20.4 | fmt | +21.4 | fmt | +21.4 | fmt | +18.3 | fmt |
| S1 | 0.195 | 0.253 | +1.7 | +21.0 | fmt | +22.1 | fmt | +22.6 | fmt | +22.8 | fmt |
| S2 | 0.198 | 0.245 | fmt | +25.2 | fmt | +23.1 | fmt | +25.0 | fmt | +24.6 | fmt |
| X1 | 0.143 | fmt | -- | +12.8 | fmt | +10.8 | fmt | +10.4 | fmt | +20.4 | fmt |
| seen stacks (6) | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| unseen-containing stacks (3) | 0.150 | -- | -- | +12.4 | -- | +11.5 | -- | +10.7 | -- | +17.1 | -- |

### Granite-3.1-8B

| condition | base fwd | base bwd | ICL Δf | LoRA-clean Δf | Δb | breadth Δf | Δb | anchored Δf | Δb | family Δf | Δb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 | 0.285 | 0.410 | +0.8 | +14.5 | fmt | +13.1 | fmt | +11.1 | fmt | +12.8 | -13.0 |
| L1b | 0.267 | 0.362 | +0.0 | +7.1 | fmt | +12.5 | fmt | +11.4 | fmt | +5.4 | fmt |
| L1r | 0.268 | 0.405 | -0.8 | +10.8 | fmt | +11.5 | fmt | +11.1 | fmt | +10.8 | -9.3 |
| L2 | 0.251 | 0.366 | -0.4 | +12.0 | fmt | +13.5 | fmt | +12.6 | fmt | +11.4 | fmt |
| S1 | 0.254 | 0.356 | -0.2 | +9.1 | fmt | +12.5 | fmt | +10.4 | fmt | +9.5 | -9.1 |
| S2 | 0.272 | 0.429 | +0.4 | +11.4 | fmt | +14.2 | fmt | +12.1 | -- | +12.5 | -- |
| X1 | 0.147 | -- | -- | +6.9 | -- | +6.0 | -- | +4.1 | -- | +13.5 | -- |
| seen stacks (6) | 0.236 | -- | -- | +7.8 | -- | +12.7 | -- | +12.0 | -- | +8.5 | -- |
| unseen-containing stacks (3) | 0.166 | -- | -- | +4.8 | -- | +4.3 | -- | +3.1 | -- | +11.4 | -- |

### Cross-model summary — mean change vs the untuned model, in points

| intervention | clean fwd | clean bwd | seen-obf fwd | seen-obf bwd | unseen-family fwd | unseen-family bwd |
|---|---:|---:|---:|---:|---:|---:|
| LoRA clean | +19.0 (n=5, 3 fmt) | -3.8 (n=4, 4 fmt) | +18.5 (n=30, 10 fmt) | -0.2 (n=17, 23 fmt) | +13.7 (n=7, 1 fmt) | +0.2 (n=3, 4 fmt) |
| breadth | +17.0 (n=5, 3 fmt) | -2.4 (n=2, 6 fmt) | +19.7 (n=30, 10 fmt) | -2.1 (n=12, 28 fmt) | +10.7 (n=7, 1 fmt) | +0.2 (n=2, 5 fmt) |
| anchored | +17.6 (n=5, 3 fmt) | +1.3 (n=1, 7 fmt) | +21.0 (n=30, 10 fmt) | +0.4 (n=5, 34 fmt) | +13.1 (n=7, 1 fmt) | +2.5 (n=1, 6 fmt) |
| family | +18.5 (n=5, 3 fmt) | -5.5 (n=5, 3 fmt) | +17.8 (n=30, 10 fmt) | -1.2 (n=20, 19 fmt) | +20.1 (n=7, 1 fmt) | +5.2 (n=3, 4 fmt) |

## 2. Models

| model | HF id | lineage | type | layers | hidden | chat template | role |
|---|---|---|---|---:|---:|---|---|
| CodeLlama-7B | `codellama/CodeLlama-7b-Instruct-hf` | Meta | coder | 32 | 4096 | system | pilot_and_ablation |
| CodeLlama-13B | `codellama/CodeLlama-13b-Instruct-hf` | Meta | coder | 40 | 5120 | system | main |
| CodeLlama-34B | `codellama/CodeLlama-34b-Instruct-hf` | Meta | coder | 48 | 8192 | system | main |
| Llama-3.1-8B | `meta-llama/Llama-3.1-8B-Instruct` | Meta | instruct | 32 | 4096 | system | candidate_main |
| StarCoder2-15B | `bigcode/starcoder2-15b-instruct-v0.1` | BigCode | coder | 40 | 6144 | merged | candidate_main |
| Gemma-3-12B | `google/gemma-3-12b-it` | Google | instruct | 48 | 3840 | system | candidate_main |
| CodeGemma-7B | `google/codegemma-7b-it` | Google | coder | 28 | 3072 | merged | candidate_main |
| Granite-3.1-8B | `ibm-granite/granite-3.1-8b-instruct` | IBM | instruct | 40 | 4096 | system | candidate_main |
| llama31-8b-base | `meta-llama/Llama-3.1-8B` | Meta | pretrained | 32 | 4096 | plain | candidate_main |

`chat template`: `system` = accepts a system role; `merged` = system text folded into the user turn; `plain` = no chat template (pretrained checkpoint, one-shot only). Qwen models are excluded by scope rule.

## 3. Dataset

| property | value |
|---|---|
| base programs (Python) | 2231 — apps 1584, cruxeval 543, humaneval 104 |
| split | by `program_id`, seed 17: train 1563 / val 111 / test (held-out eval) 557 |
| input cases per program | 3 (fixed), gold output executed from the clean parent |
| program length | mean 8.4 LOC |
| held-out eval items, clean (L0) | 557 programs × 3 cases |
| coverage per condition (programs) | L1b 553 · S1 416 · X1 405 · C_L1r_S1 418 · C_L1r_X1 405 — structural transforms decline some programs by design; the unseen family needs ≥3 sites |
| paired contrasts | run on the program subset common to every cell, recorded before evaluation |
| JavaScript | 168 held-out programs; corpus transferred intact, cannot be regenerated (no `node` on the cluster) |
| grading | strict normalised exact match, no containment; backward task graded by executing the produced call |

## 4. Obfuscation taxonomy

Single transforms are applied to the clean parent, never stacked, with identical semantics across languages. Stacks live in a separate namespace.

| code | family | transform | trainable | role in the paper |
|---|---|---|---|---|
| L0 | none | Normalized original | yes | clean reference |
| L1b | identifier | Adversarial/misleading renaming of ALL bindings including the entry function | yes | ladder |
| L1r | identifier | Random hex renaming of all bindings — v_<4hex> for variables, f_<4hex> for functions. | yes | ladder |
| L2 | identifier | Maximal identifier destruction: sequential minification (a, b, c, .. | yes | ladder |
| S1 | structural | Control-flow flattening of the entry function body into a dispatch loop with randomized non-seq | yes | ladder |
| S2 | structural | Opaque predicates (always-false/always-true guards) + never-called dead helpers. | yes | ladder |
| S3 | structural | Dead-code insertion ONLY (proposal X2) — 1-2 never-called module-level helpers, without S2's op | yes | depth-3/4 stacks only |
| S4 | structural | Opaque predicates ONLY (proposal X3) — 1-3 computed always-taken/never-taken guards at reachabl | yes | depth-3/4 stacks only |
| X1 | encoding | TRAINABLE SIBLING OF H1 (W6 lever 7, 2026-09-04) | yes | **unseen family** (trainable sibling of H1; every unseen-family number) |
| X1m | encoding | E6 MECHANISM ABLATION (2026-09-07): X1 with ONLY the MBA-arithmetic half -- every + - ^ through | yes | mechanism half of X1 |
| X1s | encoding | E6 MECHANISM ABLATION (2026-09-07): X1 with ONLY the string-encoding half -- every str literal  | yes | mechanism half of X1 |
| H1 | heldout | HELD OUT | no | quarantined; evaluation budget spent, never stacked |

**Stacked composites** (order matters; composition does not commute):

| code | composition | contains unseen family | used in |
|---|---|---|---|
| C_L1r_S1 | L1r → S1 | no | seen stacks (RQ1) |
| C_S1_L1r | S1 → L1r | no | seen stacks (RQ1) |
| C_L1b_S1 | L1b → S1 | no | seen stacks (RQ1) |
| C_L2_S4 | L2 → S4 | no | seen stacks (RQ1) |
| C_L1r_S3 | L1r → S3 | no | seen stacks (RQ1) |
| C_S4_S3 | S4 → S3 | no | seen stacks (RQ1) |
| C3_L1r_S3_S4 | L1r → S3 → S4 | no | depth-3/4 stacks |
| C3_S1_S3_S4 | S1 → S3 → S4 | no | depth-3/4 stacks |
| C3_L1r_S1_S4 | L1r → S1 → S4 | no | depth-3/4 stacks |
| C4_L1r_S1_S3_S4 | L1r → S1 → S3 → S4 | no | depth-3/4 stacks |
| C_L1r_X1 | L1r → X1 | yes | divergence ladder (RQ4) |
| C_X1_S1 | X1 → S1 | yes | divergence ladder (RQ4) |
| C_S2_X1 | S2 → X1 | yes | divergence ladder (RQ4) |
| C_L1r_X1m | L1r → X1m | yes | divergence ladder (RQ4) |
| C_S1_X1s | S1 → X1s | yes | divergence ladder (RQ4) |
| C3_L1r_S1_X1 | L1r → S1 → X1 | yes | divergence ladder (RQ4) |
