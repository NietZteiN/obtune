#!/usr/bin/env python
"""Lever 2b, step 3 — score candidates with the verifier and compare selectors.

Selectors, all over the SAME candidate set (scripts/28 parquet; sample_idx -1 = greedy,
0..n-1 = temperature samples):

  greedy          the sample_idx -1 completion (the published number)
  vote            plurality over the n samples' normalised predictions (self-consistency)
  logprob         argmax cumulative log-prob over the n samples          — zero-training control
  logprob_norm    argmax per-token log-prob                              — zero-training control
  verifier:<tag>  argmax verifier score over DISTINCT candidates (greedy included)
  any_of_n        oracle upper bound: 1 if any candidate is correct

The verifier score is logsumexp P(yes-tokens) - logsumexp P(no-tokens) at the first
generated position, obtained from vLLM with max_tokens=1, logprobs=K, under the verifier
LoRA (or none — `--adapters none` scores the untuned base as a zero-shot self-verifier).
Checkpoint choice, if several are given, is by VAL rerank accuracy; the held-out number
is reported for every checkpoint but the chosen one is marked.

Deltas vs greedy carry a cluster bootstrap by program_id (B=2000, seed 17), per condition.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import prompts, verifier  # noqa: E402
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RUNS_DIR, load_config  # noqa: E402
from obtune.eval_vllm import Engine  # noqa: E402
from obtune.transfer import ci_from_draws  # noqa: E402

B = 2000


def _lse(vals):
    vals = [v for v in vals if v is not None and math.isfinite(v)]
    if not vals:
        return -30.0
    m = max(vals)
    return m + math.log(sum(math.exp(v - m) for v in vals))


def score_with(engine: Engine, adapter, df, yes_ids, no_ids, logprobs_k: int) -> np.ndarray:
    from vllm import SamplingParams

    recs = df.to_dict("records")
    texts = [prompts.render_chat(verifier.build_verifier_prompt(r, r["cand"]), engine.tokenizer)
             for r in recs]
    outs = engine.llm.generate(
        texts, SamplingParams(temperature=0.0, max_tokens=1, logprobs=logprobs_k),
        lora_request=engine.lora_request(adapter), use_tqdm=True,
    )
    scores = np.empty(len(recs))
    for i, o in enumerate(outs):
        lp = o.outputs[0].logprobs
        d = lp[0] if lp else {}
        get = lambda tid: (d[tid].logprob if tid in d else None)  # noqa: E731
        scores[i] = _lse([get(t) for t in yes_ids]) - _lse([get(t) for t in no_ids])
    return scores


def selectors(df, score_cols: list[str]) -> dict[str, dict]:
    """Return {selector: {item_id: correct(0/1)}} on distinct-candidate rows."""
    out: dict[str, dict] = {}
    samp = df[df.sample_idx >= 0]
    greedy = df[df.sample_idx == -1].set_index("item_id")["correct"].to_dict()
    out["greedy"] = greedy
    out["any_of_n"] = df.groupby("item_id")["correct"].max().to_dict()
    # vote: plurality over pred_norm among parsed samples; ties -> earliest sample_idx
    vote = {}
    for iid, g in samp.groupby("item_id", sort=False):
        g = g.sort_values("sample_idx")
        gp = g[g.parse_ok == 1]
        if gp.empty:
            vote[iid] = int(g.iloc[0]["correct"]); continue
        counts = gp.groupby("pred_norm", sort=False)["sample_idx"].agg(["size", "min"])
        best = counts.sort_values(["size", "min"], ascending=[False, True]).index[0]
        vote[iid] = int(gp[gp.pred_norm == best].iloc[0]["correct"])
    out["vote"] = vote
    for name, col in (("logprob", "cum_logprob"), ("logprob_norm", "lp_norm")):
        pick = samp.sort_values(col, ascending=False).drop_duplicates("item_id")
        out[name] = pick.set_index("item_id")["correct"].to_dict()
    for col in score_cols:
        dd = df.drop_duplicates(["item_id", "_k"])
        pick = dd.sort_values([col, "sample_idx"], ascending=[False, False]).drop_duplicates("item_id")
        out[col] = pick.set_index("item_id")["correct"].to_dict()
    return out


def summarise(df, sel: dict[str, dict], seed: int) -> dict:
    items = df.drop_duplicates("item_id")[["item_id", "program_id", "condition"]]
    res = {}
    for cond, sub in [("ALL", items)] + [(c, g) for c, g in items.groupby("condition")]:
        progs = sub.program_id.unique()
        pidx = {p: i for i, p in enumerate(progs)}
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, len(progs), size=(B, len(progs)))
        per_prog = {}
        for name, d in sel.items():
            arr = np.zeros(len(progs)); cnt = np.zeros(len(progs))
            for iid, p in zip(sub.item_id, sub.program_id):
                arr[pidx[p]] += d.get(iid, 0); cnt[pidx[p]] += 1
            per_prog[name] = (arr, cnt)
        g_arr, g_cnt = per_prog["greedy"]
        row = {"n_items": int(len(sub)), "n_programs": int(len(progs))}
        for name, (arr, cnt) in per_prog.items():
            acc = float(arr.sum() / cnt.sum())
            draws = (arr[idx].sum(1) - g_arr[idx].sum(1)) / cnt[idx].sum(1)
            lo, hi = ci_from_draws(draws)
            row[name] = {"acc": round(acc, 4), "delta_vs_greedy_pts": round(100 * (acc - g_arr.sum() / g_cnt.sum()), 2),
                         "ci_pts": [round(100 * lo, 2), round(100 * hi, 2)]}
        res[cond] = row
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--candidates-tag", default="tuned_L0")
    ap.add_argument("--adapters", nargs="*", default=[],
                    help="verifier adapter dirs (or 'none' for the untuned base)")
    ap.add_argument("--adapter-root", default=None,
                    help="expand to every checkpoint-*/ and final/ under this dir")
    ap.add_argument("--splits", nargs="*", default=["val", "heldout"])
    ap.add_argument("--logprobs-k", type=int, default=20)
    ap.add_argument("--seed", type=int, default=GLOBAL_SEED)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    import pandas as pd

    if args.adapter_root:
        root = Path(args.adapter_root)
        args.adapters += sorted(str(p) for p in root.glob("checkpoint-*")) + [str(root / "final")]
    mcfg = load_config("models.yaml")["models"][args.model]
    ecfg = dict(load_config("eval/_base_eval.yaml").get("engine") or {})
    engine = Engine(mcfg["hf_id"], ecfg)
    yes_ids, no_ids = verifier.yes_no_token_ids(engine.tokenizer)
    print(f"[30] yes ids {yes_ids} no ids {no_ids}", flush=True)
    cand_dir = RUNS_DIR / "candidates" / args.model / args.candidates_tag
    out_dir = Path(args.out) if args.out else PROJECT_ROOT / "results" / "analysis" / "rerank" / args.model / args.candidates_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {"model": args.model, "candidates_tag": args.candidates_tag, "adapters": args.adapters,
              "yes_ids": yes_ids, "no_ids": no_ids, "splits": {}}
    for split in args.splits:
        df = pd.read_parquet(cand_dir / f"{split}.parquet")
        df["cand"] = df["text"].fillna("").str.strip()
        df["_k"] = df["pred_norm"].fillna(df["cand"])
        df["lp_norm"] = df["cum_logprob"] / df["n_tokens"].clip(lower=1)
        score_cols = []
        for ad in args.adapters:
            tag = "verifier:base" if ad == "none" else "verifier:" + "/".join(Path(ad).parts[-2:])
            t0 = time.time()
            dd = df.drop_duplicates(["item_id", "_k"]).copy()
            dd[tag] = score_with(engine, None if ad == "none" else ad, dd, yes_ids, no_ids, args.logprobs_k)
            df = df.merge(dd[["item_id", "_k", tag]], on=["item_id", "_k"], how="left")
            # verifier-as-classifier quality on distinct candidates
            y, s = dd["correct"].to_numpy(), dd[tag].to_numpy()
            order = np.argsort(s); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
            npos, nneg = y.sum(), (1 - y).sum()
            auc = float((ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)) if npos and nneg else float("nan")
            print(f"[30] {split} {tag}: {len(dd)} distinct candidates scored in {time.time()-t0:.0f}s, "
                  f"AUC={auc:.3f} acc@0={(( s > 0) == (y == 1)).mean():.3f}", flush=True)
            report["splits"].setdefault(split, {}).setdefault("classifier", {})[tag] = {
                "n": int(len(dd)), "auc": auc, "acc_at_0": float(((s > 0) == (y == 1)).mean()),
                "pos_rate": float(y.mean())}
            score_cols.append(tag)
        sel = selectors(df, score_cols)
        report["splits"][split]["selectors"] = summarise(df, sel, args.seed)
        df.to_parquet(out_dir / f"{split}_scored.parquet", index=False)
        print(f"[30] {split} ALL: " + json.dumps(report["splits"][split]["selectors"]["ALL"]), flush=True)

    if "val" in report["splits"] and score_cols:
        v = report["splits"]["val"]["selectors"]["ALL"]
        chosen = max(score_cols, key=lambda c: v[c]["acc"])
        report["chosen_by_val"] = chosen
        print(f"[30] chosen by val: {chosen}", flush=True)
    (out_dir / "rerank_report.json").write_text(json.dumps(report, indent=2))
    print(f"[30] wrote {out_dir / 'rerank_report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
