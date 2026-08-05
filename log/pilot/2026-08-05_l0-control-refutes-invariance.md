### Target Date: 2026-08-05 (L0 control — the pilot's H1 gain is task acquisition)

*Follows and corrects the reading in [`2026-08-05_kill-switch-pilot.md`](2026-08-05_kill-switch-pilot.md).
The numbers in that entry stand; the interpretation of its H1 result does not.*

- **Hypotheses / what we're testing:** The earlier entry flagged that the L1b adapter's +27.3 pt
  gain on the held-out obfuscator H1 was ambiguous, because clean L0 code rose by as much
  (+29.3) — the signature of learning the *task* rather than obfuscation robustness. The
  control this predicts:
  - **H-ctl:** an adapter trained only on **clean L0 code** should lift H1 *much less* than the
    L1b-trained adapter, if the L1b gain reflects obfuscation invariance.
    CONFIRM invariance if `acc_H1(tuned_L1b) − acc_H1(tuned_L0)` > 0 with CI excluding 0.
    REFUTE if that difference is ≈0 or negative — the H1 gain would then be task acquisition,
    available from clean code alone.

- **Setup:** identical recipe to the L1b run, only the training condition changed.
  - Config `configs/train/pilot_qwen1.5b_l0.yaml` (`_extends: _base_lora.yaml`,
    `train_conditions: [L0]`), Qwen2.5-Coder-1.5B, LoRA r=32 α=64, 3 epochs, seed 17,
    300 steps, train_loss 0.4162.
  - Checkpoint selection on the held-in L0 val slice: ckpt-100 0.408, **ckpt-200 0.441**,
    ckpt-300 0.432, final 0.432 → `best -> checkpoint-200` (epoch 2 again).
  - Eval `configs/eval/pilot_l0_control.yaml`, same 7 conditions, same items.
  - GPU 2, sharing the card with another user's job via `OBTUNE_GPU_MEM_UTIL=0.28`
    (new escape hatch — the configured 0.90 assumes an idle GPU and vLLM refuses to start
    rather than shrinking).
  - Analysis on the 23-program common subset, 3,465 trials, cluster bootstrap over
    `program_id`, 4,000 resamples, seed 17. Commit `4927d65`.

- **Results:** accuracy on the common subset —

  | system | L0 | L1b | L1r | L2 | S1 | S2 | H1 |
  |---|---|---|---|---|---|---|---|
  | base | .253 | .242 | .202 | .202 | .323 | .212 | .111 |
  | tuned on L1b | .545 | .515 | .576 | .535 | .475 | .495 | **.384** |
  | **tuned on L0 (control)** | .485 | .354 | .495 | .535 | .434 | .455 | **.414** |

  Gain on H1 versus the untuned base: L1b-trained **+27.3** pts CI [+15.2, +41.1];
  L0-trained **+30.3** pts CI [+16.5, +45.8]. The control is *higher*.

  Condition-specific benefit of training on L1b over the clean-code control
  (`acc(tuned_L1b) − acc(tuned_L0)`):

  | eval cond | Δ pts | CI95 | excludes 0 |
  |---|---|---|---|
  | **L1b** (trained) | **+16.2** | [+4.7, +28.5] | **yes** |
  | L1r (same family) | +8.1 | [−1.0, +18.4] | no |
  | L2 | +0.0 | [−8.4, +8.1] | no |
  | S1 | +4.0 | [−1.2, +10.1] | no |
  | S2 | +4.0 | [−4.4, +12.6] | no |
  | **H1** (held out) | **−3.0** | [−10.5, +3.9] | no |

- **What worked / hypothesis verdict:**
  - **H-ctl — REFUTED, and with it H1c as originally stated.** Training on clean code reaches
    the held-out obfuscator at least as well as training on adversarially-renamed code
    (.414 vs .384; difference −3.0 pts, CI spanning zero). The +27.3 pt H1 gain reported
    yesterday is **task acquisition** — learning output prediction and its answer format —
    not semantic invariance. I called that result "provisionally supported" with this exact
    caveat; the control settles it against invariance.
  - **What survives is a memorization gradient.** The obfuscation-specific benefit is
    significant only on the trained condition itself (**+16.2 pts on L1b**), positive but not
    significant on its nearest family member (L1r +8.1), and indistinguishable from zero on
    L2, S1, S2 and H1 — with the held-out condition's point estimate *negative*. Concentrated
    on what was trained, absent on what was held out: that is the profile H1c was designed to
    detect as **transform memorization**.
  - **H1a (family structure) still holds, and now more cleanly.** Measured against the control
    rather than the base, the ordering is trained (+16.2) > same-family (+8.1) > other-family
    (+0.0 to +4.0) ≥ held-out (−3.0).

- **Observations:**
  - **The design's Invariance Index was confounded and is now fixed.** Raw Δ-vs-base cannot
    separate invariance from task acquisition when the base model is weak at the task — and at
    L0 accuracy .253, this one is. The index is redefined relative to the clean-code control
    (design doc §5.1, deviation §9.9), and an L0 control adapter becomes a **required** cell of
    every model × language block rather than an optional ablation. Had the pilot not run it,
    the whole 54-run grid would have produced a headline number measuring the wrong thing.
  - Note what the control did *not* wipe out: on L1b itself the trained adapter beats the
    control by 16.2 pts with a CI excluding zero. Obfuscation-specific learning is real; it
    just does not generalize past the family it was trained on.
  - L2 is the sharpest null (+0.0, CI [−8.4, +8.1]). Sequential minification appears to be
    learnable entirely from clean code — plausible, since `a`, `b`, `c` carry no misleading
    semantics, only absent ones. That makes L1b-vs-L2 a cleaner "misleading vs uninformative
    names" contrast than anticipated, worth stating explicitly in the paper.
  - The pilot's `cond_recovery` (0.26–0.33) should be re-read in this light: prompt-only
    conditioning recovers a third of a gain that is itself mostly task acquisition.

- **New questions / new hypotheses:**
  - **H1c-revised:** no training condition produces a control-relative gain on H1 whose CI
    excludes zero. The full grid tests this across all six conditions; S1/S2-trained adapters
    are the most likely to break it, since H1's MBA rewriting is arithmetic-structural rather
    than identifier-level.
  - Does the +16.2 pt L1b-specific effect grow with training data, or is it already saturated?
    The deferred 8k-vs-24k scaling arm now has a sharper target than overall accuracy.
  - Is the L1r +8.1 (CI [−1.0, +18.4]) real? At n=23 programs this is exactly the effect size
    the pilot cannot resolve; it is the cheapest thing to settle with more test programs.
  - Should the control be L0-trained or *base-with-format-demo*? The control still shares the
    output format with the treatment, which is right for isolating obfuscation-specific
    learning, but a format-only control would separate "learned the task" from "learned to
    format" as well.

- **Next Steps:**
  1. Report the control-relative index everywhere; never cite raw Δ-vs-base as invariance.
  2. Add the L0 control to the grid manifest as a required cell per model × language.
  3. Expand the test set beyond 23 common-subset programs before trusting any effect near
     ±8 pts — this is now the binding constraint on every secondary claim.
  4. Re-run the deferred seed-42 and 8k arms against the control-relative metric.
