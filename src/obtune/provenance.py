"""Run provenance — the record that makes a result trustworthy (CLAUDE.md §4).

Captures, for every kept run: exact command, config path + resolved config, script
sha256(s), seed, GPU id(s) + timestamp, adapter/base-model identity, and best-effort
library versions. Written as `run_manifest.json` alongside the run's outputs.

Adapted from transcoders/src/provenance.py; the dictionary-identity field is
replaced by adapter identity (checkpoint sha + base model revision).
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from obtune.config import PROJECT_ROOT


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_dir(path: str | Path, patterns: tuple[str, ...] = ("*.safetensors", "*.json")) -> str:
    """Stable hash of a directory's contents (used for adapter checkpoint identity)."""
    p = Path(path)
    h = hashlib.sha256()
    files = sorted({f for pat in patterns for f in p.rglob(pat)})
    for f in files:
        h.update(str(f.relative_to(p)).encode())
        h.update(sha256_file(f).encode())
    return h.hexdigest()


def _lib_versions() -> dict[str, str]:
    """Best-effort versions of the libraries that affect results. Never raises."""
    versions: dict[str, str] = {"python": sys.version.split()[0], "platform": platform.platform()}
    for mod in ("torch", "transformers", "peft", "trl", "vllm", "numpy"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception:
            versions[mod] = "absent"
    return versions


@dataclass
class RunManifest:
    experiment: str
    run_id: str
    seed: int
    config_path: str
    config_resolved: dict[str, Any]
    model_hf_id: str | None = None
    model_revision_resolved: str | None = None
    adapter: dict[str, Any] | None = None  # {path, sha256, train_cond, rank, base_model}
    gpu_visible: str | None = field(default_factory=lambda: os.environ.get("CUDA_VISIBLE_DEVICES"))
    command: str = field(default_factory=lambda: " ".join(sys.argv))
    git_commit: str | None = None
    script_sha256: dict[str, str] = field(default_factory=dict)
    started_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_utc: str | None = None
    libraries: dict[str, str] = field(default_factory=_lib_versions)
    extra: dict[str, Any] = field(default_factory=dict)

    def hash_scripts(self, paths: list[str | Path]) -> "RunManifest":
        """Hash scripts for provenance. Relative paths are anchored to PROJECT_ROOT so the
        hashes are recorded regardless of CWD; a missing script is an error, not a skip —
        an empty hash field would silently break §4 provenance."""
        for p in paths:
            p = Path(p)
            if not p.is_absolute():
                p = PROJECT_ROOT / p
            if not p.exists():
                raise FileNotFoundError(f"provenance: script to hash not found: {p}")
            key = str(p.relative_to(PROJECT_ROOT) if p.is_relative_to(PROJECT_ROOT) else p)
            self.script_sha256[key] = sha256_file(p)
        return self

    def capture_git(self) -> "RunManifest":
        import subprocess

        try:
            self.git_commit = subprocess.check_output(
                ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"], text=True
            ).strip()
        except Exception:
            self.git_commit = None
        return self

    def finalize(self) -> "RunManifest":
        self.finished_utc = datetime.now(timezone.utc).isoformat()
        return self

    def write(self, out_dir: str | Path) -> Path:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "run_manifest.json"
        path.write_text(json.dumps(asdict(self), indent=2, default=str))
        return path
