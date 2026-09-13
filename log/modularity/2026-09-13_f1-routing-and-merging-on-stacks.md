# 2026-09-13 — F1 read: routing and merging on stacks of seen transforms (CodeLlama-7B)

**Thread:** modularity · **Status:** read against the pre-registered rules; H-F2-route submitted · **Related:** [`2026-09-12_routing-cells-were-the-base-model.md`](2026-09-12_routing-cells-were-the-base-model.md), [`2026-09-13_mixture-guard-refused-the-mixture-engine.md`](2026-09-13_mixture-guard-refused-the-mixture-engine.md)

## Provenance

`ev_f1_mole` 392638 (`obtune.mole.eval_mole`, HFEngine, h100 g-05-01, 91 min, 80 cells) → `an_f1`
392641 (`scripts/analysis/56_f1_routing_merging.py`) → `results/analysis/pipeline/f1_routing_merging_codellama7b.json`.
Common subset **394 programs** across every cell; clustered bootstrap 2,000 resamples, seed 17. The
routing cells now differ from the untuned model everywhere (e.g. `mole_router` on `C_L1b_S1` 0.325
against base 0.141), which is CLAUDE.md §4 check 2 passing where the 09-12 run failed it.

## Numbers (points, paired, all ten stacks; depth 2 / depth 3–4 in the JSON)

| contrast | all ten |
|---|---|
| `mole_router − mole_random` | **+1.34 [+0.48, +2.17]** |
| `mole_router − mole_uniform` | **+1.40 [+0.52, +2.25]** |
| `mole_hardrouter − mole_router` | +0.03 [−0.13, +0.19] |
| `mole_router − mono_all` | −0.28 [−1.57, +1.09] |
| `mole_uniform − base` | **+19.79 [+17.40, +22.23]** |
| `merge_dare_ties − tuned_L0` | +0.52 [−0.15, +1.20] |
| `merge_ties − tuned_L0` | **−5.50 [−6.86, −4.13]** |
| `merge_dare_linear − tuned_L0` | **−20.56 [−22.88, −18.25]** |
| `l0merge_ties − tuned_L0` | **−3.14 [−4.21, −2.12]** |
| `l0merge_dare_ties − tuned_L0` | **−1.74 [−2.57, −0.91]** |
| `mono_all − tuned_L0` | **+3.67 [+2.02, +5.24]** |
| order test, `tuned_S1` gain cue-intact − cue-destroyed | −0.68 [−3.30, +2.12] |

## Verdicts by the registered rules

- **H-F1-route** (CONFIRMED iff router ≈ random at ±1.0; REFUTED iff ci_lo > +1.0): **INCONCLUSIVE.** The
  router beats a random gate, significantly, by about a point; the lower bound (0.48) does not clear
  the margin. Routing is worth about one point.
- **H-F1-route-vs-breadth** (CONFIRMED iff router < breadth): **INCONCLUSIVE.** Router and breadth are
  indistinguishable (−0.28 [−1.57, +1.09]).
- **H-F1-merge** (CONFIRMED iff DARE-TIES ≤ clean control): **INCONCLUSIVE.** The best merge matches
  the clean-code control (+0.52 [−0.15, +1.20]); the other four are significantly below it, DARE-linear
  catastrophically. No merge reaches breadth (+3.67 over the control).
- **H-F1-mixture** (descriptive): the mixture is worth +19.8 over the untuned model — essentially the
  whole gain of any tuned arm.
- **H-F3-order** (CONFIRMED iff the S1 specialist gains more when S1's state-variable names are intact):
  **INCONCLUSIVE**, point estimate the wrong sign. No evidence the specialist keys on the surface cue.

## What it means for the paper

The draft's composition paragraph carried `+0.0000 [−0.0081, +0.0081]` for router − random — a
single-condition, saturated-gate number — and "routing and merging do not compose at all". On stacks
the accurate statement is narrower: **routing composes exactly as far as breadth does** (it matches
breadth, and a hard argmax router matches the soft one, so there is no blending advantage on a
two-mechanism input, which was the hypothesis the composites were built to test), and **merging does
not compose** (best case equals the clean control). The paper text is changed accordingly; the
`rq1_composition` table carries the numbers.

What is still unmeasured: routing on a stack that contains an unseen family. Pre-registered as
H-F2-route in `CLAUDE_SCRATCHPAD.md` and submitted (`ev_f2_mole`, six F2 composites, four arms).
Prediction: routing inherits breadth's failure.

## Follow-up noted

Mixture cells record `adapter_paths: []` and `adapter_sha256: {}` — `eval_mole` does not write the
experts' paths and hashes into `cell_meta.json`. The adapter-applied check above rests on the
accuracies differing from base, which is sufficient, but the provenance layer should carry the eight
expert paths and the gate checkpoint's hash.
