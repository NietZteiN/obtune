# `paper_bidirectional/` — ATTRIB 2026 submission, *The Free Flip*

*Last updated: 2026-08-12.* Draft **v1**, written from results on disk as of today.

**Scope of this directory: the bidirectional / CFT-refutation study only.** That is the
programme documented in [`../docs/CFT_REPLICATION.md`](../docs/CFT_REPLICATION.md), run
under `src/obtune/{cft,srh}/`, logged in [`../log/cft-replication/`](../log/cft-replication/),
and tabulated as Part V of [`../docs/RESULTS_BOOK_2026-08-11.md`](../docs/RESULTS_BOOK_2026-08-11.md).
It is **not** obtune's own RQ1–RQ3 paper (transfer / modularity / attention under a held-out
obfuscator), which gets its own directory when it is written — hence the name, so that a
second manuscript never has to fight this one for `paper/`. Nothing here reads or reports
`H1`; the quarantine budget in `../CLAUDE.md` §3.2 is untouched by this submission.

| | |
|---|---|
| venue | ATTRIB @ NeurIPS 2026, **main track**, non-archival |
| length | **3–6 pages body**; appendix in the same PDF, **no appendix page limit** |
| format | NeurIPS 2026 style (`neurips_2026.sty`, workshop option) |
| deadline | **Sept 1 AoE**; results freeze **Aug 28** |
| reviewing | **reciprocal.** At least one author must serve as reviewer, up to 2 papers, reviews due **Sept 22 AoE**. Submissions without a participating reviewer *may be desk rejected*. |
| checklist | **not required.** The NeurIPS paper checklist is a main-conference requirement; the ATTRIB call does not ask for it. `checklist.tex` is left in the directory but is no longer `\input`. |
| anonymity | **not stated by the call.** We submit anonymised (`[dblblindworkshop]`), which is the lower-risk default: anonymising a single-blind submission costs nothing, whereas de-anonymising a double-blind one risks desk rejection. Switch to `sglblindworkshop` and fill `\author` only if ATTRIB confirms single-blind. |
| plan of record | [`../docs/ATTRIB_CHECKLIST_2026-08-17.md`](../docs/ATTRIB_CHECKLIST_2026-08-17.md) |
| every number's source | [`NUMBERS.md`](NUMBERS.md) |

Verified 2026-08-17 against <https://attrib-workshop.cc/>.

## Files

| file | what |
|---|---|
| `main.tex` | the draft. Self-contained: `article` + `booktabs` + `natbib`, no external style file. |
| `refs.bib` | the six cited entries, trimmed from `../papers/references.bib`. |
| `NUMBERS.md` | provenance table: paper location → result file on disk. Also records what is *not* in the draft and what claims are deliberately not made. |

## Building

The host had no LaTeX toolchain, so one was installed on 2026-08-12:

```bash
conda create -y -p /data/jvl210002/conda_envs/tex -c conda-forge tectonic   # once
TMPDIR=/data/jvl210002/tmp_pip /data/jvl210002/conda_envs/tex/bin/tectonic -X compile main.tex
```

Tectonic 0.17.0, chosen over `texlive-core` because it is one binary and pulls only the
packages this document actually uses (first compile downloads them; later ones are cached
under `~/.cache/Tectonic`). It runs bibtex and the reruns itself — no `latexmk` needed.

Switching to the official style is a one-line change: replace the `\documentclass` +
`geometry` lines with the venue's `\usepackage{...}`. No body edits are needed — the draft
uses no class-specific macros.

**`refs.bib` must stay stripped of `note`/`file` fields.** Those are the annotations from
`../papers/references.bib`, and they contain raw `_` and `%`, which halt the engine while
building `main.bbl`. If you re-extract entries from the master bibliography, strip both
fields again.

### Current page count — still over the limit

**v2 (2026-08-17) compiles to 10 pages**: body §1–§11 filling p. 1–7, references on p. 8,
appendices A–E on p. 8–10. The venue allows 3–6 pp of main text (references and appendix
normally excluded), so the body is **~1 pp long**.

