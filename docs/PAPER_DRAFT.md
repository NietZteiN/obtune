# Paper draft — argument and flow

*Last updated: 2026-09-10*

A working draft of the paper's **argument**, section by section, with the load-bearing number in
each place and the gaps named. Not the prose; the skeleton the prose hangs on. Framing decisions
and the evidence map are in [`PAPER_FRAMING.md`](PAPER_FRAMING.md); the experiment ledger is
[`PAPER_EXPERIMENTS.md`](PAPER_EXPERIMENTS.md).

**Reading rule for this file.** Every number is one already published in `RQ_SUMMARY.md` or the
master report. Statements the evidence does **not** yet support are marked ❑ with the experiment
that would earn them. Nothing here is written as though a pending result had landed.

---

## 0. The argument in one paragraph

Fine-tuning a code model on obfuscated code works: +18 points on output prediction. We ask what
that competence is made of by testing whether it **composes**. It does not. Of the three ways to
compose single-transform adaptation — routing over specialists at inference, merging in weight
space, breadth in the training data — only breadth generalises to stacked inputs at all, and only
to stacks of transforms it has already seen; on an unseen transform family the same breadth is a
*liability* that grows with training volume. Probing what was learned explains why: adaptation
anchors on the **surface** a transform leaves behind, not on the semantics it preserves. Two halves
of one obfuscation family do not transfer to each other, yet either half alone recovers ~90 % of
the family's gain; breadth's stacking benefit is carried by identifier transforms; and the whole
effect reverses when the same programs are asked backwards. Anchoring the objective to clean-code
behaviour — a KL term against a clean-code-tuned teacher on the unobfuscated parent — removes
breadth's costs without creating the capability breadth lacks. That last clause is the honest one:
the method is a Pareto repair, not new robustness, and we show exactly where its unseen-family
number comes from.

## 1. Title candidates

1. **Composition Is Where Obfuscation Robustness Breaks** ← recommended: names the finding, not the method.
2. Surface, Not Semantics: What Fine-Tuning on Obfuscated Code Learns to Compose
3. Breadth Buys Recombination, Not Novelty

(1) is the clearest statement of the paper's spine and invites the RQ1→RQ4 order. (3) is the
sharpest single result but under-sells RQ2, which is the explanatory half.

## 2. Abstract (draft)

> Fine-tuning raises a code model's output-prediction accuracy on obfuscated programs by 18 points.
> We ask whether that competence composes. Using a ladder of single, semantics-preserving
> transforms and a separate namespace of stacked composites, we test three ways of composing
> single-transform adaptation — routing over per-transform specialists, task-vector merging, and
> breadth in the training data — on CodeLlama-7B/13B/34B and Llama-3.1-8B. Routing is worth
> **exactly zero** over a random gate (+0.0000, [−0.0081, +0.0081]); merging lands at or below a
> clean-code-only control; and training breadth generalises to stacked inputs (**+3.49 / +2.90 /
> +3.05** points at three scales, and +4.15 at depth 3–4) but *only* to stacks of transforms it has
> seen. On a held-out transform family the same breadth **costs** 2.6–4.3 points, a tax that grows
> monotonically with training volume (−0.49 → −2.31 → −3.79 at ¼, ½ and full corpus) while its
> benefit saturates by a quarter of the data. We then show what adaptation actually learns: the two
> mechanisms of a single obfuscation family do not transfer to each other (+1.49 [−0.95, +3.93];
> −0.10 [−2.38, +2.19]) although either alone recovers ~90 % of the family's gain, breadth's
> stacking benefit is ordered by identifier content, models become sharper where they are right and
> twice as far from the answer where they are wrong, and the entire +18-point gain becomes −1.7
> when the same programs are asked backwards. Adaptation anchors on transform surface, not on
> preserved semantics. Finally, a paired-consistency objective that anchors the student to a
> clean-code-tuned teacher on the unobfuscated parent removes both of breadth's costs — **+4.86
> [+2.88, +6.83]** over breadth on the held-out family (q = 0.0049 under multiplicity control) with
> no clean-code penalty — and holds at 13B, 34B, on a second model family and in a second language.
> Ablating the teacher shows the unseen-family number is *inherited* from it rather than created:
> the objective buys a Pareto improvement, not new invariance. We release the calibrated held-out
> proxy, the pre-registration ledger, and every refuted lever.

