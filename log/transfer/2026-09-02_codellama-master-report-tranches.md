### Target Date: 2026-09-02 (The rest of the master report on CodeLlama — and routing dies completely)

> Continues [`2026-09-01_codellama-replication.md`](2026-09-01_codellama-replication.md), which
> covered RQ1, the format floor, LOTO and the core RQ2 merges. This is everything else.

- **Hypotheses / what we're testing:** do the report's remaining arms reproduce on a new base?
  **§12 zero-training baselines** (ICL, oracle prompting, normalization), **§5 routing/MoLE**,
  **§4 rank sweep**, **§14 merge density**, **§15 RQ3 attention**, **§4 forgetting**, and the
  S2-family conditions. All Grid A, common subset 412 programs, **H1 unread throughout**.

- **Setup:** three dependency-linked DAG drivers (`pipeline_tranches.py`, `pipeline_rq3.py`,
  plus the earlier replication driver), ~45 jobs. Everything read against the **format floor**,
  not `base`.

- **Results:**
  - **§12 zero-training baselines.** `tuned_L0` 0.3409; ICL `k4_cross` 0.2784, `k1_cross`
    0.2602, `k1_clean` 0.2536; `oracle_prompt_1shot` 0.2166; **floor 0.2124**;
    `norm_structural` 0.2042; `base` 0.1988; `norm_full` 0.1947.
  - **§5 routing / MoLE ladder** (Grid A): `mole_random` **0.4016**, `mole_router` **0.4016**,
    `mole_uniform` 0.4013, `mole_hardrouter` 0.4008, `base` 0.1965.
  - **§4 rank sweep**: `mono_r64` 0.3954, `mono_all` (r32) 0.3935, `mono_r192` 0.3926,
    `ctl_r64` 0.3906, `mono_r128` 0.3883.
  - **§14 merge density**: `sweep_dare_ties_d0p3` 0.3970 > `merge_dare_ties` 0.3848 >
    **`l0merge_dare_ties` 0.3665** > `sweep_dare_ties_d0p7` 0.3453 > `sweep_ties_*` ~0.32.
  - **S2 family**: `s2fam` 0.3984, `tuned_S3` 0.3973, `tuned_S2` 0.3943, `tuned_S4` 0.3933.
  - **§15 RQ3 identifier knockout** (Δlogp, clean − knockout; positive = removing identifier
    attention HELPS), 150 items, layers [4,10,16,21,25,30]:

    | cond | base | tuned | keys knocked |
    |---|---|---|---|
    | S2 | **+0.1613** | **+0.0165** | 147.6 |
    | S1 | +0.0233 | +0.0048 | 6.1 |
    | L1b | −0.0008 | −0.0093 | 14.0 |

  - **§4 forgetting**: HumanEval+ ran for `base`, `tuned_L0`, `mono_all` (164 tasks each).

- **What worked / hypothesis verdict:** the arms reproduce, and **routing collapses further
  than it did on Qwen**.
  - **ROUTING IS WORTH NOTHING.** The learned router and the RANDOM gate agree to four
    decimals (0.4016 vs 0.4016) and the whole ladder spans **0.0008**. Mixing eight experts is
    worth **+0.205** over base; *how* they are mixed is worth zero. On Qwen the router beat
    uniform by 0.032 on trained conditions and 0.009 on H1 — here even that is gone. This is
    "models know how but not when" in its strongest form, and it is only sayable because the
    uniform and random controls were run beside it.
  - **CAPACITY IS NOT THE REASON BREADTH DOES NOT HELP** (§4 answered). Ranks 32→192 span
    **0.007**, and the single-condition control at the wider rank (`ctl_r64` 0.3906) sits
    inside that spread.
  - **RQ3 reproduces the mechanism prediction.** Knocking identifier attention out helps the
    BASE model on `S2` by +0.161 and the tuned model by only +0.017 — an order of magnitude
    less. The tuned model has already moved off identifier tokens, so there is far less left
    to remove. The effect tracks how much inert identifier material a condition adds (147.6
    keys on `S2` vs 14.0 on `L1b`, where the effect is null in both systems).

- **Observations:**
  - **Two arms sit AT OR BELOW the format floor**: `oracle_prompt_1shot` (0.2166 vs floor
    0.2124) and both normalization arms, with `norm_full` (0.1947) **below `base`**. Reported
    against `base` these read as small positive effects; against the floor they are nothing.
    This is the first time the floor has changed a sign in this project.
  - **ICL is real but is not tuning.** The best ICL arm recovers 0.066 over the floor against
    fine-tuning's 0.129 — about half. §9 called the matched-condition ICL baseline "the
    comparison a reviewer will ask for"; it now exists, on a model, for the first time.
  - **The merge density sweep inverts the Qwen ordering on trained conditions** (`d0p3` now
    beats the default `d0p5`), which is exactly the case §14 warns about: on Qwen `d0p3` won
    here and LOST on the held-out obfuscator. Density must be selected against the LOTO
    diagonal, never against this table.
  - **A completed job produced an invalid result and nearly went into this entry.** The first
    MoLE eval ran on **Grid B** (`testset`, n=145–176) because the config left `eval_source`
    unset and `data.DEFAULT_EVAL_SOURCE` is `testset` — while every other arm here is Grid A
    (n≈1600). `CLAUDE.md` forbids pooling them. It exited 0 with 30 plausible cells; the only
    tell was the sample size. On Grid B `mole_router` looked **+0.023** over `mole_uniform` on
    `S2` (0.489 vs 0.466); on Grid A that gap is **+0.006** and vanishes in the mean — the
    wrong grid would have supported a routing claim the right grid refutes. Cell paths key on
    (phase, system, condition) and NOT on grid, so a corrected re-run silently RESUMES the
    wrong cells; the Grid B set was moved to `results/cells/mole_generic_testset` rather than
    deleted, and the config now sets `eval_source: heldout` explicitly.

- **New questions / new hypotheses:** **H-mixture — the gain from an expert mixture is a
  capacity/ensembling effect, not a dispatch effect.** Predicts that mixing N experts with a
  fixed uniform gate tracks mixing N adapters of any kind, including clean-code ones. The
  `l0merge` control already points this way for merging; the uniform/random tie points the
  same way for routing.

- **Next Steps:** (1) Cluster-bootstrap CIs on these point estimates. (2) The steering
  summaries parse differently from the knockout ones and were not tabulated here. (3) H1
  remains unspent on CodeLlama.
