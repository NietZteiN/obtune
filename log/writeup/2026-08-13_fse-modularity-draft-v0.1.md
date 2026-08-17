# 2026-08-13 — FSE modularity draft v0.1, written from result files

*Thread: writeup. Companion: [`../modularity/2026-08-13_mole-random-inert-control.md`](../modularity/2026-08-13_mole-random-inert-control.md).*

## Goal / hypothesis

Draft the RQ2 (routing / merging) manuscript for the FSE research track, in a new
`paper_modularity/` directory — the second manuscript reserved by
`paper_bidirectional/README.md`. Explicit constraint from the human: **there is no headline
claim yet**, so the deliverable is a complete skeleton with every measured number in place,
every unmeasured cell visibly empty, and the pending experiments specified as first-class
content rather than a "future work" paragraph.

No GPU. Writing plus a read-only pass over `results/`.

## Setup

- Env `/data/jvl210002/conda_envs/obtune`; LaTeX via `/data/jvl210002/conda_envs/tex/bin/tectonic`.
- Numbers recomputed from **897 cells / 369,089 trials** under `results/cells/` by
  `paper_modularity/analysis/{10_collect_cells,11_rq2_contrasts}.py`. Cross-check: all 897
  recomputed accuracies match their own `cell_meta.json` to 5e-4 — **0 mismatches**.
- Statistics as elsewhere in the project: cluster bootstrap by `snippet_id`, 2000 draws,
  seed 17, BH-FDR per family, effect called only when q<0.05 **and** the CI excludes zero.

## Results

**The master report is materially stale.** `docs/MASTER_REPORT_2026-08-12.md` covers 597 cells;
there are now 897. Four experiment groups it lists as *pending* in §9 have run:

| landed | what |
|---|---|
| 2026-08-12 | `merge_overtrain_full` — the **8-expert uniform-epoch sweep** (48 cells) |
| 2026-08-12 | `merge_optimal_r{1,2,3}` — the **greedy merge-optimal search** (216 cells) |
| 2026-08-12 | `dare_linear_rescaled` — the **repaired DARE-linear arm** (6 cells) |
| 2026-08-13 | `rq2_mole_ladder` — the **activation-space mixture ladder** (30 cells) |

Two further items in §8 are out of date: §8.2 ("Grid B has no control in Python") is resolved —
`tuned_L0` and `base` cells exist on the test-set grid from `grid_s3s4_qwen1.5b`, which is what
makes RQ2 quantitative in Python — and §5.3's geometry table is superseded by a file written
after the report, which covers **eight** experts rather than three.

**New findings the draft now carries.**

1. **The router is worth nothing beyond its specialists, and now with Python CIs.** Against the
   clean-code control on the test-set grid: +0.6 / +9.1 / +0.6 / +0.6 / +0.0 / −1.7 across
   `L0…S2`. Only `L1b` moves and it does not survive correction (q=0.056, CI [+1.2,+16.7]).
   Five of six conditions indistinguishable from an adapter that never saw obfuscated code.

2. **Merge-optimal checkpoint selection buys nothing.** 27 candidates over three greedy rounds
   span 0.4434–0.4506 — 0.7 accuracy points end to end — and every round's winner is 0.7–1.0
   points *below* `merge_dare_ties` (all p>0.4).

3. **`merge_dare_linear` was a rescaling defect, not a result.** The repaired arm
   (`dl_rescaled`) gains **+41.6 [+33.9,+49.9]** pooled and lands at parity with the control on
   all six conditions, format-failure back to 0.6–2.8 % from 53.5 %. §8.5 of the master report
   can be closed. The generalisable point: a broken merge degrades the *format* channel first,
   so a pipeline reporting only accuracy would have published a −40-point "finding" about DARE.

4. **Horoi's mechanism reproduces; its consequence reverses, now without either caveat.** On the
   8-expert 9-epoch bank sign conflict rises 0.4011 → 0.4254, cosine falls 0.5799 → 0.5142,
   `interference_grows: true`. Yet merged accuracy *improves*: pooled e9−e1 = **+3.1
   [+0.0,+6.1]** (dare_ties) and +1.6 [−0.4,+3.5] (ties), better on 11 of 12 method×condition
   pairs. DARE-TIES moves from −2.6 below control at epoch 1 to +0.5 at epoch 9. The master
   report's two caveats — 3-vs-8 experts, and unequal epochs — are both removed by this bank.

5. **The mixture arm is the right sign everywhere and significant nowhere.** `mole_router` −
   `mole_uniform` is positive on **8/8** conditions (+0.6 to +7.4); pooled +3.3 [−0.4,+7.5]
   over composites, +2.9 [−0.0,+6.2] p=0.059 over all eight. No cell survives FDR at 40
   programs.

6. **`mole_random` is inert** — bit-identical to `mole_uniform` on all 1,299 items. Full
   diagnosis in the modularity entry. This is the arm that was designated to decide what the
   headline may say, so **no mixture claim is available** until it is re-run.

**Deliverable.** `paper_modularity/` — `main.tex` (7 pp compiled, `acmart` sigconf,
double-anonymous), `refs.bib` (8 extracted + 7 new, all new ones marked `UNVERIFIED`),
`NUMBERS.md` (per-claim provenance, four report-vs-file discrepancies, and what is deliberately
absent), `CLAIM_LADDER.md` (four candidate theses with firing conditions and a decision order),
`README.md`, and the two analysis scripts. Two macros carry the draft's state: `\pending` for an
unmeasured cell, `\slot` for an unearned claim; 12 occurrences, and the submission checklist is
that both reach zero.

## Observations

- **Drafting from result files rather than reports paid for itself again.** It caught the four
  stale sections above and the inert control. The master report is a good index and an unreliable
  source, which is exactly what the ATTRIB entry concluded on 2026-08-12.
- The first version of the contrast script **pooled the two evaluation grids** — it let `base`
  and `oracle_prompt_1shot` fall onto the corpus grid while the merge arms sat on the test set,
  producing plausible-looking deltas across different program populations. Grid separation is now
  enforced in code (`GRID` in `11_rq2_contrasts.py`) rather than left to care. This is the rule
  from `MASTER_REPORT` §2 and it needs a guard, not a convention.
- `acmart` + `amssymb` halts XeTeX on `\Bbbk` (newtxmath already defines it). Recorded in the
  README so it is not rediscovered.
- The honest shape of the paper right now is five settled results, of which two are negative and
  one is a bug repair, plus one open effect. That is a publishable negative-results paper today
  and a stronger paper after one evaluation pass.

## Next steps

- **Re-run `mole_random` with the ordering hazard fixed.** One eval pass, no retraining, and it
  is the first item in `CLAIM_LADDER.md`'s decision order because it currently blocks the
  abstract.
- **Revise `docs/MASTER_REPORT_2026-08-12.md`** — or supersede it — for the four stale sections
  (§5.3 geometry table, §8.2, §8.5, §9's pending list).
- Verify the 7 `UNVERIFIED` bib entries against primary sources, especially `horoi2025less`
  whose title is currently a placeholder.
- Recount composite acceptance (1656 vs 1658) and correct whichever document is wrong.
- Confirm the FSE page budget against the live CfP before treating 7 pp as headroom.
