# 2026-08-27 — Dead-store elimination helps only where the old pass was blind; the format objection is bounded and small

**Thread:** normalization · **GPU:** 0, 2 (budget 3) · **Seed:** 17 · **Grid A** (`eval_source: heldout`)

## Goal / hypothesis

Two questions left over from [2026-08-26](2026-08-26_symbolic-and-learned-routes-are-one-skill.md):

1. **N3/N4** — yesterday showed symbolic DCE is worth +4.74 to a model lacking the skill, so the
   ceiling on a zero-training arm is set by how much the analysis can *prove* dead. `norm_structural`
   proves 0.4 % of `S4` dead. Does a stronger analysis (`norm_inert`, adding dead-store elimination)
   buy real accuracy?
2. **The format objection** — `base` fails the output format on 13-28 % of items and every adapter
   on 2-6 %. How much of `tuned_L0`'s gain is "learned to emit a canonical literal" rather than
   task learning?

## Setup

* `configs/eval/inert_normalize_qwen1.5b.yaml` — `norm_inert` vs `norm_structural_fixed` vs `base`,
  plus `tuned_L0` ± `inert`, on `L0, L1r, S1, S2, S3, S4`. Grid A, n=1247-1670.
* `configs/train/formatonly_qwen1.5b_py.yaml` + `configs/eval/formatonly_qwen1.5b.yaml` — the
  label-shuffled control (`train.shuffle_labels`).
* Statistics: cluster bootstrap by `program_id` (4,000 resamples, seed 17) + exact McNemar.

## Results

### 1. `norm_inert` vs the published pass

| condition | Δ (inert − structural) | 95 % CI | McNemar p |
|---|---|---|---|
| **S4** | **+1.50** | [+0.18, +2.88] | **0.022** |
| S2 | +0.66 | [−0.48, +1.74] | 0.30 |
| S3 | −0.06 | [−0.48, +0.36] | 1.00 |
| L0 | +0.06 | [−0.18, +0.36] | 1.00 |
| L1r | −0.18 | [−0.54, +0.12] | 0.45 |
| S1 | +0.08 | [−0.40, +0.56] | 1.00 |

And what `norm_inert` buys `tuned_L0`: **S2 +2.10** [+0.60, +3.66] p=0.005, **S3 +1.56**
[+0.12, +3.05] p=0.033, S4 +0.60 (ns); controls `L0` +0.00, `L1r` +0.42, `S1` −0.40, all null.

### 2. The format-acquisition bound (Grid A, no new GPU)

| cond | n | `base` | fmt-fail | loose ceiling | `base` \| fmt-ok | `tuned_L0` |
|---|---|---|---|---|---|---|
| L0 | 1670 | 21.7 | 19.0 | 40.7 | 26.8 | 44.7 |
| S2 | 1667 | 15.3 | 13.2 | 28.5 | 17.6 | 41.8 |
| S3 | 1670 | 16.0 | 14.3 | 30.3 | 18.7 | 43.1 |
| S4 | 1667 | 19.3 | 16.7 | 35.9 | 23.1 | 43.2 |
| **H1** | 1214 | **6.4** | **28.3** | **34.8** | **9.0** | **24.5** |

## Observations

**The stronger analysis pays off exactly where the old one was blind, and nowhere else.** `S4` is
the only significant cell (+1.50) — S4 being the condition `norm_structural` could only prove
0.4 % dead. On `S3`, where the old pass already removed everything (32.3 % either way), the
difference is −0.06. All four control conditions are null, which is the evidence that the extra
removals are inert code and not live code: a bad analysis would have *cost* accuracy there.

**But the gain is far smaller than the code removed.** `norm_inert` cuts S2 programs to 58.4 % of
original against `structural`'s 81.3 %, and S4 to 67.9 % against 98.7 % — roughly doubling and
thirty-times-ing the material removed — for +0.66 and +1.50 points. So on `S2` the returns to
better static analysis are already flat: the first pass captured nearly all the accessible benefit
and the remaining inert material was not what was costing the model. That bounds N3 in a useful
direction — the ceiling on the zero-training arm is *not* mainly set by analysis strength.

**The format objection is real but small, and the adapter arm was not what settled it.** Granting
`base` a win on every item it lost to a format failure is a loose ceiling that on `H1` (34.8)
exceeds `tuned_L0` outright — but it is uninformative, because it assumes a 100 % hit rate on
items where `base` hit 9.0 % when it *did* format correctly. The conditional estimate is the
informative one: if format were free, `base` reaches **9.0 %** on `H1` against `tuned_L0`'s
**24.5 %**. Format acquisition therefore accounts for at most **≈2.6** of the **18.1**-point gain,
and ~15.5 points are task capability. Note the conditioning is on a post-treatment variable and
selects the items `base` found easy enough to format, so 9.0 % is if anything *optimistic* — which
pushes the conclusion the safe way.

**One number here deserves its own line: `base`'s format-failure rate on `H1` is 28.3 %,** against
13-19 % on every trainable condition. The held-out obfuscator breaks the base model's ability to
follow an output format roughly twice as often as anything it was trained on. That is a separate
phenomenon from accuracy and it is not currently reported anywhere.

## Errors hit

**The label-shuffled adapter collapsed and the arm is void as designed.** Training was clean and
the manipulation check was textbook — identical 4,689 rows and 222 steps to `tuned_L0`, train loss
0.448 → **1.933**, exactly the plateau expected when the input carries no information about the
target. But at eval it emitted *the same unterminated string on every item*
(`"1000000...`), giving accuracy 0.000 and `format_fail` **0.999** on all three conditions.

The cause is a design fault, not a bug: with labels shuffled, the loss-minimizing policy is the
*marginal* answer distribution, and **greedy decoding reads off the mode of a product of
per-position marginals** — a generic "average answer" that never terminates. The arm was supposed
to measure whether format can be learned without the task; greedy decode turns "learned a
distribution" into "emits one degenerate string", so it cannot. The `format_fail` check written
into the eval config is what caught this, and it was written in precisely because 0.0 accuracy
alone would have been ambiguous between "clean floor" and "degenerate adapter".

Superseded rather than repaired: the conditional-accuracy bound above answers the same question
more directly, on data already on disk, with no adapter and no GPU. The adapter could be salvaged
by scoring it under sampling instead of greedy, but it would then be decoded differently from
every arm it is meant to be compared against, which costs more in comparability than it buys.

## Next steps

* `norm_inert` has **not** earned an `H1` read on its own: +1.50 on one condition, and the S2
  result says returns to analysis strength are flat. It belongs in the batched confirmatory pass
  if anything, not ahead of it.
* Report `base`'s `H1` format-failure rate (28.3 %) as a finding in its own right.
* Attention steering (masking the same spans instead of deleting them) is the remaining live arm
  from this line — it separates "the tokens are gone" from "attention is not spent on them", which
  every deletion result so far confounds.
