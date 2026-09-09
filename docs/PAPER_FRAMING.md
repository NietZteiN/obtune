# Paper plan — RQ1–RQ4: composition, cues, anchoring, robustness

*Last updated: 2026-09-09*

> **Scope (2026-09-09): no Chinese-origin models.** Qwen/DeepSeek results are withdrawn from the
> evidence base and every number below is CodeLlama-7b/13b/34b or Llama-3.1-8B. The panel, its
> planned extension (StarCoder2, Gemma-3, a pretrained Llama-3.1, CodeGemma, Granite) and the
> dataset additions are in [`MODEL_AND_DATA_SELECTION.md`](MODEL_AND_DATA_SELECTION.md).

The paper is organised around the four research questions the user fixed on 2026-09-09
(verbatim in §1). This document maps each RQ's stated methodology and finding onto what the
project has **already measured** (with the number and the log entry), marks what is **not yet
measured**, and points at the experiment in [`PAPER_EXPERIMENTS.md`](PAPER_EXPERIMENTS.md) §7
(**F1–F9**) that closes each gap. Every number here is already published in
[`RQ_SUMMARY.md`](RQ_SUMMARY.md) §4–§7 or the master report; nothing was read for this document.

The previous framing (2026-09-08, *fluency not invariance*, contributions P1–P4) is superseded as
the paper's organising principle but not as evidence: every result it cited is re-used below. The
old text is in `git show 3825ad0:docs/PAPER_FRAMING.md`.

**Status legend.** ✅ measured and supports the finding as stated · ⚠️ measured, supports a
*narrower* statement than the finding — the paper must use the narrower one · ❌ not measured on
the current panel — an F-experiment exists · 🚫 measured and *contradicts* the finding as stated.

---

## 1. The four RQs (as fixed 2026-09-09)

**RQ1 — Composition.** *Can adaptation strategies designed for single obfuscations generalize to
stacked obfuscations?* Three levels of composition: at inference (routing over specialists), in
weights (merging), in data (broad SFT). Claimed finding: all three fail — routing because a stacked
input matches no single distribution; merging through task-vector interference; breadth by losing
on unseen families and on clean code — and failures worsen as the test stack diverges from the
training distribution.

**RQ2 — What is learned.** *What do models learn during single-transformation adaptation, and why
does it fail on composite inputs?* Within-family vs cross-mechanism transfer. Claimed finding:
surface-level structural heuristics tied to the cues of one transformation; stacking destroys the
isolated cues; the fix must anchor to clean-code semantics.

**RQ3 — Anchoring.** *Does anchoring adaptation to clean-code behaviour resolve the failure?* Paired
consistency (SFT + λ·KL to a clean-code teacher on the L0 parent), with the teacher ablated. Claimed
finding: +4.59, robustness on stacks retained, no clean-code drop, gains from the clean-code anchor
rather than generic distillation.

**RQ4 — Genuine robustness or a new heuristic?** Reverse task, deeper stacks, stacks containing
unseen families. Claimed finding: consistent performance across these ⇒ structural robustness.

---

## 2. RQ1 — composition: evidence map

