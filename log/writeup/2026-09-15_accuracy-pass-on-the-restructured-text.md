# 2026-09-15 — Accuracy pass on the restructured paper: nine claims corrected, one contradiction resolved

**Thread:** writeup · **Prompted by:** user, "correct for new results so do accuracy pass on text" ·
Every quantitative claim in the active sections (abstract, intro, setup, results, threats) re-derived
from `results/cells/` and corrected where it disagreed.

## Corrected

| claim as written | measured | where |
|---|---|---|
| breadth below clean LoRA "on six of eight (significant on six, 1.0--4.7)" | below on **8/8**, significant on 6, sig range **2.7--4.7** | results |
| clean costs backward "on six", breadth "six", anchored "six" | clean 6/8 (sig 4), breadth 4/6 readable (sig 4), anchored 6/8 (**sig 5**) | results |
| anchored sig. below base backward "on four models, by as much as 6.9" | **five models, as much as 13.2** (Granite) | results |
| DARE-TIES backward "+2.0 to +7.7, significant on seven" | **+3.0 to +6.4**, significant on 7 | results |
| TIES "significantly above on five" | **six** | results |
| merges' collapse floor "0.000--0.001" | **0.000--0.002** | results |
| "the highest collapse rate belongs to the anchored objective" | holds the **panel max (0.680)** and the per-model max on **5/8** | results |
| "roughly nineteen points" | **20.0** mean over 30 arm-model pairs on the five single seen transforms | abstract |
| merge's forward cost "two to four points" (7 places) | **2.9--5.8, mean 4.2** | abstract, intro, results |

The backward counts changed because the two sources used different poolings — the earlier log paired on
the nine stacks, the new text pools every backward condition that clears the format gate. Both are
defensible; the text now states which one it uses and uses it throughout.

## Verified, unchanged

- Breadth below the mixture 3.3--5.9 on 8/8 (sig 8), below the merge 2.3--5.2 on 8/8 (sig 7).
- **The merge is never significantly below the untuned model in any of the three regimes on any of the
  eight models.** Tested directly, 24 contrasts: seen stacks +9.2 to +24.5 (sig 8/8 where readable),
  unseen family +6.6 to +17.6 (sig 8/8 where readable), backward +3.0 to +6.4 on 7 and −0.27 null on
  Granite. This is the paper's load-bearing claim and it holds.
- 15.3 % trivial golds; Llama 0.086 vs CodeLlama-7B 0.084 by exact arguments.
- Four lineages, eight models.

## The contradiction that had been left in the file

`setup.tex` asserted that a cell over the 0.25 format gate "measures the prompt contract rather than the
task". A comment beside it, added 2026-09-14, recorded that the measurement contradicts this and left
it unedited pending the framing decision. The new results section is built on the opposite reading, so
the two sections would have contradicted each other. Corrected: gated cells are now described as the
mixture they are, with the dagger/double-dagger distinction stated in the method, and the
non-random removal named as a limitation in both setup and threats.
