# Paper framing — the spine, the contributions, the outline

*Last updated: 2026-09-08*

This is the framing recommendation for the paper, written against the results as they stand on
2026-09-08 (master report rev 19, [`RQ_SUMMARY.md`](RQ_SUMMARY.md) §6–§7,
[`PAPER_EXPERIMENTS.md`](PAPER_EXPERIMENTS.md) claims C1–C8). Every number below is one already
in those documents; each is cross-referenced to the log entry that produced it. Nothing here is a
new measurement. The paper's claim labels are **P1–P4** so they do not collide with the
experiment plan's **C1–C8**; the map between them is in §3.

---

## 1. The spine in one sentence

**Fine-tuning on obfuscated code teaches transform fluency, not semantic invariance — and the
boundary between the two is measurable, has a shape, and has a price.**

Three independent instruments, sharing no machinery, say the first half; a three-scale
dissociation says the second; a two-part mechanism explains the price; one objective avoids paying
it without creating any capability. That ordering is the paper.

## 2. Why lead with the negative

The charter asked one question (`CLAUDE.md` §3): invariance or memorization? The answer is *not
invariance*, and — unusually for a negative — it arrives from three directions at once:

| instrument | what it measures | result | entry |
|---|---|---|---|
| **the ladder does not discriminate** | specialist arms vs clean-code tuning on the six trained conditions | mean off-diagonal TR **0.906** [0.878, 0.932]; after BH-FDR **1 of 30** specialist cells survives (`tuned_S2` on S2, q = 0.030) — specialists are indistinguishable from `tuned_L0` | [`writeup/2026-09-08_fdr-over-the-families.md`](../log/writeup/2026-09-08_fdr-over-the-families.md) |
| **the family does** | the same arms on the unseen family | `mono_all − tuned_L0` @ X1 **−3.79** [−6.09, −1.65] (q = 0.014); `tuned_X1 − tuned_L0` @ X1 **+4.86** [+2.80, +6.92] (q = 0.005); X1→H1 lossless (0.08 pts) | [`transfer/2026-09-05_x1-is-a-trainable-proxy-for-h1.md`](../log/transfer/2026-09-05_x1-is-a-trainable-proxy-for-h1.md), [`writeup/2026-09-08_fdr-family-enlarged.md`](../log/writeup/2026-09-08_fdr-family-enlarged.md) |
| **bidirectionality** | the same programs, asked backwards (value → call), graded by execution | `tuned_L0` gains **+18.09** forward and loses **−1.67** [−3.29, −0.04] backward; only the family unit holds (`tuned_X1` on X1 +3.37 [+0.41, +6.34]) | [`transfer/2026-09-08_bidirectional-inverse-task-read.md`](../log/transfer/2026-09-08_bidirectional-inverse-task-read.md) |
| **human divergence** | item-level Spearman against the 98 Paper-2 human cells | `tuned_L0 − base` **Δρ = −0.303** [−0.575, −0.028]; at condition level `base` tracks the human gradient at **+0.82**, every tuned arm inverts it (−0.10 / −0.41 / −0.41) | [`human-align/2026-09-08_tuning-moves-away-from-humans.md`](../log/human-align/2026-09-08_tuning-moves-away-from-humans.md) |

A careful reader can wave away any one of these. The ladder result alone says "the ladder was too
easy"; the inverse result alone says "output prediction is a narrow task"; the human result alone
is 98 cells at one trial each. Together they are a finding, because they fail in the same
direction for unrelated reasons. **This is the spine, and the paper should say so in the first
paragraph.**

Precision matters on the first row: the point is *not* that specialists fail to transfer within
the ladder — they transfer almost completely (C3). The point is that clean-code tuning already
gets all of it, so the ladder cannot tell fluency from invariance; only a transform *family the
model has not seen* can, and there the answer is negative.

## 3. Contributions, in the order the evidence supports them

