# 2026-08-13 — Zero-training baselines: symbolic normalization and 7B zero-shot

**Thread:** modularity · **Commit:** (uncommitted; see Setup) · **GPUs:** 0, 1, 2 (gpu3 lent out)

## Goal / hypothesis

Two questions a reviewer asks before reading any adapter number, both answerable with **no
training at all**:

1. **"What does a static normalizer already recover?"** Every adapter, merge and mixture arm
   in this project buys its gain with GPU hours. If a compiler-style source-to-source
   rewriter recovers most of that gain for free, the fine-tuning framing is in trouble —
   and that is much better to learn now than in review.
2. **"Is this just a small-model artifact?"** Every headline number here is 1.5B. The claim
   under test ("obfuscation costs comprehension") is about the *base model*, so testing it
   at 7B needs no adapters.

These are the last two of the four cheap baselines. `oracle_bestof8` and the ICL arm are
already done ([`2026-08-13_mole-random-inert-control.md`](2026-08-13_mole-random-inert-control.md)
is the neighbouring entry; the ICL arm landed as pipeline stage 1 earlier today).

## Setup

New code:

| path | what |
|---|---|
| `src/obtune/normalize/py_norm.py` | four passes — `alpha`, `fold`, `dce`, `reformat` — and the three evaluated profiles |
| `src/obtune/normalize/__init__.py` | package surface |
| `scripts/analysis/21_validate_normalized.py` | the **soundness gate** (see below) |
| `configs/eval/normalize_baseline_qwen1.5b.yaml` | 4 systems × 9 conditions = 36 cells |
| `configs/eval/zeroshot_7b.yaml` | 2 systems × 9 conditions = 18 cells |
| `tests/test_normalize.py`, `tests/test_normalize_shrinks.py` | 105 tests |

Edits: `obf/py/rename.py` gained a keyword-only `preserve=` (empty for every *condition*, so
L1r/L2/L1b output is byte-identical — asserted by a test); `eval_vllm.SystemSpec` gained
`normalize:` and `render_prompts` applies it.

Profiles, in the order the passes run:

| profile | passes | attacks |
|---|---|---|
| `alpha` | canonical sequential renaming, entry point preserved, formatting preserved | L1b, L1r, L2 |
| `reformat` | `ast.unparse` only | **control** — `fold`/`dce` must unparse to take effect |
| `full` | `fold` → `dce` → `reformat` → `alpha` | everything |

Commands:

```
PYTHONPATH=src python scripts/analysis/21_validate_normalized.py --language python
setsid nohup bash scripts/pipeline.sh > runs/logs/pipeline.log 2>&1 < /dev/null &
```

Seed 17 throughout (`_base_eval.yaml`); normalization itself is seeded `Random(0)` and
asserted deterministic across five repeats.

## Results

**Soundness gate — the load-bearing number.** The arm shows the model a *rewritten* program
and grades against the *original's* stored output, so it is valid only if the rewrite
preserves behaviour. Every normalized program was executed against its item's `args_repr`
and compared with `CaseResult.matches` (exceptions by TYPE, the same rule the obfuscation
gate uses):

| profile | items | rewritten | sound | **unsound** | excluded |
|---|---|---|---|---|---|
| `alpha` | 1377 | 1377 | 1377 | **0** | 0 |
| `full` | 1377 | 1377 | 1377 | **0** | 0 |
| `reformat` | 1377 | 1377 | 1377 | **0** | 0 |

Test suite **652 passed / 0 failed**; `make check` clean; `preflight` 0 errors, 3
pre-existing warnings.

Accuracy cells were still generating when this entry was written — see the next entry for
numbers. What is already visible from the rewrites themselves:

* **S3 collapses back to L0.** The dead-helper condition's two injected helpers are removed
  outright: 545 → 199 chars, recovering the clean program's exact structure. If `norm_full`
  does not score near L0 on S3, something else is going on.
* **L1r loses its hex names.** `f_72ed(v_1f1e)` → `f_72ed(a)`, entry point intact, 259 → 199
  chars.

**First matched cells (H1, n=115 for every arm — see the phase defect below).**

| arm | acc % | vs `base` |
|---|---|---|
| `base` | 11.3 | — |
| `icl_k1_clean` (L0 demos) | **23.5** | **+12.2** |
| `icl_k1_cross` (trainable-condition demos) | 21.7 | +10.4 |
| `oracle_prompt_1shot` | 20.9 | +9.6 |

A single in-context example **more than doubles** base accuracy on the held-out obfuscator,
and `clean` ≥ `cross`: the gain comes from showing the model *the task*, not from showing it
*a transformation*. That is a strong baseline and it needs a direct comparison against the
adapter and merge arms on this same grid before any modularity claim is written up.

**Symbolic normalization, first matched cells (1.5B, Grid B).** Every arm on identical items:

