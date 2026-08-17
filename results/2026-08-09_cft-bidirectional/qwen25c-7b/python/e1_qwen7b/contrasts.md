# Arm contrasts - `e1_qwen7b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.1 | 0.0 | **+0.1** | [+0.0, +0.2] | 300 | no |
| `flip` - `cft` | 33.6 | 0.1 | **+33.5** | [+32.0, +35.1] | 300 | yes |
| `flip` - `sft` | 33.6 | 0.0 | **+33.6** | [+32.1, +35.3] | 300 | yes |
| `sft` - `base` | 0.0 | 13.1 | **-13.1** | [-15.1, -11.1] | 300 | yes |
| `cft` - `base` | 0.1 | 13.1 | **-13.0** | [-15.1, -11.1] | 300 | yes |
| `flip` - `base` | 33.6 | 13.1 | **+20.5** | [+18.2, +22.8] | 300 | yes |