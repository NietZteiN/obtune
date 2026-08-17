# cft-replication — does `nikiema2025contrastive` reproduce on our corpus?

*Last updated: 2026-08-17*
**Status:** active — replication RESOLVED at both scales (C1–C4 below); SRH Experiment 1
**complete** (dose ladder, seeds, 4-strategy sweep and the JavaScript replication all landed
2026-08-12); ATTRIB draft at v3 in `paper_bidirectional/`, body fits the 6-page limit

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

### Criterion fidelity (from 2026-08-17)
- **H-R2:** the CodeBLEU threshold of 0.4 in Eq. (1) is the other constant borrowed from the
  original criterion, and should be as redundant with execution as the readability conjunct
  turned out to be. CONFIRM if strict reverse success is flat over a threshold sweep of roughly
  0.3 to 0.5; REFUTE if any reported contrast moves. Zero GPU, same recomputation as
  [`2026-08-17_readability-substitution-sensitivity.md`](2026-08-17_readability-substitution-sensitivity.md).

### Experiment 3 (unlearning)
- **H-U2:** do the 2026-08-10 unlearning conclusions survive dropping the spurious `cft` arm?
  It was never part of the FLIP - lambda*FWD argument, so they should be untouched; CONFIRM if
  `flip`/`rev`/`u_lam*` reproduce within seed noise, REFUTE if any contrast moves.
- **H-U1:** the CodeBLEU timeouts found on 2026-08-11 are an over-negation signature, not a corpus
  property. CONFIRM if `codebleu_timeout` on `u_lam1p25`/`u_lam1p5` exceeds the
  `base`/`rev`/`flip`/`sft` rate by an order of magnitude; REFUTE if it is flat across systems.
  See [`2026-08-11_codebleu-scoring-hang.md`](2026-08-11_codebleu-scoring-hang.md).

## Hypotheses — resolved

- ✓ **C2 (CFT recovers the reverse direction) REFUTED**, 2026-08-09, Qwen2.5-Coder-7B — the
  paper's own model, which it reports at **39.00 %**. CFT never exceeds **3.0 %** under any of the
  four prompting strategies, and pooled over strategies is **−5.7 pts [−6.4, −5.0]** *below* the
  plain SFT it is meant to repair — a CI excluding zero in the wrong direction. Not a broken
  adapter: forward exec-parity is 97.5 % (SFT 97.2 %, base 92.6 %) and `assert_adapters_effective`
  reports 1.7 % identical-to-base. Already refuted at 1.5 B; scale was the last defence and it does
  not hold. Deciding entry:
  [`2026-08-09_7b-refutation-and-scheduler-repair.md`](2026-08-09_7b-refutation-and-scheduler-repair.md).
