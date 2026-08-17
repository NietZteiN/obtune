# Arm contrasts - `e2_factorial_qwen1.5b`

*Metric: `reverse_success_strict`. Paired cluster bootstrap by `program_id`, 2000 resamples, seed 17. Units are percentage points.*

| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |
|---|---|---|---|---|---|---|
| `cft` - `sft` | 0.3 | 0.3 | **-0.1** | [-0.5, +0.3] | 300 | no |
| `flip` - `cft` | 31.4 | 0.3 | **+31.1** | [+29.4, +32.9] | 300 | yes |
| `flip` - `sft` | 31.4 | 0.3 | **+31.1** | [+29.4, +32.9] | 300 | yes |
| `cftflip` - `flip` | 31.1 | 31.4 | **-0.3** | [-1.2, +0.5] | 300 | no |
| `cftflip` - `cft` | 31.1 | 0.3 | **+30.8** | [+29.2, +32.5] | 300 | yes |
| `fwd2x` - `sft` | 0.6 | 0.3 | **+0.3** | [-0.2, +0.8] | 300 | no |
| `sft` - `base` | 0.3 | 2.9 | **-2.5** | [-3.4, -1.7] | 300 | yes |
| `cft` - `base` | 0.3 | 2.9 | **-2.6** | [-3.5, -1.7] | 300 | yes |
| `flip` - `base` | 31.4 | 2.9 | **+28.5** | [+26.9, +30.4] | 300 | yes |

## 2x2 - contrastive objective x data direction

*300 programs scored on all four cells.*

| | forward only | + reverse data |
|---|---|---|
| **no aux objective** | `sft` 0.3 | `flip` 31.4 |
| **contrastive aux** | `cft` 0.3 | `cftflip` 31.1 |

| effect | estimate (pp) | 95 % CI | excludes 0 |
|---|---|---|---|
| **data** | +30.9 | [+29.3, +32.6] | yes |
| **objective** | -0.2 | [-0.7, +0.3] | no |
| **interaction** | -0.3 | [-1.3, +0.7] | no |