All three of v1's planned cuts are now applied, plus two more:

1. ~~§2's *Fidelity of the CFT reimplementation* paragraph~~ → **moved to App. A**, leaving
   two sentences and a pointer. The pointer stays in §2 — the whole reason it sits before
   §5 is to answer the desk-reject objection before it is raised.
2. ~~§7's *Prompting does not rescue what tuning removed*~~ → **folded**, and merged with
   the new prompt-insensitivity result into one paragraph.
3. ~~§10's *Auxiliary pool ratio* and *Seeds* bullets~~ → **one sentence each**.
4. ~~§2's arm-definition table~~ → **inlined as prose**; the arms were already described.
5. ~~§7's criterion paragraph~~ → **compressed**; App. C carries the table.

v2 also *added* about 0.65 pp net: Fig. 1 and its paragraph, the JavaScript paragraph, the
prompt-insensitivity result, and the determinism methods sentences.

Remaining candidates, in cost order — these are **content decisions, not mechanical trims**,
so they are deliberately left to the author:

- Table 3 (budget ratios) → appendix, ~0.3 pp
- Table 4 (per-condition reverse) → appendix, ~0.25 pp
- §1 Introduction + contributions list, ~0.3 pp

Do **not** buy pages back by cutting §8 (the HumanEval+ cost) or the CI-in-sentence
convention below.

### The figure is generated, not drawn

`fig_dose.tex` is emitted by `scripts/srh/25_fig_dose.py` straight from the dose run's
`trials.jsonl` and `contrasts.json`, so no number in it is hand-typed and re-running the eval
regenerates it. Do not hand-edit that file. Regenerate with:

```bash
python scripts/srh/25_fig_dose.py \
  --run results/2026-08-12_cft-bidirectional/qwen25c-1.5b/python/e3_dose_qwen1.5b \
  --out paper_bidirectional/fig_dose.tex
```

pgfplots is a new preamble dependency; tectonic fetches it on first compile.

## What lands next, and where it goes

The four runs this section previously listed **all landed 2026-08-12** and are folded into
v2: the dose ladder is Fig. 1, the JavaScript replication is §3 + App. E, the strategy sweep
is App. B, and the seed replication is App. D.

What remains is one optional run and two decisions:

| | item | where it goes |
|---|---|---|
| 1 | **HumanEval+ on `mix5`/`mix10`/`mix25`** (~1 h, inference only; not yet run) | §8. The benefit saturates by a 5 % reverse share; if the *cost* does not, `mix5` dominates `mix50` and §8 turns from a caveat into a prescription. The strongest remaining addition. |
| 2 | HumanEval+ for 7B `rev` and `fwd2x` (~1 h, inference) | fills the two blank cells in Table 5's 7B column. |
| 3 | **Decide the last ~1 pp of trim** | see the page-count section above. |
| 4 | Venue style file, anonymisation, OpenReview checklist | before the Aug 28 freeze. |

Items 1–2 are wired into the scheduler and validated but **deliberately not enqueued**:

```bash
python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps          # dry run
python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps --write  # enqueue
```

Compute as of 2026-08-17: all four GPUs busy (three held by the borrower, one by the
modularity grid), `gpu_budget: 1`, and five modularity jobs queued at priority 10–20. The
enqueue default of 59 sits behind them by design; `--priority 5` jumps the queue at the FSE
paper's expense and is a human decision.

## Draft conventions worth preserving through edits

- Every strong claim carries its CI **in the sentence**, not in a footnote.
- "Free" is scoped to training budget everywhere it appears, and the HumanEval+ cost is in
  the body (§8), not buried in limitations.
- The source paper *declares* Bidirectional Fine-Tuning and reports no number for it. Do
  not weaken this to "never ran the baseline" — it is factually wrong and the authors may
  review this submission.
- §2 documents CFT reimplementation fidelity **before** §5 reports the null, so the
  desk-reject objection is answered before it is raised.
