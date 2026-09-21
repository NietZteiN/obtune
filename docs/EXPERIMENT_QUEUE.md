# Experiment queue — reviewer response round
*Opened 2026-09-20. Deadline for Tier A: 2026-10-02.*

Status values: **DONE** (result exists and is in the paper) · **PARTIAL** (result exists, a stated
gap remains) · **QUEUED** (submitted) · **TODO** · **BLOCKED** (cannot run, reason given).

Update this file when an item changes state. Numbers here are pointers, not results; results live
in `results/analysis/pipeline/` and the `log/` entries named per item.

---

## Tier A — before 2026-10-02

### A1. Fill the missing arms in Table 5 — **TODO**
Reverse row: `breadth` on CodeLlama-13B and CodeLlama-34B, `router` on CodeLlama-34B.

**Triage changes what this is.** Two of the three are not absent, they are format-gated:

| model | arm | backward format-failure |
|---|---|---|
| CodeLlama-13B | breadth | 0.72–0.94 |
| CodeLlama-34B | breadth | 0.32–0.52 |
| CodeLlama-34B | router | no cells at all |

So A1 is one rerun under fixed decoding (the two breadth arms) plus one genuinely new eval
(34B router). If the rerun does not clear the 0.25 gate, the fallback the reviewer offers is the
honest one: drop the "strongest on six of eight" count and compare only where every arm exists.
*Lands in Table 5, §7.3.*

### A2. Backward-task decomposition table — **PARTIAL**
Four quantities per model per arm: execution-graded accuracy, exact reference-input recovery,
format success, direction-lock rate.
Built by `scripts/analysis/73_direction_lock.py`; `tables/backward_decomp.tex` and
`tables/direction_lock.tex` are `\input` in RQ3.
**Gap:** columns are Base, Clean, Breadth, KL, Router, Merge. The requested **ICL** column is
missing. Add it if an ICL arm exists on the panel, else say so in the caption.

### A3. Specialist-subset merges — **PARTIAL**
Four ingredient sets at fixed operator/density/weights/rank: `no-L0` (L1b,L1r,L2,S1,S2),
`ident` (L1b,L1r,L2), `struct` (S1,S2), and the six-way reference.
Built by `scripts/analysis/76_merge_ablation.py`; `tables/merge_ablation.tex` is in RQ1 §5.2.
Complete on four models, both directions, 92 forward + 64 backward cells each.
**Gap:** condition groups are `L0`, singles, depth-2, held-out. **Depth-3 stacks are not
reported** and the reviewer asks for them.

### A4. Paired bootstrap intervals — **DONE**
All eight requested contrasts are computed by `scripts/analysis/74_main_contrasts.py --ablation`,
program-clustered, 2,000 resamples, seed 17.
Two prose claims were already deleted as unsupported: Merge − Clean LoRA on `L0` is null on all
eight models, and Router − Merge on the unseen family is significant on seven, not six.
**Remaining editorial task:** sweep the draft for surviving 0.3–0.4 point claims the intervals do
not support.

### A5. Merge operator ablation and implementation audit — **PARTIAL**
*Audit:* **DONE.** `scripts/analysis/79_merge_space_check.py`, all eight models. §3's factor-space
claim matches the implementation. Its random-factor figure (cosine 0.40) is a worst case; on the
deployed adapters the two spaces agree at cosine 0.539–0.848, tracking specialist alignment at
r = 0.95. `merging.tex` amended.
**Gap:** the operator comparison. `ties`, `dare_ties` and `dare_linear` adapters exist; **plain
uniform averaging (`linear`) does not** and is the control the reviewer actually wants. Build it
and evaluate on two models.

### A6. H1 — **BLOCKED, must be CUT not run**
H1's budget is **fully spent** (CLAUDE.md §3.2, changelog 2026-09-05): one pilot pass and one
final pass, both taken. Rule 3 permits no further read, and no H1 number may select, tune or rank
anything. **Running it is forbidden and I will not.**
The resolvable half: the 2026-09-05 final read exists (`log/transfer/2026-09-05_h1-final-read.md`).
Reporting those already-paid-for numbers is not a new read. So the choice is *report the existing
final-read result* or *remove H1 from Table 2* — a writing decision, not an experiment.
X1 is the trainable sibling and is already reported throughout as the held-out family.

### B9-equivalent note
Cross-language is listed in Tier B but was run today; see B9 below.

---

## Tier B — if time allows

### B7. Deployment cost table — **TODO**
Stored parameters, peak inference memory, tokens/sec for untuned, single LoRA, router, merge.
The defence against the router is currently a cost claim with no number.

### B8. Seed variance on CodeLlama-7B — **TODO**
Three seeds for breadth and for the six specialists, to establish a noise floor. Requires real
training. Seed 42 already exists for Granite and for parts of the panel.

### B9. JavaScript — **PARTIAL**
Run today. `configs/eval/crosslang_fwd.yaml`, `scripts/analysis/78_crosslang.py`,
`tables/crosslang.tex`, in RQ3. Four models, 192/192 cells.
Result: every adapted arm reading obfuscated JavaScript beats the untuned model reading clean
JavaScript, +16.4 to +30.8 points, significant in all twelve comparisons.
**Two gaps and one hard limit:**
* `router` arm not included (Base, Clean, Breadth, Merge were).
* **Backward is impossible**: grading executes the predicted input and juno has no `node`.
* **Contamination**: CruxEval-X/HumanEval-X are ports; 87 of 168 JS test programs are Python
  training programs. All figures use the clean 81. Pinned by `tests/test_split_integrity.py`.

---

## Compute note
The juno pool share was returned to **0** on 2026-09-20 and `submit.py` refuses h200/normal
submissions at that setting. **`h100` and `a30` carry no QoS** and are where this round runs.
Raise the share deliberately, and say why in `configs/compute.yaml`, only if that proves
insufficient.
