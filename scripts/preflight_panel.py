#!/usr/bin/env python
"""Preflight: is every model weight and every data artifact the plan needs actually on disk?

    python scripts/preflight_panel.py            # audit, exit 1 if anything the plan needs is missing
    python scripts/preflight_panel.py --json     # machine-readable

WHY THIS EXISTS. Two failure modes cost real queue time on this cluster, and neither shows
up until a job has already been allocated a GPU:

  1. A HuggingFace snapshot that *looks* present but is short a shard. `snapshot_download`
     writes blobs under `blobs/` and symlinks them into `snapshots/<rev>/`, so a killed
     download leaves a directory tree with the right names and a missing or dangling file.
     The authority is the weight index (`model.safetensors.index.json`): every distinct file
     named in its `weight_map` must exist, resolve through its symlink, and be non-empty.
     A single-shard model has no index, so `model.safetensors` itself is the check.
  2. A data tree that is present but not what the manifests say it is. That is what
     `check_manifest.py` is for; this script defers to it rather than reimplementing it.

Two distinctions the first version of this script got wrong, both worth keeping:
  * A `.incomplete` blob beside a COMPLETE set of shards is orphaned scratch from an
     interrupted earlier attempt, not a broken model -- codellama-34b resolves all seven
     shards (62.9 GB) and still carries 26 GB of them. That is a disk-space report, not a
     blocker, and deleting it is a human decision (CLAUDE.md, destructive commands).
  * `role: baseline_only` models were never run and are not on the critical path, so they
     are reported as OPTIONAL rather than counted against readiness.

The model list is read from configs/models.yaml, not hard-coded: a model added to the panel
is preflighted automatically. `role: barred` entries are skipped -- they are kept only so
frozen results resolve (CLAUDE.md / docs/MODEL_AND_DATA_SELECTION.md), and downloading them
would be pointless.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.paths import EVAL_ROOT, TRAIN_ROOT  # noqa: E402

HF_HOME = Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface"))
HUB = HF_HOME / "hub"

# Conditions the approved plan reads. F2's X1-composites are NOT here: they do not exist
# yet and are built from data/train/base, which this script does check.
LADDER = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
HELDOUT_FAMILY = ["X1", "X1m", "X1s"]
COMPOSITES_D2 = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
COMPOSITES_D34 = ["C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4"]


def _snapshot_dir(hf_id: str) -> Path | None:
    d = HUB / ("models--" + hf_id.replace("/", "--")) / "snapshots"
    if not d.is_dir():
        return None
    revs = sorted((p for p in d.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime)
    return revs[-1] if revs else None


def check_model(key: str, spec: dict) -> dict:
    hf_id = spec["hf_id"]
    out = {"key": key, "hf_id": hf_id, "role": spec.get("role", "?"), "ok": False, "detail": ""}
    snap = _snapshot_dir(hf_id)
    if snap is None:
        out["detail"] = "not downloaded (no snapshot directory)"
        return out

    index = snap / "model.safetensors.index.json"
    if index.exists():
        shards = sorted(set(json.loads(index.read_text())["weight_map"].values()))
    elif (snap / "model.safetensors").exists():
        shards = ["model.safetensors"]          # genuinely single-shard
    else:
        # Neither the index nor a single-file checkpoint: only metadata has been fetched
        # (this is exactly what `hf_hub_download config.json` leaves behind).
        out["detail"] = "metadata only — weights not downloaded"
        return out
    missing, empty = [], []
    total = 0
    for name in shards:
        f = snap / name
        # resolve(): a dangling symlink into blobs/ is the signature of a killed download
        if not f.exists() or not f.resolve().exists():
            missing.append(name)
            continue
        size = f.resolve().stat().st_size
        total += size
        if size == 0:
            empty.append(name)

    # Tokenizer and config must be there too -- an eval dies on a missing tokenizer just as
    # surely as on a missing shard, and it is 300 kB, so it is easy to miss.
    need = ["config.json"]
    tok_ok = any((snap / n).exists() for n in ("tokenizer.json", "tokenizer.model", "vocab.json"))
    missing_meta = [n for n in need if not (snap / n).exists()] + ([] if tok_ok else ["tokenizer.*"])

    incomplete = list((HUB / ("models--" + hf_id.replace("/", "--")) / "blobs").glob("*.incomplete"))

    out["n_shards"] = len(shards)
    out["gb"] = round(total / 2**30, 1)
    stale = round(sum(f.stat().st_size for f in incomplete) / 2**30, 1)
    out["stale_gb"] = stale
    if missing or empty or missing_meta:
        out["detail"] = "; ".join(filter(None, [
            f"missing shards: {missing}" if missing else "",
            f"zero-length shards: {empty}" if empty else "",
            f"missing metadata: {missing_meta}" if missing_meta else "",
        ]))
        if incomplete:
            out["detail"] += f"; {len(incomplete)} .incomplete blob(s) — a download is in flight"
    else:
        out["ok"] = True
        out["detail"] = f"{len(shards)} shard(s), {out['gb']} GB"
        if incomplete:
            # Complete model, orphaned scratch beside it.
            out["detail"] += (f"  [+{stale} GB of orphaned .incomplete blobs from an earlier "
                              f"attempt — reclaimable, not a blocker]")
    return out


def check_gated_repos() -> list[dict]:
    """A gated repo must actually LOAD, not merely have its shards on disk.

    Shard-resolution says nothing about credentials: `huggingface_hub` reads the token from
    `$HF_HOME/token`, so relocating HF_HOME without it leaves every shard present and every
    gated repo failing with `GatedRepoError: 401` at the first hub call. That is exactly what
    happened on 2026-09-10 (job 389173 died on a model whose weights it could already read),
    and this file's own "OK, 5 shards, 22.7 GB" line said the model was fine.

    Loading the tokenizer is the cheapest thing that exercises the credential path.
    """
    from obtune.config import load_config as _lc
    rows = []
    token = HF_HOME / "token"
    rows.append({"item": "HF token present in the active HF_HOME", "ok": token.exists(),
                 "detail": str(token) if token.exists()
                           else f"MISSING at {token} — gated repos will 401"})
    try:
        from transformers import AutoTokenizer
    except Exception as exc:
        rows.append({"item": "gated-repo load", "ok": False,
                     "detail": f"transformers unavailable: {type(exc).__name__}"})
        return rows
    models = _lc("models.yaml")["models"]
    # One gated repo per vendor is enough to prove the credential works.
    probes = [k for k, v in models.items()
              if v.get("role") != "barred"
              and any(v["hf_id"].startswith(p) for p in ("google/", "meta-llama/"))][:3]
    for k in probes:
        hf_id = models[k]["hf_id"]
        try:
            AutoTokenizer.from_pretrained(hf_id)
            rows.append({"item": f"gated repo loads: {k}", "ok": True, "detail": hf_id})
        except Exception as exc:
            rows.append({"item": f"gated repo loads: {k}", "ok": False,
                         "detail": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return rows


def check_eval_phases() -> list[dict]:
    """Every eval config's `phase` must be in TrialRow's literal.

    This has now cost three jobs: `selfcons_generic` (376082, crashed on cell 1),
    `model_family: pretrained` (388497) and `basecheck_1shot` (388897) — each time a new config
    reached a GPU, ran to completion, and died writing the first row. The literal is a deliberate
    guard against typos and should stay closed; what was missing is a check that runs before the
    queue wait rather than after it.
    """
    from obtune.schema import TrialRow
    import typing
    allowed = set(typing.get_args(TrialRow.model_fields["phase"].annotation))
    rows = []
    for cfg in sorted(Path("configs/eval").glob("*.y*ml")):
        if cfg.name.startswith("_"):
            continue
        try:
            phase = load_config(f"eval/{cfg.name}").get("phase")
        except Exception:
            continue
        if phase and phase not in allowed:
            rows.append({"item": f"eval/{cfg.name} phase={phase!r}", "ok": False,
                         "detail": "NOT in TrialRow.phase — every row write will fail"})
    if not rows:
        rows.append({"item": "eval config phases", "ok": True,
                     "detail": "all in TrialRow.phase"})
    return rows


def check_data() -> list[dict]:
    rows = []

    def add(name, ok, detail):
        rows.append({"item": name, "ok": bool(ok), "detail": detail})

    for label, conds, root, sub in (
        ("train pairs", LADDER + HELDOUT_FAMILY, TRAIN_ROOT, "pairs"),
        ("heldout eval items", LADDER + HELDOUT_FAMILY + COMPOSITES_D2 + COMPOSITES_D34,
         EVAL_ROOT, "heldout/items"),
    ):
        missing = [c for c in conds
                   if not (root / sub / c / "python.jsonl").exists()]
        add(f"{label} (python)", not missing,
            "all present" if not missing else f"missing: {missing}")

    base = TRAIN_ROOT / "base" / "python.jsonl"
    add("corpus base (F2 builds new composites from this)", base.exists(),
        f"{base}" if base.exists() else "MISSING")

    splits = Path("data/splits/python.json")
    add("program-level splits", splits.exists(), str(splits))

    human = [Path("data/human/paper2_graded.csv"), Path("data/human/paper3_graded.csv")]
    add("human-alignment data", all(p.exists() for p in human),
        "both present" if all(p.exists() for p in human)
        else f"missing: {[str(p) for p in human if not p.exists()]}")

    # Raw HF datasets are needed ONLY to rebuild the corpus. The corpus itself transferred,
    # so this is reported as information, never as a blocker (CLAUDE.md §2).
    # Datasets live under hub/datasets--* in the current HF cache layout, NOT under
    # HF_HOME/datasets (which holds only lock files here). Looking in the wrong place
    # reported "cached: none" for three datasets that are in fact present.
    have = {p.name.replace("datasets--", "", 1).replace("--", "/") for p in HUB.glob("datasets--*")}
    src = load_config("sources.yaml")["python"]
    want = {e["hf_id"] for tier in src.values() for e in tier if "hf_id" in e}
    rows.append({"item": "raw HF datasets (corpus REBUILD only)", "ok": True,
                 "detail": f"cached: {sorted(have) or 'none'} | not cached: {sorted(want - have)}"
                           " — not needed unless the corpus is rebuilt"})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    models = load_config("models.yaml")["models"]
    mrows = [check_model(k, v) for k, v in models.items() if v.get("role") != "barred"]
    # baseline_only models were never run and are not on the critical path.
    for r in mrows:
        if r["role"] == "baseline_only" and not r["ok"]:
            r["optional"] = True
    drows = check_data() + check_eval_phases() + check_gated_repos()

    if a.json:
        print(json.dumps({"models": mrows, "data": drows}, indent=2))
    else:
        print(f"HF_HOME = {HF_HOME}\n")
        print("MODELS")
        for r in mrows:
            tag = "OK " if r["ok"] else ("opt" if r.get("optional") else "NO ")
            print(f"  {tag} {r['key']:18s} {r['role']:18s} {r['detail']}")
        stale = round(sum(r.get("stale_gb", 0) for r in mrows), 1)
        if stale:
            print(f"\n  ({stale} GB of orphaned .incomplete blobs in the HF cache — "
                  f"reclaimable; deletion is a human decision)")
        print("\nDATA")
        for r in drows:
            print(f"  {'OK ' if r['ok'] else 'NO '} {r['item']:48s} {r['detail']}")
        bad = ([r['key'] for r in mrows if not r['ok'] and not r.get("optional")]
               + [r['item'] for r in drows if not r['ok']])
        print("\n" + ("READY" if not bad else f"NOT READY: {bad}"))
    blocking = [r for r in mrows if not r["ok"] and not r.get("optional")]
    blocking += [r for r in drows if not r["ok"]]
    return 0 if not blocking else 1


if __name__ == "__main__":
    raise SystemExit(main())
