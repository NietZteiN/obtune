### Target Date: 2026-09-10 (four consistency arms were trained by the wrong entry point and are plain SFT; ~20 GPU-hours, and it would have read as a failed replication)
- **Hypotheses / what we're testing:** none — an incident report. The panel's first graded grid
  (`ev_panel_g3`, job 389609) exposed it.
- **Setup:** `panel_core` on gemma3-12b, 5 systems × 7 conditions.
- **Results — the tell, and it was nearly invisible:**

  | system | L0 | L1b | L1r | L2 | S1 | S2 | X1 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | `mono_all` | 0.5072 | 0.4753 | 0.4635 | **0.4713** | 0.4571 | **0.5027** | **0.2628** |
  | `cons_lam3` | 0.5084 | 0.4777 | 0.4629 | **0.4713** | 0.4603 | **0.5027** | **0.2628** |

  Identical accuracy on three of seven conditions. Exact counts: L2 787/787, S2 838/838,
  X1 319/319. The adapters are **not** the same file (different md5) and their raw outputs differ
  on 3–6 % of items, so this is not a duplicated cell; the aggregate counts coincide because the
  two arms are behaviourally ~96 % identical.
- **What worked / hypothesis verdict:** the arms are invalid, not a refutation.
  - **`src/obtune/train_sft.py` contains no reference to `objective` at all.** It loads the config,
    ignores the `objective:` block, and trains plain SFT. The consistency objective lives in
    `obtune.objectives`, whose pipeline invocation is
    `-m obtune.objectives train --config <cfg> --lam 3`. I submitted
    `-m obtune.train_sft --config train/obj_cons_<model>_py.yaml`.
  - **Confirmation from the training logs:** every logged step is
    `{'loss': 0.002…, 'mean_token_accuracy': 0.999…}` with **no `kl_loss`, `task_loss`,
    `kl_rows_ok` or `kl_rows_bad` keys**. `ObjectiveTrainer.log()` injects those on every call, so
    their absence is proof the objective trainer was never constructed — in the solo StarCoder2 job
    as well as the packed one, so it is not a log-interleaving artefact.
  - So all four "cons_lam3" arms are plain SFT over the same six conditions as `mono_all` — the
    same recipe under a different name.
- **Observations:**
  - **Cost: ~20 GPU-hours** (gemma3 5.6 h, starcoder2 4.3 h, codegemma + granite ~3 h each before
    being killed), plus the eval that exposed it.
  - **What it would have become.** R2 was pre-registered hours earlier as *`cons_lam3 − mono_all`
    @ X1, REPLICATED iff ci_lo > 0*. This grid gives **exactly 0.0**. Read at face value it says
    the paper's one positive methodological result does not replicate outside CodeLlama — and the
    pre-registration would have made that reading feel disciplined rather than wrong. The
    pre-registration protects against choosing a rule after seeing the number; it does nothing
    about an arm that is not what its name says.
  - **What actually caught it** was not any guard in the pipeline. The adapter-applied assertion
    passes (the adapters differ from base and from each other), provenance is correct (the manifest
    faithfully records `objective: {mode: consistency, lam: 3.0}` — for a block nothing read), and
    the sha/config checks all pass. It was caught by *two cells reporting the same integer count of
    correct answers*, noticed by eye.
  - **Fourth silent no-op today, and much the most expensive.** The others: a `str.replace` anchored
    on a function that does not exist; a shell validation whose format string bash ate; a QOS flag
    naming a QOS the cluster does not have. Each was a confident operation whose success was never
    checked. This one had a config field that no code path reads.
  - **Fix:** `train_sft.py` now refuses a config declaring `objective:`, naming the right command,
    **before** it claims a GPU. Quarantined rather than deleted: the four adapters are in
    `runs/_invalid_2026-09-10_cons_ran_as_plain_sft/` and the seven affected cells in
    `results/cells/_invalid_2026-09-10_cons_ran_as_plain_sft_cells/` — they are evidence, and they
    are also a usable *unintended* control (plain SFT trained twice under two names).
- **New questions / new hypotheses:** none. Note for the eventual read: the quarantined arms give a
  free estimate of run-to-run variance for `mono_all` under identical data and differing only in
  seed-independent training noise — 96 % output agreement, ±0.3 pts on most conditions.
- **Next Steps:** four arms resubmitted with `-m obtune.objectives train --lam 3` (389676–389679).
  The gemma3 panel grid keeps its other four systems; only the `cons_lam3` row is void and will be
  re-run.
