# 2026-09-20 — Removing the clean-code specialist costs nothing forward and 2 points backward

**Thread:** modularity · **Data:** `results/cells/mergeablate_{generic,inverse}/codellama-13b/`
(92 + 46 cells) · paired by program, program-clustered bootstrap, 2,000 resamples.

## The ablation

Four merges, identical in operator (DARE-TIES), density (0.5), weights (uniform) and rank (32),
differing only in ingredients: `struct` = S1+S2, `ident` = L1b+L1r+L2, `no-L0` = the five obfuscation
specialists, `6-way` = the paper's merge.

## Forward: the ingredients do not matter

Percent of the untuned model's clean-code accuracy, CodeLlama-13B, complete (92/92 cells):

| group | base | struct | ident | no-L0 | 6-way |
|---|---|---|---|---|---|
| `L0` | 100 | 191 | 188 | 190 | 189 |
| singles | 85 | 167 | 170 | 170 | 168 |
| depth-2 seen | 74 | 157 | 155 | 155 | 154 |
| unseen family | 57 | 123 | 118 | 120 | 119 |

`no-L0` − `6-way` on `L0` is **+0.12 [−0.6, +0.8]**, and `struct` − `no-L0` is **+0.30 [−0.8, +1.4]**.
Two specialists from one semantic view do what six do. Removing the clean-code specialist removes
nothing.

## Backward: the ingredients do matter

| arm | exec acc | exact args | format ok |
|---|---|---|---|
| base | 0.290 | 0.090 | 0.98 |
| `ident` | 0.291 | 0.109 | 0.82 |
| `no-L0` | 0.319 | 0.120 | 0.87 |
| `6-way` | **0.340** | **0.126** | 0.94 |
| `struct` | format-gated on every condition | — | — |

- `no-L0` − base **+2.97 [+1.7, +4.2]** \*
- `6-way` − base **+4.98 [+3.8, +6.2]** \*
- **`no-L0` − `6-way` −2.01 [−2.6, −1.5]** \*

The clean-code specialist contributes two points of backward accuracy, and the contribution is
significant. `ident` gains nothing at all backward (0.291 against base's 0.290). `struct` is
format-gated on every backward condition, so a two-specialist structural merge does not hold the
answer contract in the untrained direction.

## What this does to RQ1 and RQ3

The single sentence "ingredients do not matter" is wrong, and so is "the clean-code gain needs L0".
The answer is direction-dependent:

* **Forward, including on clean code, the ingredient set is irrelevant.** Any merge of obfuscation
  specialists reaches the same place. This is the finding the geometry supports: specialists already
  share directions at cosine +0.5 to +0.7, so adding more changes little.
* **Backward, the ingredient set matters.** The merge's robustness in the untrained direction —
  the paper's central claim — is partly carried by the clean-code specialist, and a narrow merge
  loses the format contract entirely.

RQ1's claim about clean-code recovery survives without L0. RQ3's claim about backward robustness
does not, and should say it is a property of the six-way merge rather than of merging in general.

One model. Three more are running, and this is the result to check hardest on them, because it is
the one that changes what the paper may claim.
