# CLAUDE_SCRATCHPAD.md — working state

*Protocol: [`CLAUDE.md`](CLAUDE.md) §0. Update before and after any complex task; this is
working memory, not a log. The durable record lives in [`log/`](log/).*

**Last updated:** 2026-09-04

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
   `ev_ll8` 377850 pending.**
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
   now waits only on `tr_verif` 377861.** `src/obtune/verifier.py`: the generator's own prompt + candidate as the
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
   the cap failure is format-level and will not). If the mono arm also loses, lever 3 closes
   on 7B; a v2 format with explicit event numbering (`12:L7 r=3`) is the only cheap retry.**
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
   0.503 on 4,689 rows, truncation 5/9,378 at 2048); `ck_cs_L0` 377852 next, `tr_cs_mono` 377853 pending.**
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
   **The H1 read of the X1 arms is the
   campaign-end final batch, together with the winner — one `final_eval` spend, agreed with
   the user.**

Rules that hold throughout: no H1 read without the human; every new arm is compared to
`tuned_L0` on the six trainable conditions first; `final_eval` stays unspent until the
campaign's winner is chosen on the trainable grid.
