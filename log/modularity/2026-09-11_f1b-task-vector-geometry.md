### Target Date: 2026-09-11 (F1b: CodeLlama reproduces the Qwen result — merging's failure is NOT explained by contrasting task-vector geometries, and SEED dominates CONDITION)
- **Repeats on CodeLlama-7b** the geometry read that refuted the interference story on Qwen
  (`REPORT_2026-08-17` §3). CPU only, ~5 min total across three jobs; no GPU, everything computed
  from safetensors already on disk.
- **Hypothesis under test.** The finding attributes merging's failure to "contrasting task-vector
  geometries" — i.e. the per-condition adapters point in conflicting directions, so a merge
  cancels them. If true, the five specialists that feed the merge should be poorly aligned, with
  high coordinate sign conflict and low TIES retention.
- **Setup.** `scripts/merge/20_geometry_report.py`, r = 32, layers 0/7/14/21/27, three banks that
  isolate the two axes:

  | bank | what varies | mean cosine | cos min | sign conflict | TIES keep | ‖ΔW‖ |
  |---|---|---:|---:|---:|---:|---:|
  | 5 specialists @ s17 | **condition only** | **0.653** | 0.550 | **0.323** | **0.916** | 0.664 |
  | `L0` @ s17/s42/s101 | **seed only** | 0.119 | 0.109 | 0.470 | 0.785 | 0.636 |
  | 5 specialists × 2 seeds | both | 0.344 | 0.070 | 0.554 | 0.699 | 0.640 |

- **Verdict: the interference mechanism is REFUTED as the explanation on this model too.** The five
  adapters the merge is actually built from are the **most aligned, least conflicting,
  highest-retention** bank of the three. TIES keeps 92 % of their coordinates. Merging them still
  loses to the specialists it is made of (−3.13 against +2.47, the published CodeLlama numbers). A
  mechanism that predicts cancellation cannot be the cause of a failure that happens where
  cancellation is at its lowest.
- **The stronger finding is the axis ordering.** Varying the **seed alone** drops mean cosine from
  0.653 to **0.119** — near-orthogonal — while varying the **condition alone** leaves it at 0.653.
  Seed moves the task vector far more than the task does. In the mixed bank the most aligned pair
  (cos 0.756) is a *same-seed* pair and the least (0.070) a cross-seed one. Whatever the ΔW
  direction encodes on this model, it is mostly not the transform.
- **Consequence for the paper.** The merging result stands; its stated *mechanism* does not. RQ1's
  merging paragraph must report the failure **without** the interference explanation and cite this
  as the reason. Two independent model families now say the same thing, which makes it a finding
  rather than a caveat.
- **Caveat, stated rather than buried.** `L0@s42` best-selects `checkpoint-74` where s17 and s101
  select `checkpoint-148`, so the seed-only bank mixes two training lengths. Cosine is
  scale-invariant and the norms are close (0.559 vs 0.674 / 0.676), so this cannot manufacture the
  0.653 → 0.119 gap, but the seed-only row is not a perfectly clean contrast and should not be
  quoted to more precision than "near-orthogonal".
- **Not claimed:** that merging fails *because* of seed sensitivity. This measures geometry, not
  accuracy, and no causal link between the two is established here.
- **Next Steps:** none blocking. F1's merge cells on composites will say whether the failure also
  holds on stacked inputs; the geometry read is independent of that.
