### Target Date: 2026-09-05 (Llama-3.1-8B probe: no promotion, but the breadth fingerprint replicates across model families)

Reduced `base`/`tuned_L0`/`mono_all` probe on Llama-3.1-8B-Instruct over the six-condition
trainable heldout grid (`ev_ll8` 377850), against CodeLlama-7b **item-for-item** on the same
9,582 items / 557 programs. **H1 is not read**; `final_eval` stays unspent. Intervals are
2,000-resample bootstraps clustered by `program_id`. Pre-registration and the NO-GO gate read
are in [`2026-09-05_x1-family-arm-and-llama31-gate.md`](2026-09-05_x1-family-arm-and-llama31-gate.md).

- **Hypotheses:**
  - **H-llama31 — NOT PROMOTED (the threshold passes, the paired interval does not).** The
    pre-registered rule was: promote to the full 8-adapter grid only if `tuned_L0(llama31-8b)`
    beats CodeLlama-7b's 0.430 outside the seed band. On `L0` it posts **0.447**, which clears
    0.430 by 1.7 pts against a ~0.1-pt seed band (s17 0.4299 / s42 0.4311) — a literal pass.
    But the *paired* contrast on the identical items is **+1.80 [−0.42, +4.07]** on `L0` and
    **+1.21 [−0.29, +2.64]** pooled: both cover zero. The threshold was written before we had
    paired intervals for cross-model contrasts, and it is the weaker instrument; reporting the
    literal pass as a win would be exactly the error [`2026-09-03_cis-and-three-corrections.md`](2026-09-03_cis-and-three-corrections.md)
    was written about. **Recorded as: no reliable difference, no promotion.**
  - **H-breadth-fingerprint-crossfamily — NEW, CONFIRMED here.** The `mono_all` = `tuned_L0`
    tie *and* its per-condition shape reproduce on a different base-model family.
- **The reason not to promote is stronger than the interval.** The whole Llama advantage is
  inherited from the base model, not produced by tuning:

  | contrast (pooled, paired) | Δ pts [95 % CI] |
  |---|---|
  | `base(llama31)` − `base(CL7b)` | **+2.08 [+0.19, +3.92]** |
  | `tuned_L0(llama31)` − `tuned_L0(CL7b)` | +1.21 [−0.29, +2.64] |
  | `mono_all(llama31)` − `mono_all(CL7b)` | +0.80 [−1.00, +2.57] |
  | tuning gap `tuned_L0 − base`, llama31 | **+17.18 [+15.23, +19.13]** |
  | tuning gap `tuned_L0 − base`, CL7b | **+18.04 [+16.04, +20.09]** |

  Llama-3.1-8B starts ~2 pts ahead and ends ~1 pt ahead: the two tuning gaps are
  indistinguishable, and if anything the newer base *converts* tuning slightly less well. A
  better base model is not a lever on this task — swapping it moves the whole ladder up by its
  own head start and changes nothing about what fine-tuning teaches. This is the cleanest
  statement yet that the campaign's findings are about the training signal, not the checkpoint.
- **The replication — same fingerprint, different family.** Per condition on Llama-3.1-8B,
  `mono_all − tuned_L0`:

  | cond | `base` | `tuned_L0` | `mono_all` | `mono_all − tuned_L0` [95 % CI] |
  |---|---|---|---|---|
  | L0 | 0.258 | 0.447 | 0.425 | **−2.22 [−4.13, −0.24]** |
  | L1b | 0.222 | 0.361 | 0.390 | **+2.83 [+0.90, +4.76]** |
  | L1r | 0.242 | 0.387 | 0.387 | +0.06 [−1.80, +1.86] |
  | L2 | 0.215 | 0.387 | 0.389 | +0.18 [−1.68, +2.15] |
  | S1 | 0.213 | 0.397 | 0.393 | −0.40 [−2.97, +2.25] |
  | S2 | 0.205 | 0.409 | 0.413 | +0.36 [−1.68, +2.46] |

  Pooled **+0.16 [−1.26, +1.61]** — the tie. And the two intervals that exclude zero are
  exactly the two that do so on CodeLlama: **an `L0` cost and an `L1b` gain**, same signs,
  comparable sizes. Six breadth adapters on CodeLlama shared one fingerprint
  ([`2026-09-04_accuracy-campaign-closes.md`](2026-09-04_accuracy-campaign-closes.md)); a
  seventh adapter on a different pretraining corpus, tokenizer and instruct-tuning recipe
  produces it again. Breadth training buys `L1b` and charges `L0` as a property of the
  *condition ladder*, not of CodeLlama.
- **What did not happen:** no H1 read, no full grid, no selection on anything but val
  (`ck_ll8_L0` best ckpt-74 at 0.435, `ck_ll8_mono` best ckpt-1260 at 0.388).
- **Next:** Llama-3.1-8B is closed as a probe. The cross-family fingerprint replication belongs
  in the RQ2 write-up as a robustness row, not as a new arm.
- **Provenance:** cells `results/cells/rq2_generic/llama31-8b/python/{base,tuned_L0,mono_all}__*`;
  adapters `runs/adapters/llama31-8b/python/{L0,L0-L1b-L1r-L2-S1-S2}_r32_s17`
  (`train_loss` 0.492 / 0.141; truncation 18/26,841 at `max_seq_len` 2048); jobs 377846–377850.
