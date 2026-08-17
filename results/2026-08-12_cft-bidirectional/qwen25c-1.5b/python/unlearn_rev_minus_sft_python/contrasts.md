# Arm contrasts - `unlearn_rev_minus_sft_python`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `flip` - `sft` | 31.4 | 0.5 | **+30.9** | [+29.3, +32.5] | 300 | yes |
| `sft` - `base` | 0.5 | 2.7 | **-2.2** | [-3.1, -1.4] | 300 | yes |
| `flip` - `base` | 31.4 | 2.7 | **+28.7** | [+27.0, +30.4] | 300 | yes |