### Target Date: 2026-09-11 (F2, the divergence ladder: anchoring BEATS the clean-code control and beats breadth on stacks containing an unseen family — and breadth's own collapse is heterogeneous, not pooled)
- **The experiment RQ4 was to be decided by.** Six new composites, each containing X1 (the unseen
  family) as a component; nine systems; CodeLlama-7b; 287 programs common to all six, **recorded
  before any system ran** (`data/manifests/f2_divergence_common_subset.json`). Rules, the RQ4
  mapping in both directions, and a scope addendum were all committed to `CLAUDE_SCRATCHPAD.md`
  **before the first cell existed**. No H1 anywhere: the unseen component is X1 throughout.
- **The divergence ladder**, `mono_all − tuned_L0` (breadth over the clean-code control):

  | level | stimulus | contains unseen? | breadth's gain |
  |---|---|---|---:|
  | **d0** | six depth-2 composites, all SEEN transforms | no | **+3.49** [+2.04, +5.01] |
  | **d1** | depth-3/4, all SEEN | no | **+4.15** [+2.37, +5.91] |
  | **d2** | `C_L1r_X1`, `C_X1_S1`, `C_S2_X1` | **yes** | **−1.71** [−3.60, +0.31] |
  | **d3** | `C3_L1r_S1_X1` | **yes** | −0.35 [−2.67, +1.86] |

  The sign flips the moment an unseen component enters the stack. The interval at d2 straddles zero.

- **Pre-registered verdicts, as they came out:**

  | hypothesis | rule | d2 | d3 | verdict |
  |---|---|---:|---:|---|
  | H-F2-breadth-monotone | ci_hi < 0 pooled at d2 | −1.71 [−3.60, **+0.31**] | — | **INCONCLUSIVE** |
  | H-F2-cons-no-tax | `cons_lam3 − tuned_L0` ci_hi ≥ 0 | **+2.13 [+0.66, +3.60]** | **+3.26 [+0.81, +5.92]** | **CONFIRMED** |
  | H-F2-cons-vs-breadth | `cons_lam3 − mono_all` ci_lo > 0 at d2 | **+3.84 [+1.90, +5.70]** | **+3.60 [+1.40, +5.81]** | **CONFIRMED** |
  | H-F2-family-stacks | `tuned_X1 − tuned_L0` ci_lo > 0 at d2 | **+5.93 [+4.10, +7.78]** | **+5.70 [+3.14, +8.27]** | **CONFIRMED** |
  | H-F2-merge | `merge_dare_ties − tuned_L0` ci_hi ≤ 0 | +0.70 [−0.39, **+1.78**] | +1.51 [−0.12, +3.26] | **INCONCLUSIVE** |

- **RQ4's mechanical reading, per the mapping fixed in advance: "undecided by F2 — breadth does not
  fall below the clean-code control at d2."** That is the verdict of record, and it is reported
  first because the mapping required *both* anchoring holding *and* breadth dropping, and only one
  of the two is established.
- **What is nonetheless established, and it is more than "no tax".** `cons_lam3` does not merely
  avoid a cost on unseen-containing stacks — it is **significantly above** the clean-code control
  (+2.13 at d2, +3.26 at d3) and **significantly above breadth** (+3.84, +3.60). The Fig-1 pattern
  is half-present: anchoring rises where breadth does not, but breadth's *fall below the control*
  is not established pooled.
- **F9's prediction, recorded before these numbers, is met.**
  [`2026-09-11_f9-anchoring-vs-breadth-on-deep-stacks.md`](../modularity/2026-09-11_f9-anchoring-vs-breadth-on-deep-stacks.md)
  found anchoring only *matches* breadth on SEEN stacks (+0.87 [−0.59, +2.33] pooled) and recorded
  the depth-4 cell's +2.03 as a directional observation, saying in terms: *"If F2's
  `cons_lam3 − mono_all` at d2 is positive, this ordering becomes a second, pre-existing line of
  support. If F2 comes out flat, this cell is noise and should be dropped."* It is **+3.84
  [+1.90, +5.70]**. So the clean statement across both experiments is: **anchoring's advantage over
  breadth appears only once the input diverges from what breadth was trained on** — absent on seen
  stacks, large on unseen-containing ones.
