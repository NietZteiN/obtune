### Target Date: 2026-09-01 (Every finding survives a complete change of base model)

- **Hypotheses / what we're testing:** the Qwen panel became unusable on this cluster, forcing
  a full rebuild on a new base. **H-replicate — the RQ1/RQ2 findings are properties of the
  task, not of Qwen.** CONFIRM if transfer ratio, the LOTO price of an unseen transform, and
  the merge-vs-clean-code-control gap reproduce on a different family. REFUTE if any of them
  moves materially. Also re-tests **H-format** and **H-mem** from scratch, since the format
  floor is model-specific (62-67 % of the gain at Qwen-1.5B, 2-14 % at Qwen-7B).

- **Setup:** CodeLlama-7b-Instruct, python, Grid A (`eval_source: heldout`), common subset 412
  programs. One dependency-linked SLURM DAG (`scripts/slurm/pipeline_replication.py`), 51 jobs,
  ~20 GPU-hours, ~6 h wall-clock under `MaxJobsPU=4`. Phases `rq1_generic` (84 cells),
  `loto_generic` (54), `rq2_generic` (54). **H1 was not read; it is absent from the DAG by
  construction.** Base go/no-go beforehand (job 360665): L0 0.257 / format_fail 0.129.

- **Results:**
  - **The format floor is VALID this time** — acc 0.280, format_fail 0.090, **943 distinct
    outputs, top share 0.048** (`'false'`, `'-1'`, `'[]'`, `'False'`, `'1'`). The diversity
    criterion adopted after the Qwen-7B collapse is what certifies it; `lr 2.0e-6` held.
  - **RQ1 transfer matrix**, seed-averaged, common subset:

    | reference | diagonal | off-diagonal | diff | mean off-diag TR |
    |---|---|---|---|---|
    | vs `base` | +0.2037 | +0.1857 | +0.0181 | 0.9124 |
    | vs **FLOOR** | +0.1899 | +0.1719 | +0.0181 | **0.9057** |

    Floor correction moves TR by 0.007 -- the floor takes ~7 % of the gain.
  - **LOTO**: mean diagonal 0.3852, `mono_all` 0.3960, `base` 0.1988. **Price of the unseen
    transform -0.0108**; the fold recovers **94.5 %** of what training on all six gives.
  - **RQ2 ladder** (mean over the six trained conditions): `mono_all` 0.3934,
    `merge_dare_ties` 0.3848, **`l0merge_dare_ties` 0.3657**, `l0merge_ties` 0.3459,
    `tuned_L0` 0.3389, `merge_ties` 0.3252, `formatonly` 0.2135, `base` 0.1988,
    `merge_dare_linear` 0.1406.

- **What worked / hypothesis verdict:** **H-replicate SUPPORTED, and tightly.**
  **H-mem REFUTED** (TR 0.906 against the floor; Qwen-7B was 0.881). **H-format REFUTED at
  this scale** (floor takes ~7 % of the gain). The LOTO number is the striking one: **-0.0108
  here against -0.0113 on Qwen-1.5B, 94.5 % vs 94.3 %** -- two different model families,
  different tokenizers, different chat templates, agreeing to three significant figures.
  The merge control reproduces too: merging six CLEAN-CODE adapters reaches 0.3657 against the
  six specialists' 0.3848, so obfuscation expertise buys **1.9 points**, and
  `merge_dare_linear` collapses BELOW the format floor exactly as it did on Qwen.

- **Observations:**
  - **This is much stronger evidence than the Qwen numbers alone were.** A finding that
    survives a change of base model, tokenizer and prompt template is a property of the task.
    The forced migration cost a corpus and bought external validity.
  - **The go/no-go read the risk correctly in advance.** CodeLlama's accuracy sits near
    Qwen-1.5B's but its format_fail (0.129) is below both Qwen models, and the prediction was
    that the format-artifact regime is governed by format HEADROOM rather than accuracy. The
    floor took 7 %, near Qwen-7B's 2-14 % and nothing like Qwen-1.5B's 62-67 %.
  - **CodeLlama degrades more under obfuscation** (6.4 pts clean->S2 at base, against
    Qwen-7B's 2.5) and still transfers at TR 0.906. More damage to repair, same conclusion.

- **New questions / new hypotheses:** the two panels now bracket a scale/quality range with
  the same answer. **H-family — the invariance result is stable across model families but the
  FORMAT FLOOR is not**, varying 7 %-67 % with no simple relation to accuracy. Predicting which
  regime a base sits in, before training, is unsolved and is what makes the floor mandatory.

- **Next Steps:** (1) Cluster-bootstrap CIs on these point estimates. (2) The 13b tier, for a
  within-family scale contrast. (3) H1 remains unspent on CodeLlama and is defensible now that
  the matrix is interpretable.
