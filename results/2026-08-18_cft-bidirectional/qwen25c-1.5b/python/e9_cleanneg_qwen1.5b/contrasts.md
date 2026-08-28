# Arm contrasts - `e9_cleanneg_qwen1.5b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cftclean` - `sft` | 0.5 | 0.2 | **+0.3** | [-0.1, +0.7] | 300 | no |
| `cftclean` - `cft` | 0.5 | 0.2 | **+0.3** | [-0.1, +0.7] | 300 | no |
| `cft` - `sft` | 0.2 | 0.2 | **+0.0** | [-0.3, +0.3] | 300 | no |
| `cftclean` - `base` | 0.5 | 2.8 | **-2.3** | [-3.3, -1.4] | 300 | yes |
| `cft` - `base` | 0.2 | 2.8 | **-2.6** | [-3.5, -1.7] | 300 | yes |
| `sft` - `base` | 0.2 | 2.8 | **-2.6** | [-3.5, -1.7] | 300 | yes |