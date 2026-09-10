# CLAUDE_SCRATCHPAD.md — working state

*Protocol: [`CLAUDE.md`](CLAUDE.md) §0. Update before and after any complex task; this is
working memory, not a log. The durable record lives in [`log/`](log/).*

**Last updated:** 2026-09-09

---

## 2026-09-03 — accuracy-improvement campaign (H1 / held-out / overall), CodeLlama-7b

User chose four untried levers; explicitly rejected CoT/trace-SFT and RL (keep the no-CoT format).
Corrections to my own earlier "untried" list, found on re-reading `log/modularity/2026-08-17`:
training on composites WAS run (Qwen-1.5B, −1.36 [−2.63, +0.04] vs unstacked) and the
S2-family curriculum WAS run (+0.02). Both refuted. Not repeated here.

Selection discipline: every arm is read on the trainable grid (`heldout`, Grid A) and LOTO;
**H1 is not read** — the single `final_eval` stays unspent until the campaign has a winner.

| W | lever | what is new | code / data | GPU |
|---|---|---|---|---|
| W1 | self-consistency | every cell so far is greedy; sample n=8 @ T=0.7, plurality vote on the normalised literal; also report any-of-n (oracle) as the headroom bound | `eval_vllm.py`: `sampling.n`, vote in `run_cell`, extra cols `sc_*`; `configs/eval/selfcons_generic.yaml` (phase `selfcons_generic`) | ~1 job, <1 h |
| W2 | variant augmentation | each program has ONE variant per condition; build K=3 extra seeds (101/202/303) for the randomised transforms L1b/L1r/S1/S2 (L0/L2 deterministic), train `mono_aug` on same programs × 4 variants; compare to `mono` s17/42/101 | `05_build_variants.py --seed/--out-tag`, `06_emit_pairs.py` → `data/train/pairs_aug/s<seed>/`, `data.py` `train.augment_seeds` | build on `normal`; 1 train ≈ 4×3.5 h? (mono took 3.5 h; 4× rows → cap epochs) |
| W3 | data scale | corpus is tier1 only (apps/cruxeval/humaneval → 2,231 programs, 1,563 train). Ingest tier2 (mbpp) + tier3 (CSN) as NEW TRAIN-ONLY programs with the existing test/val assignment frozen; train `tuned_L0_scale` / `mono_scale` | `02_build_corpus.py --tiers`, split-freeze step, dedup vs existing test | CPU days for CSN; then 2 trains |
| W4 | bigger student | `codellama-13b` is in `models.yaml`, never downloaded; train L0 + mono s17, eval base/L0/mono on the grid | download 26 GB; `grid_py_L0` / `mono_generic_py` with `--model codellama-13b` | 2 × ~45 min + evals |

Also folded in: `mono` s42/s101 adapters finished (ck_mono_s42 best 0.3495) — eval on `rq2_generic`-style grid for the seed band on the `mono_all` tie.

Expectation, stated before running: W1 without CoT mostly re-derives the greedy mode of a short
literal — the vote is expected to be within ~1 pt of greedy; the any-of-n number is what tells
us whether a reranker could ever help. W2 is the most principled invariance lever untried.
W3 is bounded by the 5.7×-data-buys-0.11-pt result from mono_all. W4 is the cheapest absolute
win if the scale trend from Qwen (1.5B → 7B) holds for CodeLlama.

---

### 2026-09-03 progress (W2/W3 plumbing)
- **Fix:** `schema.TrialRow.phase` literal lacked `selfcons_generic` → job 376082 crashed on cell 1 and then wedged (vLLM EngineCore never exits after a parent exception); cancelled, `_main_fastfail` now `os._exit(1)`s on ANY exception, cell writes are rename-atomic, resubmitted as 376113.
- W2 builds: 376093/4/5 done in ~2 min each; surfaces verified distinct per seed
  (canon≠s101≠s202 for L1b/L1r/S1/S2). Pairs emitted to `data/train/pairs_aug/{s101,s202,s303}/`;
  `load_pairs(..., augment_tags=[s101,s202,s303])` → **79,167 train rows** (mono: 26,841).
  Mix is skewed to randomised conditions (L0 = 4,689 = 6 %) — a confound to name in the log.
  Manifests rebuilt + verified (H1 scan OK). Config `configs/train/mono_aug_generic_py.yaml`
  (`adapter_root: runs/adapters_aug`, epochs 2). Loss-mask gate: job 376106 on `dev`
  (login node has an 8 GB `ulimit -v`; `inspect_batch.py` dumps core there).
- W3 plumbing: datasets were NOT in the juno HF cache (only models transferred) — fetched
  mbpp, mbppplus, CSN python (416 MB). `02_build_corpus.py --extend-frozen <tag>`: dedups
  vs testset + the existing base by id and content, assigns every survivor to train, writes
  `data/train/base_<tag>/`, `data/splits/python_<tag>.json`, `data/manifests/corpus_python_<tag>.json`
  and never touches `data/splits/python.json`. `05_build_variants.py --base-root … --aug-tag scale`
  routes the new programs' variants through the aug path at the canonical seed. Configs:
  `mono_scale_generic_py.yaml`, `L0_scale_generic_py.yaml` (`adapter_root: runs/adapters_scale`, epochs 3).

- **Seed band landed** (376083, 4.6 min): `mono_all − tuned_L0` pooled s17 +0.56 [−0.89, +2.01],
  s42 +0.77 [−0.50, +2.07], s101 +0.01 [−1.30, +1.34]. Same shape every seed: L0 cost
  (−1.4…−2.3, s101 excludes 0), L1b gain (+1.4…+2.8, s17/s42 exclude 0), rest null.
  `scripts/analysis/26_campaign_arms.py` → `results/analysis/campaign_2026-09-03.json`.
- W3 corpus: first build had 16 CSN `program_id` collisions (path-only id) → loader now
  appends the function name; `02_build_corpus` refuses collisions; rebuilt as 376118.
  Yield: mbpp 959 raw → ~750, CSN 161k loaded → 4,921 seeded → ~160. ≈ +900 programs
  (+58 % over 1,563 train programs). Modest — say so; it is what the sources give.
- Chains (resubmitted after `train_size: null` crashed `int(None)` in build_sft_splits, fixed in data.py): aug 376282→376283→376284; mono_scale 376285→376286→376287; L0_scale 376288→376289→376290.

### 2026-09-04 — W1 landed (376113, 11 min); log entry `log/transfer/2026-09-04_self-consistency-and-seed-band.md`
- vote8 − greedy pooled: **base +2.11 [+1.45, +2.81]** (39 % of flips are format repairs, ff 0.136→0.013),
  **tuned_L0 −0.99 [−1.70, −0.31]** (a T=0.7 sample costs 3.5 pts, vote recovers ~2.5),
  **mono_all +0.05 [−0.27, +0.37]** (agreement 0.82 → vote ≈ greedy). H-selfcons held for tuned
  systems; **W1 is dropped as a lever.** Any-of-8 ceilings 0.37 / 0.56 / 0.46 — headroom only,
  no verifier exists at test time. Note `tuned_L0` has the MOST headroom and `mono_all` the least
  at equal greedy → H-peaked-breadth (open, unscheduled).
- Seed band: H-seed-band refuted, the tie is real at s17/s42/s101.
- **W3 (L0 half) landed** (376288 train 33 min / 376289 ck best `checkpoint-348` val 0.402 / 376365 eval —
  376290 died on my `arch: single` typo, fixed b21525b): `tuned_L0_scale − tuned_L0` pooled
  **−0.20 [−1.00, +0.61]**, every condition null (L0 −0.66, L1b +0.48, L1r −0.06, L2 −0.78,
  S1 +0.56, S2 −0.54). +58 % programs (4,689 → 7,425 L0 rows, mbpp+CSN) buys nothing. Consistent
  with the mono_all "5.7× data → +0.11 pt" result: the corpus is not the bottleneck.
- **W4 (13B) landed** (376097 tr13_mono 5 h 10 m, loss 0.134; 376099 ck best `checkpoint-838` val 0.412;
  376100 ev13_grid). `results/analysis/campaign_13b_2026-09-04.json`. **13B − 7B (same items):
  tuned_L0 +3.39 [+1.93, +4.89], mono_all +3.60 [+1.83, +5.23], base +1.54 [+0.10, +2.99].** Positive
  on every condition for both adapters. The biggest absolute win of the campaign, and the only
  lever that moved anything. At 13B `mono_all − tuned_L0` = +0.77 [−0.71, +2.20] — the same tie,
  same shape as every 7B seed (L0 −2.34 [−4.31, −0.30]; L1b +2.71 [+0.60, +4.83]; rest null).
  format_fail base 0.102 / tuned_L0 0.016 / mono_all 0.011.
- **W3 (mono half) landed** (376285 5 h 16 m, loss 0.121; 376286 best `checkpoint-662` = epoch 1, val 0.363;
  376287 eval): `mono_scale − mono_all` **+0.73 [−0.66, +2.10]**, null everywhere (L1b +1.51, L1r +1.26,
  L2 +1.08 the largest, all spanning 0). `mono_scale − tuned_L0` +1.29 [−0.14, +2.69] with the usual
  fingerprint (L0 −1.98 [−3.90, −0.24]; L1b +3.92 [+1.75, +6.03]; S2 +2.34 [+0.48, +4.26]). +58 %
  programs is inside the seed band (s42 was +0.77 over tuned_L0). W3 is closed: null on both halves.
- **W2 landed** (376282 7 h 16 m, loss 0.085; 376283 best `checkpoint-1236` = epoch 1, val 0.368 flat;
  376284 eval): `mono_aug − mono_all` **+0.17 [−1.14, +1.38]**, null on all six; format_fail 0.0058
  (corpus minimum). Mix-skew confound would have hurt L0 and L0 is null (−0.84) → not an artefact.
- **CAMPAIGN CLOSED.** W1 ✗ W2 ✗ W3 ✗ W4 ✓ (+3.4). Six breadth adapters (s17/s42/s101, aug, scale, 13B)
  share one fingerprint vs the clean control: L0 −1.4…−2.6, L1b +1.4…+3.9, rest null, pooled tie.
  Entry `log/transfer/2026-09-04_accuracy-campaign-closes.md`; artifact updated. H1 unread;
  recommendation: hold `final_eval` (13B on H1 would only show "bigger is better").
  Open, unscheduled: H-L1b-L0-trade (existing cells, CPU), H-saturation (downward train_size sweep).

### 2026-09-04 — W5: hidden-state alignment (user: "if this doesn't work, train the hidden states to match the clean code")
- **Prior art in-repo:** `src/obtune/align.py` already implements exactly this objective —
  L = L_task(x̃) + λ·L_align, frozen `tuned_L0` teacher on the clean parent, n≠m solved by
  comparing only the last k=4 answer-position prompt states (the prompt suffix tokenizes
  identically), mismatched-teacher permutation control. Ran ONCE: Qwen-1.5B, S2-only, λ∈{0,0.1,…,10}
  (`log/modularity/2026-08-30_alignment-arm-lambda-sweep.md`) → flat-not-collapsed (matched−vanilla
  −0.004…−0.008 at every λ; mismatched degrades monotonically, so the harness works). Loophole
  recorded there: teacher tuned_L0 (0.390) was *weaker* than the vanilla student tuned_S2 (0.404).
- **Why rerun on CodeLlama-7b mono mix:** closes the loophole (tuned_L0 is the strongest 7B system,
  +19.9 over base and ≥ every breadth adapter), and the six-condition mix is where the fingerprint
  lives (L0 −2, L1b +3). If L_align is semantic it should erase the L0 tax without losing L1b.
- **Config:** `configs/train/align_codellama7b_py_mono.yaml` = exact twin of `mono_generic_py.yaml`
  @7B (six conditions incl. L0, train_size 30000, seed 17, r32, 16×4) + `align.teacher_adapter =
  runs/adapters/codellama-7b/python/L0_r32_s17/best`, layer_fracs → L4-10-16-21-25-30 on 32 layers.
  L0 rows align to the teacher on the identical input (trivial term) — kept so λ=0 is a mono_all twin.
- **Arms:** cache (1 job) → λ=0 (plumbing; must reproduce mono_all ±seed band), λ=1 matched,
  λ=1 mismatched, λ=3 matched. ~3.5 h each on H200 (mono_all was 12,460 s). Then ckpt-select
  (held-in val, H1-free) → eval on the trainable grid (`configs/eval/align_codellama7b.yaml`, arch
  invariance / invariance_mismatch) → contrast vs `mono_all` **and** `tuned_L0`, program bootstrap.
- **Untried n≠m answers, pending user's candidate list (cut off in message):** mean-pooled per-layer
  states + InfoNCE over the batch; `Variant.rename_map` token-aligned matching for L1b/L1r/L2
  (no map for S1/S2 → pooled fallback). Not built; answer-position first because it exists.
- **Loss scale note (from the first log lines):** L_align is raw MSE on unnormalized states; at 7B it
  runs ~5 at epoch 0.4 vs the task loss ~1.5 (Qwen-1.5B started at 0.9 and ended at 0.03), so λ=1 here
  weights the term harder than λ=1 did there. Added λ=0.3 (train/ckpt/eval chained) so the sweep
  brackets it: 0, 0.3, 1, 1 mm, 3. Cache 377002 done in <1 h: 5,016/5,019 parents valid.
- **Plumbing defect found while λ=0 trained (2026-09-04, fixed in `7ad5353`, NOT in the running arms):**
  `AlignTrainer.compute_loss` dropped `num_items_in_batch`, so transformers skipped the /grad_accum
  division → losses and gradients 4× mono_all's at every logged step (9.42 vs 2.27 at epoch 0.05,
  0.0129 vs 0.0040 at 2.86; grad_norm ~4.6 vs ~1.0, so the 1.0 clip engaged nearly every step).
  Same defect in the 08-30 Qwen sweep. Within-sweep contrasts (matched vs mismatched, vs λ=0) are
  unaffected — all five arms share it; only "λ=0 == mono_all exactly" is weakened to "near-twin".
  λ=0 eval_loss 1.372 vs mono_all 1.306. **The λ=0 − mono_all read decides whether W5 must rerun
  under the fix** (inside the seed band → keep; outside → rerun all five, ~17 GPU-h).
- **Plumbing PASSED (377010):** `align_lam0 − mono_all` **+0.28 [−0.71, +1.22]**, null on all six
  (|Δ| ≤ 0.96); vs tuned_L0 +0.85 [−0.58, +2.34] with the fingerprint (L0 −1.80, L1b +1.93, S2 +2.16
  excl 0). Val 0.3589 inside the s17/s42/s101 band (0.3672/0.3505/0.3573), best ckpt-838 like mono_all.
  → the 4× gradient scale is absorbed; the sweep stands, no rerun. `results/analysis/align_2026-09-04.json`.
- **W5 CLOSED (2026-09-04).** All five arms landed. Plumbing gate passed (λ=0 − mono_all +0.28
  [−0.71, +1.22], null on six). **Control decides it: matched − mismatched +0.18 [−0.82, +1.16]**,
  null on every condition, both ~1 pt under the vanilla twin. Grid dose-response monotone negative
  (+0.28 → +0.00 → −0.78 → −2.11 for λ 0/0.3/1/3; λ=3 excludes 0 on all six) while align_loss is flat
  (3.475/3.415/3.374 matched vs 5.239 mismatched) — magnitude matters, target does not. L0 tax deepens
  −1.80 → −3.35 → −4.97; λ=3 erases the L1b gain. Val non-monotone, mismatched arm highest (0.3652).
  Entry `log/modularity/2026-09-04_invariance-arm-at-7b.md`; report §23.3. B/C (InfoNCE, rename_map)
  NOT motivated — the answer-position variant already has exact correspondence and it was the teacher
  that did not matter.
- **H-L1b-L0-trade RESOLVED same day** (`log/transfer/2026-09-04_l1b-l0-trade-is-two-effects.md`,
  report §22.6): L1b gain located + dose-dependent (0.17 zero-dose → 0.408 matched specialist → 0.44–0.54
  breadth); L0 cost NOT localized (pay ratio flat across the ladder; tuned_S2 2.49 vs mono_all 3.10).
  Naive correlation and raw pay-gap both falsely confirmed it — base posts the largest correlation of any
  arm. Opens H-L0-cost-source. `tuned_S2` is the only tuned system with no L0 cost (−0.06).
- **Decision rule:** matched > mismatched AND matched−mono_all excl 0 on ≥1 non-L0 condition
  without an L0 tax → H-align supported, then and only then consider the alt L_align forms.
  Matched ≈ mismatched ≈ mono_all → objective is a regularizer at 7B too; close the arm.

## Current state

Phase 0–1 complete and verified; the RQ1–RQ3 implementation is being built out.

**Frozen contracts** — do not change without a design-doc update, everything depends on them:

