### Target Date: 2026-09-08 (E7 — BH-FDR over the transfer and arms families: what survives multiplicity)
- **Hypotheses / what we're testing:** E7 (paper plan Tier 2, "statistical hardening"), pre-registered
  2026-09-07 as **reported, gates nothing**: BH q < 0.05 over (a) the *transfer family* — 5 specialists
  × 6 seen conditions vs `tuned_L0_s17`, 30 tests — and (b) the *arms family* — `mono_all`,
  `cons_lam3`, `cons_lam1`, `tuned_X1` × 7 conditions (seen6 + X1) vs `tuned_L0`, 28 tests. p is a
  two-sided program-cluster-bootstrap p (2,000 resamples, seed 17); it stands in for the GLMM stack
  (lme4/statsmodels not installed on juno) and is labelled as a substitute. No H1.
- **Setup:** pipeline stage `an_fdr`, job **382559** (35 s, `normal`), `scripts/analysis/37_fdr_family.py`
  → `results/analysis/pipeline/fdr_codellama7b.json` (generated 2026-09-08T02:11Z). Cells from
  `rq1_generic` / `x1_generic` / `objectives_generic` / `baselines_generic`, CodeLlama-7b, Python, heldout.
- **Results:**
  - **Transfer family — 1 of 30 survives.** `tuned_S2` on S2 **+3.36** [+1.74, +5.10], q = 0.030. Six
    cells exclude zero on their raw CI but not after BH: `tuned_L1b` on L1b +2.35 [+0.72, +3.92]
    (q = 0.105); the L0 costs of `tuned_L1r` −1.44 and `tuned_S1` −1.62 (q = 0.230); `tuned_L1b`'s
    structural losses S1 −1.93 / S2 −1.68 (q = 0.230). Every other specialist diagonal is inside its
    CI already (`tuned_L1r` +0.54, `tuned_L2` +0.96, `tuned_S1` +1.60).
  - **Arms family — 8 of 28 survive.** `cons_lam3` on L1b **+4.58** (q = 0.009) and S2 **+2.70**
    (q = 0.014); `cons_lam1` on L1b +4.52 (q = 0.009) and S2 +2.52 (q = 0.028); `mono_all` on L1b
    +2.90 (q = 0.028) and on X1 **−3.79** (q = 0.017); `tuned_X1` on X1 **+4.86** (q = 0.009) and on
    L2 −3.11 (q = 0.019). Does **not** survive: `mono_all`'s L0 cost −1.56 (q = 0.257); `cons_lam3`
    on X1 vs `tuned_L0` +1.32 (q = 0.293); `tuned_X1`'s L1b/L1r/S1 costs (q 0.13–0.33).
- **What worked / hypothesis verdict:** REPORTED, as pre-registered — no verdict changes, because
  no verdict was gated on q. What the family view changes is emphasis: **the specialist transfer
  matrix is almost entirely noise after multiplicity** (1/30), so the paper should not narrate
  individual specialist cells beyond `tuned_S2`'s diagonal; the arms that carry the paper survive —
  `mono_all`'s unseen-family tax (X1 −3.79) and `tuned_X1`'s family gain (+4.86) both at q < 0.02,
  and `cons_lam3`'s L1b/S2 gains at q ≤ 0.014.
- **Observations:** (i) `cons_lam3 − tuned_L0` on X1 (+1.32) not surviving is consistent with the
  headline being `cons_lam3 − mono_all` (+4.59 at three seeds), i.e. consistency *removes* breadth's
  tax rather than beating the clean-code control on the unseen family — the report already says
  this; the FDR table makes it unambiguous. (ii) `mono_all`'s L0 cost is a raw-CI effect only here
  (−1.56 [−3.59, +0.54]); the ~1.7–2.6 pt figure in RQ_SUMMARY §6 comes from the seed-pooled
  reads, and `an_l0cost` (TOST ±1.0) is the pre-registered instrument for it. (iii) Bootstrap-p with
  2,000 draws floors at 0.0005, so the smallest q values are resolution-limited, not exact.
- **New questions / new hypotheses:** none opened; feeds RQ4′ (support) and the writeup's
  statistics paragraph.
- **Next Steps:** cite q-values wherever a single-cell contrast is quoted in the paper; re-run
  `an_fdr` after the pipeline's new arms land so the arms family includes `tuned_X1m/X1s` and the
  half/quarter arms (family membership is then a documented change, not a re-specification).
