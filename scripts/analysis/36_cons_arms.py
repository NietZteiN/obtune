#!/usr/bin/env python
"""RQ3' — does the paired-consistency objective get BOTH sides (seen gain without the
unseen tax)? Three pre-registered reads, one script so the rules cannot drift:

  --mode e3   scale: cons_lam3 at 13B and 34B (phase objectives_scale) against mono_all /
              tuned_L0 read at the same scale (phases x1_generic for X1, rq2_generic for seen).
  --mode e4   teacher ablation on 7B (phase objectives_teacher): cons_tbase (untuned teacher),
              cons_tmono (mono_all teacher) against cons_lam3 / mono_all / tuned_L0.
  --mode e8   second family (llama31-8b, phase objectives_llama).

Rules (CLAUDE_SCRATCHPAD.md, pre-registered 2026-09-07, applied verbatim; NO H1 anywhere):
  H-E3      CONFIRMED iff cons_lam3 − mono_all on X1 has ci_lo > 0 at BOTH 13B and 34B;
            PARTIAL iff at exactly one; REFUTED otherwise.
  H-E3-tax  "no unseen tax vs tuned_L0": CONFIRMED iff cons_lam3 − tuned_L0 on X1 does not
            have ci_hi < 0 at both scales.
  H-E4-view "the clean VIEW carries the gain, not the teacher": CONFIRMED iff
            cons_tbase − mono_all on X1 has ci_lo > 0.
  H-E4-teacher "teacher quality matters": CONFIRMED iff cons_lam3 − cons_tbase on X1 ci_lo > 0.
  H-E4-mono  "a broader teacher is better": CONFIRMED iff cons_tmono − cons_lam3 on X1 ci_lo > 0;
            REFUTED iff ci_hi < 0; INCONCLUSIVE otherwise.
  H-E8      CONFIRMED iff cons_lam3 − mono_all on X1 ci_lo > 0 on llama31-8b.
  H-E8-seen CONFIRMED iff cons_lam3 − tuned_L0 pooled over the five obfuscated seen
            conditions ci_lo > 0 on llama31-8b.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

CONDS = ck.SEEN + ["X1"]


def block_for(mode: str, model: str):
    if mode == "e3":
        phases = ["objectives_scale", "x1_generic", "rq2_generic"]
        systems = ["tuned_L0", "mono_all", "cons_lam3"]
    elif mode == "e4":
        phases = ["objectives_teacher", "objectives_generic", "x1_generic", "rq1_generic"]
        systems = ["tuned_L0", "mono_all", "cons_lam3", "cons_tbase", "cons_tmono"]
    else:
        phases = ["objectives_llama", "x1_generic", "rq2_generic"]
        systems = ["base", "tuned_L0", "mono_all", "cons_lam3"]
    return ck.load_block(phases, model, systems, CONDS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["e3", "e4", "e8"], required=True)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    models = a.models or {"e3": ["codellama-13b", "codellama-34b"], "e4": ["codellama-7b"],
                          "e8": ["llama31-8b"]}[a.mode]
    res = ck.new_result("RQ3'", Path(__file__).name + f" --mode {a.mode}", models)
    blocks = {}
    for m in models:
        b = block_for(a.mode, m)
        blocks[m] = b
        res["accuracy"][m], res["format_fail"][m] = ck.acc_table(b)
        C = res["contrasts"].setdefault(m, {})
        pairs = [("cons_lam3", "mono_all"), ("cons_lam3", "tuned_L0"), ("mono_all", "tuned_L0")]
        if a.mode == "e4":
            pairs += [("cons_tbase", "mono_all"), ("cons_tbase", "tuned_L0"), ("cons_lam3", "cons_tbase"),
                      ("cons_tmono", "cons_lam3"), ("cons_tmono", "mono_all"), ("cons_tmono", "cons_tbase")]
        for t, c in pairs:
            for conds, tag in ((["X1"], "X1"), (ck.OBF_SEEN, "seen"), (["L0"], "L0")):
                r = ck.contrast(b, t, c, conds, label=f"{t} - {c} @ {tag}", eq_margin=1.0)
                if r:
                    C[f"{t} - {c} @ {tag}"] = r
        ck.print_acc(m, res["accuracy"][m], CONDS)
        for lab, c in C.items():
            print(f"  {lab:<32} {ck.fmt(c)}")
        print()

    def get(m, lab):
        return res["contrasts"].get(m, {}).get(lab)

    if a.mode == "e3":
        wins = {m: (get(m, "cons_lam3 - mono_all @ X1") or {}).get("ci_lo", float("nan")) > 0 for m in models}
        have = [m for m in models if get(m, "cons_lam3 - mono_all @ X1")]
        n = sum(wins.values())
        v = "PENDING" if len(have) < len(models) else ("CONFIRMED" if n == len(models) else "PARTIAL" if n else "REFUTED")
        ck.hypothesis(res, "H-E3", "cons_lam3 − mono_all @ X1 ci_lo>0 at both scales", v,
                      "; ".join(f"{m}: {ck.fmt(get(m, 'cons_lam3 - mono_all @ X1'))}" for m in models))
        tax = [get(m, "cons_lam3 - tuned_L0 @ X1") for m in models]
        if all(tax):
            v = "CONFIRMED" if not any(t["ci_hi"] < 0 for t in tax) else "REFUTED"
        else:
            v = "PENDING"
        ck.hypothesis(res, "H-E3-tax", "cons_lam3 − tuned_L0 @ X1 not ci_hi<0 at both scales", v,
                      "; ".join(f"{m}: {ck.fmt(get(m, 'cons_lam3 - tuned_L0 @ X1'))}" for m in models))
    elif a.mode == "e4":
        m = models[0]
        r = get(m, "cons_tbase - mono_all @ X1")
        ck.hypothesis(res, "H-E4-view", "cons_tbase − mono_all @ X1 ci_lo>0",
                      "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED", ck.fmt(r))
        r = get(m, "cons_lam3 - cons_tbase @ X1")
        ck.hypothesis(res, "H-E4-teacher", "cons_lam3 − cons_tbase @ X1 ci_lo>0",
                      "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED", ck.fmt(r))
        r = get(m, "cons_tmono - cons_lam3 @ X1")
        ck.hypothesis(res, "H-E4-mono", "cons_tmono − cons_lam3 @ X1: ci_lo>0 confirms, ci_hi<0 refutes",
                      "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED" if r["ci_hi"] < 0 else "INCONCLUSIVE",
                      ck.fmt(r))
    else:
        m = models[0]
        r = get(m, "cons_lam3 - mono_all @ X1")
        ck.hypothesis(res, "H-E8", "cons_lam3 − mono_all @ X1 ci_lo>0 on llama31-8b",
                      "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED", ck.fmt(r))
        r = get(m, "cons_lam3 - tuned_L0 @ seen")
        ck.hypothesis(res, "H-E8-seen", "cons_lam3 − tuned_L0 @ seen(obf) ci_lo>0 on llama31-8b",
                      "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED", ck.fmt(r))
        r = get(m, "cons_lam3 - tuned_L0 @ X1")
        ck.hypothesis(res, "H-E8-tax", "cons_lam3 − tuned_L0 @ X1 not ci_hi<0 on llama31-8b",
                      "PENDING" if not r else "CONFIRMED" if not r["ci_hi"] < 0 else "REFUTED", ck.fmt(r))
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
