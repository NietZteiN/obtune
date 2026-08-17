### Target Date: 2026-08-14 (LOTO, the merge controls, and a continuous pipeline on 2 GPUs)

- **Hypotheses / what we're testing:** Setup + infrastructure day whose purpose is to make a
  class of question *answerable*. The framing question was "`tuned_L0_k0` looks best — should we
  train the router and merger harder?", and the answer reshaped the work:
  - **H1 (read of the §2.2 Grid B table):** `tuned_L0_k0` is the best system. **REFUTED** by
    inspection — it tops 2 of 7 columns (`L0`, and `H1` tied) and is mid-pack elsewhere, clearly
    beaten on `L1b` (.386 vs `tuned_L2` .477), `L2`, `S1`, `S2`. The pattern is the thesis:
    systems win on the conditions they trained for; the clean-code control wins on clean code and
    on the held-out obfuscator.
  - **H2 (the methodological blocker):** the reason "optimise for OOD" keeps colliding with §3.2
    rule 2 is that the project has exactly ONE OOD condition and it is the test set — there is no
    OOD *dev* set to select against. Queued LOTO to fix that.
  - **H3:** the Grid A resume-aliasing defect is confined to the `baselines` phase.
    **REFUTED** — see Observations. It is older and wider, and it is the actual cause of §8.2.

- **Setup:** Host `csr-94608`, GPUs 0+1 (gpu2 taken by the borrower's `nla-mi`
  `src.steer_run --max-hours 11` at 10:47; gpu3 still theirs). `gpu_budget: 2`, unchanged.
  Pipeline launched detached:

  ```
  setsid nohup bash scripts/pipeline.sh > runs/logs/pipeline.log 2>&1 < /dev/null &
  ```

  Test suite 652 passed / 0 failed; `preflight` 0 errors, 10 warnings. Seed 17 throughout;
  the third L0 adapter is seed 101 by design.

  New code and configs:

  | path | what |
  |---|---|
  | `eval_vllm._assert_resume_same_grid` + `GridCollisionError` | runtime guard: resuming a cell across grids is now a hard error, not a silent skip |
  | `eval_vllm` meta | records `eval_source` on every cell (absent before today) |
  | `schema.TrialRow.phase` | `baselines_gridA` added |
  | `preflight.check_cell_path_grid_collisions` | static pass over every eval config, aggregated one line per collision group |
  | `merge_adapters.base_condition` | `L0__s101` → `L0`, so N same-condition adapters can be merged; the H1 guard still validates the real condition |
  | `launch_workers.sh` | now honours `scheduler_policy.gpu_budget` (it never did) |
  | `configs/train/loto_qwen1.5b_py_hold{L0,L1b,L1r,L2,S1,S2}.yaml` | the six LOTO folds |
  | `configs/eval/loto_qwen1.5b.yaml` | the 6×6 fold matrix, no H1 by design |
  | `configs/train/l0seed_qwen1.5b_py_s101.yaml`, `configs/merge/l0_control.yaml`, `scripts/merge/23_l0_control.py`, `configs/eval/l0_merge_control_qwen1.5b.yaml` | the L0-merge control |
  | `configs/merge/ties_s42.yaml`, `configs/eval/merge_headroom_qwen1.5b.yaml` | density sweep + seed-42 replicate |
  | `configs/eval/tuned_L0_gridB_s3s4_qwen1.5b.yaml` | the 2-cell remainder of "tuned_L0 on Grid B" |

  Eight new pipeline stages, ordered gate-first: `gridA_refill`, `gridB_s3s4`, `l0ctl_train`,
  `l0ctl_merge`, `l0ctl_eval`, `loto_train`, `loto_eval`, `merge_headroom_build`,
  `merge_headroom_eval`.

