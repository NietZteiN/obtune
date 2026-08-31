### Target Date: 2026-08-30 (The format floor: H-format refuted at 7B, supported at 1.5B, and a control that faked the answer)

> Follows [`2026-08-30_7b-rq1-matrix.md`](2026-08-30_7b-rq1-matrix.md), which opened **H-format**
> as the threat to that result and gated its interpretation on this run.

- **Hypotheses / what we're testing:** **H-format — most of the fine-tuning gain is
  output-format competence, not invariance.** CONFIRM if a label-shuffled adapter (which
  cannot learn the input→output mapping) recovers most of `tuned_L0`'s gain over `base`.
  REFUTE if it recovers little. If confirmed, the matrix's diagonal and off-diagonal both sit
  on a shared non-task floor and `TR = 0.885` measures that floor rather than invariance.

- **Setup:** `train.shuffle_labels` permutes gold answers across the selected training rows
  (`data.py:479`), leaving code, prompts, answer multiset and row count intact. New configs:
  `formatonly_{lr2e5,ep1}_qwen1.5b_py.yaml`, `formatonly_{lr2e5,lr50e6,lr20e6}_qwen7b_py.yaml`;
  eval via `configs/eval/formatonly_fix_qwen1.5b.yaml` (new `phase: formatonly_fix`) and
  `formatonly*` systems added to `configs/eval/grid_rq1_7b.yaml` so the floor is scored on the
  SAME items, phase and engine as the matrix it reinterprets. Jobs 359380-359541.
  Common subset 412 programs. **H1 not read.**

- **Results:**
  - **The pre-existing arm was never usable.** `formatonly` (lr 1.0e-4) at 1.5B: acc 0.081,
    **format_fail 0.505**. Its own eval config pre-registered that as degenerate and
    uninformative. So the project's format floor has been **unmeasured**, and every
    "fine-tuning helps" number is still reported against `base`.
  - **1.5B — H-format SUPPORTED.** `formatonly_lr2e5` (lr 2.0e-5, 3 epochs) is a valid
    control: format_fail 0.041-0.059 against real adapters' 0.019-0.026, 808 distinct outputs
    of 1670, top output 9.7 %. It recovers **67.4 / 62.1 / 65.8 %** of `tuned_L0`'s gain over
    base on L0 / L1r / S2 — and **~62 % even among items where BOTH systems are format-clean**
    (L0: base .274 → formatonly .393 → tuned_L0 .467). So it is not merely format repair.
  - **7B — H-format REFUTED.** Valid control `formatonly_lr20e6` (lr 2.0e-6): format_fail
    **0.013** (better than the real specialists) with 902 distinct outputs, top share 0.070.
    Floor share of the diagonal gain per condition: **13.7, 1.9, 8.5, 5.3, −60.1, 13.6 %**.

    | reference | diagonal | off-diagonal | diff | mean off-diag TR |
    |---|---|---|---|---|
    | vs `base` | +0.1696 | +0.1496 | +0.0200 | **0.8842** |
    | vs **FLOOR** | +0.1708 | +0.1508 | +0.0200 | **0.8810** |

    Correcting for the floor moves TR by **0.003**.

- **What worked / hypothesis verdict:** **H-format REFUTED at 7B, SUPPORTED at 1.5B.** The
  threat to `2026-08-30_7b-rq1-matrix.md` is disposed of: `TR = 0.885` is not a shared floor
  effect, and the 7B RQ1 result stands as reported.

- **Observations:**
  - **A collapsed control faked the target signature, and the arm's decision rule could not
    catch it.** The first 7B attempt (lr 2.0e-5) read acc 0.001 / format_fail 0.013 — exactly
    the rule's CONFIRM-the-floor-is-zero pattern. It was **mode collapse**: 16 distinct outputs
    across 1670 items, **91 % the single string `"1234567890"`**. Well-formed and always wrong
    produces the same two numbers as "learned format, cannot do task". The pre-registered rule
    reads only `format_fail` and accuracy, so it cannot separate them. **Output diversity is the
    missing diagnostic** and is now an explicit acceptance criterion in the new configs
    (hundreds of distinct outputs, most-common share well under 0.25, WITH low format_fail).
    Had this not been checked, the entry would have reported a zero floor and a vindicated
    matrix on the strength of an artifact — the right conclusion for the wrong reason.
  - **There is no single "format floor"; it is a function of how far the control is trained.**
    The three 7B variants give 0.001 (collapsed), 0.332 and 0.429 on L0 by learning rate alone.
    More training on shuffled labels actively destroys task ability. `lr20e6` is used as the
    floor because it has the best format acquisition while staying diverse, which is the arm's
    stated purpose; `lr50e6` would give a HIGHER estimate of real task learning, so this choice
    is the conservative one.
  - **The scale difference is bigger news than either verdict.** Base format_fail is nearly
    identical at the two scales (0.179 at 7B, 0.192 at 1.5B), yet repairing it is worth ~2-14 %
    of the gain at 7B and 62-67 % at 1.5B. That implies the items a 1.5B model format-fails are
    ones it would otherwise get RIGHT, while a 7B model's format failures land on items it would
    get wrong anyway. **Every 1.5B headline in this project is therefore reported against the
    wrong reference** — `base` overstates the gain by roughly two thirds — while the 7B numbers
    are close to floor-corrected already.
  - **On `S1` the floor is BELOW base** (0.285 vs 0.371, share −60 %): shuffled-label training
    actively damages structural-condition performance rather than merely failing to help.
  - **Degenerate adapters are not reproducible across the migration; healthy ones are.**
    Re-running the same adapters on juno: `tuned_L0` acc −0.0012 and `base` +0.0006 (3-4 % of
    generations differing), against `formatonly_orig` at **+0.081 acc, −0.495 format_fail, 52 %
    of generations differing**. Published numbers are safe. A degenerate arm sits on a knife
    edge where routine nondeterminism flips half its outputs, so its metrics cannot be compared
    across runs at all — an independent reason not to build on that recipe.

- **New questions / new hypotheses:** **H-scale-floor — the format floor shrinks with model
  scale because format failures migrate onto items the model cannot solve anyway.** Testable
  directly: partition items by whether `base` format-fails, and compare `base` accuracy on the
  two partitions at each scale.

- **Next Steps:** (1) Re-report the 1.5B headlines against the format floor rather than `base`
  — on present evidence this is a real correction, not a footnote. (2) Add output diversity to
  the shuffled-label arm's acceptance criteria wherever it is documented. (3) The 7B matrix is
  now interpretable and H1 remains unspent; that read is defensible when wanted.
