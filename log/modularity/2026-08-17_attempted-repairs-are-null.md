### Target Date: 2026-08-17 (both attempted repairs to the negative result are null)

- **Hypotheses / what we're testing:** §12.10 closed RQ2 negatively by elimination, and its honest
  weakness is that five things were measured and nothing was attempted as a fix. Two fixes, both
  pre-registered in their train configs before any GPU time:
  - **H1 (curriculum).** `S2`→`H1` (§3.5) is the project's one replicated positive transfer and was
    found by accident, on an adapter trained on equal footing with everything else. If the mechanism
    is "learn to ignore code that cannot affect the result", training on the whole inert-material
    family (`S2`+`S3`+`S4`) should widen it. CONFIRM if `s2fam` beats `tuned_L0` outside the
    1.32-pt seed band on the Grid A mean; REFUTE if flat.
  - **H2 (stacking).** Every trainable condition is single-transform; `H1` is not. If unfamiliar
    *combination* of familiar mechanisms is part of the OOD gap, an adapter trained on stacked
    composites should beat one trained on the same six mechanisms unstacked. CONFIRM if
    `composite_trained` − `composite_ablation` > 0 outside noise; REFUTE if <= 0.
  - Registered in advance: `s2fam` carries a 37 % data deficit (14,037 rows is the realised
    S2+S3+S4 train pool, not a chosen cap), so a WIN is interpretable and a LOSS is **not**
    attributable to the curriculum.

- **Setup:** Host `csr-94608`. Six jobs (3 train + 3 ckpt-select) enqueued via
  `scripts/build_manifest.py --train ... --seeds 17`, then a 6-system eval. All 1.5B / Python /
  r32 / α64 / lr 1e-4 / 3 epochs / effective batch 64 / seed 17. Distinct `adapter_root` per arm
  (`runs/adapters_curriculum`, `runs/adapters_composite`) because the adapter dir name encodes only
  (conditions, rank, seed).

  | config | train_conditions | realised n_train |
  |---|---|---|
  | `configs/train/s2fam_qwen1.5b_py.yaml` | S2, S3, S4 | 14,037 |
  | `configs/train/composite_qwen1.5b_py.yaml` (`allow_composites: true`) | 6 × `C_*` | 22,152 |
  | `configs/train/composite_ablation_qwen1.5b_py.yaml` | L1b, L1r, L2, S1, S3, S4 | 22,152 |

  Read out by `configs/eval/curriculum_composite_qwen1.5b.yaml` — Grid A (`heldout`), n=1,667,
  six trainable conditions, **no H1**. Gates before GPU: dataset build, `inspect_batch` PASS on all
  three (prompt tokens −100), `build_manifest --dry-run`, `preflight --queued` 0/0, `make check`
  clean (184,803 train rows, no H1 labels or markers, splits disjoint), 710 tests pass.

  Ran unattended on one card (the borrower held 0/2, later 0/2/3). 11.0 GPU-h of training:
  `s2fam` 7,255.8 s · `composite` 19,059.5 s · `composite_ablation` 13,213.2 s. One attempt each,
  zero failures. Truncation 0.334 % on the composite arm (gate: 1 %).

- **Results:** Grid A, `heldout`, n=1,667, accuracy %:

  | system | L0 | L1b | L1r | L2 | S1 | S2 | mean |
  |---|---|---|---|---|---|---|---|
  | `base` | 21.7 | 18.8 | 18.7 | 19.8 | 20.7 | 15.3 | 19.18 |
  | `tuned_L0` (4,689 rows) | 44.7 | 34.3 | 36.7 | 37.8 | 39.0 | 41.8 | **39.04** |
  | `mono_all` (26,841 rows) | 41.6 | 38.1 | 36.7 | 37.9 | 39.2 | 41.5 | **39.15** |
  | `s2fam` | 44.4 | 32.0 | 36.6 | 36.8 | **41.4** | **43.8** | **39.16** |
  | `composite_trained` | 39.8 | 37.9 | 37.8 | 37.3 | 38.3 | 39.7 | **38.46** |
  | `composite_ablation` | 42.3 | **38.6** | 37.7 | 37.9 | 39.5 | 42.8 | **39.81** |

  Cluster bootstrap by `program_id`, 2000 draws, seed 17:

  | contrast | Δ pts | 95 % CI |
  |---|---|---|
  | stacked − unstacked | **−1.36** | [−2.63, +0.04] |
  | `s2fam` − `tuned_L0` | **+0.02** | [−0.95, +1.02] |
  | `composite_ablation` − `tuned_L0` | +0.77 | [−0.46, +2.03] |
  | `s2fam` − `mono_all` | −0.07 | [−1.39, +1.12] |

  Checkpoint selection (each on its own training conditions' val slice, so **not** mutually
  comparable): `s2fam` epoch 2 at 43.37 %, `composite` epoch 2 at 33.10 %, `ablation` epoch 1 at
  37.98 %.

