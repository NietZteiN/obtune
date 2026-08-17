#!/usr/bin/env python
"""Paired arm-vs-arm contrasts with cluster-bootstrap CIs.

    python scripts/srh/24_contrasts.py --run results/.../e2_factorial_qwen1.5b --factorial
    python scripts/srh/24_contrasts.py --run <dir> --contrast flip-sft --contrast cft-sft

Every strong claim in the workshop paper is a DIFFERENCE between two arms, and the tone
rules require each to carry its interval in the same sentence. This script is where those
intervals come from, so they are computed once, the same way, rather than by hand per
table.

PAIRED, not two independent rates. Both arms are scored on the same programs, so a
resample must draw a program once and take BOTH arms' trials for it. Bootstrapping the
two arms separately would ignore that pairing and inflate every interval -- which, for
the nulls this experiment turns on (`cft - sft`), is the difference between "no effect,
tightly bounded" and "no effect, but we could not have detected one".

`--factorial` additionally prints the 2x2 decomposition of the objective x data-direction
design (sft / cft / flip / cftflip) as two main effects and an interaction, which is the
form the attribution claim is actually stated in.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import GLOBAL_SEED  # noqa: E402
from obtune.paths import iter_jsonl  # noqa: E402

#: The contrasts the paper actually makes, as (a, b) meaning "a minus b".
DEFAULT_CONTRASTS = [
    ("cft", "sft"),        # does the contrastive objective do anything?
    ("flip", "cft"),       # the free swap vs the published method
    ("flip", "sft"),       # the data-direction effect
    ("cftflip", "flip"),   # does the objective add anything ON TOP of the data?
    ("cftflip", "cft"),    # the data effect, at the other level of the objective
    ("mix50", "sft"),      # the same effect at matched instances/steps/FLOPs
    ("flip", "mix50"),     # does doubling the data add anything?
    ("fwd2x", "sft"),      # compute control: forward-only at 2x the epochs
    ("sft", "base"),       # is fine-tuning below the untouched model?
    ("cft", "base"),
    ("mix50", "base"),
    ("flip", "base"),
]

METRIC = "reverse_success_strict"


def _load_report_module():
    """scripts/cft/12_report.py, imported for provenance rather than reimplemented.

    Nothing is used from it directly here (the bootstrap below is paired, which that
    module's is not), but importing it asserts the two live side by side and keeps the
    seed/resample conventions visible in one place.
    """
    path = ROOT / "scripts" / "cft" / "12_report.py"
    spec = importlib.util.spec_from_file_location("_cft_report", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def paired_delta(trials, a: str, b: str, metric: str,
                 n_boot: int, seed: int) -> dict[str, Any] | None:
    """Mean(a) - mean(b) over the programs BOTH arms were scored on, with a 95 % CI.

    Restricting to the shared program set is not cosmetic: if one arm dropped a program
    (a truncated generation, an executor timeout), an unrestricted difference compares
    two slightly different populations and charges the gap to the arm.
    """
    by_prog: dict[str, dict[str, list[float]]] = defaultdict(lambda: {a: [], b: []})
    for t in trials:
        if t["system"] in (a, b) and metric in t:
            by_prog[t["program_id"]][t["system"]].append(float(t[metric]))
    progs = sorted(p for p, d in by_prog.items() if d[a] and d[b])
    if len(progs) < 2:
        return None

    def stat(sample: Sequence[str]) -> float:
        va = [v for p in sample for v in by_prog[p][a]]
        vb = [v for p in sample for v in by_prog[p][b]]
        return sum(va) / len(va) - sum(vb) / len(vb)

    point = stat(progs)
    rng = random.Random(seed)
    draws = sorted(stat([progs[rng.randrange(len(progs))] for _ in progs])
                   for _ in range(n_boot))
    lo = draws[int(0.025 * len(draws))]
    hi = draws[min(len(draws) - 1, int(0.975 * len(draws)))]
    return {
        "a": a, "b": b, "n_programs": len(progs),
        "mean_a": sum(v for p in progs for v in by_prog[p][a])
                  / sum(len(by_prog[p][a]) for p in progs),
        "mean_b": sum(v for p in progs for v in by_prog[p][b])
                  / sum(len(by_prog[p][b]) for p in progs),
        "delta": point, "ci": [lo, hi], "excludes_zero": (lo > 0) or (hi < 0),
    }


def factorial(trials, metric: str, n_boot: int, seed: int) -> dict[str, Any] | None:
    """The 2x2: contrastive objective (absent/present) x data direction (fwd/bidirectional).

    Main effects are averaged over the other factor, which is what makes them main
    effects rather than two separate simple effects. The interaction is the number that
    says whether the objective's contribution DEPENDS on having reverse data -- the only
    way "CFT does nothing" could be wrong in a way the simple contrasts would miss. All
    three are resampled on the same program draw, so they share one uncertainty model.
    """
    cells = ("sft", "cft", "flip", "cftflip")
    by_prog: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {c: [] for c in cells})
    for t in trials:
        if t["system"] in cells and metric in t:
            by_prog[t["program_id"]][t["system"]].append(float(t[metric]))
    progs = sorted(p for p, d in by_prog.items() if all(d[c] for c in cells))
    if len(progs) < 2:
        return None

    def means(sample):
        return {c: (lambda v: sum(v) / len(v))(
            [v for p in sample for v in by_prog[p][c]]) for c in cells}

    def effects(sample):
        m = means(sample)
        return {
            "data": ((m["flip"] - m["sft"]) + (m["cftflip"] - m["cft"])) / 2,
            "objective": ((m["cft"] - m["sft"]) + (m["cftflip"] - m["flip"])) / 2,
            "interaction": (m["cftflip"] - m["flip"]) - (m["cft"] - m["sft"]),
        }

    point = effects(progs)
    rng = random.Random(seed)
    draws: dict[str, list[float]] = {k: [] for k in point}
    for _ in range(n_boot):
        e = effects([progs[rng.randrange(len(progs))] for _ in progs])
        for k, v in e.items():
            draws[k].append(v)
    out: dict[str, Any] = {"n_programs": len(progs), "cell_means": means(progs),
                           "effects": {}}
    for k, vals in draws.items():
        vals.sort()
        lo = vals[int(0.025 * len(vals))]
        hi = vals[min(len(vals) - 1, int(0.975 * len(vals)))]
        out["effects"][k] = {"estimate": point[k], "ci": [lo, hi],
                             "excludes_zero": (lo > 0) or (hi < 0)}
    return out


def _pp(x: float) -> str:
    return f"{100 * x:+.1f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--metric", default=METRIC)
    ap.add_argument("--contrast", action="append", default=None,
                    help="'a-b'; repeatable. Default: the paper's standard set.")
    ap.add_argument("--factorial", action="store_true",
                    help="also print the 2x2 objective x data decomposition")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    _load_report_module()

    run = Path(args.run)
    trials = [t for t in iter_jsonl(run / "trials.jsonl") if t["direction"] == "reverse"]
    if not trials:
        raise SystemExit(f"no reverse trials in {run}")
    present = {t["system"] for t in trials}

    pairs = ([tuple(c.split("-", 1)) for c in args.contrast] if args.contrast
             else [p for p in DEFAULT_CONTRASTS if set(p) <= present])

    L = [f"# Arm contrasts - `{run.name}`\n",
         f"*Metric: `{args.metric}`. Paired cluster bootstrap by `program_id`, "
         f"{args.n_boot} resamples, seed {GLOBAL_SEED}. Units are percentage points.*\n",
         "| contrast | a | b | delta (pp) | 95 % CI | n prog | CI excludes 0 |",
         "|---|---|---|---|---|---|---|"]
    results = []
    for a, b in pairs:
        r = paired_delta(trials, a, b, args.metric, args.n_boot, GLOBAL_SEED)
        if r is None:
            continue
        results.append(r)
        L.append(f"| `{a}` - `{b}` | {100*r['mean_a']:.1f} | {100*r['mean_b']:.1f} | "
                 f"**{_pp(r['delta'])}** | [{_pp(r['ci'][0])}, {_pp(r['ci'][1])}] | "
                 f"{r['n_programs']} | {'yes' if r['excludes_zero'] else 'no'} |")

    out: dict[str, Any] = {"run": str(run), "metric": args.metric, "contrasts": results}

    if args.factorial:
        f = factorial(trials, args.metric, args.n_boot, GLOBAL_SEED)
        if f:
            out["factorial"] = f
            m = f["cell_means"]
            L += ["", "## 2x2 - contrastive objective x data direction\n",
                  f"*{f['n_programs']} programs scored on all four cells.*\n",
                  "| | forward only | + reverse data |", "|---|---|---|",
                  f"| **no aux objective** | `sft` {100*m['sft']:.1f} | "
                  f"`flip` {100*m['flip']:.1f} |",
                  f"| **contrastive aux** | `cft` {100*m['cft']:.1f} | "
                  f"`cftflip` {100*m['cftflip']:.1f} |", "",
                  "| effect | estimate (pp) | 95 % CI | excludes 0 |", "|---|---|---|---|"]
            for k in ("data", "objective", "interaction"):
                e = f["effects"][k]
                L.append(f"| **{k}** | {_pp(e['estimate'])} | "
                         f"[{_pp(e['ci'][0])}, {_pp(e['ci'][1])}] | "
                         f"{'yes' if e['excludes_zero'] else 'no'} |")
            L.append("")

    (run / "contrasts.json").write_text(json.dumps(out, indent=2))
    (run / "contrasts.md").write_text("\n".join(L))
    print("\n".join(L))
    print(f"\n[24_contrasts] wrote {run}/contrasts.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
