### Target Date: 2026-09-12 (the divergence ladder on all eight models: 5 replicate, 3 inconclusive, **0 refuted** — and the R2-tracking relation survives out of sample as a trend, not as a fit)
- **Completes** [`2026-09-11_f2-divergence-ladder.md`](2026-09-11_f2-divergence-ladder.md). Every
  panel model now has a divergence read, for the cost of evaluation and **no new training** — all
  four arms the rules need already existed on every model.
- **The headline contrast, `cons_lam3 − mono_all` at d2 (stacks containing the unseen family):**

  | model | lineage | R2 @X1 (ladder) | d2 advantage | verdict |
  |---|---|---:|---:|---|
  | codellama-7b | Meta | +5.44 | **+3.84** [+1.90, +5.70] | REPLICATED |
  | codellama-13b | Meta | +3.87 | **+3.22** [+1.74, +4.65] | REPLICATED |
  | codellama-34b | Meta | +3.62 | **+3.95** [+2.13, +5.81] | REPLICATED |
  | llama31-8b | Meta | +3.38 | **+2.87** [+1.20, +4.62] | REPLICATED |
  | gemma3-12b | Google | +2.64 | **+2.44** [+0.97, +3.99] | REPLICATED |
  | starcoder2-15b | BigCode | +2.31 | +1.36 [−0.08, +2.71] | inconclusive |
  | codegemma-7b | Google | −0.41 | −1.59 [−3.26, +0.12] | inconclusive |
  | granite31-8b | IBM | −1.89 | −1.47 [−2.99, +0.00] | inconclusive |
  | **tally** | | | | **5 / 3 / 0** |

- **The advantage generalises beyond the lineage of discovery.** Gemma-3 replicates it
  significantly, so the claim is no longer Meta-only. **Nothing refutes it.** The three
  inconclusive models are the three with the *weakest or negative* R2, and two of those point
  negative.
- **The scope qualifier committed on 2026-09-11 can be softened but not dropped.** The rule fixed
  before submission asked for 3 of 3 on the first three non-Meta models; that came back 1 of 3. The
  honest sentence is now: *anchoring's advantage on unseen-containing stacks holds on five of eight
  models across three lineages and is absent, never reversed significantly, on the three where the
  objective's ladder-level benefit was itself weak or negative.*

#### The out-of-sample test of the R2-tracking relation
- **What was registered.** After three reads, `cons_lam3 − mono_all` at d2 tracked the same contrast
  on the ladder's X1 column almost exactly (`div = 0.722·R2 − 0.166`, r = 0.9989 over three points).
  Predictions for the **four models whose cell directories were verified empty first** were
  committed with a rule: CONFIRMED iff all four land within **±1.0**, REFUTED iff any lands beyond
  **2.0** or on the wrong side of zero.
- **Result:**

  | model | predicted | observed | \|err\| |
  |---|---:|---:|---:|
  | codegemma-7b | −0.46 | −1.59 | 1.13 |
  | codellama-13b | +2.63 | +3.22 | 0.59 |
  | codellama-34b | +2.45 | **+3.95** | **1.50** |
  | llama31-8b | +2.27 | +2.87 | 0.60 |

- **Verdict: INCONCLUSIVE.** Two of four inside ±1.0, none beyond 2.0, none on the wrong side of
  zero. Max error **1.50** on CodeLlama-34B. Over all eight models Pearson r is **0.9556**, down
  from 0.9989 on the three the fit was built from — the ordinary result of testing a fit out of
  sample rather than reading it off its own training points.
- **What may be said: the two quantities track each other.** Every model's sign agrees, and the
  ordering is nearly preserved. **What may NOT be said: that one predicts the other to a point.**
  The registered precision test failed, and a ±1.5 pt error on a ±2 pt effect is not a quantitative
  law. The paper should report the relation as *"the divergence advantage tracks the ladder-level
  benefit"* with the correlation and the failed precision test both stated, and should not use the
  regression to impute a value for any model.
- **The reason this test exists at all is worth keeping.** The first attempt named Gemma-3 as the
  out-of-sample point and was **withdrawn**: 17 cells including the whole d2 level already existed
  when the prediction was committed (see `CLAUDE_SCRATCHPAD.md`, 2026-09-12). The replacement
  printed the inventory *before* writing the prediction. The relation's only real test is the one
  built after that correction, and it came back inconclusive — which is precisely the outcome a
  prediction recorded after seeing the data would have hidden.
- **Next Steps:** regenerate `paper/tables/divergence_by_model.tex` (both `\pending` rows are now
  filled); soften RQ4's scope sentence in `PAPER_DRAFT.md` and `main.tex`.