## 3. Introduction — the five moves

1. **The setting and the easy result.** Obfuscation is a real deployment condition for code models
   (malware triage, minified/bundled production code, plagiarism and clone detection). Fine-tuning
   on obfuscated output prediction works: +18.09 points on the seen ladder. If that were the end of
   it, the paper would be an engineering note.
2. **The question that makes it interesting.** Real obfuscators *stack* transforms. So: does
   single-transform competence compose? This is a question about what was learned, asked
   operationally.
3. **The answer, stated as a dissociation, not a failure.** One pair of adapters, opposite signs on
   two axes: `mono_all − tuned_L0` is **+3.49** on stacked *seen* transforms and **−3.79** on an
   unseen family. Routing adds nothing; merging costs. The composition that works is in the data,
   and it works only inside what the data covered.
4. **Why — the explanatory core.** Adaptation is surface-anchored. Give the reader the X1-split
   result first because it is the cleanest: two mechanisms in one family, non-transferring to each
   other, each individually sufficient for ~90 % of the family gain. Then the reverse-task
   collapse, which no surface-independent account survives.
5. **What follows for method.** If the failure is surface anchoring, anchor to something else:
   clean-code behaviour on the same program. State the result *and its bound* in the introduction —
   the objective removes costs rather than adding capability — because that is the claim we can
   defend and the one a reviewer will otherwise extract under duress.

## 4. §2 Setup — longer than usual, and why

A negative-leaning result is attacked at the setup first, so every choice gets a sentence and a
number rather than a citation.

- **The ladder.** `L0` (normalised original) plus five single transforms — `L1b` adversarial
  renaming, `L1r` random renaming, `L2` minification, `S1` control-flow flattening, `S2` opaque
  predicates + dead code — **single-transform from the L0 parent, never stacked**, with identical
  semantics in Python and JavaScript. Composites live in a *separate namespace* precisely so that a
  transfer result is attributable to one mechanism.
- **The held-out family and its proxy.** `H1` (string encoding + guarded MBA) is quarantined behind
  four independent enforcement layers and was read exactly twice. `X1` is its trainable sibling:
  same two mechanisms, different surface, and it reproduces H1's difficulty at **r = 0.9992**
  (mean |Δ| 0.48 points). Every unseen-family number in the paper is X1; the budget for H1 is spent
  and we say so.
- **Correctness machinery, each with its number.** Program-level splits (never row-level); strict
  normalised exact match with **no containment matching** (an audit found ~3 % false positives from
  substring grading — `927` matching inside `9273`); `format_fail` reported everywhere; loss-mask
  verified on a real batch (prompt tokens −100); adapter-applied assertions; truncation logged at
  `max_seq_len` (≤ 0.7 % throughout); one prompt builder shared by training, both eval engines and
  attention extraction.
- **Statistics.** Program-clustered bootstraps (2,000 resamples) because multiple input cases per
  program are correlated; BH-FDR across the transfer matrix as one family; an item-level binomial
  GLMM as a cross-check that agrees with the bootstrap on 4/4 headline contrasts.
- **A measurement finding that belongs here, not in limitations.** Screening base models by their
  untuned `format_fail` is unsound. Applied to five candidate models it rejected three, and all
  three were wrong for *unrelated* reasons: two emitted correct values as unquoted strings; one has
  a chat template that asserts its own assistant persona and refuses a system role; one is a
  pretrained checkpoint whose answers open with a blank line that the decoder's stop sequence
  truncates. Tuned, those three reach 0.5401, 0.5180 and 0.4647 — the first two above the
  incumbent. **Untuned format failure measures the prompt contract, not the model.** ❑ *the panel
  those models support is still training; §7 states what the paper claims without them.*

## 5. §3 RQ1 — does single-transform adaptation compose?

**Claim.** Only composition in the data works, and only within what the data covered.

