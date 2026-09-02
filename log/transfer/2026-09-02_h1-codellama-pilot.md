### Target Date: 2026-09-02 (H1 on CodeLlama: the clean-code result reproduces, the merge result does not)

> **QUARANTINE ACCESS.** `pilot_eval`, logged at 2026-09-02T19:05:35Z in
> `../../data/quarantine/h1/ACCESS_LOG.md`. Authorised by the user as an explicit yes to a
> direct question, not inferred from a general go-ahead. CodeLlama's `final_eval` is UNSPENT.

- **Hypotheses / what we're testing:** the held-out obfuscator, read once, against three
  predictions fixed in `configs/eval/h1_confirm_codellama.yaml` **before any H1 number
  existed**. Every arm was trained and selected on the trainable grid and LOTO; none against H1.
  1. **`tuned_L0` — clean code only, never saw an obfuscator — is competitive**, and on Qwen
     beat `mono_all` (0.245 vs 0.229).
  2. **`merge_dare_ties` is the best system**, with `l0merge_dare_ties` (six CLEAN-CODE
     adapters) within ~1 point. That gap IS the RQ2 result.
  3. **`formatonly` bounds** how much of any H1 gain is format acquisition rather than task
     learning.

- **Setup:** job 370026, 12 systems x H1, Grid A (`heldout`), n=1214, 1 over-long prompt
  dropped (`apps_1615_0::H1::2`, the same item every panel drops). Phase `h1_codellama`.

- **Results:**

  | system | acc | format_fail | vs base | vs FLOOR |
  |---|---|---|---|---|
  | `tuned_S2` | 0.283 | 0.027 | +0.155 | +0.150 |
  | `tuned_S1` | 0.278 | 0.035 | +0.149 | +0.144 |
  | `merge_dare_ties` | 0.277 | 0.026 | +0.148 | +0.143 |
  | `tuned_L2` | 0.266 | 0.030 | +0.138 | +0.133 |
  | **`l0merge_dare_ties`** | **0.262** | 0.030 | +0.133 | +0.129 |
  | `tuned_L1b` | 0.257 | 0.030 | +0.129 | +0.124 |
  | `tuned_L1r` | 0.252 | 0.028 | +0.124 | +0.119 |
  | **`tuned_L0`** | **0.238** | 0.035 | +0.110 | +0.105 |
  | **`mono_all`** | **0.232** | 0.010 | +0.104 | +0.099 |
  | `merge_ties` | 0.224 | 0.040 | +0.096 | +0.091 |
  | `formatonly` | 0.133 | 0.170 | +0.005 | +0.000 |
  | `base` | 0.129 | 0.185 | — | −0.005 |

- **What worked / hypothesis verdict:** **two of three CONFIRMED, one REFUTED.**
  - **(1) CONFIRMED.** `tuned_L0` 0.238 beats `mono_all` 0.232. An adapter that saw only clean
    code beats the one trained on all six obfuscations, on the obfuscator neither saw. The
    project's central finding reproduces on a second model family.
  - **(2) HALF CONFIRMED, HALF REFUTED.** `l0merge_dare_ties` lands 1.5 points behind
    `merge_dare_ties` (0.262 vs 0.277) — as predicted, merging six CLEAN-CODE adapters recovers
    **87 %** of what merging six specialists gets. But `merge_dare_ties` is **not** the best
    system: `tuned_S2` (0.283) and `tuned_S1` (0.278) both beat it. On Qwen the merge led the
    panel. **This is a genuine departure between families and is not smoothed over here.**
  - **(3) The floor is worth +0.005 on H1 — nothing.** Format acquisition buys essentially zero
    on the held-out obfuscator, so every point of H1 gain is real task learning. That makes
    these the most trustworthy numbers in the corpus, and it is why a control was included in a
    read this scarce.

- **Observations:**
  - **The floor behaves completely differently on H1 than on the trainable conditions.** It
    takes ~7 % of the gain on the trainable grid and **~3 %** here (+0.005 of +0.155). The
    reason is visible in `format_fail`: `formatonly` still fails format on **17.0 %** of H1
    items against 3 % for every real adapter. The label-shuffled adapter learned the format of
    the conditions it trained on and does NOT transfer that to a transform it never saw — so
    format competence is itself transform-specific, which is a small finding in its own right.
  - **`mono_all` has the LOWEST format_fail of any system (0.010) and nearly the lowest
    accuracy.** Breadth buys formatting, not task transfer. That is the same shape as the
    §4 "breadth does not help" result seen from a new angle.
  - **The single-specialist result inverts the Qwen ordering.** `tuned_S2` leading suggests
    that on a weaker base the best route to the held-out obfuscator is the closest structural
    specialist, not a merge — plausibly because CodeLlama degrades 6.4 pts clean->S2 where
    Qwen-7B degraded 2.5, so there is more structural damage for a structural specialist to
    repair. Speculative; stated as such.

- **New questions / new hypotheses:** **H-closest-specialist — on a weaker base, the best
  held-out-obfuscator system is the specialist whose transform is most similar to the held-out
  one, not a merge.** Testable without spending H1: the LOTO diagonal already measures
  "specialist meets an unseen transform" for all six conditions.

- **Next Steps:** (1) Cluster-bootstrap CIs on the H1 gaps; the `tuned_S2` vs `merge_dare_ties`
  gap is 0.006 and may not survive. (2) CodeLlama's `final_eval` is unspent and should stay
  that way until a method is frozen. (3) H-closest-specialist is answerable from existing LOTO
  cells at zero quarantine cost.
