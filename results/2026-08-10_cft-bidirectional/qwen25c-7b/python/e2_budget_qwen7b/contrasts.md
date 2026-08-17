# Arm contrasts - `e2_budget_qwen7b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.1 | 0.0 | **+0.1** | [+0.0, +0.2] | 300 | no |
| `flip` - `cft` | 33.5 | 0.1 | **+33.5** | [+31.9, +35.1] | 300 | yes |
| `flip` - `sft` | 33.5 | 0.0 | **+33.5** | [+31.9, +35.2] | 300 | yes |
| `mix50` - `sft` | 32.8 | 0.0 | **+32.8** | [+31.3, +34.4] | 300 | yes |
| `flip` - `mix50` | 33.5 | 32.8 | **+0.7** | [-0.3, +1.8] | 300 | no |
| `fwd2x` - `sft` | 0.1 | 0.0 | **+0.1** | [+0.0, +0.2] | 300 | no |
| `sft` - `base` | 0.0 | 12.9 | **-12.9** | [-14.9, -10.9] | 300 | yes |
| `cft` - `base` | 0.1 | 12.9 | **-12.8** | [-14.8, -10.9] | 300 | yes |
| `mix50` - `base` | 32.8 | 12.9 | **+19.9** | [+17.7, +22.2] | 300 | yes |
| `flip` - `base` | 33.5 | 12.9 | **+20.7** | [+18.4, +22.9] | 300 | yes |