#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np


def _nanmean_stack(arrs: List[np.ndarray]) -> np.ndarray:
    if not arrs:
        return np.array([])
    return np.nanmean(np.stack(arrs, axis=0), axis=0)


def _infer_level(path: Path) -> str:
    m = re.search(r"(level[0-9]+|step[0-9]+)", path.as_posix(), flags=re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return "all"


def _load_npz(path: Path) -> Dict[str, object]:
    data = np.load(path, allow_pickle=False)
    return {
        "path": path,
        "phi_head": data["phi_head"],
        "phi_layer": data["phi_layer"],
        "phi_global": data["phi_global"],
        "pair_id": str(data["pair_id"].item()) if "pair_id" in data else "",
        "variant_type": str(data["variant_type"].item()) if "variant_type" in data else "",
        "is_correct": bool(data["is_correct"].item()) if "is_correct" in data else False,
        "level": _infer_level(path),
    }


def _compute_goodbad(records: List[Dict[str, object]]) -> Dict[str, np.ndarray]:
    good = [r for r in records if bool(r["is_correct"])]
    bad = [r for r in records if not bool(r["is_correct"])]
    if not good or not bad:
        raise RuntimeError("goodbad mode requires both correct and incorrect samples.")
    out = {}
    for key in ("phi_head", "phi_layer", "phi_global"):
        good_mean = _nanmean_stack([np.asarray(r[key]) for r in good])
        bad_mean = _nanmean_stack([np.asarray(r[key]) for r in bad])
        out[key] = good_mean - bad_mean
    return out


def _compute_pairdelta(records: List[Dict[str, object]]) -> Dict[str, np.ndarray]:
    grouped: Dict[str, Dict[str, np.ndarray]] = defaultdict(dict)
    for r in records:
        pid = str(r["pair_id"])
        variant = str(r["variant_type"]).lower()
        if not pid or variant not in {"plain", "obf"}:
            continue
        grouped[pid][variant] = np.asarray(r["phi_head"]), np.asarray(r["phi_layer"]), np.asarray(r["phi_global"])
    deltas_h = []
    deltas_l = []
    deltas_g = []
    for pair in grouped.values():
        if "plain" not in pair or "obf" not in pair:
            continue
        h_plain, l_plain, g_plain = pair["plain"]
        h_obf, l_obf, g_obf = pair["obf"]
        deltas_h.append(h_obf - h_plain)
        deltas_l.append(l_obf - l_plain)
        deltas_g.append(g_obf - g_plain)
    if not deltas_h:
        raise RuntimeError("pairdelta mode found no complete plain/obf pairs.")
    return {
        "phi_head": _nanmean_stack(deltas_h),
        "phi_layer": _nanmean_stack(deltas_l),
        "phi_global": _nanmean_stack(deltas_g),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute BDV vectors from saved bdv_features*.npz artifacts.")
    ap.add_argument("--input-root", type=Path, required=True)
    ap.add_argument("--glob", type=str, default="**/bdv_features_*.npz")
    ap.add_argument("--mode", choices=["goodbad", "pairdelta"], default="goodbad")
    ap.add_argument("--by-level", action="store_true")
    ap.add_argument("--out-prefix", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(args.input_root.glob(args.glob))
    if not files:
        raise FileNotFoundError(f"No files matched {args.input_root}/{args.glob}")
    records = [_load_npz(p) for p in files]

    groups: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    if args.by_level:
        for r in records:
            groups[str(r["level"])].append(r)
    else:
        groups["all"] = records

    summary = {"mode": args.mode, "groups": {}, "num_files": len(records)}
    for gname, grecs in groups.items():
        out = _compute_goodbad(grecs) if args.mode == "goodbad" else _compute_pairdelta(grecs)
        head_path = Path(f"{args.out_prefix}_{gname}_phi_head.npy")
        layer_path = Path(f"{args.out_prefix}_{gname}_phi_layer.npy")
        global_path = Path(f"{args.out_prefix}_{gname}_phi_global.npy")
        head_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(head_path, out["phi_head"])
        np.save(layer_path, out["phi_layer"])
        np.save(global_path, out["phi_global"])
        summary["groups"][gname] = {
            "count": len(grecs),
            "phi_head_path": str(head_path),
            "phi_layer_path": str(layer_path),
            "phi_global_path": str(global_path),
        }

    summary_path = Path(f"{args.out_prefix}_summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[BDV] wrote summary -> {summary_path}")


if __name__ == "__main__":
    main()