| level | mechanism | result |
|---|---|---|
| inference | learned router over per-transform specialists | **+0.0000** [−0.0081, +0.0081] vs a *random* gate; the mixture is worth +0.205, the routing worth nothing. Oracle over ten systems sits 52.9 points below a marginal-preserving permutation null — there is no complementary capability to dispatch to |
| weights | TIES / DARE-TIES / DARE-linear merges | merged accuracy at or below the clean-code control (−3.13 [−4.78, −1.40]) while the specialists being merged contribute +2.47 [+1.32, +3.70] |
| data | breadth (`mono_all`, six conditions) | **+3.49 / +2.90 / +3.05** on depth-2 composites at 7B/13B/34B; **+4.15** [+2.37, +5.91] at depth 3–4; but **−3.79 / −4.28 / −2.64** on the unseen family and −1.7 to −2.6 on clean code |

**The shape of breadth's success and failure.** The seen-composite gain **saturates by a quarter of
the corpus** (`mono_half − mono_all` +0.01, equivalent), while the unseen-family tax **grows
monotonically with volume**: −0.49 → −2.31 → −3.79 at ¼, ½, full. More data buys nothing on what it
covers and costs more on what it does not. This is the single most quotable pair of numbers in the
paper and Fig. 2 exists for it.

**Two corrections to the obvious telling, both of which the paper must make.**
- It is **not** true that all three strategies fail. Breadth succeeds on stacked-seen inputs at
  every scale tested. The finding is a *dissociation*, and stating it as blanket failure would be
  both wrong and less interesting.
- We do **not** attribute merging's failure to task-vector interference, and this is now measured
  on **the panel the paper reports** (F1b, 2026-09-11). The five specialists a merge is built from
  are the **most aligned, least conflicting** bank we measured — mean cosine **0.653**, coordinate
  sign conflict **0.323**, TIES retaining **91.6 %** of coordinates — and merging them still loses
  to them. A mechanism that predicts cancellation cannot explain a failure occurring where
  cancellation is lowest. The dominant axis is not the task at all: varying the **seed** alone drops
  mean cosine to **0.119** (near-orthogonal) while varying the **condition** alone leaves it at
  0.653, and in a mixed bank the most-aligned pair is same-seed, the least cross-seed. Geometry
  encodes initialisation, not knowledge. Two independent lineages now agree, which makes this a
  finding rather than a caveat. Caveat carried into the text: the seed-only bank mixes two
  checkpoint lengths, so "near-orthogonal" is the precision that claim supports.

❑ **Gaps.** Routing and merging have been measured on *stacks* only on a panel this paper no longer
uses (F1). No stack containing an *unseen* family has been built, so "failure worsens as the stack
diverges from training" is a hypothesis, not a result (F2) — the divergence ladder d0…d4 is designed
and costed.

## 6. §4 RQ2 — what is learned, and why it does not compose

**Claim.** Adaptation anchors on the surface a transform leaves, not the semantics it preserves.

Five independent instruments, sharing no machinery:

1. **The ladder cannot discriminate.** Mean off-diagonal transfer ratio **0.906** [0.878, 0.932];
   after BH-FDR, **1 of 30** specialist cells beats clean-code-only tuning. Whatever a specialist
   learns about its own transform, tuning on *clean code alone* already has. The seen ladder is not
   a test of invariance; only an unseen family is.
2. **The family is not the unit; the surface is.** Splitting `X1` into its MBA half and its
   string-encoding half: `tuned_X1m` reaches X1s at **+1.49** [−0.95, +3.93], `tuned_X1s` reaches
   X1m at **−0.10** [−2.38, +2.19] — they do not transfer to each other. Yet **either half alone
   recovers ~90 %** of the whole adapter's gain on stacked X1 (+4.12 / +4.20 against +4.61). Not
   additive, so not "MBA skill plus string skill". Consistent with X1 → H1 being *lossless* (0.08
   points) across genuinely different surfaces that force the same reading operation.
   ⚠ **The scaffolding reading is the natural one and it is NOT established.** The discriminating
   test ran on 2026-09-11 and came back **undecided**: classifying X1 programs by which mechanism is
   actually present lets a half-adapter be scored where none of its mechanism appears, and all three
   pre-registered rules returned INCONCLUSIVE — no interval excludes zero *and* none is equivalent
   to it. The lean is toward surface (all four cross-mechanism estimates positive: +2.64, +1.96,
   +5.44, +4.05, two excluding zero, where strict weakest-link predicts zero) but that is four of
   four with no correction over twenty contrasts, in groups as small as 49 programs. **The paper
   must say the halves do not decompose and stop there**, naming the surface account as the leading
   hypothesis and E5b as what would settle it. Writing "what transfers is the scaffolding" as fact
   is the one sentence in this section the evidence does not carry.
