"""Build the synthetic data tree the training/eval stack is developed and tested against.

The real corpus (data/) is produced by the peer-owned obf/, corpus/ and testset/
modules and does not exist yet. This generator stands in for it so the training and
evaluation code can actually be *run* today rather than merely written.

What is real here and what is not
---------------------------------
REAL: the gold labels. Every program and every variant is executed through
`obtune.exec.pool` and the canonical output is taken from the executor, exactly as the
real pipeline does. A variant whose outputs differ from its L0 parent is a hard error,
so the fixture ships its own miniature semantic gate.

NOT REAL: the transforms. L1b/L1r/L2 are done with a hand-written rename map over
programs whose identifiers we control, and S1/S2/H1 are structural stand-ins with the
right *shape* (dispatch loop; opaque predicate + dead helper; char-code string
decoder). They are not the obf/ implementations and must never be used to make a
claim about a condition — they exist to give the loaders, the collator, the grader and
the parquet/stats path real bytes to chew on.

Usage:
    PYTHONPATH=src python tests/fixtures/make_fixtures.py [--out tests/fixtures/data]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from obtune.exec.pool import BatchItem, run_batch  # noqa: E402

SEED = 17
TRAIN_CONDITIONS = ("L0", "L1b", "L1r", "L2", "S1", "S2")
ALL_CONDITIONS = TRAIN_CONDITIONS + ("H1",)


@dataclass(frozen=True)
class Prog:
    pid: str
    language: str
    name: str
    params: tuple[str, ...]
    body: tuple[str, ...]  # unindented source lines of the function body
    cases: tuple[str, ...]  # args_repr strings
    role: str  # "train" | "val" | "test"
    dataset: str = "A"


PY_PROGRAMS: tuple[Prog, ...] = (
    Prog("fx_py_0001", "python", "running_total", ("nums", "start"),
         ("total = start", "out = []", "for item in nums:",
          "    total = total + item", "    out.append(total)", "return out"),
         ("([1, 2, 3], 10)", "([], 5)", "([-1, -2], 0)"), "train"),
    Prog("fx_py_0002", "python", "count_vowels", ("text",),
         ("hits = 0", "for ch in text:", "    if ch in 'aeiou':", "        hits = hits + 1",
          "return hits"),
         ("('hello world',)", "('xyz',)", "('AEIOUaeiou',)"), "train"),
    Prog("fx_py_0003", "python", "max_gap", ("nums",),
         ("if len(nums) < 2:", "    return 0", "ordered = sorted(nums)", "best = 0",
          "for idx in range(1, len(ordered)):", "    gap = ordered[idx] - ordered[idx - 1]",
          "    if gap > best:", "        best = gap", "return best"),
         ("([3, 9, 1, 20],)", "([5],)", "([2, 2, 2],)"), "train"),
    Prog("fx_py_0004", "python", "flip_map", ("pairs",),
         ("out = {}", "for key in pairs:", "    out[str(pairs[key])] = key", "return out"),
         ("({'x': 1, 'y': 2},)", "({},)", "({'only': 'one'},)"), "train"),
    Prog("fx_py_0005", "python", "clamp_all", ("nums", "low", "high"),
         ("out = []", "for item in nums:", "    val = item",
          "    if val < low:", "        val = low", "    if val > high:", "        val = high",
          "    out.append(val)", "return out"),
         ("([1, 9, 5], 2, 6)", "([], 0, 1)", "([-4, 4], -1, 1)"), "train"),
    Prog("fx_py_0006", "python", "mean_third", ("nums",),
         ("if not nums:", "    return 0", "total = 0", "for item in nums:",
          "    total = total + item", "return total / 3.0"),
         ("([1, 2],)", "([10, 10, 10],)", "([7],)"), "train"),
    Prog("fx_py_0007", "python", "run_lengths", ("text",),
         ("out = []", "prev = None", "count = 0", "for ch in text:",
          "    if ch == prev:", "        count = count + 1", "    else:",
          "        if prev is not None:", "            out.append([prev, count])",
          "        prev = ch", "        count = 1",
          "if prev is not None:", "    out.append([prev, count])", "return out"),
         ("('aaabb',)", "('',)", "('abc',)"), "train"),
    Prog("fx_py_0008", "python", "digit_total", ("value",),
         ("total = 0", "rest = abs(value)", "while rest > 0:",
          "    total = total + rest % 10", "    rest = rest // 10", "return total"),
         ("(9273,)", "(0,)", "(-45,)"), "train"),
    Prog("fx_py_0009", "python", "merge_sorted", ("left", "right"),
         ("out = []", "idx = 0", "jdx = 0",
          "while idx < len(left) and jdx < len(right):",
          "    if left[idx] <= right[jdx]:", "        out.append(left[idx])",
          "        idx = idx + 1", "    else:", "        out.append(right[jdx])",
          "        jdx = jdx + 1",
          "return out + left[idx:] + right[jdx:]"),
         ("([1, 4], [2, 3])", "([], [1])", "([5, 6], [])"), "val"),
    Prog("fx_py_0010", "python", "unique_sorted", ("nums",),
         ("out = []", "for item in sorted(nums):",
          "    if not out or out[-1] != item:", "        out.append(item)", "return out"),
         ("([3, 1, 3, 2],)", "([],)", "([1, 1, 1],)"), "val"),
    Prog("fx_py_0011", "python", "word_lengths", ("text",),
         ("out = {}", "for word in text.split():", "    out[word] = len(word)", "return out"),
         ("('the quick fox',)", "('',)", "('aa bb aa',)"), "test", "A"),
    Prog("fx_py_0012", "python", "dot_product", ("left", "right"),
         ("total = 0", "for idx in range(min(len(left), len(right))):",
          "    total = total + left[idx] * right[idx]", "return total"),
         ("([1, 2, 3], [4, 5, 6])", "([], [])", "([2], [3, 9])"), "test", "A"),
    Prog("fx_py_0013", "python", "is_mirror", ("text",),
         ("clean = ''", "for ch in text:", "    if ch != ' ':", "        clean = clean + ch",
          "return clean == clean[::-1]"),
         ("('never odd or even',)", "('abc',)", "('',)"), "test", "B"),
    Prog("fx_py_0014", "python", "fib_pair", ("count",),
         ("prev = 0", "cur = 1", "for _ in range(count):",
          "    prev, cur = cur, prev + cur", "return [prev, cur]"),
         ("(5,)", "(0,)", "(10,)"), "test", "B"),
)

JS_PROGRAMS: tuple[Prog, ...] = (
    Prog("fx_js_0001", "javascript", "runningTotal", ("nums", "start"),
         ("let total = start;", "const out = [];", "for (const item of nums) {",
          "    total = total + item;", "    out.push(total);", "}", "return out;"),
         ("([1, 2, 3], 10)", "([], 5)", "([-1, -2], 0)"), "train"),
    Prog("fx_js_0002", "javascript", "countVowels", ("text",),
         ("let hits = 0;", "for (const ch of text) {",
          "    if ('aeiou'.indexOf(ch) >= 0) { hits = hits + 1; }", "}", "return hits;"),
         ("('hello world',)", "('xyz',)", "('aeiou',)"), "train"),
    Prog("fx_js_0003", "javascript", "maxGap", ("nums",),
         ("if (nums.length < 2) { return 0; }",
          "const ordered = nums.slice().sort(function (p, q) { return p - q; });",
          "let best = 0;", "for (let idx = 1; idx < ordered.length; idx++) {",
          "    const gap = ordered[idx] - ordered[idx - 1];",
          "    if (gap > best) { best = gap; }", "}", "return best;"),
         ("([3, 9, 1, 20],)", "([5],)", "([2, 2, 2],)"), "train"),
    Prog("fx_js_0004", "javascript", "digitTotal", ("value",),
         ("let total = 0;", "let rest = Math.abs(value);", "while (rest > 0) {",
          "    total = total + (rest % 10);", "    rest = Math.floor(rest / 10);", "}",
          "return total;"),
         ("(9273,)", "(0,)", "(-45,)"), "val"),
    Prog("fx_js_0005", "javascript", "uniqueSorted", ("nums",),
         ("const out = [];",
          "const ordered = nums.slice().sort(function (p, q) { return p - q; });",
          "for (const item of ordered) {",
          "    if (out.length === 0 || out[out.length - 1] !== item) { out.push(item); }",
          "}", "return out;"),
         ("([3, 1, 3, 2],)", "([],)", "([1, 1, 1],)"), "test", "A"),
    Prog("fx_js_0006", "javascript", "dotProduct", ("left", "right"),
         ("let total = 0;",
          "const stop = Math.min(left.length, right.length);",
          "for (let idx = 0; idx < stop; idx++) {",
          "    total = total + left[idx] * right[idx];", "}", "return total;"),
         ("([1, 2, 3], [4, 5, 6])", "([], [])", "([2], [3, 9])"), "test", "B"),
)

# Misleading names for the L1b stand-in: plausible but unrelated domain vocabulary,
# the fibfib->smoothArea trap from configs/conditions.yaml.
L1B_NAMES = {
    "running_total": "smoothArea", "count_vowels": "primeIndex", "max_gap": "minStride",
    "flip_map": "sortRows", "clamp_all": "expandRange", "mean_third": "medianDepth",
    "run_lengths": "splitTokens", "digit_total": "hashSeed", "merge_sorted": "shuffleDeck",
    "unique_sorted": "duplicateAll", "word_lengths": "charFreq", "dot_product": "crossNorm",
    "is_mirror": "isAscending", "fib_pair": "gridBounds",
    "runningTotal": "smoothArea", "countVowels": "primeIndex", "maxGap": "minStride",
    "digitTotal": "hashSeed", "uniqueSorted": "duplicateAll", "dotProduct": "crossNorm",
}
L1B_PARAMS = {
    "nums": "labels", "start": "cutoff", "text": "buffer", "pairs": "matrix",
    "low": "ceiling", "high": "floorVal", "value": "namePart", "left": "rightSide",
    "right": "leftSide", "count": "colorId",
}


def _indent(lines, n):
    pad = " " * n
    return "\n".join(pad + ln if ln else "" for ln in lines)


def render_l0(p: Prog) -> str:
    params = ", ".join(p.params)
    if p.language == "python":
        return f"def {p.name}({params}):\n{_indent(p.body, 4)}"
    return f"function {p.name}({params}) {{\n{_indent(p.body, 4)}\n}}"


def render_s1(p: Prog) -> str:
    """Control-flow-flattening *shape*: dispatch loop, non-sequential state ids."""
    params = ", ".join(p.params)
    if p.language == "python":
        return (
            f"def {p.name}({params}):\n"
            f"    def _inner({params}):\n{_indent(p.body, 8)}\n"
            "    state = 5\n"
            "    result = None\n"
            "    while True:\n"
            "        if state == 5:\n"
            "            state = 2\n"
            "        elif state == 2:\n"
            f"            result = _inner({params})\n"
            "            state = 9\n"
            "        else:\n"
            "            return result"
        )
    return (
        f"function {p.name}({params}) {{\n"
        f"    function _inner({params}) {{\n{_indent(p.body, 8)}\n    }}\n"
        "    let state = 5;\n"
        "    let result = null;\n"
        "    while (true) {\n"
        "        if (state === 5) { state = 2; }\n"
        f"        else if (state === 2) {{ result = _inner({params}); state = 9; }}\n"
        "        else { return result; }\n"
        "    }\n"
        "}"
    )


def render_s2(p: Prog) -> str:
    """Opaque-predicate + dead-helper *shape*."""
    params = ", ".join(p.params)
    if p.language == "python":
        return (
            f"def _unused_{p.name}(seed):\n"
            "    return seed * 2 + 1\n\n"
            f"def {p.name}({params}):\n"
            "    if (3 * 3) < 0:\n"
            "        return None\n"
            f"{_indent(p.body, 4)}"
        )
    return (
        f"function _unused_{p.name}(seed) {{ return seed * 2 + 1; }}\n\n"
        f"function {p.name}({params}) {{\n"
        "    if ((3 * 3) < 0) { return null; }\n"
        f"{_indent(p.body, 4)}\n}}"
    )


def render_h1(p: Prog) -> str:
    """Held-out *shape*: a run-time string decoder. Carries H1 marker patterns on
    purpose (`b64decode` / `fromCharCode`) so the quarantine scanners have something
    real to detect. Written only under data/quarantine/."""
    params = ", ".join(p.params)
    if p.language == "python":
        return (
            "def _decode(blob):\n"
            "    import base64\n"
            "    return base64.b64decode(blob).decode()\n\n"
            '_MARKER = _decode("b2J0dW5l")\n\n'
            f"def {p.name}({params}):\n{_indent(p.body, 4)}"
        )
    return (
        "function _decode(codes) {\n"
        "    return codes.map(function (c) { return String.fromCharCode(c); }).join('');\n"
        "}\n"
        "const _MARKER = _decode([111, 98, 116, 117, 110, 101]);\n\n"
        f"function {p.name}({params}) {{\n{_indent(p.body, 4)}\n}}"
    )


def _rename(source: str, mapping: dict[str, str]) -> str:
    if not mapping:
        return source
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, sorted(mapping, key=len, reverse=True))) + r")\b")
    return pattern.sub(lambda m: mapping[m.group(0)], source)


def build_variant(p: Prog, condition: str) -> tuple[str, str, dict[str, str]]:
    """Return (code, entry_point, rename_map) for one condition."""
    if condition == "L0":
        return render_l0(p), p.name, {}
    if condition == "S1":
        return render_s1(p), p.name, {}
    if condition == "S2":
        return render_s2(p), p.name, {}
    if condition == "H1":
        return render_h1(p), p.name, {}
    base = render_l0(p)
    if condition == "L1b":
        mapping = {p.name: L1B_NAMES[p.name]}
        mapping.update({q: L1B_PARAMS[q] for q in p.params})
    elif condition == "L1r":
        # Deterministic pseudo-hex from the program id, so reruns are byte-identical.
        h = abs(hash(p.pid)) if False else int(p.pid[-4:])
        mapping = {p.name: f"f_{h:04x}"}
        mapping.update({q: f"v_{(h + i * 37) % 0x10000:04x}" for i, q in enumerate(p.params)})
    elif condition == "L2":
        mapping = {p.name: "aa"}
        mapping.update({q: chr(ord("q") + i) for i, q in enumerate(p.params)})
    else:
        raise ValueError(condition)
    return _rename(base, mapping), mapping[p.name], mapping


def execute(programs, condition):
    """Run every (program, condition) and return {pid: [output_canon, ...]}."""
    items, meta = [], []
    for p in programs:
        code, entry, _ = build_variant(p, condition)
        items.append(BatchItem(p.pid, p.language, code, entry, list(p.cases)))
        meta.append(p)
    results = run_batch(items, timeout_s=5.0, workers=8)
    out = {}
    for p, r in zip(meta, results):
        if not r.all_ok:
            raise RuntimeError(
                f"fixture {p.pid}/{condition} did not execute cleanly: "
                f"{[c.status for c in r.cases]} stderr={r.stderr[:400]}"
            )
        out[p.pid] = [c.output for c in r.cases]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "data"))
    args = ap.parse_args()
    out_root = Path(args.out)

    programs = list(PY_PROGRAMS) + list(JS_PROGRAMS)
    golds: dict[str, dict[str, list[str]]] = {}
    for cond in ALL_CONDITIONS:
        golds[cond] = execute(programs, cond)

    # Miniature semantic gate: every condition must reproduce its L0 parent's outputs.
    for cond in ALL_CONDITIONS:
        for p in programs:
            if golds[cond][p.pid] != golds["L0"][p.pid]:
                raise RuntimeError(
                    f"fixture transform {cond} is not semantics-preserving for {p.pid}: "
                    f"{golds[cond][p.pid]} != {golds['L0'][p.pid]}"
                )

    written: dict[str, int] = {}

    def dump(path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        written[str(path.relative_to(out_root))] = len(rows)

    for cond in TRAIN_CONDITIONS:
        for lang in ("python", "javascript"):
            rows = []
            for p in programs:
                if p.language != lang or p.role == "test":
                    continue
                code, entry, _ = build_variant(p, cond)
                for i, args_repr in enumerate(p.cases):
                    rows.append(
                        {
                            "item_id": f"{p.pid}::{cond}::{i}",
                            "program_id": p.pid,
                            "program_group_id": p.pid,
                            "condition": cond,
                            "language": lang,
                            "code": code,
                            "entry_point": entry,
                            "args_repr": args_repr,
                            "output_repr": golds[cond][p.pid][i],
                            "split": p.role,
                            "provenance": "synthetic",
                        }
                    )
            dump(out_root / "train" / "pairs" / cond / f"{lang}.jsonl", rows)

    for cond in ALL_CONDITIONS:
        for lang in ("python", "javascript"):
            rows = []
            for p in programs:
                if p.language != lang or p.role != "test":
                    continue
                code, entry, _ = build_variant(p, cond)
                for i, args_repr in enumerate(p.cases):
                    rows.append(
                        {
                            "item_id": f"{p.pid}::{cond}::{i}",
                            "program_id": p.pid,
                            "dataset": p.dataset,
                            "condition": cond,
                            "language": lang,
                            "code": code,
                            "entry_point": entry,
                            "args_repr": args_repr,
                            "output_repr": golds[cond][p.pid][i],
                            "case_role": "generated",
                            "meta": {"fixture": True},
                        }
                    )
            if cond == "H1":
                dump(out_root / "quarantine" / "h1" / f"{lang}.jsonl", rows)
            else:
                dump(out_root / "eval" / "testset" / "variants" / cond / f"{lang}.jsonl", rows)

    (out_root / "README.md").write_text(
        "# Synthetic fixture data tree\n\n"
        "Generated by `tests/fixtures/make_fixtures.py`. Gold labels are real "
        "(programs are executed through `obtune.exec.pool`); the transforms are "
        "shape-only stand-ins for the peer-owned `src/obtune/obf/` implementations and "
        "must never be used to support a claim about a condition.\n\n"
        f"Seed: {SEED}. Files:\n\n"
        + "\n".join(f"- `{k}` — {v} rows" for k, v in sorted(written.items()))
        + "\n"
    )
    print(json.dumps({"out": str(out_root), "files": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
