# 2026-09-13 — StarCoder2 has no untuned backward baseline, so it has no backward contrast

**Thread:** modularity · **Status:** analysis hardened; StarCoder2 reported in absolute terms only · **Related:** [`2026-09-13_merge-backward-reverses-on-granite.md`](2026-09-13_merge-backward-reverses-on-granite.md)

`ev_invmerge_starcoder2-15b` produced clean merge cells — format-failure 0.03–0.18, accuracies 0.288
to 0.452 — and the analysis crashed. The cause is the row it was dividing by: **every backward `base`
cell on StarCoder2 is format-failure 1.00, accuracy 0.000.** The untuned model emits nothing parseable
when asked the task backwards.

So on this model `merge − base` is not a small number or a noisy one; it is undefined. The apparent
"+45 points over the untuned model" a naive read would produce is the prompt-contract failure the
project already records as a measurement artefact (CLAUDE.md §4 item 6, and the 2026-09-13 finding that
screening base models by untuned format failure is unsound), not a capability difference. The direction
ratio, which puts the forward gain over base in the denominator, is equally undefined.

**Fix.** `62_merge_backward.py` now detects a fully gated baseline, writes
`no_untuned_reference` into the result with the merge arms' **absolute** backward accuracies, and
computes no contrast and no ratio. It no longer crashes, and more importantly it no longer *could*
produce a contrast against a zero that means "did not answer in the required format".

**Where this leaves the backward-merge question.** Three models read, three different situations:

| model | status |
|---|---|
| CodeLlama-7B | full contrast: merge **+3.21** backwards, DR **+0.17** |
| Granite-3.1-8B | merge **−7.66**, DR **−0.68**; 25 cells gated, so no tuned control |
| StarCoder2-15B | **no baseline at all**; absolute accuracies only (0.29–0.45) |

Llama-3.1-8B is queued. The backward-merge finding is one model deep with a contradiction on the
second and no reference on the third, and the paper must not carry it as anything more than that.