| # | claim | load-bearing number | plan claim | strength |
|---|---|---|---|---|
| **P1** | Tuning teaches fluency, not invariance | the four rows of §2 | C2, C3, C8, RQ5′ | three instruments, all pre-registered, all FDR-surviving where a family exists |
| **P2** | Breadth generalises over *composition*, not *novelty* — and the tax grows with data | stacked-seen `mono_all − tuned_L0` **+3.49 / +2.90 / +3.05** at 7B/13B/34B; unseen **−3.79 / −4.28 / −2.64**; q = 0.014; GLMM agrees 4/4 (**−0.546** [−0.761, −0.331] logits). Seen gain saturates by ¼ corpus (`mono_half − mono_all` +0.01); X1 tax grows **−0.49 → −2.31 → −3.79** | C1, RQ1′ | strongest single result; the figure the paper is remembered by |
| **P3** | The mechanism is polarization + inheritance | `mono_all` log P(gold): right **−0.16 vs −0.33**, wrong **−12.95 vs −7.00** (sharper where right, twice as far where wrong); student X1 = teacher X1 + ~1 pt for three teachers (`cons_tbase − mono_all` @ X1 −8.98; `cons_tmono − cons_lam3` −4.20) | RQ4′, E4, E14 | correlational; the attention knockout is inert (< 0.5 % of gold log-prob, both hypotheses REFUTED), so **no causal leg** |
| **P4** | Paired consistency avoids the tax — a Pareto point, not a capability | `cons_lam3 − mono_all` @ X1 **+4.86**, q = **0.0049** in a 203-test `mono_all`-controlled family, all seeds and all λ; no L0 tax (−0.30 [−1.80, +1.32]); 13B +3.95, 34B +3.38, Llama-3.1-8B +3.46; **7th of 33 on X1** (`x1_resample` 0.324, `tuned_X1` 0.315 … `cons_lam3` 0.282) | C5, RQ3′ | corollary of P3 — it removes a cost by distilling from a clean-code-tuned teacher; it does not beat any family-trained arm on the family |

Entries: P2 — [`transfer/2026-09-07_composites-on-codellama.md`](../log/transfer/2026-09-07_composites-on-codellama.md),
[`transfer/2026-09-08_composites-at-13b-and-depth-3-4.md`](../log/transfer/2026-09-08_composites-at-13b-and-depth-3-4.md),
[`transfer/2026-09-08_composites-at-34b.md`](../log/transfer/2026-09-08_composites-at-34b.md),
[`transfer/2026-09-08_saturation-the-tax-grows-with-data.md`](../log/transfer/2026-09-08_saturation-the-tax-grows-with-data.md),
[`writeup/2026-09-08_glmm-agrees.md`](../log/writeup/2026-09-08_glmm-agrees.md).
P3 — [`transfer/2026-09-08_breadth-polarizes.md`](../log/transfer/2026-09-08_breadth-polarizes.md),
[`transfer/2026-09-08_teacher-is-the-ingredient.md`](../log/transfer/2026-09-08_teacher-is-the-ingredient.md),
[`attention/2026-09-08_x1-knockout-is-inert.md`](../log/attention/2026-09-08_x1-knockout-is-inert.md).
P4 — [`transfer/2026-09-06_consistency-objective-repairs-breadth.md`](../log/transfer/2026-09-06_consistency-objective-repairs-breadth.md),
[`transfer/2026-09-08_consistency-survives-scale.md`](../log/transfer/2026-09-08_consistency-survives-scale.md),
[`transfer/2026-09-08_consistency-replicates-on-llama.md`](../log/transfer/2026-09-08_consistency-replicates-on-llama.md),
[`writeup/2026-09-08_fdr-the-uncovered-headline.md`](../log/writeup/2026-09-08_fdr-the-uncovered-headline.md).

