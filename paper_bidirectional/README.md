# `paper_bidirectional/` — ATTRIB 2026 submission, *The Free Flip*

*Last updated: 2026-08-18.* Draft **v4** — reframed.

> **What this paper is about, as of v4.** The contribution is an **attribution confound**, not a
> refutation. When training pairs read both ways, every example is already an example of the
> opposite direction, so any intervention that adds instances also changes which directions the
> model sees — and the usual controls miss it, because instance counts, tokens, steps and compute
> can all be matched exactly while directional content differs. The CFT replication is the
> *worked instance* where that confound accounts for a published effect entirely. Edits that
> push the paper back toward "CFT does not work" are moving it away from the venue: ATTRIB is an
> attribution workshop, and the general claim is the part that belongs there.

**Scope of this directory: the directional-confound paper only** (the CFT replication is its
worked instance). That is the
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
export XDG_CACHE_HOME=/data/jvl210002/.cache   # keep the package cache off $HOME (small NFS)
TMPDIR=/data/jvl210002/tmp_pip /data/jvl210002/conda_envs/tex/bin/tectonic -X compile main.tex
```

**`tectonic` is not on `$PATH`** and there is no `pdflatex`/`latexmk` anywhere on the host, so a
bare `which pdflatex` reports nothing and looks like a missing toolchain. It is not. Use the
absolute path above, or `export PATH=/data/jvl210002/conda_envs/tex/bin:$PATH` first.

Tectonic 0.17.0, chosen over `texlive-core` because it is one binary and pulls only the
packages this document actually uses (first compile downloads them; later ones are cached
under `~/.cache/Tectonic`). It runs bibtex and the reruns itself — no `latexmk` needed.

Switching to the official style is a one-line change: replace the `\documentclass` +
`geometry` lines with the venue's `\usepackage{...}`. No body edits are needed — the draft
uses no class-specific macros.

**No literal non-ASCII in `main.tex`.** Check before every submit:

```bash
grep -nP '[^\x00-\x7F]' main.tex          # must print nothing
pdftotext main.pdf - | grep -c $'\u0306'   # must print 0
```

Tectonic is XeTeX, so `\usepackage[utf8]{inputenc}` is a no-op (`main.log`: *"inputenc package
ignored with utf8 based engines"*) while `[T1]{fontenc}` stays in force. A literal `§` (U+00A7)
therefore lands on T1 slot 0xA7, which is `ğ`, and four of them shipped in draft v3 rendering as
`ğ4`/`ğ5`/`ğ2`. Use `\S\ref{...}`, never a pasted `§`. Note the second check greps the
**combining breve** — `pdftotext` decomposes `ğ`, so grepping the precomposed character finds
nothing and false-passes.

**`refs.bib` must stay stripped of `note`/`file` fields.** Those are the annotations from
`../papers/references.bib`, and they contain raw `_` and `%`, which halt the engine while
building `main.bbl`. If you re-extract entries from the master bibliography, strip both
fields again.

### Current page count — 6 pp, at the limit

**Measured on v4 (2026-08-18), not estimated.** `main.pdf` is **13 pages**: body §1–§7 filling
p. 1–**6** exactly, references beginning at the top of p. 7, appendices **A–O** on p. 7–13. The
venue allows 3–6 pp of main text with the appendix excluded, so the body is **compliant at 6 pp**,
with zero spare lines.

> **Appendix letters move whenever a section is added — never cite them by letter in prose.**
> As of draft v3 they are: **A** training mixtures, **B** reimplementation fidelity + determinism
> floor, **C** the paper-literal negative construction, **D** dose response, **E** limitations,
> **G** measured training budget, **H** scoring quantities, **I** the five transforms, **J**–**M**
> per-condition and criterion tables, **N** seeds, **O** JavaScript. All in-document
> cross-references are `\ref` and track automatically; prose elsewhere in the repo that names a
> letter is what goes stale.

**There is no slack, and both recent rounds proved it.** The v3 additions ran 17 lines over
(~6 recovered by compressing new prose, 11 by moving Table 1 to the appendix). The v4 reframe ran
11 lines over (~8 by compressing new prose, 3 by deleting a mechanism sentence that had ended up
stated three times in §1). **Compile before believing any body addition fits.**

Measured page-buying options, cheapest first:

- **Look for your own repetition before cutting anything.** Both rounds ended by finding a
  restatement rather than by sacrificing content. It is the first place to look, not the last.
- **Table 1 (arms) → appendix: applied in v3.** ~8–11 lines. The arms are re-explained in prose
  where used, so the cost is a flip to Appendix A for the map.
- **Demoting a body paragraph to a footnote: does not work.** ~8 lines of body become ~5 at
  footnote size, not enough to cross a page boundary.
- Untried: Table 5 → appendix, which is self-defeating since §5 argues from it.
- **Spent.** §1's contributions paragraph is gone — v4 replaced it with the general test, which
  is now the contribution and must not be cut for pages.

Do **not** buy pages back by cutting §5's cost discussion or the CI-in-sentence convention below.

Cuts applied earlier and retained:

1. ~~§7's *Prompting does not rescue what tuning removed*~~ → **folded** into the
   prompt-insensitivity paragraph.
2. ~~§10's *Auxiliary pool ratio* and *Seeds* bullets~~ → **one sentence each**.
3. ~~§7's criterion paragraph~~ → **compressed**; the appendix carries the table.
4. ~~§2's *Fidelity of the CFT reimplementation* paragraph~~ → **moved to the appendix**. As of v3
   a two-sentence version of its core argument is back in the body, in §4's closing paragraph,
   which is where the "you tested a strawman" objection actually lands.

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

Everything this section used to list has run. The four 08-12 evals are folded in (dose ladder is
Fig. 1, JavaScript is §3 + Appendix O, strategy sweep Appendix L, seeds Appendix N), on 2026-08-17
the two HumanEval+ gaps plus **MBPP+ across all seven 7B arms** landed, and on 2026-08-18 the
**paper-literal `clean_mutant` control** (Appendix C) closed the last promised-but-unrun item.

What remains is mechanical:

| | item | where it goes |
|---|---|---|
| 1 | Venue style file, anonymisation, OpenReview checklist | before the Aug 28 freeze |
| 2 | Optional: **MBPP+ at 1.5B** | would say whether "~5 pts regardless of mixture" is scale-general. The 1.5B HumanEval+ column behaves quite differently, where `sft` is the worst arm. Not a dependency. |
| 3 | Optional: retrofit `per_task` onto the HumanEval+ path | would let the two probes be paired-tested against each other. Known debt; not for this deadline. |

Compute as of 2026-08-17 evening: all four A6000s idle, queue empty, `allowed_gpus: [0,1,2,3]`,
`gpu_budget: 4`. The modularity grid that used to gate this thread drained at 07:03 UTC. Nothing
needed `--priority 5`.

```bash
python scripts/srh/26_enqueue_forgetting.py --preset mbpp-7b --suite mbpp          # dry run
python scripts/srh/26_enqueue_forgetting.py --preset mbpp-7b --suite mbpp --write  # enqueue
```

Manual invocation of `obtune.forgetting` needs **both** `PYTHONPATH=src` and the conda env's
`bin` on `PATH` — vLLM's flashinfer sampler JIT-compiles on first use and shells out to `ninja`.
Without it, startup dies as `RuntimeError: Engine core initialization failed` with the real cause
nine frames down. The scheduler's workers set both, so queued jobs are unaffected.

## Draft conventions worth preserving through edits

- Every strong claim carries its CI **in the sentence**, not in a footnote.
- "Free" is scoped to training budget everywhere it appears, and the HumanEval+ cost is in
  the body (§8), not buried in limitations.
- The source paper *declares* Bidirectional Fine-Tuning and reports no number for it. Do
  not weaken this to "never ran the baseline" — it is factually wrong and the authors may
  review this submission.
- **Keep the tone diagnostic, not prosecutorial.** §1 says of CFT's two-things-at-once design
  that "it is not careless, it is what almost any auxiliary-task method looks like", and the
  conclusion says explicitly that we do **not** claim every auxiliary-task result on paired data
  is a directional artifact. Both sentences are load-bearing for the reframe and for the fact
  that Nikiema et al. may review this.
- **§1's general test is the contribution, not a summary.** It replaced the old contributions
  paragraph: *for any method that adds instances to paired training data, train the arm that
  supplies the same directional content and none of the method.* The reason it is more than
  advice is that the ablation arm is also the remedy, so running it pays for itself either way.
  Do not cut it for pages; cut around it.
- **The mechanism is stated once.** "Reading a pair backwards is already a reverse example"
  appeared three times in §1 after the reframe and cost three lines. It belongs in the opening
  paragraph; the habitat and test paragraphs should assume it.
- The CFT reimplementation is defended **in the body**, in §4's closing paragraph, beside the
  replication failure it qualifies. It lived only in the appendix through v2, which is the one
  review that could have sunk the paper. A fuller §2 version was written and reverted on the page
  limit; if space ever appears, §2 is the better home.
- The general-ability cost is stated against **two** probes, and the contaminated one is labelled
  as such. Do not quote the HumanEval+ column against the untouched model on its own: 74 of its
  164 problems are in the training split, which is what made forward-only tuning look free.