| File | Contract |
|---|---|
| `src/obtune/config.py` | `PROJECT_ROOT`, `load_config` (with `_extends`), `GLOBAL_SEED = 17` |
| `src/obtune/paths.py` | quarantine guard; `load_training_jsonl` is the only training-read entry point |
| `src/obtune/schema.py` | `BaseProgram`, `Variant`, `TrainPair`, `EvalItem`, `TrialRow` (the stats contract) |
| `src/obtune/exec/pool.py` | `BatchItem` → `ProgramResult`; `CaseResult.matches` compares exceptions **by type only** |
| `src/obtune/exec/canon.{py,mjs}` | canonical output spec, verified byte-identical across languages |
| `configs/conditions.yaml` | the 7-condition ladder + H1 marker patterns + gate policy |

**Verified by running (2026-08-04):**
- canon parity Python ↔ JavaScript: 9/9 fixtures identical; sets/undefined/NaN/deep-nesting rejected on both sides.
- executor: Python and JS, both languages returning `ok` / `raised` (type only) / `timeout` / `unserializable` correctly; infinite loops terminate via RLIMIT_CPU (Python) and the vm watchdog (JS).
- quarantine lint: 5/5 (loader guard rejects quarantine/eval/outside paths; H1-labeled rows rejected inside the training tree; no `obf/h1` imports outside the generator; javascript-obfuscator confined to H1).
- environment: torch 2.11.0+cu130, transformers 5.14.1, trl 1.9.2, peft 0.20.0, vllm 0.26.0 in `/data/jvl210002/conda_envs/obtune`; Qwen2.5-Coder-1.5B-Instruct downloaded; `js/node_modules` installed (168 packages).

---

## Decisions taken (and the ones rejected)

1. **L2 = sequential minification** (`a`, `b`, …) + annotation stripping, not "L1r + extras". The legacy tiers were never purely identifier-based, so "per the existing tier definition" had to be resolved. Sequential minify matches what the legacy JS-L3 minifier actually produced and gives L1r-vs-L2 a *same-family, different-surface* contrast at equal information loss. **Rejected:** L2 as a strict superset of L1r — it would make L1r→L2 transfer trivial by construction.
2. **Dual tier namespace** (`condition` vs `tier_icse`) rather than relabelling the legacy ladder. Legacy tier semantics differ per language *and* per vintage; one label meaning four transforms is exactly the drift that would invalidate a cross-language claim.
3. **Integral floats collapse to plain integers** in `canon` (`2.0` → `2`). JavaScript has one number type; keeping the Python int/float distinction would score the same program differently by language. Scoring compares numerics with a tolerance anyway.
4. **javascript-obfuscator confined to H1.** Its `deadCodeInjection` forcibly enables `stringArray`, and `stringArray` is on by default — any use for a trainable condition leaks the held-out feature. Handled architecturally, plus a marker scan in the gate. **Rejected:** careful per-condition option configuration; one upstream default change would silently poison the corpus.
5. **No containment stage in scoring.** The `../LOG.md` §2026-06-09 audit measured ~3 % false positives from substring matching (`927` in `9273`). With no-CoT completions there is nothing to extract, so leniency buys nothing.
6. **PEFT `add_weighted_adapter` for merges,** not mergekit (whose LoRA path is merge-then-SVD-extract and which pins an incompatible accelerate).
7. **Single env** for train + vLLM eval: vLLM pins torch 2.11 and TRL/PEFT accept it. DeepSpeed dropped — single-GPU LoRA needs nothing from it.

---

## Open questions / watch items

- **S1 coverage is bounded by program *length*, not just by bail constructs.** Measured on the 12 Python
  fixtures: 10 flattened cleanly (randomized state ids, shuffled cases, outputs identical), 2 bailed — and
  both bails were `min_states=3`, i.e. the function body was too short to make a dispatch loop, not a
  `try`/`with`/`yield` construct. `configs/data.yaml` sets `loc_min: 3`, so a meaningful slice of the corpus
  will be S1-ineligible for this reason. Consequences to check once the builder runs at scale: (a) S1's
  program set will systematically differ from L1b's — the all-conditions-succeeded common subset is the
  defense and it must be used for headline numbers; (b) if the common subset is much smaller than the full
  set, consider raising `loc_min` for corpus admission rather than letting S1 silently select for long
  programs, which would confound "structural condition" with "longer program".
- **Coverage of S2** on real programs is still unknown until the builder runs.
- **H1 eligibility is literal-density-bound — RESOLVED as a reporting requirement, not a
  bug.** Measured on the real 70 test parents: **Python 27/40, JavaScript 24/30, 51/70
  overall (73 %)**. Of the 13 Python rejects, **6 have zero H1 sites** (no strings, no
  integer literals, no MBA-able operators — there is simply nothing for string encoding
  or MBA to act on) and 7 have 1–2 sites. Lowering `min_total_sites` to 1 would recover
  those 7 but at the cost of near-identity H1 variants, which is precisely the
  degeneracy the bar exists to prevent and would *inflate* the Invariance Index — the
  wrong trade for the headline number. **Decision: keep the bar at 3.** Consequences
  the analysis must honour: report H1 coverage explicitly, compute the Invariance Index
  on the H1-eligible subset, and restrict the other conditions to that same subset when
  comparing, so the H1 column is not read against a different program set.
- **JS corpus scale**: curated ceiling ≈1.3k programs. Transpilation is execution-gated so correctness is safe, but the distribution shifts — the `provenance` covariate must actually be tested in the GLMM, not just recorded.
- **Attention span→token resolution** must be re-measured on Qwen2.5-Coder tokenizers (the transcoders validation was on Llama-3.1-8B and Qwen3-0.6B). Hard-fail below 0.98.
- **Dataset A Python I/O** is human-formatted and the code is double-spaced; canonical outputs are re-derived by execution and disagreements with the human key are logged. Anything beyond `FALSE` vs `False` is a finding, not a formatting artifact.

---

## Side thread — CFT replication (`nikiema2025contrastive`), started 2026-08-08

Full design and the deviation list: [`docs/CFT_REPLICATION.md`](docs/CFT_REPLICATION.md).
Code in `src/obtune/cft/`, configs in `configs/cft/`, tests in `tests/test_cft_*.py`.

**Why:** it is the nearest prior work to the pilot finding (`papers/RELATED_WORK.md` §2.1) and
§7 names CFT as the candidate RQ1 intervention. Before adopting an intervention, check whether
its result reproduces on our corpus.

**Scope limit that cannot be worked around:** the paper's third transformation is string
encryption, which maps onto our `H1`. H1 is quarantined, so this replication covers renaming
(`L1b`/`L1r`/`L2`) and dead code (`S2`), and adds `S1` (control-flow flattening), which the
paper lacks. The paper's *hardest* arm is the one we cannot run.

**Decisions taken here (2026-08-08):**
- **Negatives are the obfuscated variant with one token changed**, not clean-vs-clean as the
  paper does. Under the paper's construction "is B obfuscated?" predicts the label perfectly,
  so L_pos/L_neg can be solved without comparing semantics. `clean_mutant` is kept as a config
  option so the confound is measurable rather than arguable.
- **Every negative is executed** against its parent's cases and kept only if an output really
  differs *and* it still runs on ≥50 % of them. Rejects equivalent mutants (which would teach
  the inverse of the intended lesson) and everywhere-broken ones (trivially spottable).
- **CodeBLEU is the published implementation** (`codebleu==0.7.0`), vendored to `env/vendor/`
  so `env/lock-obtune.txt` is untouched. The distribution's tree-sitter 0.22 pin is deliberately
  NOT vendored — it would shadow the 0.26 grammars `obf/base.py` depends on. `metrics.py`
  *appends* the vendor dir to `sys.path` for that reason.
- **Readability is a labelled substitute**, not Scalabrino et al.'s Java model. Only within-run
  contrasts are interpretable. Its short-identifier threshold (0.5) was set by measurement over
  400 programs (L0 flagged 8 % / L2 flagged 89 %), not by taste.
- **Model ladder:** 1.5B is a pipeline smoke test only. The headline number runs on
  `qwen25c-7b` — the paper's own "QwenCoder" row (39.00 % reverse under CFT), and the paper
  reports an architectural capacity hierarchy, so a null at 1.5B would be uninformative.
- **Queue priority 60** — behind the entire RQ1 grid. A replication of someone else's paper
  does not preempt the project's own experiments.