| leg | what the finding says | what is measured | status |
|---|---|---|---|
| **inference — routing** | fails: a stacked input matches no single distribution | On **singles**, CodeLlama-7b: learned gate − random gate **+0.0000** [−0.0081, +0.0081]; mixture worth +0.205 regardless of gate; oracle over 10 systems 52.9 pts below a permutation null (no complementary capability to route to). On **stacks**: nothing on this panel (the only stacked routing read was Qwen, now withdrawn). **No routing arm has been evaluated on a composite on the CodeLlama panel**, and the router's *behaviour* on a stack (which expert it picks, with what entropy) has never been recorded. | ❌ → **F1** |
| **weights — merging** | fails through task-vector interference (contrasting geometries) | On singles: TIES/DARE merges at or below `tuned_L0` (−3.13 [−4.78, −1.40] while specialists contribute +2.47). On stacks: never on this panel. **The interference explanation was tested and refuted on the (now withdrawn) Qwen panel** (`REPORT_2026-08-17` §3): three `L0` adapters on byte-identical data at different seeds were near-orthogonal (cos 0.053, sign conflict 0.487 — a coin flip) and *merged fine*, while eight different-transform specialists were 0.59-aligned — geometry was initialisation. That read cannot be cited; **F1b repeats it on CodeLlama**, and until it lands the mechanism is neither supported nor refuted. | ❌ on stacks and on the mechanism → **F1** (accuracy) + **F1b** (geometry, cross-seed, CodeLlama) |
| **data — breadth** | fails: drops on unseen families and degrades clean code | `mono_all − tuned_L0`: **stacked-seen +3.49 / +2.90 / +3.05** at 7B/13B/34B, depth 3/4 **+4.15**; **unseen X1 −3.79 / −4.28 / −2.64**, H1 −4.12; **L0 −1.74 / −2.34 / −2.63**; the X1 tax grows with data (−0.49 → −2.31 → −3.79 at ¼/½/full) while the seen gain saturates by ¼. GLMM agrees 4/4; `mono_all` on X1 survives FDR at q = 0.014. | ⚠️ **Breadth does not fail on stacked-seen inputs — it is the one strategy that succeeds there.** It fails on the two axes the finding names (unseen, clean). The paper must say "breadth generalises to recombination of *seen* transforms and pays for it on unseen families and on clean code", not "all three fail". |
| **divergence gradient** | failures worsen as the stack diverges from training | Two points exist: depth-2 seen (+3.49) → depth-3/4 seen (+4.15, *no decay*) and single unseen (−3.79). **No stack containing an unseen family has ever been built**; there is no intermediate point on the axis. | ❌ → **F2** (the divergence ladder: seen-d2 → seen-d3/4 → one-unseen-d2 → one-unseen-d3 → unseen-only) |

**What the current data support for RQ1, verbatim for the paper.** *Of the three composition
strategies, only training breadth generalises to stacked inputs, and only to stacks of transforms it
has seen; routing and merging add nothing over the clean-code control on single transforms (F1
extends this to stacks). Breadth's stacked gain is bought with a tax on unseen families that grows
with data volume and a cost on clean code that grows with scale.* The "worsens with divergence"
sentence becomes available only after F2.

Entries: [`transfer/2026-09-07_composites-on-codellama.md`](../log/transfer/2026-09-07_composites-on-codellama.md),
[`transfer/2026-09-08_composites-at-13b-and-depth-3-4.md`](../log/transfer/2026-09-08_composites-at-13b-and-depth-3-4.md),
[`transfer/2026-09-08_composites-at-34b.md`](../log/transfer/2026-09-08_composites-at-34b.md),
[`transfer/2026-09-08_saturation-the-tax-grows-with-data.md`](../log/transfer/2026-09-08_saturation-the-tax-grows-with-data.md),
[`modularity/`](../log/modularity/) (router/merge on CodeLlama singles), `REPORT_2026-08-15_modularity_verdict.md`,
`REPORT_2026-08-17_geometry-and-attempted-repairs.md`.

## 3. RQ2 — what is learned: evidence map