- **Results:** Infrastructure, not measurements. What is established:
  - 1,142 existing cells backfilled with `eval_source`, inferred from `snippet_id` shape (never
    from the `dataset` column). Census: `main` 691 testset / 238 heldout, `baselines` 127
    testset, `baselines_gridA` 51 heldout, `pilot` 35 testset.
  - 51 genuinely-Grid-A cells **migrated** from `baselines` to `baselines_gridA` rather than
    regenerated: several are H1 and each would have cost a quarantine access to reproduce a
    number already on disk. Accuracy verified unchanged (`tuned_L0__L0` 0.449701 before and
    after); `phase_migrated` records the original label.
  - `launch_workers.sh` budget cap verified by inducing the failure: with 2 live workers it now
    prints `gpu2: at gpu_budget (2) — not started` instead of starting a third.
  - Pipeline live at 10:41; `gridArefill` for both models running on GPUs 0 and 1 within 90 s.

- **What worked / hypothesis verdict:** H1 refuted (see above), H2 acted on rather than tested,
  H3 refuted. The stub gate earned its keep twice: it caught `arch: merge` not being a member of
  the `adapter_arch` enum in two configs, before either reached a GPU.

- **Observations:**

  **The aliasing defect is older and wider than §12.1 said, and it explains §8.2.** The new
  static check fires on `main/qwen25c-1.5b/python/base__{L0,L1b,L1r,L2,S1,S2}`: `grid_rq1` and
  `mono_gate` write those cells as `heldout` (n=1670), while every merge, mixture and overtrain
  config requests them as `testset` (n=176) and was silently resumed into the heldout cells. So
  "§8.2 Grid B has no control in Python" was never an oversight — it is the same defect, one
  phase over, and it has been there since the merge arms were first run. The Grid B `base` cells
  do exist; they are in `baselines/`, which no §5 analysis reads.

  **`phase` is being asked to be a general output namespace and it is not one.** Three incidents
  now (2026-08-13 phase-level, 2026-08-14 eval_source-level, and this pre-existing `main` case)
  share one root cause: `cell_dir` keys on `phase` alone. The durable fix is `eval_source` in the
  cell path or the resume key. Today's guard makes the failure loud instead of silent, which is
  the important half, but the path fix is still owed.

  **Why the static check WARNs rather than ERRORs.** Erroring would block every pipeline run on
  debt that predates the check, including the `main` collisions above. The runtime guard
  hard-fails on the thing that actually corrupts a result — resuming across grids — so the static
  pass is there to keep the debt visible and to catch a *new* collision while it is still a config
  edit. Both directions are needed; neither alone is sufficient.

  **The budget cap was load-bearing within four minutes.** `ensure_infra` calls
  `launch_workers.sh` on every poll, and that script filtered by `allowed_gpus` but not by
  `gpu_budget` — so with `[0,1,2]` and budget 2 it started three workers and would have restarted
  a manually-stopped one on the next poll. CLAUDE.md §1 already asserted the script honoured the
  budget; it did not. Twelve minutes after the cap went in, the borrower took GPU 2 for an
  11-hour job. The worker's own idle check would also have refused, but relying on that is relying
  on the last line of defence.

  **Counting live workers only among the candidate list is the subtle version of the same bug.**
  A worker that is *busy* makes its GPU non-idle, so auto-detect drops that card — counting
  within the candidates therefore saw zero live workers exactly when the budget was fully spent.
  Fixed to count every `workers/*.pid`.

  **On "optimise for H1".** The instinct is right and the mechanism is not: `H1` is the only
  evidence separating invariance from memorization, so selecting on it turns every downstream
  `H1` number into training accuracy. LOTO gives the same signal — train on many, test on unseen —
  from trainable data only, at zero quarantine cost. Recorded as §12.7 with a three-tier design
  (trainable / OOD-dev / OOD-test) and the honest note that `H1` is already partly burned, so
  promoting it to dev and minting a fresh frozen family is a legitimate option once `H2` exists.

- **New questions / new hypotheses:**
  - **Does the L0-merge control reach ~.348 on H1?** If yes, merging regresses toward the
    clean-code model and §5 must be rewritten; if no, the gap is the specialists' contribution.
    This gates items 2–4 of §12.6, which is why it is ordered first in the pipeline.
  - **Does the LOTO diagonal predict H1?** If the 6-fold mean correlates with H1 across systems,
    it is a valid surrogate and every future sweep can use it. If not, that is itself a finding
    about how unlike the trainable ladder `H1` is.
  - **Is the 3-seed L0-merge a fair control for a 6-expert merge?** Expert count is a live
    confound. The matched version needs a 3-expert *specialist* merge, which does not exist.

