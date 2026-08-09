# cft-replication — does `nikiema2025contrastive` reproduce on our corpus?

*Last updated: 2026-08-08*
**Status:** active — replication built and queued; SRH Experiment 1 built, Stage 1 queued at priority 61

Replication of Nikiema et al. (2025), *"Using Contrastive Learning to Improve Two-Way Reasoning in
Large Language Models: The Obfuscation Task as a Case Study"* (arXiv:2509.05553). Design, the
condition mapping and the full deviation list live in [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).

**Why this thread exists.** The paper is the nearest prior work to the pilot finding
([`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) §2.1) and §7 names Contrastive
Fine-Tuning as the candidate intervention for RQ1. Before adopting an intervention we should know
whether its result reproduces here. This thread does **not** touch obtune's own RQ1–RQ3 claims: it
is their question (forward vs reverse direction) on our data, not ours (held-out obfuscator family).

## Hypotheses — open

### Experiment 1 (SRH follow-up) — is it the objective, or just the data direction?
- **E1-A (kill-gate):** `r(REV) > 0` — reverse is learnable at all here. If not, every other
  arm's null is uninterpretable and the experiment stops.
- **E1-B:** `r(MIX50) > 0` while `r(FWD) ≈ r(FWD2x) ≈ 0` — bidirectional *exposure* alone
  produces reverse capability, at no extra budget on any axis.
- **E1-C:** `r(FLIP) > r(CFT)` — the contrastive objective is dominated.
- **E1-E:** does bidirectionality cost forward accuracy? MIX50 halves forward supervision at
  matched compute, so the FWD−MIX50 forward gap is the price of it.

### Replication

- **C1 (cognitive specialization reproduces).** An adapter trained only on forward obfuscation
  (`tasks: [gen]`) scores near zero on reverse deobfuscation while scoring well forward.
  CONFIRM if `reverse_success_paper` ≤ 5 % with forward exec-parity clearly above the base model;
  REFUTE if reverse success is materially above zero. Paper's number: **0 %** (§4.3.3, Fig. 4).
- **C2 (CFT recovers the reverse direction).** Adding L_pos + L_neg lifts reverse success without
  costing forward performance. CONFIRM if CFT's reverse success exceeds SFT's with a
  cluster-bootstrap CI (by `program_id`) excluding zero, and forward exec-parity is within noise;
  REFUTE if the two arms are indistinguishable in reverse. Paper: **39–52 %**, Qwen2.5-Coder-7B **39.00 %**.
- **C3 (the gain is renaming-only).** Any CFT reverse gain is concentrated on the identifier
  conditions (`L1b`/`L1r`/`L2`) and absent on the structural ones (`S1`/`S2`). CONFIRM if the
  identifier-condition gain exceeds the structural one; REFUTE if `S1`/`S2` gain equally. The paper
  reports dead code and string encryption still failing after CFT (§5.0.3).
- **C4 (prompting cannot substitute).** Reverse performance is flat across the four prompting
  strategies for every system. CONFIRM if the spread across simple / few-shot / CoT / augmented is
  small relative to the SFT→CFT gap. Paper: ΔR ≈ 0.01–0.05 (§4.3.3).

## Hypotheses — resolved

- ✓ **C5 (the three-term loss is not three-way balanced) SUPPORTED**, 2026-08-08, no GPU.
  Equal instance counts across the pools — the paper's stated balancing — do not give the three
  loss terms comparable weight: a `gen` target is a whole program (**196.7** supervised tokens),
  a `pos`/`neg` target is the single token YES or NO (**3.0**). Measured
  `task_token_share` = gen **0.977** / pos 0.011 / neg 0.011, against a 0.95 threshold. Instance
  upsampling cannot repair it (equal token mass needs ~86×, a ~976 000-instance mixture).
  Deciding entry: [`2026-08-08_implement-cft.md`](2026-08-08_implement-cft.md).
- ✓ **E1-D (budget dominance) SUPPORTED**, 2026-08-08, no GPU. Extending C5's accounting to all
  four axes: CFT costs **2.65×** forward-only SFT's compute (2.52× instances, 2.52× steps) to add
  **1.02×** its supervised signal, while the free flip costs **2.09×** to add **1.43×** — all of
  it on the target direction. The Experiment-1 comparison is therefore framed as *dominance*, not
  as budget-matching. Deciding entry:
  [`2026-08-08_srh-exp1-plumbing.md`](2026-08-08_srh-exp1-plumbing.md); table in
  `../../results/srh/budget_qwen7b_python.json`.

## What worked

- **Vendoring the published CodeBLEU instead of reimplementing it.** `codebleu==0.7.0` into
  `env/vendor/` leaves `env/lock-obtune.txt` untouched and keeps our thresholds comparable to the
  paper's. The one trap: its tree-sitter 0.22 pin must NOT be vendored or it shadows the 0.26
  grammars `obf/base.py` needs — `metrics.py` appends rather than prepends the vendor dir.
- **Setting the readability threshold by measurement.** The short-identifier cutoff separates clean
  code from `L2` at 8 % false positives / 89 % detection over 400 programs; a guessed 0.4 scored
  17 % of ordinary code as minified.
- **Testing arm configs against a registry.** Generating the 7B configs by appending a second
  `train:` block is valid YAML in which the later key silently wins — it cost `mix50_qwen7b` its
  `direction_mix` and `fwd2x_qwen7b` its `epochs: 6`, so both would have trained as plain FWD and
  produced a null that read as a finding. `tests/test_srh_dataset.py` now checks every arm config
  against `srh/arms.py`.

## What didn't

- **The first readability calibration inverted `L2`.** With single letters on an idiomatic
  whitelist, fully-minified code scored `identifier_meaning = 1.00` — the metric rated the most
  destructive identifier condition as perfectly readable. Fixed by deciding "short names are idiom"
  per *program* (from the share of short names) rather than per token.
- **A `verify_rate` that looked like a quality signal but was not.** It is per-*proposal* and
  deflated by design, because verification stops once a program has its mutant quota.
  `program_coverage` is the number to read; both are now reported.
- **Mixed epoch conventions in the first budget table.** `steps` applied epochs and
  `sequence_tokens` did not, so `fwd2x` — whose entire purpose is to match FLIP's compute —
  reported 1.00× compute. All four axes are now totals over training.

## Open ideas

- If C2 confirms, the follow-up obtune actually cares about is whether the same auxiliary losses
  move transfer to a *held-out obfuscator* under output prediction. That is a different experiment
  and it needs a decision about the H1 read budget (`../../CLAUDE.md` §3.2 rule 3: two passes total).
- `negative_style: clean_mutant` runs the paper's literal negative construction. One extra arm
  would turn "their design has a shortcut" from an argument into a measurement.

## Entries

- [`2026-08-08_srh-exp1-plumbing.md`](2026-08-08_srh-exp1-plumbing.md) — SRH Experiment 1 built;
  the four-axis budget table shows CFT is dominated on compute-for-signal before any GPU time.
- [`2026-08-08_implement-cft.md`](2026-08-08_implement-cft.md) — implementation, data layer, and the
  six deviations from the paper; both arms queued behind the RQ1 grid.

## Doc / results links

- [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md) — design + deviation list
- [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) §2.1 — the paper's position
- `../../results/YYYY-MM-DD_cft-bidirectional/` — results (not yet produced)
