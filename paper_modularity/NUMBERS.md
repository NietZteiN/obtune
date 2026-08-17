# Provenance for every number in `main.tex`

*Last updated: 2026-08-13. Draft v0.1.*

Rule for this file, inherited from [`../paper_bidirectional/NUMBERS.md`](../paper_bidirectional/NUMBERS.md):
**every figure in the paper is traceable to a file on disk produced by a recorded run.**
Nothing in `main.tex` is quoted from `docs/MASTER_REPORT_*.md` or from any other report — the
reports were used as an index of *where to look*, and were then cross-checked against these
files. Where a report and a result file disagreed, the file won and the discrepancy is recorded
in §4 below.

Every accuracy in the paper was **recomputed from the per-cell trial records**, not read from
`cell_meta.json`. As a check, all 897 cells were compared against their own recorded accuracy:
**0 mismatches** at a tolerance of 5e-4.

---

## 1. How to regenerate every number

```bash
cd /data/jvl210002/my_downloads/obtune
export OBTUNE_PAPER_CACHE=paper_modularity/.cache
/data/jvl210002/conda_envs/obtune/bin/python paper_modularity/analysis/10_collect_cells.py
/data/jvl210002/conda_envs/obtune/bin/python paper_modularity/analysis/11_rq2_contrasts.py
```

| script | produces |
|---|---|
| `analysis/10_collect_cells.py` | `.cache/cells2.csv`, `.cache/trials_all.parquet` — every cell and every trial, keyed by the cell's own `system` label. Deliberately **not** routed through `obtune.trial_table`, whose `is_core` definition has drifted before (`MASTER_REPORT` §8.1). |
| `analysis/11_rq2_contrasts.py` | all control-relative deltas, cluster-bootstrap CIs, BH-FDR, and the pooled composite contrasts |

Statistics: cluster bootstrap by `snippet_id` (program), 2000 resamples, seed 17; BH-FDR
within each delta family; an effect is called only when `q<0.05` **and** the bootstrap CI
excludes zero. Every comparison is restricted to the programs present in *both* arms.

**Grid separation is enforced in code.** `GRID` in `11_rq2_contrasts.py` splits the corpus grid
(`apps_*`, `cruxeval_*`; 557 Python programs) from the test-set grid (`A:…`, `B:…`; 40 Python
programs). The first version of this script did not, and let `base`/`oracle_prompt_1shot` fall
onto the corpus grid while the merge arms sat on the test set — exactly the error the
never-pool rule exists to prevent. That version's numbers are not in the paper.

## 2. Runs the paper draws on

| experiment_id | what | cells | date |
|---|---|---|---|
| `grid_v1` | router, the three merges, on the test-set grid | 27 py / 27 js | 2026-08-09 |
| `grid_rq1` | the RQ1 transfer matrix (motivation only) | 91 py / 98 js | 2026-08-09 |
| `grid_s3s4_qwen1.5b` | `tuned_L0` and `base` on the test-set grid, plus `S3`/`S4` | 60 py / 66 js | 2026-08-09/10 |
| `merge_overtrain_full_qwen25c-1.5b_python` | **8-expert uniform-epoch merge sweep** | 48 | 2026-08-12 |
| `merge_optimal_r{1,2,3}_qwen25c-1.5b_python` | **greedy merge-optimal checkpoint search** | 216 | 2026-08-12 |
| `dare_linear_rescaled_qwen1.5b` | **the repaired DARE-linear arm** | 6 | 2026-08-12 |
| `rq2_mole_ladder` | **the activation-space mixture ladder** | 30 | 2026-08-13 |
| — | router training/routing reports | — | `results/router/qwen25c-1.5b/{python,javascript}/routing_report.json` |
| — | task-vector geometry | — | `results/merge_geometry/adapters{,_overtrain}_qwen25c-1.5b_python.json` |

The last four experiment groups **postdate `docs/MASTER_REPORT_2026-08-12.md`**, which lists
them as pending (§9). This paper is the first document to report them.

