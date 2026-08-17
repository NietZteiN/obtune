# Arm contrasts - `unlearn_negation_python`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 12.7 | 0.0 | **+12.7** | [+10.8, +14.7] | 300 | yes |
| `flip` - `cft` | 33.7 | 12.7 | **+20.9** | [+18.6, +23.3] | 300 | yes |
| `flip` - `sft` | 33.7 | 0.0 | **+33.7** | [+32.1, +35.3] | 300 | yes |
| `sft` - `base` | 0.0 | 13.3 | **-13.3** | [-15.3, -11.3] | 300 | yes |
| `cft` - `base` | 12.7 | 13.3 | **-0.5** | [-1.1, +0.1] | 300 | no |
| `flip` - `base` | 33.7 | 13.3 | **+20.4** | [+18.0, +22.7] | 300 | yes |