"""RQ1 merge ablation: does the clean-code gain need the L0 specialist, or diversity of view?

Four merges, identical in operator (DARE-TIES), density (0.5), weights (uniform) and rank (32),
differing only in INGREDIENTS:

  struct   S1+S2                      2 specialists, one semantic view (structure)
  ident    L1b+L1r+L2                 3 specialists, one semantic view (identifiers)
  nol0     L1b+L1r+L2+S1+S2           5 specialists, both views, no clean-code specialist
  6-way    L0+L1b+L1r+L2+S1+S2        the paper's merge

Two questions, answerable by comparing columns:
  * does removing L0 remove the clean-code gain?          nol0 vs 6-way on L0
  * does diversity of view beat number of adapters?       struct vs ident vs nol0

Use --unfiltered to retain every available evaluation cell regardless of format-failure rate.
Missing raw cells then stop generation before any paper files are written.

Everything is reported against the untuned model's L0 accuracy, as Table 4 is, and with paired
program-clustered bootstrap CIs for the two contrasts that matter.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

MODELS = ["codellama-7b","codellama-13b","llama31-8b","granite31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B",
        "llama31-8b":"Llama-3.1-8B","granite31-8b":"Granite-3.1-8B"}
ABL  = ["mergeablate_generic"]; ABLB = ["mergeablate_inverse"]
FULL = ["panel_core","composite_generic","composite_depth","f2_divergence","merge_panel",
        "mole_generic","rq2_generic"]
BWD  = ["inverse_1shot","inverse_generic"]
ARMS = [("struct","merge_struct",ABL,"S1+S2"),("ident","merge_ident",ABL,"L1b+L1r+L2"),
        ("no-L0","merge_nol0",ABL,"5 obf."),("6-way","merge_dare_ties",FULL,"all six")]
# d3/d4 exist in the FORWARD ablation phase only; the backward config carries 16 conditions
# and none of them is a depth-3 stack, so those rows render as `--` under backward. That is a
# real gap in the eval, not a reporting choice, and showing it beats omitting the group.
GROUPS = [("L0", ["L0"]), ("singles", ["L1b","L1r","L2","S1","S2"]),
          ("d2 seen", ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"]),
          ("d3 seen", ["C3_L1r_S3_S4","C3_S1_S3_S4","C3_L1r_S1_S4"]),
          ("d4 seen", ["C4_L1r_S1_S3_S4"]),
          ("unseen", ["X1","C_L1r_X1","C_X1_S1","C_S2_X1"])]

UNFILTERED = "--unfiltered" in sys.argv

def pool(ph, m, arm, cs):
    fr=[d for d in (load_cell(ph,m,arm,c) for c in cs) if d is not None and (UNFILTERED or d.format_fail.mean()<=0.25)]
    if UNFILTERED and len(fr) != len(cs):
        raise FileNotFoundError(f"Missing raw cells for {m}/{arm}: {cs}; refusing an incomplete unfiltered table")
    return pd.concat(fr) if fr else None

def acc(ph, m, arm, cs):
    d = pool(ph, m, arm, cs); return None if d is None else float(d.correct.mean())

def contrast(phA, phB, m, a, b, cs, n=2000):
    A, B = pool(phA,m,a,cs), pool(phB,m,b,cs)
    if A is None or B is None: return None
    ps = sorted(set(A.snippet_id) & set(B.snippet_id))
    if not ps: return None
    ga = {p:g.correct.to_numpy(float) for p,g in A.groupby("snippet_id") if p in ps}
    gb = {p:g.correct.to_numpy(float) for p,g in B.groupby("snippet_id") if p in ps}
    pt = (np.concatenate([ga[p] for p in ps]).mean()-np.concatenate([gb[p] for p in ps]).mean())*100
    rng = np.random.default_rng(17); idx = np.arange(len(ps))
    dr = [(np.concatenate([ga[ps[j]] for j in pk]).mean()-np.concatenate([gb[ps[j]] for j in pk]).mean())*100
          for pk in (rng.choice(idx,len(ps),True) for _ in range(n))]
    lo,hi = np.percentile(dr,[2.5,97.5]); return pt,lo,hi

def _completeness_guard():
    """Refuse to report on a phase whose eval is still running.

    Reading mergeablate_generic mid-write produced a 20-point spread on CodeLlama-7B's unseen-family
    row that vanished once the remaining cells landed: arms had different numbers of readable
    conditions at the moment of reading, so the group means averaged different condition sets. A
    partially written phase looks exactly like a real effect.
    """
    import subprocess
    try:
        q = subprocess.run(["squeue","-h","-u",__import__("os").environ.get("USER",""),"-o","%j"],
                           capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return
    live = [l.strip() for l in q.split("\n") if l.strip().startswith("ev_mergeablate_")]
    if live:
        print("WARNING: these ablation evals are still running; their rows are masked:",
              file=__import__("sys").stderr)
        for l in sorted(live): print("   ", l, file=__import__("sys").stderr)
        if "--force" not in __import__("sys").argv:
            print("    Re-run when the queue is clear, or pass --force to read the rest.",
                  file=__import__("sys").stderr)
            raise SystemExit(2)
    return live


def _is_live(live, tag, model):
    """True if this model's eval for this direction is still writing cells.

    Matching is prefix-tolerant in both directions because squeue truncates long job
    names, and a truncated name that silently failed to match would reintroduce exactly
    the mid-write artefact this guard exists to prevent.
    """
    d = {"forward": "fwd", "backward": "bwd"}[tag]
    want = f"ev_mergeablate_{d}_{model}"
    return any(j.startswith(want) or want.startswith(j) for j in live)


def _tex(out):
    """The ablation as one table: clean code (`L0`) and the depth-3 seen stacks, both directions.

    L0 is the row the ablation was designed around (the clean-code reference the whole paper
    compares to). The depth-3 block was added 2026-09-25, once the backward d3 cells existed
    (A3's gap): it is where the two directions part -- forward, the two-specialist structural
    merge is at or above the six-way; backward, breadth wins -- and putting both directions on
    one line is what makes that asymmetry legible. The other groups are in the JSON.
    """
    import decimal
    cols = ["base", "struct", "ident", "no-L0", "6-way"]
    note = (r"No cells are excluded by format-failure rate." if UNFILTERED else
            r"\texttt{--}: every cell of that arm exceeded the 0.25 format gate.")
    pct = lambda v: r"\texttt{--}" if v is None else str(int(decimal.Decimal(str(v)).quantize(
        decimal.Decimal("1"), rounding=decimal.ROUND_HALF_UP)))
    L = [r"% GENERATED by scripts/analysis/76_merge_ablation.py -- do not edit by hand.",
         r"\begin{table}[t]", r"\centering\small\setlength{\tabcolsep}{3.5pt}",
         r"\caption{\textbf{Merge ingredient ablation.} Accuracy as a percentage of the untuned "
         r"model's clean-code accuracy on the same programs, on clean code (\texttt{L0}) and pooled "
         r"over the three seen depth-3 stacks. All four merges use DARE-TIES at identical density, "
         r"weights and rank and differ only in their specialists: \emph{struct} \texttt{S1+S2}, "
         r"\emph{ident} \texttt{L1b+L1r+L2}, \emph{no-L0} the five obfuscation specialists, "
         r"\emph{6-way} the default merge. Forward on \texttt{L0}, every \emph{no-L0}$-$\emph{6-way} "
         r"interval contains zero. " + note + "}",
         r"\label{tab:ablation}",
         r"\begin{tabular}{@{}ll" + "r"*len(cols) + "r"*len(cols) + r"@{}}", r"\toprule",
         r" & & \multicolumn{5}{c}{\textbf{forward}} & \multicolumn{5}{c}{\textbf{backward}} \\",
         r"\cmidrule(lr){3-7}\cmidrule(lr){8-12}",
         "model & test & " + " & ".join(cols) + " & " + " & ".join(cols) + r" \\",
         r"\midrule"]
    for m in MODELS:
        for gi, (grp, lab) in enumerate((("L0", r"\texttt{L0}"), ("d3 seen", "depth 3"))):
            cells = [NICE[m] if gi == 0 else "", lab]
            for tag in ("forward", "backward"):
                g = (out.get(m, {}).get(tag) or {}).get("groups", {}).get(grp)
                cells += [pct(None if not g else g.get(c)) for c in cols]
            L.append(" & ".join(cells) + r" \\")
        if m != MODELS[-1]:
            L.append(r"\addlinespace[2pt]")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    # paper/final/ is the authoritative draft; router_merger/ \input's the same file.
    targets = [ROOT/"paper/final/tables/merge_ablation.tex"]
    if not UNFILTERED:
        targets.append(ROOT/"paper/router_merger/tables/merge_ablation.tex")
    for f in targets:
        f.write_text("\n".join(L) + "\n")
        print(f"wrote {f}")


def _fmt_table(out, live, tag, ab_ph, full_ph):
    """Format-failure rate per arm.

    On the backward task the narrow merges are removed from the means by the >0.25
    format gate rather than by being absent, so a table of blanks hides the actual
    result: breadth of ingredients protects the output format. Report it explicitly.
    """
    all_cs = [c for _, cs in GROUPS for c in cs]
    print(f"{tag} format-failure rate (cells gated out of {len(all_cs)} at ff>0.25)\n")
    arms = [("base", "base", ab_ph)] + [(n, a, (ab_ph if ph is ABL else full_ph))
                                        for n, a, ph, _ in ARMS]
    print(f"{'model':15s} " + " ".join(f"{n:>14s}" for n, _, _ in arms))
    for m in MODELS:
        if _is_live(live, tag, m):
            print(f"{m:15s} (eval still running - masked)")
            continue
        row, rec = [], {}
        for nm, arm, ph in arms:
            ff = [d.format_fail.mean() for d in
                  (load_cell(ph, m, arm, c) for c in all_cs) if d is not None]
            if not ff:
                row.append(f"{'--':>14s}"); rec[nm] = None; continue
            mean = sum(ff) / len(ff); gated = sum(1 for x in ff if x > 0.25)
            rec[nm] = dict(mean_ff=round(mean, 3), gated=gated, cells=len(ff))
            row.append(f"{mean:11.2f} /{gated:2d}")
        out.setdefault(m, {}).setdefault(tag, {})["format_fail"] = rec
        print(f"{m:15s} " + " ".join(row))
    print()


def _report(out, live, tag, ab_ph, full_ph):
    """One direction's table + contrasts. `ab_ph` holds the three ablation merges,
    `full_ph` the paper's six-way merge and the untuned baseline."""
    arms = [(n, a, (ab_ph if ph is ABL else full_ph), d) for n, a, ph, d in ARMS]
    print(f"{tag}, % of the untuned model's clean-code accuracy\n")
    print(f"{'model':15s} {'group':9s} {'base':>6s} " + " ".join(f"{n:>7s}" for n, _, _, _ in arms))
    seen = []
    for m in MODELS:
        if _is_live(live, tag, m):
            print(f"{m:15s} (eval still running - masked)")
            out.setdefault(m, {})[tag] = {"incomplete": True}
            continue
        ref = acc(ab_ph + full_ph, m, "base", ["L0"])
        if not ref:
            print(f"{m:15s} (no readable L0 reference)")
            continue
        seen.append(m)
        rec_m = out.setdefault(m, {}).setdefault(tag, {})
        rec_m["ref_L0"] = round(ref, 4)
        rec_m["groups"] = {}
        for g, cs in GROUPS:
            row, rec = [], {}
            b = acc(ab_ph + full_ph, m, "base", cs)
            row.append("   --  " if b is None else f"{b/ref*100:5.0f}%")
            # Two decimals, not one: _tex formats these to whole percent, and a value
            # stored as 110.5 lands on Python's banker's rounding and prints 110 while
            # the console, formatting the unrounded float, prints 111.
            rec["base"] = None if b is None else round(b/ref*100, 2)
            for nm, arm, ph, _ in arms:
                a = acc(ph, m, arm, cs)
                rec[nm] = None if a is None else round(a/ref*100, 2)
                row.append("   --  " if a is None else f"{a/ref*100:6.0f}%")
            rec_m["groups"][g] = rec
            print(f"{m:15s} {g:9s} " + " ".join(row))
        print()
    print("paired contrasts (95% CI, program-clustered, 2000 resamples)\n")
    # The third column is the depth result. At L0 the four ingredient sets are
    # indistinguishable; at depth 3 the two-specialist STRUCTURAL merge beats the six-way on
    # every model. Reported here because a table of group means shows the gap but not whether
    # it survives a paired interval.
    D3 = ["C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4"]
    print(f"{'model':15s} {'no-L0 - 6-way on L0':>26s} {'struct - no-L0 on L0':>26s}"
          + (f" {'struct - 6-way @ d3':>26s}" if tag == "forward" else ""))
    f = lambda r: "          --          " if r is None else \
        f"{r[0]:+6.2f} [{r[1]:+5.1f},{r[2]:+5.1f}]{'*' if (r[1]>0)==(r[2]>0) else ' '}"
    for m in seen:
        c1 = contrast(ab_ph, full_ph, m, "merge_nol0", "merge_dare_ties", ["L0"])
        c2 = contrast(ab_ph, ab_ph, m, "merge_struct", "merge_nol0", ["L0"])
        cr = out[m][tag].setdefault("contrasts", {})
        for k, r in (("nol0_minus_6way_L0", c1), ("struct_minus_nol0_L0", c2)):
            cr[k] = None if r is None else dict(delta=round(r[0], 2), lo=round(r[1], 2), hi=round(r[2], 2))
        line = f"{m:15s} {f(c1):>26s} {f(c2):>26s}"
        if tag == "forward":
            c3 = contrast(ab_ph, full_ph, m, "merge_struct", "merge_dare_ties", D3)
            cr["struct_minus_6way_d3"] = None if c3 is None else dict(
                delta=round(c3[0], 2), lo=round(c3[1], 2), hi=round(c3[2], 2))
            line += f" {f(c3):>26s}"
        print(line)
    print()


def main():
    live = _completeness_guard() or []
    out = {}
    _report(out, live, "forward", ABL, FULL)
    print("=" * 78 + "\n")
    _report(out, live, "backward", ABLB, BWD)
    _fmt_table(out, live, "backward", ABLB, BWD)
    _tex(out)
    name = "merge_ablation_unfiltered.json" if UNFILTERED else "merge_ablation.json"
    (ROOT/"results/analysis/pipeline"/name).write_text(json.dumps(out, indent=2))
    print(f"wrote results/analysis/pipeline/{name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
