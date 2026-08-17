# CFT bidirectional evaluation — python, e2_budget_qwen7b

*Generated from `results/2026-08-10_cft-bidirectional/qwen25c-7b/python/e2_budget_qwen7b`. Model: `see run_manifest.json`.*

Replication of `nikiema2025contrastive` (arXiv:2509.05553). Design and the full deviation list: [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).

**300 test-split programs · 21000 generations · conditions L1b, L1r, L2, S1, S2.** The paper's third transformation (string encryption) maps onto our quarantined `H1` and is absent by design.

> `readability_*` is `metrics.readability_proxy`, **not** the Scalabrino et al. model the paper uses. Only within-run contrasts are interpretable; absolute values are not comparable to the paper's R.


## Reverse direction — the headline comparison

`success_paper` is the paper's criterion (§4.3.2: similarity to the obfuscated input below the threshold AND readability restored). `success_exec` is obtune's: the recovered program actually reproduces the original's outputs. `strict` is both.

| system | strategy | success_paper [95 % CI] | success_exec | strict | S(deobf,obf) | S(deobf,orig) | id-recall |
|---|---|---|---|---|---|---|---|
| `base` | simple | **23.3 %** [21.0 %, 25.5 %] | 81.0 % | 12.9 % | 0.572 | 0.571 | 0.598 |
| `sft` | simple | **0.4 %** [0.1 %, 0.7 %] | 89.2 % | 0.0 % | 0.696 | 0.520 | 0.436 |
| `cft` | simple | **0.2 %** [0.0 %, 0.5 %] | 91.3 % | 0.1 % | 0.720 | 0.538 | 0.486 |

### Reverse success by condition (C3: is any gain renaming-only?)

| system | `L1b` | `L1r` | `L2` | `S1` | `S2` |
|---|---|---|---|---|---|
| `base` | 4.7 % | 19.0 % | 18.7 % | 64.7 % | 9.3 % |
| `sft` | 0.0 % | 0.3 % | 0.0 % | 0.7 % | 1.0 % |
| `cft` | 0.0 % | 0.0 % | 0.0 % | 0.7 % | 0.3 % |

## Forward direction — did fine-tuning work at all?

`exec_parity` is the check the paper could not run: does the obfuscated program the model produced still compute the original's outputs?

| system | exec_parity [95 % CI] | S(gen,tool) | parse_ok | identity | empty |
|---|---|---|---|---|---|
| `base` | **92.9 %** [91.5 %, 94.3 %] | 0.459 | 99.8 % | 6.5 % | 0.0 % |
| `sft` | **97.1 %** [96.1 %, 97.9 %] | 0.635 | 99.9 % | 0.0 % | 0.0 % |
| `cft` | **97.5 %** [96.6 %, 98.4 %] | 0.636 | 99.7 % | 0.0 % | 0.0 % |

`identity` is the failure the paper reports for StarCoder (§4.1.3, excluded from their analysis for reproducing its input exactly) and for every SFT model in reverse (§4.3.3: "outputs nearly identical to the obfuscated input"). A high rate here means the arm is echoing, not transforming.


## CFT − SFT (C2), pooled over strategies

| measure | SFT | CFT | difference [95 % CI] |
|---|---|---|---|
| reverse success (paper) | 0.4 % | 0.2 % | **-0.2 %** [-0.5 %, 0.1 %] |
| reverse success (exec) | 89.2 % | 91.3 % | **2.1 %** [0.9 %, 3.3 %] |
| reverse identifier recall | 43.6 % | 48.6 % | **5.1 %** [4.1 %, 6.0 %] |
| forward exec parity | 97.1 % | 97.5 % | **0.5 %** [-0.1 %, 1.1 %] |

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
- adapter-effectiveness check: `{"cft": {"identical_rate": 0.027, "identical_to_base": 81, "n_compared": 3000}, "flip": {"identical_rate": 0.014333333333333333, "identical_to_base": 43, "n_compared": 3000}, "fwd2x": {"identical_rate": 0.014666666666666666, "identical_to_base": 44, "n_compared": 3000}, "mix50": {"identical_rate": 0.015, "identical_to_base": 45, "n_compared": 3000}, "rev": {"identical_rate": 0.032, "identical_to_base": 96, "n_compared": 3000}, "sft": {"identical_rate": 0.024333333333333332, "identical_to_base": 73, "n_compared": 3000}}`
- readability weights: `{"identifier_length": 0.15, "identifier_meaning": 0.55, "line_length": 0.15, "nesting": 0.15}`
