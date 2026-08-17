# Arm contrasts - `e3_javascript_qwen1.5b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.4 | 0.0 | **+0.4** | [+0.0, +0.8] | 167 | no |
| `flip` - `cft` | 30.4 | 0.4 | **+30.1** | [+27.9, +32.1] | 167 | yes |
| `flip` - `sft` | 30.4 | 0.0 | **+30.4** | [+28.4, +32.5] | 167 | yes |
| `mix50` - `sft` | 30.3 | 0.0 | **+30.3** | [+28.3, +32.5] | 167 | yes |
| `flip` - `mix50` | 30.4 | 30.3 | **+0.1** | [-0.2, +0.5] | 167 | no |
| `sft` - `base` | 0.0 | 3.8 | **-3.8** | [-5.6, -2.4] | 167 | yes |
| `cft` - `base` | 0.4 | 3.8 | **-3.5** | [-5.1, -2.0] | 167 | yes |
| `mix50` - `base` | 30.3 | 3.8 | **+26.5** | [+23.4, +29.3] | 167 | yes |
| `flip` - `base` | 30.4 | 3.8 | **+26.6** | [+23.5, +29.5] | 167 | yes |