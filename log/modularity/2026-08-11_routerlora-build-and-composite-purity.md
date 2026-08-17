# 2026-08-11 — RouterLoRA built end to end; composite purity was vacuous

*Thread: modularity (RQ2). Companion to [`../cft-replication/2026-08-11_attrib-chain-and-zero-gpu-repairs.md`](../cft-replication/2026-08-11_attrib-chain-and-zero-gpu-repairs.md), which covers the same day's ATTRIB work.*

## Goal / hypothesis

Build every remaining piece of Part III (RouterLoRA: attention over LoRA experts) and Part V
Stage 2 (merge-optimal checkpoint selection), and wire both into `scripts/pipeline.sh` so the
whole remaining programme runs unattended. No new results today — this is a build entry, and
the numbers below are coverage and parameter counts, not findings.

The premise for Part III is unchanged and is worth restating because it is what makes a
*negative* result publishable here: the learned router is saturated
(`router_val_accuracy 0.9969`, entropy ~1e-6 nats against a max of 2.079), so *which adapter to
pick* is solved on seen conditions. The remaining headroom is only where **no single expert is
correct** — which is what the stacked conditions manufacture.

## Setup

Commit: see `git log` for this entry's date. No GPU consumed by this work; all four GPUs stayed
on the Part IV unlearning controls (`057_evalunlearn_*`, 7B and 1.5B) throughout.

Built or repaired:

| file | what |
|---|---|
| `src/obtune/mole/{experts,mixture,gate,model,eval_mole,train_mole}.py` | the mixture, the gate, the trainer, the HF engine |
| `configs/mole/routerlora_v1.yaml`, `configs/eval/mole_ladder_qwen1.5b.yaml` | the arm and its ladder |
| `scripts/merge/22_merge_optimal.py` | Part V Stage 2, the greedy merge-optimal search |
| `src/obtune/obf/validate.py` | `_purity_composite` + composite spec resolution |
| `scripts/05_build_variants.py` | `--conditions-config`, and output-path namespacing |
| `scripts/pipeline.sh` | `t2_epoch_sweep_full`, a real `t2_merge_optimal`, and three `p3_*` stages |

Verification: 432 tests pass (was 429); `scripts/preflight.py` 0 errors / 7 known unrelated
warnings; `make check` clean (manifest OK, 40 train files, 122 119 rows, no H1 labels or
markers, splits disjoint).

## Results

**The gate trains and the mixture evaluates.** `--dry-run` on the real mixture:
7384 instances, truncation **0.000 %** at `max_seq_len 2048`, **2 766 876** trainable gate
parameters against a **295 436 288**-parameter frozen expert bank (ratio 0.0094), loss mask
264/482 prompt tokens at −100, base and bank asserted frozen.

**Composite corpus is viable.** Generated at full scale on CPU:

| language | programs | `C_L1r_S1` accepted | rate |
|---|---|---|---|
| python | 2231 | 1658 | 74.3 % |
| javascript | 674 | 665 | 98.7 % |

Above the plan's Gate-0 threshold (re-pick pairs below ~50 %), so the pair set stands.

**Stub eval produces schema-valid cells.** `--stub --limit 4` wrote three cells that
`TrialRow.model_validate` accepts, carrying `adapter_arch ∈ {none, mole_uniform, mole_random}`
and a populated `is_core` — i.e. `trial_table.py` collates them with no special-casing, which
was the whole point of implementing `HFEngine` against `eval_vllm.run_cell`'s contract rather
than writing a second pipeline.

## Observations

Six defects, all silent, all found by writing the thing that would have consumed them. The
pattern from the last several days holds exactly: **every one is an identifier or code path
that does not encode what actually varies.**

