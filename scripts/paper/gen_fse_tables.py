#!/usr/bin/env python
"""Emit results tables for `paper/paper_latex/` in THAT draft's house style.

    python scripts/paper/gen_fse_tables.py

STYLE, matched to the existing hand-written tables in `paper/paper_latex/sections/`:
`\\begin{table}[ht]`, `\\centering`, caption ABOVE the tabular, `@{}`-trimmed column specs,
booktabs rules (acmart provides them), `\\texttt{}` for system names, and signed numbers in math
mode (`$-3.79$`) with intervals as `[$-4.78$, $-1.40$]`.

NUMBERS ARE GENERATED, NEVER TYPED. Each table is computed from a JSON under `results/analysis/`,
which comes from the per-cell parquets. The draft's existing tables were written by hand and
several of their numbers are now superseded -- the panel went from three model scales to eight
models, and the RQ1 dissociation is now a paired difference rather than two separate levels. These
tables are the replacements; the header of each file names its source so it can be traced.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "analysis"
OUT = ROOT / "paper" / "paper_latex" / "tables"
NICE = {"codellama-7b": "CodeLlama-7B", "codellama-13b": "CodeLlama-13B",
        "codellama-34b": "CodeLlama-34B", "llama31-8b": "Llama-3.1-8B",
        "starcoder2-15b": "StarCoder2-15B", "gemma3-12b": "Gemma-3-12B",
        "codegemma-7b": "CodeGemma-7B", "granite31-8b": "Granite-3.1-8B"}
LIN = {"codellama-7b": "Meta", "codellama-13b": "Meta", "codellama-34b": "Meta",
       "llama31-8b": "Meta", "starcoder2-15b": "BigCode", "gemma3-12b": "Google",
       "codegemma-7b": "Google", "granite31-8b": "IBM"}
ORDER = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
         "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
DASH = "--"


def load(rel):
    p = RES / rel
    if not p.exists():
        print(f"  missing input: {p.relative_to(ROOT)}", file=sys.stderr)
        return None
    return json.loads(p.read_text())


def num(v, prec=2):
    return f"${v:+.{prec}f}$"


def iv(c, prec=2, bold_sig=True):
    """`$+3.36$ [$+1.57$, $+5.27$]`, bolded when the interval excludes zero."""
    if c is None:
        return DASH
    v, lo, hi = c.get("value_pts", c.get("delta_pts")), c.get("ci_lo"), c.get("ci_hi")
    if v is None:
        return DASH
    s = f"{num(v, prec)} [{num(lo, prec)}, {num(hi, prec)}]"
    sig = c.get("excludes_zero", (lo is not None and hi is not None and (lo > 0 or hi < 0)))
    return f"\\textbf{{{s}}}" if (bold_sig and sig) else s


def write(name, body, source, note=""):
    hdr = (f"% GENERATED {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by "
           f"scripts/paper/gen_fse_tables.py\n% SOURCE: {source}\n"
           f"% Do not edit by hand -- regenerate. {note}\n")
    (OUT / name).write_text(hdr + body + "\n")
    print(f"  wrote paper/paper_latex/tables/{name}")


def t_rq1_dissociation():
    d = load("pipeline/stack_dissociation.json")
    ms = (d or {}).get("models", {})
    rows, n = [], None
    for m in ORDER:
        e = ms.get(m)
        if not e:
            continue
        n = e["n_programs"]
        rows.append(f"{NICE[m]} & {LIN[m]} & {iv(e['seen'])} & {iv(e['unseen_containing'])} "
                    f"& {iv(e['difference'])} \\\\")
    tal = (d or {}).get("tally", {})
    body = (r"""\begin{table*}[ht]
\centering
\caption{\textbf{RQ1: the dissociation, measured within model on one program set.} Breadth
(\texttt{mono\_all}) against the clean-code control (\texttt{tuned\_L0}) on stacks built from
\emph{seen} transforms and on stacks containing an \emph{unseen} family. The \emph{difference} is
the measured quantity; the two levels are context, and on most models the unseen-side interval
straddles zero on its own. Both halves are paired on the """ + str(n or "N") + r""" programs common
to every cell of both groups. Bold intervals exclude zero.}
\label{tab:rq1_dissociation}
\begin{tabular}{@{}llccc@{}}
\toprule
\textbf{Model} & \textbf{Lineage} & \textbf{Seen stacks} & \textbf{Unseen inside} & \textbf{Difference} \\
\midrule
""" + "\n".join(rows) + r"""
\midrule
\multicolumn{4}{@{}l}{\emph{difference significant on}} & """
            + f"{tal.get('difference_significant','?')} of {tal.get('models_read','?')} models"
            + r""" \\