- ✓ **C6 (the paper's headline is achievable without any fine-tuning) SUPPORTED**, 2026-08-09 — a
  hypothesis we did not pre-register and should have. The **untouched base model** scores
  **38.7 % [35.9, 41.5]** under the `augmented` strategy, statistically indistinguishable from the
  39.00 % the paper attributes to its contrastive method. The paper reports **no untouched
  baseline**, so its headline number is not separable from what the model could already do. This is
  now the strongest criticism in the writeup — it needs no budget accounting, only the missing row.
- ✓ **C1 (cognitive specialization reproduces) SUPPORTED, but prompt-dependent**, 2026-08-09. Under
  the paper's `simple` instruction the forward-only adapter scores **0.3 % [0.1, 0.7]** in reverse
  while beating base forward (97.2 % vs 92.6 %) — the paper's 0 %, reproduced. But the *same
  adapter* scores **12.5 %** under `augmented`. A 40× swing from instruction wording alone means
  the effect is substantially a property of the elicitation, not only of the model.
- ✓ **C4 (prompting cannot substitute) REFUTED**, 2026-08-09. The paper reports ΔR ≈ 0.01–0.05
  across strategies. Here the spread is **0.3 % → 12.5 %** for SFT and **23.6 % → 38.7 %** for
  base — far larger than the −5.7 pt SFT→CFT difference. Prompting matters more than the method
  does, in the opposite direction to the paper's claim.
- ✓ **C3 (any CFT gain is renaming-only) NOT EVALUABLE — vacuous**, 2026-08-09. There is no CFT
  gain to decompose. The by-condition table is still informative in its own right: the reverse
  signal that *does* exist concentrates on `S1` (base 71.8 %) and is near-absent on `L1b`
  (base 10.5 %) — the structural transformation is mechanically invertible, adversarial renaming
  destroys information no method can recover. So a single pooled reverse number is dominated by
  transformation mix, and the paper's is too.

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

- [`2026-08-17_readability-substitution-sensitivity.md`](2026-08-17_readability-substitution-sensitivity.md)
  — the reverse criterion's readability conjunct uses our proxy rather than the model the
  original study uses. **H-R1 refuted:** strict reverse success is insensitive to the choice.
  Dropping the conjunct moves no arm by more than 0.6 pp and the headline contrast by 0.2 pp,
  and it decides only 0.2 % of trials for `flip`/`mix50`, because execution plus the CodeBLEU
  bound already imply it. Open follow-up **H-R2**, sweep the borrowed 0.4 CodeBLEU threshold
  the same way.
- [`2026-08-17_attrib-v2-and-determinism.md`](2026-08-17_attrib-v2-and-determinism.md) — the
  four 08-12 evals folded into draft v2 (Fig. 1 generated from the run, App. B/D/E rebuilt).
  **H-D1 refuted:** the differing `base` rates across passes are not program-set drift — the
  sets are byte-identical — but batch nondeterminism in greedy decoding, worth ±0.3 pp
  cross-pass; the seeds config's gate was testing the wrong thing and is rewritten. Computing
  the dose CIs also caught an overclaim before it reached the paper: `mix50` − `mix5` is
  +4.5 pp [+3.2, +5.8], so the ladder saturates rather than stepping.
- [`2026-08-11_codebleu-scoring-hang.md`](2026-08-11_codebleu-scoring-hang.md) — the four
  `srh/exp3-unlearning` cells died twice without producing a verdict; `codebleu`'s `DFG_python`
  does not terminate on deeply-nested predictions. Bounded at 20 s and surfaced as
  `codebleu_timeout`; cells requeued. Two addenda: obtune cut to GPUs 0–1 (2–3 lent out), and
  `_extends` was found to MERGE `systems:`, so every unlearning run evaluated an undeclared `cft`
  arm — the root cause of the 7B "cft pointed at a 1.5B adapter" bug in the master report, and
  wider than that entry states.
- [`2026-08-09_7b-refutation-and-scheduler-repair.md`](2026-08-09_7b-refutation-and-scheduler-repair.md)
  — CFT refuted at the paper's own 7B model; the untouched base matches its headline number; four
  scheduler defects fixed, three of which were our own infrastructure killing our own jobs.
- [`2026-08-08_srh-exp1-plumbing.md`](2026-08-08_srh-exp1-plumbing.md) — SRH Experiment 1 built;
  the four-axis budget table shows CFT is dominated on compute-for-signal before any GPU time.
- [`2026-08-08_implement-cft.md`](2026-08-08_implement-cft.md) — implementation, data layer, and the
  six deviations from the paper; both arms queued behind the RQ1 grid.

## Doc / results links

- [`../../docs/REPORT_bidirectional_2026-08-09.md`](../../docs/REPORT_bidirectional_2026-08-09.md)
  — standalone report, written for a reader new to the terms; §6.1 carries the 7B result
- [`../../results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b/report.md`](../../results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b/report.md)
  — generated 7B tables with CIs
- [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md) — design + deviation list
- [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) §2.1 — the paper's position
- `../../results/YYYY-MM-DD_cft-bidirectional/` — results (not yet produced)
