### Target Date: 2026-09-08 (Read — E4 / RQ3′ teacher variation: the *tuned clean-code* teacher is the ingredient — an untuned teacher destroys the objective, a breadth teacher imports breadth's unseen-family tax)
- **Hypotheses / what we're testing:** rules frozen in `CLAUDE_SCRATCHPAD.md` (E4, before the 09-07
  submission). **H-E4-view** ("the parent view alone beats breadth on the unseen family") CONFIRMED
  iff `cons_tbase − mono_all` @ X1 ci_lo > 0. **H-E4-teacher** ("the tuned clean-code teacher
  matters") CONFIRMED iff `cons_lam3 − cons_tbase` @ X1 ci_lo > 0. **H-E4-mono**
  (`cons_tmono − cons_lam3` @ X1): ci_lo > 0 CONFIRMED (a breadth teacher helps), ci_hi < 0 REFUTED
  (a breadth teacher imports its tax), else INCONCLUSIVE.
- **Setup:** two new 7B arms, both `cons` objective, parent view, λ = 3, seed 17, differing only in the
  frozen teacher: **`cons_tbase`** = untuned `base` as teacher; **`cons_tmono`** = `mono_all` as
  teacher. `tr_cons_tbase` / `tr_cons_tmono` → `ck_*` → `ev_teacher` → `an_e4` **382548**
  (`36_cons_arms.py --mode e4`, `results/analysis/pipeline/e4_teacher.json`). Seven columns, n_prog
  557 (L0/seen) and 405 (X1). No H1.
- **Results (accuracy, 7B):**

  | system | L0 | L1b | L1r | L2 | S1 | S2 | X1 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | `tuned_L0` | **0.4263** | 0.3571 | 0.3766 | 0.3796 | 0.3833 | 0.3881 | 0.2710 |
  | `mono_all` | 0.4132 | 0.3860 | 0.3874 | 0.3802 | 0.3849 | 0.4043 | 0.2331 |
  | `cons_lam3` (teacher `tuned_L0`) | 0.4216 | **0.4017** | **0.3928** | **0.3928** | **0.4018** | **0.4151** | **0.2817** |
  | `cons_tbase` (teacher `base`) | 0.3060 | 0.2823 | 0.2892 | 0.2844 | 0.2606 | 0.3035 | 0.1433 |
  | `cons_tmono` (teacher `mono_all`) | 0.4126 | 0.3999 | 0.3892 | 0.3892 | 0.3921 | 0.4127 | 0.2397 |

  Contrasts, pts [95 % CI], program-clustered bootstrap:
  - **H-E4-view REFUTED:** `cons_tbase − mono_all` @ X1 **−8.98** [−11.44, −6.43]*; seen −10.35*,
    L0 −10.72*. An untuned teacher does not merely fail to help — the arm lands ~5 pts above `base`
    (L0 0.306 vs 0.257) and 12 pts below `tuned_L0` on every column. With λ = 3 the KL term pins the
    student to the teacher's distribution, and the base model's distribution on clean code is the
    wrong target: the SFT term cannot pull the student away from it.
  - **H-E4-teacher CONFIRMED:** `cons_lam3 − cons_tbase` @ X1 **+13.84** [+11.19, +16.56]*; seen
    +11.55*, L0 +11.56*. Swapping the teacher from `tuned_L0` to `base` accounts for more than the
    whole tuned-vs-base gap. The teacher is not incidental.
  - **H-E4-mono REFUTED** (a breadth teacher imports its tax): `cons_tmono − cons_lam3` @ X1
    **−4.20** [−6.27, −2.14]*; seen −0.39 [−1.71, +0.92], L0 −0.90 [−2.52, +0.72]. And
    `cons_tmono − mono_all` @ X1 +0.66 [−0.91, +2.23] — the student with a breadth teacher lands on
    breadth's X1 number, not on `tuned_L0`'s.
- **Reading — a clean decomposition of what the objective does.** The two halves of `cons_lam3`'s
  result have different sources, and E4 separates them:
  1. **The seen-condition gain does not depend on the teacher.** `cons_tmono` and `cons_lam3` are
     within 0.4 pts on the seen average (0.3999 vs 0.4017 on L1b, etc.), and both are ~+2.4 over
     `tuned_L0`. That gain comes from the SFT term over the obfuscated rows, which is the same in
     both arms.
  2. **The unseen-family number is inherited from the teacher.** Student X1 tracks teacher X1 with a
     small, non-significant bonus: teacher `tuned_L0` 0.2710 → student 0.2817 (+1.07 [−0.82, +2.96]);
     teacher `mono_all` 0.2331 → student 0.2397 (+0.66 [−0.91, +2.23]); teacher `base` 0.1194 →
     student 0.1433 (and the base teacher drags everything else down with it). The consistency
     objective is, on the unseen family, a distillation of the teacher — it does not *create*
     invariance, it *transfers* the teacher's behaviour on the family and adds breadth's seen gain on
     top without breadth's tax, **provided the teacher itself has not paid that tax**.
  This narrows the RQ3′ claim in exactly the way `docs/PAPER_EXPERIMENTS.md` E4 anticipated: the
  method is "distil from a *clean-code-tuned* model on the clean parent", not "distil from *some*
  view of the clean parent". The paper must say so. It also explains E8 and E3 without new
  machinery: at every scale and on Llama, `cons_lam3` ≈ `tuned_L0` on X1 (−0.33 / +0.74 / +0.58 /
  +1.07) because that is the teacher's number.
- **Unregistered observation:** `cons_tmono` is a strictly better breadth model than `mono_all` —
  seen +0.81 [−0.25, +1.89], L0 −0.06 (breadth's own L0 cost was −1.32), X1 +0.66. The objective
  removes breadth's L0 cost even with a breadth teacher; only the X1 tax is inherited. Exploratory.
- **Caveats.** Single seed; λ = 3 only (a smaller λ with the base teacher would presumably collapse
  less, but the pre-registered arm is λ = 3 and no λ sweep on `cons_tbase` was run); 7B only.
- **Next:** RQ3′'s open column is now empty (scale ✓, Llama ✓, ingredient ✓). Docs: `docs/RQ_SUMMARY.md`
  §6 RQ3′ row, `log/transfer/README.md` H-cons-teacher, `docs/PAPER_EXPERIMENTS.md` E4.
