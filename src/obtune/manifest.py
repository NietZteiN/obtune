"""SHA manifests over the data tree — quarantine enforcement layer 4.

A manifest records, for every generated data file, its sha256 and row-level facts
(row count, conditions present). `verify` then answers three questions that the
loader guard alone cannot:

  1. Has a file changed since it was generated? (silent corruption / manual edit)
  2. Does any file in the training tree share a sha256 with a quarantined file?
     (the same H1 bytes copied under a legal path)
  3. Does any training file *contain* H1-family markers, whatever its label says?
     (leakage through a mislabeled or badly-configured generator — this is the
     check that would catch javascript-obfuscator's default-on string arrays, or
     the legacy ICSE JS L2/L3 rows whose dispatch tables are an H1-family feature)

Check 3 is the important one: labels can be wrong, content cannot.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from obtune.config import load_config
from obtune.paths import MANIFESTS_ROOT, QUARANTINE_ROOT, TRAIN_ROOT, iter_jsonl
from obtune.provenance import sha256_file


@dataclass
class FileEntry:
    path: str  # relative to the data root
    sha256: str
    bytes: int
    rows: int | None = None
    conditions: list[str] = field(default_factory=list)


@dataclass
class Manifest:
    name: str
    created_utc: str
    files: list[FileEntry] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Manifest":
        d = json.loads(Path(path).read_text())
        return cls(name=d["name"], created_utc=d["created_utc"],
                   files=[FileEntry(**f) for f in d["files"]])


def _describe(path: Path, root: Path) -> FileEntry:
    entry = FileEntry(path=str(path.relative_to(root)), sha256=sha256_file(path),
                      bytes=path.stat().st_size)
    if path.suffix == ".jsonl":
        conds: set[str] = set()
        n = 0
        for row in iter_jsonl(path):
            n += 1
            c = row.get("condition")
            if isinstance(c, str):
                conds.add(c)
        entry.rows = n
        entry.conditions = sorted(conds)
    return entry


def build(root: Path, name: str, patterns: Iterable[str] = ("*.jsonl", "*.json")) -> Manifest:
    files = sorted({f for pat in patterns for f in root.rglob(pat)})
    m = Manifest(name=name, created_utc=datetime.now(timezone.utc).isoformat())
    m.files = [_describe(f, root) for f in files if f.is_file()]
    return m


def write(root: Path, name: str, out: Path | None = None) -> Path:
    m = build(root, name)
    out = out or (MANIFESTS_ROOT / f"{name}.manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(m.to_json())
    return out


def h1_marker_patterns() -> list[re.Pattern[str]]:
    cfg = load_config("conditions.yaml")
    return [re.compile(p, re.IGNORECASE) for p in cfg["h1_marker_patterns"]]


def scan_for_h1_markers(path: Path, patterns: list[re.Pattern[str]] | None = None) -> list[dict[str, Any]]:
    """Return every training row whose code matches an H1-family marker.

    Scans the `code` field specifically rather than the raw file text: a filename or
    a metadata note mentioning "base64" is not leakage, obfuscated code containing a
    base64 decoder is.
    """
    patterns = patterns or h1_marker_patterns()
    hits: list[dict[str, Any]] = []
    if path.suffix != ".jsonl":
        return hits
    for i, row in enumerate(iter_jsonl(path), 1):
        code = row.get("code")
        if not isinstance(code, str):
            continue
        for pat in patterns:
            if pat.search(code):
                hits.append({
                    "file": str(path), "line": i,
                    "program_id": row.get("program_id"),
                    "condition": row.get("condition"),
                    "pattern": pat.pattern,
                })
                break
    return hits


@dataclass
class VerifyReport:
    ok: bool
    changed: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    shared_with_quarantine: list[str] = field(default_factory=list)
    h1_marker_hits: list[dict[str, Any]] = field(default_factory=list)
    h1_labeled_in_train: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.ok:
            return "manifest verify: OK"
        parts = []
        if self.changed:
            parts.append(f"{len(self.changed)} changed file(s)")
        if self.missing:
            parts.append(f"{len(self.missing)} missing file(s)")
        if self.shared_with_quarantine:
            parts.append(f"{len(self.shared_with_quarantine)} training file(s) sharing bytes with quarantine")
        if self.h1_marker_hits:
            parts.append(f"{len(self.h1_marker_hits)} training row(s) containing H1 markers")
        if self.h1_labeled_in_train:
            parts.append(f"{len(self.h1_labeled_in_train)} H1-labeled training file(s)")
        return "manifest verify: FAILED — " + "; ".join(parts)


def verify(train_root: Path = TRAIN_ROOT, quarantine_root: Path = QUARANTINE_ROOT,
           manifest_path: Path | None = None) -> VerifyReport:
    rep = VerifyReport(ok=True)

    manifest_path = manifest_path or (MANIFESTS_ROOT / "train.manifest.json")
    if manifest_path.exists():
        m = Manifest.load(manifest_path)
        for entry in m.files:
            p = train_root / entry.path
            if not p.exists():
                rep.missing.append(entry.path)
            elif sha256_file(p) != entry.sha256:
                rep.changed.append(entry.path)

    q_shas: set[str] = set()
    if quarantine_root.exists():
        for f in quarantine_root.rglob("*.jsonl"):
            q_shas.add(sha256_file(f))

    patterns = h1_marker_patterns()
    if train_root.exists():
        for f in sorted(train_root.rglob("*.jsonl")):
            if q_shas and sha256_file(f) in q_shas:
                rep.shared_with_quarantine.append(str(f))
            rep.h1_marker_hits.extend(scan_for_h1_markers(f, patterns))
            if any(r.get("condition") == "H1" for r in iter_jsonl(f)):
                rep.h1_labeled_in_train.append(str(f))

    rep.ok = not (rep.changed or rep.missing or rep.shared_with_quarantine
                  or rep.h1_marker_hits or rep.h1_labeled_in_train)
    return rep
