# 2026-09-20 — Ablation panel complete: what matters backward is breadth, not the clean-code specialist

**Thread:** modularity · **Supersedes the numbers in**
[`2026-09-20_the-l0-ingredient-matters-backward-only.md`](2026-09-20_the-l0-ingredient-matters-backward-only.md),
which was written on one model from a partially written phase. That entry stands unaltered per the
§6 protocol; this one corrects it.

**Data:** `results/cells/mergeablate_{generic,inverse}/` on CodeLlama-7B, CodeLlama-13B,
Llama-3.1-8B and Granite-3.1-8B. 92 forward and 64 backward cells per model, all present.
Paired by program, program-clustered bootstrap, 2,000 resamples, seed 17.

## Two corrections to the earlier entry

**1. Its CodeLlama-13B backward figure came from an incomplete read.** The entry reports 46 inverse
cells and `no-L0 − 6-way = −2.01 [−2.6, −1.5]`. The phase holds 64 cells (4 arms × 16 conditions);
the complete read gives **−3.47 [−5.0, −2.1]**. Sign and significance survive, the magnitude does
not. This is the second time this phase has been read mid-write, and the reason
`76_merge_ablation.py` now masks the rows of any model whose eval is still in the queue rather than
refusing globally — the all-or-nothing refusal is what made `--force` attractive enough to misuse.

**2. Its headline does not replicate.** "The clean-code specialist contributes two points of
backward accuracy" holds on three of four models and is null on the fourth.

| model | `no-L0 − 6-way`, backward, on `L0` |
|---|---|
| CodeLlama-7B | −0.06 [−1.0, +0.8] |
| CodeLlama-13B | −3.47 [−5.0, −2.1] \* |
| Llama-3.1-8B | −1.38 [−2.5, −0.3] \* |
| Granite-3.1-8B | −1.80 [−3.0, −0.6] \* |

## Forward: the ingredients do not matter, on any model

Percent of the untuned model's clean-code accuracy, `L0` row, all cells present:

| model | base | struct | ident | no-L0 | 6-way |
|---|---|---|---|---|---|
| CodeLlama-7B | 100 | 166 | 166 | 164 | 166 |
| CodeLlama-13B | 100 | 191 | 188 | 190 | 189 |
| Llama-3.1-8B | 100 | 175 | 180 | 180 | 178 |
| Granite-3.1-8B | 100 | 149 | 147 | 153 | 152 |

Every `no-L0 − 6-way` and every `struct − no-L0` interval contains zero, on all four models. Two
specialists from a single semantic view reach the same place as six. **Removing the clean-code
specialist removes nothing forward**, and the gain is not a function of how many adapters are
merged or how many views they cover.

`75_specialist_geometry.py` says why, on the two models computed so far: `L0`'s mean cosine to the
five obfuscation specialists (0.699 CodeLlama-7B, 0.475 Llama-3.1-8B) matches the within-family
pairs (0.714, 0.493). The clean-code specialist occupies no direction the others do not span.

## Backward: breadth matters, and it is a larger effect than L0

| model | `struct − no-L0` | `no-L0 − 6-way` |
|---|---|---|
| CodeLlama-7B | −4.19 [−6.0, −2.3] \* | −0.06 |
| CodeLlama-13B | format-gated | −3.47 \* |
| Llama-3.1-8B | −8.98 [−10.9, −7.1] \* | −1.38 \* |
| Granite-3.1-8B | −6.52 [−8.6, −4.6] \* | −1.80 \* |

Cutting from five specialists to two costs 4–9 points backward on every model where the narrow arm
is readable — three to six times the cost of dropping `L0` alone. On Llama-3.1-8B and Granite the
ordering is monotone in breadth (76 / 90 / 97 / 101 and 76 / 76 / 99 / 105 for struct / ident /
no-L0 / 6-way against base's 100).

**This is not a formatting artefact, and that had to be checked**, because on CodeLlama the narrow
merge collapses the answer contract:

| model | base | struct | ident | no-L0 | 6-way |
|---|---|---|---|---|---|
| CodeLlama-7B | 0.06 | **0.33** (12/16 gated) | 0.08 | 0.05 | 0.04 |
| CodeLlama-13B | 0.02 | **0.72** (16/16 gated) | 0.22 | 0.13 | 0.06 |
| Llama-3.1-8B | 0.07 | 0.10 (0 gated) | 0.05 | 0.05 | 0.05 |
| Granite-3.1-8B | 0.21 | 0.16 (1 gated) | 0.19 | 0.04 | 0.04 |

On Llama-3.1-8B the structure-only merge has a format-failure rate of 0.10 with nothing gated out,
and still loses 8.98 points. So the breadth effect is a genuine accuracy effect that *additionally*
manifests as format collapse on the CodeLlama family. Reporting only the means would have hidden
it: all 16 cells exist on every model, and the blanks in the backward table are gates, not gaps.

## What this does to the paper

* **RQ1 keeps its claim in full.** Clean-code recovery does not need the clean-code specialist, on
  four of four models, and the geometry gives the mechanism.
* **RQ3's backward claim needs one qualifier, but not the one the earlier entry proposed.** The
  right statement is not "backward robustness is a property of the six-way merge" — it is that
  backward robustness needs **breadth of semantic view**, which the six-way merge has and a
  two-specialist merge does not. The marginal contribution of `L0` on top of the five obfuscation
  specialists is real on three of four models but small (0.9–3.5 points) next to the breadth effect.
* **The forward/backward asymmetry is itself a result.** Forward is saturated: any ingredient set
  gets there. Backward discriminates sharply. The untrained direction is where the merge's
  composition actually shows.

## Open

Four models, not eight — the ablation adapters exist only for these. The claim is stated at that
scope. Nothing here reads H1.
