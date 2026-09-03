### Target Date: 2026-09-03 (Cluster-bootstrap CIs — and three claims that do not survive them)

> **CORRECTS** [`2026-09-01_codellama-replication.md`](2026-09-01_codellama-replication.md),
> [`2026-09-02_codellama-master-report-tranches.md`](2026-09-02_codellama-master-report-tranches.md)
> and [`2026-09-02_h1-codellama-pilot.md`](2026-09-02_h1-codellama-pilot.md). Those entries are
> NOT edited (`../../CLAUDE.md` §6, append-only). Every number in them was a POINT ESTIMATE
> reported without an interval; three were stated as findings and do not survive interval
> estimation.

- **Hypotheses / what we're testing:** not a new experiment. Cluster bootstrap by `program_id`
  (B=2000, seed 17) over every contrast the CodeLlama campaign reported, because
  `../../CLAUDE.md` §4 requires it and because several quoted gaps were small enough that the
  ordering alone could not carry them.

- **Setup:** existing cells only, no GPU. Resampling by program rather than by item, because
  multiple input cases per program are correlated and item bootstrap would understate the CIs.

- **Results:**

  **SURVIVES — RQ1, against the format floor (n=412):**

  | statistic | estimate | 95 % CI |
  |---|---|---|
  | diagonal gain | +0.1898 | [+0.1663, +0.2124] |
  | off-diagonal gain | +0.1718 | [+0.1488, +0.1938] |
  | diagonal − off-diagonal | **+0.0180** | **[+0.0129, +0.0234]** |
  | mean off-diagonal **TR** | **+0.9057** | **[+0.8784, +0.9322]** |

  **SURVIVES — routing is worth nothing, and now that is measured rather than asserted:**

  | contrast | estimate | 95 % CI |
  |---|---|---|
  | router − uniform | +0.0003 | [−0.0076, +0.0081] |
  | router − random | +0.0000 | [−0.0081, +0.0081] |
  | uniform − base (the mixture gain) | **+0.2047** | **[+0.1788, +0.2298]** |

  **SURVIVES — on H1:** `merge_dare_ties − l0merge_dare_ties` **+0.0148 [+0.0025, +0.0280]**;
  `tuned_S2 − tuned_L0` +0.0453 [+0.0247, +0.0667]; `merge_dare_ties − merge_ties` +0.0527
  [+0.0321, +0.0741]; the floor `formatonly − base` +0.0049 [−0.0025, +0.0124] (i.e. zero).

  **DOES NOT SURVIVE — three claims:**

  | claim as stated | actual | verdict |
  |---|---|---|
  | "`tuned_L0` **beats** `mono_all` on H1" | +0.0058 [−0.0173, +0.0288] | **not distinguishable from 0** |
  | "the merge-leads-the-panel result is REFUTED (`tuned_S2` beat `merge_dare_ties`)" | +0.0066 [−0.0107, +0.0247] | **not distinguishable from 0** |
  | "LOTO: an unseen transform **costs** 1.1 points" | −0.0108 [−0.0218, +0.0011] | **not distinguishable from 0** |

- **What worked / hypothesis verdict:** the headline results stand and two get STRONGER; three
  statements were overclaimed and are corrected here.
  - **RQ1 and routing are unaffected.** TR = 0.906 has a tight interval, and the
    router-vs-random CI is narrow enough to assert that dispatch is worth nothing rather than
    merely failing to detect an effect. That distinction was not available from point estimates.
  - **LOTO is STRONGER than reported, not weaker.** I wrote "an unseen transform costs 1.1
    points". The interval includes zero, and the fraction of `mono_all` recovered is
    **0.9452 [0.8940, 1.0058]** — an interval containing 1.0. The defensible claim is that a
    fold which never saw a transform is **not distinguishable from the model trained on all
    six**, which is a bigger result than a small measured cost.
  - **The H1 headline must be "matches", not "beats".** `tuned_L0` vs `mono_all` is
    +0.006 [−0.017, +0.029]. The master report's own wording for the Qwen panel is that
    `tuned_L0` "matches every obfuscation-trained specialist" — that is the correct verb, and
    the ordering of two point estimates does not upgrade it.
  - **The Qwen/CodeLlama merge "departure" was not a departure.** `tuned_S2` outranking
    `merge_dare_ties` by 0.0066 is inside noise. I recorded it as "a genuine cross-family
    departure, not smoothed over" — that framing was wrong in the opposite direction from the
    usual failure: I treated an unestablished difference as a finding because it was
    inconvenient, which is not the same as being careful.

- **Observations:**
  - **What separates the surviving claims from the failed ones is not effect size but interval
    width relative to it.** `merge_dare_ties − l0merge_dare_ties` (+0.0148) survives while
    `tuned_S2 − merge_dare_ties` (+0.0066) does not, and both are "about a point". Ranking
    tables invite exactly this error, and every table in the two corrected entries is a
    ranking table.
  - **The H1 panel is n=405 programs**, the smallest in the campaign, so its CIs are the widest
    — which is precisely where the closest orderings were reported.

- **New questions / new hypotheses:** none. This is an inference pass, not an experiment.

- **Next Steps:** (1) `H-closest-specialist` is now unsupported as motivated — it was opened on
  the `tuned_S2` > `merge_dare_ties` ordering, which is noise; it can still be tested from LOTO
  at zero cost but has no evidence behind it. (2) The GLMM stack remains blocked (`r_analysis`
  did not survive the migration), so these bootstraps are the inferential story.
