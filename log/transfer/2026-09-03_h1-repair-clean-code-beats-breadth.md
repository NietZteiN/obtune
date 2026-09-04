### Target Date: 2026-09-03 (H1 repair read — the clean-code adapter BEATS `mono_all` on the unseen obfuscator, and the control column collapses the RQ2 ladder)

> Follows [`2026-09-03_prefix-cache-collision.md`](2026-09-03_prefix-cache-collision.md). Supersedes
> the `tuned_L0` rows of [`2026-09-02_h1-codellama-pilot.md`](2026-09-02_h1-codellama-pilot.md),
> the RQ2 control column and §12 fractions of
> [`2026-09-02_codellama-master-report-tranches.md`](2026-09-02_codellama-master-report-tranches.md),
> and the withdrawn `tuned_L0 − mono_all` interval of
> [`2026-09-03_cis-and-three-corrections.md`](2026-09-03_cis-and-three-corrections.md).

- **Quarantine accounting.** ONE cell (`tuned_L0 × H1`, n=1214, 405 programs) re-read as a
  repair of the 2026-09-02 `pilot_eval` pass, authorized by the human on 2026-09-03 after the
  contaminated cell was shown never to have measured the adapter. Job 376050, `--systems
  tuned_L0`, `purpose=pilot_eval`; `ACCESS_LOG.md` carries the rationale above its row. Nothing
  was trained, selected or tuned between the pilot and the repair. **`final_eval` remains
  unspent.** The contaminated cell is preserved under `results/cells/_contaminated_2026-09-03/`.

- **Setup:** unchanged from the pilot — same 11 comparison cells, same items, Grid A. Twelve
  non-H1 `tuned_L0` cells (`rq2_generic`, `baselines_generic`) were re-run in the same fix and
  verified against the clean `rq1_generic` reference: within 0.5 pt on every condition, 96–97 %
  raw-output agreement (the LOTO job's cells sat at 96–98 %). Cluster bootstrap by program,
  B=2000, seed 17, throughout.

- **Results — H1:**

  | system | acc | format_fail |
  |---|---|---|
  | `tuned_S2` | 0.2834 | 0.027 |
  | `tuned_S1` | 0.2776 | 0.035 |
  | `merge_dare_ties` | 0.2768 | 0.026 |
  | **`tuned_L0`** | **0.2735** (was 0.2381 contaminated) | 0.029 (was 0.035) |
  | `tuned_L2` | 0.2661 | 0.030 |
  | `l0merge_dare_ties` | 0.2619 | 0.030 |
  | `tuned_L1b` / `tuned_L1r` | 0.2570 / 0.2521 | 0.030 / 0.028 |
  | `mono_all` | 0.2323 | 0.010 |
  | `merge_ties` | 0.2241 | 0.040 |
  | `formatonly` / `base` | 0.1334 / 0.1285 | 0.170 / 0.185 |

  | contrast | estimate [95 % CI] |
  |---|---|
  | **`tuned_L0 − mono_all`** | **+0.0412 [+0.0181, +0.0643]** |
  | `tuned_L0 − merge_dare_ties` | −0.0033 [−0.0189, +0.0116] |
  | `tuned_L0 − tuned_S2` | −0.0099 [−0.0280, +0.0091] |
  | `tuned_L0 − tuned_S1` | −0.0041 [−0.0206, +0.0124] |
  | `tuned_L0 − tuned_L2` | +0.0074 [−0.0074, +0.0215] |
  | `tuned_L0 − l0merge_dare_ties` | +0.0115 [−0.0058, +0.0288] |
  | `tuned_L0 − formatonly` | +0.1400 [+0.1128, +0.1680] |

- **Results — the trainable grid, with the clean control (Grid A common subset, n=412
  programs, mean over the six trainable conditions):**

  | system | acc | − `tuned_L0` |
  |---|---|---|
  | `tuned_L0` | 0.3922 | — |
  | `mono_all` | 0.3934 | +0.0012 [−0.0152, +0.0170] |
  | `merge_dare_ties` | 0.3848 | −0.0074 [−0.0159, +0.0009] |
  | `l0merge_dare_ties` | 0.3657 | −0.0265 [−0.0365, −0.0169] |
  | `l0merge_ties` | 0.3459 | −0.0463 [−0.0589, −0.0348] |
  | `merge_ties` | 0.3252 | −0.0669 [−0.0821, −0.0525] |
  | `merge_dare_linear` | 0.1406 | −0.2516 [−0.2768, −0.2264] |

  §12 baselines against the floor (`tuned_L0 − formatonly` = 0.1800 is fine-tuning's gain):
  `icl_k4_cross` +0.0660 [+0.0481, +0.0833] = **0.37** of it (the pilot said "about half");
  `icl_k1_cross` 0.27; `icl_k1_clean` 0.23; `oracle_prompt_1shot` +0.0042 [−0.0102, +0.0182]
  = 0.02; `norm_full` −0.0177 [−0.0266, −0.0092] and `norm_structural` −0.0082 [−0.0149,
  −0.0022] are BELOW the floor.

- **What this means / hypothesis verdict:**
  1. **The project's central claim is confirmed on CodeLlama with an interval, and it is
     stronger than the Qwen master report stated.** An adapter trained ONLY on clean code beats
     the adapter trained on all six obfuscations, on an obfuscator neither saw, by 4.1 points
     with a CI that clears zero by 1.8. On Qwen the verb was "matches"; here it is "beats".
     Breadth of obfuscation exposure did not buy transfer to the seventh transform — it cost it.
  2. **On H1, `tuned_L0` is indistinguishable from the best specialist and the best merge.**
     Every obfuscation-trained system in the panel lands within noise of an adapter that never
     saw obfuscated code, except `mono_all` (below it) and `merge_ties` (below it). The
     specialist-vs-merge ordering that H-closest-specialist was built on is noise
     (`2026-09-03_cis-and-three-corrections.md`); the ordering that is NOT noise is
     `{every tuned system} > mono_all`.
  3. **On the trainable grid the RQ2 ladder collapses onto the control.** `mono_all` ties
     `tuned_L0` (+0.001); the best merge is 0.7 pts BELOW it with an interval that touches
     zero; every other merge is significantly below it. The deflated control had made the
     merges look like they were adding something. They add nothing over training on clean code.
     This is the same statement as (1), made on conditions the systems DID train on.
  4. **`mono_all`'s signature is now legible:** lowest format_fail of anything (0.010 on H1)
     and the lowest accuracy of any tuned system. Breadth taught the output format thoroughly
     and the task no better than clean code did — a mild form of the memorization the paper
     is looking for, in the system that had the most transforms to memorize.
  5. **§12 direction survives, magnitude does not:** ICL is real (+0.066, CI well clear) but
     recovers ~a third of tuning's gain, not half; oracle prompting recovers nothing;
     normalization hurts.

- **What didn't / caveats:** single seed (`s17`) for every H1 row; `mono_all` s42 and s101 are
  training (375907/375909) and will be evaluated on the trainable grid to bound seed variance
  on contrast (3), but their H1 rows wait for `final_eval`. The claim in (1) rests on one
  program-clustered interval at n=405 programs; it is the pre-registered prediction, read once,
  and it is what the final pass exists to confirm.

- **Next steps:** finish the seed panel on the trainable grid; recompute the `MASTER_REPORT`
  CodeLlama tables from the clean cells (the RQ2 control column and §12 fractions in
  `2026-09-02_codellama-master-report-tranches.md` are superseded by this entry); the
  alignment-arm teacher question is now moot — `tuned_L0` IS the ceiling on H1, so there is
  no stronger clean-code teacher to try.
