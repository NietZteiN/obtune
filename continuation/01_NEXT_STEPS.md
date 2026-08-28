# 01 — Next steps, in execution order

Agreed with the PI (Jack Le) on 2026-08-27. The destination is a **7B replication for the paper**;
everything below is what must happen first so that only arms worth 7B GPU time get promoted.

Ordering rationale: **the instrument comes before the experiment.** `H1` is one obfuscator, is
partly burned (`00_STATE.md` weakness 3), and its control moves up to 6 points across
re-evaluations. Spending more of it to evaluate a brand-new training objective is the wrong order.

---

## Phase 0 — Close the geometry/merging question cheaply (~1 GPU-hour)

**The existing data already answers most of it, negatively.** Record this rather than re-deriving:

- **Routing cannot be improved by geometry.** The router is at **1.000** dispatch accuracy with
  entropy ~3e-6 and buys a gain on one of six conditions. On `H1` it is *undefined*, not
  unmeasured — `results/router/qwen25c-1.5b/python/routing_report.json` records `n_heldout: 0`, and
  a router over per-transform experts has no correct answer for a transform with no expert.
- **Merging via geometry helps trained conditions, not the held-out one.** The task-vector norm
  `‖ΔW‖` predicts merged accuracy at **Spearman ρ = +0.86** (p = 9.5e-6, n = 17 merges) where sign
  conflict predicts nothing — but the best-normed merge, `sweep_dare_ties_d0p3` (‖ΔW‖ = 0.567,
  **1.56×** a single expert), reads **32.2** on Grid B `H1` against `merge_dare_ties`' 34.8.

**The one untested version, worth closing.** Nothing has built a merge *explicitly norm-matched* to
1.0× a single expert. Rescale `merge_dare_ties` (0.62×) and `sweep_dare_ties_d0p3` (1.56×) to 1.0×
— reuse `src/obtune/merge_adapters.py` and the rescale path already proven by `dl_rescaled` — and
run one Grid A `H1` eval.

**Predict null.** If null, item closed by measurement rather than inference. No training.

---

## Phase 1 — Build `H2` and `H3` (CPU only, ~1–2 days engineering each)

One held-out family cannot separate *"`S2` taught a general inert-material skill"* from *"`S2` and
`H1` share a quirk."* Two families with **opposite predictions** can:

| family | mechanism | prediction if the RQ3/normalization account is right |
|---|---|---|
| **`H2`** | inert material, **different surface form** from `S2` and `H1` — e.g. redundant computation whose result is discarded, unreachable branches from a different generator | `tuned_S2` **reaches it** |
| **`H3`** | semantics-preserving **rearrangement**, no inert material added — dependence-respecting statement reordering, loop restructuring, virtualization | `tuned_S2` **does not reach it** |

That 2×2 converts the inferential step into a measurement. A double hit or a double miss is equally
informative. Cheap first version: stack existing generators (`H1∘S1`).

**Build on the existing pattern, do not invent one.** Template:
`scripts/gen_h1_quarantined.py` + `src/obtune/obf/h1/{py_h1.py, js_h1.mjs}`. The four-layer
quarantine in `CLAUDE.md §3.2` must be **extended, not bypassed**:

1. `src/obtune/paths.py::load_training_jsonl` — reject `H2`/`H3`-labelled rows.
2. `tests/test_quarantine_lint.py` — add the new generator modules to the import ban.
3. New generators refuse to run without their own `--i-am-the-*-generator` flag; outputs `0o444`.
4. `scripts/check_manifest.py` — **new marker patterns in `configs/conditions.yaml`** per family, so
   the content scan catches leakage even when labels are correct.

Semantic soundness reuses `src/obtune/obf/validate.py`: every variant executed against its parent's
inputs plus fuzzed ones. Publish coverage to `data/manifests/coverage_matrix.json`. Each family gets
its own `ACCESS_LOG.md`.

**Decide `H1`'s status only once `H2` exists.** The honest option is to promote `H1` to OOD-dev,
tune against it freely, and freeze the new families as the final test. Irreversible; costs nothing
to defer.

---

## Phase 2 — The alignment arm (the real experiment)

