#!/usr/bin/env python
"""MASTER_REPORT.md §2.2b — the whole-panel table for the CodeLlama/Llama era. NO H1 READ.

§2.2 is the same thing for the frozen Qwen panel, and it is Qwen-only by a rule stated in its own
preamble: 7B roughly doubles accuracy on every condition, so one 7B row in a 1.5B table would be a
model effect wearing a system's name. That rule is right, which is why this is a SEPARATE table
rather than more rows in that one — and why the models here are blocked, not interleaved.

H1: cells that already exist are re-aggregated and never re-read. CLAUDE.md §3.2 rule 3 counts reads
of `data/quarantine/`; re-tabulating a number a logged read already produced spends no budget. The
live held-out column is **X1** (36 systems against H1's 14), so X1 is what the summary column shows.

ELIGIBILITY, and the first draft of this script got it wrong in a way worth recording. Selection was
"largest n, then newest", which silently picked `inverse_generic` for `tuned_L0__L0` — the
**input-prediction** task (RQ5'), a different task entirely, whose cell happens to have one more row
(1,671 vs 1,670). `tuned_L0` on `L0` came out as 0.324 instead of 0.429. Three filters now apply
before any selection, each for a stated reason:

  * **prompt_id must not be an inverse prompt.** The task is identified by the prompt, not the phase.
    Oracle and ICL prompts stay in — those are different *prompting* of the same forward task.
  * **`selfcons_generic` is excluded** — it samples at T = 0.7, and §26 excludes it for the same reason.
  * **`*_testset` phases are excluded** from the Python panel — a different grid (40 programs against
    557), which is the mistake §2.2's `grid` warning exists to prevent.
  * **`mole_generic` is used only for `mole_*` systems**, matching §2.2's documented engine rule: the
    hf-mole mixture engine reads differently from vLLM, and mixtures must be read through it.

Selection among what survives: **largest n, then newest run_ts**. Disagreements above 0.5 pts are
counted and reported under the table, the way §2.2 does it. `n_prog` is shown for every row — the program
count behind the five single-transform columns, i.e. behind `mean single` — because a mean over a
different program set is the other way these tables mislead (RQ_SUMMARY §4.1). The `X1`, `H1` and
composite cells sit on their own, usually smaller, program sets; that is why they are separate
columns and not folded into one number.

    python scripts/analysis/49_master_panel_table.py --out results/analysis/master_panel_table.md
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CELLS = ROOT / "results" / "cells"

SINGLE = ["L1b", "L1r", "L2", "S1", "S2"]
CORE = ["L0"] + SINGLE + ["X1", "H1"]
COMP = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
EXTRA = ["S3", "S4", "X1m", "X1s", "X2", "Y2",
         "C3_L1r_S1_S4", "C3_L1r_S3_S4", "C3_S1_S3_S4", "C4_L1r_S1_S3_S4",
         "T_L0", "T_L1", "T_L1b", "T_L2", "T_L3"]

#: name prefix -> family, in priority order. Mirrors §1's "approaches tried" taxonomy.
FAMILIES = [
    (r"^base$|^base_trace$", "Reference — untuned"),
    (r"^formatonly", "Reference — format floor"),
    (r"^tuned_L0(_s\d+)?$", "Reference — clean-code control"),
    (r"^tuned_L0_", "Clean-code control variants"),
    (r"^tuned_(L1b|L1r|L2|S1|S2|S3|S4)", "Per-condition specialists"),
    (r"^tuned_(X1|X1m|X1s|X2|Y2)", "Family-exposure specialists (X1 and siblings)"),
    (r"^x1_", "Family-exposure variants"),
    (r"^cons_|^align_", "Objectives — consistency / alignment"),
    (r"^curr", "Objectives — curriculum"),
    (r"^neg_", "Objectives — negatives / unlikelihood"),
    (r"^mono_", "Monolithic breadth"),
    (r"^loto_", "Leave-one-transform-out"),
    (r"^(merge_|l0merge_|sweep_|crossseed_|residual_)", "Task-vector merges"),
    (r"^mole_|^router", "Routing / MoLE mixtures"),
    (r"^icl_|^oracle_", "Zero-training — ICL and oracle prompting"),
    (r"^norm_", "Zero-training — symbolic normalization"),
    (r"^trace", "Execution-trace SFT"),
    (r"^ctl_|^rank", "Rank / capacity controls"),
]


def family(name: str) -> str:
    for pat, fam in FAMILIES:
        if re.search(pat, name):
            return fam
    return "Other"


def settings_of(df: pd.DataFrame) -> str:
    """Derived from the trial rows, never hand-written: the adapter directory already encodes
    rank, seed and objective, and `adapter_arch` says what kind of system it is."""
    arch = str(df["adapter_arch"].iloc[0])
    aid = df["adapter_id"].iloc[0]
    if not aid or str(aid) == "None":
        return "no adapter" if arch == "none" else arch
    d = Path(str(aid)).parent.name
    root = "objectives" if "adapters_objectives" in str(aid) else \
           "saturation" if "adapters_saturation" in str(aid) else \
           "formatonly" if "adapters_formatonly" in str(aid) else ""
    return f"{d}" + (f" · {root}" if root else "")


def collect() -> tuple[dict, collections.Counter]:
    panel: dict = collections.defaultdict(dict)
    dupes = collections.Counter()
    for p in CELLS.rglob("trials.parquet"):
        parts = p.relative_to(CELLS).parts
        if len(parts) < 4 or parts[0].startswith("_"):
            continue
        phase, model, lang, cell = parts[0], parts[1], parts[2], parts[3]
        if "qwen" in model:
            continue
        system, _, cond = cell.rpartition("__")
        if not cond:
            continue
        if phase == "selfcons_generic" or phase.endswith("_testset"):
            continue
        if phase == "mole_generic" and not system.startswith("mole_"):
            continue
        df = pd.read_parquet(p, columns=["correct", "snippet_id", "run_ts", "prompt_id",
                                         "adapter_id", "adapter_arch"])
        if str(df["prompt_id"].iloc[0]).startswith("inverse"):
            continue
        rec = {"acc": float(df["correct"].mean()), "n": len(df),
               "n_prog": int(df["snippet_id"].nunique()),
               "ts": str(df["run_ts"].iloc[0]), "phase": phase,
               "settings": settings_of(df)}
        key = (model, lang, system)
        prev = panel[key].get(cond)
        if prev is None:
            panel[key][cond] = rec
        else:
            if abs(prev["acc"] - rec["acc"]) > 0.005:
                dupes[(model, lang)] += 1
            # largest n, then newest
            if (rec["n"], rec["ts"]) > (prev["n"], prev["ts"]):
                panel[key][cond] = rec
    return panel, dupes


def fmt(v) -> str:
    return f"{v['acc']:.3f}" if v else "—"


def mean_of(row: dict, cols: list[str]) -> str:
    vals = [row[c]["acc"] for c in cols if c in row]
    return f"**{sum(vals) / len(vals):.3f}**" if len(vals) == len(cols) else ""


def render(panel: dict, model: str, lang: str, conds: list[str], out: list[str]) -> list[tuple]:
    rows = [(s, r) for (m, l, s), r in panel.items() if m == model and l == lang]
    if not rows:
        return []
    byfam = collections.defaultdict(list)
    for s, r in rows:
        byfam[family(s)].append((s, r))
    hdr = (["system", "settings", "n_prog", "**mean single**", "**unseen (X1)**", "**mean composed**"]
           + conds)
    out.append("| " + " | ".join(hdr) + " |")
    out.append("|" + "---|" * len(hdr))
    summary = []
    order = [f for _, f in FAMILIES] + ["Other"]
    seen = set()
    for fam in order:
        if fam in seen or fam not in byfam:
            continue
        seen.add(fam)
        out.append(f"| **{fam}** |" + " |" * len(hdr[1:]))
        best = None
        for s, r in sorted(byfam[fam]):
            ms, mc = mean_of(r, SINGLE), mean_of(r, COMP)
            x1 = f"**{r['X1']['acc']:.3f}**" if "X1" in r else ""
            npr = sorted({v["n_prog"] for c, v in r.items() if c in SINGLE}) or \
                  sorted({v["n_prog"] for v in r.values()})
            npr_s = str(npr[0]) if len(npr) == 1 else f"{npr[0]}–{npr[-1]}"
            out.append("| `" + s + "` | " + (r[next(iter(r))]["settings"]) + " | " + npr_s + " | "
                       + " | ".join([ms, x1, mc] + [fmt(r.get(c)) for c in conds]) + " |")
            if ms and (best is None or float(ms.strip("*")) > best[1]):
                best = ((s, r), float(ms.strip("*")), ms, x1, mc)
        if best:
            summary.append((fam, best[0][0], best[0][1], best[2], best[3], best[4]))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--family-table", metavar="PATH",
                    help="also emit the compact APPROACH x CONDITION table, one block per model "
                         "(docs/RQ_SUMMARY.md 7)")
    a = ap.parse_args()
    panel, dupes = collect()
    out: list[str] = []

    blocks = [("codellama-7b", "python", CORE + COMP, "CodeLlama-7b · Python — the live panel"),
              ("codellama-13b", "python", CORE + COMP, "CodeLlama-13b · Python"),
              ("codellama-34b", "python", CORE + COMP, "CodeLlama-34b · Python"),
              ("llama31-8b", "python", CORE + COMP, "Llama-3.1-8B · Python — the cross-family replicate"),
              ("codellama-7b", "javascript", ["L0"] + SINGLE + COMP,
               "CodeLlama-7b · JavaScript — the cross-language grid (E13)")]
    summaries = {}
    for model, lang, conds, title in blocks:
        n = sum(1 for (m, l, _) in panel if m == model and l == lang)
        if not n:
            continue
        out.append(f"\n**{title}** — {n} systems.\n")
        summaries[title] = render(panel, model, lang, conds, out)

    # sparse conditions, 7B python only
    out.append("\n**Conditions with only a handful of rows** (CodeLlama-7b · Python). Kept out of the "
               "table above so it does not become mostly `—`.\n")
    hdr = ["system"] + EXTRA
    out.append("| " + " | ".join(hdr) + " |")
    out.append("|" + "---|" * len(hdr))
    for (m, l, s), r in sorted(panel.items()):
        if (m, l) != ("codellama-7b", "python"):
            continue
        if any(c in r for c in EXTRA):
            out.append("| `" + s + "` | " + " | ".join(fmt(r.get(c)) for c in EXTRA) + " |")

    out.append("\n**Best row per family, by `mean single`.**\n")
    for title, summ in summaries.items():
        if not summ:
            continue
        out.append(f"\n*{title}*\n")
        out.append("| family | best row | mean single | unseen (X1) | mean composed |")
        out.append("|---|---|---:|---:|---:|")
        for fam, s, _, ms, x1, mc in sorted(summ, key=lambda t: -float(t[3].strip("*"))):
            out.append(f"| {fam} | `{s}` | {ms} | {x1 or '—'} | {mc or '—'} |")

    out.append(f"\n*Cells disagreeing by >0.5 pts across phases, resolved by largest-n-then-newest: "
               f"{dict(dupes) or 'none'}.*")
    Path(a.out).write_text("\n".join(out))
    print(f"wrote {a.out} ({len(out)} lines)")

    if a.family_table:
        fam_out: list[str] = []
        for model, lang, conds, title in blocks:
            rows = [(s_, r) for (m, l, s_), r in panel.items() if m == model and l == lang]
            if not rows:
                continue
            byfam: dict = collections.defaultdict(list)
            for s_, r in rows:
                byfam[family(s_)].append((s_, r))
            # one REPRESENTATIVE system per family: its best by mean single. Never a per-column
            # max, which would build a row out of several different systems.
            reps = []
            for fam, members in byfam.items():
                scored = [(mean_of(r, SINGLE), s_, r) for s_, r in members]
                scored = [t for t in scored if t[0]]
                if not scored:
                    continue
                # Prefer a representative that HAS the held-out read, so the column that
                # discriminates is not empty for a whole approach; among those, the best by
                # mean single. Only if no member of the family was ever read on X1 does the
                # plain best win. Stated in the caption, because it is a selection rule.
                withx1 = [t for t in scored if "X1" in t[2]]
                pool = withx1 or scored
                ms, s_, r = max(pool, key=lambda t: float(t[0].strip("*")))
                reps.append((float(ms.strip("*")), fam, s_, r))
            if not reps:
                continue
            present = [c for c in conds if any(c in r for _, _, _, r in reps)]
            fam_out.append(f"\n**{title}**\n")
            hdr = ["approach", "representative row", "mean single"] + present
            fam_out.append("| " + " | ".join(hdr) + " |")
            fam_out.append("|" + "---|" * len(hdr))
            for ms, fam, s_, r in sorted(reps, reverse=True):
                cells_ = [fmt(r.get(c)) for c in present]
                fam_out.append(f"| {fam} | `{s_}` | **{ms:.3f}** | " + " | ".join(cells_) + " |")
        Path(a.family_table).write_text("\n".join(fam_out))
        print(f"wrote {a.family_table} ({len(fam_out)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
