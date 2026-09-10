### Target Date: 2026-09-10 (paper draft: argument and flow for RQ1–RQ4)
- **Hypotheses / what we're testing:** writing day, no experiment and no cell read.
- **Setup:** `docs/PAPER_DRAFT.md` created — title candidates, abstract, the introduction's five
  moves, and a section-by-section argument with the load-bearing number in each place. Sources are
  `RQ_SUMMARY.md`, `PAPER_FRAMING.md` and the pipeline JSONs; no new measurement.
- **Results:** the spine, in one line — *adaptation to single obfuscations produces surface-anchored
  competence that composes only within what it has seen; anchoring to clean-code behaviour removes
  the cost of breadth without creating the capability breadth lacks.*
- **What worked / hypothesis verdict:** n/a. Three of the originally stated findings are adjusted in
  the draft because the evidence differs, and each adjustment makes the paper stronger rather than
  weaker:
  1. **"All three composition strategies fail" → a dissociation.** Breadth *succeeds* on stacked-seen
     inputs at every scale (+3.49 / +2.90 / +3.05, +4.15 at depth 3–4). The finding is that it buys
     recombination and not novelty, with the tax growing as the gain saturates. Blanket failure would
     be both wrong and less interesting.
  2. **"Merging fails through task-vector interference" → no mechanism claimed.** The interference
     account was refuted on the frozen panel (same-data cross-seed adapters near-orthogonal at
     cosine 0.053 and merging fine), and that panel is not cited any more, so the paper reports
     merging's failure without supplying a cause until F1b measures it here.
  3. **"Consistent performance on the reverse task" → does no harm.** `cons_lam3 − base` is +0.49
     [−1.38, +2.30]: it is the only SFT-family arm not damaged by the flip, which is a real and
     defensible claim, and not the same as improving.
- **Observations:**
  - **The gate-as-screen result is promoted into §2 Setup as a measurement contribution**, not
    buried in limitations. Screening base models by untuned `format_fail` rejected three of five
    candidates for three unrelated prompt-contract reasons; tuned, they reach 0.5401 / 0.5180 /
    0.4647. "Untuned format failure measures the prompt contract, not the model" is a finding an SE
    venue should want, and it is cheap to state.
  - **RQ4's bound is written in the paper's own voice rather than left for a reviewer to extract.**
    On the held-out family the anchored arm equals clean-code tuning and is 7th of 33; combined with
    the teacher ablation (student ≈ teacher + ~1 pt) the claim is a Pareto repair, not new invariance.
  - **Every ❑ in the draft is a gap with the experiment that closes it**, so the draft doubles as a
    to-do: routing/merging on stacks (F1), the unseen-in-stack divergence ladder (F2, which is what
    would actually decide RQ4), the cue-destruction order pair (F3), the compute-matched control (F4),
    and the model-panel extension now training.
- **New questions / new hypotheses:** none.
- **Next Steps:** prose for §1 and §2 against this skeleton; Fig. 1 (the dissociation at three scales
  plus the volume row) first, since it is the image the paper is remembered by and every number in it
  already exists.
