# Arm contrasts - `e2_seeds_qwen1.5b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.4 | 0.4 | **+0.0** | [-0.5, +0.5] | 300 | no |
| `flip` - `cft` | 30.9 | 0.4 | **+30.5** | [+28.8, +32.2] | 300 | yes |
| `flip` - `sft` | 30.9 | 0.4 | **+30.5** | [+28.8, +32.1] | 300 | yes |
| `mix50` - `sft` | 30.0 | 0.4 | **+29.6** | [+27.9, +31.3] | 300 | yes |
| `flip` - `mix50` | 30.9 | 30.0 | **+0.9** | [+0.1, +1.6] | 300 | yes |
| `sft` - `base` | 0.4 | 2.7 | **-2.3** | [-3.3, -1.4] | 300 | yes |
| `cft` - `base` | 0.4 | 2.7 | **-2.3** | [-3.3, -1.4] | 300 | yes |
| `mix50` - `base` | 30.0 | 2.7 | **+27.3** | [+25.5, +29.1] | 300 | yes |
| `flip` - `base` | 30.9 | 2.7 | **+28.1** | [+26.4, +29.9] | 300 | yes |