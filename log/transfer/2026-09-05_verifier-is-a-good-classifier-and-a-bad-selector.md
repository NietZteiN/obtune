### Target Date: 2026-09-05 (Best-of-n rerank: H-verifier REFUTED, H-self-judge REFUTED backwards; ranking quality does not convert to selection gain)

Lever 2b evaluated end to end (`cand_*` 377859/377860/377945, `tr_verif` 377861, `rerank`
377946) on the six-condition trainable heldout grid: 9,582 items, 557 programs, 8 samples at
T=0.7 plus one greedy row per item. **H1 is not read**; `final_eval` stays unspent. The
verifier checkpoint was chosen **on val only**. Intervals are 2,000-resample bootstraps
clustered by `program_id`. Pre-registration: [`2026-09-05_verifier-rerank-submitted.md`](2026-09-05_verifier-rerank-submitted.md).

- **Hypotheses:**
  - **H-verifier — REFUTED.** The rule was: `verifier − greedy` > 0 with the program-cluster CI
    excluding 0 **and** above the log-prob controls. It is **+1.09 [0.00, 2.17]** — the lower
    bound touches zero rather than clearing it — and against the zero-training control it is
    **+0.38 [−0.58, +1.38]**. Both conjuncts fail. A 3.2 h LoRA does not beat `cum_logprob`.
  - **H-self-judge — REFUTED, and in the opposite direction to the one posed.** The hypothesis
    was that the untuned base judges about as well as the trained verifier ("knows how, not
    when"). The base as judge scores **AUC 0.347** — *below chance* — and costs **−5.52
    [−6.75, −4.28]** pts as a selector. It is not uninformative about its own correctness; it
    is **anti**-informative (an inverted base judge would post AUC 0.653). "Knows how but not
    when" understates the problem: on this task the base's confidence points the wrong way.
- **Results — pooled heldout (n = 9,582):**

  | selector | acc | Δ vs greedy [95 % CI] |
  |---|---|---|
  | greedy | 0.3854 | — |
  | **any-of-8 (ceiling, not a selector)** | **0.5628** | **+17.74 [+16.38, +19.09]** |
  | vote (maj@8) | 0.3756 | −0.98 [−1.67, −0.33] |
  | `cum_logprob` | 0.3907 | +0.53 [−0.09, +1.15] |
  | `cum_logprob / n_tokens` | 0.3889 | +0.34 [−0.21, +0.89] |
  | verifier, base (zero-shot judge) | 0.3302 | **−5.52 [−6.75, −4.28]** |
  | **verifier, ckpt-1132 (chosen on val)** | 0.3963 | **+1.09 [0.00, 2.17]** |

  Per condition the chosen verifier is +0.12 to +2.04, and only `S2` excludes zero
  (+2.04 [+0.36, +3.84]) — one cell out of six, which BH-FDR across the family would not keep.
- **The mechanism — a good classifier is not a good selector.** The verifier is genuinely
  strong at the task it was trained on: **AUC 0.887**, acc@0 0.781 on 35,553 held-out
  candidates. It simply cannot spend that. Decomposing over items (mean 3.71 *distinct*
  candidates each):

  | | fraction |
  |---|---|
  | items with **no** correct candidate — unreachable by any selector | **0.437** |
  | items with a correct candidate | 0.563 |
  | …of those, greedy already had it | 0.685 |
  | …of those, verifier picks it | 0.704 |
  | …verifier **rescues** a greedy miss | 0.131 |
  | …verifier **breaks** a greedy hit | 0.112 |

  The rescues and the breakages nearly cancel: +0.131 − 0.112 = +0.019 of the 0.563 reachable
  subset ≈ **+1.1 pts**, which is exactly the measured effect. The 17.74-pt any-of-8 ceiling is
  not 17.74 pts of headroom for a selector — 43.7 % of items have no correct candidate at all,
  and on the rest the discriminations the verifier gets wrong are the same ones the sampler
  gets wrong. **AUC 0.887 buys +1.1 pts.** This is the concrete answer to a question the
  self-consistency entry left open ([`2026-09-04_self-consistency-and-seed-band.md`](2026-09-04_self-consistency-and-seed-band.md)):
  the any-of-n gap was quoted there as "headroom only", and this quantifies how little of it a
  strong reranker converts.
- **What did not happen:** no H1 read; checkpoint chosen on val (ckpt-1132, val AUC 0.901)
  before any heldout number was computed; no selection on heldout.
- **Consequence for H-trace-complement.** That hypothesis was pre-registered *gated on this
  one clearing*, and it did not. It does **not** inherit a pass, and it is not run under the
  old registration. Whether it deserves its own is a live question with a real argument on
  each side: the trace/direct case is a **two-way** choice between two differently-trained
  systems (break-even is 52 % on the binary discrimination, against top-1-of-3.71 here), and
  AUC 0.887 is comfortably above that — but the failure above was *not* a ranking-power
  failure, so the analogy may not hold. Re-registered separately in a later entry or dropped;
  not carried silently.
- **Provenance:** `results/analysis/rerank/codellama-7b/tuned_L0/rerank_report.json` and
  `{val,heldout}_scored.parquet`; verifier `runs/adapters_verifier/codellama-7b/python/tuned_L0_r32_s17`
  (36,268 balanced examples from 99,523 distinct (item, answer) pairs — the 40k cap never bound,
  the 18,134 positives did; `train_loss` 0.203). Candidates
  `runs/candidates/codellama-7b/tuned_L0/{val,train,heldout}.parquet`.
- **One infrastructure note:** `cand_heldout` 377858 and `ck_X1`/`ck_monoX` 377842/377844 all
  died on the same defect in three different code paths — a single over-long prompt raising
  inside vLLM instead of being dropped. `drop_overlong` existed and was wired into the scoring
  path only; it is now called from the candidate sampler and the ckpt-select path as well
  (commits `ebbe818`, `a20e72b`). The held-out sampler drops 6 items (all `apps_1615_0`, a
  20,055-token literal), ckpt-select drops 3 (`apps_3529_0::X1`).
