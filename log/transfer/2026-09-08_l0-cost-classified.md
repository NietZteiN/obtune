### Target Date: 2026-09-08 (Read — E11 / RQ1′–RQ4′ support: every arm's L0 cost classified — 21 arms pay it, 1 is certified L0-free, 38 are underpowered at a ±1.0 margin)
- **Hypotheses / what we're testing:** none verdicted. Pre-registered as a *report* (`CLAUDE_SCRATCHPAD.md`
  E11): every arm's `__L0` cell vs `tuned_L0`, program-clustered bootstrap, TOST equivalence at
  ±1.0 pts, classified **L0-free** (CI inside ±1.0) / **pays L0 cost** (ci_hi < 0) / **gains on L0**
  (ci_lo > 0) / **underpowered** (otherwise). "Reported, gates nothing."
- **Setup:** `an_l0cost` **382560** (`38_l0_cost.py --model codellama-7b`,
  `results/analysis/pipeline/l0_cost_codellama7b.json`), run last so every arm in the campaign is
  included: 60 arms, n_prog 557 on every row. No H1.
- **Results — the classification:**
  - **L0-free (1):** `tuned_L0_s17` +0.36 [+0.06, +0.72] — a seed twin of the reference, which is
    the only kind of arm whose CI is narrow enough to fit inside ±1.0 at this n.
  - **Gains on L0 (0).** Nothing beats clean-only on clean code.
  - **Pays L0 cost (21), ordered:** `curr_sft` −1.68*, `mono_all_s101` −2.04*, `tuned_X1m` −2.22*,
    `mono_aug` −2.28*, `neg_data` −2.34*, `align_span_lam1_mm` −2.40*, `x1_resample` −2.57*,
    `align_lam1` −3.05*, `l0merge_ties` −3.23*, `align_lam1_mm` −3.29*, `tuned_L0_quarter` −3.29*,
    `neg_ul` −3.47*, `tuned_X1s` −4.25*, `align_lam3` −4.67*, `merge_ties` −5.93*, `cons_tbase`
    −12.04*, `formatonly` −14.49*, `base` −16.95*, `merge_dare_linear` −27.37*.
  - **Underpowered (38), i.e. |Δ| small but the CI spans both ±1.0 and 0:** every consistency arm
    (`cons_lam1` −0.12, `cons_lam3` −0.48 [−1.98, +1.14], `cons_lam3_s42` −0.36, `cons_lam3_s101`
    −0.72, `cons_lam5` −0.96, `cons_lam10` −1.32, `cons_same_lam1` −0.90, `curr_kl` −0.06,
    `cons_tmono` −1.38), `mono_all` −1.32 [−3.35, +0.66], `mono_all_s42` −1.14, `mono_half` −1.62,
    `mono_quarter` −1.56, `mono_scale` −1.68, `mono_allX` −1.56, `tuned_X1` −1.56 [−3.17, +0.06],
    `tuned_L0_half` −1.38, `merge_dare_ties` −0.48, `l0merge_dare_ties` −1.38, all ten specialist
    seeds (+0.48 … −1.26), the `align_lam0`/`0.3`/`span_lam1`/`span_lam3` arms (−1.14 … −1.92).
- **Reading.**
  1. **The instrument, not the arms, is what this read mostly measures.** A single 557-program L0
     cell at p ≈ 0.4 gives a program-clustered CI of roughly ±1.5–2.0 pts, so a ±1.0 TOST margin can
     only be met by an arm whose point estimate is essentially zero *and* whose errors are correlated
     with the reference's (the seed twin). "L0-free" was therefore unreachable by construction for
     any genuinely different arm, and the 38 "underpowered" verdicts are the honest label. The
     campaign's earlier "no L0 tax" statements for `cons_lam3` (−0.30 / −0.48, CI spanning zero) are
     *consistent with* L0-free but do not *certify* it; the paper should say "no detectable L0 cost
     at n = 557" rather than "L0-free". Certifying ±1.0 would need paired seeds pooled or ~4× the
     programs — a design note for any follow-up, **not** a margin to be relaxed post hoc.
  2. **The ordering is nonetheless informative and matches the campaign's story.** Point estimates
     rank the families exactly as RQ1′/RQ3′ predict: consistency (−0.1 … −1.0 at λ ≤ 5) < breadth
     (−1.1 … −1.7, and −2.0* / −2.3* on the s101 / `mono_aug` variants) < X1-family training
     (−1.6 / −2.2* / −2.6* / −4.3*) < alignment and negatives (−1.9 … −3.5*, `align_lam3` −4.7*)
     < TIES merges (−3.2* … −5.9*) ≪ `cons_tbase` −12.0*, `formatonly` −14.5*, `base` −17.0*,
     `merge_dare_linear` −27.4*. Every arm that *changed the objective away from the SFT loss* pays
     more on L0 than breadth does, except consistency; every arm that *changed the data* pays about
     what breadth pays. `cons_lam10` (−1.32) shows the KL weight can be pushed until it costs as much
     as breadth — λ = 3 sits where the seen gain is kept and the L0 cost is at its floor.
  3. **Data volume costs L0 in the direction one would expect:** `tuned_L0_quarter` −3.29*,
     `tuned_L0_half` −1.38 (E12's H-sat-L0 refutation, seen from the L0 side); `mono_quarter` −1.56
     vs `mono_all` −1.32 — breadth's L0 cost does *not* fall with less data, so it is not a
     capacity effect. Consistent with the rank sweep (`21e6d7e`, "capacity does not explain breadth hurts").
  4. **E11's actual question — *where* on L0 the cost lands (answer format vs length) — is not
     answered here.** `38_l0_cost.py` classifies arms; it does not stratify the cost by answer type
     or program length. That part of E11 remains open and is analysis-only on existing cells.
- **Cross-check with E6:** `39_x1_split.py` reported `tuned_X1` L0 −1.68* against `tuned_L0`
  0.4275; this script reports −1.56 [−3.17, +0.06] against 0.4263. Point estimates agree to 0.1 pt;
  the two scripts differ in the reference cell (which `tuned_L0` seed set) and in bootstrap draw, and
  the CI sits on the boundary either way. `tuned_X1`'s L0 cost should be reported as ~−1.6, marginal.
- **Caveats.** 7B only; TOST at ±1.0 is the pre-registered margin and stands; the same `tuned_L0`
  reference for all 60 rows means the 60 CIs are not independent (BH-FDR was not applied here — the
  read gates nothing).
- **Next:** the by-format / by-length stratification that E11 actually asks for (`38_l0_cost.py`
  extension, CPU only, no new evals). Docs: `docs/RQ_SUMMARY.md` §6 RQ4′ row and §6.1 L0 row
  footnote; `docs/PAPER_EXPERIMENTS.md` E11.
