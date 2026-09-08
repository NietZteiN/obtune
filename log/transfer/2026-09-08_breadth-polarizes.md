### Target Date: 2026-09-08 (E14 — the `mono_all` log P(gold) anomaly is real, is **not** X1-specific, and turns out to be a polarization effect that predicts the unseen-family tax)
- **Hypotheses / what we're testing:** **REPORTED, not verdicted** (pre-registration #2, `8da96b4`,
  amended before submission to add six extraction runs). `an_attention` refuted both RQ4′ knockout
  hypotheses and left one unplanned number: on X1 the *clean* mean log P(gold) is −11.4 for
  `mono_all` against −6.3 for `tuned_L0` and `cons_lam3`. One number from an instrument that turned
  out inert is not a finding, so this read asks only two things: is it real, and is it specific to
  the unseen family?
- **Setup:** the pre-existing dumps carry all five arms on X1 only, so six more score-mode
  extractions were submitted (`ko_{l0,s2}_{tuned_L0,mono_all,cons_lam3}`, **383174–383179**, ~2 min
  each, same script, same 150-item cap) → `an_logp` **383181**
  (`scripts/analysis/46_logp_anomaly.py`). Per-item pairing on the same 150 items, bootstrap by
  program, with the two artifacts that could manufacture the gap checked explicitly: gold-token count
  (log P is a **sum**, so a longer answer is mechanically more negative) and a heavy tail. No H1.
- **Results — clean mean log P(gold), and it is global:**

  | | L0 | S2 | X1 |
  |---|---:|---:|---:|
  | `tuned_L0` | −4.13 | −4.20 | −6.26 |
  | `cons_lam3` | −4.09 | −4.16 | −6.36 |
  | `mono_all` | **−8.27** | **−8.36** | **−11.42** |
  | `tuned_X1` | — | — | −5.96 |
  | `base` | — | −15.03 | −16.72 |

  `mono_all − tuned_L0`, paired, [95 % CI]: **L0 −4.14** [−5.37, −3.05]*, **S2 −4.16**
  [−5.38, −3.10]*, **X1 −5.15** [−6.77, −3.81]*. Per gold token: −1.02 / −1.05 / −1.24. Not a
  length artifact (gold-token counts are identical across arms by construction, 4.68 / 4.84) and not
  a pure tail (worse on 56 % / 59 % / 74 % of items; the 10 %-trimmed means, −2.99 / −3.11 / −3.97,
  keep most of the effect, though the gap between mean and median does show real right skew).
  `cons_lam3 − tuned_L0` is **+0.04 / +0.04 / −0.09**, every interval spanning zero.
- **The mechanism, which is the part worth keeping.** Splitting each arm's items by whether that arm
  got them right:

  | arm | L0 correct / wrong | S2 correct / wrong | X1 correct / wrong |
  |---|---:|---:|---:|
  | `tuned_L0` | −0.33 / −7.00 | −0.39 / −6.50 | −2.24 / −8.16 |
  | `cons_lam3` | −0.37 / −6.59 | −0.35 / −6.33 | −2.19 / −8.10 |
  | `mono_all` | **−0.16 / −12.95** | **−0.16 / −13.05** | **−2.33 / −14.15** |

  **Breadth training does not degrade the model's probability of the gold answer. It polarizes it.**
  On the items it gets right `mono_all` is *more* confident than the clean-code arm (−0.16 against
  −0.33); on the items it gets wrong it is roughly **twice as far** from the gold (−12.95 against
  −7.00). The whole −4 nat deficit lives in the wrong-answer half. Its within-arm spread between the
  two halves is 12.8 nats on L0 where `tuned_L0`'s is 6.7 and `cons_lam3`'s is 6.2.
- **Why this matters for RQ1′.** It supplies a mechanism for the tax that the inert knockout could
  not: breadth makes the model *more decisive everywhere*, which is free on conditions it has seen —
  L0 and S2 accuracy are unchanged or better — and expensive exactly where its decisions are wrong
  more often. On the unseen family more items sit in the wrong-answer regime, and there breadth is
  not merely wrong but committed, so the gold answer is further out of reach and the margin that
  would have been recoverable is gone. **The unseen-family tax is what breadth's sharpening costs
  when the sharpening is aimed at the wrong answer.** That is a hypothesis this read *supports*, not
  one it establishes: it is correlational, on 150 items, at one seed.
- **And it corroborates E4 independently.** `cons_lam3` sits on `tuned_L0`'s profile on **both**
  sides of the split, on all three conditions. A KL to a frozen clean-code teacher should reproduce
  the teacher's confidence profile, and it does — measured on log-probabilities, an instrument
  entirely separate from the accuracy cells E4 was read on.
- **Caveats.** 150 items per cell, one seed, `base` unavailable on L0 (the dump predates the arm
  list). The correct/wrong split conditions on each arm's **own** correctness, so the item sets
  differ slightly between arms; the within-arm spread is the statistic to quote, and it is
  descriptive, not a test. Two conditions besides X1 is enough to say "not X1-specific" and not
  enough to characterise the shape across the whole ladder. RQ4′ keeps its correlational status —
  nothing here restores the causal leg the knockout lost.
- **Next:** the natural follow-up is a calibration curve (ECE / reliability) per arm per condition on
  the full cells rather than 150 items, which is CPU-only on data that already exists. Docs:
  `docs/RQ_SUMMARY.md` §6 RQ1′/RQ4′, `MASTER_REPORT.md` §29.4.