- **What worked / hypothesis verdict:**
  - **H1 (curriculum) ✗ REFUTED.** `+0.02` pts [−0.95, +1.02] on the clean-code control — flat, and
    the interval is unusually tight rather than underpowered. Training deliberately for the one
    transfer that works buys nothing on the trainable ladder.
  - **H2 (stacking) ✗ REFUTED, and the sign runs against it.** `−1.36` [−2.63, +0.04]: training on
    stacked transforms is if anything *worse* than the same mechanisms unstacked.
  - The pre-registered data-deficit clause does not fire — the result is neither a win nor a loss,
    it is flat.

- **Observations:**

  **Most of these columns are OOD, so these are generalization nulls.** `s2fam` never saw
  L0/L1b/L1r/L2/S1; `composite_trained` never saw *any* single transform. This is not an
  in-distribution readout.

  **The per-condition shape reproduces the thesis exactly.** `s2fam` tops the `S2` column (43.8) and
  the `S1` column (41.4) — the structural family it trained on — and is the *worst* row on `L1b`
  (32.0). Training *for* the mechanism reproduced the mechanism's locality rather than escaping it.

  **`tuned_L0` at 4,689 rows is still indistinguishable from every multi-condition adapter**,
  including `mono_all` at 5.7× the data. Whatever binds this task is neither training-set size nor
  obfuscation exposure. That also answers the `s2fam` volume worry empirically: a 5.7× data
  difference buys 0.11 points, so a 14k-vs-22k gap cannot carry an effect of the size sought.

  **What this does NOT show.** §3.5 is a claim about `H1`, deliberately unread here (§3.2 rule 2 —
  these arms were still being selected). The curriculum is flat on the *trainable* ladder; whether it
  reaches the held-out obfuscator is the question it was built for and is now the decisive open item.

  **Two infrastructure defects, both of the expensive kind, found and fixed before they cost a run.**
  `allow_composites` was designed as "a narrow allowance requested explicitly by the one caller that
  needs it" — RouterLoRA, which trains through `mole/train_mole.py`. This is the first `train_sft`
  arm to use composites, and it walked through every *other* caller that never received the opt-in:
  (a) `eval_vllm.run_ckpt_select` called `load_pairs` without it, so checkpoint selection would have
  died on `QuarantineViolation` **after the 5.3-hour training run**; (b) `scripts/preflight.py`
  validated `train_conditions` against `TRAINABLE_CONDITIONS` only, turning preflight permanently
  red. Both now forward the flag from the same config the adapter was trained with, and the guard was
  verified still active for a config that has not opted in. A narrow allowance is only narrow until a
  second caller appears.

  Also recorded: `build_manifest.py --eval` silently drops any system whose `arch` starts with
  `merge` (they are meant to go through `rq2_jobs`, which instead *rebuilds* the standard merges and
  would overwrite `runs/adapters/.../merge_*`), so a pre-built merge needs a hand-written queue
  entry — the route the density sweep also used.

- **New questions / new hypotheses:**
  - **Does the curriculum reach `H1`?** The only question `s2fam` was built for, and unread. Belongs
    in the single batched confirmatory pass with the density-sweep, seed-42 and cross-seed reads.
  - Is the flatness a property of the objective rather than the data? Every arm so far trains for
    per-condition accuracy and hopes invariance follows. The invariance-loss arm is the one
    remaining repair that optimizes invariance directly — and needs `invariance` added to
    `schema.TrialRow.adapter_arch` first, or it fails at the first row written.

- **Next Steps:**
  1. Run the batched `H1` confirmatory pass — now the decisive item, and it settles five owed reads
     at once.
  2. Build the invariance-loss arm (design in the plan file; `adapter_arch` Literal first).
  3. Correct the LOTO configs' size-matching comment in its own commit (`train_size: 30000` never
     binds; folds are 22,152–23,373 against `mono_all`'s 26,841).