**Watch item:** `train.py` records `task_token_share` per run. Equal *instance* counts across
the three pools (the paper's balancing) do NOT mean equal loss weight — a `gen` target is a
whole program, a `pos`/`neg` target is one token. If the measured gen share is ~0.99, the
"three-term loss" is close to gen-only plus a rounding error, and that is a fact about the
paper's recipe worth reporting rather than silently correcting.

---

## Next up

1. Finish the module build-out and integration review; get the full test suite green.
2. Run the data layer end to end: test-set ingest → corpus → variants → H1 (quarantined), then `make check`.
3. Pre-register H1a–H3 before the main grid (the pilot is exploratory and labeled `phase=pilot`).
4. Week-1 kill-switch pilot on one idle GPU; fill in the verdict box in `docs/CHECKLIST.md` §5.

## 2026-09-04 — W6: "I want more" — every lever except RL, in one campaign

User asked what else raises H1 and accuracy in general, then said "everything except 4" (RL).
Levers, in the order they are queued, each with the decision it exists to make:

1. **Newer base model — `llama31-8b`** (go/no-go job 377796 — 377787 was cancelled unstarted: `submit.py --argv` prepends `python`, so `--argv python -m …` rendered `python python -m …`; `eval/basecheck_llama31_8b.yaml`,
   six trainable conditions, no H1). Evidence: Qwen2.5-Coder-7B *untuned* + 4-shot ICL reads
   L0 0.487 / H1 0.291, above every tuned CodeLlama-7B system. Qwen is barred here; Llama-3.1
   is the newest ungated instruct model already in HF_HOME. Template accepts system role;
   re-gated max_seq_len 2048 (mean 404, p95 685, 0.00 % truncation). GO if untuned base ≥
   tuned CodeLlama-7B on L0 (~0.43) or clears CodeLlama base widely with format_fail ≪ 0.13.
   On GO: 6-adapter grid + mono_all + tuned_L0, then §26-style ranking.
   **GATE READ 2026-09-05 (377796, 4 min): NO-GO on the pre-declared rule.** Llama-3.1-8B base
   on heldout: L0 0.257 / L1b 0.222 / L1r 0.242 / L2 0.215 / S1 0.213 / S2 0.205, format_fail
   0.04–0.06. CodeLlama-7b base is L0 0.257 / L1r 0.207 / S2 0.193 at format_fail 0.13–0.16 —
   i.e. identical on L0, +1…+3.5 on the obfuscated columns, and *conditional on a well-formed
   answer* it is weaker (0.270 vs 0.295 on L0). Not ≥0.43, not a wide clear. Because the
   question the lever exists to answer is the TUNED ceiling, not the base one, a reduced probe
   runs instead of the 8-adapter grid: `tr_ll8_L0` 377846 → `ck_ll8_L0` 377847, `tr_ll8_mono`
   377848 → `ck_ll8_mono` 377849 → `ev_ll8` 377850 (`rq2_generic --systems base,tuned_L0,mono_all`).
   Promote to the full grid only if `tuned_L0` beats CodeLlama-7b's 0.430 outside the seed band.
   **`tr_ll8_L0` 377846 DONE (20 min, train_loss 0.492); `tr_ll8_mono` 377848 DONE (3.0 h, 1260 steps,
   train_loss 0.141, truncation 18/26,841 at 2048). `ck_ll8_L0` 377847 / `ck_ll8_mono` 377849 →
   `ck_ll8_L0` 377847 done: 0.435 / 0.435 / 0.420 / 0.417 (ckpt 74/148/222/final), best 0.435 —
   against CodeLlama-7b `tuned_L0`'s 0.408 on its own val, +2.7 pts. `ck_ll8_mono` 377849: 0.371 /
   0.386 / 0.388 / 0.386, best 0.388.**
   **`ev_ll8` 377850 read (2026-09-05) — LEVER 1 CLOSED, not promoted.** L0 0.447 clears the
   literal 0.430 gate, but paired on the identical items it is +1.80 [−0.42, +4.07] on L0 and
   +1.21 [−0.29, +2.64] pooled — both cover zero, and the threshold predates paired intervals for
   cross-model contrasts. Decisive: `base` is +2.08 [+0.19, +3.92] ahead while the tuning gaps tie
   (+17.18 vs +18.04) — the advantage is INHERITED, not produced by tuning; the newer base even
   converts tuning slightly worse. **Keeper: the RQ2 fingerprint replicates cross-family** —
   `mono_all − tuned_L0` pooled +0.16 [−1.26, +1.61], with the L0 cost (−2.22 [−4.13, −0.24]) and
   L1b gain (+2.83 [+0.90, +4.76]) the only intervals excluding zero, same signs as CodeLlama.
   Entry `log/transfer/2026-09-05_llama31-probe-fingerprint-replicates.md`.**
2. **Self-consistency (maj@8)** — ALREADY RUN (`selfcons_generic`, 09-04 05:36) and never
   analysed: vote−greedy is −1…−2 pts for `tuned_L0`, ±0 for `mono_all`, +2…+3 for `base`.
   NULL for tuned adapters, as the config predicted. BUT any-of-8 for `tuned_L0` is
   0.53–0.59 vs 0.43 greedy → **2b: trained verifier / best-of-n reranker** (not RL) is the
   lever that headroom points at. Queued after 3.
   **2b SUBMITTED 2026-09-05.** Pipeline: `scripts/28_sample_candidates.py` (vLLM, `tuned_L0`
   adapter, n=8 T=0.7 top_p 0.95 seed 17 + one greedy row as `sample_idx −1`, every row
   graded and carrying `cum_logprob`) → `runs/candidates/codellama-7b/tuned_L0/{heldout,val,
   train}.parquet`, jobs `cand_heldout` 377858 / `cand_val` 377859 / `cand_train` 377860
   (train = the six-condition train split, 26.8k items; trainable conditions only — the
   script refuses H1).
   **Fix 09-05:** `cand_heldout` 377858 FAILED — one held-out prompt is 8,193 tokens and vLLM
   raises rather than truncates; script 28 now calls `eval_vllm.drop_overlong` (same rule as
   the eval path, dropped ids recorded in the summary json). Resubmitted as 377945, `rerank`
   re-chained as 377946 (afterok 377945:377861). `cand_val` 377859 done clean: 1,917 items,
   greedy 0.369, sample 0.344, any-of-8 0.534, all-of-8 0.189 — the 16-pt any-of-8 gap is
   the headroom the verifier is chasing. `cand_train` 377860 DONE (11.5 min): 26,841 items, greedy 0.482 (train split — the L0 sixth
   is memorised), sample 0.427, any-of-8 0.666, no drops. 43 % positives among 215k samples
   → `tr_verif` 377861 balances and caps at 40k. Now eligible.
   **`cand_heldout` 377945 DONE: 9,582 items (6 dropped, all `apps_1615_0` — the 20,055-token
   literal program `drop_overlong` was written for), greedy 0.385 pooled over six conditions,
   sample 0.353, any-of-8 0.559, all-of-8 0.189. Held-out headroom is 17 pts. `rerank` 377946
   now waits only on `tr_verif` 377861.**
   **`rerank` 377946 read (2026-09-05) — LEVER 2b CLOSED, BOTH HYPOTHESES REFUTED.**
   Heldout pooled: greedy 0.3854, any-of-8 0.5628 (+17.74), vote 0.3756 (−0.98), cum_logprob
   0.3907 (+0.53 [−0.09, 1.15]), verifier ckpt-1132 0.3963 (**+1.09 [0.00, 2.17]** — bound touches
   zero) and **+0.38 [−0.58, +1.38] over the logprob control**: both conjuncts fail. base-as-judge
   **AUC 0.347, BELOW CHANCE**, −5.52 [−6.75, −4.28] — anti-informative, not merely uninformative.
   Mechanism: AUC 0.887 buys +1.1 pts because 43.7 % of items have NO correct candidate (any-of-n
   is not headroom) and on the rest rescues 0.131 ≈ breakages 0.112. H-trace-complement was gated
   on this clearing → does NOT inherit a pass; needs its own registration (two-way break-even is
   52 %, but 2b failed on conversion not ranking power). Entry
   `log/transfer/2026-09-05_verifier-is-a-good-classifier-and-a-bad-selector.md`.**
   **`tr_verif` 377861 DONE (3.2 h, 1132 steps, train_loss 0.203). Pool: 241,569 sampled rows →
   99,523 distinct (item, answer) pairs, 18,134 pos / 81,389 neg → balanced to 36,268 at 50 % pos
   (the 40k cap never bound; the positives did). Val 1,000 at 51.3 % pos. Truncation 49/36,268.
   Two checkpoints (566, 1132) — `rerank` 377946 scores both plus the zero-training logprob
   controls and picks on val only.** `src/obtune/verifier.py`: the generator's own prompt + candidate as the
   assistant turn + "Is the return value above exactly correct? Answer yes or no." → one-token
   completion; `scripts/29_train_verifier.py` (`train/verifier_generic_py.yaml`: r32, 2 epochs,
   dedup on (item, pred_norm), class-balanced, cap 40k) → `runs/adapters_verifier/codellama-7b/
   python/tuned_L0_r32_s17/`, job `tr_verif` 377861 (after 377859+377860). `scripts/30_rerank.py`
   scores every distinct candidate (logsumexp yes − logsumexp no at the first token, vLLM
   max_tokens 1 logprobs 20) under each checkpoint AND the untuned base ("zero-shot
   self-verifier"), then compares greedy / vote / logprob / logprob_norm (zero-training
   controls) / verifier / any_of_n with a program-cluster bootstrap vs greedy; checkpoint is
   chosen on VAL rerank accuracy, heldout reported for all. Job `rerank` 377862 (after
   377858+377861) → `results/analysis/rerank/codellama-7b/tuned_L0/rerank_report.json`.
   Decision rule: the verifier is a real lever if verifier−greedy on heldout is > 0 with a CI
   excluding zero AND beats the logprob controls; if base-as-verifier ≈ trained verifier, the
   finding is "the model can already judge, it just cannot pick" (models-know-how-not-when).
3. **Execution-trace SFT** (`src/obtune/trace.py`, `prompt.trace: true`): the completion becomes
   a per-line trace of the *obfuscated* program (`L<line> name=value …`, changed locals only,
   ≤40 events then `...`), then `=> <literal>`. Teaches execution, invariant by construction;
   H1's MBA/string-encoding needs intermediate computation a direct-answer model cannot do.
   Arms: `trace_L0` (clean only — the `tuned_L0` analogue) and `trace_mono` (six conditions).
   Frozen 2026-09-04 after calibration: `max_events 64, max_repr 48`; 200-row prompt+trace
   lengths were L0 max 1966 / S2 2265 / S1 3399 tokens (S1 prompts alone p95 1520), so
   **max_seq_len 4096** (3072 truncates 3.5 % of S1 — the >1 % guard would abort), batch 8×8,
   eval `max_tokens 2048`, `ckpt_select.max_tokens 2048`. Adapters under `runs/adapters_trace/`
   (the dir name encodes only conds/rank/seed and would overwrite the greedy bank). Eval
   config `eval/trace_generic.yaml` adds `base_trace` (untuned base, trace prompt) so the
   format effect and the training effect separate. Trace cache `runs/trace_cache/python/`.
   Silent-failure guards: truncation rate on prompt+trace, format_fail on the extracted
   answer, and the trace arm's *greedy* answer compared to `tuned_L0` on the same items.
   **Status: loss-mask gate PASS (dev 377801); chains `tr_L0` 377802→`ck_tr_L0` 377804→`ev_tr_L0` 377806,
   `tr_mono` 377803→377805→377807, all pending. Entry: `log/transfer/2026-09-04_trace-sft-and-34b-submitted.md`.**
   **`tr_L0` 377802 DONE (43 min, 222 steps, train_loss 0.173, truncation 0/4688 at 4096,
   len p95 1077 / max 3933); `tr_mono` 377803 DONE (6.3 h, 1260 steps, train_loss 0.0505,
   truncation 16/26,832 = 0.06 % at 4096, len p95 1620 / max 5706). The tiny loss is the long,
   near-deterministic trace completion dominating the token count, not an accuracy signal —
   `ck_tr_mono` 377805 → `ev_tr_mono` 377807 pending.**
   **`ev_tr_L0` 377806 read (2026-09-05): trace_L0 vs tuned_L0 vs mono_all, item-for-item on
   rq2_generic — L0 0.361 / 0.429 / 0.412; L1b 0.319 / 0.362 / 0.387; L1r 0.319 / 0.375 / 0.384;
   L2 0.335 / 0.380 / 0.378; S1 0.085 / 0.379 / 0.383; S2 0.241 / 0.389 / 0.405. NEGATIVE, two
   mechanisms: (1) runaway traces — format_fail 12–22 % (S1 74 %) and it equals the fraction
   hitting the 2048-token cap to three decimals; the model NEVER emits the `...` budget cut
   (0/9.6k outputs) although 11 % of training traces end in one — it has no counter, so
   "stop after 64 events" was not learnable from the cut alone; (2) even conditional on a
   parsed answer it trails tuned_L0 on the same items (L0 0.411 vs 0.452, S1 0.327 vs 0.451).
   A trace→tuned_L0-on-cap hybrid is still −3.7 [−6.0, −1.4] on L0 and −7.7 [−10.0, −5.4] on
   S2 (program-cluster bootstrap). Complementarity exists (trace ✓ & tuned_L0 ✗ ≈ 9 % of items)
   but tuned_L0 ✓ & trace ✗ is 14–31 %. base_trace (untuned, trace prompt) 0.05–0.15, ff 49–80 %.
   Verdict pending `ev_tr_mono` 377807 (S1/S2 traces in training may fix the structural cells;
   the cap failure is format-level and will not). `ck_tr_mono` 377805 done: val 0.350 / 0.359 /
   0.350 / 0.350, best 0.359 — below `mono_all`'s direct-answer val, consistent with the L0 arm. If the mono arm also loses, lever 3 closes
   on 7B; a v2 format with explicit event numbering (`12:L7 r=3`) is the only cheap retry.**
   **`ev_tr_mono` 377807 read (2026-09-05) — LEVER 3 CLOSED, null but complementary.**
   `trace_mono` fixes the format by DISTRIBUTION (training on long S1/S2 traces), not by format:
   format_fail 0.011–0.032 (from 0.121–0.740), S1 0.085 → 0.356, trace-v1 unchanged. It then lands
   on `mono_all` exactly: L0 0.392/0.412, L1b 0.382/0.387, L1r 0.384/0.384, L2 0.377/0.378,
   S1 0.356/0.383, S2 0.389/0.405; pooled −1.06 [−3.14, +0.75], every per-condition interval
   covering zero. **But the two are equal AND disagree**: both✓ 0.274, both✗ 0.501, trace-only
   0.107, mono-only 0.118 → oracle union +10.75 [+9.51, +11.98] over `mono_all`, uniform across
   conditions. Second ~10-pt headroom beside any-of-8's, and it is two differently-trained systems
   rather than eight draws from one. Opens H-trace-complement, gated on `rerank` 377946: if 2b
   clears, add `trace_mono` as a second candidate source and re-rank the union. Entry
   `log/transfer/2026-09-05_trace-sft-is-null-but-complementary.md`.**
   **`ck_tr_L0` 377804 read (2026-09-05): held-in L0 val exact_match 0.294 / 0.330 / 0.339 / 0.336
   (ckpt 74 / 148 / 222 / final), best ckpt-222 at 0.339 — against `tuned_L0`'s 0.408 (ckpt-148)
   on the SAME 333 val items. −7 pts on clean code held-in. Still rising at the last epoch (the
   direct-answer arm plateaued at epoch 2), and the extracted-answer format_fail / trace
   truncation are not in the ckpt-select output — `ev_tr_L0` 377806 reports them. Early read:
   trace SFT is not a free lift on L0; the question it exists for is the obfuscated columns.**
3b. **Span-aligned alignment variant** — the one L_align candidate W5 did not test (per-token
   pairing of clean/obfuscated spans via `rename_map`, not the answer slot). Cheap; after 3.
   **SUBMITTED 2026-09-05 as `align.mode: span`.** Per-token pairing via `rename_map` was
   dropped: it exists only for the identifier family and L2 also strips annotations, so
   the correspondence is not 1:1 even there. Instead each side is MEAN-POOLED over its own
   code span per layer (student on obfuscated code, frozen tuned_L0 on the clean parent),
   which covers S1/S2 too and is the literal reading of "make the hidden states match the
   unobfuscated code". `align.resolve_span_mask` recovers the span from token ids by
   re-assembling sentencepiece pieces and locating the frozen `Program:\n` … `\n\nCall:`
   markers; gate `scripts/check_span_mask.py` (dev 377863): recall = precision = 1.000 on
   40 rows × six conditions (span 125–701 tokens). Configs `train/align_span_codellama7b_py_mono.yaml`
   (twin of the W5 config + `mode: span`), `eval/align_span_codellama7b.yaml` (rq2_generic,
   systems `align_span_lam1`, `align_span_lam1_mm`, `align_span_lam3`). Cache stores
   `[N, 6, 4096]` pooled states (`…__best__span.npz`). Chain: `al_span_cache` 377864 →
   `al_span_lam1` 377865 / `al_span_lam1_mm` 377866 / `al_span_lam3` 377867 → `ck_span_*`
   377868/377869/377870 → `ev_span` 377871. Decision rule unchanged from W5 (matched >
   mismatched AND matched − mono_all excl 0 on ≥1 non-L0 condition, no L0 tax); the pooled
   MSE has a different raw scale from the k=4 variant, so λ is not comparable across modes —
   λ=3 is there to bracket, and align_loss is logged separately as before.
   **`al_span_cache` 377864 DONE: 5,019 × 6 layers × 4096, valid 5019/5019, row-0 span decodes to
   exactly the program text (gate `check_span_mask.py` had already passed 1.000/1.000 on dev
   377863). `al_span_lam1` 377865 DONE (3.5 h, 1257 steps, total 0.236). The span objective is
   REAL, not a no-op: align_loss 0.262 → 0.066 train and 0.090 → 0.069 on val, i.e. it
   generalises to held-out programs. But the task term overfits hard — task loss ≈ 0.005 by
   epoch 3 while eval_loss climbs monotonically 0.711 → 1.326, so for THIS arm the checkpoint
   choice carries real weight and `ck_span_lam1` 377868 (val exact_match, not loss) is doing
   the work.**
   **`al_span_lam1_mm` 377866 DONE (3.5 h) — THE CONTROL WORKS, which is what makes the matched
   arm interpretable: with mismatched targets align_loss plateaus at **0.214** against the matched
   arm's **0.066** (3.3×) and never descends, so the matched arm is fitting the CORRECT clean-code
   states, not just any low-rank projection that shrinks a pooled MSE. Total loss 0.388 vs 0.236;
   eval_loss 1.615 vs 1.326. `ck_span_lam1` 377868 best ckpt-838 (val 0.359). `al_span_lam3` 377867
   running; `ck_span_*` 377869/70 done (mismatched best ckpt-419 val 0.3505; λ=3 best ckpt-838 val 0.3745).**
   **`ev_span` 377871 read (2026-09-05) — LEVER 3b CLOSED, PASSES ITS RULE MARGINALLY.**
   λ=3 − mismatched **+1.38 [+0.19, +2.58]*** (S1 +2.65 [+0.80, +4.57]*) and the mismatched control
   sits below mono_all (−0.56) — the alignment signal is REAL and SPECIFIC, corroborated by the
   training-side separation (align_loss 0.066 matched vs 0.214 mismatched). But λ=3 − mono_all is
   **+0.81 [−0.15, +1.89]** pooled and the W5 rule's second clause is carried by ONE cell of six
   (L2 +1.50 [+0.12, +2.99]) that BH-FDR would not keep. Reported as marginal, NOT a win.
   Monotone in λ (val 0.3745 > 0.3594 > 0.3505) → ceiling not found; λ ∈ {6,10} is the obvious
   follow-up, NOT queued (1–2 pts upside vs 34B's +8.56 for the same GPU time). Entry
   `log/modularity/2026-09-05_span-alignment-is-real-but-marginal.md`.**
5. **More data** — extra input cases per program (execution-gated, free) and more programs
   if a source is available; H-saturation is still open.
   **SUBMITTED 2026-09-05.** The parent's `gate_inputs` (5–20 per program; ran on the parent,
   determinism-checked, and verified output-identical on every kept variant by the gate) are
   promoted to training cases: `06_emit_pairs.py --extra-cases 3 --aug-tag cases3` picks up
   to 3 per program, output-diverse first (91 % distinct within the extra set, 77 % new vs
   the canonical three). Bank `data/train/pairs_aug/cases3/` = 38,346 rows, exactly mirroring
   the canonical six (L0 6,693 …). Eval inputs unchanged (`cases[:3]` from base). Configs
   `train/L0_cases_generic_py.yaml`, `train/mono_cases_generic_py.yaml` (`augment_tags:
   [cases3]`, `adapter_root runs/adapters_cases`, epochs 3), `eval/cases_generic.yaml`
   (`rq2_generic` phase → ranks item-for-item against `tuned_L0`/`mono_all`). Chains:
   `tr_cs_L0` 377851 → `ck_cs_L0` 377852; `tr_cs_mono` 377853 → `ck_cs_mono` 377854 →
   `ev_cases` 377855. Question: is the corpus saturated in programs (H-scale ✗) but not in
   labelled behaviour per program?
   **`tr_cs_L0` 377851 DONE (44 min, 441 steps, 9,378 rows, train_loss 0.490 vs `tuned_L0`'s
   0.503 on 4,689 rows, truncation 5/9,378 at 2048). `ck_cs_L0` 377852 done: val exact_match
   0.411 / 0.396 / 0.405 / 0.409 (ckpt 147/294/441/final) — best 0.411 vs `tuned_L0`'s 0.408 on the
   same 333 items, i.e. 3× the labelled cases per program buys +0.3 pts on val. `tr_cs_mono` 377853
   DONE (6.8 h, 2514 steps, 53,682 rows = 2× the canonical 26.8k, train_loss 0.143 vs `mono_all`'s
   comparable schedule, truncation 58/53,682). `ck_cs_mono` 377854 best ckpt-2514 val 0.367.**
   **`ev_cases` 377855 read (2026-09-05) — LEVER 5 CLOSED, H-cases REFUTED.**
   `tuned_L0_cases − tuned_L0` pooled +0.31 [−0.55, +1.17] (2× rows for nothing);
   `mono_cases − mono_all` +1.25 [−0.01, +2.54]; 1 of 12 cells excludes zero (L2 +2.22). Third
   independent "more data" null at 7B after more programs and augmentation → H-saturation.
   Flagged NOT claimed: `mono_cases − tuned_L0_cases` +1.50 [+0.01, +2.97] vs the canonical tie's
   +0.56 — possible data-limited tie, needs its own registration. Entry
   `log/transfer/2026-09-05_more-cases-per-program-is-null.md`.**
6. **CodeLlama-34B-Instruct** — first download died on the login node's 8 GB vmem cap
   (`memory allocation of 67021731 bytes failed`, hf_transfer); resubmitted as CPU job 377794
   on `normal` (`submit.py --gres none`, new option; 377794 hit the same `python python` argv slip, 377795 died because /tmp is node-local; the script now lives at `scripts/hf_snapshot.py`, job 377810), then
   register + go/no-go + `tuned_L0`/`mono_all`. 13B beat 7B by 2–4 pts in every column.
   **DONE 377810 → registered `codellama-34b` (48 × 8192, GQA, 4×16 batch); submitted `bc34` 377812,
   `tr34_L0` 377813 → `ck34_L0` 377815, `tr34_mono` 377814 (30 h wall) → `ck34_mono` 377816 →
   `ev34_grid` 377817 (`rq2_generic --systems base,tuned_L0,mono_all`, `--mem 128G`).**
   **`bc34` read (377812, 2026-09-05):** untuned 34B on heldout L0 0.254 / L1r 0.220 / S2 0.191,
   format_fail 0.254 / 0.209 / 0.137. Base accuracy is flat across scale (7b 0.257, 13b 0.252,
   34b 0.254 on L0) and 34B's L0 format_fail is *double* 7b's (0.129); conditional on a
   well-formed answer it is 0.340 vs 7b 0.295 / 13b 0.280, so the scale signal in the base is
   entirely masked by format. Not a gate for the tuned arms (already queued, tuning removes the
   format failures); it does say the untuned 34B is not a free win.
   **`tr34_mono` 377814 DONE (9.8 h, 1257 steps, train_loss 0.108, truncation 32/26,841 at 2048).
   `ck34_L0` 377815 DONE: val exact_match 0.4985 / 0.4895 / 0.4985 / 0.4985 (ckpt 74/148/222/final)
   — against CodeLlama-7b's 0.408 and Llama-3.1-8B's 0.435 on the SAME 333 val items, i.e. **+9.0
   pts over 7B on val**, by far the largest move any lever has produced. If it holds on heldout
   (`ev34_grid` 377817) scale is the one lever that works. `ck34_mono` 377816 pending.**
   **`ev34_grid` 377817 read (2026-09-05) — H-34b CONFIRMED, CAMPAIGN WINNER.** Heldout:
   L0 0.522, L1b 0.419, L1r 0.468, L2 0.465, S1 0.472, S2 0.484. `tuned_L0` 34b − 7b pooled
   **+8.56 [+7.00, +10.15]**, − 13b +5.17 [+3.78, +6.64]. **The gain is ALL tuning**: 34b−7b base
   is null +1.47 [−0.24, +3.27] while the tuning gap widens +18.04 → +25.13. Exact opposite of the
   Llama-3.1 swap (inherited +2.08, gap flat). RQ2 tie survives at 34B (+0.14 [−1.24, +1.53]) and
   the fingerprint holds on four models; but the L1b gain DOUBLES (+2.41 7b → +5.19 34b) while the
   L0 cost barely moves (−1.74 → −2.63) → new H-breadth-scales. **34B `tuned_L0` is the arm to
   carry into the single H1 `final_eval` batch with the X1 arms.** Entry
   `log/transfer/2026-09-05_scale-is-the-only-lever-that-works.md`.**

7. **H1-adjacent trainable transforms ("X1")** — a *sibling* mechanism family (different string
   encoding scheme, different MBA identities than H1's) as a trainable condition. This is the
   one lever that touches the held-out claim: report it in a separate namespace, never pool
   with the headline systems, and any H1 read of an X1-trained adapter is a human decision
   that spends the final pass. Design goes to the user before generation.
   **APPROVED 2026-09-05 ("ok proceed"); IMPLEMENTED AND SUBMITTED.** `src/obtune/obf/py/x1.py`:
   strings → `_rs([cp ^ k, …], k)` (XOR key 1..255, per-program), arithmetic → `_ar_p/_ar_m/_ar_x`
   helpers (`a+b=(a|b)+(a&b)`, `a−b=(a^b)−2(~a&b)`, `a^b=(a+b)−2(a&b)`, int-guarded, bool
   excluded), int literals → `(n−k)+k` / `k−(k−n)` (≤24 sites); bar `min_total_sites: 3`;
   family `encoding`; Python only; emits none of `h1_marker_patterns` (tested). Registered in
   builder/paths/schema/conditions.yaml; `validate.py` gained an encoding-family purity branch
   (no renaming, helpers defined, mechanism present); 15 tests in `tests/test_transform_x1.py`.
   `05_build_variants.py` now suffixes `coverage_matrix_*` with the condition list when a
   partial build runs (the S3/S4 build had overwritten the six-condition matrix).
   Testset build (377838): X1 = 27/40 python programs; the 13 declines are `too few X1 sites`
   (≤2 arithmetic/literal sites, no strings) — coverage honesty, not a bug. Train build 377836
   (32 workers, `normal`) → `x1_pairs` 377837 → `x1_evitems` 377839 (+ testset items 377840).
   GPU chains (h200, dependent on the pairs job): `tr_X1` 377841 → `ck_X1` 377842;
   `tr_monoX` 377843 (`mono_allX_generic_py.yaml`, seven conditions, train_size 40000) →
   `ck_monoX` 377844; `ev_X1` 377845 (`eval/x1_generic.yaml`: base, formatonly, tuned_L0/S1/S2,
   tuned_X1, mono_all, mono_allX on six + X1, heldout, NO H1). Adapter dirs
   `X1_r32_s17` and `L0-L1b-L1r-L2-S1-S2-X1_r32_s17`. Train build (377836, 4 min): **X1 =
   1649/2231 programs (74 %)**, 4,947 pairs (3,468 train / 264 val / 1,215 heldout eval items);
   per variant median 6 MBA sites (4 literal expansions + 2 helper calls; 80 % have ≥1 helper
   call), 49 % have ≥1 encoded string; size ratio median 4.14× (p95 7.24× — the 4-helper
   prelude dominates short programs; token-length audit vs max_seq_len 2048 is job `x1_len`
   377856, `scripts/x1_lengths.py`); 0 H1-marker hits over all 1,649 variants.
   **Length audit read (377856): X1 train pairs p50 688 / p95 1150 / max 5736 tokens, 24/3468
   over 2048 = 0.69 % — under the 1 % train guard, so `max_seq_len 2048` stands (S1 is 0.49 %,
   L0 0.06 % on the same tokenizer). No config change; the `tr_X1`/`tr_monoX` chains run as queued.**
   **`tr_X1` 377841 DONE (38 min, 162 steps, 3468 rows, truncation 24/3468 = 0.69 % as audited).
   train_loss 0.763 — every other specialist sits at 0.50–0.54 (L0 0.503, S1 0.533 on the same
   162-step schedule). X1 is the hardest condition to fit by a wide margin: the answer requires
   evaluating XOR-decoded strings and MBA helper calls, which a direct-answer model cannot do
   in one token. Expect `tuned_X1` on X1 to sit well under the other specialists' own-condition
   ~0.40; `ck_X1` 377842 → `ev_X1` 377845 report.**
   **`tr_monoX` 377843 DONE (4.2 h, 1419 steps, 30,309 rows = the six-condition 26.8k + X1's
   3.5k, train_loss 0.153, truncation 56/30,309 = 0.18 % at 2048, all of it X1 rows). `ck_monoX`
   377844 → `ev_X1` 377845 next.**
   **`ck_X1` 377842 / `ck_monoX` 377844 FAILED (2026-09-05), `ev_X1` 377845 DependencyNeverSatisfied.
   Cause: the ckpt-select path never called `drop_overlong` — only the scoring path did — so a
   single 2,177-token X1 val prompt against the `max_seq_len + 128 = 2176` window killed the
   selection. This is the same defect as `cand_heldout` 377858 in a third code path. Fixed in
   `eval_vllm.py` (drop once BEFORE the checkpoint loop so every checkpoint is scored on an
   identical item set; `n_val_dropped_overlong` recorded in `ckpt_select.json`). Resubmitted:
   `ck_X1` 377997, `ck_monoX` 377998, `ev_X1` 377999 (afterok both).**
   **Both resubmits COMPLETED (2026-09-05), fix confirmed: each dropped exactly 3 over-long
   prompts (`apps_3529_0::X1::{0,1,2}`) and ran to completion. `ck_X1` val on X1 0.245 / 0.264 /
   0.249 / 0.257 (ckpt 54/108/162/final), best 0.264 — against the six specialists' ~0.40 on
   their own conditions, so X1's own-condition diagonal is ~14 pts below every other
   specialist's, exactly as `tr_X1`'s 0.763 train loss predicted. `ck_monoX` best 0.343 over the
   seven-condition val.**
   **`ev_X1` 377999 FAILED (2026-09-05) — third distinct infrastructure defect on this arm, and
   the most avoidable: `phase: x1_generic` was never added to `schema.py::TrialRow`'s phase
   Literal, so vLLM generated all 1,670 completions and THEN pydantic rejected the first row.
   Added `x1_generic` and `align_span_generic`, and audited every config in `configs/**` against
   the literal (0 remaining mismatches) so this cannot recur silently. Resubmitted as 378459.**
   **`ev_X1` 378459 read (2026-09-05) — H-X1-family first conjunct CONFIRMED, H-mono-X CONFIRMED,
   and a NEW result: X1 IS A TRAINABLE PROXY FOR H1.** X1 heldout (1,214 items / 405 programs):
   base 0.119, formatonly 0.125, mono_all 0.232, tuned_L0 0.270, tuned_S1 0.272, tuned_S2 0.286,
   **mono_allX 0.310, tuned_X1 0.319**. `tuned_X1 − tuned_L0` +4.86 [+2.80, +6.92]*;
   `− tuned_S2` +3.29 [+1.23, +5.52]*; `mono_allX − mono_all` +7.74 [+5.45, +10.21]*;
   `mono_allX − tuned_X1` −0.91 [−2.96, +1.15] (the tie AGAIN, on a 7th condition).
   **Across the six arms measured on BOTH X1 and the spent H1 pilot — same 405 programs —
   r = 0.9992, ρ = 1.000, mean |Δ| = 0.48 pts.** X1 is a free development surface for held-out
   family work. LIMIT: holds only for arms trained on neither column, so tuned_X1/mono_allX X1
   numbers are DIAGONAL and must not predict their H1 numbers. Gate resolved — the X1 arms have
   earned the read. Entry `log/transfer/2026-09-05_x1-is-a-trainable-proxy-for-h1.md`.**
   **The H1 read of the X1 arms is the
   campaign-end final batch, together with the winner — one `final_eval` spend, agreed with
   the user.**

Rules that hold throughout: no H1 read without the human; every new arm is compared to
`tuned_L0` on the six trainable conditions first; `final_eval` stays unspent until the
campaign's winner is chosen on the trainable grid.

## 2026-09-05 — CAMPAIGN RANKING (all W6 arms, trainable grid, H1 NOT read)

`scripts/analysis/31_campaign_ranking.py` → `results/analysis/campaign_ranking_2026-09-05.json`.
64 CodeLlama-7b systems on 9,582 common items, plus the three-system probes at 13b/34b/llama31-8b.
Every arm vs **its own model's** `tuned_L0`; program-clustered bootstrap, 2,000 resamples.

**The whole 7B search space is 1.8 points wide.** Best arm `mono_cases` 0.4043 (+1.82
[+0.41, +3.33]); then `mole_random` +1.36, `mole_router` +1.31, `mole_hardrouter` +1.25,
`mole_uniform` +1.22 — the MoLE cluster, all ~+1.3 and mutually indistinguishable, which is the
routing-is-random finding again. `tuned_L0` itself sits 30th of 64. Nothing on 7B clears +2.

**One scale step is worth 8.6.** 34b `tuned_L0` 0.4717 (+8.56 vs 7b), `mono_all` 0.4731
(+0.14 [−1.23, +1.47] vs its own tuned_L0 — the tie holds); 13b +3.39/+4.16; llama31-8b +1.21
(n.s.). Stated plainly: **every algorithmic lever this campaign tried at 7B fits inside a 1.8-pt
band; capacity alone is worth 8.6 pts.**

Bottom of the table is the sanity check that the ranking is measuring something real:
`base` −18.04, `base_trace` −28.24, `merge_dare_linear` −24.97, `formatonly` −16.37 — all
excluding zero and all in the expected order.

### Proposed H1 `final_eval` batch — ONE submission, needs human authorisation
Chosen on the trainable grid alone (H1 unread), per CLAUDE.md §3.2:
1. `codellama-34b tuned_L0` — campaign winner.
2. `codellama-34b mono_all` — the RQ2 tie at the top of the ladder. H1 is precisely where
   `tuned_L0` BEAT `mono_all` at 7B (+0.041 [+0.018, +0.064]); whether that inverts at 34b is
   the single most valuable unread cell in the project.
3. `codellama-34b base` — the base anchor; without it the 34b TR denominators and the H1
   tuning gap cannot be computed, and it cannot be added later.
4. `tuned_X1`, `mono_allX` (7b) — the pre-registered H-X1-family test. **Gated on `ev_X1`
   378459**: if X1's own-condition diagonal is as weak on heldout as on val (0.264), the arm may
   not be worth the read, and that judgement must be made BEFORE the batch is submitted.
7b `tuned_L0`/`mono_all`/merges on H1 already exist from the spent pilot, so no re-read is needed.

## 2026-09-05 — H1 FINAL READ SPENT. CAMPAIGN CLOSED.

Jobs 378518 (34b: base/tuned_L0/mono_all) + 378519 (7b: tuned_X1/mono_allX), ONE batch, both
submitted before either was looked at. Pre-registration `361d354` predates submission.
**THE H1 BUDGET IS GONE — no H1 number may select, tune or rank anything from here.**

Panel (7b non-X1 rows = spent pilot): base 7b 0.1285 / 34b 0.1433; mono_all 7b 0.2323;
tuned_L0 7b 0.2735; tuned_S1 0.2776; tuned_S2 0.2834 (old leader); **mono_all 34b 0.2965;
mono_allX 7b 0.3089; tuned_X1 7b 0.3180; tuned_L0 34b 0.3213 (NEW LEADER)**.

ALL pre-registered tests confirm:
- H-34b-h1: 34b tuned_L0 vs 7B leader **+3.79 [+1.56, +6.10]***
- **H-rq2-at-scale (DECISIVE): tuned_L0 − mono_all @34b +2.47 [+0.41, +4.78]*** (7B: +4.12*).
  The 7B H1 finding is NOT a small-model artefact. Clean-code-only training beats breadth on the
  unseen obfuscator at BOTH scales. This is the paper's RQ2 headline.
- H-X1-family 2nd conjunct: tuned_X1 vs tuned_S2 **+3.46 [+1.32, +5.51]***
- H-mono-X on H1: **+7.66 [+5.35, +10.04]***
- 34b tuning gap on H1 **+17.79 [+14.81, +20.94]***
- **tuned_X1 (7B) vs tuned_L0 (34B): −0.33 [−2.88, +2.06] — INDISTINGUISHABLE.** Family training
  at 7B = scale at 34B. Opens H-family-beats-scale.

Honest surprise: I pre-registered that the X1 diagonal carries NO info about H1 for X1-trained
arms. Right stance, and empirically the transfer is LOSSLESS — tuned_X1 0.3188→0.3180,
mono_allX 0.3097→0.3089 (0.08 pts each). X1 and H1 are the same problem to this model.

Integrity verified before interpretation (pilot had a prefix-cache collision): base shares
**0.0000** identical outputs with every tuned arm; no pair >0.44; ff 0.014–0.026 tuned.

Entry `log/transfer/2026-09-05_h1-final-read.md`. CLAUDE.md changelog updated.

## 2026-09-05 — OBJECTIVES CAMPAIGN (user: "try all" four new fine-tuning objectives)

Honest framing first: every arm so far shared ONE objective (next-token CE on the answer span);
only 3b changed the loss. The four below change the OBJECTIVE, not the data or the model. H1 is
spent, so the held-out-family read is **X1** everywhere (lossless proxy: 0.08 pts).

| # | objective | mechanism | arms | control |
|---|---|---|---|---|
| O1 | **paired consistency** | L = CE(x_obf) + λ·KL(p_T(·\|x_L0parent) ‖ p_S(·\|x_obf)) at answer tokens; T = frozen tuned_L0 loaded as a 2nd PEFT adapter, no_grad | `cons_lam1`, `cons_lam3` | `cons_same_lam1`: T sees the SAME obfuscated input (plain KD) — separates "consistency across surfaces" from "distillation from a stronger teacher" |
| O2 | **semantic negatives** | verified single-operator mutants (reuses `cft/mutate.py` propose + exec) of the obfuscated rows; mutant + true output = extra CE row; mutant + ORIGINAL output = NEGATIVE row, loss = unlikelihood −log(1−p) at the FIRST token where y_orig diverges from y_mut | `neg_ul` | `neg_data`: same mutant positives, no negative rows (isolates the UL term from the data) |
| O3 | **resampled surfaces** | X1 re-built at seeds 101/202 (`--aug-tag`), 3 surfaces × 1 epoch = same steps as `tuned_X1` (1 surface × 3 epochs) | `x1_resample` | `tuned_X1` itself. Prior LOW: `mono_aug` (4 surfaces, six conds) was null |
| O4 | **curriculum** | init LoRA from `tuned_L0/best`, 1 epoch on the five non-L0 conds at lr 5e-5 | `curr_kl` (O1 loss) | `curr_sft` (plain CE) — order vs objective |

Code: `src/obtune/objectives.py` (one trainer, modes consistency/negatives; `init_adapter`),
`scripts/32_build_negatives.py` → `data/train/negatives/<cond>/python.jsonl` (under TRAIN_ROOT,
read through `paths.load_training_jsonl`, so all quarantine layers apply), `train_sft.py` gains
`train.save_steps` (O3 needs step checkpoints inside its single epoch).

Pre-registered decision rules (commit BEFORE submission; all CIs program-clustered, 2000 resamples):
- H-cons: `cons_lam1 − mono_all` on X1 excludes 0 (>0) AND `cons_lam1 − cons_same_lam1` > 0.
  Read also vs `tuned_L0` on X1 (the standing 7B non-X1 best on the held-out family).
- H-neg: `neg_ul − neg_data` > 0 on X1 excl 0; `neg_data − mono_all` is the data-only read
  (expected null per lever 5).
- H-resample: `x1_resample − tuned_X1` on X1 excl 0.
- H-curr: `curr_kl − tuned_L0` ≥ 0 on L0 (no tax) AND `curr_kl − mono_all` > 0 pooled non-L0;
  `curr_kl − curr_sft` separates the objective from the order.
Anything that fails its rule is reported as null; nothing is tuned on X1 after this read.

Budget: 8 adapters (~3.5–6 h each on h200) + 8 ckpt-selects + 1 eval (7 conds). Smoke
(`--max-steps 4`) on h200 before the full chain.

### 2026-09-05 — objectives campaign: implementation landed, pre-registration commit
- Code: `src/obtune/objectives.py` (consistency / negatives / curriculum-init trainer, TRL-mirrored
  tokenisation, answer-token correspondence assert, dry-run), `scripts/32_build_negatives.py`
  (propose → run_batch → first verified differing mutant per (program, condition) train group,
  one NegativePair each: mutant code + true output + orig output), `scripts/33_smoke_objectives.py`,
  `scripts/analysis/34_objectives.py`. `train_sft.py` gained `save_steps`; `schema.py` gained phase
  `objectives_generic` and arch strings `obj_*`.
- Login-node checks: quarantine lint green; 40/40 student↔teacher answer-token correspondence on
  S1/L2 rows; S1 negatives smoke on 30 groups → 13 kept (AOR 5 / ROR 5 / ICR 3), yield raised with
  `--n-mutants 8`; analysis script runs against the x1_generic controls.
- CPU builds submitted BEFORE this commit (data only, no hypothesis touched): 378683 negatives
  (L0..S2, normal, 32 cpu), 378684→378685 X1 s101 build→pairs, 378686→378687 X1 s202.
- Adapter names (runs/adapters_objectives/codellama-7b/python/): `L0-L1b-L1r-L2-S1-S2_r32_cons_parent_lam{1,3}_s17`,
  `…_cons_same_lam1_s17`, `…_neg_ul_lam1_s17`, `…_neg_data_lam1_s17`, `X1_r32_s17` (resample),
  `L1b-L1r-L2-S1-S2_r32_curr_sft_s17`, `…_curr_cons_parent_lam1_s17`.
- Order of operations from here: commit (this) → smoke job (all six arms, `--max-steps 4`, h200)
  → full chains train → ckpt-select → eval (afterok) → `34_objectives.py` → log entry.
  **Decision rules above are frozen at this commit. Nothing is tuned on X1 after the read.**

### 2026-09-05 — objectives campaign: chains submitted (smoke 378765 green, fix in `04d349a`)

| arm | train | ckpt-select | adapter dir (`runs/adapters_objectives/codellama-7b/python/`) |
|---|---|---|---|
| cons_lam1 | 378779 | 378780 | `L0-L1b-L1r-L2-S1-S2_r32_cons_parent_lam1_s17` |
| cons_lam3 | 378781 | 378782 | `…_cons_parent_lam3_s17` |
| cons_same_lam1 | 378783 | 378784 | `…_cons_same_lam1_s17` |
| neg_ul | 378785 | 378786 | `…_neg_ul_lam1_s17` |
| neg_data | 378787 | 378788 | `…_neg_data_lam1_s17` |
| x1_resample | 378789 | 378790 | `X1_r32_s17` |
| curr_sft | 378791 | 378792 | `L1b-L1r-L2-S1-S2_r32_curr_sft_s17` |
| curr_kl | 378793 | 378794 | `…_curr_cons_parent_lam1_s17` |

Eval `ev_objectives` = **378795**, `afterok` on all eight ckpt-selects, config
`configs/eval/objectives_codellama7b.yaml`, phase `objectives_generic`. Nothing is
tuned after this point; analysis is `scripts/analysis/34_objectives.py` with the
decision rules frozen at `447ecdb`.

### 2026-09-06 — quota incident during the objectives chains

`/work/jvl210002` reached its **1100 GB hard quota** (1099.83 GB) at 00:27 UTC, while five
objective trainers were running. `tr_curr_sft` (378791) finished its single epoch but the
redundant `final/` save died with `Disk quota exceeded`; `checkpoint-346` was already
complete (adapter 320 MB + optimizer + trainer_state), so the arm is intact. Actions taken:
- Deleted only my own smoke output: the twelve `checkpoint-4`/`final` dirs under
  `/work/jvl210002/migration/smoke_objectives/` (7.3 GB of 4-step runs from job 378765).
  The `training_summary.json`/`run_manifest.json` files there were kept. Quota now 99.3 %.
- Removed the README-only stub `…curr_sft_s17/final/` (a 5 KB directory the failed save left
  behind) because `discover_checkpoints` would have enumerated it as a checkpoint.
- Cancelled `ck_curr_sft` 378792 (DependencyNeverSatisfied) and `ev_objectives` 378795;
  resubmitted as **ck_curr_sft 379318** and **ev_objectives 379319** (afterok on
  378782, 378784, 378786, 378788, 378790, 378794, 379318).
- Nothing else was deleted. Candidates for the human to approve: `tmp/uv-cache` (25 GB,
  package cache) and the `optimizer.pt` files inside old checkpoint dirs (see below), which
  are resume state, not results.

## 2026-09-06 — objectives campaign: CLOSED OUT

All 8 arms trained → ckpt-selected → evaluated (56 cells, adapter-applied assertion passed,
format_fail ≤ 0.017) → `34_objectives.py` (18 contrasts, n_boot 2000, clustered by snippet_id)
→ `results/analysis/objectives_2026-09-05.json`. Read against the frozen rules of `447ecdb`;
nothing was tuned on X1 after the read.

| hypothesis | rule | verdict |
|---|---|---|
| H-cons | `cons_lam1 − mono_all` X1 > 0 AND `cons_lam1 − cons_same` > 0 | ✓ +3.05 [+1.24, +4.78]; +0.94 [+0.10, +1.79] (pooled; X1 +0.25 null, +2.31* at λ=3) |
| H-neg | `neg_ul − neg_data` X1 > 0 | ✗ wrong direction: −2.72 [−4.20, −1.15]; data control itself −3.38 on X1 |
| H-resample | `x1_resample − tuned_X1` X1 > 0 | ✗ +0.49 [−1.07, +1.90]; pooled −0.74* |
| H-curr | `curr_kl − tuned_L0` L0 ≥ 0 AND `curr_kl − mono_all` non-L0 > 0 | ✗ second clause +1.06 [−0.12, +2.28]; `curr_kl − curr_sft` +1.32* on all 7 conds |

Headline: `cons_lam3` pooled 0.3919 (highest of the 15 7B systems on the seven-condition set),
X1 0.2834, `cons_lam3 − mono_all` X1 +5.11 [+3.05, +7.08]; vs `tuned_L0` X1 +1.32 [−0.58, +3.13].
Entry: `log/transfer/2026-09-06_consistency-objective-repairs-breadth.md`; ledgers updated.

Still pending, needs human approval (none given yet): quota cleanup. /work is at ~99.7 % of the
1100 GB hard cap. Candidates listed in the quota-incident section above (optimizer.pt 681 files /
343 GB; tmp/uv-cache 25 GB; runs/adapters_overtrain 103 GB). Nothing further deleted.

## 2026-09-06 — quota cleanup DONE (user: "I trust you to make space")
Removed 685 `runs/**/optimizer.pt` (~346 GB) and `tmp/uv-cache` (25 GB). `/work` 99.72 % → 66.24 %.
Weights/results/hf_home untouched; verify_migration OK. Runs are no longer resumable.
`runs/adapters_overtrain` (was 103 GB) kept — its weights are results. Entry: `log/setup/2026-09-06_quota-cleanup.md`.

## 2026-09-06 — objectives round 2: PRE-REGISTRATION (frozen before submission)

Five adapters + one gated eval, all CodeLlama-7b python, read on X1 (H1 spent). Nothing in this
round is used to select anything on X1; the λ read is on the trainable grid.

**Arms** (configs: `train/obj_cons_codellama7b_py.yaml`, `train/obj_currmono_codellama7b_py.yaml`;
eval `eval/objectives2_codellama7b.yaml`, same phase dir `objectives_generic`):
- `cons_lam3_s42`, `cons_lam3_s101` — the headline arm at two more seeds.
- `cons_lam5`, `cons_lam10` — λ sweep at s17.
- `currmono_kl` — curr_kl's recipe (5 non-L0 conds, 1 epoch, lr 5e-5, teacher tuned_L0 on the
  parent) initialised from `mono_all/best` instead of `tuned_L0/best`.
- `mono_all_s42`, `mono_all_s101` re-read on all 7 conditions (seed-matched X1 controls; the
  adapters already exist).

**Decision rules**
- **H-cons-seed** — CONFIRM if `cons_lam3_sN − mono_all_sN` on X1 is > 0 with the cluster-bootstrap
  CI excluding zero for BOTH N ∈ {42, 101}; PARTIAL if one; REFUTE if neither. Secondary: the
  three-seed pooled contrast (s17+s42+s101 vs the matching `mono_all` seeds, clustered by
  snippet_id) and the seed spread of `cons_lam3` on X1 (report the range).
- **H-cons-lam** — read on the TRAINABLE GRID pooled (L0–S2, 6 conditions). CONFIRM if
  `cons_lam10 − cons_lam3` > 0 excl. 0; REFUTE ("over-regularised") if < 0 excl. 0; NULL otherwise.
  `cons_lam5 − cons_lam3` is reported as the monotonicity check. X1 values for λ=5/10 are reported
  but not used to choose λ; no λ is promoted to "the" setting on the basis of X1.
- **H-curr-kl-from-mono** — CONFIRM if `currmono_kl − mono_all` on X1 > 0 excl. 0 AND
  `currmono_kl − tuned_L0` on X1 does not exclude zero from below (penalty removed); REFUTE if the
  first contrast is null or negative. Secondary: `currmono_kl − curr_kl` on X1 and pooled (does
  the start matter once the KL term is applied?), and the L0 tax `currmono_kl − mono_all` on L0.
- Every contrast: `bootstrap_delta` clustered by `snippet_id`, n_boot 2000, same rows as round 1.
  L0 tax reported for every arm. format_fail reported; > 2 % on any cell voids that cell's read.

**Order of operations:** commit this → `submit_chains_r2.sh` (train → ckpt-select afterok, eval
afterok on all five ckpt-selects) → extend `34_objectives.py` with the round-2 contrasts (adding
only these; round-1 contrasts unchanged) → log entry.

### 2026-09-06 — objectives round 2: chains submitted (after pre-registration commit 2b0b841)
| arm | train | ckpt-select | walltime asked |
|---|---|---|---|
| cons_lam3_s42 | 380166 | 380167 | 6 h (round-1 cons runs took 4.4 h) |
| cons_lam3_s101 | 380168 | 380169 | 6 h |
| cons_lam5 | 380170 | 380171 | 6 h |
| cons_lam10 | 380172 | 380173 | 6 h |
| currmono_kl | 380174 | 380175 | 3 h (curr_kl took 1.3 h) |
| **eval** `ev_objectives_r2` | 380176 | afterok on all five ckpt-selects | 1.5 h |
`34_objectives.py` extended with the round-2 contrasts (round-1 contrasts untouched) and a
`pooled_grid` (L0–S2) read for the λ decision; dry-run on round-1 cells OK. Next: when 380176
completes → `python scripts/analysis/34_objectives.py --model codellama-7b --n-boot 2000` →
log entry `log/transfer/2026-09-0X_objectives-round2.md`.

## 2026-09-06 — master report rev 15 (DONE)
- `MASTER_REPORT.md` 4,607 → 4,888 lines: §27 (H1 final read / X1 / scale / null levers / objectives / quota / round 2),
  §1 addendum, §24 + §26 stale H1 advice superseded in place, §25.1 recounted (3,188 cells / 2,546,826 trials,
  `results/analysis/corpus_inventory_2026-09-06.json`), rev 15 changelog. Entry `log/writeup/2026-09-06_master-report-rev15.md`.
- NOTE: `28_master_panel.py` hard-codes `master_panel_2026-09-04.json` as output — do not rerun it without adding `--out`.
- Rev 16 trigger: objectives round 2 (380166–380176) → fold §27.7 into §27.5.

## 2026-09-07 — objectives round 2: READ AND CLOSED
- **H-cons-seed CONFIRMED** (X1 +4.53 s42 / +4.12 s101, three-seed +4.59 [+3.16, +5.99], seed range 0.91 pts).
- **H-cons-lam REFUTED downward** (`cons_lam10 − cons_lam3` grid −0.65 [−1.20, −0.14]); λ=3 stands. ckpt-select
  validation ranked λ=10 first and the held-out grid reversed it — do not promote on the val column.
- **H-curr-kl-from-mono CONFIRMED by 0.16 pts**; `currmono_kl − curr_kl` null on grid, −2.47 [−4.12, −0.91] on X1.
- **OPEN FOR THE HUMAN — H-format-gate:** the pre-registered "format_fail > 2 % voids the cell" rule voids the
  `tuned_L0` control on all 7 conditions and 6 published round-1 cells. Deliberately NOT re-specified after seeing
  the reads. Every verdict reproduces on the format-clean subset. Needs a differential or panel-calibrated rule.
- `34_objectives.py --out` defaults to the 09-05 filename — always pass `--out` explicitly (same as 28_master_panel.py).
- Rev 16 pending: fold MASTER_REPORT §27.7 into §27.5, drop the "single seed" caveat.
- **rev 16 DONE (09-07):** §27.7 = round-2 result; §27.5/§1/§20 cautions retired with replacements;
  format gate published in §27.7 + §24, NOT re-specified; corpus 3,237 / 2,622,398.
  Structural note for next revision: promote §27.5+§27.7 to their own "objectives campaign" section.

## 2026-09-07 — paper experiment plan
- `docs/PAPER_EXPERIMENTS.md`: claims C1–C8 mapped to evidence; Tier 1 = E1/E2 (X1 at 13B/34B +
  tuned_L0 seed band on X1, EVAL ONLY, <1 GPU-h), E3 H-cons-scale, E4 H-cons-teacher, E5 second
  family pair X2/Y2, E6 X1 str-vs-mba ablation. Tier 1 total ~33 GPU-h.
- Scope decision recorded: **Python-only paper**, JS declared as a limitation (node still missing).
- E7: do the GLMM+FDR in Python (statsmodels) rather than waiting on the R env — no multiplicity
  correction currently exists anywhere in the paper.
- E10: human alignment must be RUN or CUT before the framing is written.

### 2026-09-07 — E1/E2 PRE-REGISTRATION (frozen before submission)
Eval-only; all six adapters already exist. Configs `eval/x1_scale.yaml` (13B, 34B) and
`eval/x1_seedband_codellama7b.yaml` (7B). Contrasts: `bootstrap_delta` clustered by `snippet_id`,
n_boot 2000, seed 17, on the 1,214 X1 heldout items / 405 programs the existing X1 cells use.

- **E1 / H-C1-scale-X1** — CONFIRM if `tuned_L0 − mono_all` on X1 excludes zero ABOVE at BOTH 13B
  and 34B; PARTIAL if one; REFUTE if neither. This is the scale replication of C1 on a readable
  column. Reference values: the same contrast is +3.79 pts on X1 at 7B (0.2702 vs 0.2323) and
  +2.47 [+0.41, +4.78] on H1 at 34B.
- **E2 / H-C1-seed-X1** — CONFIRM if `tuned_L0_sN − mono_all_sN` on X1 excludes zero above for BOTH
  N ∈ {42, 101}; PARTIAL if one; REFUTE if neither. Secondary: report the `tuned_L0` X1 seed range
  alongside `cons_lam3`'s 0.91 pts and `mono_all`'s (0.2323/0.2348/0.2331, range 0.25 pts).
- Format-fail is REPORTED, not used as a gate — H-format-gate is open and un-respecified (09-07).
- No H1 cell is read by either job. Neither result may be used to select or tune anything.

### 2026-09-07 — E3 PRE-REGISTRATION (H-cons-scale), frozen before submission
Arms: `cons_lam3` (λ=3, teacher_view parent, teacher = same-scale `tuned_L0/best`) trained at
**13B** and **34B**; configs `train/obj_cons_codellama{13b,34b}_py.yaml`, eval
`eval/objectives_scale.yaml` on all 7 conditions. Controls `tuned_L0` / `mono_all` already exist at
both scales (rq2_generic for L0–S2, x1_generic for X1). Contrasts: bootstrap_delta clustered by
snippet_id, n_boot 2000, seed 17.

- **H-cons-scale** — CONFIRM if `cons_lam3 − mono_all` on **X1** excludes zero ABOVE at **both** 13B
  and 34B; PARTIAL if one; REFUTE if neither. Reference: +5.11 [+3.05, +7.08] at 7B (s17).
- Secondary, reported either way: (a) the `L0` tax `cons_lam3 − tuned_L0` on L0 at each scale — at
  7B it is −0.30 [−1.80, +1.32], i.e. no tax, and the question is whether that survives where
  breadth's tax is larger (34B: −2.63 [−4.49, −0.78]); (b) `cons_lam3 − tuned_L0` pooled non-L0;
  (c) whether the trainable-grid gain tracks the X1 gain across scale.
- λ is NOT re-swept at scale: λ=3 was fixed on the 7B trainable grid (round 2) and carrying it
  unchanged is the point — re-tuning per scale would make the comparison a sweep, not a replication.
- format_fail reported, not gated (H-format-gate open).
- 34B runs with `objective.teacher_device: cuda:1` and `--gres=gpu:2`: student + teacher is ~134 GB
  of a 141 GB card at 34B and OOMs on activations otherwise. New code path — SMOKE FIRST.

### 2026-09-07 — E5 PRE-REGISTRATION (H-family-generalises), frozen before any Y2 read
Second family pair: **X2** (trainable; value crosses a raised `LookupError`, caught in-frame) and
**Y2** (EVAL-ONLY; value crosses a generator `return` read back as `StopIteration.value`). Same
family, different surface — the X1:H1 relationship rebuilt in a family that is neither identifier,
structural, dead-code nor encoding. Generator `src/obtune/obf/py/xy2.py`; ladder entries in
`configs/conditions.yaml`; `Y2` is absent from `paths.TRAINABLE_CONDITIONS`, which is the enforced
guarantee no adapter sees it. Configs: `train/grid_py_X2.yaml`, `eval/xy2_family.yaml`.
Contrasts: bootstrap_delta clustered by `snippet_id`, n_boot 2000, seed 17, on the items every
system in the column shares.

- **H-family-generalises (primary)** — CONFIRM if `tuned_X2 − tuned_L0` on **Y2** excludes zero
  ABOVE. REFUTE if it does not. Reference: the analogous X1→H1 contrast is +4.86 [+2.80, +6.92]
  (on X1) and `tuned_X1 − tuned_S2` +3.46 [+1.32, +5.51] on H1.
- **H-family-specific (secondary, decides the STRENGTH of the claim)** — `tuned_X1 − tuned_L0` on
  **Y2**. `tuned_X1` saw a held-out family, but the WRONG one. If it is null while `tuned_X2` is
  positive, the effect is *family-specific* and the claim is "the model learns the family it was
  shown". If `tuned_X1` is also positive, the effect is generic "exposure to any unusual
  transform", which is a weaker and importantly different reading — reported either way.
- **Also reported, not decisive:** `mono_all − tuned_L0` on Y2 (does breadth hurt on a held-out
  family a second time? the C1 pattern at 7B on H1 is +3.79 for `tuned_L0`); the X2 diagonal
  `tuned_X2 − tuned_L0` on X2 (if the surface is not learnable the arm is dead); and the `L0` tax.
- **Coverage note:** X2 and Y2 gate on IDENTICAL program sets by construction (measured: 117/120
  local, 35/40 testset, X2-only 0 / Y2-only 0), so the comparison carries no coverage confound.
- format_fail reported, not gated (H-format-gate still open).
- Y2 is NOT quarantined: it is regenerable from the module, so a re-read costs nothing. It
  therefore EXTENDS H1's evidence and cannot replace it. No H1 cell is read by any E5 job.

## 2026-09-07 — docs/RQ_SUMMARY.md
- One-page index: 20 approaches, RQ1/RQ2/RQ3 answers, per-condition leaders, and **§4 combined
  (stacked) obfuscation** — NEW analysis of composite cells that existed on the Qwen panel and had
  never been read as a group.
- **KEY NEW FINDING (Qwen-only, needs CodeLlama replication = RQ-A):** `mono_all − tuned_L0` is
  **+3.91 [+2.45, +5.28]** pooled on stacked conditions, while the same contrast is **−4.12** on
  the unseen H1. Breadth buys robustness to RECOMBINATION of seen transforms and pays for it with
  robustness to UNSEEN ones. Stacking cost: tuned_L0 −8.23 pts, mono_all −3.62.
- Order matters: C_L1r_S1 vs C_S1_L1r differ up to 3.6 pts, no consistent direction (RQ-D).
- New RQs proposed A–G; A and B are the same ~2 GPU-h job and are the cheapest high-value work.

### 2026-09-07 — RQ-A / RQ-B PRE-REGISTRATION (composites on CodeLlama), frozen before submission
Eval-only; composite items are model-independent and already exist. Config `eval/composite_generic.yaml`,
5 systems x 6 composites. Contrasts: bootstrap_delta clustered by snippet_id, n_boot 2000, seed 17.

- **RQ-A / H-stack-dissociation** — CONFIRM if `mono_all − tuned_L0` **pooled over the six
  composites** excludes zero ABOVE on CodeLlama-7b, given that the same pair's contrast on the
  unseen column is negative (X1: `tuned_L0 − mono_all` +3.79 [+1.65, +6.09]). That is the
  dissociation: one model, one grid, opposite signs on stacked-seen vs unseen. REFUTE if the
  composite contrast is null or negative. Qwen reference: +3.91 [+2.45, +5.28].
- **RQ-B / H-cons-stacking** — CONFIRM if `cons_lam3 − tuned_L0` pooled on composites excludes zero
  ABOVE **and** `cons_lam3 − mono_all` on composites does not exclude zero from below. That is the
  "dominates mono_all outright" reading: breadth's stacking robustness kept, without its held-out
  tax (X1 +4.59 [+3.16, +5.99]) and without its L0 tax (−0.30 [−1.80, +1.32]).
- Reported either way: per-composite deltas; the order pair `C_L1r_S1` vs `C_S1_L1r` (Qwen shows up
  to 3.6 pts with no consistent direction, RQ-D); `tuned_S2` as the specialist reference.
- format_fail reported, not gated (H-format-gate still open). No H1 cell is read.

## 2026-09-07 — REVISED RQs (RQ1′–RQ4′) ADOPTED; PIPELINE PRE-REGISTRATION (frozen before submission)
User: "let's add these as rqs and run the experiment. we have a lot planned so work on an end to end
autonomous pipeline to run everything." The paper's RQs are re-cut as in `docs/RQ_SUMMARY.md` §6:
**RQ1′** what breadth buys (stacked-seen) and costs (unseen, L0); **RQ2′** the unit of transfer is the
family; **RQ3′** can an objective get both sides; **RQ4′** mechanism and support. Everything below is
driven by `scripts/pipeline/plan.yaml` (47 stages, ~45 GPU-h requested) and applied verbatim by the
analysis scripts; the rules are copied from those scripts, not paraphrased. **No stage reads H1.**
Every contrast = `bootstrap_delta` clustered by `snippet_id`, n_boot 2000, seed 17, 95 % percentile
CI; TOST equivalence uses the 90 % interval at the stated margin. Verdicts are one of CONFIRMED /
REFUTED / PARTIAL / INCONCLUSIVE / PENDING / REPORTED, as the script emits them.

### RQ1′ — breadth's stacked-seen gain vs its unseen/L0 cost
- **RQ-A / RQ-B at scale** (`an_composite_13b`, `an_composite_34b`; `35_composites` on
  `composite_scale`, six depth-2 composites, systems tuned_L0 / mono_all / cons_lam3; `base` omitted —
  it is the only arm whose composite behaviour we do not need, and it is 4 h at 34B). Same rules as the
  2026-09-07 RQ-A/RQ-B pre-registration above: **RQ-A** CONFIRMED iff `mono_all − tuned_L0` pooled
  ci_lo > 0; **RQ-B** CONFIRMED iff `cons_lam3 − tuned_L0` pooled ci_lo > 0 AND `cons_lam3 − mono_all`
  pooled ci_hi ≥ 0. Reported per model; a scale trend is described, never tested (n = 3 models).
- **RQ-C depth leg** (`an_depth`; `composite_depth`, C3_L1r_S3_S4 / C3_S1_S3_S4 / C3_L1r_S1_S4 /
  C4_L1r_S1_S3_S4 on the `--common` program subset, 7B). **RQ-C-persists** CONFIRMED iff
  `mono_all − tuned_L0` pooled over depth-3/4 has ci_lo > 0, else REFUTED. **RQ-C-grows** CONFIRMED iff
  that ci_lo exceeds the depth-2 pooled point estimate (`results/analysis/composites_codellama7b_2026-09-07.json`),
  REFUTED iff ci_hi is below it, else INCONCLUSIVE. **RQ-C-cons-persists** CONFIRMED iff
  `cons_lam3 − tuned_L0` pooled over depth-3/4 has ci_lo > 0.
- **E12 saturation** (`an_saturation`; `40_saturation`; arms tuned_L0 at 4,689 / 2,344 / 1,172 rows,
  mono at 26,841 / 13,420 / 6,710 rows, all r32 s17 codellama-7b). **H-sat-L0** CONFIRMED iff
  `tuned_L0_half − tuned_L0` pooled over the six seen conditions is TOST-equivalent at ±1.0 pt.
  **H-sat-mono** likewise for `mono_half − mono_all`. **H-tax-scales** ("the unseen tax is a
  data-volume effect"): CONFIRMED iff `mono_quarter − tuned_L0_quarter` @ X1 has ci_hi ≥ 0 AND the
  full-data tax `mono_all − tuned_L0` @ X1 is more negative than the quarter tax; REFUTED iff the quarter
  arm already has ci_hi < 0; else INCONCLUSIVE.

### RQ2′ — is the family the unit of transfer?
- (`an_x1split`; `39_x1_split`; X1m = X1's MBA half, X1s = X1's string-encoding half, each trained alone
  at r32 s17; eval on L0 / X1 / X1m / X1s.) **H-family-unit** CONFIRMED iff `tuned_X1m − tuned_L0` @ X1s
  ci_lo > 0 AND `tuned_X1s − tuned_L0` @ X1m ci_lo > 0 (each half transfers to the other — the family,
  not the mechanism, is the unit); PARTIAL if exactly one; REFUTED if neither. **H-whole-ge-parts**
  CONFIRMED iff neither `tuned_X1m − tuned_X1` nor `tuned_X1s − tuned_X1` @ X1 has ci_lo > 0.
  **H-mech-dominance** (which half carries X1's level) and **H-breadth-on-parts** (`mono_all − tuned_L0`
  on X1m and X1s separately) are REPORTED, not gated.
- E5b (a hard second family) stays disabled in the plan: the generator does not exist.

### RQ3′ — can one objective get both sides?
- **E3** (`an_e3`; `36_cons_arms --mode e3`; cons_lam3 at 13B and 34B vs the same models' mono_all /
  tuned_L0, already frozen in the 2026-09-07 E3 pre-registration above; restated for the script):
  **H-E3** CONFIRMED iff `cons_lam3 − mono_all` @ X1 has ci_lo > 0 at BOTH 13B and 34B; PARTIAL if at
  one; REFUTED if at neither. **H-E3-tax** CONFIRMED iff `cons_lam3 − tuned_L0` @ X1 does NOT have
  ci_hi < 0 at both scales (cons pays no unseen tax at scale).
- **E4 teacher variation** (`an_e4`; `--mode e4`; 7B; `cons_tbase` = untuned base teacher,
  `cons_tmono` = mono_all teacher, both parent view, lam 3). **H-E4-view** ("the parent view alone
  beats breadth on the unseen family") CONFIRMED iff `cons_tbase − mono_all` @ X1 ci_lo > 0.
  **H-E4-teacher** ("the tuned clean-code teacher matters") CONFIRMED iff `cons_lam3 − cons_tbase` @ X1
  ci_lo > 0. **H-E4-mono** (`cons_tmono − cons_lam3` @ X1): ci_lo > 0 CONFIRMED (a breadth teacher
  helps), ci_hi < 0 REFUTED (a breadth teacher imports its tax), else INCONCLUSIVE.
- **E8 cross-family replication** (`an_e8`; `--mode e8`; llama31-8b, cons_lam3 with the Llama tuned_L0
  teacher). **H-E8** CONFIRMED iff `cons_lam3 − mono_all` @ X1 ci_lo > 0. **H-E8-seen** CONFIRMED iff
  `cons_lam3 − tuned_L0` pooled over the five obfuscated seen conditions ci_lo > 0. **H-E8-tax**
  CONFIRMED iff `cons_lam3 − tuned_L0` @ X1 does not have ci_hi < 0.

### RQ4′ — mechanism and support
- **E9 attention/knockout on X1** (`an_attention`; `41_attention_x1`; `30_knockout` score mode,
  identifier class, 150 stratified X1 items, arms base / tuned_L0 / mono_all / cons_lam3 / tuned_X1;
  Δ = log P(gold | knocked out) − log P(gold | clean), negative = the knockout hurt; per-item Δ paired
  across arms and bootstrapped by program). **H-attn-cons** CONFIRMED iff mean(Δ_cons − Δ_mono) ci_lo > 0
  (cons depends less on identifier keys). **H-attn-breadth** CONFIRMED iff mean(Δ_mono − Δ_L0) ci_hi < 0
  (breadth makes the model MORE identifier-dependent on the unseen family). **H-attn-order** (Spearman
  between per-arm mean damage and per-arm X1 accuracy, n = 5) is descriptive only. This is support for
  RQ4′, not a causal claim about transfer.
- **E7 FDR** (`an_fdr`; `37_fdr_family`): BH q < 0.05 over the transfer family (5 specialists × 6
  conditions vs tuned_L0_s17, 30 tests) and the arms family (mono_all / cons_lam3 / cons_lam1 /
  tuned_X1 × 7 conditions). p is a two-sided program-cluster-bootstrap p; it stands in for the GLMM
  (statsmodels/lme4 not installed on juno) and is labelled as such. **Reported, gates nothing.**
- **E11 L0 cost** (`an_l0cost`; `38_l0_cost`): every arm's `__L0` cell vs tuned_L0, TOST ±1.0;
  classified L0-free / pays L0 cost / gains on L0 / underpowered. Reported, gates nothing.
- E10 human alignment stays disabled: the tier_icse items are not emitted and there is no script.

### Discipline
- Rules above are final for this batch; nothing is re-specified after a read. X1 is read exactly
  once per new arm by the pipeline's eval stage; no hyperparameter, checkpoint or prompt is chosen on
  X1 (ckpt-select uses the train conditions' val split, as everywhere). H1 is never read.
- Refuted hypotheses are reported as refuted in the pipeline report, the log and the master report.
- `report` stage runs `afterany` on every analysis stage; a failed upstream stage shows as PENDING,
  never as a number.

### 2026-09-07 — pipeline SUBMITTED (after pre-registration commit `0286c5f`)
`python scripts/pipeline/run.py` → 47 stages, jobs **382515–382561** (`runs/pipeline/state.json`).
Roots: `ev_composite_13b` 382515, `bld_depth` 382519 (running), `tr_{L0,mono}_{half,quarter}`
382523–382526, `bld_x1split` 382533 (running), `tr_cons_tbase/tmono` 382543/382544,
`tr_cons_llama` 382549, `ko_x1_*` 382553–382557, `an_fdr` 382559; `an_e3` 382542 waits on the
external 34B chain (382141 → 382142); `report` 382561 is `afterany` on every `an_*`. Requested
walltime 78.5 GPU-h (the 34B composite eval and the three 7 h objective arms dominate). Queue:
everything pending on Priority except `an_fdr`, held by QOSMaxJobsPerUserLimit. Monitor task
`b5er8g695` reports every terminal state. Fix-and-resubmit protocol: `run.py --only <stage>`.
- **X1 split coverage (noted before any read, 382533–382535):** X1m 4,263 pairs / 1,053 held-out
  items; X1s 2,910 pairs / 738 items (X1: 4,947 / 1,215). X1s applies to fewer programs (needs
  string literals). So `tuned_X1s` trains on ~40 % less data than `tuned_X1m`; if H-family-unit is
  PARTIAL with the X1s→X1m leg weak, data volume is a confound to name — E12's half/quarter arms
  calibrate it. Rules unchanged.

## 2026-09-08 — RQ5′ BIDIRECTIONAL (inverse task) PRE-REGISTRATION, frozen before submission
User request: "add Bidirectional ty as another rq (does output prediction also help with input
prediction — this is like a stress test for true understanding)". Distinct from
`paper_bidirectional/` (ATTRIB: forward obfuscation vs reverse deobfuscation *code emission*); this is
value-level: the same held-out items asked backwards.

**Task.** Program + entry point + return value → a call `f(args)` that returns it (CRUXEval-I style).
Prompt: `prompts.SYSTEM_PROMPT_INVERSE` + `USER_TEMPLATE_INVERSE`, one L0 demonstration for EVERY
arm (`one_shot: true`, `prompt_id=inverse_1shot_v1`; the forward template hash is unchanged, tested).
Grading: **execution** (`src/obtune/inverse.py`; single-line `name(args)` parsed by `ast.literal_eval`,
run in the exec sandbox, canonical output == gold output_repr, float tol 1e-6). Any args that produce
the gold value count — the gold args are never the target. `format_fail` = not a single parsable call.
No adapter is trained on the inverse task. **No H1** (`run_grid` refuses `task: input` with H1).
Config `configs/eval/inverse_generic.yaml`, phase `inverse_generic`, heldout items, 7 conditions
(L0 L1b L1r L2 S1 S2 X1), 11 systems. Stages `ev_inverse_core` (base, formatonly, tuned_L0,
mono_all, cons_lam3, tuned_X1) and `ev_inverse_specialists` (tuned_{L1b,L1r,L2,S1,S2}) → `an_inverse`
(`scripts/analysis/42_inverse.py`). Forward numbers are the existing Grid A cells, never re-run.

**Rules** (95 % program-cluster bootstrap; TOST ±1.0 pts at 90 %; seen6 = L0 L1b L1r L2 S1 S2;
obf = L1b L1r L2 S1 S2):
- **Format gate (first).** An arm whose pooled-seen6 inverse `format_fail_rate` > 0.25 is NOT
  INTERPRETABLE and every hypothesis naming it is INCONCLUSIVE, whatever its accuracy. The
  `formatonly − base` contrast is reported as the *format residue* of forward tuning on this task.
- **H-inv-transfer** (primary): forward tuning transfers to the inverse task. CONFIRMED iff
  `tuned_L0 − base @ seen6` ci_lo > 0 AND `tuned_L0 − formatonly @ seen6` ci_lo > 0 (the gain is not
  answer-format adaptation). REFUTED iff `tuned_L0 − base` is TOST-equivalent or ci_hi < 0 — tuning
  is direction-specific ("cognitive specialization", Nikiema et al. 2025, replicates at value level).
  Else INCONCLUSIVE.
- **H-inv-breadth**: `mono_all − tuned_L0 @ obf` (inverse): ci_lo > 0 CONFIRMED; equivalent or
  ci_hi < 0 REFUTED; else INCONCLUSIVE.
- **H-inv-cons**: `cons_lam3 − mono_all @ obf` (inverse): same rule.
- **H-inv-family**: `tuned_X1 − tuned_L0 @ X1` (inverse): same rule.
- **H-inv-diagonal**: each specialist vs tuned_L0 on its own condition (5 contrasts): ≥ 3/5 ci_lo > 0
  CONFIRMED; 0/5 REFUTED; else PARTIAL.
- **Direction ratio** (descriptive, gates nothing): DR(arm) = (inv_arm − inv_base)/(fwd_arm − fwd_base),
  pooled seen6, for formatonly, tuned_L0, mono_all, cons_lam3, tuned_X1 (X1 arm on X1 also reported).
- **BH-FDR** over the five primary contrasts is reported; verdicts use the CIs.
- Expectation stated before the read: base inverse accuracy will be low (the task is harder than
  forward, CRUXEval-I < CRUXEval-O on every model) and format_fail may be high for base — the gate
  exists for that; tuned arms, having learned the *forward* answer format only, may fail the inverse
  format more, which is why every arm gets the one-shot demonstration.
- Nothing is re-specified after the read. X1 is read once per arm by the eval stage. H1 never.

### 2026-09-08 — RQ5′ SUBMITTED (after pre-registration commit `832a6cb`)
`run.py --only ev_inverse_core` → **382620**, `--only ev_inverse_specialists` → **382621**,
`--only an_inverse` → **382622** (afterok both). Both evals pending on QOSMaxJobsPerUserLimit behind
the 09-07 pipeline. The queued `report` 382561 predates `an_inverse`; re-run `--only report` after
382622. Monitor `b79onvos5`. Docs: RQ_SUMMARY §6.3 (pending rows), PAPER_EXPERIMENTS E16, log
`transfer/2026-09-08_bidirectional-inverse-task-submitted.md`. E7 FDR read logged separately
(`writeup/2026-09-08_fdr-over-the-families.md`): 1/30 transfer cells, 8/28 arm cells survive BH.

### 2026-09-08 — `tr_X1s` (382537) refused by the truncation gate; resubmitted as 382803
1.64 % truncation at 2048 (33/2,007 rows, max 4,612 tokens; X1 parent 0.69 %, X1m 0.10 %):
string encoding lengthens every literal and X1s concentrates the rows X1 diluted. Fix: `max_seq_len:
4096` for this arm only (`configs/train/grid_py_X1s.yaml`), keeping the program set intact rather
than dropping the long tail — the split's point is that X1m and X1s see the same programs. Stranded
dependents 382539/382540/382541 cancelled; chain resubmitted `tr_X1s` **382803** → `ck_X1s` 382804 →
`ev_x1split` 382805 (also afterok `ck_X1m` 382538) → `an_x1split` 382806. RQ2′ rules untouched; the
window difference is a caveat to name beside the coverage asymmetry already on file.

### 2026-09-08 — RQ5′ READ (jobs 382620/382621/382622 all COMPLETED; nothing re-specified)
- Format gate: no arm blocked (max `tuned_L0` 0.187). H-inv-transfer **REFUTED** (−1.67 [−3.29, −0.04] vs
  base; −1.22 n.s. vs formatonly; forward +18.09). H-inv-breadth INCONCLUSIVE (+1.45 [−0.04, +2.94]).
  H-inv-cons CONFIRMED (+1.73*) but `cons_lam3 − base` +0.49 n.s. H-inv-family CONFIRMED (+7.00*, q = 0.005;
  `tuned_X1 − base` @ X1 +3.37*). H-inv-diagonal CONFIRMED 3/5 (L1b/S1/S2 vs tuned_L0) — vs base S2 is −3.7.
- Written: `log/transfer/2026-09-08_bidirectional-inverse-task-read.md`, RQ_SUMMARY §6/§6.3, PAPER_EXPERIMENTS E16.
- Next: `run.py --only report` (382561 predates an_inverse). No tuning on the read; no H1.

### 2026-09-08 — E12 SATURATION READ (382531/382532 COMPLETED; rules as frozen)
- H-sat-L0 REFUTED (−1.05*, quarter −2.71*); H-sat-mono CONFIRMED (+0.01 equiv); H-tax-scales CONFIRMED
  (X1 tax −0.49 → −2.31* → −3.79*; `mono_quarter − mono_all` @ X1 +3.29*). Written to
  `log/transfer/2026-09-08_saturation-the-tax-grows-with-data.md`, RQ_SUMMARY §6/§6.1, PAPER_EXPERIMENTS E12.
- `tr_X1s` 382803 passed the 4096-window gate (27 min); chain 382804 → 382805 → 382806 continues.

### 2026-09-08 — E3 READ (382142/382542 COMPLETED; rules as frozen)
- H-E3 CONFIRMED (13B +3.95*, 34B +3.38* for `cons_lam3 − mono_all` @ X1); H-E3-tax CONFIRMED (−0.33 / +0.74 vs
  `tuned_L0`). Written to `log/transfer/2026-09-08_consistency-survives-scale.md`, RQ_SUMMARY §6/§6.1, PAPER_EXPERIMENTS E3.
- Remaining: `ev_composite_34b` 382516 → `an_composite_34b`; E4 (`ck_cons_tmono` → `ev_teacher` → `an_e4`); E8 (`ev_llama` → `an_e8`);
  X1s chain 382804–382806; `an_l0cost`; `report` 383102.

### 2026-09-08 — E8 READ (382551/382552 COMPLETED; rules as frozen)
- H-E8 +3.46*, H-E8-seen +2.53*, H-E8-tax +0.58 (ci_hi > 0) — all CONFIRMED on Llama-3.1-8B. Written to
  `log/transfer/2026-09-08_consistency-replicates-on-llama.md`, RQ_SUMMARY §6/§6.1, PAPER_EXPERIMENTS E8.

### 2026-09-08 — E6 X1-SPLIT READ (382805/382806 COMPLETED; rules as frozen)
- H-family-unit REFUTED (+1.49 n.s. / −0.10); H-whole-ge-parts CONFIRMED (−0.49 / −0.41). Reported: either half
  +4.12 / +4.20 on X1 vs whole +4.61; breadth tax −4.94* / −3.93* on the halves. Written to
  `log/transfer/2026-09-08_x1-split-mechanism-not-family.md`, RQ_SUMMARY §6/§6.2, PAPER_EXPERIMENTS E6.

### 2026-09-08 — reads: composite_34b, E4, E11 (pipeline fully read)
- **composite_34b (382518):** RQ-A +3.05 [+1.60, +4.50]*, RQ-B +5.63*, `cons_lam3 − mono_all` +2.58
  [+1.26, +3.90]* → H-cons-stack-strict CONFIRMED at 13B (+1.36 [+0.18, +2.55]) and 34B. §6.1 34B
  cell filled. `log/transfer/2026-09-08_composites-at-34b.md`.
- **E4 (382548):** H-E4-view REFUTED (`cons_tbase − mono_all` @ X1 −8.98*), H-E4-teacher CONFIRMED
  (+13.84*), H-E4-mono REFUTED (`cons_tmono − cons_lam3` @ X1 −4.20*; seen −0.39 n.s.). Student X1 ≈
  teacher X1 + ~1 pt in all three teacher choices → seen gain is the SFT term, unseen number is
  distilled. RQ3′ claim narrowed to "distil from a clean-code-*tuned* teacher on the parent".
  `log/transfer/2026-09-08_teacher-is-the-ingredient.md`.
- **E11 (382560):** 60 arms: 21 pay / 0 gain / 1 L0-free (seed twin) / 38 underpowered at TOST ±1.0.
  Instrument lesson: n = 557 gives ±1.5–2 pt CIs; "no L0 tax" must be written as "no detectable
  cost". Margin stays ±1.0 (no post-hoc relaxation). Stratification by answer format / length still
  open. `log/transfer/2026-09-08_l0-cost-classified.md`.
- **State:** all 47 stages + external 34B chain terminal and read. Open follow-ups, none submitted:
  E11 stratification (CPU); `an_fdr` re-run over the enlarged arms family (documented family change);
  master report revision.

### 2026-09-08 — PRE-REGISTRATION (frozen before any of the three follow-ups is run)
Written and committed **before** `43_l0_stratify.py` and the enlarged-family `37_fdr_family.py`
exist as runnable code, per the campaign's standing rule. Nothing below may be re-specified after
a read; refuted is reported as refuted. NO stage reads H1.

**E11b — where on L0 the cost lands** (`an_l0strat`, `scripts/analysis/43_l0_stratify.py`,
codellama-7b, CPU). E11's classification (read 09-08) said *which* arms pay; §22.6's open question
is *where*. Item metadata joins from `data/eval/heldout/items/L0/python.jsonl` (1,671 items / 557
programs / Grid B — the exact item set every 7B L0 cell was graded on).
- **Strata, fixed now:**
  1. **Answer-format class** of the gold `output_repr`, by a deterministic classifier on the literal
     string: `list` (`[`), `tuple` (`(`), `dict_set` (`{`), `str` (quote), `bool_none`
     (true/false/null/True/False/None), `int` (`^-?\d+$`), `float` (numeric with `.`/`e`), else
     `other`. A class is **common** iff it holds **≥ 10 %** of the 1,671 items; every remaining class
     is pooled into **unusual**. The 10 % threshold is fixed here, before the distribution is looked at.
  2. **Program length**: `meta.loc` of the L0 program, **terciles over the 557 evaluated programs**
     (T1 short / T2 mid / T3 long), boundaries from the evaluated set itself.
  3. **Answer length**: `len(output_repr)` in characters, item-level terciles. Exploratory.
- **Estimand.** Δ(arm, stratum) = 100·(acc_arm − acc_ref) on that stratum. Reference = the pooled
  clean-code control {`tuned_L0`, `tuned_L0_s42`} (two seeds). Program-clustered bootstrap, 2,000
  draws, seed 17; **one resample of programs per draw, every stratum recomputed on it**, so
  between-stratum differences are paired and their CIs are valid.
- **Primary unit:** `mono_all` pooled over {`mono_all`, `mono_all_s42`, `mono_all_s101`} — pooling
  seeds is the power fix the E11 read identified, and breadth's L0 cost is the fingerprint §22.6 is
  about. Reported but **not** verdicted: `cons_lam3` (3 seeds), `tuned_X1`, and `base` as a reference
  pattern (its −17 must land somewhere; if it too is flat, the strata are the wrong ones and the
  read says so).
- **H-L0-format** ("the cost concentrates on unusual answer formats"): CONFIRMED iff, for the primary
  unit, Δ(unusual) − Δ(common) has **ci_hi < 0**; REFUTED iff that interval lies inside **±1.0**
  (the same TOST margin as E11); else INCONCLUSIVE.
- **H-L0-length** ("the cost concentrates on long programs"): CONFIRMED iff Δ(T3) − Δ(T1) has
  **ci_hi < 0**; REFUTED iff inside ±1.0; else INCONCLUSIVE.
- **H-L0-answerlen**: same statistic on answer-length terciles. **Reported, not verdicted.**
- Gates nothing. If both are REFUTED or INCONCLUSIVE the honest conclusion is that the L0 cost is
  **diffuse** — that is a finding about the phenomenon, and §22.6 gets it as an answer, not a TODO.

**E7b — FDR family enlargement** (`an_fdr2`, same `scripts/analysis/37_fdr_family.py`, new families).
- The two families pre-registered 2026-09-07 — `transfer` (30 tests) and `arms` (28 tests) — are
  **primary and frozen**; their q-values are re-reported unchanged and no claim moves on the new ones.
- Added as a **conservative robustness check only** (enlarging a family can only raise q, never lower
  it — so nothing can be upgraded by this, only survive or fail it):
  - **`arms_all`**: every system holding all seven generic cells (L0 + the five seen + X1),
    **discovered mechanically** from the campaign's generic phases — no hand-picking, no arm added
    because of how its number came out — × 7 conditions vs `tuned_L0`.
  - **`composites`**: {`mono_all`, `cons_lam3`} × the six depth-2 composites vs `tuned_L0`, 7B
    (12 tests) — RQ-A/RQ-B have never been multiplicity-corrected.
- Rule unchanged: a cell survives iff **q < 0.05**. Reported; gates nothing.

**Master report rev 18.** Editorial, no new numbers: a §29 for the pipeline campaign (every stage,
every verdict including the refutations), §1 amended where the pipeline narrowed a headline claim
(RQ3′ is teacher-distillation, not learned invariance), Contents, scope counts, Changelog.

### 2026-09-08 — reads: E11b stratification, E7b enlarged FDR, master report rev 18
- **E11b (`an_l0strat` 383161):** **H-L0-format INCONCLUSIVE** by the frozen one-sided rule — but the
  observed effect is a *significant reversal*: `mono_all` (3 seeds) loses on **common** answer types
  (−2.38 [−3.94, −0.78]) and not at all on the unusual tail (+2.32); unusual − common **+4.70**
  [+0.44, +8.89]. Whole cost sits on **short** answers (−4.16) with none on long (+0.30).
  **H-L0-length INCONCLUSIVE** (−2.00 [−5.87, +2.20]); `base` localizes on length in the same strata
  (−7.36 [−13.67, −1.13]), so the null is a bound, not an instrument failure. Rules NOT re-specified.
  **Lesson for the next pre-registration: a one-sided rule needs an explicit branch for a significant
  reversal.** Confound to state in the paper: "unusual format" and "easy item" are the same stratum.
  `log/transfer/2026-09-08_where-the-l0-cost-lands.md`.
- **E7b (`an_fdr2` 383162):** primary families reproduce **byte-identically** (58/58 rows). Enlarged
  `arms_all` 203 tests / 69 survive, **none of the eight primary survivors lost**; `mono_all` @ X1
  q = 0.014, `tuned_X1` @ X1 q = 0.005; `cons_lam3 − tuned_L0` @ X1 still q = 0.44. `composites`
  10/12 (RQ-B 6/6, RQ-A 4/6). **Open gap, deliberately not closed:** every family is controlled
  against `tuned_L0`, so `cons_lam3 − mono_all` @ X1 is uncorrected — pre-register a
  `mono_all`-controlled family BEFORE the next read; do not add it after noticing.
  `log/writeup/2026-09-08_fdr-family-enlarged.md`.
- **Master report rev 18:** §29 added (6 subsections, the whole campaign), §1 *Added 8 Sep* block
  narrows RQ3′ (teacher distillation) and RQ2′ (shared surface) where the claims are first made,
  RQ4′ loses its causal leg, "no L0 tax" → "no detectable cost at n = 557", nine refutations gathered
  in §29.6. 5,176 → 5,522 lines. Corpus recounted: **3,564 cells / 3,104,044 trials**, panel 1,141.
- **State:** 52 pipeline stages, all terminal and read. Next: the paper draft. Blocked/parked: E5b
  (needs a hard-family generator), E10 (needs tier_icse items graded), all JavaScript (`node`), the
  GLMM (R stack).

### 2026-09-08 — PRE-REGISTRATION #2 (frozen before submission; the "open items" wave)
The 09-08 reads left six open items. Four turned out not to be blocked at all, and the reason is
worth recording: **`node` blocks *regenerating* the JavaScript corpus, not *using* it**, and the
corpus transferred intact. Verified before writing any config — `scripts/check_manifest.py` passes
on the whole tree (SHA manifests **and** the H1-marker content scan), the JS banks hold 2,022 train
pairs and 504 heldout items per condition plus the six depth-2 composites, and network access to
PyPI/CRAN/nodejs.org works from the login node. NO stage below reads H1.

**A. E13 / cross-language — the paper's Python-only scope, tested** (`tr_js_L0` → `ck_js_L0` →
`tr_js_mono`/`tr_js_cons` → `ck_*` → `ev_crosslang_js` → `an_crosslang`). CodeLlama-7b, seed 17,
`configs/eval/crosslang_js.yaml`: `base` / `tuned_L0` / `mono_all` / `cons_lam3` on the six seen
conditions and the six depth-2 composites. Sequence lengths measured first (max 1,247 tokens; 0.00 %
over 2048), so the inherited window stands and no truncation-gate refusal is expected.
- **H-xlang-stack** (RQ-A in a second language): `mono_all − tuned_L0` pooled over the six JS
  composites — ci_lo > 0 CONFIRMED, ci_hi < 0 REFUTED, else INCONCLUSIVE.
- **H-xlang-cons-seen** (RQ3′ in a second language): `cons_lam3 − tuned_L0` pooled over the five
  obfuscated seen conditions — same three-way rule.
- **H-xlang-cons-stack**: `cons_lam3 − mono_all` on the six composites — same three-way rule.
- **H-xlang-L0** (breadth's clean-code cost replicates): `mono_all − tuned_L0` @ L0 — ci_hi < 0
  CONFIRMED, inside ±1.0 REFUTED, else INCONCLUSIVE.
- **H-xlang-volume** — **REPORTED, not verdicted**, and the prediction is put on record *now* so it
  is falsifiable either way: JS trains on ~12.1k rows against Python's ~26.8k, and E12 showed
  breadth's taxes grow with data volume, so **the JS L0 cost should be the smaller one** (Python:
  −1.32). No verdict is claimed, because a cross-language magnitude comparison is confounded by the
  programs, the tokenizer and the ladder's per-language surface all at once.
- **Not claimed here:** any unseen-family number. X1 is Python-only by construction and no JS X1
  generator exists; H1 is spent. The cross-language read covers the "buy" side and the L0 cost only,
  and must say so.

**B. E7c — the `mono_all`-controlled FDR family** (`an_fdr3`). The gap the 09-08 E7b read recorded
and deliberately did not close on the spot: every existing family is controlled against `tuned_L0`,
so RQ3′'s headline `cons_lam3 − mono_all` @ X1 has never been corrected. Family membership is again
**discovered mechanically** — every system holding all seven generic cells — now contrasted against
**`mono_all`**, 7 conditions. Rule unchanged: survives iff q < 0.05. Reported; gates nothing. This is
the family being frozen *before* its read, which is the whole point of deferring it on 09-08.

**C. E7d — the GLMM the charter actually asks for** (`an_glmm`). CLAUDE.md §4 specifies item-level
binomial GLMMs with crossed random effects for program × model; every report to date substitutes a
program-clustered bootstrap and says so. `statsmodels` is installable (network works) and goes in a
**separate venv** (`envs/obtune-stats`) so the pinned training env is not touched.
`BinomialBayesMixedGLM` with crossed variance components for `program_id` and `system` on the 7B
generic grid. **REPORTED, gates nothing, and it does not replace a single existing number**: it is
reported as agreement or disagreement with the bootstrap intervals. Rule fixed now: for each of the
campaign's four headline contrasts the GLMM "agrees" iff its posterior mean has the same sign as the
bootstrap point **and** its 95 % credible interval excludes zero iff the bootstrap CI did. Any
disagreement is reported as a disagreement, not resolved in favour of whichever is convenient.

**D. E11c — breaking E11b's format/difficulty confound** (`an_l0strat2`). E11b could not separate
"unusual answer format" from "easy item" because `bool_none` is both. Fix, fixed now: recompute the
format contrast on a **difficulty-matched subsample** — bin items by the control's own per-item
accuracy (0, partial, 1 over the control's trials for that item) and compare common vs unusual
*within* each bin, then pool the within-bin deltas. **H-L0-format-matched**: ci_hi < 0 CONFIRMED
(cost concentrates on unusual formats once difficulty is held), ci_lo > 0 **CONFIRMED-REVERSED**
(it concentrates on common formats), inside ±1.0 REFUTED, else INCONCLUSIVE. **The rule is two-sided
this time** — E11b's one-sided rule had no branch for the reversal it found, and that was a rule
design error, recorded then and corrected here.

**E. E14 — the `mono_all` log P(gold) anomaly** (`an_logp`). Unplanned observation from `an_attention`:
`mono_all`'s clean log P(gold) on X1 is −11.4 against −6.3 for `tuned_L0` and `cons_lam3`, sitting
exactly where the unseen-family tax is. **REPORTED, not verdicted** — it is one number from an
instrument that turned out inert, so the read's job is to establish whether it is real (present on
other conditions and other arms, not an artifact of the attention subset) and nothing more.

**E14 amendment (recorded before submission, same day).** The X1 knockout dumps carry all five arms;
`L0` and `S2` carry only `base` + the matching specialist, so the comparison the anomaly needs —
is `mono_all`'s log P(gold) deficit *specific to the unseen family* or *global*? — cannot be made on
existing files. Six more score-mode extractions are therefore submitted (`ko_{l0,s2}_{tuned_L0,
mono_all,cons_lam3}`, ~2 min each, same script, same 150-item cap, same identifier class). E14 stays
**REPORTED, not verdicted**; this only makes the reported comparison possible.

### 2026-09-08 — PRE-REGISTRATION #3 (E10 human alignment; frozen before the eval is submitted)
E10 has been "disabled, not pretended" since the plan was written, on the grounds that it needs the
`tier_icse` items emitted and graded plus the Paper-2 item map. Checked before assuming: the map is
not missing — `data/human/paper2_graded.csv` holds **600 graded responses from 50 participants over
98 item cells**, and every one of those 98 cells matches a legacy row. `scripts/47_emit_icse_items.py`
now emits all 350 rows (320 parse; the 30 skipped are LeetCode keyword-call rows **outside** the
human set, so human coverage is 98/98). Labels are `T_*` (`schema.TierCondition`), outside
`AnyCondition`, never trainable.
- **Setup:** `ev_human_align_py` (and `_js`, after the JS arms exist) → `an_human_align`
  (`scripts/analysis/48_human_align.py`). Arms `base` / `tuned_L0` / `mono_all` / `cons_lam3` on
  `T_L0…T_L3`. Human accuracy per cell = fraction of that cell's responses graded `Correct`
  (case-normalised; ~6.1 responses per cell, min 5). Model accuracy per cell = mean `correct`.
  Bootstrap clusters by **program_id** (70 programs), never by cell.
- **H-human-base** (does the untuned model order items like people?): item-level Spearman ρ between
  `base` accuracy and human accuracy over the 98 cells. CONFIRMED iff ci_lo > 0, REFUTED iff
  ci_hi < 0, else INCONCLUSIVE.
- **H-human-shift** (the charter's actual question — does tuning move models toward or away from
  human difficulty orderings?): Δρ = ρ(`tuned_L0`) − ρ(`base`), paired on the same bootstrap draws.
  ci_lo > 0 **TOWARD**, ci_hi < 0 **AWAY**, else NO DETECTABLE SHIFT. Same statistic reported for
  `mono_all` and `cons_lam3`, verdicted only for `tuned_L0` (one arm, one rule).
- **H-human-tier** — condition level, 5 tiers: report the human and model orderings and their rank
  correlation. **REPORTED, never verdicted**: n = 5.
- **Paper-3 (n = 73, `paper3_graded.csv`) is used at CONDITION level only**, per CLAUDE.md — 6 items
  cannot support an item-level ρ, and saying so is part of the contribution.
- **Mandatory sensitivity check, fixed now:** the study's key carries its own spelling (`FALSE`,
  `True`). The read reports strict grading AND a case/whitespace-insensitive regrade from
  `output_parsed`, and if they disagree by more than 2 pts on any arm the strict number is reported
  as an underestimate rather than quietly replaced.
- Gates nothing. If ρ is flat this is a null and gets written as one.

**E13 corrections and gates, recorded BEFORE the read (2026-09-08).**
1. **Split leakage checked explicitly** (§4 item 1, the first silent failure on the list). The JS
   `data/train/pairs/<cond>/javascript.jsonl` files carry **all three splits**, and the training
   loader filters to `train`. Verified: `train` 473 programs, `val` 33, `test` 168, and the 168 test
   programs are **exactly** the heldout eval set with **zero** overlap against `train` or `val`.
   No leakage.
2. **The pre-registration's data-volume figure was wrong and is corrected here, before any result is
   looked at.** It said "JS trains on ~12.1k rows against Python's ~26.8k" — that 12.1k counted all
   splits. The **train** splits are **JS 8,490 rows / 473 programs** against **Python 26,841 / 1,563**,
   so JS is **32 %** of Python's volume, not 45 %. This sharpens H-xlang-volume rather than changing
   it: 32 % is close to E12's *quarter* arm, where breadth's taxes essentially vanished
   (`mono_quarter` X1 tax −0.49 n.s.; `mono_quarter − mono_all` @ X1 +3.29). The prediction on record
   is therefore that **breadth's JS L0 cost should be small or undetectable and its stacked-seen gain
   should still be there**. H-xlang-volume remains REPORTED, not verdicted — the confounds named in
   the pre-registration (different programs, tokenizer, per-language ladder surface) are untouched by
   this correction.

### 2026-09-08 — reads: E13 cross-language, E10 human alignment (the open-items wave is complete)
- **E13 (`an_crosslang` 383171):** H-xlang-cons-seen **CONFIRMED** +7.35 [+4.93, +9.72];
  H-xlang-cons-stack **CONFIRMED** +4.91 [+2.68, +7.29]; H-xlang-stack **INCONCLUSIVE** +2.55
  [−0.30, +5.31]; H-xlang-L0 **INCONCLUSIVE** −3.17 [−6.75, +0.20]. `cons_lam3` best on all 12
  columns and **+3.37 [+0.79, +5.95] over `tuned_L0` on L0** (no Python counterpart).
  **Breadth's stacking gain is a failure to replicate, not low power**: three of six composites
  negative, pooled figure carried by `C_S4_S3` +14.09, where Python had 6/6 positive at three scales.
  **H-xlang-volume's pre-read prediction was WRONG** (−3.17 vs Python −1.32 at 32 % volume) — written
  up as wrong. Checkpoint selector does corroborate the volume story: JS `mono_all` peaks epoch 1,
  Python's epoch 2. No unseen-family column (X1 Python-only) — the tax half is untested in JS.
  `log/transfer/2026-09-08_crosslanguage-javascript.md`.
- **E10 (`48_human_align.py`, 383195/383200):** **H-human-shift AWAY** — `tuned_L0 − base`
  Δρ = −0.303 [−0.575, −0.028]; `mono_all` −0.174, `cons_lam3` −0.244 (same sign, n.s.; only
  `tuned_L0` verdicted per the rule). H-human-base INCONCLUSIVE (+0.132). Condition level: human
  accuracy falls monotonically across the ladder, `base` +0.82 rank corr, every tuned arm negative
  and best on `T_L3`. Claim C8 answered for the first time.
  `log/human-align/2026-09-08_tuning-moves-away-from-humans.md`.
- **Standing lesson from this wave, worth carrying:** four of the six "blocked" items were not
  blocked — the blocker notes had gone stale and nobody re-tested them. **Re-test a blocker before
  believing it.** `node` blocked regeneration not use; E10's "missing" map was on disk; statsmodels
  installs fine into a side venv. Only E5b was genuinely unbuilt.
- **Open after this wave:** a JS X1 (needs a node toolchain — installable, no root required) so the
  cross-language *tax* can be measured; a second JS seed; E5b's generator against its respecified
  design; Paper-3 (n = 73) at condition level; a calibration curve per arm (E14 follow-up, CPU-only).

## 2026-09-08 — paper framing written (no experiment)

`docs/PAPER_FRAMING.md`: the spine is *fluency, not invariance*, a characterisation paper. Four
contributions P1–P4 (labels chosen not to collide with `PAPER_EXPERIMENTS.md` C1–C8). Every number
is an already-published one, cross-referenced to its log entry; nothing was read. Recorded
correction: the first instrument is "the ladder cannot discriminate" (TR 0.906, 1/30 after FDR),
not "transfer collapses". Entry: `log/writeup/2026-09-08_paper-framing.md`.

## 2026-09-09 — paper plan re-cut to RQ1–RQ4 (no experiment; F1–F9 drafted, NOT pre-registered yet)

User fixed four RQs (composition / what is learned / anchoring / robustness) with stated findings.
`docs/PAPER_FRAMING.md` rewritten as an evidence map with a status per finding; `docs/PAPER_EXPERIMENTS.md`
§7 lists F1–F9. Nothing was read; nothing was submitted.

What the record does NOT support as stated (the paper must use the narrower form):
- "All three composition strategies fail" — breadth WINS on stacked-seen (+3.49/+2.90/+3.05; depth 3/4 +4.15);
  it fails on unseen (−3.79/−4.28/−2.64) and L0 (−1.74/−2.34/−2.63).
- "Merging fails through contrasting task-vector geometries" — refuted 08-17 (cross-seed L0 bank cos 0.053,
  sign conflict 0.487, merges fine). Report merging's failure without that mechanism unless F1b says otherwise.
- "Consistent performance on the reverse task" — `cons_lam3 − base` +0.49 [−1.38, +2.30]: undamaged, not improved.
- Unseen-family number of `cons_lam3` is the teacher's (E4); 7th of 33 on X1.

Unmeasured: routing/merging on any CodeLlama composite; router decision on a stack; any stack containing an
unseen family; specialists on CodeLlama composites (RQ2's "stacking destroys the cue"); compute-matched control
for the consistency arm.

F-order on the user's go: **F2** (six X1/X1m/X1s-containing composites, 10 systems, ~1.5 GPU-h) → **F1** (MoLE ×4,
merges ×5, specialists ×3 on the ten existing composites + gate dump, ~2 GPU-h) → F3/F3a/F1b (CPU) → **F4**
(`cons_lam0`, paired SFT without KL, 4.4 h/seed) → F5, F7, F8; F6 = E5b stays design-gated.
Rules are drafted in §7 and must be copied here verbatim and committed BEFORE the first F-job is submitted.
**H1 is never stacked, never read; every unseen component is X1.** Calibrate `size_cap` for the X1 composites
on real programs before the full build (conditions_composite.yaml header rule); record the common subset
before any read.

## 2026-09-09 — SCOPE RULE: no Chinese-origin models (user). Panel + dataset plan written, nothing run.

- `models.yaml`: qwen25c-* `role: barred`; `transpiler: llama31-8b`; `candidates:` block (not resolvable).
- Withdrawn from evidence: Qwen composites (+3.91) and the Qwen geometry refutation → **F1b is now required**.
- Recommended panel (docs/MODEL_AND_DATA_SELECTION.md §3): StarCoder2-15B-Instruct > Gemma-3-12B-it (on disk)
  > Llama-3.1-8B pretrained (on disk) > CodeGemma-7B-it > Granite-3.1-8B / Mistral-7B-v0.3; OLMo-2 if
  contamination is to be measured. Gate before any adapter: basecheck ff ≤ 0.15, template/plain-text path,
  truncation re-gate, loss-mask gate, adapter-applied assert, tuned_L0 clears base beyond the seed band.
- Dataset: training corpus untouched. Eval-only columns D1–D5. Node: x86_64 + glibc 2.34 → official tarball
  runs in user space; install under $OBTUNE_ROOT/../tools/node and add to env.sh PATH.
- Awaiting: user's panel size decision (5 vs 3). Then downloads + basecheck configs; no adapters until gates pass.

## 2026-09-09 — FIVE-MODEL PANEL ADOPTED (user: "let's try five models"); GATE RULE PRE-REGISTERED

Panel keys in models.yaml (role: candidate_main): starcoder2-15b, gemma3-12b, codegemma-7b,
granite31-8b, llama31-8b-base (pretrained). Alternates under `candidates:` (Mistral-7B-v0.3, OLMo-2-13B).

**GATE RULE, frozen before any read:** a candidate enters the panel iff untuned format_fail <= 0.15 on L0
AND untuned L0 accuracy is in a band where a +/-4-pt contrast is visible (not floor, not saturating).
Every gate read is REPORTED whatever the verdict. No gate reads X1 or H1.
Then per model that passes: truncation re-gate at 2048 on 1500 mono rows, loss-mask gate
(inspect_batch.py), adapter-applied assert on the first eval, and tuned_L0 must clear base beyond the
seed band before mono_all/cons_lam3 are queued.

Jobs: downloads 385346 (StarCoder2) / 385353 (CodeGemma) / 385360 (Granite); gates 385500 (gemma3-12b),
385501 (llama31-8b-base). All PENDING on QOSMaxJobsPerUserLimit behind the nla arrays.

**Code change that had to happen first (log/setup/2026-09-09_five-model-panel.md):** 3 of 5 models
cannot take the system role prompts.py emits. prompts.py now has ONE adaptation layer
(template_mode/adapt_messages/render_plain/to_trl_example); train_sft, measure_truncation,
objectives._ids, attention/capture, inspect_batch all route through it. Identity in `system` mode ->
no existing adapter or cell is affected. 30 tests in tests/test_template_adaptation.py.
Gemma-3 needs peft_exclude_modules (vision tower) — wired into LoraConfig.

## 2026-09-09 — QUOTA CLEANUP (user approved: "ok proceed"). 125 GB freed, 0 damage.

/work is quota'd PER USER and SHARED ACROSS PROJECTS: 1000 GB soft / 1100 hard. Was 1058 (42 GB from
the stop) and falling ~15 GB/h as transcoders/nla ran. Now **965.4 GB, 134.6 GB headroom**.

