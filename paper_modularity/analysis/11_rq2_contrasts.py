"""RQ2 stats v2 -- adds explicit GRID separation and pooled composite contrasts.

Grid A ("corpus", dataset tag B, 557 Python programs) and Grid B ("test set", dataset tags
A/B, 40 Python programs) are disjoint in programs and are never pooled (MASTER_REPORT 2).
v1 of this script let `base`/`oracle_prompt_1shot` fall onto Grid A while the merge arms sat
on Grid B, which is exactly the mistake that rule exists to prevent.
"""
import os
import numpy as np
import pandas as pd

SC = os.environ.get("OBTUNE_PAPER_CACHE", ".cache")
B, SEED = 2000, 17
GRID = {"A": lambda t: t.snippet_id.str.startswith(("apps_", "cruxeval")),
        "B": lambda t: t.snippet_id.str.match(r"^[AB]:")}


def boot(a, b, plist, ga, gb):
    rng = np.random.default_rng(SEED)
    d = np.empty(B)
    for i in range(B):
        pick = rng.choice(len(plist), len(plist), replace=True)
        d[i] = (np.concatenate([ga[plist[j]] for j in pick]).mean()
                - np.concatenate([gb[plist[j]] for j in pick]).mean()) * 100
    return d


def delta(t, sys_a, sys_b, conds, grid, lang="python", label=None):
    """Paired delta pooled over `conds` (a list), on one grid, shared programs only."""
    s = t[(t.language == lang) & GRID[grid](t) & t.eval_cond.isin(conds)
          & t.system.isin([sys_a, sys_b])]
    if s.system.nunique() < 2:
        return None
    s = s.assign(key=s.snippet_id + "|" + s.eval_cond)
    keys = set.intersection(*[set(g.key) for _, g in s.groupby("system")])
    s = s[s.key.isin(keys)]
    a, b = s[s.system == sys_a], s[s.system == sys_b]
    plist = sorted(set(s.snippet_id))
    ga = {p: g.correct.values for p, g in a.groupby("snippet_id")}
    gb = {p: g.correct.values for p, g in b.groupby("snippet_id")}
    plist = [p for p in plist if p in ga and p in gb]
    d = boot(a, b, plist, ga, gb)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return dict(system=sys_a, ref=sys_b, cond=label or "+".join(conds), grid=grid,
                delta=(a.correct.mean() - b.correct.mean()) * 100, lo=lo, hi=hi,
                p=max(2 * min((d <= 0).mean(), (d >= 0).mean()), 1 / B),
                n_prog=len(plist), n_item=len(a))


def bh(rows, alpha=0.05):
    r = sorted(rows, key=lambda x: x["p"])
    for i, x in enumerate(r, 1):
        x["q"] = min(1.0, x["p"] * len(r) / i)
    for i in range(len(r) - 2, -1, -1):
        r[i]["q"] = min(r[i]["q"], r[i + 1]["q"])
    for x in r:
        x["sig"] = "*" if x["q"] < alpha and (x["lo"] > 0) == (x["hi"] > 0) else ""
    return r


def table(t, systems, ref, conds, grid, title, lang="python"):
    rows = bh([d for sy in systems for c in conds
               if (d := delta(t, sy, ref, [c], grid, lang)) is not None])
    df = pd.DataFrame(rows)
    df["s"] = df.apply(lambda r: f"{r.delta:+.1f}{r.sig}", axis=1)
    print(f"\n### {title}\n    vs {ref}, grid {grid}, {lang}; * = BH q<.05 AND CI excludes 0")
    print(df.pivot(index="system", columns="cond", values="s")
            .reindex(index=[s for s in systems if s in set(df.system)],
                     columns=[c for c in conds if c in set(df.cond)]).to_string())
    for r in sorted(rows, key=lambda x: (x["system"], x["cond"])):
        print(f"    {r['system']:22s} {r['cond']:10s} {r['delta']:+6.1f} "
              f"[{r['lo']:+.1f},{r['hi']:+.1f}] q={r['q']:.3f}{r['sig']} n_prog={r['n_prog']}")
    return df


if __name__ == "__main__":
    t = pd.read_parquet(f"{SC}/trials_all.parquet")
    C6 = ["L0", "L1b", "L1r", "L2", "S1", "S2", "H1"]
    COMP = ["C_L1r_S1", "C_S1_L1r", "C_L1b_S1", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]

    print("=" * 78, "\nGRID B (test set, 40 Python programs) -- the RQ2 grid")
    table(t, ["router", "merge_dare_ties", "dl_rescaled", "merge_ties",
              "merge_dare_linear", "oracle_prompt_1shot", "base"], "tuned_L0", C6, "B",
          "RQ2: routing, merging and oracle prompting")

    print("\n" + "=" * 78, "\nGRID A (corpus, 557 Python programs) -- reference only, NEVER pooled with B")
    table(t, ["oracle_prompt_1shot", "base"], "tuned_L0", C6, "A", "oracle prompting at scale")

    print("\n" + "=" * 78, "\nMoLE ladder (Grid B, composites)")
    table(t, ["mole_router", "mole_uniform", "mole_random"], "base", COMP + ["L1r", "S1"], "B",
          "mixture arms vs base through the same HF engine")
    table(t, ["mole_router"], "mole_uniform", COMP + ["L1r", "S1"], "B",
          "the learned gate against the one-thing-different fixed mixture")
    for lab, cs in [("6 composites pooled", COMP), ("all 8 conditions", COMP + ["L1r", "S1"])]:
        d = delta(t, "mole_router", "mole_uniform", cs, "B", label=lab)
        print(f"    POOLED {lab:22s} {d['delta']:+.1f} [{d['lo']:+.1f},{d['hi']:+.1f}] "
              f"p={d['p']:.4f} n_prog={d['n_prog']} n_item={d['n_item']}")
