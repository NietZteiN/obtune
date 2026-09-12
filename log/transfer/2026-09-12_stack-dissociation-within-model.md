### Target Date: 2026-09-12 (RQ1's headline as a MEASURED difference: the seen/unseen stack dissociation is significant on 4 of 4 models read, across three lineages)
- **What changed.** Until now the dissociation was two separate reads on two program sets, and the
  natural summary — *"breadth gains on seen stacks and loses on unseen-containing ones"* — was
  **not a test of the difference between them**. On three of the four models the unseen-side
  interval straddles zero on its own, so stating the dissociation from the two levels separately
  would have been stating something never measured. Same error as
  [F3a](../modularity/2026-09-11_f3a-stack-identifier.md), same fix.
- **What is computed.** Per model, on the **319 programs common to every cell of both groups**:

  `[mono_all − tuned_L0 on the six SEEN depth-2 composites] − [same on the three composites
  containing the unseen family]`

  on one program-clustered bootstrap (2,000 resamples, seed 17), so the halves are paired and the
  difference carries its own interval. `scripts/analysis/57_stack_dissociation.py`.
- **Results:**

  | model | lineage | seen stacks | unseen-containing | **difference** |
  |---|---|---:|---:|---:|
  | codellama-7b | Meta | **+3.36** [+1.57, +5.27] | **−1.92** [−3.70, −0.14] | **+5.28** [+3.20, +7.54] |
  | codellama-34b | Meta | **+2.27** [+0.44, +4.09] | −0.77 [−2.62, +1.12] | **+3.03** [+0.78, +5.28] |
  | llama31-8b | Meta | **+2.30** [+0.47, +4.15] | −1.05 [−2.72, +0.63] | **+3.35** [+1.50, +5.30] |
  | starcoder2-15b | BigCode | +1.50 [−0.02, +3.00] | −1.19 [−2.93, +0.49] | **+2.68** [+0.77, +4.65] |
  | **tally** | | | | **4 of 4 significant** |

- **The dissociation is the robust quantity; the levels are not.** Only one model has a
  significantly negative unseen-side level and only three have a significantly positive seen-side
  one — **but every one of the four differences excludes zero**, including StarCoder2, whose two
  levels both straddle zero individually. Pairing is what makes the claim measurable.
- **Intersecting moved the estimates, and that is reported rather than hidden.** The seen composites
  cover more programs than the unseen-containing ones (the unseen family needs ≥ 3 sites), so the
  common set is 319 against the 557 the seen composites have alone. CodeLlama-7b's unseen-side level
  goes from −1.71 (n.s., on its own 287-program set) to **−1.92 (significant)** here. Neither number
  is wrong; they are different program sets, and only the paired one supports a difference.
- **What may be said:** on every model read, breadth's advantage over clean-code tuning is
  **2.7–5.3 points larger on stacks built from transforms it saw than on stacks containing a family
  it did not**, and the gap is significant on each.
- **What may NOT be said:** that breadth is significantly *harmed* by an unseen component. Three of
  four unseen-side intervals include zero. The measured claim is the **difference**.
- **Coverage.** Four of eight models. The other four need their seen-composite cells, which are
  queued (`ev_cseen_*`, P0/C3 of `docs/EXPERIMENT_CHECKLIST.md`); the script skips an incomplete
  grid rather than reading a partial one.
- **Next Steps:** re-run when the remaining four land; carry the difference column into
  `paper/tables/` and RQ1.
