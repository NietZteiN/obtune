# Arm contrasts - `e7_strategies_qwen7b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.8 | 3.0 | **-2.2** | [-2.7, -1.7] | 300 | yes |
| `flip` - `cft` | 32.9 | 0.8 | **+32.1** | [+30.6, +33.6] | 300 | yes |
| `flip` - `sft` | 32.9 | 3.0 | **+29.9** | [+28.5, +31.4] | 300 | yes |
| `mix50` - `sft` | 31.5 | 3.0 | **+28.5** | [+27.1, +30.0] | 300 | yes |
| `flip` - `mix50` | 32.9 | 31.5 | **+1.4** | [+0.6, +2.2] | 300 | yes |
| `sft` - `base` | 3.0 | 18.6 | **-15.7** | [-17.8, -13.6] | 300 | yes |
| `cft` - `base` | 0.8 | 18.6 | **-17.8** | [-19.9, -15.8] | 300 | yes |
| `mix50` - `base` | 31.5 | 18.6 | **+12.9** | [+10.6, +15.0] | 300 | yes |
| `flip` - `base` | 32.9 | 18.6 | **+14.3** | [+12.0, +16.5] | 300 | yes |