# 2026-09-13 — Merging on the panel: DARE-TIES does not pay breadth's unseen tax

**Thread:** modularity · **Status:** read against the pre-registered rules on three models; StarCoder2 pending · **Related:** [`2026-09-13_f1-routing-and-merging-on-stacks.md`](2026-09-13_f1-routing-and-merging-on-stacks.md), [`../transfer/2026-09-12_stack-dissociation.md`](../transfer/2026-09-12_stack-dissociation.md)

## Provenance

`configs/eval/merge_panel.yaml` (phase `merge_panel`): untuned + TIES / DARE-TIES / DARE-linear + five
specialists on the ladder, X1, six seen stacks, four X1-containing stacks. Llama-3.1-8B 393040 (27 min,
153 cells), Granite 393039 (35 min, 153 cells); the untuned cells reproduce `panel_core`'s to the third
decimal on the same item counts, so the grid is the same. CodeLlama-7B's merges come from
`rq2_generic` / `composite_generic` / `f2_divergence` (no single-X1 merge cell; that level is skipped).
Analysis `scripts/analysis/60_merge_panel.py` → `results/analysis/pipeline/merge_panel_<model>.json`;
every level on the programs common to its cells (417 seen, 319 unseen), clustered bootstrap 2,000 / 17.
DARE-linear exceeds the 0.25 format gate on several cells on both new models and is never the best merge;
TIES is below the control everywhere. Everything below is DARE-TIES.

## Numbers (points, paired)

| model | stacks | merge − clean | merge − breadth | merge − anchored | breadth − clean | anchored − clean |
|---|---|---|---|---|---|---|
| CodeLlama-7B | seen (6) | **+0.83 [+0.01, +1.63]** | **−2.80 [−4.43, −1.19]** | **−4.01 [−5.29, −2.70]** | **+3.63** | **+4.84** |
| CodeLlama-7B | unseen-containing (4) | +0.86 [−0.05, +1.78] | **+2.35 [+0.63, +3.97]** | **−1.39 [−2.72, −0.05]** | −1.49 | **+2.25** |
| Granite-3.1-8B | seen (6) | **+1.57 [+0.76, +2.46]** | **−3.23 [−4.92, −1.52]** | **−2.32 [−4.01, −0.61]** | **+4.80** | **+3.89** |
| Granite-3.1-8B | unseen-containing (4) | **+2.09 [+1.10, +3.09]** | **+2.20 [+0.50, +3.84]** | **+2.98 [+1.28, +4.65]** | −0.10 | −0.89 |
| Llama-3.1-8B | seen (6) | **+2.31 [+1.27, +3.38]** | −0.85 [−2.41, +0.72] | **−2.80 [−4.26, −1.35]** | **+3.16** | **+5.11** |
| Llama-3.1-8B | unseen-containing (4) | **+2.56 [+1.49, +3.61]** | **+3.09 [+1.54, +4.60]** | +0.81 [−0.47, +2.12] | −0.52 | **+1.75** |

## Verdicts by the registered rules

- **H-merge-panel-a** ("merging does not beat the clean control on seen stacks", CONFIRMED iff ci_hi ≤ +1):
  CodeLlama-7B INCONCLUSIVE, Granite INCONCLUSIVE, **Llama-3.1-8B REFUTED** (ci_lo +1.27 > +1). My
  prediction was CONFIRMED on all three. It was wrong: DARE-TIES is above the clean control on seen stacks
  on every model, significantly on all three.
- **H-merge-panel-b** ("merging stays below breadth"): CodeLlama-7B CONFIRMED, Granite CONFIRMED,
  Llama-3.1-8B INCONCLUSIVE (equal to breadth).

## What the pattern is

Merging gains **less than breadth or anchoring on seen stacks** (−2.3 to −4.0 against anchoring on all
three) and **keeps its smaller gain on stacks containing the unseen family**, where breadth loses it: on
unseen-containing stacks DARE-TIES is above breadth on **three of three** models (+2.2 to +3.1, all
significant). Against the anchored objective there it is below on CodeLlama-7B (−1.39), equal on Llama
(+0.81 n.s.) and **above on Granite (+2.98)** — Granite being the model on which anchoring's repair
reverses (RQ3 panel table). So the paper's "merging fails both tests" is not what the data say on the
composition test: merging is the baseline that never had the tax, because it never had breadth's
seen-stack gain either. The dissociation result (RQ1, breadth) is untouched; the claim that anchoring is
*the* method without the tax now has a competitor that is cheaper (CPU, no training) and, on one model,
better.

Not measured: merging on the backward task on any model; StarCoder2 (queued, 393029). CodeLlama-7B's
earlier ladder-level merge number (−3.13, "merging costs") was a different contrast on single transforms
and is not contradicted; the stack-level DARE-TIES number on the six seen stacks is +0.83.

## Paper changes made

`rq1_merge_panel` table added to RQ1 with a paragraph stating the above; the abstract's "merging
outright", the intro's "merging performs at or below the clean-code-tuned control", and RQ1's "merging
does not compose at all" are rewritten to the measured statement; Threats notes the backward gap. The
framing question — whether merging is presented as a failed baseline or as the second method without a
tax — is the user's; the text now states the numbers either way.
