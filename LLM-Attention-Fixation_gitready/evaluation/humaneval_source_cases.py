from __future__ import annotations

import json
import re
from bisect import bisect_right
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import javalang  # type: ignore
except Exception:
    javalang = None


class SourceCaseBuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class HumanevalSourceCase:
    case_id: str
    expr: str
    origin: str
    expected_bool: bool
    trace_mode: str
    prelude: str
    raw_source_line_start: int
    raw_source_line_end: int
    raw_display_line_start: str
    raw_display_line_end: str
    source_line_start: int
    source_line_end: int
    display_line_start: str
    display_line_end: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class _CaseTextSpan:
    expr: str
    start: int
    end: int


def _extract_main_body_bounds(java_code: str) -> Optional[Tuple[int, int]]:
    sig = re.search(
        r"public\s+static\s+void\s+main\s*\(\s*String\s*\[\]\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\)\s*\{",
        java_code,
    )
    if not sig:
        return None
    body_start = sig.end()
    depth = 1
    idx = body_start
    while idx < len(java_code):
        ch = java_code[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return body_start, idx
        idx += 1
    return None


def _replace_main_body(java_code: str, new_body: str) -> str:
    bounds = _extract_main_body_bounds(java_code)
    if not bounds:
        raise SourceCaseBuildError("Could not locate main method body.")
    start, end = bounds
    return java_code[:start] + "\n" + new_body + "\n" + java_code[end:]


def _line_starts(source: str) -> List[int]:
    starts = [0]
    for idx, ch in enumerate(source):
        if ch == "\n":
            starts.append(idx + 1)
    return starts


def _line_number_for_index(starts: Sequence[int], index: int) -> int:
    return bisect_right(starts, index) - 1 + 1


def _display_line(line: int) -> str:
    return f"L{line:03d}"


def _scan_matching(source: str, open_idx: int, open_char: str, close_char: str) -> int:
    if open_idx < 0 or open_idx >= len(source) or source[open_idx] != open_char:
        raise SourceCaseBuildError(f"Expected '{open_char}' at index {open_idx}.")
    depth = 1
    i = open_idx + 1
    in_str = False
    in_char = False
    escape = False
    line_comment = False
    block_comment = False
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if in_char:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_char = False
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch == '"':
            in_str = True
            i += 1
            continue
        if ch == "'":
            in_char = True
            i += 1
            continue
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise SourceCaseBuildError(f"Unmatched '{open_char}' starting at index {open_idx}.")


def _split_top_level_csv_spans(exprs: str) -> List[_CaseTextSpan]:
    out: List[_CaseTextSpan] = []
    cur: List[str] = []
    cur_start: Optional[int] = None
    depth = 0
    in_str = False
    in_char = False
    escape = False
    line_comment = False
    block_comment = False

    def flush(_: int) -> None:
        nonlocal cur, cur_start
        token = "".join(cur)
        if cur_start is None:
            cur = []
            return
        stripped = token.strip()
        if stripped:
            lead = len(token) - len(token.lstrip())
            trail = len(token.rstrip())
            out.append(_CaseTextSpan(stripped, cur_start + lead, cur_start + trail))
        cur = []
        cur_start = None

    for i, ch in enumerate(exprs):
        nxt = exprs[i + 1] if i + 1 < len(exprs) else ""
        if cur_start is None and not ch.isspace() and not (ch == "," and depth == 0):
            cur_start = i
        if line_comment:
            cur.append(ch)
            if ch == "\n":
                line_comment = False
            continue
        if block_comment:
            cur.append(ch)
            if i > 0 and exprs[i - 1] == "*" and ch == "/":
                block_comment = False
            continue
        if in_str:
            cur.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if in_char:
            cur.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_char = False
            continue
        if ch == "/" and nxt == "/":
            if cur_start is None:
                cur_start = i
            cur.append(ch)
            line_comment = True
            continue
        if ch == "/" and nxt == "*":
            if cur_start is None:
                cur_start = i
            cur.append(ch)
            block_comment = True
            continue
        if ch == '"':
            cur.append(ch)
            in_str = True
            continue
        if ch == "'":
            cur.append(ch)
            in_char = True
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            flush(i)
            continue
        cur.append(ch)
    flush(len(exprs))
    return out


def render_numbered_source(java_code: str) -> str:
    lines = java_code.splitlines()
    rendered = "\n".join(f"{_display_line(i + 1)} {line}" for i, line in enumerate(lines))
    if java_code.endswith("\n"):
        rendered += "\n"
    return rendered


def strip_java_comments(java_code: str) -> str:
    out: List[str] = []
    i = 0
    in_str = False
    in_char = False
    escape = False
    line_comment = False
    block_comment = False
    while i < len(java_code):
        ch = java_code[i]
        nxt = java_code[i + 1] if i + 1 < len(java_code) else ""
        if line_comment:
            if ch == "\n":
                out.append("\n")
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            if ch == "\n":
                out.append("\n")
            i += 1
            continue
        if in_str:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if in_char:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_char = False
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        out.append(ch)
        if ch == '"':
            in_str = True
        elif ch == "'":
            in_char = True
        i += 1
    return "".join(out)


def build_prompt_source_view(java_code: str) -> Dict[str, object]:
    stripped = strip_java_comments(java_code)
    raw_lines = stripped.splitlines()
    prompt_lines: List[str] = []
    raw_to_prompt: Dict[int, int] = {}
    prompt_to_raw: Dict[int, int] = {}
    for raw_line_no, line in enumerate(raw_lines, start=1):
        cleaned = line.rstrip()
        if not cleaned.strip():
            continue
        prompt_line_no = len(prompt_lines) + 1
        raw_to_prompt[raw_line_no] = prompt_line_no
        prompt_to_raw[prompt_line_no] = raw_line_no
        prompt_lines.append(cleaned)
    prompt_source = "\n".join(prompt_lines)
    if prompt_lines:
        prompt_source += "\n"
    prompt_numbered = "\n".join(
        f"{_display_line(i + 1)} {line}" for i, line in enumerate(prompt_lines)
    )
    if prompt_lines:
        prompt_numbered += "\n"
    return {
        "source": prompt_source,
        "numbered_source": prompt_numbered,
        "raw_to_prompt": raw_to_prompt,
        "prompt_to_raw": prompt_to_raw,
    }


def _map_raw_span_to_prompt(raw_to_prompt: Dict[int, int], start_line: int, end_line: int) -> Tuple[int, int]:
    mapped = [raw_to_prompt[line] for line in range(start_line, end_line + 1) if line in raw_to_prompt]
    if not mapped:
        raise SourceCaseBuildError(
            f"Could not map raw source span {start_line}-{end_line} into prompt line space."
        )
    return mapped[0], mapped[-1]


def apply_prompt_line_mapping(
    cases: Sequence[HumanevalSourceCase],
    raw_to_prompt: Dict[int, int],
) -> List[HumanevalSourceCase]:
    out: List[HumanevalSourceCase] = []
    for case in cases:
        prompt_start, prompt_end = _map_raw_span_to_prompt(
            raw_to_prompt,
            case.raw_source_line_start,
            case.raw_source_line_end,
        )
        out.append(
            replace(
                case,
                source_line_start=prompt_start,
                source_line_end=prompt_end,
                display_line_start=_display_line(prompt_start),
                display_line_end=_display_line(prompt_end),
            )
        )
    return out


def extract_humaneval_source_cases(java_code: str) -> List[HumanevalSourceCase]:
    bounds = _extract_main_body_bounds(java_code)
    if not bounds:
        return []
    body_start, body_end = bounds
    body = java_code[body_start:body_end]
    starts = _line_starts(java_code)
    cases: List[HumanevalSourceCase] = []

    m = re.search(r"List<Boolean>\s+correct\s*=\s*Arrays\.asList\s*\(", body, re.DOTALL)
    if m:
        block_start = body_start + m.end()
        close_idx = _scan_matching(java_code, block_start - 1, "(", ")")
        expr_block = java_code[block_start:close_idx]
        prelude = body[:m.start()].strip()
        for idx, span in enumerate(_split_top_level_csv_spans(expr_block), start=1):
            line_start = _line_number_for_index(starts, block_start + span.start)
            line_end = _line_number_for_index(starts, max(block_start + span.end - 1, block_start + span.start))
            cases.append(
                HumanevalSourceCase(
                    case_id=f"s{idx:03d}",
                    expr=span.expr,
                    origin="correct_list",
                    expected_bool=True,
                    trace_mode="expression",
                    prelude=prelude,
                    raw_source_line_start=line_start,
                    raw_source_line_end=line_end,
                    raw_display_line_start=_display_line(line_start),
                    raw_display_line_end=_display_line(line_end),
                    source_line_start=line_start,
                    source_line_end=line_end,
                    display_line_start=_display_line(line_start),
                    display_line_end=_display_line(line_end),
                )
            )
        return cases

    if javalang is None:
        return cases

    tree = javalang.parse.parse(java_code)
    main_method = None
    for _, method in tree.filter(javalang.tree.MethodDeclaration):
        if getattr(method, "name", "") == "main":
            main_method = method
            break
    if main_method is None:
        return cases

    def _contains_assertion_throw(stmt: Any) -> bool:
        if stmt is None:
            return False
        if isinstance(stmt, javalang.tree.ThrowStatement):
            expr = getattr(stmt, "expression", None)
            if isinstance(expr, javalang.tree.ClassCreator):
                t = getattr(expr, "type", None)
                return getattr(t, "name", "") == "AssertionError"
            return False
        if isinstance(stmt, javalang.tree.BlockStatement):
            return any(_contains_assertion_throw(s) for s in getattr(stmt, "statements", []) or [])
        return False

    idx = 1
    for _, stmt in main_method.filter(javalang.tree.IfStatement):
        if not _contains_assertion_throw(getattr(stmt, "then_statement", None)):
            continue
        pos = getattr(stmt, "position", None)
        if pos is None:
            continue
        line = int(pos.line)
        line_start_idx = starts[line - 1]
        scan_idx = line_start_idx + max(int(pos.column) - 1, 0)
        if_idx = java_code.find("if", scan_idx)
        if if_idx < 0:
            continue
        open_idx = java_code.find("(", if_idx)
        if open_idx < 0:
            continue
        close_idx = _scan_matching(java_code, open_idx, "(", ")")
        cond = java_code[open_idx + 1:close_idx].strip()
        if not cond:
            continue
        abs_start = open_idx + 1
        abs_end = close_idx
        line_start = _line_number_for_index(starts, abs_start)
        line_end = _line_number_for_index(starts, max(abs_end - 1, abs_start))
        cases.append(
            HumanevalSourceCase(
                case_id=f"s{idx:03d}",
                expr=cond,
                origin="if_throw",
                expected_bool=True,
                trace_mode="program_success",
                prelude="",
                raw_source_line_start=line_start,
                raw_source_line_end=line_end,
                raw_display_line_start=_display_line(line_start),
                raw_display_line_end=_display_line(line_end),
                source_line_start=line_start,
                source_line_end=line_end,
                display_line_start=_display_line(line_start),
                display_line_end=_display_line(line_end),
            )
        )
        idx += 1
    return cases


def clone_humaneval_for_case(java_code: str, case: HumanevalSourceCase) -> str:
    if case.origin == "if_throw":
        return java_code
    lines: List[str] = []
    if case.prelude:
        lines.append(case.prelude)
    lines.append("List<Boolean> correct = Arrays.asList(")
    lines.append(f"    {case.expr}")
    lines.append(");")
    lines.append("if (correct.contains(false)) {")
    lines.append("    throw new AssertionError();")
    lines.append("}")
    return _replace_main_body(java_code, "\n".join(lines))


def summary_for_cases(cases: Sequence[HumanevalSourceCase]) -> Dict[str, int]:
    out: Dict[str, int] = {"total_cases": len(cases)}
    for case in cases:
        out[f"origin:{case.origin}"] = out.get(f"origin:{case.origin}", 0) + 1
        out[f"trace_mode:{case.trace_mode}"] = out.get(f"trace_mode:{case.trace_mode}", 0) + 1
    return out


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