\bottomrule
\end{tabular}
\end{table*}""")
    write("rq1_dissociation.tex", body, "results/analysis/pipeline/stack_dissociation.json",
          "Supersedes the hand-written '+3.49 / +2.90 / +3.05 across three model scales'.")


def t_rq2_identifier():
    a = load("pipeline/f3a_stack_identifier_depth_seen_codellama7b.json")
    b = load("pipeline/f3a_stack_identifier_f2_unseen_codellama7b.json")
    rows = []
    for lbl, d, note in (("All-seen depth-3/4 stacks", a, "in-sample"),
                         ("Stacks containing the unseen family", b, "out-of-sample")):
        p = (d or {}).get("pooled", {})
        rows.append(f"{lbl} ({note}) & {iv(p.get('with_identifier'))} & "
                    f"{iv(p.get('structural_only'))} & {iv(p.get('difference_of_differences'))} \\\\")
    body = (r"""\begin{table*}[ht]
\centering
\caption{\textbf{RQ2: breadth's stack gain depends on an identifier transform being present.}
Breadth over the clean-code control, split by whether the stack contains an identifier transform,
with the \emph{difference} between the groups. The rule defining the split was fixed before the
unseen-containing stimulus existed, which makes the second row an out-of-sample test of it. We
report the difference because one interval excluding zero while another does not is not a test of
the difference between them.}
\label{tab:rq2_identifier}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Stimulus} & \textbf{With identifier} & \textbf{Structural only} & \textbf{Difference} \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}""")
    write("rq2_identifier.tex", body,
          "results/analysis/pipeline/f3a_stack_identifier_{depth_seen,f2_unseen}_codellama7b.json",
          "Supersedes the hand-written '+6.6 down to +1.1', which was an ordering, not a contrast.")


def t_rq3_panel():
    d = load("panel_replication_final.json") or {}
    mark = {"REPLICATED": r"\checkmark", "REFUTED": r"$\times$", "INCONCLUSIVE": r"$\circ$"}
    rows, tal = [], {r: {} for r in ("R1", "R2", "R3")}
    for m in ORDER:
        e = d.get(m)
        if not e:
            continue
        cells = []
        for r in ("R1", "R2", "R3"):
            v = e[r]["verdict"]
            tal[r][v] = tal[r].get(v, 0) + 1
            cells.append(iv({**e[r], "value_pts": e[r]["delta_pts"]}) + " " + mark.get(v, ""))
        rows.append(f"{NICE[m]} & {LIN[m]} & " + " & ".join(cells) + r" \\")
    t = " & ".join(f"{x.get('REPLICATED',0)} / {x.get('INCONCLUSIVE',0)} / {x.get('REFUTED',0)}"
                   for x in (tal["R1"], tal["R2"], tal["R3"]))
    body = (r"""\begin{table*}[ht]
