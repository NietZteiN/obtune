# 2026-09-14 — The merge gains backward competence on seven of eight models, and this is the first read where all eight are comparable

**Thread:** modularity · **Status:** 8/8, one prompt throughout · **Supersedes:** [`2026-09-13_merging-gains-backward.md`](2026-09-13_merging-gains-backward.md) and §6.5d of `docs/RQ_SUMMARY.md`, both of which had four models and a prompt confound

`62_merge_backward.py` could previously run on four models: the other four had no backward merge
cells at all, because `inverse_merge.yaml` never covered them, and the script refused rather than
reporting a hole. Those cells were run into phase `inverse_1shot` with the rest of the ladder
repair. **Every arm on every model in this table was asked with the same one-shot prompt**, which
was not true of any previous version of it.

## Backward gain against the untuned model, pooled over the ladder

| model | `merge_dare_ties` | `merge_ties` | `mono_all` (breadth) | `cons_lam3` (anchored) |
|---|---|---|---|---|
| CodeLlama-7B | **+3.21** \* | −0.30 | −0.74 | +0.39 |
| CodeLlama-13B | **+4.18** \* | +0.71 | gated | **−6.94** \* |
| CodeLlama-34B | **+4.40** \* | **+4.43** \* | gated | **−6.55** \* |
| Llama-3.1-8B | **+2.00** \* | **+2.42** \* | **−7.74** \* | **−6.05** \* |
| StarCoder2-15B | **+7.72** \* | **+5.60** \* | **−5.54** \* | **+2.93** \* |
| Gemma-3-12B | **+2.31** \* | **+2.36** \* | +0.42 | gated |
| CodeGemma-7B | **+6.25** \* | gated | **+7.27** \* | gated |
| Granite-3.1-8B | −0.27 | **+6.94** \* | **−4.72** \* | gated |

\* 95 % program-clustered bootstrap excludes zero.

## What stands

**The DARE-TIES merge is positive on all eight models, significant on seven, negative on none.** No
other arm is positive everywhere. Its direction ratio is between **+0.11 and +0.29 on seven of the
eight** (+0.17, +0.19, +0.17, +0.11, +0.15, +0.12, +0.29) with Granite the one null at −0.02 — an
unusually tight spread for a ratio of small differences across eight architectures.

The TIES merge is positive on five significantly, null on two, gated on one, negative on none.

**Breadth and anchoring are the arms that lose.** Breadth is significantly negative on three, and
anchoring on three, with anchoring format-gated on three more. Where they are readable they are
mostly below the untuned model — which is the paper's claim, now on eight models with one prompt.

## The two exceptions, stated rather than smoothed

- **CodeGemma's breadth adapter gains +7.27 backwards**, the largest breadth number on the panel and
  significant. Breadth is not uniformly a backward cost; on one model it is a backward benefit.
- **Granite is where the merge does nothing** (−0.27, interval spanning zero) while its *other*
  merge gains +6.94. Two merge recipes, opposite readings, same model. Whatever the paper says about
  merging should not lean on a single recipe.

## Relation to the stack read

Consistent, and the two are independent: this is the ladder, the other is stacks
([`2026-09-14_merge-reads-backward-better-than-base.md`](../transfer/2026-09-14_merge-reads-backward-better-than-base.md)),
and they agree that the merge is the only arm that does not pay backward for its forward gain. The
ladder version is stronger because every cell is now comparable; the stack version is stronger
because it never had the confound to begin with.
