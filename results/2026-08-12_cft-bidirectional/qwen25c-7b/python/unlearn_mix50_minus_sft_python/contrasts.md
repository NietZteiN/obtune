# Arm contrasts - `unlearn_mix50_minus_sft_python`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `flip` - `sft` | 32.9 | 0.0 | **+32.9** | [+31.5, +34.5] | 300 | yes |
| `sft` - `base` | 0.0 | 12.8 | **-12.8** | [-14.8, -10.8] | 300 | yes |
| `flip` - `base` | 32.9 | 12.8 | **+20.1** | [+18.0, +22.4] | 300 | yes |