### Target Date: 2026-09-12 (the stack dissociation extends to 6 of 6 models across four lineages — including the model that refuted the anchoring result)
- **Extends** [`2026-09-12_stack-dissociation-within-model.md`](2026-09-12_stack-dissociation-within-model.md),
  whose Next Steps said to re-run as the remaining seen-composite grids landed. Two have. Same
  script, same rule, same 319-program paired set.
- **Results:**

  | model | lineage | seen stacks | unseen-containing | **difference** |
  |---|---|---:|---:|---:|
  | codellama-7b | Meta | **+3.36** [+1.57, +5.27] | **−1.92** [−3.70, −0.14] | **+5.28** [+3.20, +7.54] |
  | codellama-34b | Meta | **+2.27** [+0.44, +4.09] | −0.77 [−2.62, +1.12] | **+3.03** [+0.78, +5.28] |
  | llama31-8b | Meta | **+2.30** [+0.47, +4.15] | −1.05 [−2.72, +0.63] | **+3.35** [+1.50, +5.30] |
  | starcoder2-15b | BigCode | +1.50 [−0.02, +3.00] | −1.19 [−2.93, +0.49] | **+2.68** [+0.77, +4.65] |
  | gemma3-12b | Google | **+2.63** [+0.56, +4.64] | **−2.09** [−3.81, −0.42] | **+4.72** [+2.62, +6.85] |
  | granite31-8b | IBM | **+3.66** [+1.54, +5.68] | −0.24 [−2.02, +1.57] | **+3.91** [+1.41, +6.32] |
  | **tally** | | | | **6 of 6 significant** |

- **The headline: RQ1's dissociation is MORE ROBUST than RQ3's anchoring result, and the panel now
  separates them cleanly.** Granite is the model that **refuted R2** on the ladder (−1.89) and whose
  anchoring advantage on unseen-containing stacks is **negative** (−1.47). Its dissociation is
  nonetheless **+3.91, significant**. So *"breadth composes on what it saw and not on what it did
  not"* survives on a model where *"anchoring repairs that"* does not.
- **This is the sharpest thing the eight-model panel has produced.** Two claims that were reported
  together now come apart: one is 6 of 6 across four lineages, the other is 5 of 8 with a reversal.
  The paper should lead with the first and condition the second, which is what
  `paper/main.tex` §RQ1 and §RQ3 now do.
- **What may NOT be said, unchanged from the first entry:** that breadth is significantly *harmed*
  by an unseen component. Four of six unseen-side intervals include zero. The measured quantity is
  the **difference**, which is why it is computed as one.
- **Coverage:** 6 of 8. `codellama-13b` and `codegemma-7b` still need their seen-composite grids
  (queued); the script skips an incomplete grid rather than reading a partial one.