1. **Composite purity was vacuous, and the H1 content scan was skipped for composites.**
   `validate.gate` resolved its spec from `cfg["conditions"]`, where `C_` codes do not appear.
   So `family` was unknown, every `purity_*` check was skipped, and — because the resulting
   `{}` made `spec["trainable"]` falsy — the **H1 marker scan never ran** on the one arm about
   to be added to the training tree. The purity half was pinned by a deliberate test written
   yesterday (`test_purity_is_currently_vacuous_for_composites`), which failed as designed and
   is now inverted into a positive assertion. The H1 half was not pinned and was not known.

2. **Composed invariants cannot just be both constituents' invariants.** `C_S4_S3` proves it:
   S3's set requires that no opaque guard was added, S4's requires that one was. Each
   condition's *exclusion* clauses exist to separate it from its siblings **when applied
   alone**, and under composition they contradict each other. `_purity_composite` therefore
   applies only the positive mechanism invariants, and records which ones it relaxed in a
   `purity_composite_relaxed` gate key rather than leaving that in a comment. The negative
   control — label a plain `L1r` output as `C_L1r_S1` — is now rejected on
   `purity_composite_S1_dispatch_loop`, where before it would have entered the corpus carrying
   Part III's entire claim.

3. **`05_build_variants.py` would have overwritten the RQ1 coverage matrix.**
   `coverage_matrix_<target>.json` and `data/rejects/<lang>/<target>.jsonl` are fixed paths, so
   a composite run would have replaced the ladder's coverage summary with a six-condition
   composite one. Both are now suffixed by the ladder file.

4. **`HFEngine` was missing `ecfg`.** `run_cell` reads `engine.ecfg` for the `drop_overlong`
   bounds; the contract is five members, not the four I implemented. The first real cell would
   have died on `AttributeError` — loudly, at least, unlike the rest of these.

5. **`base` through the mixture engine was not base.** `clear_routing()` clears the contexts,
   but the per-layer pre-hooks refill them on the very next forward, so a `base` row would have
   been evaluated as whatever gate happened to be installed — and *every* delta in the ladder is
   measured against that row. Added `MoLEModel.bypass`, verified bit-exact against the
   pre-attach logits and verified reversible, and pinned it with a test that first asserts the
   mixture is not inert (otherwise the equality proves nothing).

6. **`t2_merge_optimal` ran the epoch sweep, not merge-optimal selection.** Flagged yesterday,
   fixed now: the stage is renamed `t2_epoch_sweep_full` for what it actually runs, and a real
   `t2_merge_optimal` runs `22_merge_optimal.py` for three greedy rounds with `--collect`
   *between* rounds, since each round's winner becomes the next round's incumbent.

Two design notes worth keeping:

- **The mixture is in activation space, not weight space** — `h = Wx + Σ a_e(x)·(α/r)·B_e A_e x`.
  This is exact, needs no per-item merge rebuild, and does not grow rank. It relies on linearity
  that holds only for vanilla LoRA; every adapter on disk is `r=32, α=64, use_dora=false,
  use_rslora=false`, and `ExpertBank` refuses ragged or mixed-rank banks rather than trusting it.
- **`mole_uniform` is the primary fixed-mixture contrast, not `merge_dare_ties`.**
  `merge_dare_ties` differs from the RouterLoRA in three ways at once (fixed vs learned,
  weight vs activation space, pruned+elected vs exact); `mole_uniform` differs in exactly one.

## Next steps

- Let the queue drain the Part IV controls, then the ATTRIB chain, then Tier 2, then `p3_*`.
- Part III's first real number is **Gate 1**, which needs no new training:
  `oracle_bestof8 − merge_dare_ties` on the composites. ≤2 pts means stop and report the
  negative RQ2 finding.
- `mole_random` must be run and reported whatever happens. If `mole_router ≈ mole_random`, the
  gain is rank-256 residency rather than routing, and the headline has to say so.
- Still open: `stats/R/config.R` needs the composite levels before any `C_` trial reaches the R
  stack, and the 12 orphaned duplicate merge cells (`ties_e6/e9`, `dare_ties_e6/e9`) still
  await a human decision per CLAUDE.md §2.
