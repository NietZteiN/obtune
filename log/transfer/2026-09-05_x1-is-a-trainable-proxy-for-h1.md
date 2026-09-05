### Target Date: 2026-09-05 (X1 heldout: the diagonal is real, and X1 predicts H1 to r = 0.999 without touching it)

`ev_X1` 378459 on the held-out X1 column, CodeLlama-7b, 1,214 items / 405 programs. **No new H1
read**: the H1 numbers below come from the already-spent `h1_codellama` pilot phase, and no
selection of any kind used them. Intervals are 2,000-resample program-clustered bootstraps.
Pre-registration: [`2026-09-05_x1-family-arm-and-llama31-gate.md`](2026-09-05_x1-family-arm-and-llama31-gate.md).

- **Hypotheses:**
  - **H-X1-family — first conjunct CONFIRMED.** The rule has two parts: `tuned_X1 − tuned_L0` on
    X1 excludes zero, **and** the campaign-end H1 read of `tuned_X1`/`mono_allX` exceeds the
    `tuned_S2` leader outside its interval. Part one is **+4.86 [+2.80, +6.92]**. Part two needs
    the H1 batch and is not claimed here.
  - **H-mono-X — CONFIRMED on the X1 half.** Adding a seventh, different-family bank is worth
    **+7.74 [+5.45, +10.21]** on X1 and does not break the six-condition grid (`mono_allX` was
    within the band there).
  - **H-X1-proxy — NEW, CONFIRMED.** X1 reproduces H1's difficulty ordering and *level* across
    every arm measured on both.
- **Results — X1 column:**

  | system | X1 | |
  |---|---|---|
  | base | 0.1194 | |
  | formatonly | 0.1252 | |
  | mono_all | 0.2323 | |
  | tuned_L0 | 0.2702 | clean-code control |
  | tuned_S1 | 0.2718 | |
  | tuned_S2 | 0.2858 | best *transfer* arm |
  | **mono_allX** | **0.3097** | |
  | **tuned_X1** | **0.3188** | own-condition diagonal |

  | contrast | Δ pts [95 % CI] |
  |---|---|
  | `tuned_X1 − tuned_L0` | **+4.86 [+2.80, +6.92]** |
  | `tuned_X1 − tuned_S2` | **+3.29 [+1.23, +5.52]** |
  | `mono_allX − mono_all` | **+7.74 [+5.45, +10.21]** |
  | `mono_allX − tuned_S2` | +2.39 [−0.08, +5.11] |
  | `mono_allX − tuned_X1` | −0.91 [−2.96, +1.15] |
  | `tuned_S2 − tuned_L0` | +1.57 [−0.08, +3.21] |

  Two things worth naming. First, **the breadth-vs-specialist tie appears again**, now on a
  seventh condition the ladder was not built around: `mono_allX − tuned_X1` = −0.91 [−2.96,
  +1.15]. Second, `tuned_S2` leads the transfer arms on X1 (+1.57 over `tuned_L0`), the same
  ordering it holds on H1 — the structural specialist is the best transfer arm to *both*
  held-out families.
- **The finding: X1 is a trainable stand-in for H1.** On the six arms measured on both columns —
  same 405 programs, same 1,214 items — the correspondence is near-exact:

  | arm | X1 | H1 (spent pilot) |
  |---|---|---|
  | tuned_S2 | 0.2858 | 0.2834 |
  | tuned_S1 | 0.2718 | 0.2776 |
  | tuned_L0 | 0.2702 | 0.2735 |
  | mono_all | 0.2323 | 0.2323 |
  | formatonly | 0.1252 | 0.1334 |
  | base | 0.1194 | 0.1285 |

  **Pearson r = 0.9992, Spearman ρ = 1.000, mean |Δ| = 0.48 pts** (mean signed −0.40, i.e. X1 is
  a hair harder). X1 was constructed to be H1's trainable sibling — different MBA identities,
  different string-encoding key, none of `h1_marker_patterns` — and it reproduces H1's *level*,
  not merely its ordering, on every arm that has never seen either.

  This matters beyond the hypothesis. The project's H1 budget is two reads and one is spent, so
  every design decision about the held-out obfuscator has had to be made blind. **X1 gives a
  legitimate development surface for held-out-family work** — it can be trained on, tuned on and
  iterated against without spending anything, and its numbers land within half a point of the
  quarantined column. That is a methodological contribution the quarantine discipline makes
  possible rather than one it costs.
- **The caveat that keeps this honest.** The correspondence is established *only* on arms trained
  on neither column. `tuned_X1` and `mono_allX` are trained on X1, so their X1 numbers are
  diagonal, not transfer, and **must not** be used to predict their H1 numbers. Whether
  family-specific training carries from X1 to H1 is exactly what the final read is for; if the
  X1 diagonal could stand in for it, there would be no experiment.
- **Consequence for the H1 batch.** The gating worry recorded before this ran — that a weak X1
  diagonal (val 0.264) would make the arm not worth a read — is resolved: the held-out diagonal
  is 0.3188 and beats every transfer arm outside its interval. **The X1 arms have earned their
  place in the single `final_eval` batch.**
- **Provenance:** cells `results/cells/x1_generic/codellama-7b/python/*__X1`; H1 cells
  `results/cells/h1_codellama/codellama-7b/python/*__H1` (pilot, already spent — read-only here);
  adapters `runs/adapters/codellama-7b/python/X1_r32_s17` and `.../mono_allX...`; job 378459
  (three earlier attempts died on infrastructure, see `2026-09-05_verifier-is-a-good-classifier-and-a-bad-selector.md`
  and commit `e824040`).
