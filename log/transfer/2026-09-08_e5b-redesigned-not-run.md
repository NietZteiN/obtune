### Target Date: 2026-09-08 (E5b — respecified rather than run: E6 refuted the relation the planned design was built to test)
- **Hypotheses / what we're testing:** nothing was run, so nothing is verdicted. This entry exists
  because "not run" is a decision that needs its reasoning on the record as much as a result does.
- **What E5b was.** E5 (2026-09-07) tried to generalise C2 — *what transfers is the family, not
  invariance* — beyond the single X1/H1 pair, using X2/Y2: **same mechanism** (values routed through
  exception machinery), **different surface** (X2 raises a `LookupError`, Y2 uses the generator
  protocol). It came back +1.21 [−0.81, +3.22], and the entry correctly diagnosed a *power* failure:
  the family damages a clean-code adapter by 3.8 pts against X1's 15.8, so ~1.2 pts of signal sat
  against a ±2-pt interval. E5b was written as "the same experiment with a harder family".
- **Why that specification is now wrong.** E6 (read 2026-09-08) tested the *same relation* inside X1
  itself. X1m (guarded MBA) and X1s (string encoding) share the family, the module, the helper-naming
  convention and the reading schema — and they **do not transfer to each other**: `tuned_X1m` on X1s
  is **+1.49** [−0.95, +3.93], `tuned_X1s` on X1m is **−0.10** [−2.38, +2.19]. H-family-unit REFUTED.
  A harder X2/Y2 pair is the same "shared mechanism, different surface" relation with more damage,
  so E6 predicts it comes back null **whatever** its difficulty — and a null would then confirm E6
  rather than test C2. Running it would spend a CPU-day and ~1.5 GPU-h to buy an uninterpretable
  number.
- **What the two results jointly say, and what E5b must therefore become.** X1 → H1 is *lossless*
  (0.08 pts) across genuinely different surfaces — different helper names, different algebraic
  identities, a different encoding scheme — while X1m → X1s fails across a *shared* surface. Neither
  "surface" nor "mechanism", as those were operationalised, survives both observations. What does is
  **the reading operation the transform forces**: X1 and H1 both force "evaluate a locally-defined
  decoder to recover a literal", while MBA and string encoding force different ones despite sitting
  in one family. E5b's job is to vary *that*, at matched damage:
  - **X3 / Y3** sharing one forced reading operation and differing in every surface detail, in a
    domain that is neither encoding nor arithmetic — the strongest candidate is comparison/ordering
    (every `<`, `<=`, `==` recomputed through a helper: X3 by sign-of-difference, Y3 by a
    `sorted`-based lookup).
  - **The damage gate stays and is non-negotiable:** build Y3 first, evaluate `tuned_L0` on it,
    proceed only if the drop from L0 exceeds 10 pts. E5's null was a power failure; repeating it
    would waste the corpus as well as the GPU.
  - **Pre-register before the generator exists**, so which pair "counts" cannot be chosen after
    seeing which damages more — the same discipline that made E7c worth running.
- **Why it is not being written today.** This is a design problem, not an execution problem. Every
  other open item this session turned out to be blocked on something that was not actually true
  (`node` blocked *regenerating* the JS corpus rather than using it; E10's "missing" Paper-2 item map
  is on disk with all 98 cells matching). E5b is the one that is genuinely unbuilt, and a generator
  shipped in haste writes a corpus that costs CPU-days to regenerate and can silently corrupt a
  headline claim — the H1-quarantine layers exist because exactly that class of mistake is
  unrecoverable. Specifying it correctly and leaving it unrun is the better outcome than running the
  version E6 already answered.
- **Next:** pre-register X3/Y3 to the shape above, then write the generator against the damage gate.
  Docs updated: `docs/PAPER_EXPERIMENTS.md` E5b (specification replaced, status recorded).
