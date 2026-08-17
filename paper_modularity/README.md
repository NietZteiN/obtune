# `paper_modularity/` — the RQ2 routing-and-merging manuscript

*Last updated: 2026-08-13.* Draft **v0.1**, written from result files on disk as of today.

**Scope: RQ2 (modularity) only** — how six per-transformation LoRA specialists can be combined
into one system, and what each combination strategy is worth. Sibling to
[`../paper_bidirectional/`](../paper_bidirectional/) (the CFT-refutation side thread, ATTRIB
2026), which reserved this directory in its own README. RQ1 appears here only as motivation;
RQ3 (attention) and the human-alignment thread are not in this manuscript.

| | |
|---|---|
| venue | **FSE research track** — `acmart` `sigconf`, double-anonymous |
| length | ~10 pp technical + unlimited references — **confirm against the live CfP before freezing** |
| current | **7 pp** including references. Room to grow. |
| status | **thesis deliberately empty** — see [`CLAIM_LADDER.md`](CLAIM_LADDER.md) |
| every number's source | [`NUMBERS.md`](NUMBERS.md) |

## Files

| file | what |
|---|---|
| `main.tex` | the draft |
| `refs.bib` | 8 entries extracted from `../papers/references.bib` + **7 new ones marked `UNVERIFIED`** |
| `NUMBERS.md` | per-claim provenance; also records 4 report-vs-file discrepancies and what is deliberately absent |
| `CLAIM_LADDER.md` | the four candidate theses, the run that licenses each, and the decision order |
| `analysis/10_collect_cells.py` | collects all 897 cells and 369,089 trials from `results/cells/` |
| `analysis/11_rq2_contrasts.py` | every delta, CI, and FDR correction in the paper |

## Building

```bash
cd paper_modularity
TMPDIR=/data/jvl210002/tmp_pip /data/jvl210002/conda_envs/tex/bin/tectonic -X compile main.tex
```

Tectonic 0.17.0 (installed 2026-08-12 for `paper_bidirectional`; first compile of `acmart`
downloads it, later ones are cached under `~/.cache/Tectonic`). It runs bibtex and reruns
itself — no `latexmk`.

**Do not add `\usepackage{amssymb}`.** `acmart` loads `newtxmath`, which already defines
`\Bbbk`; adding `amssymb` halts the engine. `booktabs` and `amsmath` are likewise already
loaded by the class.

## Regenerating every number

```bash
cd ..                                    # repo root
export OBTUNE_PAPER_CACHE=paper_modularity/.cache
/data/jvl210002/conda_envs/obtune/bin/python paper_modularity/analysis/10_collect_cells.py
/data/jvl210002/conda_envs/obtune/bin/python paper_modularity/analysis/11_rq2_contrasts.py
```

`.cache/` is regenerable and should be gitignored.

## Audits to run before any submission

```bash
grep -n 'pending\|slot{' main.tex          # both must reach zero (or a consciously kept set)
grep -n UNVERIFIED refs.bib                # must reach zero
```

Citation-key audit (the naive regex misses keys ending in digits — allow them):

```bash
python - <<'EOF'
import re
tex, bib = open('main.tex').read(), open('refs.bib').read()
cited = {k.strip() for m in re.findall(r'\\cite\{([^}]*)\}', tex) for k in m.split(',')}
have  = set(re.findall(r'^@\w+\{([^,]+),', bib, re.M))
print('dangling:', sorted(cited - have), '| unused:', sorted(have - cited))
EOF
```

Currently: 15 cited, 15 in bib, 0 dangling, 0 unused.

## The three things a reader of this draft should know first

1. **The thesis slot is empty on purpose.** Five results are settled (`CLAIM_LADDER.md`
   "What is already settled"); the sixth — whether a learned mixture beats a fixed one on
   composite inputs — is +2.9 points at p=0.059 with an inert control. The draft reports that
   and declines the claim.
2. **`mole_random` does not work.** It is bit-identical to `mole_uniform` on all 1,299 items
   because a `ConstantGate` exposes no parameters for its re-init loop to touch, and
   `mole_uniform` runs first in the ladder. Diagnosis in `NUMBERS.md` §5, filed in
   `../log/modularity/2026-08-13_mole-random-inert-control.md`. **One evaluation pass fixes it
   and it is the first item in the decision order.**
3. **Four experiment groups here postdate `docs/MASTER_REPORT_2026-08-12.md`**, which still
   lists them as pending: the 8-expert uniform-epoch sweep, the merge-optimal search, the
   repaired DARE-linear arm, and the mixture ladder. The master report also carries a
   superseded geometry table and a resolved "no Python control" issue — see `NUMBERS.md` §4.
   **The master report should be revised before it is used as an index again.**

## Conventions worth preserving through edits

- **Every number is read from a result file, never from a report.** The reports are an index of
  where to look. Four discrepancies were caught this way (`NUMBERS.md` §4).
- **The two evaluation grids are never pooled.** They are disjoint in programs. This is enforced
  in `11_rq2_contrasts.py`, not left to care.
- **Every strong claim carries its CI in the sentence**, not in a footnote (inherited from
  `paper_bidirectional`).
- **`\pending` is never filled with a plausible value.** It marks a gap, and a gap that reads as
  a measurement is worse than an obvious hole.
- **The reference is the clean-code adapter, not the base model.** A system that beats the base
  model has shown nothing — §3.5 of the draft says why, and it should stay in the body.
- **`merge_dare_linear` stays in the paper as a defect**, with its repair. Deleting it would
  hide the most transferable methodological point: format-failure rate is what distinguished a
  bug from a −40-point finding.

## What lands next

Ordered by `CLAIM_LADDER.md`'s decision order. All are pending runs, not writing tasks.

| | run | what it changes in the draft |
|---|---|---|
| 1 | `mole_random` with the ordering hazard repaired | unblocks the abstract; decides Branch A vs B |
| 2 | under-trained expert bank, routed **and** merged | tests Branch D, the strongest thesis |
| 3 | composites at corpus scale (~550 programs) | powers the §7 effect |
| 4 | second seed for every combination arm | makes every ±3 pt number claimable |
| 5 | merge density sweep; hard-router rung; `H1` routing entropy; 7B | scope, threats, deployment claim |