| cond | n | `base` | `norm_alpha` | `norm_full` | `norm_reformat` |
|---|---|---|---|---|---|
| L0 | 176 | **29.0** | 22.2 (−6.8) | 22.7 (−6.3) | 28.4 (−0.6) |
| L1b | 176 | 23.3 | 23.3 (0.0) | **24.4** (+1.1) | 22.7 (−0.6) |
| L1r | 176 | 23.3 | **25.0** (+1.7) | 24.4 (+1.1) | 21.6 (−1.7) |
| L2 | 176 | 21.0 | 21.0 (0.0) | 21.0 (0.0) | 21.0 (0.0) |
| S1 | 145 | 26.2 | 19.3 (−6.9) | 18.6 (−7.6) | **26.9** (+0.7) |

**The baseline does not threaten the fine-tuning story — it is close to inert, and where it
moves it mostly hurts.** Best case is +1.7 pts (`norm_alpha` on L1r); L2 is *exactly*
unchanged in all three profiles, which is the sanity check working (L2 *is* the `seq`
canonicalizer, so alpha-normalizing it is a near-identity); and the predicted cost lands hard
at −6.8 on L0 and −6.9 on S1, where canonicalization destroys meaningful identifiers and
buys nothing.

The most interesting cell is **L1b at +0.0 for `norm_alpha`**: removing deliberately
misleading names does *not* recover the damage they caused. Whatever L1b costs the model, it
is not a penalty that survives only while the bad names are present — which is a sharper
claim than "renaming hurts" and worth a paragraph in the write-up.

Two caveats before this is quoted: S2/S3/S4/H1 were still generating, and **S3 is the cell
that matters most** — it is where `dce` removes the injected helpers outright (545 → 199
chars) and is the one condition where a large normalization gain is actually predicted.

## Observations

**A phase-namespace defect that silently invalidated the comparison — including the ICL run
that had already completed.**

Both baseline configs originally declared `phase: main`. `main` holds two grids CLAUDE.md
says are never pooled: `base__L0` is n=1670 (Grid A, the 557-program corpus) and `base__S3`
is n=176 (Grid B, the testset). These arms run on Grid B, and `output.resume: true` did
exactly what it should — it found an existing `base__L0` cell and skipped regenerating it.

The result was a table with `norm_full__L0` at n=176 sitting beside `base__L0` at n=1670.
Every delta for L0/L1b/L1r/L2/S1/S2/H1 was computed **across different programs** while
looking like a result. Scale of the distortion: `base__H1` reads 6.4 % on the Grid A cell and
**11.3 %** on the matched Grid B cell, so the ICL effect was being overstated by roughly 5
points. S3/S4 happened to be unaffected — `grid_s3s4` had already written Grid B base cells.

It would also have collapsed `trial_table.compute_is_core`, which intersects programs across
a whole (phase, model, language) group — the hazard already flagged in `trial_table.py:78`.
No committed analysis artifact had been regenerated since the ICL cells landed (the
`analysis` stage marker predates them), so nothing downstream was contaminated.

Fixed by giving all three baseline configs `phase: baselines`, which regenerates *every*
arm — including `base` — on exactly the items it is scored on. The 45 already-written cells
were **moved, not deleted**, to `results/cells/_misplaced_2026-08-13/` with a README; they
are valid Grid B generations, superseded only because they have no matched floor.

**That fix then exposed a closed-enum ripple, and cost two GPU jobs to learn.** `TrialRow.phase`
is a pydantic `Literal["pilot", "main", "final"]`, so naming a new phase in a config is a
*schema* change, not a config change. Both jobs loaded their model, generated a full cell,
and only then raised `ValidationError` on the first row — and neither process exited
afterwards, wedging in vLLM shutdown while still holding ~43 GB each until killed by hand.
`schema.py` now lists `baselines`, and `tests/test_baseline_configs.py` asserts every
baseline config's declared phase is one `TrialRow` accepts, so the next such mistake is a
CPU test failure instead of two dead GPU jobs.

**Two normalizer defects found, one of which no execution test could ever have caught.**

1. `_pass_dce` filled every empty `orelse` with `pass`, turning "no else clause" into
   `else: pass` on every `if` and `for`. Behaviour identical — the soundness gate passed
   with zero unsound programs — but the model was being shown **more** scaffolding than the
   un-normalized program had, which would have biased `norm_full` downwards and read as
   "normalization does not help". For this baseline semantic equivalence is necessary and
   nowhere near sufficient; `tests/test_normalize_shrinks.py` now asserts size and shape
   separately.
2. `_icl_demo` seeded demo selection with `abs(hash((pid, name)))`. Python randomizes string
   hashing per interpreter and `seedutil` setting `PYTHONHASHSEED` in-process is too late to
   change it, so **every ICL cell would have picked different demos on re-run**. Replaced
   with a SHA-256 digest. This is my own bug from earlier today, and it is exactly the
   silent-unreproducibility failure CLAUDE.md's seed rule exists to prevent.

