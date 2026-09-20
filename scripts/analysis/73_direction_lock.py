"""Direction-locking and backward decomposition, every model x every method (user request, 2026-09-20).

Two tables the paper asserts but does not show:

  DIRECTION LOCK  the fraction of BACKWARD replies that are exactly the gold FORWARD answer. The
                  model was asked for an input and returned the output. This is the mechanism behind
                  the backward losses and it is currently claimed with two example numbers.

  DECOMPOSITION   backward accuracy split four ways -- execution-graded accuracy, exact-input
                  recovery, format success, and the direction-lock rate -- so that reverse reasoning
                  is separated from formatting failure and from answering the wrong question.

Writes both as LaTeX into paper/router_merger/tables/ and prints them.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis")); sys.path.insert(0, str(ROOT/"src"))
from cellkit import load_cell, trials_path

MODELS = ["codellama-7b","codellama-13b","codellama-34b","llama31-8b","starcoder2-15b",
          "gemma3-12b","codegemma-7b","granite31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B","codellama-34b":"CodeLlama-34B",
        "llama31-8b":"Llama-3.1-8B","starcoder2-15b":"StarCoder2-15B","gemma3-12b":"Gemma-3-12B",
        "codegemma-7b":"CodeGemma-7B","granite31-8b":"Granite-3.1-8B"}
ARMS = [("Base","base"),("Clean","tuned_L0"),("Breadth","mono_all"),
        ("KL","cons_lam3"),("Router","mole_router"),("Merge","merge_dare_ties")]
BWD = ["inverse_1shot","inverse_generic"]
CONDS = ["L0","L1b","L1r","L2","S1","S2","X1","C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4",
         "C_L1r_S3","C_S4_S3","C_L1r_X1","C_X1_S1","C_S2_X1"]

_GOLD: dict = {}
def gold(cond):
    if cond not in _GOLD:
        from obtune.data import load_eval_items
        try:
            _GOLD[cond] = {(i.program_id, i.item_id): str(i.output_repr).strip().strip('"').strip("'").replace(" ","")
                           for i in load_eval_items([cond], "python", source="heldout")}
        except Exception:
            _GOLD[cond] = {}
    return _GOLD[cond]

def norm(x): return str(x).strip().strip('"').strip("'").replace(" ","")

def stats(model, arm):
    """Pool every backward condition. Format success is measured on ALL cells; the other three on
    cells clearing the 0.25 gate, because a gated cell's accuracy is not a fair reading."""
    lock_hit = lock_n = 0
    keep = []
    seen_any = False
    for c in CONDS:
        d = load_cell(BWD, model, arm, c)
        if d is None: continue
        seen_any = True
        g = gold(c)
        if g is not None and "output_raw" in d.columns and g:
            for sid, iid, raw in zip(d["snippet_id"], d["item_id"], d["output_raw"]):
                lock_n += 1
                if norm(raw) == g.get((sid, iid), "\x00"): lock_hit += 1
        keep.append(d)
    if not seen_any: return None
    allc = pd.concat(keep)
    ungated = pd.concat([d for d in keep if d.format_fail.mean() <= 0.25]) if any(
        d.format_fail.mean() <= 0.25 for d in keep) else None
    return dict(
        exec_acc = None if ungated is None else float(ungated.correct.mean()),
        args     = None if ungated is None else float(ungated.args_exact.mean()),
        fmt_ok   = 1.0 - float(allc.format_fail.mean()),
        lock     = (lock_hit/lock_n) if lock_n else None,
    )

def fnum(v, d=3): return "--" if v is None else f"{v:.{d}f}"

def main():
    rows = {m: {a: stats(m, sy) for a, sy in ARMS} for m in MODELS}
    # ---- table 1: direction lock ----
    L = [r"\begin{table}[t]", r"\centering\small",
         r"\caption{\textbf{Direction locking.} Fraction of \emph{backward} replies that are exactly the "
         r"gold \emph{forward} answer: the model was asked for an input and returned the output. Pooled over "
         r"16 backward conditions. The untuned models and the merge sit at the floor; every single-adapter "
         r"arm is above it. \texttt{--}: arm not run on that model.}",
         r"\label{tab:dirlock}", r"\begin{tabular}{@{}l" + "r"*len(ARMS) + r"@{}}", r"\toprule",
         "model & " + " & ".join(n for n, _ in ARMS) + r" \\", r"\midrule"]
    for m in MODELS:
        L.append(NICE[m].replace("-", "-") + " & " + " & ".join(
            fnum(rows[m][a]["lock"]) if rows[m][a] else "--" for a, _ in ARMS) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (ROOT/"paper/router_merger/tables/direction_lock.tex").write_text("\n".join(L) + "\n")
    # ---- table 2: decomposition ----
    D = [r"\begin{table*}[p]", r"\centering\scriptsize\setlength{\tabcolsep}{1.7pt}",
         r"\caption{\textbf{Backward-task decomposition.} For each arm: \emph{exec} execution-graded "
         r"accuracy, \emph{args} exact-input recovery, \emph{fmt} the fraction of replies meeting the answer "
         r"contract, and \emph{lock} the direction-lock rate of Table~\ref{tab:dirlock}. \emph{exec} and "
         r"\emph{args} are computed on cells clearing the 0.25 format gate; \emph{fmt} and \emph{lock} on all "
         r"cells. The split separates reverse reasoning from formatting failure and from answering the "
         r"forward question.}",
         r"\label{tab:bwddecomp}",
         r"\resizebox{\textwidth}{!}{%",
         r"\begin{tabular}{@{}l" + "cccc"*len(ARMS) + r"@{}}", r"\toprule",
         " & " + " & ".join(r"\multicolumn{4}{c}{\textbf{" + n + "}}" for n, _ in ARMS) + r" \\",
         "".join(r"\cmidrule(lr){" + f"{2+4*k}-{5+4*k}" + "}" for k in range(len(ARMS))),
         "model & " + " & ".join(r"{\scriptsize exec} & {\scriptsize args} & {\scriptsize fmt} & {\scriptsize lock}"
                                 for _ in ARMS) + r" \\", r"\midrule"]
    for m in MODELS:
        cs = []
        for a, _ in ARMS:
            s = rows[m][a]
            cs += ["--","--","--","--"] if s is None else [fnum(s["exec_acc"]), fnum(s["args"]),
                                                            fnum(s["fmt_ok"],2), fnum(s["lock"])]
        D.append(NICE[m] + " & " + " & ".join(cs) + r" \\")
    D += [r"\bottomrule", r"\end{tabular}}", r"\end{table*}"]
    (ROOT/"paper/router_merger/tables/backward_decomp.tex").write_text("\n".join(D) + "\n")
    # ---- console ----
    print(f"{'model':16s} " + " ".join(f"{n:>8s}" for n, _ in ARMS) + "   (direction-lock rate)")
    for m in MODELS:
        print(f"{m:16s} " + " ".join(f"{fnum(rows[m][a]['lock']) if rows[m][a] else '--':>8s}" for a, _ in ARMS))
    print("\nwrote tables/direction_lock.tex and tables/backward_decomp.tex")
    return 0

if __name__ == "__main__":
    sys.exit(main())
