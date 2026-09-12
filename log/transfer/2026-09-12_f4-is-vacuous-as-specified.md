### Target Date: 2026-09-12 (F4 — "the one new training arm the paper cannot go out without" — is VACUOUS as specified: `cons_lam0` *is* `mono_all`, and the premise behind it is false)
- **What F4 was for.** `docs/PAPER_EXPERIMENTS.md` §7 records the gap as *"the consistency arm sees
  two views per row; no compute-matched control exists"*, and `PAPER_DRAFT.md` §5 calls `cons_lam0`
  the one new training arm the paper cannot go out without. Budget: **3 × 4.4 h ≈ 13 GPU-h**.
- **The premise is false, and the code says so unambiguously.** In
  `src/obtune/objectives.py::compute_loss`:
  - `if self.lam <= 0.0: return task, outputs` — with λ = 0 the loss is `outputs.loss`, plain CE.
  - the collator **pops** `t_ids` / `t_att` / `t_clen` before the batch reaches the student, so the
    student's forward is byte-identical to plain SFT on that batch.
  - the teacher runs under `torch.no_grad()` on its own device.

  **The student never sees the parent view at all — only the frozen teacher does.** There is no
  "extra exposure" to control for.
- **And the data is identical, not merely similar.** From the two arms' own
  `training_summary.json`: **`n_train` 26,841 and `steps` 1,257 for BOTH** `mono_all` and
  `cons_lam3`. The consistency loader *raises* on a missing L0 parent rather than silently reducing
  the set (`DataContractError`), so the row sets cannot drift apart.
- **Verified empirically rather than by code-reading**, because a reading is not a result. A λ = 0
  run at the same seed and shape, against `mono_all`'s own logged losses at the same steps:

  | step | `mono_all` | `cons_lam0` | Δ |
  |---:|---:|---:|---:|
  | 40 | 0.63104 | 0.6317 | +0.0007 |
  | 60 | 0.56746 | 0.5682 | +0.0007 |
  | 80 | 0.54275 | 0.5445 | +0.0017 |
  | 100 | 0.50121 | 0.5013 | +0.0001 |
  | 140 | 0.44918 | 0.4566 | +0.0074 |
  | 180 | 0.39257 | 0.3985 | +0.0059 |

- **Verdict: `cons_lam0` is `mono_all`.** The trajectories agree to 3 significant figures and drift
  by ~1 % by step 180 — the signature of **GPU numerical nondeterminism across different hardware**
  (the two runs used different cards), not of a different objective. **Not claimed:** bit-identity,
  which is not achievable across hardware and is not the question.
- **Consequence: F4 is struck, and 13 GPU-h is not spent.** `mono_all` already **is** the
  data-matched control and is in every comparison the paper makes. The question F4 *meant* to ask —
  "is it the KL or the teacher?" — is a different question and is **already answered by E4**, the
  teacher-variation ablation: untuned-base teacher → the arm collapses (−8.98); breadth teacher →
  it inherits breadth's tax (−4.20); across all three, student ≈ teacher + ~1 pt on the unseen
  family.
- **The process lesson, which is the reusable part.** F4 sat in the plan for three days as a
  *blocking* item costed at 13 GPU-h, and the thing that killed it was **reading the objective's
  own loss function and comparing two numbers already on disk**. `MASTER_REPORT` §29.8 already
  records "in a long campaign, re-test a blocker before believing it"; this is its sibling —
  **re-read the code behind a planned control before building it.** The gap was real as written and
  the writing was wrong.
- **A silent config bug found on the way, and fixed.** `train.max_steps` in a config was accepted by
  the loader and then **ignored**: every other knob in `TrainingArguments` reads the config's
  `train:` block with a default, but `max_steps` read the CLI flag alone. A 61-step probe therefore
  ran the full 1,257-step schedule and hit its 1.5 h walltime at step 226. The config was not wrong,
  it was unread. `objectives.py` now falls back to `tcfg["max_steps"]`, CLI still winning. **The
  timeout is why this entry has losses out to step 180 instead of step 60**, so the bug improved the
  evidence and is recorded rather than quietly patched.
- **Next Steps:** strike F4 from `PAPER_EXPERIMENTS.md` §7 and from `PAPER_DRAFT.md` §5's gap line,
  citing E4 in its place.