## 3. Section by section

| paper location | numbers | source | status |
|---|---|---|---|
| Abstract, §1 | mean off-diagonal TR 0.073; specialists +1 to +8 pts | `MASTER_REPORT` §3.2 / `results/analysis/master_report.json` | measured |
| §3.5 | base format-fail 17.3 % py; adapters 1–3 % | `.cache/cells2.csv`, `fmt` column | measured |
| §4.2 | route accuracy 1.000; 1025 py / 804 js items; val 0.9969 py / 1.0000 js | `results/router/*/routing_report.json` | measured |
| §4.2 | entropy 3.9e-7 … 6.7e-3 nats vs max ln 8 = 2.0794 | same, `entropy.per_condition[*].entropy_mean` | measured |
| §4.3, Table 1 | `router` row +0.6/+9.1/+0.6/+0.6/+0.0/−1.7; L1b CI [+1.2,+16.7] q=0.056 | `11_rq2_contrasts.py`, Grid B family | measured |
| §4.4 | `H1` never routed | `routing_report.json`, `entropy.n_heldout: 0` | measured |
| Table 1, control row | absolute `tuned_L0` .494/.369/.460/.500/.434/.489/.400 | `.cache/cells2.csv`, `system == tuned_L0`, Grid B | measured |
| Table 1, `H1` column for `router` / `dl_rescaled` | — | **not run**; `H1` budget exhausted (§4 below) | **pending** |
| §5.3 | `merge_dare_linear` 53.5 % format-fail py | `.cache/cells2.csv` | measured |
| §5.3 | `dl_rescaled` − `merge_dare_linear` = +41.6 [+33.9,+49.9] pooled | `11_rq2_contrasts.py` pooled delta | measured |
| §5.4 | 27 candidates span 0.4434–0.4506; each round's winner −0.7 to −1.0 vs `merge_dare_ties`, all p>0.4 | `.cache/cells2.csv`, `system` matching `^mo_r\d_` | measured |
| §6.1 | Frobenius identity verified to 5.6e-16 | `log/modularity/2026-08-10_overtraining-and-merge-geometry.md` | measured |
| §6.2, Table 2 | both banks, all four quantities | `results/merge_geometry/*.json`, `epochs` + `verdict` | measured |
| §6.3 | e9−e1 = +3.1 [+0.0,+6.1] dare_ties, +1.6 [−0.4,+3.5] ties; e9 vs control +0.5, e1 −2.6 | `11_rq2_contrasts.py` pooled deltas | measured |
| §6.3 | 11 of 12 method×condition pairs improve | `.cache/cells2.csv`, `overtrain_full_*` | measured |
| §6.3 | `merge_ties` ‖ΔW‖ 0.19× a single expert's | `log/modularity/README.md` "What didn't" | measured, **unexplained** |
| §7.1 | gate 2,766,876 params vs 295,436,288 frozen bank (0.0094) | `log/modularity/2026-08-11_routerlora-build-and-composite-purity.md` | measured |
| §7.3 | mixture vs base +8 to +28; router−uniform +0.6…+7.4 on 8/8; pooled +3.3 [−0.4,+7.5] composites, +2.9 [−0.0,+6.2] p=0.059 all-8 | `11_rq2_contrasts.py` MoLE families | measured |
| §7.4 | `mole_random` ≡ `mole_uniform` on all 1299 items | `.cache/trials_all.parquet`; confirmed against source, see §5 | measured |
| §8 | ckpt epochs 1/1/2/2/3/3/3/3 by condition | `MASTER_REPORT` §5.3, to be re-derived from adapter dirs | **to re-verify** |
| §8 | `H1` access log: 3 pilot + 88 final reads over 4 sittings | `data/quarantine/h1/ACCESS_LOG.md` | measured |
| §9 Table 3 | costs and gates | `configs/mole/routerlora_v1.yaml`, `configs/merge/ties_v1.yaml`, `docs/RESULTS_BOOK_2026-08-11.md` gates | design, not result |
| §10 | seed noise 0.6 py / 2.0 js pts | `MASTER_REPORT` §3.7 (Grid A, larger n) | measured elsewhere |

