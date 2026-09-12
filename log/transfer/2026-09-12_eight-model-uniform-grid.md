### Target Date: 2026-09-12 (the eight-model uniform grid: R1 6/8 with ZERO refutations, R2 6/8, R3 5/8 — and every one of the failures is outside the lineage the findings were discovered on)
- **What this is.** All eight panel models read from **one phase** (`panel_core`), one config, five
  arms × seven conditions, program-clustered bootstrap (2,000 resamples, seed 17). The four
  incumbents' `tuned_X1` arms were retrained overnight for exactly this: so the table is one
  measurement rather than three campaigns stitched together. No H1.
- **The measurement is validated before the table is read.** `scripts/analysis/55_grid_agreement.py`
  recomputes each incumbent's published R1–R3 through the new grid. **4 of 4 agree, every published
  value inside the new interval, largest disagreement 0.85 pts.** So a departure below is a property
  of the model, not of the config.
- **The tally:**

  | model | lineage | R1 `mono_all−tuned_L0` @X1 | R2 `cons_lam3−mono_all` @X1 | R3 `cons_lam3−tuned_L0` @L0 |
  |---|---|---:|---:|---:|
  | codellama-7b | Meta | **−3.71** [−5.93, −1.56] | **+5.44** [+3.37, +7.41] | −0.54 [−1.98, +1.08] |
  | codellama-13b | Meta | **−4.04** [−6.26, −1.89] | **+3.87** [+2.06, +5.77] | −0.72 [−2.28, +0.90] |
  | codellama-34b | Meta | **−2.72** [−5.02, −0.49] | **+3.62** [+1.40, +5.76] | +0.48 [−0.84, +1.80] |
  | llama31-8b | Meta | **−2.72** [−4.70, −0.91] | **+3.38** [+1.57, +5.36] | −0.30 [−1.98, +1.26] |
  | starcoder2-15b | BigCode | **−2.72** [−4.94, −0.58] | **+2.31** [+0.58, +4.03] | −0.96 [−2.51, +0.60] |
  | gemma3-12b | Google | **−4.70** [−6.93, −2.55] | **+2.64** [+0.91, +4.53] | **−1.80** [−3.53, −0.06] REF |
  | codegemma-7b | Google | −1.98 [−3.95, +0.16] | −0.41 [−2.39, +1.49] | **−2.04** [−3.77, −0.18] REF |
  | granite31-8b | IBM | −0.91 [−2.97, +1.15] | **−1.89** [−3.54, −0.25] REF | **−3.41** [−5.39, −1.26] REF |
  | **tally** | | **6 REPL / 2 inc / 0 REF** | **6 REPL / 1 inc / 1 REF** | **5 REPL / 0 inc / 3 REF** |

- **R1 is the paper's most robust claim and should be stated as such.** Breadth pays a tax on the
  unseen family on **every model in the panel** — six significantly, two with the right sign and an
  interval spanning zero, and **not one contradiction**. Across three lineages and 7B–34B.
- **R2 survives but is conditional.** Anchoring removes the tax on 6 of 8. It is *reversed* on
  Granite, where the anchored arm is worse than breadth on the unseen family, and absent on
  CodeGemma.
- **R3 is the casualty and the paper's claim must become conditional.** Clean-code protection holds
  on 5 of 8 and fails on three. It was discovered on four Meta-lineage models and it holds on all
  four of them.
- **The pattern nobody planned for: every failure is outside the lineage the findings came from.**

  | | Meta lineage (4) | other lineages (4) |
  |---|---|---|
  | R1 | 4 replicate / 0 inconclusive | 2 / 2 |
  | R2 | 4 / 0 | 2 / 1 / **1 refuted** |
  | R3 | 4 / 0 | 1 / 0 / **3 refuted** |

  All three findings replicate **4 of 4 within the lineage they were discovered on** and degrade
  outside it, R3 most.
- **And it is NOT established, which is the part that must survive into the paper.** Fisher's exact
  on the R3 split (Meta 4/4 vs other 1/4) is **p = 0.0714** one-sided — the strongest of the three,
  and not significant. R1 and R2 give p = 0.2143. With **eight models** a 4-versus-4 split cannot
  carry a claim about lineages. Worse, "non-Meta" is not one thing: it is BigCode (1), Google (2)
  and IBM (1), and **both Google models refute R3**, so a Google-family effect and a
  lineage-in-general effect are perfectly confounded here. The honest statement is: *the findings
  replicate uniformly on the lineage they were found on and unevenly off it; with n = 8 the pattern
  is a warning about single-lineage evaluation, not a result about lineages.*
- **StarCoder2 is the counter-example that keeps the story honest.** It is the only non-Meta model
  to replicate all three, it is the panel's strongest model, and it is the one the untuned gate
  scored **0.0000** and rejected (`docs/MODEL_AND_DATA_SELECTION.md` §5b). Had that screening rule
  stood, the panel would have lost the single strongest piece of evidence that the findings are not
  a Meta-lineage artefact — and the lineage pattern above would have looked *cleaner* and been
  *more wrong*.
- **What may now be said, and what may not.**
  - SAY: breadth's unseen-family tax replicates across three lineages with no contradiction (R1).
  - SAY: anchoring removes it on six of eight, with one reversal, named.
  - **DO NOT SAY** clean-code protection is a property of the objective. It is model-dependent:
    5 of 8, and 1 of 4 outside the lineage of discovery.
  - **DO NOT SAY** anything causal about lineage. n = 8, p = 0.07 at best, Google/non-Meta confounded.
- **Next Steps:** RQ3's section in `PAPER_DRAFT.md` was held back pending this table and can now be
  written — conditional, with the tally in the text. The F2 divergence ladder is CodeLlama-7b only
  and StarCoder2 is the natural second model for it, being the one non-Meta model that replicates
  everything.
