# 2026-09-20 — The specialists occupy overlapping directions, not orthogonal ones

**Thread:** modularity · **Data:** `results/analysis/pipeline/specialist_geometry_codellama-7b.json`
· 6 specialists, 224 shared target modules, cosine computed in factored form, TIES-trim overlap and
sign agreement at density 0.5 on every 16th module.

## Why this was run

RQ1 argues that merging composes a general program-reasoning capability rather than a union of
transform-specific ones. The evidence in the paper is *where the advantage appears* — the merge is
not best on the transforms its specialists were built from, and is strongest where the surface is
unfamiliar. That is an inference from accuracy. This measures the weights directly.

## CodeLlama-7B

| pair kind | n | mean cosine | mean trim overlap | mean sign agreement |
|---|---|---|---|---|
| within family | 4 | **+0.714** | 0.660 | 0.951 |
| across family | 6 | **+0.613** | 0.617 | 0.911 |
| clean (`L0` with each) | 5 | +0.699 | 0.653 | 0.947 |

Every pair, including the least aligned (`L2`–`S1`, +0.550), is strongly positive.

## What it shows

**The specialists are not learning disjoint surfaces.** If each had fitted the surface of its own
transform, their task vectors would be close to orthogonal. They are at cosine +0.55 to +0.76, with
sign agreement between 0.89 and 0.97 on the coordinates TIES retains. Most of what each specialist
learned points in a direction the others also point in. That is the geometric form of the claim RQ1
makes from accuracy, and it is independent evidence for it.

**The family structure is real but weak.** Within-family pairs are more aligned than across-family
ones (+0.714 vs +0.613), and the two identifier pairs `L1r`–`L2` and `L1b`–`L1r` are the most aligned
of all. But the gap is 0.10 on a scale where every pair exceeds 0.55, so family membership modulates
a shared direction rather than defining separate ones.

**It explains why sign election changes little here.** With 0.89–0.97 sign agreement, the disjoint
merge discards few coordinates. The merge is closer to a trimmed average than the TIES description
suggests, which is consistent with plain TIES and DARE-TIES agreeing on seven of eight models.

## What it does not show

High cosine between LoRA updates is not by itself evidence of shared *reasoning*. These adapters
share a base model, a rank, a prompt format, an optimiser and a training distribution that differs
only in the transform applied to the same programs. Some alignment is expected from that alone, and
this measurement cannot separate the two. What it does rule out is the strong form of the opposing
hypothesis: specialists fitting disjoint transform surfaces would not produce cosines of +0.6.

## Llama-3.1-8B (added the same day, second model)

| pair kind | n | mean cosine | mean trim overlap | mean sign agreement |
|---|---|---|---|---|
| within family | 4 | **+0.493** | 0.572 | 0.867 |
| across family | 6 | **+0.385** | 0.546 | 0.802 |
| clean (`L0` with each) | 5 | +0.475 | 0.565 | 0.856 |

**The qualitative pattern replicates exactly.** Same ordering, within > clean > across, and the same
within-minus-across gap: 0.11 here against 0.10 on CodeLlama-7B. Every pair is again strongly
positive, the least aligned being `L2`–`S1` at +0.351.

**The magnitude does not.** CodeLlama-7B's specialists are far more aligned than Llama-3.1-8B's:
+0.714 against +0.493 within family, and sign agreement 0.951 against 0.867. So "the specialists
share directions" is a property of both models, but how much they share is model-specific and should
not be quoted as a single number.

Lower sign agreement means TIES's disjoint merge discards more coordinates on Llama-3.1-8B than on
CodeLlama-7B --- roughly 13 % of retained coordinates against 5 %. That is the model where pooled
training loses most in the backward direction (−6.17 points at seed 17, −10.73 at seed 42), and where
the merge's advantage over pooled training on the unseen family is largest (−2.96). We note the
co-occurrence and do not claim a mechanism from two models.
