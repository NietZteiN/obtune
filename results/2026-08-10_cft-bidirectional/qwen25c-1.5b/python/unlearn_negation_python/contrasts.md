# Arm contrasts - `unlearn_negation_python`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.1 | 0.3 | **-0.2** | [-0.5, +0.1] | 300 | no |
| `flip` - `cft` | 31.4 | 0.1 | **+31.3** | [+29.6, +32.9] | 300 | yes |
| `flip` - `sft` | 31.4 | 0.3 | **+31.1** | [+29.4, +32.8] | 300 | yes |
| `sft` - `base` | 0.3 | 2.7 | **-2.4** | [-3.3, -1.5] | 300 | yes |
| `cft` - `base` | 0.1 | 2.7 | **-2.6** | [-3.5, -1.7] | 300 | yes |
| `flip` - `base` | 31.4 | 2.7 | **+28.7** | [+26.9, +30.5] | 300 | yes |