- **Next Steps:**
  1. Read out `gridA_refill` — in particular whether the 7B Grid A panel now has its floor.
  2. `l0ctl_eval` is the decision point; read it before spending anything on merge tuning.
  3. Put `eval_source` in the cell path (or the resume key) and retire the `phase`-as-namespace
     pattern. Until then §8.2 stays open even though its cells exist.
  4. A regression test for the `launch_workers.sh` budget cap — not written, because exercising
     it spawns real workers; it needs a dry-run flag first.
  5. `H2` (virtualization) is the next OOD family; the `H1` promotion decision waits on it.

---

## Addendum — the gate reports, read for the first time (2026-08-14, evening)

`gate_report.json` has been written per cell since the mixture ladder first ran and had never been
analysed. `scripts/analysis/22_gate_routing_report.py` now does;
`results/analysis/gate_routing.json` is the artifact. Full write-up in MASTER_REPORT §12.8–12.9.

**The gate is input-independent.** Total-variation distance between each of the 9 conditions'
expert-mass profiles and the grand mean is **0.011–0.056**. Every input yields one fixed blend:
~.38 `L2`, ~.24 each `S2`/`S4`, ~.11 `L1b`, and near-zero on `L1r`, `S1`, `S3`, `L0` — three of
eight experts are dead regardless of input. On the `L1r` cell the `L1r` expert gets **.003**, 38x
*below* uniform; on `S1`, the `S1` expert gets .013. It does not merely fail to specialise, it
avoids the matching expert.

**Composites do not decompose.** Mass on the experts whose transforms are present, chance = .250:
`C_L1r_S1` **.019**, `C_S1_L1r` **.016**, `C_L1r_S3` **.004**, `C_L1b_S1` .149, `C_S4_S3` .290,
`C_L2_S4` **.605**. Order has no effect (`C_L1r_S1` vs `C_S1_L1r` differ by .003).

**`C_L2_S4` is a trap and nearly produced a false positive.** At .605 it reads as compositional
routing. It is not: `L2` and `S4` are exactly the two experts the gate favours on *every* input,
including `H1`. The discriminating arm is `C_L1r_S1`, whose relevant experts the gate never uses —
.019. Reading the strongest-looking row alone would have supported the opposite conclusion. Worth
generalising: in a table where one row can be explained by a fixed preference, the informative row
is the one where the preference and the hypothesis disagree.

**Cause, and it is not subtle.** `train_mole.py` steps `loss = holder.model(**batch).loss` and
nothing else — no load-balancing term, no entropy regulariser, no routing supervision (grep for
`load_balanc|aux_loss|z_loss|importance` over `src/obtune/mole/` and `configs/mole/` returns
nothing). Collapse is the *expected* optimum of that objective: a constant blend minimises average
loss and nothing rewards varying with the input. Switch Transformer and GShard both add an
auxiliary balancing loss for exactly this reason. Learned temperature confirms the picture — tau
fell to .39–.51 uniformly across all 28 layers from an init of 1.0, i.e. the gate learned to be
*more confident* about a preference that does not depend on its input.

**This explains two earlier results rather than adding a third.** §12.4's `mole_hardrouter` ≈
`mole_router` follows immediately (hardening cannot change which expert wins if the output barely
depends on the input), and so does the vanishing of the router's advantage on `H1` (the gate emits
the same blend on `H1` as everywhere else, TV = .016, same entropy).

**Limitation that bounds all of the above.** `MoLEModel._captured[layer]` is *overwritten* each
forward, so every report describes the **final batch** of its cell, not all items. The
cross-condition comparison survives — a batch of pure `L1r` items still puts .003 on the `L1r`
expert — but per-condition estimates are noisier than the decimals imply and within-condition
per-item variation is invisible. Overwrite → accumulate is a one-line change giving whole-cell
statistics at zero GPU cost, and it should land before any re-run.

