# Arm contrasts - `bidir_qwen7b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.8 | 3.1 | **-2.2** | [-2.7, -1.8] | 300 | yes |
| `sft` - `base` | 3.1 | 18.5 | **-15.4** | [-17.4, -13.5] | 300 | yes |
| `cft` - `base` | 0.8 | 18.5 | **-17.7** | [-19.7, -15.8] | 300 | yes |