**Human divergence is not a fifth contribution.** It belongs inside P1 as the third instrument;
that is where it does the most work. Modularity (C4: router − random gate +0.0000
[−0.0081, +0.0081]; merging −3.13 vs specialists' +2.47) is likewise evidence *for* P1 — there is
no complementary capability for a router or merge to find — rather than a section of its own.

## 4. Title

1. **Fluency, Not Invariance: What LoRA Fine-Tuning on Obfuscated Code Actually Transfers** ← recommended
2. Breadth Buys Composition, Not Novelty: The Boundary of Transfer Under Code Obfuscation
3. Tuned Models Get Better and Less Human: Measuring Semantic Invariance After Fine-Tuning on Obfuscated Code

(1) names the dissociation in four words and the second clause tells the reader this is a
measurement, not a method. (3) is the strongest hook and the weakest description — the human
result is one instrument of four.

## 5. Abstract (draft; every number is already published in the report)

> Fine-tuning on obfuscated code raises output-prediction accuracy by 18 points. We ask whether
> that gain is *semantic invariance* — robustness to the class of meaning-preserving transforms —
> or *transform fluency* — familiarity with the transforms seen in training. Across 116 systems on
> CodeLlama-7B/13B/34B and Llama-3.1-8B, three independent instruments give the same answer.
> (i) Within the trained ladder, specialists are indistinguishable from clean-code tuning (1 of 30
> cells at q < 0.05); on an unseen transform family, training breadth *costs* 2.6–4.3 points.
> (ii) Tuned models that gain 18 points forward lose 1.7 on the same programs asked backward.
> (iii) Tuning moves models *away* from human difficulty orderings (Δρ = −0.30 [−0.58, −0.03]);
> the base model tracks the human gradient, every tuned arm inverts it. What tuning does teach has
> a measurable shape: breadth buys robustness to *recomposition of seen transforms* (+3.0 to +3.5
> points at all three scales, FDR q = 0.014, GLMM-confirmed), saturating by a quarter of the
> corpus, while the unseen-family tax grows monotonically with data. The mechanism is polarization,
> not degradation — broad models are sharper where right and twice as far from gold where wrong —
> and the tax is inherited from whatever a student is distilled from. A paired-consistency
> objective removes the tax without creating new capability, replicating and amplifying in
> JavaScript while the breadth effect does not. We release the calibrated held-out proxy
> (r = 0.9992 to the quarantined obfuscator), the pre-registration ledger, and every refuted
> lever.

## 6. Section outline and what each carries

1. **Introduction** — the 18-point gain; the two hypotheses; the three-instrument answer in one
   figure (Fig 1); the shape of what transfers in one sentence.
2. **Setup** — the ladder (`L0/L1b/L1r/L2/S1/S2`, single-transform, identical semantics in both
   languages, [`TIER_MAPPING.md`](TIER_MAPPING.md)); the H1 quarantine and the X1 proxy
   (r = 0.9992, mean |Δ| 0.48 pts); program-level splits; the strict grader; the composite
   grid. **Longer than usual.** Reviewers of a negative result attack the setup first, so every
   silent-failure check in `CLAUDE.md` §4 (split leakage, adapter-applied assertion, one prompt
   builder, loss-mask gate, no substring grading, format-fail rate, forgetting, truncation) gets
   a sentence and a number.
3. **Tuning teaches fluency, not invariance (P1)** — 3.1 the ladder does not discriminate
   (TR, FDR); 3.2 the family does (X1 diagonal, breadth's tax); 3.3 bidirectionality;
   3.4 human alignment (item-level ρ with program-clustered bootstrap; condition-level table;
   power stated: 98 cells, one trial each, by construction).
4. **The shape of what transfers (P2)** — composition vs novelty at three scales; depth 3/4
   (+4.15); saturation; the L0 cost (21 of 60 arms pay, none gains; it lands on the *common*
   answer classes, difficulty-matched +10.21 [+5.34, +15.14] —
   [`transfer/2026-09-08_l0-cost-format-matched.md`](../log/transfer/2026-09-08_l0-cost-format-matched.md));
   the ranking of every lever against `tuned_L0` as the single control row (Fig 4).
5. **Why (P3)** — polarization (E14); teacher inheritance (E4); the attention knockout reported
   as inert so the mechanism stays predictive, not causal.
6. **Avoiding the tax (P4)** — `cons_lam3` across λ, seeds, scales, languages; explicitly ranked
   7th on X1; compute-matched caveat (the consistency arm sees two views per row — a
   compute-matched `tuned_L0` has not been run).
7. **Cross-language** — consistency replicates and amplifies in JavaScript (best on all 12
   columns; +7.35 seen, +3.37 on L0); breadth's stacking gain does **not** replicate
   (+2.55 [−0.30, +5.31], three of six composites negative); no unseen-family column exists in
   JS. Its own section, not a limitations bullet: a partial replication is a result
   ([`transfer/2026-09-08_crosslanguage-javascript.md`](../log/transfer/2026-09-08_crosslanguage-javascript.md)).
8. **Limitations** — one family pair (E5's second pair null by construction,
   [`transfer/2026-09-07_second-family-pair-is-null.md`](../log/transfer/2026-09-07_second-family-pair-is-null.md);
   E5b respecified, unrun); the H1 budget is spent, so every unseen number in the body is X1;
   one JS seed; the mechanism is correlational; Qwen/DeepSeek systems exist only on the 34–40
   program subset (`RQ_SUMMARY.md` §4.1 caveat); the human anchor is one trial per cell.
9. **Related work** — the DOBF lineage and why never training on recovery is the separation;
   Nikiema et al. on direction-specificity (RQ5′ replicates it at value level); Papers 1–3 for
   the human baselines.

**Appendix:** the full 116-row panel (`MASTER_REPORT.md` §2.2b, `RQ_SUMMARY.md` §7); the
pre-registration ledger (`CLAUDE_SCRATCHPAD.md`) with every refuted hypothesis listed as refuted
and every wrong pre-read prediction (the JS volume prediction among them) reported; the coverage
matrix; the per-condition GLMMs.

## 7. Figures

- **Fig 1 — three instruments.** Three panels: (a) specialist matrix heatmap with the one
  surviving cell outlined and the X1 column beside it; (b) forward vs inverse paired points per
  arm; (c) human-vs-model difficulty rank plots for `base` and `tuned_L0`.
- **Fig 2 — the dissociation.** Seen-composed gain and unseen tax as paired bars with CIs at
  7B/13B/34B; a second row for volume (¼, ½, full). This is the figure the paper is remembered by.
- **Fig 3 — mechanism.** Log P(gold) distributions on right and wrong items for `tuned_L0` vs
  `mono_all` (polarization), beside student-vs-teacher X1 scatter for the three teachers
  (inheritance).
- **Fig 4 — the levers.** Every 7B system against `tuned_L0`, one row of intervals each, ±1.0
  TOST band shaded, arms grouped by family. Most rows sit inside the band; that is the point.

## 8. Claims to refuse

- **"Fine-tuning hurts generalisation."** It hurts on one axis and helps on another; the whole
  paper is that the axis matters.
- **Any causal attention story.** The knockout is inert. RQ3's re-anchoring is a correlate on seen
  conditions and is reported as one.
- **"Consistency training improves robustness."** It removes a cost. Say Pareto; say the unseen
  number is distilled from the teacher; say it is 7th on X1.
- **Anything about H1 beyond the calibration figure.** The budget is spent (`CLAUDE.md`
  changelog 2026-09-05). No H1 number selects, tunes, or ranks anything.
- **JS as a replication.** It is a partial one, and the stacking half failed.
- **Corrected p-values for the wrong contrasts.** `cons_lam3 − tuned_L0` on X1 (q = 0.44) and
  breadth's L0 cost (q = 0.38) do not survive; the GLMM resolves the latter (−0.218
  [−0.397, −0.040]) but that is uncorrected and is not promoted.

## 9. Venue

The human-alignment instrument and the three-paper lineage argue for an SE venue (ICSE/FSE) over
an ML one. There, "tuned models get better and less human" is a contribution rather than a
curiosity, and the setup rigour in §2 is what reviewers reward. At an ML venue the same paper
reads as a negative result with a modest method attached, and P4 would be pushed to the front,
where it loses on the one column that matters.

## 10. The scope decision

This is a **characterisation paper, not a methods paper.** Framed as "we propose paired
consistency", the dozen-plus refuted levers (C6, C4) become filler and the paper's best result is
an arm that is 7th on the discriminator. Framed as characterisation, every refutation is
evidence for P1 and the objective is the corollary that closes the story.

---

## Changelog
- **2026-09-08** — Created. Framing written against master report rev 19 and `RQ_SUMMARY.md` §6–§7,
  after the whole-panel tables (§2.2b / §7) and the `cons_lam3` implications discussion. One
  correction relative to the conversational draft that preceded it: §2's first instrument is not
  "the transfer matrix collapses" — within the ladder transfer is near-complete (C3, TR 0.906);
  it is that the ladder *cannot discriminate* fluency from invariance because clean-code tuning
  already captures it, and the unseen family can.