**What may be claimed today:** `mole_router` is a **learned static mixture weight**, not a router.
It beats an untuned uniform blend and is indistinguishable from its own one-hot. Nothing about
routing, mixture-of-experts behaviour, or compositional specialisation may be claimed.

**Next steps** (§12.9 has the full ladder): a linear probe on the gate's input hidden states for
condition identity decides whether this is a *training* failure or a *representation* failure —
which makes the plan file's "Part I Phase 2 (probes + CKA)" the load-bearing next experiment rather
than a side quest. Then a load-balancing loss plus a temperature floor in one retrain (~3 GPU-h),
and routing supervision (one-hot per condition, two-hot per composite) only if compositional
decomposition is to be a headline — stating plainly that a *taught* decomposition is a weaker claim
than a learned one.

---

## Addendum — the overnight run completed 2026-08-15 06:02. Three results, one story.

42/42 stages, **0 skipped**, 224 done, 2 in `failed/` (both the documented false alarms).
~17.5 h wall on 2 GPUs, unattended, no human intervention after launch.

**1. The gate probe settles §12.9's branch: TRAINING failure, not representation failure.**
Linear probe on the decoder-layer input hidden states, 200 programs, program-disjoint split,
train-only standardisation: **99.4 % at layer 4 against 16.7 % chance**, and above 97 % at every
layer sampled. Condition identity is almost perfectly linearly available in exactly what the gate
reads. The v1 gate could have routed and did not.

**2. The balancing fix works — routing became real.** v1 → `routerlora_balanced`:

| | v1 | balanced |
|---|---|---|
| TV distance from grand mean | .011–.056 | **.074–.106** |
| `L1r` expert on the `L1r` cell | .003 | **.080** |
| `S1` expert on the `S1` cell | .013 | **.253** (top expert) |
| `C_L1r_S1` mass on {L1r,S1} (chance .250) | .019 | **.332** |
| `C_L1b_S1` on {L1b,S1} | .149 | **.375** |
| entropy (norm) | .151–.180 | .270–.289 |

The mass now tracks what is actually present: `S1` sits at .243–.253 on every condition
containing S1 and drops to .096–.103 on those without it. Four of six composites reach or exceed
chance. Reports are whole-cell now (2.1–4.4 M tokens each), confirming the capture fix.
Not everything recovered: `S3` stays weak (.042–.055) and `L1r` self-routing (.080) is still
below uniform, so `C_L1r_S3` (.124) and `C_S4_S3` (.237) remain under chance.
`C_L2_S4` FELL .605 → .383 — correctly: v1's .605 was the artifact of L2/S4 being its fixed
favourites, and .383 is the honest number.

**3. And it bought nothing. `mole_router_bal` − `mole_router` = +0.4 pts mean (−1.1 to +1.7),
entirely inside the 1.32/3.61 seed band.** This was pre-registered in
`configs/eval/mole_balanced_qwen1.5b.yaml` as the outcome to watch for, and it is the one that
landed: **routing correctly is worth nothing here.**

**4. LOTO says why.** Diagonal mean **38.0** (adapter scored on a transform it never saw) against
`mono_all` **39.1** (saw all six) and the clean-code control `tuned_L0` **39.0**. Holding out a
transform costs **~1.1 points — inside seed noise** — and neither multi-condition adapter beats an
adapter trained only on clean code.

**The three converge.** The probe proves the transform is identifiable; the balanced gate proves it
can be routed on; the accuracy proves routing on it changes nothing. Together with the L0-merge
control (3 clean-code adapters merged = 6 specialists merged, on H1), the conclusion is not about
gates or merge algorithms at all: **the per-condition experts do not carry distinct transferable
knowledge, so no combination strategy can extract value that is not there.** That is fix 5 of
§12.9's ladder, reached by eliminating 1–4 rather than by assuming it.

**Next:** write this into §12.10; re-scope §5's modularity claim around it; the composite
`C_L1r_S3`/`C_S4_S3` shortfall and `S3`'s weak revival are the only loose threads on the gate side.