---

### ADDENDUM, same day — the third repair (residual merge) is null too

§3.1 of the report decomposed each expert against the clean-code direction: 52–70 % of every
specialist's task vector points along `dW_L0`, and the condition-specific residuals are only mildly
aligned (mean cosine 0.284, within-family L1b|L2 0.451 / S2|S4 0.438 vs cross-family L1r|S4 0.174).
Measured dilution: ‖mean resid‖ / mean‖resid‖ = **0.6255**, so a uniform merge discards ~37 % of each
specialist-specific update while keeping all of the shared part. (The orthogonality bound √7/7 =
0.378 would say 62 % — quoting it instead of the measurement overstates the effect by 25 points.)

**The prescribed fix, and why it needed no new machinery.** dW = dW_L0 + γ·(1/n)·Σ resid_c expands to
a plain linear combination of the ORIGINAL vectors: w_L0 = 1 − (γ/n)Σs_c, w_c = γ/n. With
s_c ∈ [0.475, 0.727] (Σ = 4.181) and γ = 1/0.6255 = 1.599 that is **w_L0 = +0.045, w_c = +0.228**
(uniform would be 0.125). `MergeSpec` already accepts `weights`, so this is a re-weighting of the
validated driver — and it sidesteps the rank ceiling that blocks exact task arithmetic
(`combination_type="cat"` sums ranks; 8 experts would need r256 against vLLM's `max_lora_rank: 64`).
`scripts/merge/25_residual_merge.py` recomputes the coefficients from safetensors rather than
hardcoding them, so the arm cannot drift from the bank it describes.

**Result** (Grid B, six trainable conditions, `configs/eval/residual_merge_qwen1.5b.yaml`,
job `160_residual_merge`):

| system | mean | format-fail % |
|---|---|---|
| uniform `dare_ties` d0.3 (sweep winner) | **47.03** | 0.4 |
| **residual** `dare_ties` d0.5 | 45.82 | 0.7 |
| uniform `dare_ties` d0.5 (headline) | 44.95 | 1.5 |
| **residual** `dare_ties` d0.3 | 42.31 | 0.5 |
| **residual** `ties` d0.5 | 36.74 | 1.7 |
| uniform `ties` d0.5 | 36.17 | 1.4 |

Cluster bootstrap by `program_id`, 2000 draws: matched-density d0.5 `dare_ties` **+0.88**
[−0.66, +2.47] null; d0.5 `ties` **+0.59** [−0.92, +1.94] null; residual-best vs uniform-best
**−1.27** [−4.61, +2.25] null; **matched-density d0.3 `dare_ties` −4.68 [−8.20, −1.33] SIGNIFICANTLY
WORSE**.

**Verdict: ✗ refuted.** Null at matched density, harmful at the sweep-winning density. The d0.3
damage has a clean cause — DARE rescales survivors by 1/density (3.33× at d=0.3), compounding with
weights summing to 1.644 to give ‖dW‖ = **1.99×** a single expert. Format failure stayed at 0.5 %, so
this is not a `merge_dare_linear`-style artifact; the over-scaled update simply predicts worse. Best
merge in the project remains uniform `dare_ties` at d=0.3.

**Why it is worth reporting.** The dilution is geometrically real and correcting it changes nothing,
so the diluted component was not carrying recoverable accuracy. That upgrades §12.10 from "no
combination strategy we tried helps" to **"the condition-specific part of each expert, even preserved
at full magnitude and correctly weighted, carries no extractable per-condition value"** — a measured
mechanism rather than an empirical sweep.

**Compute note.** `gpu_budget` raised 2 → 3 → 4 on the user's instruction: GPUs 0–2 were idle and the
16.7 GB engine on GPU 3 turned out to be obtune's OWN `forget__qwen25c-7b__7b_rev` job started by a
concurrent session, not a borrowed process. With no borrower on the box, capping below 4 left an idle
card unusable beside our own work. Workers now on all four; the idle check still protects any card a
borrower later takes.

---

### ADDENDUM 2, same day — the residual result decomposed and settled at power

The Grid B confirmatory read produced one contrast surviving BH-FDR: `residual_dare_ties` 41.7 vs
`merge_dare_ties` 34.8 on `H1` (q=0.048, McNemar b/c=8/0). Two defects had to be cleared.

**Defect 1 — not attributable.** The residual arm merged EIGHT ingredients; `merge_dare_ties` merges
six (`ties_v1.yaml`). Reweighting and ingredient count differed at once.
**Defect 2 — underpowered.** 115 items / 27 programs cannot resolve a ~3-pt effect against a 3.61-pt
seed band.

Rebuilt matched (6 ingredients at both banks — s42 has no S3/S4, so six is the largest ladder that
exists at both), added a uniform-8 control, and re-ran on **Grid A `H1`, n=1,214 / 405 programs**
(`configs/eval/residual_decompose_gridA_qwen1.5b.yaml`, phase `final` — `main` was unusable because
these system names already hold Grid B cells there and `cell_dir` does not key on `eval_source`).

| arm | ingr | weights | bank | Grid A | Grid B |
|---|---|---|---|---|---|
| A | 6 | uniform | s17 | 23.9 | 34.8 |
| B | 6 | residual | s17 | **25.9** | 37.4 |
| C | 8 | uniform | s17 | 23.1 | 35.7 |
| D | 8 | residual | s17 | 25.3 | **41.7** |
| F | 6 | uniform | s42 | 24.9 | 38.3 |
| E | 6 | residual | s42 | 25.6 | 41.7 |
| `tuned_L0` | — | — | — | **24.5** | 33.9 |
| `tuned_S2_s17` | — | — | — | **28.0** | — |

| contrast | Δ | CI | b/c | q |
|---|---|---|---|---|
| B−A weighting (s17) | **+1.98** | [+0.49, +3.62] | 49/25 | **0.018 SIG** |
| D−C weighting at 8 ingr | **+2.22** | [+0.91, +3.54] | 51/24 | **0.012 SIG** |
| E−F weighting (s42) REPLICATION | +0.74 | [−0.74, +2.06] | 43/34 | 0.362 null |
| C−A ingredient count | −0.82 | [−1.73, +0.08] | 13/23 | 0.221 null |
| D − `tuned_L0` | +0.74 | [−0.58, +1.98] | 34/25 | 0.362 null |

**Verdict, three parts, none of which changes the thesis.** The residual weighting is REAL and SMALL
(+1.98 / +2.22 at two ladder sizes, both surviving FDR at power; not ingredient count, which is
−0.82 null). It DOES NOT REPLICATE on an independent expert bank (+0.74, null). And it DOES NOT BEAT
THE CONTROL (+0.74 over `tuned_L0`, null); `tuned_S2_s17` at 28.0 still beats every merge. A ~2-pt
improvement to *merging* with equivocal replication — the "bounded rather than promising" reading
registered in the config header before the run.

**The finding that matters more: Grid B overstated the effect 3–5x.** Same contrast: +7.0 (q=0.048)
at n=115, +1.98 at n=1,214. Every arm fell ~10 points between grids AND the ORDERING changed — `D`
was top on Grid B (41.7) and is mid-pack on Grid A (25.3). **Grid B `H1` (115 items / 27 programs)
cannot support merge comparisons.** Every `H1` merge number the RQ2 conclusion rests on is from that
grid (`merge_dare_ties` 34.8, `tuned_L0_k0` 33.9, `l0merge_dare_ties` 33.9, `mole_router` 33.9); they
need an explicit power caveat and future `H1` merge claims belong on Grid A.

**What this run does firm up is §12.10 itself.** At n=1,214 the best uniform merge is **23.9 against
the clean-code control's 24.5** — slightly BELOW rather than level with it. The central negative
result now holds at ten times the power it was established on.

**Two of my own errors, recorded because both were self-inflicted and both were caught only by
checking rather than by the tooling.** (a) I compared an 8-ingredient merge to a 6-ingredient
baseline. (b) The first matched rebuild silently did nothing: parameterizing the script left a
`NameError` on a deleted `SEED` constant, and my `grep` on a `2>&1` pipe discarded the traceback, so
it exited 0 with no output and no merges. `MERGE_SEED` (DARE's Bernoulli mask) is now explicitly
separate from `--seed` (the expert bank) so a bank comparison cannot silently change the mask.
Lesson: never filter stderr when checking whether a build ran.

**Also recorded**: `--stub` on an H1 config really loads quarantined items (generation is stubbed,
`load_eval_items` is not), so two smoke tests appended two ACCESS_LOG rows corresponding to no
measurement. Declared in the log; smoke against a non-H1 condition list in future.