3. **Breadth's stacking gain is identifier recognition**, by a measured contrast rather than an
   ordering (F3a, 2026-09-11). On depth-3 stacks, breadth's gain over the clean-code control is
   **+5.00** [+3.02, +6.88] when the stack contains an identifier transform and **+1.61**
   [−1.02, +4.23] when it does not, and the **difference of differences is +3.39** [+0.82, +6.16],
   on one bootstrap over the 394 programs all four stacks share. We compute the difference because
   "one interval excludes zero and another does not" is not a test of the difference between them —
   the structural-only interval reaches +4.07 and overlaps every significant one. What may *not* be
   said, and the text says so: n = 1 structural-only stack, whose point estimate is positive, so the
   claim is about the difference and not about structural transforms contributing nothing.
4. **Breadth polarizes rather than degrades.** `mono_all`'s clean log P(gold) is ~4 nats below the
   control on *every* condition, and the whole deficit is in items it gets **wrong**: where right
   it is *more* confident (−0.16 vs −0.33), where wrong it is **twice as far** (−12.95 vs −7.00).
   Breadth makes the model more decisive about cues — free where the cue is right, expensive on a
   family where it is not. This supplies the tax mechanism.
5. **The competence is direction-specific.** The same adapters, the same programs, asked backwards
   (value → a call producing it, graded by execution): the arm that gains **+18.09** forward
   **loses 1.67** [−3.29, −0.04] backward. At most a tenth of any forward gain survives the flip.
   Only the family-trained arm beats the untuned model backwards, on its own family (+3.37
   [+0.41, +6.34]).

**Secondary instrument, reported as one:** tuning moves models *away* from human difficulty
orderings (Δρ = **−0.303** [−0.575, −0.028]); the untuned model tracks the human gradient at +0.82
and every tuned arm inverts it. Weak instrument (98 cells, one trial each) and labelled as such.

**Mechanism honesty.** The attention account is correlational. The causal instrument — identifier
knockout — is **inert**: it moves gold log-probability by < 0.5 % for every arm on every condition,
and both pre-registered hypotheses were refuted. We report that rather than omit it.

❑ **Gap, now narrower.** F3a establishes that breadth's stack gain *depends on an identifier
transform being present*, by direct contrast. It does not establish the causal step — that stacking
**destroys** a structural specialist's cue. The order pair `C_L1r_S1` / `C_S1_L1r` (renaming *after*
flattening removes the state-variable names a structural specialist keys on) is that test, and it
still needs specialists evaluated on composites (F3).

## 7. §5 RQ3 — anchoring to clean-code behaviour

**Claim.** Anchoring removes breadth's costs **on most models**; it does not add the capability
breadth lacks. The qualifier is load-bearing and is established below: across eight models the
tax-removal holds on six and reverses on one, and the no-clean-code-cost half holds on five.

**Objective.** `L = CE(y | x_obf) + λ · KL( p_teacher(· | x_L0parent) ‖ p_student(· | x_obf) )` at
answer tokens. The teacher is a clean-code-tuned adapter reading the *unobfuscated parent* of the
same program; λ = 3 is a plateau from a sweep on the trainable grid.

**Result** (values below are the published reads; the uniform grid reproduces each to within
0.85 pts — see the panel check below). `cons_lam3 − mono_all` on the unseen family: **+4.59**
[+3.16, +5.99] at 7B across three seeds, **+3.95** at 13B, **+3.38** at 34B, **+3.46** on
Llama-3.1-8B — and **q = 0.0049** in a
203-test, breadth-controlled FDR family. No clean-code tax (−0.30 [−1.80, +1.32]). It keeps
breadth's stacked-seen gain (+4.76 / +4.26 / +5.63 over the control at three scales) and beats
breadth there at 13B and 34B. In JavaScript it is best on all twelve columns and *amplifies*
(+7.35 seen, +3.37 on clean code) while breadth's stacking gain does **not** replicate.

**The ablation is the contribution, not the accuracy.** Vary the teacher and the result decomposes:
- teacher = untuned base → the arm **collapses** (−8.98 [−11.44, −6.43] vs breadth on X1);
- teacher = breadth model → it **inherits breadth's tax** (−4.20 [−6.27, −2.14] vs the clean-code
  teacher) while matching on seen conditions;
