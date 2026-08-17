# Arm contrasts - `unlearn_mix50_minus_sft_python`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `flip` - `sft` | 30.6 | 0.3 | **+30.3** | [+28.5, +32.0] | 300 | yes |
| `sft` - `base` | 0.3 | 2.7 | **-2.4** | [-3.3, -1.5] | 300 | yes |
| `flip` - `base` | 30.6 | 2.7 | **+27.9** | [+26.1, +29.7] | 300 | yes |