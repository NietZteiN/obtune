# 2026-09-13 — Correction: where `an_f1` was resubmitted

**Thread:** modularity · **Corrects:** [`2026-09-13_mixture-guard-refused-the-mixture-engine.md`](2026-09-13_mixture-guard-refused-the-mixture-engine.md) §Resubmission

That entry says the chained `an_f1` "went to `normal` instead" after `dev` refused it. Wrong: `normal`
refused it with the same message. The cause was not the partition. `scripts/slurm/submit.py` applies
its default `--gres gpu:1` to every ad-hoc submission, CPU partitions included, and neither `dev` nor
`normal` has a node with a GPU — hence "Requested node configuration is not available". The 09-12
submission had gone through a manifest, which carries no gres for an analysis job.

Submitted with `--gres ""` on `dev`: **392641**, `afterok:392638`. The chain is
`ev_f1_mole` 392638 (h100) → `an_f1` 392641 (dev).