- across all three, **student ≈ teacher + ~1 point on the unseen family**.

So the seen-condition gain comes from the SFT term and is teacher-independent; the unseen-family
number is **distilled from the teacher**. The method is "distil from a clean-code-*tuned* model on
the clean parent", and the paper says exactly that.

**The panel breadth check, and it is the section's biggest change (eight-model uniform grid,
2026-09-12).** All eight models were re-read from **one phase, one config**, and the grid was
validated before the table: all four incumbents reproduce their published values through it, every
one inside the new interval, largest disagreement **0.85 pts**. So a departure is the model, not the
measurement.

| finding | tally over 8 models | Meta lineage (4) | other lineages (4) |
|---|---|---|---|
| **R1** breadth's unseen-family tax | **6 replicated, 2 inconclusive, 0 refuted** | 4 / 0 / 0 | 2 / 2 / 0 |
| **R2** anchoring removes it | **6 replicated, 1 inconclusive, 1 refuted** | 4 / 0 / 0 | 2 / 1 / 1 |
| **R3** no clean-code tax | **5 replicated, 0 inconclusive, 3 refuted** | 4 / 0 / 0 | 1 / 0 / 3 |

- **R1 is the paper's most robust claim** and should be stated as such: breadth's tax has the right
  sign on **every model in the panel**, across three lineages and 7B–34B, with **no contradiction**.
- **R2 survives at 6 of 8**, and is **reversed on Granite**, where the anchored arm is *worse* than
  breadth on the unseen family. That reversal is named in the text, not relegated.
- **R3 must become conditional.** "Anchoring pays no clean-code tax" holds on 5 of 8 and fails on
  three. It was discovered on four Meta-lineage models and holds on all four.
- **The lineage pattern is reported as a warning, not a result.** Every failure is outside the
  lineage of discovery, and all three findings are 4-of-4 within it. But Fisher's exact on the R3
  split is **p = 0.0714** one-sided (R1 and R2: 0.2143), **n = 8 models**, and "non-Meta" is three
  lineages in which *both Google models* refute R3 — so a Google-family effect and a lineage effect
  are perfectly confounded. The paper says: these findings replicate uniformly on the lineage they
  were found on and unevenly off it, and **single-lineage evaluation would have hidden that**.
- **StarCoder2 is the counter-example that keeps it honest** and belongs in the text: the only
  non-Meta model to replicate all three, the panel's strongest, and the one an untuned screening
  gate scored 0.0000 and would have rejected. Dropping it would have made the lineage pattern look
  *cleaner* and be *more wrong*.

❑ **Gap.** The consistency arm sees two views per row; no compute-matched control exists (F4,
`cons_lam0` — paired SFT without the KL term — is specified and would separate the objective from
the extra exposure).

## 8. §6 RQ4 — is it robustness, or a better surface heuristic?

**Claim, stated at its true strength.** The objective generalises along every axis we can test
*except* the one that would demonstrate new capability, and we are explicit about which is which.

| stress test | result | reading |
|---|---|---|
| deeper stacks (depth 3–4) | `cons_lam3 − tuned_L0` **+5.02** [+3.41, +6.69]; largest gain on the depth-4 stack | holds, and does not decay with depth |
| second language | best arm on all twelve JS columns; +4.91 over breadth on composites | replicates and amplifies |
| reverse task | `cons_lam3 − base` **+0.49** [−1.38, +2.30]; lowest `format_fail` of any arm | **does no harm** — the only SFT-family arm not damaged. Not "consistent performance" |
| confidence profile | sits on the clean-code arm's log P(gold) profile on both right and wrong items (+0.04 / −0.09), not on breadth's polarized one | not a new over-committing heuristic |
| the unseen family itself | ≈ the clean-code control (−0.30 / −0.33 / +0.74 across scales); **7th of 33** arms on X1 | the bound |

**The bound, stated in the paper's own voice.** On the held-out family the anchored model is *as
robust as clean-code tuning and no more*; every arm that beats it there was trained on that
family's sibling. Combined with the teacher ablation, the correct claim is: **anchoring buys
breadth's recombination benefit at no cost, and no new invariance.** A reviewer who extracts that
under duress has extracted our own sentence.

