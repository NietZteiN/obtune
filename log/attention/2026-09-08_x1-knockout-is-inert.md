### Target Date: 2026-09-08 (E9 — identifier knockout on X1 across five arms: both hypotheses refuted, and the instrument has no leverage)
- **Hypotheses / what we're testing:** RQ4′ support, pre-registered 2026-09-07 (`CLAUDE_SCRATCHPAD.md`
  "RQ4′ — mechanism and support", frozen in `0286c5f` before submission). Δ = log P(gold | identifier
  keys knocked out) − log P(gold | clean), per item, paired across arms, program-cluster bootstrap.
  **H-attn-cons**: `cons_lam3` depends *less* on identifier keys than `mono_all` on the unseen family —
  CONFIRMED iff mean(Δ_cons − Δ_mono) ci_lo > 0. **H-attn-breadth**: breadth makes the model *more*
  identifier-dependent on X1 — CONFIRMED iff mean(Δ_mono − Δ_L0) ci_hi < 0. **H-attn-order**: Spearman
  between per-arm damage and per-arm X1 accuracy, descriptive (n = 5).
- **Setup:** `ko_x1_{base,tuned_L0,mono_all,cons_lam3,tuned_X1}` jobs **382553–382557** (h200, 78–106 s
  each), `scripts/attn/30_knockout.py --mode score --classes identifier --condition X1 --max-items 150`
  (150 stratified X1 items, 50 programs, layers 4/10/16/21/25/30, 44.5 identifier keys knocked per item)
  → `results/attn/knockout/codellama-7b/X1/<arm>.json`; `an_attention` **382558** (`41_attention_x1.py`)
  → `results/analysis/pipeline/attention_x1_codellama7b.json`. Adapters: the s17 `best` checkpoints
  used everywhere else. No H1.
- **Results:**
  | arm | mean log P(gold) clean | mean Δ (knockout − clean) | median Δ |
  |---|---:|---:|---:|
  | base | −16.72 | +0.028 | +0.019 |
  | tuned_L0 | −6.26 | −0.029 | −0.006 |
  | mono_all | −11.42 | −0.010 | −0.000 |
  | cons_lam3 | −6.36 | −0.010 | −0.002 |
  | tuned_X1 | −5.96 | +0.008 | +0.001 |

  Paired contrasts (nats): `cons_lam3 − mono_all` **−0.0001** [−0.097, +0.102]; `mono_all − tuned_L0`
  **+0.019** [−0.088, +0.126]; `cons_lam3 − tuned_L0` +0.019 [−0.021, +0.062]; `tuned_X1 − tuned_L0`
  +0.037 [−0.007, +0.082]; `tuned_L0 − base` −0.057 [−0.142, +0.016]. Spearman(damage, X1 acc) = −0.3
  over five arms.
- **What worked / hypothesis verdict:** **H-attn-cons REFUTED** (point −0.0001, interval straddles
  zero by ±0.1) and **H-attn-breadth REFUTED** (+0.019, ci_hi +0.126 > 0), exactly as the rules were
  written. H-attn-order REPORTED: −0.3 on n = 5 is noise.
- **Observations:**
  1. **The knockout is inert, not merely null.** Removing every identifier key from six layers moves
     the gold log-probability by at most 0.06 nats on totals of −6 to −17 — under 0.5 % — for every
     arm. This is not specific to X1: the seen-condition knockouts on file show the same
     (`L1b` −0.001/−0.009, `S1` +0.023/+0.005, `S2` +0.161/+0.017 for base/specialist). Whatever
     the RQ3 attention *correlation* on seen conditions was tracking, removing identifier-keyed
     attention in score mode does not carry the gold answer. So the two refutations say "no
     detectable difference on an instrument with no dynamic range", and the paper must not read
     them as "the arms are equally identifier-dependent". Causal support for RQ4′ from this
     instrument is **absent**, and E9 is closed as such.
  2. **The unplanned number is the clean likelihood column.** On X1 gold answers, `mono_all`
     assigns mean log P = −11.42 where `tuned_L0` gives −6.26, `cons_lam3` −6.36 and `tuned_X1` −5.96.
     Breadth's unseen-family tax (−3.79 pts accuracy) is a five-nat likelihood gap against the
     clean-code control on the same 150 items, and consistency closes it entirely. Not
     pre-registered, no verdict attached; it is the strongest mechanistic descriptor this stage
     produced and is worth a paired bootstrap of its own before anything is claimed.
  3. Positive Δ for `base` (+0.028): knocking identifier keys *helps* the untuned model slightly,
     consistent with base attending to misleading surface tokens — but see (1) for the scale.
- **New questions / new hypotheses:** H-lik-gap (not registered): the paired clean log-likelihood gap
  `mono_all − tuned_L0` on X1 gold is negative with ci_hi < 0 and `cons_lam3 − tuned_L0` is
  equivalent at ±0.5 nats. A generate-mode or ablation-strength sweep would be needed before the
  knockout instrument can say anything about RQ4′; not scheduled.
- **Next Steps:** RQ_SUMMARY §6 RQ4′ row updated to "refuted, instrument inert"; the writeup carries
  RQ4′ as correlational support only.
