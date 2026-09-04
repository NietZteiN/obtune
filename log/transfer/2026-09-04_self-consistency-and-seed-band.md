### Target Date: 2026-09-04 (Self-consistency voting and the `mono_all` seed band — CodeLlama-7b)

First two arms of the accuracy campaign (`CLAUDE_SCRATCHPAD.md` §2026-09-03: W1 self-consistency,
W2 variant augmentation, W3 split-frozen data scale, W4 CodeLlama-13b, plus the leftover
`mono_all` s42/s101 seed band). Everything here is read on the **trainable grid only**
(`eval_source: heldout`, Grid A, six conditions). **H1 is not read**; the single `final_eval`
stays unspent. Aug / scale / 13B are still training (chains 376282→84, 376285→87, 376288→90,
376097→99→100) and get their own entry when they land.

- **Hypotheses / what we're testing:**
  - **H-selfcons (pre-registered in `configs/eval/selfcons_generic.yaml` before the run):** with a
    no-CoT prompt and a short-literal answer, a plurality vote over 8 samples mostly re-derives the
    greedy mode. PREDICTION: vote within ~1 pt of greedy for every system; the informative number
    is any-of-8 − greedy, reported as a *ceiling* that no selector can reach without the label.
    CONFIRM if |vote − greedy| ≤ ~1 pt; REFUTE if the vote moves a tuned system by > 1 pt with an
    interval excluding zero.
  - **H-seed-band:** the `mono_all` = `tuned_L0` tie on the trainable grid (+0.001 [−0.015, +0.017]
    at s17, 2026-09-03) is a seed accident. CONFIRM if a second or third `mono_all` seed separates
    from `tuned_L0` with an interval excluding zero; REFUTE if all three seeds tie.
- **Setup:**
  - Self-consistency: job **376113** (`selfcons_cl7b`, h200 `g-07-01`, 11 min 08 s), config
    `configs/eval/selfcons_generic.yaml` (phase `selfcons_generic`, `eval_source: heldout`,
    `sampling: {n: 8, temperature: 0.7, top_p: 0.95, max_tokens: 64, seed: 17}`), systems `base`,
    `tuned_L0` (`runs/adapters/codellama-7b/python/L0_r32_s17/best`), `mono_all`
    (`…/L0-L1b-L1r-L2-S1-S2_r32_s17/best`), six eval conditions, 28,746 rows. Vote = plurality over
    `repr(scoring.parse_literal(pred_norm)[1])` (`eval_vllm.self_consistency_vote`), ties broken
    by first occurrence; unparsable samples do not vote. Rows carry `sc_any_correct`,
    `sc_first_correct`, `sc_agree`, `sc_n_parsed`, `sc_n_distinct`. Greedy comparator = the same
    system's cells under `results/cells/rq2_generic/` (post-prefix-cache-fix re-runs), joined on
    `item_id` (0 duplicates either side).
  - Seed band: job **376083** (`mono_seeds_cl7b`, 4 min 36 s), `configs/eval/mono_seeds_generic.yaml`
    → systems `mono_all_s42`, `mono_all_s101` under `rq2_generic`.
  - Contrasts: `scripts/analysis/26_campaign_arms.py --model codellama-7b --n-boot 2000` →
    `results/analysis/campaign_2026-09-03.json`. Every interval is a program-cluster bootstrap
    (`obtune.control_relative.bootstrap_delta`, B=2000, seed 17, n=557 programs, 9,582 items pooled).
