### Target Date: 2026-09-08 (Read — E11b / RQ1′: the L0 cost is **not** where §22.6 guessed — it lands on the ordinary items the clean-code adapter gets right, not on the exotic tail)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` and committed as
  **`e5d08ab`** *before* `scripts/analysis/43_l0_stratify.py` existed. **H-L0-format** CONFIRMED iff
  Δ(unusual) − Δ(common) has ci_hi < 0; REFUTED iff that interval lies inside ±1.0 (E11's TOST
  margin); else INCONCLUSIVE. **H-L0-length** the same on Δ(T3 long) − Δ(T1 short).
  **H-L0-answerlen** reported, not verdicted. Gates nothing.
- **Setup:** `an_l0strat` **383161** (`43_l0_stratify.py --model codellama-7b`,
  `results/analysis/pipeline/l0_stratify_codellama7b.json`), CPU, no new evaluation. Item metadata
  joined from `data/eval/heldout/items/L0/python.jsonl` — 1,671 items / 557 programs, the exact set
  every 7B L0 cell was graded on. Primary unit **`mono_all` pooled over 3 seeds** against the pooled
  clean-code control {`tuned_L0`, `tuned_L0_s42`} (the seed-pooling power fix the E11 read called
  for). One program-clustered resample per bootstrap draw with every stratum recomputed on it, so
  the between-stratum differences are paired. No H1.
- **The strata, as they came out:** format classes `int` 34.8 % · `str` 31.3 % · `list` 20.1 % ·
  `bool_none` 9.6 % · `dict_set` 3.1 % · `float` 1.1 % → **common = {int, str, list}** (86.2 % of
  items), **unusual = {bool_none, dict_set, float}** = 230 items. LOC terciles 3–5 / 5–9 / 9–56
  (185 / 186 / 186 programs). Answer-length terciles at the item level.
- **Results — `mono_all` (3 seeds), overall −1.74 pts on L0:**

  | stratum | Δ pts [95 % CI] | control acc |
  |---|---:|---:|
  | answer format **common** | **−2.38** [−3.94, −0.78] | 0.402 |
  | answer format **unusual** | +2.32 [−1.51, +6.10] | 0.596 |
  | **unusual − common** | **+4.70** [+0.44, +8.89]* | |
  | LOC T1 (3–5) | −1.11 [−4.11, +1.66] | 0.435 |
  | LOC T2 (5–9) | −0.99 [−3.13, +1.21] | 0.432 |
  | LOC T3 (9–56) | −3.11 [−5.80, −0.32] | 0.419 |
  | **T3 − T1** | −2.00 [−5.87, +2.20] | |
  | answer length T1 (short) | **−4.16** [−6.72, −1.51] | 0.489 |
  | answer length T2 | −1.35 [−3.98, +1.27] | 0.486 |
  | answer length T3 (long) | +0.30 [−2.16, +2.74] | 0.311 |
  | **T3 − T1** | **+4.46** [+0.96, +8.15]* | |

- **Verdicts, by the frozen rule.**
  - **H-L0-format INCONCLUSIVE.** The rule was one-sided (ci_hi < 0 confirms, ±1.0 refutes) and the
    result is neither: **+4.70 [+0.44, +8.89]**. **The rule is not re-specified.** But the honest
    report of what the data show is that the effect is *significant in the direction opposite to the
    hypothesis* — the cost is on the **common** formats and there is none on the unusual tail. A
    one-sided rule with no branch for a significant reversal is a rule-design mistake, recorded here
    so the next pre-registration states both tails.
  - **H-L0-length INCONCLUSIVE.** −2.00 [−5.87, +2.20]: the point estimate is in the hypothesized
    direction (T3 −3.11 is the only LOC stratum whose own interval clears zero) but the difference
    neither clears zero nor fits inside ±1.0. Not resolved at this n.
  - **H-L0-answerlen (exploratory):** +4.46 [+0.96, +8.15] — the same reversal, and the sharpest
    version of it. Breadth's whole L0 cost sits on **short answers** (−4.16) and is exactly zero on
    long ones (+0.30).
