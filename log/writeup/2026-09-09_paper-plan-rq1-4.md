### Target Date: 2026-09-09 (paper plan reorganised around RQ1–RQ4; experiment list F1–F9)
- **Hypotheses / what we're testing:** Organisational day, no experiment and no cell read. The user
  fixed four RQs — **RQ1** can single-obfuscation adaptation strategies (routing / merging / breadth)
  generalise to stacked obfuscation; **RQ2** what is learned in single-transform adaptation and why it
  fails on composites; **RQ3** does paired-consistency anchoring to clean-code behaviour resolve it;
  **RQ4** genuine structural robustness or a new surface heuristic — each with a stated finding. The
  question for the day: which of those findings does the record already support, which does it
  support only in a narrower form, and which are unmeasured?
- **Setup:** `docs/PAPER_FRAMING.md` rewritten (the 2026-09-08 P1–P4 framing is kept in git,
  `3825ad0`); `docs/PAPER_EXPERIMENTS.md` §7 added. Sources: `RQ_SUMMARY.md` §4–§7, the pipeline
  JSONs under `results/analysis/pipeline/`, `REPORT_2026-08-17_geometry-and-attempted-repairs.md`,
  and the cell inventory under `results/cells/`. Every number is one already published.
- **Results:** the mapping, by status.
  ✅ supported as stated — RQ3's +4.59 (`cons_lam3 − mono_all` @ X1, q = 0.0049, scale/Llama/JS
  replications), its stacked-seen retention (+4.76/+4.26/+5.63 over `tuned_L0`; over breadth +1.36*
  at 13B, +2.58* at 34B), no detectable L0 cost, and the teacher/view ablations (E4: base teacher
  −8.98, breadth teacher −4.20; `cons_same` +2.31 below on X1); RQ2's cue evidence (X1 split, X1→H1
  lossless, identifier-ordered composite gains, polarization, reverse task, human divergence).
  ⚠️ supported in a narrower form — RQ1's breadth leg: breadth does **not** fail on stacked-seen
  inputs (+3.49/+2.90/+3.05 at 7B/13B/34B, +4.15 at depth 3/4); it fails on unseen (−3.79/−4.28/−2.64)
  and clean (−1.74/−2.34/−2.63). RQ4's reverse-task leg: `cons_lam3 − base` +0.49 [−1.38, +2.30] is
  "undamaged", not "consistent performance". RQ3/RQ4's unseen-family number is the teacher's (E4),
  so the arm is 7th of 33 on X1.
  🚫 contradicted — "merging fails through contrasting task-vector geometries": the 2026-08-17 read
  found same-data cross-seed adapters near-orthogonal (cos 0.053, sign conflict 0.487) *and* merging
  fine; geometry is initialisation.
  ❌ unmeasured on the current panel — routing and merging on **any** stack (only Qwen-1.5B on the
  34/40 subset §4.1 forbids ranking; no router decision dump on a stack exists); **no stack containing
  an unseen family has ever been built**, so RQ1's "failures worsen with divergence" and RQ4's
  "stacks containing unseen families" have no data point; no specialist on a CodeLlama composite, so
  RQ2's "stacking destroys the cue" is an inference, not a measurement; no compute-matched control
  for the consistency arm.
- **What worked / hypothesis verdict:** n/a. One existing hypothesis can be closed from existing cells
  without compute: **H-stack-identifier** — structural-only depth-3 `C3_S1_S3_S4` gives
  `mono_all − tuned_L0` +1.61 [−1.02, +4.31] n.s. against +6.10* with an identifier part
  (`composite_depth_codellama7b.json`); the 09-07 CONFIRM condition is met. Filed as F3a; the read
  itself is a separate entry when written.
- **Observations:** The experiment list is F1–F9 in `PAPER_EXPERIMENTS.md` §7, ordered by what the
  stated findings cannot go out without: **F2** (six composites with X1/X1m/X1s as a part — the
  divergence ladder d0…d4; ~1.5 GPU-h) decides RQ4 and supplies RQ1's last sentence; **F1** (four MoLE
  arms, five merges, three specialists on the ten existing composites + router decision dump; ~2
  GPU-h) supplies RQ1's first two legs; **F3** turns RQ2's causal sentence into a paired order-pair
  test on `C_L1r_S1`/`C_S1_L1r`; **F4** (`cons_lam0`, paired SFT without KL; ~14 GPU-h for three seeds)
  is the compute-matched control RQ3 lacks; F5 (resampled X1 surfaces), F1b (CodeLlama geometry,
  cross-seed), F7 (inverse at 13B/34B), F8 (13B second seed), F6 (= E5b, design-gated) harden.
  ~22 GPU-h without F8/F6. H1 is never stacked and never read; every unseen component is X1.
- **New questions / new hypotheses:** F-rules drafted in §7 (H-F1-route, H-F1-merge, H-F2-breadth-
  monotone, H-F2-cons-no-tax, H-F2-cons-vs-breadth, H-F2-family-stacks, H-F3-order, H-F3-cue-items,
  H-F4-kl, H-F5-stability, H-F7-no-harm) — to be frozen in `CLAUDE_SCRATCHPAD.md` before submission.
- **Next Steps:** on the user's go: pre-register F2 + F1 rules, calibrate the X1-composite `size_cap`
  on real programs, build, submit eval-only jobs; write F3a's read; queue F4 s17.
