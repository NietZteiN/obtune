# CFT bidirectional evaluation — python, e1_qwen1.5b

*Generated from `results/2026-08-09_cft-bidirectional/qwen25c-1.5b/python/e1_qwen1.5b`. Model: `see run_manifest.json`.*

Replication of `nikiema2025contrastive` (arXiv:2509.05553). Design and the full deviation list: [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).

**300 test-split programs · 21000 generations · conditions L1b, L1r, L2, S1, S2.** The paper's third transformation (string encryption) maps onto our quarantined `H1` and is absent by design.

> `readability_*` is `metrics.readability_proxy`, **not** the Scalabrino et al. model the paper uses. Only within-run contrasts are interpretable; absolute values are not comparable to the paper's R.


## Reverse direction — the headline comparison

`success_paper` is the paper's criterion (§4.3.2: similarity to the obfuscated input below the threshold AND readability restored). `success_exec` is obtune's: the recovered program actually reproduces the original's outputs. `strict` is both.

| system | strategy | success_paper [95 % CI] | success_exec | strict | S(deobf,obf) | S(deobf,orig) | id-recall |
|---|---|---|---|---|---|---|---|
| `base` | simple | **9.6 %** [8.1 %, 11.0 %] | 83.3 % | 2.9 % | 0.833 | 0.544 | 0.591 |
| `sft` | simple | **7.1 %** [6.0 %, 8.3 %] | 74.0 % | 0.4 % | 0.594 | 0.500 | 0.415 |
| `cft` | simple | **8.7 %** [7.6 %, 9.9 %] | 74.3 % | 0.3 % | 0.579 | 0.498 | 0.393 |

### Reverse success by condition (C3: is any gain renaming-only?)

| system | `L1b` | `L1r` | `L2` | `S1` | `S2` |
|---|---|---|---|---|---|
| `base` | 2.3 % | 1.3 % | 8.7 % | 34.7 % | 1.0 % |
| `sft` | 0.0 % | 1.7 % | 1.0 % | 29.3 % | 3.7 % |
| `cft` | 0.7 % | 0.3 % | 0.3 % | 41.0 % | 1.3 % |

## Forward direction — did fine-tuning work at all?

`exec_parity` is the check the paper could not run: does the obfuscated program the model produced still compute the original's outputs?

| system | exec_parity [95 % CI] | S(gen,tool) | parse_ok | identity | empty |
|---|---|---|---|---|---|
| `base` | **86.7 %** [83.7 %, 89.4 %] | 0.429 | 99.7 % | 69.7 % | 0.0 % |
| `sft` | **90.3 %** [88.5 %, 92.1 %] | 0.626 | 99.7 % | 0.0 % | 0.0 % |
| `cft` | **92.3 %** [90.9 %, 93.7 %] | 0.631 | 99.6 % | 0.0 % | 0.0 % |

`identity` is the failure the paper reports for StarCoder (§4.1.3, excluded from their analysis for reproducing its input exactly) and for every SFT model in reverse (§4.3.3: "outputs nearly identical to the obfuscated input"). A high rate here means the arm is echoing, not transforming.


## CFT − SFT (C2), pooled over strategies

| measure | SFT | CFT | difference [95 % CI] |
|---|---|---|---|
| reverse success (paper) | 7.1 % | 8.7 % | **1.6 %** [0.4 %, 2.9 %] |
| reverse success (exec) | 74.0 % | 74.3 % | **0.3 %** [-1.3 %, 1.9 %] |
| reverse identifier recall | 41.5 % | 39.3 % | **-2.2 %** [-3.0 %, -1.3 %] |
| forward exec parity | 90.3 % | 92.3 % | **2.0 %** [0.7 %, 3.4 %] |

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
- adapter-effectiveness check: `{"cft": {"identical_rate": 0.0006666666666666666, "identical_to_base": 2, "n_compared": 3000}, "flip": {"identical_rate": 0.0, "identical_to_base": 0, "n_compared": 3000}, "flipsym": {"identical_rate": 0.0, "identical_to_base": 0, "n_compared": 3000}, "mix50": {"identical_rate": 0.0, "identical_to_base": 0, "n_compared": 3000}, "rev": {"identical_rate": 0.07833333333333334, "identical_to_base": 235, "n_compared": 3000}, "sft": {"identical_rate": 0.0003333333333333333, "identical_to_base": 1, "n_compared": 3000}}`
- readability weights: `{"identifier_length": 0.15, "identifier_meaning": 0.55, "line_length": 0.15, "nesting": 0.15}`
