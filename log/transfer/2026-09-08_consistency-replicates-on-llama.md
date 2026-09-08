### Target Date: 2026-09-08 (Read — E8: the consistency objective replicates on Llama-3.1-8B; not a CodeLlama artefact)
- **Hypotheses / what we're testing:** E8 rules frozen in `CLAUDE_SCRATCHPAD.md` before the pipeline
  submission. **H-E8**: `cons_lam3 − mono_all` @ X1 ci_lo > 0. **H-E8-seen**: `cons_lam3 − tuned_L0`
  pooled over the five obfuscated seen conditions ci_lo > 0. **H-E8-tax**: `cons_lam3 − tuned_L0` @ X1
  not ci_hi < 0.
- **Setup:** `tr_cons_llama` **382549** (4:00 h; paired consistency λ = 3, parent view, teacher = the
  Llama-3.1-8B `tuned_L0`, r32 s17) → `ck_cons_llama` **382550** → `ev_llama` **382551** (5:36) →
  `an_e8` **382552** (`36_cons_arms --mode e8`, `results/analysis/pipeline/e8_llama.json`). Controls
  `base`/`tuned_L0`/`mono_all` on Llama-3.1-8B are the existing 09-04 cells. n_prog 557 / 405. No H1.
- **Results:**

  | arm (Llama-3.1-8B) | L0 | L1b | L1r | L2 | S1 | S2 | **X1** |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | `base` | 0.2575 | 0.2220 | 0.2425 | 0.2150 | 0.2133 | 0.2052 | 0.1318 |
  | `tuned_L0` | **0.4473** | 0.3637 | 0.3880 | 0.3910 | 0.3970 | 0.4109 | 0.2488 |
  | `mono_all` | 0.4251 | 0.3896 | 0.3862 | 0.3880 | 0.3929 | 0.4091 | 0.2199 |
  | `cons_lam3` | **0.4473** | **0.4065** | **0.4030** | **0.4084** | **0.4122** | **0.4445** | **0.2545** |

  | contrast | Llama-3.1-8B | CodeLlama-7B (for reference) |
  |---|---:|---:|
  | `cons_lam3 − mono_all` @ X1 | **+3.46** [+1.65, +5.35]* | +4.59 [+3.16, +5.99] |
  | `cons_lam3 − mono_all` @ seen | +2.19 [+0.76, +3.61]* | |
  | `cons_lam3 − mono_all` @ L0 | +2.22 [+0.36, +4.07]* | |
  | `cons_lam3 − tuned_L0` @ X1 | +0.58 [−1.07, +2.22] | −0.30 [−1.80, +1.32] |
  | `cons_lam3 − tuned_L0` @ seen (5 obf) | **+2.53** [+1.30, +3.73]* | |
  | `cons_lam3 − tuned_L0` @ L0 | +0.00 [−1.56, +1.56] | |
  | `mono_all − tuned_L0` @ X1 | −2.88 [−4.86, −0.99]* | −3.79 |
  | `mono_all − tuned_L0` @ L0 | −2.22 [−4.07, −0.36]* | −1.74 |
  | `mono_all − tuned_L0` @ seen | +0.34 [−1.10, +1.85] | |

- **What worked / hypothesis verdict:** **H-E8 CONFIRMED** (+3.46*), **H-E8-seen CONFIRMED**
  (+2.53*), **H-E8-tax CONFIRMED** (+0.58, ci_hi > 0). On a second model family the objective does
  what it does on CodeLlama: it beats breadth on the unseen family by ~3.5 pts, beats clean-only on
  the seen obfuscations by ~2.5 pts, and pays nothing on L0 (+0.00 exactly against `tuned_L0`) or
  X1. `cons_lam3` is the best or tied-best arm on all seven columns.
- **Observations:**
  - The breadth fingerprint on Llama is the same as on CodeLlama at every scale: L0 tax −2.22*, X1
    tax −2.88*, seen gain over clean-only not above zero on single transforms (+0.34). With E3, the
    RQ3′ result now holds on four model/scale points (7B×3 seeds, 13B, 34B, Llama-8B) and breadth's
    trade-off holds on all of them.
  - `cons_lam3 − tuned_L0` @ L0 = +0.00 [−1.56, +1.56] is the cleanest "no clean-code tax" reading in
    the campaign.
  - Single seed on Llama. The Llama arms land within ~2 pts of their CodeLlama-7B counterparts
    (`base` X1 0.132 vs 0.119; `tuned_L0` X1 0.249 vs 0.269), so this is a replication at matched
    strength, not a harder or easier setting.
- **New questions / new hypotheses:** none new; E4 (which ingredient) is the remaining 7B leg and
  `an_composite_34b` the remaining scale leg.
- **Next Steps:** RQ_SUMMARY §6 RQ3′ row and §6.1; PAPER_EXPERIMENTS E8 → done.
