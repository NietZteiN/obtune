### Target Date: 2026-09-07 (E5 — the second family pair: H-family-generalises REFUTED as pre-registered, and the reason is that Y2 is not hard enough to test it)

The generality test for the paper's central claim, pre-registered at commit `e2041c0` **before any
Y2 read**. Jobs 381382 (`tr_X2`), 381383 (`ck_X2`), 381494 (`ev_xy2`). No H1 cell was read.

- **Hypotheses / what we're testing:** C2 — "a tuned model acquires the transformation FAMILY it
  was shown, not semantic invariance" — rests entirely on **one** family pair (X1 trainable / H1
  held out, both string-encoding + MBA), and H1's budget is spent so that pair can never be
  extended. X2/Y2 are a second pair in a different family: every value crosses a raise/except
  boundary. X2 raises a `LookupError` and catches it in-frame; **Y2**, the unseen sibling, reads
  `StopIteration.value` off a generator return.
  - **H-family-generalises (primary)** — CONFIRM if `tuned_X2 − tuned_L0` on **Y2** excludes zero
    above; REFUTE if not.
  - **H-family-specific (secondary)** — `tuned_X1 − tuned_L0` on Y2. `tuned_X1` saw a held-out
    family but the *wrong* one. Null there + positive primary ⇒ the effect is family-specific;
    both positive ⇒ generic novelty exposure.

- **Setup:** CodeLlama-7b, Python, LoRA r=32, seed 17. Generator `src/obtune/obf/py/xy2.py`;
  ladder entries in `configs/conditions.yaml`; `Y2` absent from `paths.TRAINABLE_CONDITIONS`.
  Corpus: X2 1683/2231 and Y2 1680/2231 train programs gate (common 1679); heldout eval items
  X2 1245 / Y2 1242. `tuned_X2` trained in 21 min (168 steps, train_loss 0.5170), ckpt-select
  chose epoch 1 (**X2 only** as validation — Y2 never used for selection). Contrasts:
  `bootstrap_delta` clustered by `snippet_id`, n_boot 2000, seed 17, 1,241 items / 414 programs.
  Numbers → `results/analysis/xy2_family_2026-09-07.json`.

- **Results — accuracy:**

  | system | `L0` | `X2` | **`Y2`** | format_fail (Y2) |
  |---|---:|---:|---:|---:|
  | `base` | 0.2569 | 0.1913 | 0.1910 | 0.1330 |
  | `tuned_L0` | **0.4263** | 0.3746 | 0.3884 | 0.0242 |
  | **`tuned_X2`** | 0.4108 | **0.4043** | **0.4005** | 0.0274 |
  | `tuned_X1` | 0.4102 | 0.4011 | 0.3852 | 0.0210 |
  | `mono_all` | 0.4114 | 0.3593 | 0.3755 | 0.0073 |

- **Results — the pre-registered contrasts on Y2:**

  | contrast | Δ pts [95 % CI] | verdict |
  |---|---:|---|
  | **PRIMARY** `tuned_X2 − tuned_L0` | **+1.21 [−0.81, +3.22]** | **REFUTED** — does not exclude zero |
  | SECONDARY `tuned_X1 − tuned_L0` | −0.32 [−2.42, +1.69] | null — no generic novelty effect either |
  | `tuned_X2 − tuned_X1` | +1.53 [−0.40, +3.38] | null |
  | `mono_all − tuned_L0` | −1.29 [−3.62, +0.89] | right direction for C1, but not separable |

  **The arm is not dead:** the X2 diagonal `tuned_X2 − tuned_L0` on X2 is **+2.97 [+1.04, +5.06]**,
  so the surface *is* learnable and the specialist *did* learn it. The `L0` tax is
  −1.56 [−3.17, +0.06], the familiar specialist shape.

- **Why it came out null, measured rather than argued.** Y2 is a far easier transform than H1/X1,
  and there is almost no room for family exposure to help:

  | held-out family | `tuned_L0` on `L0` → on the family | drop | headroom the family specialist won |
  |---|---|---:|---:|
  | X1 (encoding + MBA) | 0.4281 → **0.2702** | **−15.8 pts** | `tuned_X1` **+4.9 pts** |
  | Y2 (exception routing) | 0.4263 → **0.3884** | **−3.8 pts** | `tuned_X2` **+1.2 pts** |

  The encoding family costs a clean-code adapter 15.8 points; exception routing costs it 3.8. The
  observed effect sizes are close to proportional to the damage (4.9 / 15.8 ≈ 0.31 vs 1.2 / 3.8 ≈
  0.32), which is what a "family exposure recovers about a third of the family's damage" reading
  would predict — but with only 3.8 points of damage to recover from, that third is 1.2 points and
  the interval cannot resolve it. **Y2 is not a discriminator.** X2/Y2 route values through
  exception machinery without obscuring identifiers, control flow, string contents or arithmetic,
  so the code stays readable; H1/X1 destroy the surface of every literal and every operator.

- **What worked / hypothesis verdict:** **H-family-generalises REFUTED**, on the rule as written,
  and it is recorded as refuted. What it licenses is narrower than "the family claim is wrong":
  the experiment had ~1.2 points of available signal against a ±2-point interval, so it was
  **underpowered by construction** — a fact that is visible only now the difficulty was measured,
  and that I did not anticipate when choosing the family. The claim C2 can now make is unchanged in
  strength but explicitly narrower in scope: *for a family that badly damages a clean-code adapter,
  training on a sibling surface recovers a substantial share of the damage (X1→H1)*. Whether that
  generalises to other **hard** families is still open, and E5 as run does not answer it.

  I am **not** re-specifying the rule, re-running with a different bar, or reporting the +1.21 as a
  trend. The pre-registration exists precisely for the case where the result is inconvenient.

- **Observations:**
  - Five infrastructure bugs surfaced building this, four of them silent. The worst: a new
    condition must be registered in **four** places — `TRANSFORM_REGISTRY`, `conditions.yaml`,
    `schema.Condition` and (for a new eval phase) `schema.TrialRow.phase` — and a missing
    `Condition` entry makes `builder` report every program as "declined", i.e. a 0/2231 build with
    no error anywhere. A test asserting those four agree would have caught it in seconds.
  - The exec sandbox (`src/obtune/exec/runner_py.py`) builds child globals from `dir(builtins)`
    filtered on `not startswith("_")` plus `__import__`, so **`__build_class__` is absent and any
    class-defining program fails with `NameError`**. That silently excludes class-defining programs
    from every condition in this project, not just X2. Not fixed here: changing it would change
    what the corpus admits for already-published conditions. Worth a decision.
  - `mono_all` again has the lowest format-fail of any tuned system (0.0073) and the lowest
    accuracy among them on the held-out column — the §20 pattern, a third time.

- **Next steps:** if C2's generality is still wanted, it needs a **hard** second family — one that
  costs a clean-code adapter ≳10 points, i.e. that destroys surface information rather than
  rerouting control flow. Candidates: numeric-base re-encoding of all literals with computed
  reconstruction, or identifier-to-computed-attribute indirection. That is a new experiment with a
  new pre-registration, and its power should be estimated **from the difficulty of the held-out
  sibling** before any adapter is trained — the check E5 skipped.
