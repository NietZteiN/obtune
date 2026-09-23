# 2026-09-23 — The delivered "final" paper did not build; pre-registration section added, A5/B7/B8 ported into it

**Thread:** writeup · **Prompted by:** user — "update the paper (the final version I gave you) with
the original checklist of things that we wanted to do" · **Related:**
[`2026-09-22_a5-b7-b8-into-the-paper-and-the-noise-floor.md`](2026-09-22_a5-b7-b8-into-the-paper-and-the-noise-floor.md),
[`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md)

## Two things were wrong before any content could be added

**1. I had been editing a different paper.** `paper/final.zip` (uploaded by the user
2026-09-20 20:45, commit `55d98ae`) is a distinct revision from `paper/router_merger/`, not a copy
of it: it inputs `intro-3`, `background-2`, `setup` and a single `appendix` where router_merger
uses `intro-2`, `background`, `evaluation` and four appendices, and its `results.tex` differs by
1,156 lines. It was also never extracted — it existed only as a zip, so nothing could build or edit
it. Extracted to `paper/final/`. **The 09-22 A5/B7/B8 work went into `router_merger/` and had to be
ported.**

**2. The delivered final version did not compile.** `sections/results.tex` uses `\FloatBarrier`
and no `\usepackage{placeins}` is loaded. Fixed by adding it. Two false leads worth recording
because both looked right: the `takeaway` environment appeared undefined (a commented-out
`%\usepackage[most]{tcolorbox}` sits right above it) but was in fact already defined at line 196,
and re-adding the package raised `Option clash for package tcolorbox` because `[skins]` is loaded
at line 105. The missing package was the only real fault. **An earlier "exit code 0" on this build
was my shell pipeline's status, not tectonic's — the baseline had been failing all along.**

## The pre-registration section

`sections/prereg.tex`, `\input` before `threats`. It reports `docs/CHECKLIST.md` §1 — the ledger as
registered 2026-08-05, before the main grids — against what the campaign actually determined. Every
verdict is quoted from the dated log entry that decided it; **no row was given a plausible
outcome**. Sources: `log/pilot/README.md` (H1a-trainable, H1a, H1c), `log/attention/README.md`
(H3-causal via A2; and A4, which is what H3 needed), `continuation/00_STATE.md` §RQ2 (H2a dispatch
1.000; H2d's −3.13 cost against +2.47 contribution), `log/human-align/README.md` (HA1).

Twelve rows: 4 supported, 3 refuted, 1 retired, 1 inconclusive, 1 split, 1 partial, **2 never
resolved**. The two `n/r` rows are the point of including the table at all:

* **H3** — "anchoring shift predicts which transfers succeed" — needed a shift-vs-transfer
  regression across all system × condition cells. `log/attention/README.md` row A4 records it as
  **open, never run**. What exists is the mechanism it presupposed (re-anchoring is real and
  causal), which supports the mechanism and not the predictive claim. The paper now says so.
* **HA1** — human alignment — only the untuned correlation was read (ρ = +0.132 [−0.140, +0.381]);
  the pre/post change the hypothesis was about was never measured.

The original discriminator's fate is also stated plainly: **H1c was retired within a day of the
pilot** because a clean-code adapter reached the held-out family at least as well as an
obfuscation-trained one (0.414 vs 0.384), and its control-relative replacement H1c-rev was refuted
(−3.0 [−10.5, +3.9]). That is why every claim in the paper is stated against a clean-code control.
The modularity rows (H2b, H2d) were registered as positive predictions and came back negative,
which is the ancestry of the present RQ2.

## Ported from router_merger into final

| item | lands in | table |
|---|---|---|
| B8 seed noise floor | `setup.tex`, Measurement | `tab:seednoise` |
| A5 operator ablation | `merging.tex`, after *Merge operator* | `tab:mergeop` |
| B7 deployment cost | `alternatives.tex`, after *Router* | `tab:deploycost` |

`final/` had no `tables/` directory — its tables are inlined — so one was created and the three
generated files copied in. They remain generated artefacts: `82_merge_operator.py::_tex`,
`83_seed_variance.py::_tex`, `80_deployment_cost.py --tex`.

**The 09-22 seed-floor rescoping does NOT carry over.** It rewrote a claim ordering the router
above the merge on the held-out family by +0.96 to +2.75 points; `final/results.tex` makes no such
claim, so the floor enters here as a measurement convention rather than as a correction. Its RQ
takeaways were read against the floor and none of them turns on a sub-floor difference.

## Verification

`envs/tex/bin/tectonic` builds `paper/final/fse27.pdf` at exit 0, 29 pages. All five new labels
resolve in the `.aux` (`sec:prereg`, `tab:prereg`, `tab:seednoise`, `tab:mergeop`, `tab:deploycost`).
`\label{sec:threats}` was added because nothing defined it. Remaining undefined, all pre-existing
and none introduced here: citations `roundy2013packers`, `fewshot`, `distillation`,
`hendrycks2021apps`, and a `tab:main` reference in `appendix.tex`.

## Open

No clean page-count baseline: the delivered source never built, so "29 pages" has nothing to be
compared against. If the venue limit binds, the pre-registration table is the compressible part.
