#!/usr/bin/env python
"""What the RouterLoRA gate actually attends to — and whether composites decompose.

    PYTHONPATH=src python scripts/analysis/22_gate_routing_report.py
    PYTHONPATH=src python scripts/analysis/22_gate_routing_report.py --json

THE THREE QUESTIONS THIS ANSWERS
--------------------------------
`mole/eval_mole` has been writing a per-cell `gate_report.json` (per-layer expert mass and
routing entropy over the 8-expert bank) since the mixture ladder first ran, and nothing has
ever read them. They answer three things the accuracy column cannot:

1. **How much mass sits on each expert?** Accuracy says the router beats its controls; it
   does not say whether that is one expert doing the work or eight sharing it.

2. **Does the gate collapse to one expert, or blend?** §12.4 showed `mole_hardrouter` (the
   trained gate argmaxed to one-hot) reproduces `mole_router` to within seed noise, which
   already implied the blend is doing nothing. Entropy measures that directly instead of
   inferring it from accuracy.

3. **On COMPOSED code, does routing decompose?** This is the sharp one. `C_L1r_S1` is L1r
   and S1 stacked on one program. If the mixture is genuinely compositional, the gate should
   put its mass on the L1r expert AND the S1 expert — the two transforms actually present —
   rather than on whichever single expert it likes. Nothing else in the project tests
   composition as a *mechanism* rather than as an accuracy number.

WHY LAYER STRUCTURE IS REPORTED, NOT JUST A MEAN
------------------------------------------------
Routing is not uniform across depth: layer 0 in the observed reports puts 99.6 % of its mass
on a single expert while middle layers spread across three. A single all-layer average would
hide that and could report "balanced" for a gate that is one-hot everywhere except a few
middle layers. Early/middle/late thirds are reported alongside the mean.

CONTROLS ARE INCLUDED ON PURPOSE
--------------------------------
`mole_uniform` (gate frozen uniform) and `mole_random` (gate frozen at random init) bound
what a NON-learned gate produces on the same inputs. A "relevant-expert mass" of 0.4 means
nothing until you know the controls give 0.25.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CELLS = ROOT / "results" / "cells" / "main" / "qwen25c-1.5b" / "python"
OUT = ROOT / "results" / "analysis" / "gate_routing.json"

SYSTEMS = ["mole_router", "mole_hardrouter", "mole_uniform", "mole_random"]


def relevant_experts(cond: str) -> list[str]:
    """Which experts SHOULD carry the mass, if routing tracks the transforms present.

    `C_L1r_S1` -> [L1r, S1]; a single condition -> itself; `H1` -> [] (held out by
    construction, so no expert corresponds to it — which is what makes it the interesting
    case rather than a missing one).
    """
    if cond == "H1":
        return []
    m = re.fullmatch(r"C_([A-Za-z0-9]+)_([A-Za-z0-9]+)", cond)
    if m:
        return [m.group(1), m.group(2)]
    return [cond]


def load(system: str, cond: str) -> dict | None:
    p = CELLS / f"{system}__{cond}" / "gate_report.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def summarize(rep: dict) -> dict:
    experts = rep["experts"]
    layers = rep["routing"]["layers"]
    idx = sorted(layers, key=int)
    n = len(idx)
    mass = [layers[i]["expert_mass"] for i in idx]
    ent = [layers[i]["entropy_norm"] for i in idx]

    def mean_mass(sub):
        if not sub:
            return [0.0] * len(experts)
        return [sum(row[j] for row in sub) / len(sub) for j in range(len(experts))]

    third = max(1, n // 3)
    return {
        "experts": experts,
        "mass_all": mean_mass(mass),
        "mass_early": mean_mass(mass[:third]),
        "mass_mid": mean_mass(mass[third: 2 * third]),
        "mass_late": mean_mass(mass[2 * third:]),
        "entropy_norm_mean": sum(ent) / len(ent),
        "entropy_norm_min": min(ent),
        "entropy_norm_max": max(ent),
        "collapsed_flag": rep["routing"].get("collapsed"),
        "n_layers": n,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="print the artifact instead of the report")
    args = ap.parse_args(argv)

    conds = sorted({p.name.split("__", 1)[1] for p in CELLS.glob("mole_router__*")
                    if (p / "gate_report.json").exists()})
    if not conds:
        print("no gate_report.json found — has the mixture ladder run?", file=sys.stderr)
        return 1

    art: dict = {"conditions": conds, "systems": SYSTEMS, "cells": {}}
    for s in SYSTEMS:
        for c in conds:
            rep = load(s, c)
            if rep:
                art["cells"][f"{s}__{c}"] = summarize(rep)

    if args.json:
        print(json.dumps(art, indent=2))
        return 0

    experts = art["cells"][f"mole_router__{conds[0]}"]["experts"]
    W = 7

    print("=" * 100)
    print("1. EXPERT MASS — mole_router, mean over all 28 layers (8 experts, uniform = .125)")
    print("=" * 100)
    print(f"{'condition':12s}" + "".join(f"{e:>{W}s}" for e in experts) + "   entropy  top-2")
    for c in conds:
        k = f"mole_router__{c}"
        if k not in art["cells"]:
            continue
        d = art["cells"][k]
        m = d["mass_all"]
        order = sorted(range(len(m)), key=lambda j: -m[j])[:2]
        top2 = ", ".join(f"{experts[j]} {m[j]:.2f}" for j in order)
        print(f"{c:12s}" + "".join(f"{v:{W}.3f}" for v in m)
              + f"   {d['entropy_norm_mean']:.3f}   {top2}")

    print()
    print("=" * 100)
    print("2. DOES IT COLLAPSE? — normalised entropy, 0 = one expert, 1 = uniform over 8")
    print("=" * 100)
    print(f"{'condition':12s}" + "".join(f"{s.replace('mole_',''):>14s}" for s in SYSTEMS))
    for c in conds:
        row = ""
        for s in SYSTEMS:
            d = art["cells"].get(f"{s}__{c}")
            row += f"{d['entropy_norm_mean']:14.3f}" if d else f"{'—':>14s}"
        print(f"{c:12s}{row}")

    print()
    print("=" * 100)
    print("3. DO COMPOSITES DECOMPOSE? — mass on the experts whose transforms are PRESENT")
    print("=" * 100)
    print("   chance = |relevant| / 8.  Controls bound what a non-learned gate gives.")
    print()
    hdr = f"{'condition':12s}{'relevant':16s}{'chance':>8s}{'router':>9s}{'hard':>9s}{'uniform':>9s}{'random':>9s}   split (router)"
    print(hdr)
    for c in conds:
        rel = relevant_experts(c)
        if not rel:
            continue
        chance = len(rel) / len(experts)
        cells = {}
        for s in SYSTEMS:
            d = art["cells"].get(f"{s}__{c}")
            if not d:
                cells[s] = None
                continue
            m = dict(zip(d["experts"], d["mass_all"]))
            cells[s] = sum(m.get(r, 0.0) for r in rel)
        d = art["cells"].get(f"mole_router__{c}")
        split = ""
        if d:
            m = dict(zip(d["experts"], d["mass_all"]))
            split = " / ".join(f"{r}={m.get(r,0.0):.2f}" for r in rel)
        def f(v):
            return f"{v:9.3f}" if v is not None else f"{'—':>9s}"
        print(f"{c:12s}{','.join(rel):16s}{chance:8.3f}"
              + f(cells['mole_router']) + f(cells['mole_hardrouter'])
              + f(cells['mole_uniform']) + f(cells['mole_random'])
              + f"   {split}")

    print()
    print("=" * 100)
    print("4. ORDER EFFECT — the same two transforms, applied in each order")
    print("=" * 100)
    pairs = [(a, b) for a in conds for b in conds
             if a < b and relevant_experts(a) and
             sorted(relevant_experts(a)) == sorted(relevant_experts(b)) and a != b]
    if not pairs:
        print("   (no reversed composite pair present)")
    for a, b in pairs:
        for c in (a, b):
            d = art["cells"].get(f"mole_router__{c}")
            if not d:
                continue
            m = dict(zip(d["experts"], d["mass_all"]))
            rel = relevant_experts(c)
            print(f"   {c:12s} " + "  ".join(f"{r}={m.get(r,0.0):.3f}" for r in rel)
                  + f"   entropy={d['entropy_norm_mean']:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2))
    print(f"\nartifact -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
