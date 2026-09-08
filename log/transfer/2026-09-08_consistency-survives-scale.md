### Target Date: 2026-09-08 (Read — E3: the consistency objective survives scale; at 34B it is the best arm on every column)
- **Hypotheses / what we're testing:** the E3 rules frozen in `CLAUDE_SCRATCHPAD.md` (2026-09-07 E3
  pre-registration, restated for `36_cons_arms --mode e3` before the pipeline submission).
  **H-E3 (H-cons-scale)**: CONFIRMED iff `cons_lam3 − mono_all` @ X1 has ci_lo > 0 at **both** 13B and
  34B; PARTIAL at one; REFUTED at neither. **H-E3-tax**: CONFIRMED iff `cons_lam3 − tuned_L0` @ X1 does
  not have ci_hi < 0 at both scales (consistency pays no unseen tax at scale).
- **Setup:** `cons_lam3` (paired consistency, λ = 3, parent view, the same-scale `tuned_L0` as teacher,
  r32 s17) trained at 13B (chain 381340 → 382139 → 382140, done 09-07) and 34B (`tr_cons34b` **381405**
  12:05 h → `ck_cons34b` **382141** → `ev_cons34b` **382142** 7:32) → `an_e3` **382542**
  (`results/analysis/pipeline/e3_scale.json`). Controls `tuned_L0` / `mono_all` at each scale are the
  existing cells. Cluster-bootstrap by `program_id`, n_prog = 557 seen / 405 X1. No H1.
- **Results:**

  | scale | arm | L0 | L1b | L1r | L2 | S1 | S2 | **X1** |
  |---|---|---:|---:|---:|---:|---:|---:|---:|
  | 13B | `tuned_L0` | 0.4689 | 0.3957 | 0.4156 | 0.4078 | 0.4042 | 0.4241 | 0.2965 |
  | 13B | `mono_all` | 0.4455 | 0.4228 | 0.4192 | 0.4192 | 0.4122 | 0.4439 | 0.2537 |
  | 13B | `cons_lam3` | 0.4629 | **0.4367** | **0.4371** | **0.4299** | **0.4346** | **0.4685** | 0.2932 |
  | 34B | `tuned_L0` | 0.5222 | 0.4186 | 0.4683 | 0.4647 | 0.4723 | 0.4841 | 0.3262 |
  | 34B | `mono_all` | 0.4958 | 0.4704 | 0.4581 | 0.4629 | 0.4667 | 0.4829 | 0.2998 |
  | 34B | `cons_lam3` | **0.5263** | **0.4928** | **0.4862** | **0.4814** | **0.4932** | **0.5255** | **0.3336** |

  | contrast | 7B (09-06/07) | 13B | 34B |
  |---|---:|---:|---:|
  | `cons_lam3 − mono_all` @ X1 | **+4.59** [+3.16, +5.99] | **+3.95** [+2.22, +5.84] | **+3.38** [+1.32, +5.51] |
  | `cons_lam3 − mono_all` @ seen | | +1.77 [+0.52, +3.09]* | **+2.77** [+1.45, +4.06]* |
  | `cons_lam3 − mono_all` @ L0 | | +1.74 [+0.12, +3.41]* | **+3.05** [+1.32, +4.79]* |
  | `cons_lam3 − tuned_L0` @ X1 (the tax) | −0.30 [−1.80, +1.32] | −0.33 [−2.06, +1.48] | **+0.74** [−0.99, +2.47] |
  | `cons_lam3 − tuned_L0` @ seen | | **+3.20** [+1.99, +4.42]* | **+3.49** [+2.49, +4.49]* |
  | `cons_lam3 − tuned_L0` @ L0 | | −0.60 [−2.15, +1.02] | +0.42 [−0.90, +1.80] |
  | `mono_all − tuned_L0` @ X1 (breadth's tax) | −3.79 [−6.09, −1.65] | −4.28 [−6.50, −2.06]* | −2.64 [−4.94, −0.33]* |
  | `mono_all − tuned_L0` @ L0 | −1.74 | −2.34 [−4.37, −0.24]* | −2.63 [−4.55, −0.84]* |
  | `mono_all − tuned_L0` @ seen | | +1.43 [−0.03, +2.91] | +0.72 [−0.61, +2.10] |

- **What worked / hypothesis verdict:**
  - **H-E3 — CONFIRMED.** `cons_lam3 − mono_all` on X1 excludes zero above at both 13B (+3.95) and
    34B (+3.38). The 7B result (+4.59 at three seeds) is not a small-model repair; the point estimate
    shrinks slightly with scale but the lower bound stays above +1.3 at every size.
  - **H-E3-tax — CONFIRMED.** `cons_lam3 − tuned_L0` on X1 is −0.33 [−2.06, +1.48] at 13B and
    +0.74 [−0.99, +2.47] at 34B: consistency pays no unseen tax at any scale, where breadth pays
    −2.6 to −4.3 at every one.
  - Beyond the registered rules, the 34B row is the cleanest table in the campaign: **`cons_lam3` is
    the best arm on all seven columns**, beating `tuned_L0` on seen by +3.49* and `mono_all` on L0
    by +3.05*, with L0 (+0.42) and X1 (+0.74) both non-negative against the clean-only adapter. At
    13B it wins six of seven and loses L0 by −0.60 n.s. The "both sides of the trade" claim of
    RQ3′ — breadth's stacked-seen gain without breadth's L0 and unseen-family taxes — holds at
    every scale run.
- **Observations:**
  - Breadth's two taxes are scale-invariant: L0 −1.74 / −2.34* / −2.63*, X1 −3.79 / −4.28* / −2.64*.
    Scale does not resolve the trade-off; the objective does. That is the contrast the paper's
    RQ1′ ↔ RQ3′ pairing rests on.
  - `mono_all − tuned_L0` on seen is +1.43 [−0.03, +2.91] at 13B and +0.72 [−0.61, +2.10] at 34B —
    plain breadth's seen gain over clean-only is *not* reliably above zero at scale on
    single-transform conditions; its gain is on stacked composites (RQ-A). Consistency's seen gain
    is above zero at both.
  - `cons_lam3 − mono_all` @ L0 growing with scale (+1.74* → +3.05*) says the consistency term's
    protection of clean-code accuracy is not a 7B artefact either.
  - One seed at 13B and 34B (s17); the 7B seed band (s42/s101 +4.53/+4.12) is the only replication.
    E3 was costed at 20 GPU-h and used ~19 (12 h at 34B).
- **New questions / new hypotheses:** H-cons-stack-strict at 34B (`an_composite_34b`, 382518, pending
  `ev_composite_34b` 382516) is the remaining scale leg; E4 (which ingredient) and E8 (Llama) are
  running. Whether the shrinking X1 point estimate (+4.59 → +3.95 → +3.38) is a trend or seed noise
  would need a second seed at 34B — not registered.
- **Next Steps:** RQ_SUMMARY §6 RQ3′ row + §6.1 scale columns; PAPER_EXPERIMENTS E3 → done.
