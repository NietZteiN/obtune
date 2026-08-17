"""RQ2 aggregation, v2 -- per-cell parquets, keyed by the cell's own system label.

Adds: program set identity (snippet_id), dataset tag, and a common-subset accuracy so
cells are never compared across different program populations (MASTER_REPORT 2).
"""
import json, glob, os, sys
import pandas as pd

OUT = os.environ.get("OBTUNE_PAPER_CACHE", ".cache")


def load():
    recs, trials = [], []
    for meta_f in glob.glob("results/cells/*/*/*/*/cell_meta.json"):
        d = json.load(open(meta_f))
        cell = os.path.dirname(meta_f)
        tp = os.path.join(cell, "trials.parquet")
        if not os.path.exists(tp):
            continue
        df = pd.read_parquet(tp)
        df["cell"] = os.path.basename(cell)
        df["experiment_id"] = d.get("experiment_id")
        df["system"] = d["system"]
        trials.append(df[["cell", "experiment_id", "system", "language", "dataset",
                          "snippet_id", "item_id", "eval_cond", "correct", "format_fail"]])
        recs.append(dict(
            experiment_id=d.get("experiment_id"), lang=cell.split("/")[-2],
            system=d["system"], cond=d["eval_cond"], n=len(df),
            acc=float(df["correct"].mean()), fmt=float(df["format_fail"].mean()),
            ts=d["run_ts"][:10], dataset="/".join(sorted(set(df["dataset"].astype(str)))),
            n_prog=df["snippet_id"].nunique(), cell=os.path.basename(cell),
        ))
    return pd.DataFrame(recs), pd.concat(trials, ignore_index=True)


def common_subset(t, systems, conds, lang="python"):
    """Accuracy restricted to snippet_ids present in EVERY (system, cond) requested."""
    s = t[(t.language == lang) & t.system.isin(systems) & t.eval_cond.isin(conds)]
    groups = s.groupby(["system", "eval_cond"])["snippet_id"].apply(set)
    if len(groups) < len(systems) * len(conds):
        missing = {(sy, c) for sy in systems for c in conds} - set(groups.index)
        print(f"  ! missing cells: {sorted(missing)}", file=sys.stderr)
    keep = set.intersection(*groups.tolist())
    s = s[s.snippet_id.isin(keep)]
    p = s.pivot_table(index="system", columns="eval_cond", values="correct", aggfunc="mean")
    return p.reindex(index=[x for x in systems if x in p.index],
                     columns=[c for c in conds if c in p.columns]), len(keep)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cells, trials = load()
    cells.to_csv(f"{OUT}/cells2.csv", index=False)
    trials.to_parquet(f"{OUT}/trials_all.parquet")
    print(f"{len(cells)} cells, {len(trials)} trials", file=sys.stderr)
    print(cells.groupby(["experiment_id", "lang", "dataset"])
              .agg(cells=("cell", "size"), progs=("n_prog", "max")).to_string())
