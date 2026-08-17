# Arm contrasts - `e1_qwen1.5b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.3 | 0.4 | **-0.1** | [-0.5, +0.3] | 300 | no |
| `flip` - `cft` | 31.5 | 0.3 | **+31.2** | [+29.5, +32.9] | 300 | yes |
| `flip` - `sft` | 31.5 | 0.4 | **+31.1** | [+29.4, +32.9] | 300 | yes |
| `mix50` - `sft` | 30.6 | 0.4 | **+30.2** | [+28.5, +31.9] | 300 | yes |
| `flip` - `mix50` | 31.5 | 30.6 | **+0.9** | [-0.1, +1.9] | 300 | no |
| `sft` - `base` | 0.4 | 2.9 | **-2.5** | [-3.4, -1.6] | 300 | yes |
| `cft` - `base` | 0.3 | 2.9 | **-2.6** | [-3.6, -1.7] | 300 | yes |
| `mix50` - `base` | 30.6 | 2.9 | **+27.7** | [+25.9, +29.5] | 300 | yes |
| `flip` - `base` | 31.5 | 2.9 | **+28.6** | [+26.9, +30.5] | 300 | yes |