Deleted: 218 non-selected epoch checkpoints (98.2 GB) + 11 orphaned .incomplete blobs (23.8 GB,
codellama-34b + gemma-3-12b only) + Qwen2.5-Coder-1.5B (2.9 GB, barred, unreferenced elsewhere).
Guards re-derived at delete time; 0 refused.

**THREE TRAPS the dry-run caught — keep these in mind for any future cleanup:**
1. `best/` is a SYMLINK into checkpoint-N. Blanket checkpoint deletion destroys every selected adapter.
2. `runs/merges` + `runs/taskvecs` are EXPERIMENT BANKS, not scratch (withdrawn from the plan).
3. `configs/eval/overtrain_individual_*.yaml` PINS 12 raw checkpoints as evaluated systems. Scan
   configs for `checkpoint-\d+` before deleting anything under runs/.

**Pre-existing damage found, NOT caused by this:** qwen25c-1.5b/python/{L0,L1b}_r32_s17_pilotsplit/best
dangle (targets checkpoint-200/198 never existed in those dirs); links dated 2026-08-28 15:50 =
migration day path-rewrite bug. Qwen pilot arms, barred from the paper. 110/112 best symlinks resolve.

Download chain RELEASED: 385666 sc2 -> 385667 granite -> 385668 cgemma -> 385669 datasets (dev).