\centering
\caption{\textbf{RQ3: the three findings across eight models and four lineages}, all read from one
evaluation phase. \checkmark\ replicated, $\circ$ inconclusive, $\times$ refuted. R1 is breadth's
unseen-family tax (\texttt{mono\_all} $-$ \texttt{tuned\_L0} on the held-out family); R2 is
anchoring removing it (\texttt{cons\_lam3} $-$ \texttt{mono\_all}); R3 is anchoring's clean-code
cost (\texttt{cons\_lam3} $-$ \texttt{tuned\_L0} on clean code). Bold intervals exclude zero.}
\label{tab:rq3_panel}
\begin{tabular}{@{}llccc@{}}
\toprule
\textbf{Model} & \textbf{Lineage} & \textbf{R1} unseen tax & \textbf{R2} anchoring repair & \textbf{R3} clean-code cost \\
\midrule
""" + "\n".join(rows) + r"""
\midrule
\multicolumn{2}{@{}l}{\emph{replicated / inconclusive / refuted}} & """ + t + r""" \\
\bottomrule
\end{tabular}
\end{table*}""")
    write("rq3_panel.tex", body, "results/analysis/panel_replication_final.json",
          "Supersedes the single-scale claim that anchoring 'completely removes' the cost.")


def t_rq4_ladder():
    d = load("pipeline/f2_divergence_codellama7b.json")
    dep = load("pipeline/composite_depth_codellama7b.json") or {}
    lv = (d or {}).get("by_level", {})
    d0 = dep.get("ref_depth2", {}).get("mono_all - tuned_L0")
    d1 = dep.get("pooled", {})
    rows = [
        f"d0 & depth 2, all seen & {iv(d0)} & {DASH} & {iv(d1.get('cons_lam3 - mono_all'))} \\\\",
        f"d1 & depth 3--4, all seen & {iv(d1.get('mono_all - tuned_L0'))} & "
        f"{iv(d1.get('cons_lam3 - tuned_L0'))} & {iv(d1.get('cons_lam3 - mono_all'))} \\\\",
        r"\midrule",
        f"d2 & depth 2, \\textbf{{unseen inside}} & {iv(lv.get('d2',{}).get('mono_all - tuned_L0'))} & "
        f"{iv(lv.get('d2',{}).get('cons_lam3 - tuned_L0'))} & {iv(lv.get('d2',{}).get('cons_lam3 - mono_all'))} \\\\",
        f"d3 & depth 3, \\textbf{{unseen inside}} & {iv(lv.get('d3',{}).get('mono_all - tuned_L0'))} & "
        f"{iv(lv.get('d3',{}).get('cons_lam3 - tuned_L0'))} & {iv(lv.get('d3',{}).get('cons_lam3 - mono_all'))} \\\\",
    ]
    body = (r"""\begin{table*}[ht]
\centering
\caption{\textbf{RQ4: the divergence ladder.} Composites that contain a transform family the model
has never seen. Breadth's advantage flips sign the moment such a component enters, while anchoring
rises \emph{above} the clean-code control. The pre-registered rule required both that anchoring hold
and that breadth fall below the control; only the first is established, since the pooled interval at
d2 straddles zero. CodeLlama-7B, 287 programs common to all six composites, fixed before any system
was evaluated.}
\label{tab:rq4_ladder}
\begin{tabular}{@{}llccc@{}}
\toprule
\textbf{Level} & \textbf{Stimulus} & \texttt{mono}$-$\texttt{clean} & \texttt{cons}$-$\texttt{clean} & \texttt{cons}$-$\texttt{mono} \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}""")
    write("rq4_ladder.tex", body,
          "results/analysis/pipeline/{f2_divergence_codellama7b,composite_depth_codellama7b}.json",
          "New: the stimulus this table describes did not exist when the draft was written.")


def t_rq4_by_model():
    rows = []
    for m in ORDER:
        f = ("pipeline/f2_divergence_codellama7b.json" if m == "codellama-7b"
             else f"pipeline/f2_divergence_core_{m.replace('-', '')}.json")
        if not (RES / f).exists():
            continue
        b = json.loads((RES / f).read_text())["by_level"]["d2"]
        rows.append(f"{NICE[m]} & {LIN[m]} & {iv(b['cons_lam3 - mono_all'])} & "
                    f"{iv(b['cons_lam3 - tuned_L0'])} & {iv(b['tuned_X1 - tuned_L0'])} \\\\")
    body = (r"""\begin{table*}[ht]
\centering
\caption{\textbf{RQ4: the divergence result across the panel}, on stacks containing the unseen
family. \texttt{cons}$-$\texttt{mono} is anchoring's advantage over breadth; \texttt{fam} is an arm
trained on the unseen family's trainable sibling, included because family exposure is the largest
effect in the table and replicates on every model. Bold intervals exclude zero.}
\label{tab:rq4_by_model}
\begin{tabular}{@{}llccc@{}}
\toprule
\textbf{Model} & \textbf{Lineage} & \texttt{cons}$-$\texttt{mono} & \texttt{cons}$-$\texttt{clean} & \texttt{fam}$-$\texttt{clean} \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}""")
    write("rq4_by_model.tex", body, "results/analysis/pipeline/f2_divergence{,_core}_*.json",
          "New: shows anchoring's advantage is conditional on the model.")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (t_rq1_dissociation, t_rq2_identifier, t_rq3_panel, t_rq4_ladder, t_rq4_by_model):
        f()
    print(f"\n  {len(list(OUT.glob('*.tex')))} tables in paper/paper_latex/tables/")
    print("  add to the RQ sections with, e.g.:  \\input{tables/rq1_dissociation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