- **Is the reversal a floor artifact?** No. A points-scale delta is bounded by the control's accuracy
  in that stratum, so a stratum where the control is weak mechanically permits a smaller fall. Here
  the bound runs *against* the finding: the control is **stronger** on unusual formats (0.596, i.e.
  59.6 pts of room to fall) than on common ones (0.402), and breadth still falls only on the common
  ones. As a fraction of the room available: common −5.9 %, unusual +3.9 %. The answer-length result
  is the one where the confound bites (T1 room 48.9 vs T3 room 31.1), but the relative form keeps the
  sign and most of the size (−8.5 % vs +1.0 %). Point-estimate ratios, no intervals; reported as a
  sanity check, not a second test.
- **The `base` reference row is what makes the null informative.** Run through the same strata,
  `base − control` (−17.19 overall) **does** localize on program length: T3 −21.86 against T1 −14.51,
  **T3 − T1 −7.36 [−13.67, −1.13]\***. So these 557 programs *can* resolve a length effect when one
  is there; they cannot resolve a ~2-pt one. That converts "H-L0-length INCONCLUSIVE" from an
  instrument failure into a bound: **breadth's L0 cost is not concentrated on long programs at
  anything like the scale at which the base model's deficit is.** `base` also shows the format
  reversal (+8.33 [+1.90, +14.70]) — the unusual stratum is where *any* weak model does relatively
  best, because it is dominated by `bool_none`.
- **The confound that must be stated.** "Unusual format" and "easy item" are the *same stratum* here:
  `bool_none` is 9.6 % of items and the control scores 0.596 on the unusual group against 0.402 on
  the common one. This read therefore cannot separate *format rarity* from *item easiness*, and the
  honest claim is the weaker one — **breadth's cost avoids the easy short-answer tail and lands on
  the bulk of ordinary items** — not "rare formats are protected".
- **The other arms.**
  - `cons_lam3` (3 seeds, overall −0.76): the same shape at about half the size — common −1.20
    [−2.48, +0.12], unusual +2.03, unusual − common +3.23 [−0.10, +6.66]; short answers −2.24
    [−4.23, −0.16]. Consistency pays a smaller version of *the same* cost, not a different one.
  - `tuned_X1` (overall −1.80): a **different** shape. No format reversal (unusual − common −0.44
    [−3.68, +2.96]), no length gradient, and the cost sits in the middle answer-length tercile
    (−3.33 [−5.74, −0.92]). Whatever the X1-family arm gives up on clean code, it is not what
    breadth gives up.
- **Reading.** §22.6 asked whether the L0 cost concentrates on unusual answer formats or on long
  programs. The answer is **neither, and the first is backwards**. Breadth's clean-code cost is spread
  across the ordinary case — common answer types, short answers, programs of every length — which is
  precisely where the clean-code-only adapter is strongest. That is a more damaging description than
  the one the section was fishing for: it is not a tail effect that could be documented away as a
  formatting quirk, it is a uniform erosion of the model's best behaviour. It also fits the RQ3′
  mechanism from E4 the same day: what breadth loses is *the clean-code teacher's ordinary
  competence*, which is exactly what `cons_lam3` distils back and exactly why `cons_lam3`'s residual
  cost has the same shape at half the size.
- **Caveats.** 7B only; single item set (Grid B heldout, Python); format classifier is applied to the
  gold literal, so it captures answer *type*, not prompt formatting; the format/difficulty confound
  above; INCONCLUSIVE verdicts are exactly that — no directional claim is being smuggled in as a
  verdict, only reported as the observed sign.
- **Next:** none required. If it is ever worth resolving, the length question needs ~4× the programs
  and the format question needs a stratum design that breaks the rarity/easiness confound (e.g.
  matching on control accuracy). Docs: `docs/RQ_SUMMARY.md` §6 RQ1′, `docs/PAPER_EXPERIMENTS.md` E11.
