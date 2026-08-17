"""Score prompts with the trained router: adapter choice, softmax, entropy.

Emits three things, all of them RQ2 deliverables rather than diagnostics:

1. `results/router/routing.parquet` — one row per item:
   item_id, program_id, true condition, routed condition, chosen adapter, the full
   6-way softmax, and the routing entropy in nats (and normalized by log 6).
2. Per-condition confusion matrix (rows = true condition, cols = routed condition).
   The interesting cells are the identifier-family confusions: L1b/L1r/L2 differ only in
   the *style* of the renaming, so a router that collapses them is telling us the
   per-type decomposition is finer than the model's representation supports — which is
   an answer to RQ2, not a bug.
3. The H1 routing-entropy distribution vs the held-in conditions, with a
   Mann-Whitney U comparison. H1 is out of distribution by construction; whether the
   router *knows* it is out of distribution (high entropy) or confidently misroutes it
   (low entropy, wrong adapter) determines whether a router-based system can be expected
   to degrade gracefully on an unseen obfuscator. This is a reported result.

H1 never influences the router: it is scored only, never fit. Reading H1 here is an
eval-time access and must be logged in data/quarantine/h1/ACCESS_LOG.md by the caller.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np

from obtune.config import RESULTS_DIR
from obtune.paths import TRAINABLE_CONDITIONS
from obtune.router.features import LABEL_TO_CONDITION, FeatureSet, load_features
from obtune.router.train_router import RouterCheckpoint, build_model, load_checkpoint

__all__ = ["route_features", "confusion_matrix", "entropy_report", "ROUTER_RESULTS_DIR"]

ROUTER_RESULTS_DIR = RESULTS_DIR / "router"


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def route_features(
    fs: FeatureSet,
    ck: RouterCheckpoint,
    *,
    adapter_map: Optional[dict[str, str]] = None,
    batch_size: int = 4096,
) -> list[dict[str, Any]]:
    """One routing decision per row. `adapter_map` maps condition -> adapter id."""
    import torch

    if fs.X.shape[1] != ck.in_dim:
        raise ValueError(f"feature dim {fs.X.shape[1]} != router in_dim {ck.in_dim}")
    amap = adapter_map or {c: c for c in TRAINABLE_CONDITIONS}

    # The router's class space and the set of adapters we can actually route to are two
    # different things, and they drifted apart the moment the S2 split raised
    # TRAINABLE_CONDITIONS from 6 to 8: the head now has S3/S4 units, but the feature
    # jobs enumerate only the six original conditions, so those units are never trained —
    # and no S3/S4 per-condition adapter exists yet either. An untrained unit can still
    # win an argmax. `amap.get(cond, cond)` would then have silently emitted the literal
    # string "S3" as an adapter path, and eval_vllm would have been handed something that
    # is not a path at all. Refuse instead, naming the gap.
    if adapter_map is not None:
        unroutable = [LABEL_TO_CONDITION[k] for k in range(ck.n_classes)
                      if LABEL_TO_CONDITION.get(k) and LABEL_TO_CONDITION[k] not in amap]
        if unroutable:
            print(f"[route] WARNING: router can predict {unroutable} but no adapter is "
                  f"mapped for them; any item routed there is a hard error", flush=True)

    model = build_model(ck)
    X = (fs.X - ck.mean) / ck.std

    logits = np.zeros((len(fs), ck.n_classes), dtype=np.float32)
    with torch.no_grad():
        for i in range(0, len(X), batch_size):
            logits[i:i + batch_size] = model(
                torch.tensor(X[i:i + batch_size], dtype=torch.float32)).numpy()
    probs = _softmax(logits.astype(np.float64))
    ln6 = math.log(ck.n_classes)

    rows: list[dict[str, Any]] = []
    for i in range(len(fs)):
        p = probs[i]
        k = int(p.argmax())
        cond = LABEL_TO_CONDITION[k]
        if adapter_map is not None and cond not in amap:
            raise SystemExit(
                f"[route] item {fs.item_ids[i]} routed to {cond!r}, which has no adapter in "
                f"--adapter-map (have: {sorted(amap)}). Train that adapter, or drop the class. "
                f"Emitting the condition name as an adapter path would fail downstream in "
                f"eval_vllm with a far less obvious message.")
        ent = float(-(p[p > 0] * np.log(p[p > 0])).sum())
        rows.append({
            "item_id": str(fs.item_ids[i]),
            "program_id": str(fs.program_ids[i]),
            "language": str(fs.languages[i]),
            "true_condition": str(fs.conditions[i]),
            "routed_condition": cond,
            "adapter": amap.get(cond, cond),
            "routed_label": k,
            "entropy": ent,
            "entropy_norm": ent / ln6,
            "max_prob": float(p[k]),
            "correct_route": int(str(fs.conditions[i]) == cond),
            "is_heldout": int(str(fs.conditions[i]) not in TRAINABLE_CONDITIONS),
            **{f"p_{c}": float(p[j]) for j, c in enumerate(ck.class_order)},
        })
    return rows


def confusion_matrix(rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """rows = true condition (H1 included), cols = routed condition."""
    trues = sorted({r["true_condition"] for r in rows},
                   key=lambda c: (c not in TRAINABLE_CONDITIONS, c))
    cm = {t: {c: 0 for c in TRAINABLE_CONDITIONS} for t in trues}
    for r in rows:
        cm[r["true_condition"]][r["routed_condition"]] += 1
    return cm


def entropy_report(rows: Sequence[dict[str, Any]], heldout: str = "H1") -> dict[str, Any]:
    """H1 routing-entropy distribution vs the held-in conditions (an RQ2 result)."""
    from scipy import stats

    h1 = np.array([r["entropy"] for r in rows if r["true_condition"] == heldout])
    held_in = np.array([r["entropy"] for r in rows if r["true_condition"] in TRAINABLE_CONDITIONS])
    out: dict[str, Any] = {
        "heldout_condition": heldout,
        "n_heldout": int(h1.size),
        "n_held_in": int(held_in.size),
        "max_entropy_nats": math.log(len(TRAINABLE_CONDITIONS)),
        "per_condition": {},
    }
    for c in sorted({r["true_condition"] for r in rows}):
        e = np.array([r["entropy"] for r in rows if r["true_condition"] == c])
        mp = np.array([r["max_prob"] for r in rows if r["true_condition"] == c])
        acc = np.array([r["correct_route"] for r in rows if r["true_condition"] == c])
        out["per_condition"][c] = {
            "n": int(e.size),
            "entropy_mean": float(e.mean()) if e.size else None,
            "entropy_median": float(np.median(e)) if e.size else None,
            "entropy_q25": float(np.percentile(e, 25)) if e.size else None,
            "entropy_q75": float(np.percentile(e, 75)) if e.size else None,
            "max_prob_mean": float(mp.mean()) if mp.size else None,
            "route_accuracy": float(acc.mean()) if c in TRAINABLE_CONDITIONS and acc.size else None,
        }
    if h1.size and held_in.size:
        u = stats.mannwhitneyu(h1, held_in, alternative="two-sided")
        # rank-biserial effect size: +1 => H1 entropy always above held-in
        rb = 2.0 * u.statistic / (h1.size * held_in.size) - 1.0
        out["mannwhitney"] = {"U": float(u.statistic), "p": float(u.pvalue),
                              "rank_biserial": float(rb),
                              "delta_mean_entropy": float(h1.mean() - held_in.mean())}
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    import pandas as pd

    ap = argparse.ArgumentParser(description="Route items with the trained RQ2 router")
    ap.add_argument("--router", required=True, help="npz from router.train_router")
    ap.add_argument("--features", required=True, help="npz from router.features (may include H1)")
    ap.add_argument("--adapter-map", default=None, help="JSON {condition: adapter_id}")
    ap.add_argument("--out", default=str(ROUTER_RESULTS_DIR / "routing.parquet"))
    # The evaluator consumes a plain {item_id: adapter_path} JSON
    # (eval_vllm._load_route_map does json.load and rejects anything else). Writing the
    # parquet to a `.json` path -- which is what the emitted job asked for -- meant the
    # routed eval could never load its own route map. Two files, two formats, named honestly.
    ap.add_argument("--route-map", default=None,
                    help="JSON {item_id: adapter_path} for eval_vllm --route-map")
    ap.add_argument("--report", default=str(ROUTER_RESULTS_DIR / "routing_report.json"))
    args = ap.parse_args(argv)

    ck = load_checkpoint(args.router)
    fs = load_features(args.features)
    amap = json.loads(Path(args.adapter_map).read_text()) if args.adapter_map else None
    rows = route_features(fs, ck, adapter_map=amap)

    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)

    if args.route_map:
        rm = Path(args.route_map)
        rm.parent.mkdir(parents=True, exist_ok=True)
        rm.write_text(json.dumps({r["item_id"]: r["adapter"] for r in rows}, indent=2))

    cm = confusion_matrix(rows)
    rep = {
        "router_val_accuracy": ck.val_accuracy,
        "router_best_epoch": ck.best_epoch,
        "class_order": ck.class_order,
        "n_items": len(rows),
        "overall_route_accuracy": float(
            np.mean([r["correct_route"] for r in rows if not r["is_heldout"]])
        ) if any(not r["is_heldout"] for r in rows) else None,
        "confusion_matrix": cm,
        "entropy": entropy_report(rows),
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(rep, indent=2))

    print(f"wrote {out} ({len(df)} rows) and {args.report}"
          + (f" and {args.route_map}" if args.route_map else ""))
    print(f"  router val_acc={ck.val_accuracy:.4f}  overall route_acc={rep['overall_route_accuracy']}")
    hdr = "true\\routed".ljust(12) + "".join(c.rjust(7) for c in TRAINABLE_CONDITIONS)
    print("  " + hdr)
    for t, r in cm.items():
        print("  " + t.ljust(12) + "".join(str(r[c]).rjust(7) for c in TRAINABLE_CONDITIONS))
    e = rep["entropy"]
    for c, v in e["per_condition"].items():
        print(f"  entropy[{c}] n={v['n']} mean={v['entropy_mean']} median={v['entropy_median']}")
    if "mannwhitney" in e:
        print(f"  H1 vs held-in entropy: U={e['mannwhitney']['U']:.0f} "
              f"p={e['mannwhitney']['p']:.3g} rb={e['mannwhitney']['rank_biserial']:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
