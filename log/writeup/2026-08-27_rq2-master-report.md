# 2026-08-27 — writeup — RQ2 master report: closing the routing-and-merging thread

**Goal / hypothesis.** The routing-and-merging thread (RQ2 / `modularity`) ran 08-05 → 08-17 and
ended negative, but had **no single document covering the whole arc**: `MASTER_REPORT_2026-08-12.md`
predates the verdict, and the 08-15 and 08-17 reports each cover a three-day chain — with 08-17
retiring the central claim of 08-15 without either being marked. Produce the closing master report,
recomputing every number from cells rather than copying it forward, and see what survives contact
with the raw data.

**Setup.** No GPU. `/data/jvl210002/conda_envs/obtune/bin/python`, read-only over
`results/cells/*/qwen25c-1.5b/python/*/trials.parquet` (1,918 cells), `results/analysis/*.json`,
`results/merge_geometry/*.json`, `results/router/.../routing_report.json`. Contrasts: paired
cluster bootstrap by `program_id`, 2,000 resamples, seed 17. Output:
[`../../docs/MASTER_REPORT_2026-08-27_router-and-merging.md`](../../docs/MASTER_REPORT_2026-08-27_router-and-merging.md).

**Results.** The verdict reproduces exactly. All four published Grid A `H1` contrasts recompute to
≤0.02 pts: `merge_dare_ties` − `tuned_L0` = **−0.66** [−1.89, +0.66]; `l0merge_dare_ties` −
`tuned_L0` = **−3.13** [−4.78, −1.40]; 6-specialist − 3×clean-code merge = **+2.47** [+1.32, +3.70];
`tuned_S2_s17` − `tuned_L0` = **+3.46** [+2.06, +4.94]. Geometry (0.053 / 0.487 cosine and sign
conflict for the byte-identical-data `L0` bank vs 0.592 / 0.390 for the eight different-transform
specialists), the gate collapse (TV .011–.056, `L1r` self-mass .003), the probe (99.4 % at layer 4),
the router (route accuracy 1.000), and the density sweep (47.0 / 44.7 / 40.5 at d = 0.3 / 0.5 / 0.7)
all reproduce.

**Three findings the re-check produced.**

1. **The eval stack is 2–15× noisier than recorded, on the control everything is read against.**
   `tuned_L0` on Grid B `H1` was run three times with the same adapter path, prompt sha, 115 items,
   engine (vllm-0.26.0) and sampling (T=0): **40.0** (08-05, commit `4927d65`, gpu2), **34.8**
   (08-13, `469f857`, gpu1), **33.9** (08-14, `469f857`, gpu1). The last two match on **every**
   recorded field and still differ on **12 of 115 generations**, flipping 5 graded trials. Across
   the commit boundary: 31 of 115 generations, 6.1 pts. The recorded floor is "0.1–0.4 pts from
   batching nondeterminism". The Grid A panel is unaffected in substance (paired contrasts, n=1214),
   but **every Grid B `H1` comparison in the older documents is within one re-evaluation of its
   neighbour** — including the 34.8-vs-33.9 tie that opened this thread. Also an `H1` exposure
   issue: `pilot_eval` + two `final_eval` passes on the same quarantined items.
2. **The pooled seed band has been applied to Python-only contrasts throughout.**
   `MASTER_REPORT_2026-08-12.md` §8.4 reports Python **0.63 / 1.46**, JavaScript **2.01 / 4.03**,
   pooled **1.32 / 3.61**, and states the correct per-language rule. The **pooled** number is what
   propagated — into the 08-15 and 08-17 reports, four log entries, and the docstrings of
   `scripts/merge/24_crossseed_control.py`, `scripts/merge/25_residual_merge.py` and
   `scripts/attn/30_knockout.py`. Every experiment in this thread is Python, so the bar has been
   ~2.5× too permissive. My recompute over 42 matched Python s17/s42 pairs: mean **0.52**, p95
   **0.96**, max 2.22. **One secondary claim moves:** "`mole_hardrouter` reproduces `mole_router`,
   max 2.7, all inside 3.61" — at the Python bar of ~1.5 the max |Δ| of 2.67 does not clear it.
   Restated as "11 of 15 cells inside the bar, mean |Δ| 0.88, signed both ways", which still
   supports selection-not-blending. Nothing in the verdict depends on the band; those carry CIs.
3. **The best merge density does not transfer to `H1`.** `d=0.3` is monotonically best on all six
   trainable conditions (47.0 vs 44.7 at 0.5), and the 08-17 report listed its `H1` read as owed.
   The cell landed 08-17 and reads **32.2** on Grid B `H1` against `merge_dare_ties`' 34.8. The
   condition it was tuned on improves; the held-out one does not.

**Also recorded:** `mole_random` — a `RouterGate` frozen at random init — has mean normalised
entropy **1.000** and per-expert mass uniform to three decimals, i.e. it is behaviourally a second
uniform gate (it differs from `mole_uniform` on 3–11 generations per condition, ≤1.7 pts). The
mixture ladder therefore has three rungs but **two distinct controls**, which is what kills
`CLAIM_LADDER.md` Branch B. Branches C and D are dead on §5.3 and the uniform-epoch sweep
respectively; the draft's empty thesis slot should be filled with **Branch A**.

**Observations.** Writing a master report from cells rather than from reports is what surfaced all
three items — the same lesson `paper_modularity/` already records, now with a fourth instance. The
noise finding is the uncomfortable one: it does not touch the Grid A verdict, but it means a whole
layer of Grid B readings in this project were never resolvable, and it was invisible because each
report quoted a single number per cell with no re-run to compare against.

**Next steps.** (1) Determinism note in `CLAUDE.md` §Correctness, and an `ACCESS_LOG.md` reconcile
for the three `H1` control passes. (2) Fix the seed-band constant in the three script docstrings to
the Python figure. (3) The `train_size: 30000` LOTO correction, still owed in its own commit.
(4) Fill `paper_modularity/main.tex`'s thesis slot with Branch A. **No new RQ2 runs are
recommended** — §9 of the report ranks what would reopen the thread, and only a second held-out
family (`H2`/`H3`) could overturn rather than qualify the verdict; the `attention` and
`normalization` threads are already pursuing the one positive result (`S2` → `H1`).