**`prompts.py` being frozen forced a real trade-off.** It carries no oracle description for
S3/S4, so an `oracle_prompt` arm and the S3/S4 conditions are mutually exclusive. S3 is the
one condition where `dce` is predicted to pay, so the conditions won and both configs ship
without an oracle arm. The oracle reference already exists on `[H1, L1b, L1r, L2, S1, S2]`
in `eval/icl_cross_h1_qwen1.5b.yaml`, on the same items.

**L0 is in the condition list on purpose.** L0 is clean code with meaningful identifiers and
`alpha` renames them to `a`, `b`, `c`. Normalization is *expected to hurt* there. Without
that cell the arm would look strictly free, and it is not — the L0 delta is the method's
price and belongs in the table next to its gains.

**The passes were deliberately not tuned against H1.** Inspecting the held-out obfuscator's
implementation to decide which rewrites to implement would be using H1 for hyperparameter
selection, which §3.2 rule 2 forbids as squarely as training on it. `fold` folds constant
expressions because that is what normalizers do, not because anyone checked what H1 emits.
Whatever it recovers on H1 is therefore an honest OOD measurement. For the same reason the
soundness gate covers the trainable ladder only and never reads H1: it is re-run on every
pass change, and iterating until H1 looked good is precisely the drip-feed the budget exists
to stop.

**Access-log correction — read this before auditing the H1 budget.**
`data/quarantine/h1/ACCESS_LOG.md` gained **9 rows dated 2026-08-13**. They are not 9
evaluations. They break down as:

* several `--stub --limit 4` config validations, which generate FAKE text and score
  nothing — they exist only to prove a config parses and expands;
* the first ICL and normalization runs, which wrote into `phase: main` and were superseded
  by the re-runs under `phase: baselines` (see the phase defect below);
* the two 7B/normalization jobs that died on the `phase` `ValidationError` before scoring
  a single row.

The log is written *before* the resume check and before any generation succeeds, so it
counts intent, not evaluation. Rows are never edited, hence this note. The substantive H1
evaluations from today are the `baselines`-phase cells: one ICL pass, one normalization
pass, one 7B pass, one k-sweep pass.

## Next steps

* Read the 54 cells out and put `base` / `norm_alpha` / `norm_reformat` / `norm_full` and
  `base@7B` into the master report as accuracy tables per condition, with the L0 cost row
  shown, not buried.
* The comparison that decides the framing: `norm_full` vs `tuned_<cond>` per condition. If
  normalization closes most of the adapter gap on the *structural* conditions, the
  contribution narrows to the renaming family and should be re-scoped explicitly.
* `norm_full@7B` vs `norm_full@1.5B` — do normalization and scale compose, or overlap?
* The remaining two untested routing questions are unaffected by this and still open:
  route H1 and report entropy; route the composites.

---

## Addendum — remaining work built and queued (2026-08-13, late)

All five outstanding items built on the user's instruction, after they were presented as
blocking decisions rather than assumed:

| item | what shipped |
|---|---|
| **Grid A baselines** | `configs/eval/baselines_gridA_{qwen1.5b,7b}.yaml` — `eval_source: heldout`. THE blocker: every baseline is Grid B, every RQ1/RQ2 headline is Grid A, and `base` on H1 differs 6.4 vs 11.3 between them. Spends an H1 `final_eval` access, **explicitly authorised**. |
| **`mole_hardrouter`** | `mole.gate.HardenedGate` — the trained RouterGate argmaxed to one-hot. Same weights as `mole_router`; only the softmax changes, so the pair isolates BLENDING from per-token selection. Decides whether "mixture" is an honest word. The pre-existing `mole_hardrouter:<i>` is a different control (pins one expert) and cannot answer this. |
| **Route H1** | `configs/eval/mole_h1_routing_qwen1.5b.yaml`, kept separate so `mole_ladder`'s documented "NO H1" rationale is not silently invalidated. Reports gate entropy against `log 8`, not just accuracy: a gate that goes uniform on H1 and one that stays confidently wrong are different failures the accuracy column cannot separate. |
| **`structural` profile** | `full` minus `alpha`. The first run showed `alpha` costs 6.8 pts on L0 by renaming meaningful identifiers, swamping dce's +4.5 on S3. |
| **`oracle_bestof8`** | Now refuses to pool grids and reports WHY each condition is excluded. This immediately diagnosed the long-standing S3/S4-only puzzle: **only `tuned_L0` is on Grid A (n=1670); the other seven experts are Grid B (n=176)**, so the old silent `dropna()` was hiding a grid mismatch, not missing data. |

**A duplicate-claim race, found by watching rather than by a test.** Restarting the pipeline
while a job was mid-flight left the original `eval_vllm` alive (killing `pipeline.sh` does not
kill a worker's subprocess), and a fresh worker then claimed the SAME job on another GPU —
two processes writing the same cell directories under `resume: true`. Caught before any
parquet was corrupted; the newer duplicate was killed and the 23-minute original kept. Worth
a proper guard in `sched/worker.py` (a claim should not be grantable while an identical
job_id sits in any `running/` tag), which is NOT yet written.