- **POST-HOC, and flagged as such: the d2 pooling hides an opposite-signed split that is not noise.**

  | composite | parts | `mono_all − tuned_L0` |
  |---|---|---:|
  | `C_L1r_X1` | identifier → unseen | **+2.67 [+0.35, +5.11]** |
  | `C_L1r_X1m` | identifier → unseen (MBA half) | +1.28 [−1.16, +3.72] |
  | `C3_L1r_S1_X1` | identifier → structural → unseen | −0.35 [−2.67, +1.86] |
  | `C_S2_X1` | structural → unseen | **−3.60 [−6.40, −0.58]** |
  | `C_S1_X1s` | structural → unseen (string half) | **−3.84 [−6.75, −0.93]** |
  | `C_X1_S1` | unseen → structural | **−4.19 [−7.09, −1.28]** |

  Three cells significantly negative, one significantly positive, ordered by **identifier content**:
  stacks beginning with `L1r` are where breadth still helps, stacks containing a structural
  transform are where it is hurt, and the one containing **both** sits at zero. **Pooling
  opposite-signed significant effects and reporting "inconclusive" is the wrong summary of this
  level**, and the pre-registered rule produced exactly that. Recorded as the honest state: the
  rule as written is answered INCONCLUSIVE, and the data say something sharper that the rule was
  not shaped to capture.
- **This is the F3a mechanism, on new stimulus.**
  [`2026-09-11_f3a-stack-identifier.md`](../modularity/2026-09-11_f3a-stack-identifier.md)
  established on SEEN depth-3 stacks, by direct contrast (+3.39 [+0.82, +6.16]), that breadth's
  stack advantage depends on an identifier transform being present. The d2 ordering is that same
  dependence, now visible on stacks containing an unseen family, and F3a was pre-registered and
  read **before** these cells existed. That makes the post-hoc reading prediction-consistent rather
  than a fishing expedition — but it is still post-hoc, and the pre-registered test of it is a
  difference-of-differences on THESE composites, which has not been run.
- **Scope, per the addendum committed before the read.** This is **CodeLlama-7b alone**, the model
  the anchoring objective was developed on. The panel has just shown R2 to be model-dependent
  (replicated 2 of 4 new models, refuted on Granite). So the licensed sentence is *"on the model
  where the objective was developed, anchoring's advantage survives — and grows — when an unseen
  component enters the stack"*, with the scope qualifier in the sentence and not a footnote.
  Generalising needs the divergence read on a non-Meta-lineage model; StarCoder2 is the candidate
  and its `tuned_X1`/`mono_allX` arms do not exist yet.
- **Truncation, as pre-registered:** exactly **1 over-long prompt dropped per cell, in all 54
  cells** — the same program every time (`apps_1615_0`). Prompt length does not depend on which
  adapter is loaded, so the drop is uniform across systems and every paired comparison is intact.
- **Merging:** `merge_dare_ties − tuned_L0` is +0.70 [−0.39, +1.78] at d2 — indistinguishable from
  the clean-code control. The rule asked for ci_hi ≤ 0 and did not get it, so INCONCLUSIVE; the
  substantive reading is "merging buys nothing here", not "merging is harmful here".
- **Family exposure is the largest single effect anywhere in this table.** `tuned_X1 − tuned_L0`
  +5.93 at d2, and `mono_allX − mono_all` +6.28 — adding the family to breadth rescues breadth
  completely. Consistent with RQ2′: transfer follows the family, and a stack containing it is still
  a stack containing it.
- **Next Steps:** run the difference-of-differences on d2 (identifier-containing vs
  structural-containing) as a *pre-registered* test rather than the post-hoc reading above; and get
  one non-Meta-lineage model onto the divergence ladder before RQ4's sentence generalises.
