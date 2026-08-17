# Arm contrasts - `e1_qwen1.5b_s42`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.1 | 0.3 | **-0.2** | [-0.5, +0.1] | 300 | no |
| `flip` - `cft` | 30.8 | 0.1 | **+30.7** | [+29.1, +32.3] | 300 | yes |
| `flip` - `sft` | 30.8 | 0.3 | **+30.5** | [+28.9, +32.2] | 300 | yes |
| `mix50` - `sft` | 29.9 | 0.3 | **+29.6** | [+27.9, +31.3] | 300 | yes |
| `flip` - `mix50` | 30.8 | 29.9 | **+0.9** | [+0.1, +1.6] | 300 | yes |
| `sft` - `base` | 0.3 | 2.9 | **-2.5** | [-3.5, -1.7] | 300 | yes |
| `cft` - `base` | 0.1 | 2.9 | **-2.7** | [-3.7, -1.9] | 300 | yes |
| `mix50` - `base` | 29.9 | 2.9 | **+27.1** | [+25.3, +28.9] | 300 | yes |
| `flip` - `base` | 30.8 | 2.9 | **+27.9** | [+26.2, +29.7] | 300 | yes |