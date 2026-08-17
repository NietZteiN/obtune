# CFT bidirectional evaluation — python, bidir_qwen7b

*Generated from `results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b`. Model: `see run_manifest.json`.*

Replication of `nikiema2025contrastive` (arXiv:2509.05553). Design and the full deviation list: [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).

**300 test-split programs · 22500 generations · conditions L1b, L1r, L2, S1, S2.** The paper's third transformation (string encryption) maps onto our quarantined `H1` and is absent by design.

> `readability_*` is `metrics.readability_proxy`, **not** the Scalabrino et al. model the paper uses. Only within-run contrasts are interpretable; absolute values are not comparable to the paper's R.


## Reverse direction — the headline comparison

`success_paper` is the paper's criterion (§4.3.2: similarity to the obfuscated input below the threshold AND readability restored). `success_exec` is obtune's: the recovered program actually reproduces the original's outputs. `strict` is both.

| system | strategy | success_paper [95 % CI] | success_exec | strict | S(deobf,obf) | S(deobf,orig) | id-recall |
|---|---|---|---|---|---|---|---|
| `base` | augmented | **38.7 %** [35.9 %, 41.5 %] | 73.3 % | 21.6 % | 0.496 | 0.536 | 0.569 |
| `base` | cot | **34.7 %** [32.2 %, 37.4 %] | 78.3 % | 21.8 % | 0.508 | 0.538 | 0.579 |
| `base` | few_shot | **32.7 %** [30.2 %, 35.3 %] | 74.3 % | 17.7 % | 0.515 | 0.553 | 0.573 |
| `base` | simple | **23.6 %** [21.3 %, 25.9 %] | 80.9 % | 13.0 % | 0.571 | 0.570 | 0.598 |
| `sft` | augmented | **12.5 %** [11.0 %, 14.0 %] | 83.5 % | 4.8 % | 0.684 | 0.559 | 0.523 |
| `sft` | cot | **11.0 %** [9.7 %, 12.3 %] | 85.5 % | 5.5 % | 0.688 | 0.573 | 0.528 |
| `sft` | few_shot | **6.8 %** [5.5 %, 8.2 %] | 85.9 % | 2.0 % | 0.717 | 0.542 | 0.516 |
| `sft` | simple | **0.3 %** [0.1 %, 0.7 %] | 89.1 % | 0.0 % | 0.696 | 0.520 | 0.437 |
| `cft` | augmented | **2.6 %** [1.8 %, 3.3 %] | 86.5 % | 1.3 % | 0.713 | 0.557 | 0.519 |
| `cft` | cot | **3.0 %** [2.1 %, 3.9 %] | 91.5 % | 1.5 % | 0.782 | 0.574 | 0.569 |
| `cft` | few_shot | **1.9 %** [1.3 %, 2.7 %] | 85.3 % | 0.5 % | 0.690 | 0.536 | 0.492 |
| `cft` | simple | **0.2 %** [0.0 %, 0.5 %] | 91.7 % | 0.1 % | 0.722 | 0.537 | 0.485 |

### Reverse success by condition (C3: is any gain renaming-only?)

| system | `L1b` | `L1r` | `L2` | `S1` | `S2` |
|---|---|---|---|---|---|
| `base` | 10.5 % | 28.7 % | 29.2 % | 71.8 % | 21.8 % |
| `sft` | 0.1 % | 3.5 % | 4.1 % | 25.1 % | 5.5 % |
| `cft` | 0.0 % | 1.3 % | 0.8 % | 7.2 % | 0.3 % |

## Forward direction — did fine-tuning work at all?

`exec_parity` is the check the paper could not run: does the obfuscated program the model produced still compute the original's outputs?

| system | exec_parity [95 % CI] | S(gen,tool) | parse_ok | identity | empty |
|---|---|---|---|---|---|
| `base` | **92.6 %** [91.1 %, 94.1 %] | 0.459 | 99.8 % | 6.7 % | 0.0 % |
| `sft` | **97.2 %** [96.2 %, 98.1 %] | 0.635 | 99.9 % | 0.0 % | 0.0 % |
| `cft` | **97.5 %** [96.6 %, 98.4 %] | 0.637 | 99.6 % | 0.0 % | 0.0 % |

`identity` is the failure the paper reports for StarCoder (§4.1.3, excluded from their analysis for reproducing its input exactly) and for every SFT model in reverse (§4.3.3: "outputs nearly identical to the obfuscated input"). A high rate here means the arm is echoing, not transforming.


## CFT − SFT (C2), pooled over strategies

| measure | SFT | CFT | difference [95 % CI] |
|---|---|---|---|
| reverse success (paper) | 7.6 % | 1.9 % | **-5.7 %** [-6.4 %, -5.0 %] |
| reverse success (exec) | 86.0 % | 88.8 % | **2.8 %** [1.8 %, 3.7 %] |
| reverse identifier recall | 50.1 % | 51.6 % | **1.5 %** [1.0 %, 2.1 %] |
| forward exec parity | 97.2 % | 97.5 % | **0.3 %** [-0.2 %, 0.9 %] |

## The paper's reported numbers, for comparison

| quantity | paper | source |
|---|---|---|
| universal across all models and transforms | **0 %** | §4.3.3, Fig. 4 |
| our comparable model | **39.00 %** | Fig. 4, Qwen2.5-Coder-7B |
| commercial, not comparable to ours | **52.03 %** | Fig. 4, GPT-4.1-Mini |
| SFT echoes the obfuscated input back | **0.61–0.79** | §4.3.3 |
| across simple / few-shot / CoT / augmented | **ΔR ≈ 0.01–0.05** | §4.3.3 |
| vs SFT's 0.42–0.50; CFT preserves forward | **0.42–0.51** | §5.0.3 |

## Provenance

- CodeBLEU: `codebleu==0.7.0 (vendored, env/vendor/)`
- prompt template: `101309399bb1223a…` (`cft_v1`)
- reverse-success thresholds: `{"reverse_readability_tolerance": 0.1, "reverse_sim_threshold": 0.4}`
- adapter-effectiveness check: `{"cft": {"identical_rate": 0.017466666666666665, "identical_to_base": 131, "n_compared": 7500}, "sft": {"identical_rate": 0.018266666666666667, "identical_to_base": 137, "n_compared": 7500}}`
- readability weights: `{"identifier_length": 0.15, "identifier_meaning": 0.55, "line_length": 0.15, "nesting": 0.15}`
