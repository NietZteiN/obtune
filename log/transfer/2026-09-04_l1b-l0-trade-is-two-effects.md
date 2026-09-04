### Target Date: 2026-09-04 (H-L1b-L0-trade: the L1b gain is real and located; the L0 cost is not its price)

> Resolves the hypothesis opened in [`2026-09-04_accuracy-campaign-closes.md`](2026-09-04_accuracy-campaign-closes.md).
> No GPU, no new evaluation, no H1 — existing cells only, read at the item level for the first time.

- **Hypotheses / what we're testing:** **H-L1b-L0-trade** — the fingerprint every six-condition
  adapter shows against the clean-code control (L0 −1.4…−2.6, L1b +1.4…+3.9, rest null, pooled a
  tie) is **one mechanism seen twice**: breadth teaches "distrust the identifiers", which `L1b`
  (adversarial renaming) rewards and `L0` (meaningful names) punishes.
  - CONFIRM if the L1b gain and the L0 cost fall on the **same items**, and if both track how much
    renaming an adapter was trained on.
  - REFUTE if the two are separate populations — in which case the tie is an arithmetic
    coincidence between one located effect and one unlocated one, and calling it a "trade" is a
    story laid over a pooled null.

- **Setup:** [`scripts/analysis/29_l1b_l0_trade.py`](../../scripts/analysis/29_l1b_l0_trade.py) →
  `results/analysis/l1b_l0_trade_2026-09-04.json`. Items are paired **across conditions**:
  `<program>::L0::<i>` and `<program>::L1b::<i>` are the same program on the same input with the
  same correct answer, so the pairing is exact rather than matched-sample. 1,658 cases / 553
  programs per arm. Program-cluster bootstrap, B=2000, seed 17.
  - Two strata, defined **only by the control** (`tuned_L0`), so the treatment cannot move them:
    **sensitive** = control right on `L0` and wrong on `L1b` (renaming alone broke it; n=197–201),
    **robust** = control right on both (n=517–584).
  - **The dose ladder** is what separates mechanism from item difficulty: `tuned_S1`/`tuned_S2`
    never saw a renaming, `tuned_L2`/`tuned_L1r` saw a different one, `tuned_L1b` saw exactly this
    one, the six-condition adapters saw all of them. `base` is the untuned floor.

- **Results:**

  | system | renaming dose | recovers `L1b` on sensitive | pay ratio (L0 failure, sensitive ÷ robust) | L0 Δ | L1b Δ |
  |---|---|---|---|---|---|
  | `base` | untuned | 0.107 [0.066, 0.154] | 1.43 [1.22, 1.68] | −17.37 | −16.53 |
  | `tuned_S2` | none | 0.179 [0.125, 0.234] | 2.49 [1.53, 4.07] | −0.06 | −0.66 |
  | `tuned_S1` | none | 0.184 [0.132, 0.237] | 2.15 [1.41, 3.27] | −1.63 | −0.30 |
  | `tuned_L2` | partial | 0.169 [0.117, 0.227] | 3.24 [2.03, 5.34] | −1.15 | +0.84 |
  | `tuned_L1r` | partial | 0.229 [0.173, 0.295] | 3.01 [1.94, 4.78] | −1.51 | +0.24 |
  | `tuned_L1b` | **matched** | **0.408 [0.336, 0.480]** | 3.62 [2.43, 5.60] | −1.27 | +2.35 |
  | `mono_all` s17 | six | 0.487 [0.417, 0.558] | 3.10 [2.28, 4.24] | −1.81 | +2.41 |
  | `mono_all` s42 | six | 0.502 [0.431, 0.577] | 3.24 [2.31, 4.55] | −1.39 | +2.77 |
  | `mono_all` s101 | six | 0.497 [0.427, 0.569] | 2.45 [1.77, 3.34] | −2.41 | +1.39 |
  | `mono_aug` | six | 0.502 [0.431, 0.577] | 2.41 [1.81, 3.18] | −2.59 | +3.02 |
  | `mono_scale` | six | **0.543 [0.472, 0.614]** | 2.39 [1.79, 3.21] | −2.11 | +3.92 |
  | `mono_all` 13B | six | 0.439 [0.373, 0.513] | 3.81 [2.83, 5.14] | −2.29 | +2.71 |

  - **Recovery is a strict dose-response.** Zero-dose specialists sit at 0.169–0.184, partial dose
    reaches 0.229, the matched specialist **0.408 [0.336, 0.480]** — disjoint from every partial-dose
    interval (`tuned_L1r` upper bound 0.295) — and breadth 0.439–0.543.
  - **The pay ratio is flat across the same ladder.** `tuned_S2`, which never saw a renaming,
    posts 2.49 [1.53, 4.07]; `mono_all` s17 posts 3.10 [2.28, 4.24]. Every tuned interval overlaps
    every other. Only `base` is lower (1.43), and that is a floor effect — it fails `L0` on 46 % of
    robust items, so it has little room to be *disproportionately* hurt anywhere.
  - The naive item-level correlation `corr(d_L0, d_L1b)` is **positive** for every arm
    (+0.32…+0.42), which is the opposite sign the trade predicts — and `base`, no kind of breadth
    adapter, posts the largest of all at **+0.4677 [+0.4178, +0.5202]**. The correlation measures
    shared item difficulty between any two systems and cannot answer the question.
  - Conditional lift runs the wrong way too: P(win `L1b` | lose `L0`) is 0.032–0.061 against an
    unconditional P(win `L1b`) of 0.095–0.114, i.e. **losing on `L0` makes an item *less* likely to
    be one breadth wins on `L1b`.**

