### Target Date: 2026-09-04 (Master report rev 14 — the report rebuilt on the CodeLlama panel)

> Continues [`2026-08-27_master-report-rev13.md`](2026-08-27_master-report-rev13.md). Rev 13 was
> the last revision written entirely on Qwen-1.5B; everything since 2026-08-28 is a different
> cluster and a different base model, and rev 14 is where that lands in one document.

- **Hypotheses / what we're testing:** organizational — no new experiment. The question is a
  documentation one: can the CodeLlama era be *added* to the existing report rather than replacing
  it, without either (a) leaving Qwen numbers unlabelled so a reader pools two panels, or
  (b) silently re-stating log-entry numbers instead of recomputing them. Failure looks like a table
  whose model is ambiguous, or a number that exists only in a log entry.

- **Setup:**
  - `MASTER_REPORT.md` (written as `docs/MASTER_REPORT_2026-09-04.md`, moved to the repo root under
    a stable filename later the same day) = `cp` of `docs/MASTER_REPORT_2026-08-27.md` (3,827 lines), then
    front matter rewritten, §1 given a *Rewritten 4 Sep* block, §17 retitled
    "Provenance — the Qwen panel", **§18–§25 added** (529 new lines), Contents and Changelog updated.
    Final: 4,482 lines.
  - Numbers recomputed by a new [`scripts/analysis/28_master_panel.py`](../../scripts/analysis/28_master_panel.py)
    → `results/analysis/master_panel_2026-09-04.json`: inventory over every `results/cells/**`
    parquet; system × condition accuracy per phase for both CodeLlama rungs; the same on the
    all-conditions-succeeded **common subset**; `system − tuned_L0` program-cluster bootstraps
    (B=2000, seed 17); and 13B − 7B on the systems present at both scales.
    Campaign and alignment numbers come from `26_campaign_arms.py` / `27_align_arms.py`
    (`campaign_2026-09-03.json`, `campaign_13b_2026-09-04.json`, `align_2026-09-04.json`).
  - Job-level facts (runtimes, checkpoint selections, defect accounts) taken from the eleven log
    entries 2026-08-28 → 09-04 and each adapter's `training_summary.json` / `ckpt_select.json`.

- **Results:**
  - **Corpus recount:** **2,966 cells / 2,200,119 graded trials**, against rev 13's 2,215 /
    1,046,382. Of these the **CodeLlama-7b panel is 525 cells / 792,118 trials**, the **13B rung 18
    cells / 28,746**, and **73 cells are quarantined** (28 `_contaminated_2026-09-03`, 45
    `_misplaced_2026-08-13`) and excluded from every table. Full breakdown in §25.1.
  - **Two bases for the RQ2 ladder, both now published.** Common subset (412 programs), mean over
    the six trainable conditions: `tuned_L0` 0.3922, `mono_all` 0.3934, `merge_dare_ties` 0.3848,
    `l0merge_dare_ties` 0.3657, `l0merge_ties` 0.3459, `merge_ties` 0.3252, `merge_dare_linear`
    0.1406. Unrestricted (557 programs, recomputed here for the first time): 0.3858 / 0.3914 /
    0.3864 / 0.3686 / 0.3510 / 0.3287 / 0.1368. **The unrestricted means run 0.4–0.6 pts lower and
    change exactly one ordering:** `merge_dare_ties` is 0.74 pts BELOW `tuned_L0` on the common
    subset (0.3848 vs 0.3922) and 0.06 pts ABOVE it unrestricted (0.3864 vs 0.3858). The swap sits
    far inside that contrast's interval (−0.0074 [−0.0159, +0.0009]), so nothing is claimed either
    way — but it is a live demonstration that the coverage restriction is not cosmetic. Every other
    pair keeps its order. The common subset stays the headline because CLAUDE.md §4 requires it.
  - **H1 panel re-derived from the parquets and reproduces the 09-03 repair entry to the digit**
    (n=1214, 405 programs): `tuned_S2` 0.2834, `tuned_S1` 0.2776, `merge_dare_ties` 0.2768,
    `tuned_L0` 0.2735, `tuned_L2` 0.2661, `l0merge_dare_ties` 0.2619, `tuned_L1b` 0.2570,
    `tuned_L1r` 0.2521, `mono_all` 0.2323, `merge_ties` 0.2241, `formatonly` 0.1334, `base` 0.1285.
    Format-fail likewise (`mono_all` 0.0099, `base` 0.1853).
  - **13B rung recomputed:** `tuned_L0` L0 0.4689 / L1b 0.3957 / L1r 0.4156 / L2 0.4078 / S1 0.4042 /
    S2 0.4241; `mono_all` 0.4455 / 0.4228 / 0.4192 / 0.4192 / 0.4122 / 0.4439; `base` 0.2521 /
    0.2220 / 0.2251 / 0.2281 / 0.2133 / 0.1842. format_fail 0.0157 / 0.0107 / 0.1018.

- **What worked / hypothesis verdict:** the additive structure worked and the labelling problem is
  the one that needed real work. Three devices carry it: the front matter now states **which model
  each section range is about** and that the Qwen panel is *frozen*; §17 was retitled to name its
  panel rather than being a bare "Provenance"; and §25 is a second provenance section for the new
  era rather than an edit of the old one. The alternative — rewriting §1–§17 in CodeLlama terms —
  was rejected because those cells cannot be re-evaluated on this cluster, so a rewrite would have
  had to either drop them or restate them without provenance.

- **Observations:**
  - **Recomputing found no disagreement with any log entry**, which is the first time that has been
    true of a report revision (rev 13 found 41 duplicate cells disagreeing, 27 by >0.5 pt). The
    reason is structural, not virtuous: the CodeLlama era has one evaluation path (vLLM, one engine
    version) where the Qwen era accumulated three.
  - The only *new* fact the recompute produced is the unrestricted-vs-common-subset gap above. It
    is worth publishing precisely because it is small: the common-subset convention has been
    asserted in this project since the design doc and never quantified.
  - §21 (the defects section) is now the longest new section, and that is the honest weighting —
    the prefix-cache collision changed a headline result's sign-relative-to-noise, and the
    guard that would have caught it is *still not implemented*.

- **New questions / new hypotheses:** none opened here. The report's own §24 carries the open list
  (H-L1b-L0-trade, H-saturation, H-peaked-breadth, H-mixture, H-scale-floor, the canary guard, the
  unspent `final_eval`).

- **Next Steps:** the two alignment arms still training (λ=3 job 377006, λ=0.3 job 377108) land in
  §23.3 as a follow-up edit; §23 already states the control's verdict, which they cannot change.
  If the canary guard is implemented, §21.1's last paragraph needs its "not yet implemented" removed.