| observation | number | what it says about cues | status |
|---|---|---|---|
| **The ladder cannot discriminate.** Specialists ≈ clean-code tuning on every seen condition | mean off-diagonal TR **0.906** [0.878, 0.932]; after BH-FDR **1 of 30** specialist cells beats `tuned_L0` (`tuned_S2` on S2, q = 0.030) | whatever a specialist learns on its own transform, clean-code tuning already has — the seen-transform "skill" is mostly task acquisition | ✅ |
| **Inside a family the mechanism is the unit; across it the surface is.** X1 split (E6) | `tuned_X1m` → X1s **+1.49** [−0.95, +3.93]; `tuned_X1s` → X1m **−0.10** [−2.38, +2.19]; yet either half alone gives **+4.12 / +4.20** on stacked X1 against the whole's +4.61 (~90 %) | the two mechanisms of one family do not reach each other, but either half's training carries the family's *scaffolding cue* (helper defs at module top, longer code) — a surface heuristic, non-additive | ✅ the strongest direct evidence for "surface cues" |
| **Cross-surface, same reading operation transfers losslessly** | X1 → H1 **0.08 pts**; the gentle second family X2 → Y2 **+1.21** [−0.81, +3.22] (underpowered) | transfer follows the forced reading operation / scaffold, not the mechanism and not invariance | ✅ (one family pair) |
| **Breadth's stacked gain is carried by the identifier component** | per-composite `mono_all − tuned_L0`: +6.6 / +5.6 (identifier+S1) → +1.1 (S4+S3) at 7B; 13B +4.5/+5.0/+4.1 → +0.4/+1.4; depth-3 structural-only `C3_S1_S3_S4` **+1.61** [−1.02, +4.31] n.s. vs `C3_L1r_S1_S4` +6.10* | the composite gain is identifier-cue recognition, not structure — H-stack-identifier can be closed CONFIRMED from existing cells | ✅ (analysis F3a formalises it) |
| **Polarization, not degradation** (E14) | `mono_all` right items −0.16 vs −0.33 nats; wrong items **−12.95 vs −7.00**; global, not X1-specific | breadth learns to *commit* on cues; where the cue misleads it is twice as far from gold — the signature of a cue-driven heuristic | ✅ |
| **Forward tuning does not survive the reverse task** (RQ5′) | `tuned_L0` **+18.09** forward, **−1.67** [−3.29, −0.04] backward; DR ≤ 0.10 for every arm; `tuned_L1b` — the one signal that penalises trusting names — is the best inverse arm on all 7 conditions (single seed, unregistered) | what is learned is the forward task's surface, not a direction-free program model | ✅ |
| **Tuning moves away from human difficulty orderings** (E10) | `tuned_L0 − base` Δρ **−0.303** [−0.575, −0.028]; `base` tracks the human gradient at +0.82, every tuned arm inverts it | the learned heuristic is not the one humans use | ✅ (weak instrument: 98 cells, one trial each) |
| **Attention knockout is inert** | identifier knockout moves gold log-prob < 0.5 % for every arm | no causal attention story is available; cue-dependence must be shown *behaviourally* | ⚠️ RQ2 is behavioural and correlational; say so |
| **"Stacking destroys the isolated cues"** — the causal link to RQ1 | the order pair `C_L1r_S1` vs `C_S1_L1r` (renamer after flattener destroys S1's `_st_` state-variable names) exists, and identifier-first is easier in 7/9 model×system reads by ≤ 2.6 pts — but **no specialist has been evaluated on the CodeLlama composites**, so "the S1 specialist's gain vanishes when its cue is renamed away" is unmeasured | ❌ → **F3** (specialists on stacks, cue-survival item split, order pair) |

**Verbatim for the paper.** *Single-transformation adaptation teaches recognisable-surface
heuristics: inside one family the two mechanisms do not transfer to each other, yet either one carries
the family's scaffold; across families only a shared reading operation transfers; breadth's stacked
gain is identifier-cue recognition and its failure is over-commitment on cues that mislead; none of it
survives asking the same programs backwards; and it moves models away from human difficulty
orderings.* The sentence "stacking destroys the cues" needs F3.

Entries: [`transfer/2026-09-08_x1-split-mechanism-not-family.md`](../log/transfer/2026-09-08_x1-split-mechanism-not-family.md),
[`transfer/2026-09-08_breadth-polarizes.md`](../log/transfer/2026-09-08_breadth-polarizes.md),
[`transfer/2026-09-08_bidirectional-inverse-task-read.md`](../log/transfer/2026-09-08_bidirectional-inverse-task-read.md),
[`human-align/2026-09-08_tuning-moves-away-from-humans.md`](../log/human-align/2026-09-08_tuning-moves-away-from-humans.md),
[`writeup/2026-09-08_fdr-over-the-families.md`](../log/writeup/2026-09-08_fdr-over-the-families.md),
[`attention/2026-09-08_x1-knockout-is-inert.md`](../log/attention/2026-09-08_x1-knockout-is-inert.md).

## 4. RQ3 — anchoring: evidence map

| claim | number | status |
|---|---|---|
| **+4.59** | `cons_lam3 − mono_all` @ X1, 7B: **+4.59** [+3.16, +5.99] (three seeds +4.53/+4.12 at s42/s101); `mono_all`-controlled FDR family of 203 tests: **q = 0.0049**, all seeds, all four λ. 13B **+3.95** [+2.22, +5.84], 34B **+3.38** [+1.32, +5.51], Llama-3.1-8B **+3.46** [+1.65, +5.35] | ✅ — the number is the *advantage over breadth on the unseen family*; the paper must name the contrast |
| **retains robustness on stacked inputs** | `cons_lam3 − tuned_L0` on depth-2 composites **+4.76 / +4.26 / +5.63** (7B/13B/34B); `cons_lam3 − mono_all` **+1.27** [−0.02, +2.59] / **+1.36*** / **+2.58***; depth 3/4 `− tuned_L0` **+5.02***, `− mono_all` +0.87 n.s.; JS `− mono_all` on composites **+4.91*** | ✅ |
| **no clean-code drop** | `cons_lam3 − tuned_L0` @ L0 **−0.30** [−1.80, +1.32] (7B), −0.60 n.s. (13B), +0.42 (34B), +0.00 (Llama), **+3.37*** (JS); vs `mono_all` +1.74* / +3.05* | ✅ as "no *detectable* cost" — at n = 557 a ±1.0 TOST margin is unreachable (E11), so certified equivalence is not available |
| **gains come from the clean-code anchor, not generic distillation** | teacher ablation (E4): untuned `base` teacher **−8.98** [−11.44, −6.43] vs `mono_all` on X1; `mono_all` teacher inherits breadth's tax (**−4.20** [−6.27, −2.14] vs `cons_lam3`) while matching it on seen (−0.39 n.s.). View ablation (round 1): `cons_same_lam1` (teacher sees the *same* obfuscated input = plain distillation) — `cons_lam3 − cons_same_lam1` @ X1 **+2.31** [+0.82, +3.87], pooled +1.31*. Decomposition: the seen gain is the SFT term (teacher-independent); the unseen number is *inherited from the teacher* (student X1 ≈ teacher X1 + ~1 pt for all three teachers) | ✅ — **but the same ablation bounds the claim**: on the unseen family `cons_lam3` ≈ `tuned_L0` (−0.30 / −0.33 / +0.74), i.e. it *removes breadth's tax* rather than adding capability; it is **7th of 33** on X1 behind every family-trained arm |
| compute-matched control | the consistency arm sees two views per row; no `tuned_L0`/`mono_all` at matched token budget, and no λ = 0 "paired SFT" arm exists | ❌ → **F4** |

**Verbatim for the paper.** *Anchoring to a clean-code-tuned teacher on the clean parent keeps
breadth's stacked gain (and beats breadth there at 13B/34B and in JavaScript), pays neither of
breadth's taxes, and the unseen-family number is inherited from the teacher — the objective is a
Pareto repair, not a source of new capability.* "Resolves the trade-off" is right; "improves
robustness" is not.

Entries: [`transfer/2026-09-06_consistency-objective-repairs-breadth.md`](../log/transfer/2026-09-06_consistency-objective-repairs-breadth.md),
[`transfer/2026-09-08_consistency-survives-scale.md`](../log/transfer/2026-09-08_consistency-survives-scale.md),
[`transfer/2026-09-08_teacher-is-the-ingredient.md`](../log/transfer/2026-09-08_teacher-is-the-ingredient.md),
[`transfer/2026-09-08_consistency-replicates-on-llama.md`](../log/transfer/2026-09-08_consistency-replicates-on-llama.md),
[`writeup/2026-09-08_fdr-the-uncovered-headline.md`](../log/writeup/2026-09-08_fdr-the-uncovered-headline.md).

## 5. RQ4 — robustness or a new heuristic: evidence map

| stress test | number | status |
|---|---|---|
| **reverse task** (input prediction, execution-graded) | `cons_lam3 − base` @ seen6 **+0.49** [−1.38, +2.30]; `− mono_all` @ obf **+1.73*** ; `− tuned_L0` @ obf **+3.18***; lowest `format_fail` of any arm (1.4 %); DR +0.03 | ⚠️ **"does no harm", not "consistent performance"** — every SFT arm loses backwards, consistency is the only one that does not; it does not teach inversion. 7B only |
| **deeper stacks** (depth 3/4, 394-program common subset) | `cons_lam3 − tuned_L0` **+5.02** [+3.41, +6.69]; `− mono_all` +0.87 [−0.59, +2.33]; largest gain on the depth-4 stack (+7.20 over `tuned_L0`) | ✅ vs the control; vs breadth n.s. at 7B (significant at 13B/34B on depth 2 only) |
| **stacks containing unseen families** | — | ❌ **never built** → **F2** |
| a second language | JS: best arm on all 12 columns, +7.35* seen, +4.91* over breadth on composites, +3.37* on L0 | ✅ (no unseen-family column in JS; `node` absent) |
| surface perturbation of the unseen family | `x1_resample` exists as a *training* arm; no arm has been evaluated on X1 rebuilt at a different obfuscation seed | ❌ → **F5** |
| a second hard family pair | E5 null (underpowered); E5b respecified, not run | ❌ → **F6** (design-gated) |
| profile evidence | `cons_lam3` sits on `tuned_L0`'s log P(gold) profile on both right and wrong items (+0.04 / −0.09 vs `tuned_L0`), not on breadth's polarized one | ✅ supports "not a new over-committing heuristic" |
| human alignment | `cons_lam3 − base` Δρ −0.244, interval spans zero (not verdicted) | ⚠️ moves away from humans like every tuned arm |

**The claim that must be confronted head-on.** E4 says the unseen-family number of `cons_lam3` is
the *teacher's* number. "Genuine structural robustness" therefore cannot rest on X1 alone: on X1 the
arm is exactly as robust as clean-code tuning, no more. What the current data support is: *the
objective adds breadth's stacked gain without breadth's over-commitment, and that combination holds
at depth 3/4, in a second language, and on the reverse task (where it is the only SFT arm not
damaged).* Whether it holds on **stacks that include an unseen family** — the case where breadth's
two behaviours collide — is the experiment that decides RQ4, and it is F2.

Entries: [`transfer/2026-09-08_bidirectional-inverse-task-read.md`](../log/transfer/2026-09-08_bidirectional-inverse-task-read.md),
[`transfer/2026-09-08_composites-at-13b-and-depth-3-4.md`](../log/transfer/2026-09-08_composites-at-13b-and-depth-3-4.md),
[`transfer/2026-09-08_crosslanguage-javascript.md`](../log/transfer/2026-09-08_crosslanguage-javascript.md),
[`transfer/2026-09-08_breadth-polarizes.md`](../log/transfer/2026-09-08_breadth-polarizes.md),
[`transfer/2026-09-08_e5b-redesigned-not-run.md`](../log/transfer/2026-09-08_e5b-redesigned-not-run.md).

---

## 6. Section outline

1. **Introduction** — single-transform adaptation works (+18 pts); real obfuscation is stacked; the
   three ways to compose single-transform adaptation; the four questions; one figure (Fig 1: the
   divergence ladder, every strategy as a line).
2. **Setup** — ladder `L0/L1b/L1r/L2/S1/S2`, single-transform by construction; the composite
   namespace (depth 2/3/4; order pairs); the held-out family H1, its trainable proxy X1
   (r = 0.9992, |Δ| 0.48 pts) and the quarantine; program-level splits; strict grader; the
   silent-failure checks of `CLAUDE.md` §4 each get a sentence and a number.
3. **RQ1 — Composition** — 3.1 routing on stacks (F1) with the router's decision distribution;
   3.2 merging on stacks (F1) and why geometry is not the explanation (cross-seed control);
   3.3 breadth: the dissociation at three scales, saturation, the L0 cost and where it lands
   (common answer classes, +10.21 matched); 3.4 the divergence ladder (F2) — Fig 2.
4. **RQ2 — What is learned** — 4.1 the ladder does not discriminate (TR 0.906, 1/30);
   4.2 the X1 split: mechanism inside, surface across; 4.3 the identifier carries the stacked
   gain (F3a) and the cue-destruction test (F3); 4.4 polarization; 4.5 the reverse task;
   4.6 human divergence. Explicitly behavioural: the knockout is inert and is reported as such.
5. **RQ3 — Anchoring** — objective; λ and seed bands; scale (13B/34B) and family (Llama);
   stacked-seen at every depth; the teacher and view ablations; the compute-matched control (F4);
   the decomposition (SFT term → seen gain; teacher → unseen number) stated as the mechanism.
6. **RQ4 — Robustness** — reverse task; depth 3/4; unseen-in-stack (F2); surface resampling (F5);
   JavaScript; the profile evidence; the honest bound (X1 = teacher's number; 7th of 33).
7. **Limitations** — one hard family pair (F6 pending); H1 budget spent, every unseen number is X1;
   single seed at 13B/34B; JS has no unseen column; mechanism is correlational; human anchor is
   one trial per cell; no Chinese-origin model (scope rule), so the Qwen-era results are not cited.
8. **Related work** — DOBF lineage (never trained on recovery); task-vector merging (TIES/DARE) and
   the interference literature we fail to reproduce; MoE/LoRA routing; consistency/invariance
   regularisers; Nikiema et al. (direction-specificity); Papers 1–3 (human baselines).

**Figures.** Fig 1 divergence ladder (x = seen-d2 → seen-d3/4 → one-unseen-d2 → one-unseen-d3 →
unseen; y = Δ vs `tuned_L0`; one line per strategy: router, merge, breadth, consistency, family) —
*needs F1+F2*. Fig 2 the dissociation at three scales + volume (exists). Fig 3 cue evidence: X1-split
2×2 + per-composite breadth gain ordered by identifier content + polarization histograms. Fig 4
anchoring: `cons_lam3` vs `mono_all` vs `tuned_L0` on every column at 7B/13B/34B/Llama/JS, plus the
teacher ablation bars. Fig 5 stress tests: forward vs inverse per arm; depth curve; resampled-surface
variance (F5).

## 7. Claims to refuse (carried over and extended)

- **"All three composition strategies fail."** Breadth succeeds on stacked-seen at every scale. Say
  which axis each strategy fails on.
- **"Merging fails because of task-vector interference."** Neither supported nor refuted on this panel (the
  Qwen refutation is withdrawn). Report merging's failure without a mechanism until F1b lands.
- **"Consistency training improves robustness / learns invariance."** It removes a cost; on the
  unseen family it inherits the teacher; 7th of 33 on X1.
- **"Consistent performance on the reverse task."** It is undamaged, not improved (+0.49 vs base).
- **Any causal attention story.** Knockout inert.
- **Anything about H1 beyond calibration.** Budget spent; H1 is never stacked, never read.
- **Failures "worsen with divergence"** — until F2 has run.

## 8. Venue

Unchanged: SE venue (ICSE/FSE). RQ1–RQ2 are a characterisation, RQ3–RQ4 a modest repair with an
honest bound; that shape is rewarded there and read as "a negative result with a method attached"
at an ML venue.

---

## Changelog
- **2026-09-09 (b)** — Scope rule: no Chinese-origin models; Qwen numbers removed from the evidence
  map (the Qwen composite +3.91 and the Qwen geometry refutation), F1b promoted from "reported" to
  required. Panel and dataset plan in `MODEL_AND_DATA_SELECTION.md`.
- **2026-09-09** — Reorganised around the user's RQ1–RQ4 (composition / what is learned / anchoring /
  robustness), replacing the 2026-09-08 "fluency, not invariance" P1–P4 framing as the organising
  principle. Every result is re-mapped with a status; three stated findings are flagged against the
  record: breadth does *not* fail on stacked-seen inputs, the task-vector-interference mechanism for
  merging was refuted on 2026-08-17, and routing/merging on stacks plus every stack containing an
  unseen family are unmeasured. The experiments that close the gaps are F1–F9 in
  `PAPER_EXPERIMENTS.md` §7.
- **2026-09-08** — Created (P1–P4 framing; see `git show 3825ad0:docs/PAPER_FRAMING.md`).