**The gap is now closed, and the answer is partial (F2, 2026-09-11).** Six composites were built,
each containing the unseen family as a component, and nine systems were evaluated on the 287
programs all six share, recorded before any system ran. Five rules and RQ4's reading **in both
directions** were committed before the first cell existed.

| level | stimulus | `mono_all − tuned_L0` | `cons_lam3 − tuned_L0` | `cons_lam3 − mono_all` |
|---|---|---:|---:|---:|
| d0 | depth-2, all seen | **+3.49** [+2.04, +5.01] | — | +0.87 [−0.59, +2.33] |
| d1 | depth-3/4, all seen | **+4.15** [+2.37, +5.91] | **+5.02** [+3.41, +6.69] | +0.87 (pooled with d0) |
| **d2** | depth-2, **contains unseen** | −1.71 [−3.60, +0.31] | **+2.13** [+0.66, +3.60] | **+3.84** [+1.90, +5.70] |
| **d3** | depth-3, **contains unseen** | −0.35 [−2.67, +1.86] | **+3.26** [+0.81, +5.92] | **+3.60** [+1.40, +5.81] |

- **What the pre-registered mapping returns: *undecided*.** It required *both* anchoring holding
  *and* breadth falling below the control, and only the first is established — d2's interval
  straddles zero. That verdict is reported as the verdict, first, in the paper's own voice.
- **What is established is stronger than "no tax".** On stacks containing an unseen family
  `cons_lam3` is **significantly above** the clean-code control and **significantly above breadth**.
  Read beside the seen stacks, where it merely *matches* breadth (+0.87, n.s.), the clean statement
  is: **anchoring's advantage over breadth appears only once the input diverges from what breadth
  was trained on.** That ordering was recorded as a prediction before these numbers existed.
- **Breadth's collapse is heterogeneous, and by the rule that predicts it.** The d2 pool averages
  three *significantly negative* cells with one *significantly positive* one. Splitting them by
  F3a's rule — committed 91 minutes before the first F2 cell, checkable in git — the
  identifier-containing group sits at +1.98 [−0.12, +4.18] and the structural-containing group at
  **−3.88** [−6.08, −1.71], a difference of **+5.85** [+3.10, +8.72] against +3.39 on seen stacks.
  So breadth is not uniformly broken by an unseen component; it is broken where the stack gives it
  no identifier surface to key on.
- **Family exposure remains the largest effect in the table:** `tuned_X1 − tuned_L0` **+5.93**, and
  `mono_allX − mono_all` **+6.28** — adding the family to breadth rescues breadth entirely.

**Scope, and it goes in the sentence rather than a footnote.** F2 is CodeLlama-7b alone, the model
the objective was developed on, and the panel has since shown R2 to be model-dependent (replicated
on 2 of 4 new models, refuted on Granite). The licensed claim is *"on the model where the objective
was developed, anchoring's advantage survives — and grows — when an unseen component enters the
stack."* ❑ Generalising needs the divergence ladder on one non-Meta-lineage model; StarCoder2 is the
candidate and its `tuned_X1`/`mono_allX` arms do not exist yet.

## 9. §7 Threats to validity

