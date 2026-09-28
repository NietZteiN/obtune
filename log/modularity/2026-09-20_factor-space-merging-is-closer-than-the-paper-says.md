# 2026-09-20 — Factor-space and update-space merging agree at cosine 0.75 on real adapters, not 0.40

**Thread:** modularity · **Data:** `results/analysis/pipeline/merge_space_*.json`, seven models.
Script `scripts/analysis/79_merge_space_check.py`. CPU only, from adapters already on disk.

## The question

`sections/merging.tex` §\ref{sec:factorspace} argues that PEFT applies TIES/DARE-TIES to the LoRA
factors $A$ and $B$ separately, not to the assembled update $\Delta = sBA$, and that the two are not
equivalent. The argument is structural and correct: each entry of $\Delta$ is a sum over the rank, so
an entry of $B$ participates in a whole row of the update and a sign elected on a factor coordinate
is not a statement about a parameter of the update.

The section then quantifies the gap as **cosine 0.40, 39 % sign disagreement**. That number is
computed on **random factors**, which are close to orthogonal. The specialists here are not — they
sit at cosine 0.35–0.75 (`75_specialist_geometry`). So the cited figure may not describe the adapters
the paper actually deploys.

## The measurement

Compare the **merged adapter already on disk** (built by PEFT's `add_weighted_adapter`, i.e. factor
space — the artefact every result in this paper is evaluated on) against
`peft.utils.merge_utils`' **same `ties` / `dare_ties` primitive applied to the materialised
updates**. Nothing is reimplemented, so the only variable is what the operator acts on. Every 16th
module; a 7B module is ~180 MB materialised.

TIES is reported beside DARE-TIES because DARE draws a Bernoulli mask, so one DARE-TIES comparison
confounds the structural question with a single random draw. TIES is deterministic; DARE-TIES is
averaged over three seeds.

| model | TIES cos | TIES sign | DARE-TIES cos | DARE-TIES sign |
|---|---|---|---|---|
| CodeLlama-13B | 0.848 | 0.890 | 0.852 | 0.844 |
| StarCoder2-15B | 0.841 | 0.889 | 0.843 | 0.845 |
| CodeLlama-7B | 0.841 | 0.884 | 0.841 | 0.839 |
| CodeGemma-7B | 0.754 | 0.832 | 0.736 | 0.789 |
| Llama-3.1-8B | 0.725 | 0.817 | 0.702 | 0.776 |
| Granite-3.1-8B | 0.679 | 0.810 | 0.649 | 0.765 |
| Gemma-3-12B | 0.539 | 0.801 | 0.508 | 0.756 |

**TIES cosine 0.539–0.848 (mean 0.747); sign agreement 0.801–0.890 (mean 0.846).**

Against the section's random-factor figures of 0.40 and 0.61, the real gap is smaller by roughly a
factor of two in cosine.

## What changes and what does not

* **The structural argument stands unchanged.** Factor-space and update-space merging are different
  operations, for the reason given, and the choice to merge in factor space (it preserves rank; the
  alternative needs a truncated SVD that changes the rank *before* the merge rule is evaluated) is
  unaffected.
* **The magnitude is overstated.** As written, the section reads as though factor-space merging
  computes something largely unrelated to what the published algorithm computes. On mutually aligned
  specialists it does not: 0.75 cosine and 85 % sign agreement.
* The ordering is informative. The models whose specialists are most aligned (CodeLlama-13B,
  StarCoder2-15B, both ~0.74–0.75 within-family) are the models where the two merge spaces agree
  most (0.85); Gemma-3-12B, the least aligned at 0.349, is where they agree least (0.54). The gap is
  a function of specialist alignment, which is exactly why the random-factor figure is a worst case.

## A bug this found

Gemma-3-12B first reported `sign agreement nan` off 27 good samples. A sampled module whose
update-space merge is **entirely zero** — every coordinate lost the sign election — shares no
non-zero coordinate with the factor-space merge and carries no sign information; averaging that one
NaN destroyed the model's whole figure. Degenerate modules are now excluded and counted.

Gemma-3-12B has **6 of 27** such modules under TIES and 18 of 81 under DARE-TIES. That is a real
property of its specialists: they disagree in sign often enough that update-space TIES annihilates
whole modules. No other model in the panel showed one.

## Open

CodeLlama-34B is running and is the only model missing. `merging.tex` is **not yet amended**; the
range should be stated over the full panel.
