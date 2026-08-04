"""Quarantine enforcement layer 2: static lint for bypasses of the loader guard.

Layer 1 (paths.load_training_jsonl) only helps if every training read goes through it.
This test greps the source tree for the two ways that discipline gets broken:
  * a raw file read against a data/ path outside paths.py, and
  * an import of the H1 generators outside scripts/gen_h1_quarantined.py.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "obtune"
SCRIPTS = ROOT / "scripts"

# paths.py is the guard itself; the H1 generator is the sanctioned H1 importer;
# gen scripts legitimately write to the quarantine tree.
LOADER_EXEMPT = {SRC / "paths.py"}
H1_IMPORT_EXEMPT = {SCRIPTS / "gen_h1_quarantined.py"}

RAW_READ = re.compile(
    r"""(?:open\s*\(|\.read_text\s*\(|pd\.read_(?:json|parquet|csv)\s*\(|load_dataset\s*\()"""
)
DATA_PATH_HINT = re.compile(r"""data/train|TRAIN_ROOT|data/quarantine|QUARANTINE_ROOT""")


def _py_files() -> list[Path]:
    files = list(SRC.rglob("*.py")) + list(SCRIPTS.rglob("*.py"))
    return [f for f in files if "__pycache__" not in f.parts]


def test_no_raw_reads_of_the_training_tree():
    """Reading data/train/ outside paths.py bypasses the H1-label rejection."""
    offenders = []
    for f in _py_files():
        if f in LOADER_EXEMPT:
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if RAW_READ.search(line) and DATA_PATH_HINT.search(line):
                offenders.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not offenders, (
        "training-tree reads must go through paths.load_training_jsonl:\n" + "\n".join(offenders)
    )


def test_h1_modules_imported_only_by_the_generator():
    """obf/h1/* must be unreachable from any code path a training job can enter."""
    offenders = []
    for f in _py_files():
        if f in H1_IMPORT_EXEMPT:
            continue
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(".h1" in n or n.endswith("py_h1") or "obf.h1" in n for n in names):
                offenders.append(f"{f.relative_to(ROOT)}:{node.lineno}: imports {names}")
    assert not offenders, (
        "only scripts/gen_h1_quarantined.py may import obf/h1/*:\n" + "\n".join(offenders)
    )


def test_javascript_obfuscator_confined_to_h1():
    """javascript-obfuscator's stringArray is default-on and deadCodeInjection forces it,
    so any use outside the H1 generator would leak the held-out feature into training."""
    offenders = []
    for f in list((ROOT / "src").rglob("*.mjs")) + list((ROOT / "src").rglob("*.js")):
        if "h1" in f.parts or f.name.startswith("js_h1"):
            continue
        if "javascript-obfuscator" in f.read_text():
            offenders.append(str(f.relative_to(ROOT)))
    assert not offenders, (
        "javascript-obfuscator may only be used by the H1 generator: " + ", ".join(offenders)
    )


def test_loader_guard_rejects_quarantine_and_eval(tmp_path):
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from obtune import paths

    quarantined = paths.QUARANTINE_ROOT / "h1" / "python.jsonl"
    with pytest.raises(paths.QuarantineViolation):
        paths.assert_trainable_path(quarantined)

    eval_row = paths.EVAL_ROOT / "testset" / "base" / "dataset_a.jsonl"
    with pytest.raises(paths.QuarantineViolation):
        paths.assert_trainable_path(eval_row)

    outside = tmp_path / "somewhere_else.jsonl"
    outside.write_text("{}\n")
    with pytest.raises(paths.QuarantineViolation):
        paths.assert_trainable_path(outside)


def test_loader_rejects_h1_labeled_rows_inside_the_training_tree(tmp_path, monkeypatch):
    """Even a correctly-placed file is rejected if its rows claim to be H1."""
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from obtune import paths

    fake_train = tmp_path / "train"
    fake_train.mkdir()
    f = fake_train / "python.jsonl"
    f.write_text('{"condition": "L1b"}\n{"condition": "H1"}\n')
    monkeypatch.setattr(paths, "TRAIN_ROOT", fake_train)
    monkeypatch.setattr(paths, "QUARANTINE_ROOT", tmp_path / "quarantine")
    monkeypatch.setattr(paths, "EVAL_ROOT", tmp_path / "eval")
    with pytest.raises(paths.QuarantineViolation, match="quarantine breach"):
        paths.load_training_jsonl(f)