- **Results:**
  - **Vote8 − greedy, pooled (pts, 95 % CI):**

    | system | greedy | vote8 | Δ | any-of-8 | first sample (T=0.7) | agreement | format_fail greedy → vote |
    |---|---|---|---|---|---|---|---|
    | `base` | 0.2057 | 0.2268 | **+2.11 [+1.45, +2.81]** | 0.3665 | 0.1904 | 0.490 | 0.136 → 0.013 |
    | `tuned_L0` | 0.3861 | 0.3762 | **−0.99 [−1.70, −0.31]** | 0.5576 | 0.3511 | 0.596 | 0.027 → 0.001 |
    | `mono_all` | 0.3918 | 0.3923 | +0.05 [−0.27, +0.37] | 0.4627 | 0.3861 | 0.816 | 0.008 → 0.002 |

    Per condition: `base` is positive on all six with every interval excluding zero (L0 +2.04,
    L1b +2.77, L1r +1.62, L2 +2.40, S1 +2.33, S2 +1.56). `tuned_L0` is negative on all six, only L0
    excludes zero (−1.86 [−3.05, −0.78]; L1b −1.33 [−2.71, +0.06]). `mono_all` is within ±0.4 pt
    everywhere.
  - **Flip decomposition (item-level, vote vs greedy):** `base` right→wrong 2.2 %, wrong→right
    4.3 %, and **39 % of the wrong→right items were greedy format failures** — the vote is partly
    a format repair (unparsable samples are discarded before voting). `tuned_L0` right→wrong 4.5 %
    vs wrong→right 3.5 %; format repair explains 5 % of its gains. `mono_all` 1.15 % vs 1.20 %.
  - **Seed band, `mono_all − tuned_L0` pooled:** s17 +0.56 [−0.89, +2.01] · s42 +0.77 [−0.50, +2.07]
    · s101 +0.01 [−1.30, +1.34]. Same per-condition shape at every seed: L0 −1.74 / −1.38 / −2.34
    (only s101 excludes zero), L1b +2.41 / +2.77 / +1.39 (s17 and s42 exclude zero), L1r/L2/S1/S2 null.
    (The s17 pooled figure differs from the 2026-09-03 entry's +0.001 [−0.015, +0.017] in units
    only — that one is a fraction, this one is points — and in the pooled-vs-mean-of-conditions
    aggregation; both are a tie.)
- **What worked / hypothesis verdict:**
  - **H-selfcons — SUPPORTED for the tuned systems, REFUTED for `base`.** `mono_all` moves
    +0.05 pt; `tuned_L0` moves −0.99 [−1.70, −0.31], just inside the ~1-pt band and in the *wrong*
    direction. `base` moves +2.11 [+1.45, +2.81], outside the band. **Sampling is not free of
    charge: a single T=0.7 sample costs `tuned_L0` 3.5 pts against greedy (0.351 vs 0.386) and
    eight votes only recover ~2.5 of them.** For `mono_all` the samples agree 82 % of the time, so
    the vote is greedy by another name. Self-consistency is not a lever for the tuned systems;
    the campaign drops it.
  - **H-seed-band — REFUTED.** Three seeds, three ties on the pooled grid. The tie is the result,
    not an accident; the per-condition structure (L0 cost, L1b gain) is stable across seeds.
- **Observations:**
  - The any-of-8 ceilings are large — 0.5576 for `tuned_L0` against 0.3861 greedy — and
    **`tuned_L0` has the most headroom of the three while `mono_all` has the least (0.4627)**,
    despite tying on greedy. `mono_all` is the more *peaked* model (agreement 0.82 vs 0.60,
    1.98 vs 3.46 distinct answers per item): breadth of training sharpened the output distribution
    without moving its mode. This is the same "breadth buys format, not transfer" pattern as the
    H1 read, seen from the sampling side. The ceiling is not selectable without a verifier, and
    output prediction has no execution oracle at test time, so it is reported as headroom only.
  - `base`'s vote gain is the format floor again: 39 % of its flips are format repairs, and its
    format_fail drops from 13.6 % to 1.3 %. Against the label-shuffled `formatonly` floor most of
    the +2.1 would vanish. Not worth a floor run; the tuned systems are the ones that matter.
  - Silent-failure checks: 0 duplicate `item_id`s on either side of the join; `sc_n_parsed`
    6.85 / 7.87 / 7.94 of 8 for base / tuned_L0 / mono_all; format_fail after voting ≤ 1.3 %.
- **New questions / new hypotheses:**
  - **H-peaked-breadth:** `mono_all`'s low sample diversity (agreement 0.82) is why merges and
    mixtures built on it cannot beat `tuned_L0` — there is less to ensemble. Testable by
    comparing any-of-8 of `merge_dare_ties` and the MoLE uniform mixture against their greedy.
    Not scheduled; noted for the writeup.
- **Next Steps:**
  - Wait for the three 7B chains and the 13B chain; rerun `26_campaign_arms.py` and the
    control-relative analysis with `--model codellama-13b`; write those up in a separate entry.
  - Master-results artifact: add the vote/greedy table and the seed band.