## 4. Discrepancies found and resolved

Recorded so the correction is auditable. In every case the result file won.

1. **Router best epoch.** `MASTER_REPORT` §5.1 reports "Best epoch: 1" beside the Python
   validation accuracy. The files give `router_best_epoch: 7` for **Python** and `1` for
   **JavaScript** — the report quoted the JavaScript epoch alongside the Python accuracy.
   The paper cites neither (the epoch is not load-bearing); recorded here so the report can be
   corrected.
2. **Composite acceptance count.** `MASTER_REPORT` §5.4 says 1656/2231 (74 %);
   `log/modularity/2026-08-11_…md` says 1658/2231 (74.3 %). Not yet recounted from the corpus;
   the paper cites neither number. **Open.**
3. **The task-vector geometry table in `MASTER_REPORT` §5.3 is superseded.** It reports the
   overtrain probe as *three* experts (sign conflict 0.336 → 0.355, ‖ΔW‖ 0.286 → 0.602). The
   file on disk (`adapters_overtrain_*.json`, written 2026-08-12 17:53, i.e. after the report)
   covers **eight** conditions and gives 0.4011 → 0.4254 and 0.291 → 0.617. Table 2 of the paper
   uses the file. **This removes the report's own "3 experts vs 6–8" caveat** — both banks now
   contain the same eight conditions.
4. **`MASTER_REPORT` §8.2 — "Grid B has no control in Python" — is out of date.** `tuned_L0`
   and `base` cells exist on the test-set grid (from `grid_s3s4_qwen1.5b`), which is what makes
   Table 1 of this paper quantitative in Python. Verified by program-set intersection: 40
   programs shared with every merge arm.

## 5. The one number that is a bug report, not a result

§7.4's claim that `mole_random` is inert was established three ways, all recorded here because
it is the finding that blocks the paper's thesis:

1. **Outputs.** `mole_random` and `mole_uniform` have identical `correct` vectors over all
   1,299 shared items (0 disagreements) and identical raw generated strings on inspection.
2. **Mechanism.** `src/obtune/mole/eval_mole.py::_load_gate` implements `mole_random` as
   `for p_ in holder.gate.parameters(): if p_.dim() > 1: init.normal_(...)`. The ladder in
   `configs/eval/mole_ladder_qwen1.5b.yaml` runs `mole_uniform` **before** `mole_random`, and
   `mole_uniform` replaces `holder.gate` with a `ConstantGate` whose routing vector `w` is a
   registered **buffer**, not a parameter.
3. **Direct check** (CPU, no GPU):

   ```
   ConstantGate n_parameters: 0
   buffers: ['w']
   weights after the mole_random re-init loop: [0.125] * 8
   ```

The `mole_router` branch immediately below guards against exactly this ordering hazard, with a
comment stating that arms must not depend on the order they run in. The control branch was not
given the same guard.

## 6. What is deliberately NOT in the draft

- **Any `H1` number for an arm built after 2026-08-09.** The quarantine budget is spent
  (§8 of the paper). `\pending` in that column is a statement about the protocol, not about the
  arm, and must not be filled by running a third pass without declaring it.
- **The JavaScript merge/router deltas.** They exist and point the same way, but the JS test-set
  grid is 30 programs and the seed-noise floor there is ~4 points. Adding them would widen the
  paper without strengthening any claim. Reconsider once item 1 of §9 (second seed) lands.
- **Any claim that the learned gate beats the uniform mixture.** The effect is +2.9 points at
  p=0.059 with no cell surviving FDR, and its decisive control is inert. §7.3 reports the
  numbers and declines the claim.
- **Any comparison between the two evaluation grids.** They are disjoint in programs.