- **What worked / hypothesis verdict:** **H-L1b-L0-trade REFUTED as stated, with its first half
  SUPPORTED.**
  - *Supported:* breadth really does learn identifier-distrust, and the `L1b` gain is **located** —
    it lives on the items where renaming alone broke the clean-code control, and its size tracks
    renaming exposure across seven arms.
  - *Refuted:* the `L0` cost is **not the price of that gain**. It does not concentrate on
    identifier-sensitive items any more than it does for an adapter that never saw a renaming, and
    the items breadth loses on `L0` are not the items it wins on `L1b`. The pooled tie is one
    located effect plus one unlocated one that happen to be the same size.

- **Observations:**
  - **Breadth recovers renamed items at least as well as the specialist trained on that exact
    transform** (0.487–0.543 vs `tuned_L1b`'s 0.408; `mono_scale`'s interval clears the
    specialist's upper bound by 0.008 and no other arm separates). Breadth is not a diluted `L1b`
    adapter on this axis — if anything the other five conditions help.
  - **`tuned_S2` is the only tuned system with no `L0` cost at all** (−0.06 against −1.15…−2.59 for
    everything else, `tuned_S1` included). The project's one positive-transfer arm is also the one
    whose skill does not trade against reading clean code — consistent with the dead-code-elimination
    account in the master report §15/§16, and not something the trade hypothesis anticipated.
  - The `L0` cost is not explained by renaming exposure either: `tuned_S1` never saw a renaming and
    pays −1.63. Whatever it is, it accompanies training on almost any non-`L0` condition.
  - Method note worth keeping: **the naive correlation and the raw pay gap in points both "confirmed"
    the hypothesis** (the gap is +19…+31 pts for every breadth adapter). Both collapse the moment a
    zero-dose arm and an untuned floor are put beside them. The negative control was again the whole
    experiment — the fourth time in this project (`mole_random`, `l0merge`, oracle-of-k, the
    invariance arm).

- **New questions / new hypotheses:** **H-L0-cost-source** — if the `L0` cost is not identifier
  distrust, what is it? It appears for every specialist except `S2`, at roughly constant size,
  which points at something generic about training on a transformed distribution (format or
  prior shift) rather than anything condition-specific. Testable from existing cells: does the cost
  concentrate on items where the *format* of the answer is unusual, or on long programs?

- **Next Steps:** fold into the master report §22.5 (the fingerprint is now one located effect plus
  one unlocated one) and drop H-L1b-L0-trade from §24's open list. H-L0-cost-source replaces it.