**The idea (PI's):** instead of steering activations at inference, fine-tune so the model's hidden
states on obfuscated code match a **frozen** copy's hidden states on the *original* code.
Weight-space internalization of the steering correction.

```
L = L_task(x̃)  +  λ · L_align
```

*"Do the task on the obfuscated code, and while you're at it, think about it the way you think about
the clean code."* `L_task` is the ordinary answer loss — identical to the vanilla SFT baseline, and
what prevents the student satisfying alignment by degenerating.

**This is a better-posed version of something already on the books.** `§9` lists "the invariance-loss
arm — the only attempted repair that optimizes invariance as an *objective* rather than through the
data. Designed, never built." The report's Stage 3 sketch used a *symmetric consistency* loss
between two obfuscated views, which can collapse to a shared degenerate representation. Anchoring to
a frozen teacher on the clean original is asymmetric and cannot drift.

### `L_align` — answer-position form (decided)

The `n ≠ m` problem: teacher states on clean `x` are `[n × d]`, student states on obfuscated `x̃`
are `[m × d]`, and `n ≠ m` because obfuscated code tokenizes differently. **Solution chosen:
compare only at the answer position.** `src/obtune/prompts.py` is frozen and its template sha is
pinned in every run manifest, so the prompt *suffix* tokenizes identically across conditions — the
mismatch never arises.

```python
h_s = student(x_obf).hidden[L][:, -k:, :]    # [B, k, d]
h_t = teacher(x_clean).hidden[L][:, -k:, :]  # [B, k, d], no grad
L_align = mse(h_s, h_t.detach())
```

`k ∈ {1, 4}`; layer set `L ⊆ {4, 9, 14, 19, 23, 27}` — the layers RQ3 already sweeps, chosen because
the condition is linearly decodable at **99.4 %** by layer 4, so that is where "read past the
surface" has to happen.

*Alternatives considered and deferred:* anchor-token correspondence (dense, reuses
`src/obtune/attention/metrics.py::resolve_spans_to_tokens`, but cannot cover `S1` — flattening
destroys correspondence); mean-pooling (discards the token structure RQ3 showed carries the
mechanism — keep as an ablation); soft-DTW / optimal transport (general but makes a null ambiguous
between a bad objective and a bad alignment).

### Design decisions that are not obvious

- **Teacher = frozen `tuned_L0`, not `base`.** `base` scores 21.7 on `L0`; aligning to it teaches
  the student to be as weak as an untuned model. `tuned_L0` scores **44.7** and is the project's
  control anyway, so the arm's ceiling is "think about obfuscated code the way the clean-code
  adapter thinks about clean code" — on `H1` that is **24.5 → 44.7** of headroom.
- **Pairing is free.** Every condition is single-transform from an `L0` parent by construction
  (`CLAUDE.md §3.1`), so `(clean, obfuscated)` pairs are a `program_id` join on the existing corpus.
- **Cost ≈ 2× vanilla SFT** — one extra no-grad teacher forward per step. LoRA SFT at 1.5B is
  2–3 h/adapter, so budget 4–6 h per arm.
- **`src/obtune/schema.py:146` needs a new `invariance` literal** in `TrialRow.adapter_arch` or the
  run dies at the first row written. Already flagged in `§9`.

### The control that decides whether a positive result means anything

**Align to a *different program's* clean hidden states.** If the mismatched teacher works as well as
the matched one, `L_align` is a **regularizer, not semantic alignment**, and the interpretation
collapses. This project has been burned three times by exactly this shape:

- `mole_random` was behaviourally a second uniform gate (entropy 1.000), so the mixture ladder had
  three rungs and two controls;
- the `l0merge` control showed merging six specialists ≈ merging three clean-code adapters;
- the oracle-of-k "headroom" was an artifact until a permutation null was built.

**Budget the mismatched-teacher arm as first-class, not a nice-to-have.**

Secondary ablations: `λ = 0` (must reproduce the vanilla specialist — a plumbing check); mean-pooled
`L_align`; teacher = `base` (does teacher quality drive it?).

### Selection discipline

**Sweep `λ` and the layer set on the LOTO folds, never on `H1`.** `§12.10` built leave-one-transform-out
precisely because "any sweep selected on `H1` destroys it" and there was no legitimate OOD dev
signal. This is the first arm that actually needs it. One batched confirmatory read on
`H1`/`H2`/`H3` at the end.

### Pre-registered outcomes — write these into the config before running

- **Confirm:** beats `tuned_L0` on `H1` **and** `H2`, outside the Python seed band (**0.63 mean /
  1.46 p95** — the Python row, not the pooled 1.32/3.61).
- **Refute:** flat against `tuned_L0`, **or** matched by the mismatched-program control.
- **Most likely partial result, still worth having:** gains on trained conditions and nothing OOD.
  That reproduces the project's central pattern from a *new objective*, which makes the negative
  result substantially stronger than five arms that all shared the task-accuracy objective.

---

## Then — 7B

Only arms that survived Phase 0–2 on `H1` **and** at least one new family get promoted. §12.3 is why
this is worth doing: `H1` is the only condition whose penalty does *not* shrink with scale
(−20.9 at 7B vs −17.7 at 1.5B), so the instrument gets **sharper** at 7B, not blunter. Budget
~8–11 GPU-h per 7B adapter, one GPU each, no model parallelism.

---

## Carry-over: unfinished work from 2026-08-27

The `‖ΔW‖` column landed in the master table (136/169 rows) and §14.4b documents ρ = +0.86, but
propagation is incomplete and one item is a **correction owed**:

- **Verify ρ within each algorithm separately** before it enters a manuscript. The obvious objection
  is that it restates "DARE-TIES beats TIES." Within-algorithm signal exists — the `dare_ties`
  density sweep is monotone in both norm and accuracy (0.567/0.226/0.115 → 47.03/44.71/40.53) while
  `ties` is flat in both (0.066/0.069/0.064 → 35.54/35.89/36.29) — but report ρ per algorithm and a
  partial correlation controlling for an algorithm indicator.
- **`§12.13` says Branches B, C and D are dead. Branch C now fires** — `paper_modularity/CLAIM_LADDER.md`
  Branch C's gate names `‖ΔW‖` explicitly and both prerequisites (density sweep, second seed) have
  landed. It fires in *full*, since its headline is "predicts but does not prescribe" and the
  merge-optimal search (0.7 points, every round below status quo) supplies the second half.
  **Conditional on the check above.**
- `paper_modularity/NUMBERS.md:78` still records `merge_ties` ‖ΔW‖ = 0.19× as **"unexplained"**, and
  `log/modularity/README.md` still carries it under **What didn't**. Both are now answered: the sign
  election retains 86 % of magnitude *per surviving coordinate*, but averaging six vectors only
  0.56-aligned cancels most of the vector sum. Retention and magnitude are different quantities.
- `§14.4b` is missing from the master report's table of contents; the changelog needs the `‖ΔW‖`
  column and the Branch C reversal.
