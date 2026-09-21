"""Split leakage, checked three ways.

CLAUDE.md §4 lists split leakage first among the silent failures, because an obfuscated
variant of a training program in the test set inflates every transfer number at once and
looks like a result. These assertions exist because on 2026-09-20 two hand-written leakage
checks BOTH passed in the reassuring direction before a third found real contamination:

  * comparing evaluation ids against training ids found zero overlap. True, and irrelevant:
    the ids differ by language while the programs do not.
  * comparing against every id under data/train/ found contamination everywhere, including
    across the clean Python panel. That tree is the POOL; the partition lives in
    data/splits/<language>.json and is applied at load time.

The split file is the authority. Tests are skipped, not failed, when the data is absent, so
a checkout without data/ stays usable.
"""
from __future__ import annotations
import json, re, hashlib, collections
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT/"data/splits"

def _assignment(lang):
    f = SPLITS/f"{lang}.json"
    if not f.exists(): pytest.skip(f"no split file for {lang}")
    return json.loads(f.read_text())["assignment"]

def _norm(code: str) -> str:
    code = re.sub(r"#.*", "", code)
    return hashlib.sha1(re.sub(r"\s+", " ", code).strip().encode()).hexdigest()

def _l0_rows(lang):
    f = ROOT/f"data/train/pairs/L0/{lang}.jsonl"
    if not f.exists(): pytest.skip(f"no L0 pool for {lang}")
    out = []
    with f.open() as fh:
        for line in fh:
            try: r = json.loads(line)
            except Exception: continue
            pid = r.get("snippet_id") or r.get("program_id")
            if pid and r.get("code"): out.append((str(pid), r["code"]))
    return out


@pytest.mark.parametrize("lang", ["python", "javascript"])
def test_split_partitions_by_program(lang):
    """Every program has exactly one assignment. Partition, not overlap."""
    asg = _assignment(lang)
    buckets = collections.Counter(asg.values())
    assert set(buckets) <= {"train", "val", "test"}, buckets
    assert buckets["train"] and buckets["test"], buckets


@pytest.mark.parametrize("lang", ["python", "javascript"])
def test_no_duplicate_program_body_across_split(lang):
    """The same program under two ids, on opposite sides of the split, is leakage.

    Checked on L0, the unobfuscated parent: identical normalized bodies there are the
    same program whatever the ids say.
    """
    asg = _assignment(lang)
    tr = {k for k, v in asg.items() if v == "train"}
    te = {k for k, v in asg.items() if v == "test"}
    by_body = collections.defaultdict(set)
    for pid, code in _l0_rows(lang):
        by_body[_norm(code)].add(pid)
    straddling = [sorted(p) for p in by_body.values() if (p & tr) and (p & te)]
    assert not straddling, f"{len(straddling)} program bodies span train and test: {straddling[:3]}"


def test_javascript_eval_programs_are_ports_of_python_training_programs():
    """CruxEval-X and HumanEval-X are ports, so a JS test program may be a Python TRAIN
    program in another language. This does NOT fail -- it is a property of the corpora, not
    a bug -- but any cross-language analysis must filter on it, and this pins the number so
    a corpus change cannot move it unnoticed.

    scripts/analysis/78_crosslang.py excludes these by default.
    """
    jsa, pya = _assignment("javascript"), _assignment("python")
    js_test = {k for k, v in jsa.items() if v == "test"}
    py_train = {k for k, v in pya.items() if v == "train"}
    twin_of = {"cruxevalx": "cruxeval_sample_{n}", "humaneval": "humaneval_py_{n}"}

    def twin(sid):
        m = re.match(r"^(.*?)_js_(\d+)$", sid)
        if not m: return None
        t = twin_of.get(m.group(1))
        return None if t is None else t.format(n=m.group(2))

    contaminated = {s for s in js_test if (t := twin(s)) and t in py_train}
    assert len(js_test) == 168, len(js_test)
    assert len(contaminated) == 87, (
        f"{len(contaminated)} of {len(js_test)} JS test programs have a Python-train twin; "
        "78_crosslang.py's filter and the paper's stated subset size both assume 87")
