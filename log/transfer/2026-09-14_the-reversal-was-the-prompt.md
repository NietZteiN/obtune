# 2026-09-14 — Granite's backward reversal was the missing demo, and my account of which way the bias ran was wrong

**Thread:** transfer · **Status:** 6 of 7 models repaired, three re-read · **Corrects:** [`2026-09-14_two-prompts-one-phase.md`](2026-09-14_two-prompts-one-phase.md) (direction of the bias) and §6.5d of `docs/RQ_SUMMARY.md` (the reversal itself) · **Script:** `62_merge_backward.py` on phase `inverse_1shot`

## What I got wrong this morning

When I found that the backward ladder held two prompts, I wrote that "its format-gate exclusions and
**part of its merge advantage** are a prompt difference rather than a method difference" — i.e. that
the merges were flattered. I asserted that without measuring it. It is the wrong way round.

`68_prompt_effect.py`, six models, same adapters, same items, ladder conditions, common program set
(n = 317). The one-shot demo's effect on the **untuned model**:

| model | zero-shot | one-shot | delta |
|---|---|---|---|
| CodeLlama-13B | 0.361 | 0.279 | **−8.28** \* |
| CodeLlama-34B | 0.379 | 0.310 | **−6.93** \* |
| Granite-3.1-8B | 0.349 | 0.256 | **−9.37** \* |
| Llama-3.1-8B | 0.338 | 0.347 | +0.83 |
| Gemma-3-12B | 0.388 | 0.387 | −0.05 |
| CodeGemma-7B | 0.227 | 0.229 | +0.20 |

**The demo never helps the untuned model** and costs it 7–9 points on half the panel. Meanwhile it
helps the anchored arm on all six (+8.67 to +15.02) and lifts the format gate on eight of the
twenty-four tuned cells. So the zero-shot ladder systematically **flattered `base` and crippled the
tuned arms**, and a one-shot merge contrasted against a zero-shot `base` was measured against an
inflated reference. The bias ran *against* the merge, never for it.

## The consequence, re-read on repaired cells

`merge_dare_ties − base`, backward, pooled over the ladder:

| model | published (mixed prompts) | **re-read (one-shot both sides)** |
|---|---|---|
| Granite-3.1-8B | **−7.66** [−10.08, −5.17] \* | **−0.27** [−2.33, +1.83] — null |
| Llama-3.1-8B | +2.91 [+0.80, +5.11] \* | +2.00 [+0.36, +3.79] \* |
| CodeLlama-7B | +3.21 [+1.52, +4.85] \* | unchanged (always one-shot) |

**Granite's reversal does not exist.** It was −7.66 against a baseline inflated by +9.37, and on a
fair comparison it is a null. Its `merge_ties` is **+6.94** [+5.29, +8.64], the largest backward gain
by any arm on any model.

And the separation on Llama-3.1-8B is now clean in a way it was not: both merges are significantly
positive (+2.00, +2.42) while **every single-adapter arm is significantly negative** (`tuned_L0`
−5.35, `mono_all` −7.74, `cons_lam3` −6.05, `tuned_X1` −2.78).

## What this retires

§6.5d's sentence "**Merging is therefore *not* backward-safe; the cost is model-dependent and large
in either direction**" was built on one number and that number was an artefact. Across the three
models re-read so far the merges are positive or null in all six arm×model cells and negative in
none, while the single-adapter arms are negative wherever they are readable. That is consistent with
the stack-based reads, which never had the confound
([`2026-09-14_merge-reads-backward-better-than-base.md`](2026-09-14_merge-reads-backward-better-than-base.md)).

## The lesson, stated plainly

I found a confound and, in the same hour, published a sentence about which direction it biased
results — from intuition, with the measurement one script away. The measurement took twenty minutes
and reversed the sign. **Finding a confound is not the same as knowing its direction, and the gap
between them is exactly where a plausible story does the most damage.** The entry that got it wrong
is left unamended above this one.

StarCoder2 is the last model outstanding; its untuned backward cells are gated in both readings, so
it will not change this.
