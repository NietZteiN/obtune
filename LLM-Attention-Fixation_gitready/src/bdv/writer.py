from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

from .schema import BDV_SCHEMA


def save_record_layers_full_json_gz(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return path


def save_bdv_schema(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path
    path.write_text(json.dumps(BDV_SCHEMA, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return path


def save_bdv_features_npz(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    availability_json = json.dumps(payload.get("availability", {}), sort_keys=True)
    np.savez_compressed(
        path,
        schema_version=np.array(payload.get("schema_version", "bdv_v1")),
        bucket_count=np.array(payload.get("bucket_count", 1), dtype=np.int32),
        phi_head=np.asarray(payload["phi_head"], dtype=np.float16),
        phi_layer=np.asarray(payload["phi_layer"], dtype=np.float16),
        phi_global=np.asarray(payload["phi_global"], dtype=np.float32),
        bucket_counts=np.asarray(payload.get("bucket_counts", []), dtype=np.int32),
        availability_json=np.array(availability_json),
        pair_id=np.array(payload.get("pair_id", "")),
        variant_type=np.array(payload.get("variant_type", "")),
        is_correct=np.array(bool(payload.get("is_correct", False)), dtype=np.bool_),
    )
    return path