- **One held-out family pair.** X1/H1 only. A second, gentler pair returned null and was
  underpowered by construction (it damaged the control by 3.8 points against X1's 15.8); a
  redesigned pair is specified and deliberately unrun, because a prior result predicts it null
  whatever its difficulty.
- **H1's budget is spent.** Every unseen number in the body is X1, calibrated at r = 0.9992.
- **Correlational mechanism.** The knockout is inert; no causal attention claim is made.
- **Single seed at 13B/34B.** The 7B seed band is the only replication of the headline.
- **One trial per human cell.** By construction — the human study used one input case per item.
- **Language.** JavaScript replicates the objective and *not* breadth's stacking gain; there is no
  JS unseen-family column, so the tax half is untested there.
- **Model panel.** ❑ The current panel is CodeLlama ×3 + Llama-3.1-8B; a five-model extension
  (StarCoder2-15B, Gemma-3-12B, CodeGemma-7B, Granite-3.1-8B, a pretrained Llama-3.1) is training.
  Until it lands the paper claims what four Meta-lineage models support and says so.

## 10. §8 Related work — the three conversations we join

1. **Deobfuscation / DOBF lineage.** Our separation is that we never train or evaluate on recovery:
   evaluation is always on code that stays obfuscated, so we measure semantic competence under
   transformation rather than the ability to undo it.
2. **Model merging and modular adaptation** (TIES, DARE, MoLE, LoRA routing). We contribute a
   negative with an unusually strong control — a *random* gate — and a warning that task-vector
   geometry is dominated by initialisation rather than knowledge.
3. **Robustness to semantics-preserving transformation** in code models, and **direction
   specificity** in code understanding, which our reverse-task result replicates at value level.

## 11. Figures

- **Fig. 1 — the dissociation, now with the divergence ladder.** Paired bars, seen-composite gain vs
  unseen-family tax, at 7B/13B/34B, with a second row for training volume (¼, ½, full). Add a third
  row: breadth and anchoring across **d0 → d1 → d2 → d3**, where breadth crosses zero and anchoring
  does not. That crossing is the paper's memorable image and it now exists as data.
- **Fig. 2 — composition, three ways.** Router (vs random gate), merges, breadth, each against the
  clean-code control, on singles and on stacks. ❑ *stacks need F1.*
- **Fig. 3 — what is learned.** X1-split 2×2 (each half → each condition); breadth's stack gain
  with vs without an identifier transform **as a paired contrast with its difference annotated**
  (+5.00 / +1.61, difference +3.39 [+0.82, +6.16]), not a per-composite ordering; forward vs inverse
  per arm.
- **Fig. 4 — polarization.** log P(gold) distributions on right and wrong items, control vs breadth
  vs anchored.
- **Fig. 5 — the ablation.** Student X1 accuracy against teacher X1 accuracy for the three teachers,
  with the y = x line. The clearest statement that the number is inherited.

## 12. What must not be claimed

- "All three composition strategies fail" — breadth succeeds on stacked-seen at every scale.
- "Merging fails through task-vector interference" — **refuted on this panel** (F1b): the merged
  specialists are the most aligned, least conflicting bank measured. Say the failure without a
  mechanism, and report that seed dominates condition in the geometry.
- "Consistency training improves robustness" — it removes a cost; say Pareto.
- "Consistent performance on the reverse task" — it is undamaged, not improved.
- Any causal attention story — the knockout is inert.
- Anything about H1 beyond the calibration figure.
- **"Failures worsen with divergence"** — F2 ran. Breadth's gain flips sign once an unseen
  component enters (+3.49 / +4.15 seen → −1.71 / −0.35 unseen-containing), but the d2 interval
  straddles zero, so the pre-registered rule is **INCONCLUSIVE**. Say the sign flips and that the
  drop is not individually significant when pooled; the significant version is the
  identifier-vs-structural split, not the level.
- **"Anchoring is robust to unseen transformation families in stacks"** — say it about *the model
  the objective was developed on*, with the scope in the sentence. One model, and R2 is already
  known to be model-dependent. *(The divergence ladder is queued on StarCoder2, Gemma-3 and
  Granite with the rules and the prediction pre-registered; three of three would let the qualifier
  go.)*
- **"Anchoring pays no clean-code tax"** — **5 of 8 models.** Conditional, with the three failures
  named.
- **Anything causal about model lineage** — n = 8, p = 0.07 at best, and Google/non-Meta are
  confounded. It is a warning about single-lineage evaluation, not a result about lineages.
- **"What transfers is the family's scaffolding/surface"** — the discriminating test came back
  **undecided** (E6 item split, 2026-09-11). Say the halves do not decompose, name the surface
  account as the leading hypothesis, and cite E5b as what would settle it.
- "Anchoring beats breadth on stacked inputs" — on seen stacks it *matches* breadth (+0.87
  [−0.59, +2.33] pooled); only the depth-4 cell separates, at one significant result of four with no
  multiplicity correction.
- "Structural transforms contribute nothing to breadth's stack gain" — F3a measures a *difference*
  (+3.39), on n = 1 structural-only stack whose own estimate is positive.

---

## Changelog
- **2026-09-10** — Created. Argument and flow for the user's RQ1–RQ4, written against the results as
  they stand. Three of the originally stated findings are adjusted where the evidence differs
  (breadth succeeds on stacked-seen; the interference mechanism is not supported; the reverse-task
  result is "undamaged", not "consistent"), and the gate-as-screen finding is promoted into §2 as a
  measurement contribution.
