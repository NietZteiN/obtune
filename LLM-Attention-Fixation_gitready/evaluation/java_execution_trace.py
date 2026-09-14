from __future__ import annotations

import json
import re
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from counterfactual_eval import build_case_pack
from paths import resolve_artifact_path, resolve_dataset_source_root
from util import utity

_CF_MODULE_PATH = Path(__file__).resolve().parent / "java_counterfactual.py"
_CF_SPEC = importlib.util.spec_from_file_location("_java_counterfactual_impl_for_trace", _CF_MODULE_PATH)
if _CF_SPEC is None or _CF_SPEC.loader is None:
    raise ImportError(f"Failed to load counterfactual helpers from {_CF_MODULE_PATH}")
_CF_MOD = importlib.util.module_from_spec(_CF_SPEC)
sys.modules[_CF_SPEC.name] = _CF_MOD
_CF_SPEC.loader.exec_module(_CF_MOD)
_extract_seed_expressions = _CF_MOD._extract_seed_expressions
_mutate_expr_false = _CF_MOD._mutate_expr_false

try:
    import javalang  # type: ignore
except Exception as exc:  # pragma: no cover - data/environment dependent
    javalang = None
    _JAVALANG_IMPORT_ERROR = exc
else:  # pragma: no cover - branch chosen at runtime
    _JAVALANG_IMPORT_ERROR = None


TRACE_JSON_BEGIN = "TRACE_JSON_BEGIN"
TRACE_JSON_END = "TRACE_JSON_END"


class TraceBuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class TraceCase:
    case_id: str
    expr: str
    expected_bool: bool
    origin: str
    mutation_type: str
    prelude: str


@dataclass(frozen=True)
class _Edit:
    start: int
    end: int
    text: str


def _line_starts(source: str) -> List[int]:
    starts = [0]
    for idx, ch in enumerate(source):
        if ch == "\n":
            starts.append(idx + 1)
    return starts


def _index_from_position(source: str, starts: Sequence[int], line: int, column: int) -> int:
    if line < 1 or line > len(starts):
        raise TraceBuildError(f"Invalid source position line={line} column={column}.")
    base = starts[line - 1]
    idx = base + max(column - 1, 0)
    if idx < 0 or idx > len(source):
        raise TraceBuildError(f"Position out of range at line={line} column={column}.")
    return idx


def _is_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_" or ch == "$"


def _scan_matching(
    source: str,
    open_idx: int,
    open_char: str,
    close_char: str,
) -> int:
    if open_idx < 0 or open_idx >= len(source) or source[open_idx] != open_char:
        raise TraceBuildError(f"Expected '{open_char}' at index {open_idx}.")

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

    raise TraceBuildError(f"Unmatched '{open_char}' starting at index {open_idx}.")


def _find_keyword(source: str, start_idx: int, keyword: str) -> int:
    pat = re.compile(rf"\b{re.escape(keyword)}\b")
    m = pat.search(source, pos=start_idx)
    if not m:
        raise TraceBuildError(f"Could not find keyword '{keyword}' from index {start_idx}.")
    return m.start()


def _find_statement_semicolon(source: str, start_idx: int) -> int:
    depth_paren = 0
    depth_brace = 0
    depth_bracket = 0
    i = start_idx
    in_str = False
    in_char = False
    escape = False
    while i < len(source):
        ch = source[i]
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
        if ch == '"':
            in_str = True
        elif ch == "'":
            in_char = True
        elif ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren = max(0, depth_paren - 1)
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace = max(0, depth_brace - 1)
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket = max(0, depth_bracket - 1)
        elif ch == ";" and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
            return i
        i += 1
    raise TraceBuildError(f"Could not locate statement semicolon from index {start_idx}.")


def _top_level_indices(text: str, target: str) -> List[int]:
    out: List[int] = []
    depth_paren = 0
    depth_brace = 0
    depth_bracket = 0
    in_str = False
    in_char = False
    escape = False
    for i, ch in enumerate(text):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if in_char:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_char = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "'":
            in_char = True
            continue
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren = max(0, depth_paren - 1)
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace = max(0, depth_brace - 1)
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket = max(0, depth_bracket - 1)
        elif ch == target and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
            out.append(i)
    return out


def _sanitize_java_for_javalang(java_code: str) -> str:
    out: List[str] = []
    i = 0
    in_str = False
    in_char = False
    escape = False
    while i < len(java_code):
        ch = java_code[i]
        nxt = java_code[i + 1] if i + 1 < len(java_code) else ""
        if in_str:
            if escape:
                out.append(ch)
                escape = False
                i += 1
                continue
            if ch == "\\" and nxt == "s":
                out.append("\\")
                out.append("\\")
                i += 2
                continue
            if ch == "\\":
                out.append(ch)
                escape = True
                i += 1
                continue
            out.append(ch)
            if ch == '"':
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
        out.append(ch)
        if ch == '"':
            in_str = True
        elif ch == "'":
            in_char = True
        i += 1

    sanitized = "".join(out).replace("\\s", "\\\\")
    # javalang does not support pattern-matching instanceof bindings such as:
    #   x instanceof String s
    # For parser-only sanitization, blank the binding identifier while preserving
    # source length so positions from the original file remain aligned.
    sanitized = re.sub(
        r"(\binstanceof\b\s+[^)\]&|,:;]+?\b)(\s+)([A-Za-z_$][A-Za-z0-9_$]*)(?=\s*(?:&&|\|\||[)\],:;]))",
        lambda m: m.group(1) + m.group(2) + (" " * len(m.group(3))),
        sanitized,
    )
    out_lines: List[str] = []
    for line in sanitized.splitlines(True):
        line = re.sub(r"(\bcase\b[\s\S]*?)\-\>", r"\1: ", line)
        line = re.sub(r"(\bdefault\b[\s\S]*?)\-\>", r"\1: ", line)
        out_lines.append(line)
    return "".join(out_lines)


def _method_local_nodes(method: Any, node_type: Any) -> Iterable[Tuple[Any, Any]]:
    for path, node in method.filter(node_type):
        nested_method = False
        for ancestor in path:
            if isinstance(ancestor, javalang.tree.MethodDeclaration) and ancestor is not method:
                nested_method = True
                break
        if nested_method:
            continue
        yield path, node


def _method_body_bounds(source: str, starts: Sequence[int], method: Any) -> Tuple[int, int]:
    if method.position is None:
        raise TraceBuildError(f"Method '{getattr(method, 'name', '<unknown>')}' has no source position.")
    start_idx = _index_from_position(source, starts, method.position.line, method.position.column)
    brace_idx = source.find("{", start_idx)
    if brace_idx == -1:
        raise TraceBuildError(f"Could not find body for method '{method.name}'.")
    end_idx = _scan_matching(source, brace_idx, "{", "}")
    return brace_idx, end_idx


def _requires_raw_condition(cond: str) -> bool:
    return re.search(
        r"\binstanceof\b\s+[^)\]&|,:;]+?\b\s+[A-Za-z_$][A-Za-z0-9_$]*(?=\s*(?:&&|\|\||[)\],:;]))",
        cond,
    ) is not None


def _constant_boolean_value(cond: str) -> Optional[bool]:
    text = cond.strip()
    if text == "true":
        return True
    if text == "false":
        return False
    if not text or '"' in text or "'" in text:
        return None

    identifiers = re.findall(r"[A-Za-z_$][A-Za-z0-9_$]*", text)
    if any(token not in {"true", "false"} for token in identifiers):
        return None

    python_expr = re.sub(r"\btrue\b", "True", text)
    python_expr = re.sub(r"\bfalse\b", "False", python_expr)
    python_expr = python_expr.replace("&&", " and ")
    python_expr = python_expr.replace("||", " or ")
    python_expr = re.sub(r"!(?!=)", " not ", python_expr)
    try:
        value = eval(python_expr, {"__builtins__": {}}, {})
    except Exception:
        return None
    if isinstance(value, bool):
        return value
    return None


def _branch_wrapper(method_name: str, branch_kind: str, branch_id: str, line: int, cond: str) -> str:
    return (
        f'TraceRuntime.branchEval("{method_name}", "{branch_kind}", "{branch_id}", {line}, ({cond}))'
    )


def _enhanced_for_wrapper(method_name: str, branch_id: str, line: int, iterable_expr: str) -> str:
    return (
        f'TraceRuntime.iterate("{method_name}", "{branch_id}", {line}, {iterable_expr})'
    )


def _next_non_whitespace_index(source: str, start_idx: int) -> int:
    idx = start_idx
    while idx < len(source) and source[idx].isspace():
        idx += 1
    return idx


def _inject_block_probe(
    source: str,
    edits: List[_Edit],
    *,
    body_search_start: int,
    method_name: str,
    branch_kind: str,
    branch_id: str,
    line: int,
) -> None:
    cursor = _next_non_whitespace_index(source, body_search_start)
    if cursor >= len(source) or source[cursor] != "{":
        raise TraceBuildError(
            f"Literal-true {branch_kind} at line {line} requires a braced body for tracing."
        )
    edits.append(
        _Edit(
            cursor + 1,
            cursor + 1,
            f'\nTraceRuntime.branchEval("{method_name}", "{branch_kind}", "{branch_id}", {line}, true);\n',
        )
    )


def _line_probe(method_name: str, line: int) -> str:
    return f'TraceRuntime.lineExec("{method_name}", {line});'


def _is_simple_probe_statement(node: Any) -> bool:
    simple_types = (
        javalang.tree.StatementExpression,
        javalang.tree.LocalVariableDeclaration,
        javalang.tree.ThrowStatement,
        javalang.tree.BreakStatement,
        javalang.tree.ContinueStatement,
        javalang.tree.AssertStatement,
    )
    return isinstance(node, simple_types)


def _simple_statement_end(source: str, start_idx: int) -> int:
    return _find_statement_semicolon(source, start_idx) + 1


def _wrap_statement_with_probe(
    source: str,
    edits: List[_Edit],
    *,
    stmt_start: int,
    stmt_end: int,
    method_name: str,
    line: int,
) -> None:
    stmt_text = source[stmt_start:stmt_end]
    replacement = "{\n" + _line_probe(method_name, line) + "\n" + stmt_text + "\n}"
    edits.append(_Edit(stmt_start, stmt_end, replacement))


def _build_trace_runtime_class() -> str:
    return f"""
class TraceRuntime {{
    private static final java.util.List<String> EVENTS = new java.util.ArrayList<>();
    private static int EVENT_IDX = 0;

    private static String esc(String s) {{
        if (s == null) {{
            return "null";
        }}
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {{
            char ch = s.charAt(i);
            if (ch == '\\\\' || ch == '"') {{
                sb.append('\\\\');
            }}
            if (ch == '\\n') {{
                sb.append("\\\\n");
            }} else if (ch == '\\r') {{
                sb.append("\\\\r");
            }} else if (ch == '\\t') {{
                sb.append("\\\\t");
            }} else {{
                sb.append(ch);
            }}
        }}
        return sb.toString();
    }}

    private static String base(String eventType, String methodName, int line) {{
        String safeMethod = methodName == null ? "" : methodName;
        return "{{\\"event_idx\\":" + (EVENT_IDX++) +
            ",\\"event_type\\":\\"" + esc(eventType) +
            "\\",\\"method_name\\":\\"" + esc(safeMethod) +
            "\\",\\"line\\":" + line;
    }}

    public static void methodEnter(String methodName, int line) {{
        EVENTS.add(base("method_enter", methodName, line) + "}}");
    }}

    public static void methodExit(String methodName, int line) {{
        EVENTS.add(base("method_exit", methodName, line) + "}}");
    }}

    public static void lineExec(String methodName, int line) {{
        EVENTS.add(base("line_exec", methodName, line) + "}}");
    }}

    public static boolean branchEval(String methodName, String branchKind, String branchId, int line, boolean outcome) {{
        EVENTS.add(base("branch_eval", methodName, line) +
            ",\\"branch_kind\\":\\"" + esc(branchKind) +
            "\\",\\"branch_id\\":\\"" + esc(branchId) +
            "\\",\\"outcome\\":" + (outcome ? "true" : "false") + "}}");
        return outcome;
    }}

    public static <T> Iterable<T> iterate(String methodName, String branchId, int line, Iterable<T> iterable) {{
        return new Iterable<T>() {{
            @Override
            public java.util.Iterator<T> iterator() {{
                final java.util.Iterator<T> base = iterable.iterator();
                return new java.util.Iterator<T>() {{
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = base.hasNext();
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public T next() {{
                        return base.next();
                    }}
                    @Override
                    public void remove() {{
                        base.remove();
                    }}
                }};
            }}
        }};
    }}

    public static <T> Iterable<T> iterate(String methodName, String branchId, int line, T[] array) {{
        return new Iterable<T>() {{
            @Override
            public java.util.Iterator<T> iterator() {{
                return new java.util.Iterator<T>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public T next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Character> iterate(String methodName, String branchId, int line, char[] array) {{
        return new Iterable<Character>() {{
            @Override
            public java.util.Iterator<Character> iterator() {{
                return new java.util.Iterator<Character>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Character next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Integer> iterate(String methodName, String branchId, int line, int[] array) {{
        return new Iterable<Integer>() {{
            @Override
            public java.util.Iterator<Integer> iterator() {{
                return new java.util.Iterator<Integer>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Integer next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Long> iterate(String methodName, String branchId, int line, long[] array) {{
        return new Iterable<Long>() {{
            @Override
            public java.util.Iterator<Long> iterator() {{
                return new java.util.Iterator<Long>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Long next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Double> iterate(String methodName, String branchId, int line, double[] array) {{
        return new Iterable<Double>() {{
            @Override
            public java.util.Iterator<Double> iterator() {{
                return new java.util.Iterator<Double>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Double next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Float> iterate(String methodName, String branchId, int line, float[] array) {{
        return new Iterable<Float>() {{
            @Override
            public java.util.Iterator<Float> iterator() {{
                return new java.util.Iterator<Float>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Float next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Boolean> iterate(String methodName, String branchId, int line, boolean[] array) {{
        return new Iterable<Boolean>() {{
            @Override
            public java.util.Iterator<Boolean> iterator() {{
                return new java.util.Iterator<Boolean>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Boolean next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Byte> iterate(String methodName, String branchId, int line, byte[] array) {{
        return new Iterable<Byte>() {{
            @Override
            public java.util.Iterator<Byte> iterator() {{
                return new java.util.Iterator<Byte>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Byte next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static Iterable<Short> iterate(String methodName, String branchId, int line, short[] array) {{
        return new Iterable<Short>() {{
            @Override
            public java.util.Iterator<Short> iterator() {{
                return new java.util.Iterator<Short>() {{
                    int idx = 0;
                    @Override
                    public boolean hasNext() {{
                        boolean outcome = idx < array.length;
                        TraceRuntime.branchEval(methodName, "for", branchId, line, outcome);
                        return outcome;
                    }}
                    @Override
                    public Short next() {{
                        return array[idx++];
                    }}
                }};
            }}
        }};
    }}

    public static <T> T methodReturning(String methodName, int line, T value) {{
        String valueRepr = String.valueOf(value);
        EVENTS.add(base("return", methodName, line) +
            ",\\"value_repr\\":\\"" + esc(valueRepr) + "\\"}}");
        methodExit(methodName, line);
        return value;
    }}

    public static void methodReturnVoid(String methodName, int line) {{
        EVENTS.add(base("return", methodName, line) +
            ",\\"value_repr\\":\\"void\\"}}");
        methodExit(methodName, line);
    }}

    public static void caseResult(String caseId, boolean value) {{
        EVENTS.add(base("case_result", "main", -1) +
            ",\\"case_id\\":\\"" + esc(caseId) +
            "\\",\\"outcome\\":" + (value ? "true" : "false") + "}}");
    }}

    public static void printTrace() {{
        StringBuilder sb = new StringBuilder();
        sb.append("{{\\"events\\":[");
        for (int i = 0; i < EVENTS.size(); i++) {{
            if (i > 0) {{
                sb.append(',');
            }}
            sb.append(EVENTS.get(i));
        }}
        sb.append("]}}");
        System.out.println("{TRACE_JSON_BEGIN}");
        System.out.println(sb.toString());
        System.out.println("{TRACE_JSON_END}");
    }}
}}
"""


def _build_case_prelude_map(java_code: str, dataset: str) -> Dict[Tuple[str, str], str]:
    mapping: Dict[Tuple[str, str], str] = {}
    for seed in _extract_seed_expressions(java_code, dataset.strip().lower()):
        mapping.setdefault((seed.expr.strip(), seed.origin), seed.prelude)
        for cand_expr, _ in _mutate_expr_false(seed.expr):
            mapping.setdefault((cand_expr.strip(), seed.origin), seed.prelude)
    return mapping


def _resolve_trace_case(java_code: str, dataset: str, case_pack: Dict[str, object], case_id: str) -> TraceCase:
    target = None
    for case in case_pack.get("cases", []):
        if str(case.get("case_id")) == case_id:
            target = case
            break
    if target is None:
        raise TraceBuildError(f"Case id '{case_id}' not found in case pack.")

    expr = str(target.get("expr", "")).strip()
    origin = str(target.get("origin", "")).strip()
    prelude = str(target.get("prelude", "")).strip()
    if not prelude:
        prelude = _build_case_prelude_map(java_code, dataset).get((expr, origin), "").strip()
    literal_expr = expr.strip().lower()
    if (
        not prelude
        and dataset.strip().lower() == "humaneval"
        and literal_expr not in {"true", "false"}
    ):
        raise TraceBuildError(
            f"Could not recover prelude for case '{case_id}' ({origin})."
        )

    return TraceCase(
        case_id=str(target.get("case_id")),
        expr=expr,
        expected_bool=bool(target.get("expected_bool")),
        origin=origin,
        mutation_type=str(target.get("mutation_type", "")),
        prelude=prelude,
    )


def _extract_main_body(java_code: str) -> Optional[Tuple[int, int]]:
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
    bounds = _extract_main_body(java_code)
    if not bounds:
        raise TraceBuildError("Could not locate main method body for trace harness.")
    start, end = bounds
    return java_code[:start] + "\n" + new_body + "\n" + java_code[end:]


def _build_trace_main_body(case: TraceCase) -> str:
    lines: List[str] = ["try {"]
    if case.prelude:
        lines.append(case.prelude)
    lines.append(f"boolean __trace_case_result = ({case.expr});")
    lines.append(f'TraceRuntime.caseResult("{case.case_id}", __trace_case_result);')
    lines.append("} finally {")
    lines.append('TraceRuntime.methodExit("main", -1);')
    lines.append("TraceRuntime.printTrace();")
    lines.append("}")
    return "\n".join(lines)


def _build_program_success_trace_main_body(case_id: str, original_body: str) -> str:
    lines: List[str] = ["try {"]
    if original_body.strip():
        lines.append(original_body.strip())
    lines.append(f'TraceRuntime.caseResult("{case_id}", true);')
    lines.append("} catch (Throwable __trace_case_exc) {")
    lines.append(f'TraceRuntime.caseResult("{case_id}", false);')
    lines.append("} finally {")
    lines.append('TraceRuntime.methodExit("main", -1);')
    lines.append("TraceRuntime.printTrace();")
    lines.append("}")
    return "\n".join(lines)


def _instrument_java_source(java_code: str) -> str:
    if javalang is None:
        raise TraceBuildError(f"javalang is unavailable: {_JAVALANG_IMPORT_ERROR}")

    try:
        tree = javalang.parse.parse(_sanitize_java_for_javalang(java_code))
    except Exception as exc:  # pragma: no cover - data dependent
        raise TraceBuildError(f"javalang parse failed: {exc}") from exc

    if not getattr(tree, "types", None):
        raise TraceBuildError("No Java type declarations found for tracing.")

    starts = _line_starts(java_code)
    edits: List[_Edit] = []

    first_type = tree.types[0]
    if getattr(first_type, "position", None) is None:
        raise TraceBuildError("First type declaration has no source position.")
    first_type_idx = _index_from_position(
        java_code,
        starts,
        first_type.position.line,
        first_type.position.column,
    )
    edits.append(_Edit(first_type_idx, first_type_idx, _build_trace_runtime_class()))

    branch_sites: List[Tuple[int, Any, Any, str]] = []
    for _, method in tree.filter(javalang.tree.MethodDeclaration):
        brace_idx, end_idx = _method_body_bounds(java_code, starts, method)
        method_line = int(method.position.line if method.position else -1)
        edits.append(
            _Edit(
                brace_idx + 1,
                brace_idx + 1,
                f'\nTraceRuntime.methodEnter("{method.name}", {method_line});\n',
            )
        )
        if method.return_type is None and method.name != "main":
            edits.append(
                _Edit(
                    end_idx,
                    end_idx,
                    f'\nTraceRuntime.methodExit("{method.name}", {method_line});\n',
                )
            )

        for _, stmt in _method_local_nodes(method, javalang.tree.ReturnStatement):
            if stmt.position is None:
                raise TraceBuildError(f"Return statement in method '{method.name}' has no source position.")
            ret_start = _index_from_position(java_code, starts, stmt.position.line, stmt.position.column)
            keyword_idx = _find_keyword(java_code, ret_start, "return")
            semi_idx = _find_statement_semicolon(java_code, keyword_idx)
            expr_text = java_code[keyword_idx + len("return"):semi_idx].strip()
            line = int(stmt.position.line)
            if expr_text:
                replacement = f'return TraceRuntime.methodReturning("{method.name}", {line}, {expr_text});'
            else:
                replacement = f'TraceRuntime.methodReturnVoid("{method.name}", {line}); return;'
            edits.append(_Edit(keyword_idx, semi_idx + 1, replacement))

        for path, stmt in _method_local_nodes(method, javalang.tree.Statement):
            if stmt.position is None or not _is_simple_probe_statement(stmt):
                continue
            stmt_start = _index_from_position(java_code, starts, stmt.position.line, stmt.position.column)
            stmt_end = _simple_statement_end(java_code, stmt_start)
            line = int(stmt.position.line)
            parent = path[-1] if path else None
            if isinstance(parent, list):
                if any(isinstance(ancestor, javalang.tree.SwitchStatementCase) for ancestor in path):
                    _wrap_statement_with_probe(
                        java_code,
                        edits,
                        stmt_start=stmt_start,
                        stmt_end=stmt_end,
                        method_name=method.name,
                        line=line,
                    )
                    continue
                edits.append(_Edit(stmt_start, stmt_start, _line_probe(method.name, line) + "\n"))
                continue
            if isinstance(
                parent,
                (
                    javalang.tree.IfStatement,
                    javalang.tree.ForStatement,
                    javalang.tree.WhileStatement,
                    javalang.tree.DoStatement,
                ),
            ):
                _wrap_statement_with_probe(
                    java_code,
                    edits,
                    stmt_start=stmt_start,
                    stmt_end=stmt_end,
                    method_name=method.name,
                    line=line,
                )
                continue

        for _, stmt in _method_local_nodes(method, javalang.tree.IfStatement):
            if stmt.position is not None:
                branch_sites.append(
                    (_index_from_position(java_code, starts, stmt.position.line, stmt.position.column), method, stmt, "if")
                )
        for _, stmt in _method_local_nodes(method, javalang.tree.WhileStatement):
            if stmt.position is not None:
                branch_sites.append(
                    (_index_from_position(java_code, starts, stmt.position.line, stmt.position.column), method, stmt, "while")
                )
        for _, stmt in _method_local_nodes(method, javalang.tree.ForStatement):
            if stmt.position is not None:
                branch_sites.append(
                    (_index_from_position(java_code, starts, stmt.position.line, stmt.position.column), method, stmt, "for")
                )
        for _, stmt in _method_local_nodes(method, javalang.tree.DoStatement):
            if stmt.position is not None:
                branch_sites.append(
                    (_index_from_position(java_code, starts, stmt.position.line, stmt.position.column), method, stmt, "do")
                )

    branch_sites.sort(key=lambda item: item[0])
    for idx, (start_idx, method, stmt, kind) in enumerate(branch_sites, start=1):
        branch_id = f"b{idx:03d}"
        line = int(stmt.position.line) if stmt.position is not None else -1

        if kind in {"if", "while"}:
            keyword_idx = _find_keyword(java_code, start_idx, kind)
            open_idx = java_code.find("(", keyword_idx)
            if open_idx == -1:
                raise TraceBuildError(f"Could not find condition start for {kind} at line {line}.")
            close_idx = _scan_matching(java_code, open_idx, "(", ")")
            cond = java_code[open_idx + 1:close_idx].strip()
            if not cond:
                raise TraceBuildError(f"Empty {kind} condition at line {line}.")
            if _requires_raw_condition(cond):
                continue
            const_bool = _constant_boolean_value(cond)
            if kind == "while" and const_bool is True:
                _inject_block_probe(
                    java_code,
                    edits,
                    body_search_start=close_idx + 1,
                    method_name=method.name,
                    branch_kind=kind,
                    branch_id=branch_id,
                    line=line,
                )
                continue
            edits.append(
                _Edit(
                    open_idx + 1,
                    close_idx,
                    _branch_wrapper(method.name, kind, branch_id, line, cond),
                )
            )
            continue

        if kind == "for":
            keyword_idx = _find_keyword(java_code, start_idx, "for")
            open_idx = java_code.find("(", keyword_idx)
            if open_idx == -1:
                raise TraceBuildError(f"Could not find for-header start at line {line}.")
            close_idx = _scan_matching(java_code, open_idx, "(", ")")
            header = java_code[open_idx + 1:close_idx]
            semis = _top_level_indices(header, ";")
            if len(semis) == 2:
                cond_start = open_idx + 1 + semis[0] + 1
                cond_end = open_idx + 1 + semis[1]
                cond_raw = java_code[cond_start:cond_end]
                cond = cond_raw.strip()
                const_bool = _constant_boolean_value(cond) if cond else None
                if cond == "" or const_bool is True:
                    _inject_block_probe(
                        java_code,
                        edits,
                        body_search_start=close_idx + 1,
                        method_name=method.name,
                        branch_kind="for",
                        branch_id=branch_id,
                        line=line,
                    )
                    if cond == "":
                        continue
                    continue
                if _requires_raw_condition(cond):
                    continue
                edits.append(
                    _Edit(
                        cond_start,
                        cond_end,
                        _branch_wrapper(method.name, "for", branch_id, line, cond),
                    )
                )
                continue
            if isinstance(getattr(stmt, "control", None), javalang.tree.EnhancedForControl):
                colon_indices = _top_level_indices(header, ":")
                if len(colon_indices) != 1:
                    raise TraceBuildError(f"Unsupported enhanced-for header at line {line}.")
                iterable_start = open_idx + 1 + colon_indices[0] + 1
                iterable_end = close_idx
                iterable_expr = java_code[iterable_start:iterable_end].strip()
                if not iterable_expr:
                    raise TraceBuildError(f"Empty enhanced-for iterable at line {line}.")
                edits.append(
                    _Edit(
                        iterable_start,
                        iterable_end,
                        _enhanced_for_wrapper(method.name, branch_id, line, iterable_expr),
                    )
                )
                continue
            raise TraceBuildError(f"Unsupported for-header at line {line}.")

        if kind == "do":
            keyword_idx = _find_keyword(java_code, start_idx, "do")
            cursor = keyword_idx + len("do")
            while cursor < len(java_code) and java_code[cursor].isspace():
                cursor += 1
            if cursor >= len(java_code):
                raise TraceBuildError(f"Malformed do-while at line {line}.")
            if java_code[cursor] == "{":
                body_end = _scan_matching(java_code, cursor, "{", "}") + 1
            else:
                body_end = _find_statement_semicolon(java_code, cursor) + 1
            while_idx = _find_keyword(java_code, body_end, "while")
            open_idx = java_code.find("(", while_idx)
            if open_idx == -1:
                raise TraceBuildError(f"Could not find do-while condition at line {line}.")
            close_idx = _scan_matching(java_code, open_idx, "(", ")")
            cond = java_code[open_idx + 1:close_idx].strip()
            if not cond:
                raise TraceBuildError(f"Empty do-while condition at line {line}.")
            if _requires_raw_condition(cond):
                continue
            if _constant_boolean_value(cond) is True:
                _inject_block_probe(
                    java_code,
                    edits,
                    body_search_start=keyword_idx + len("do"),
                    method_name=method.name,
                    branch_kind="do",
                    branch_id=branch_id,
                    line=line,
                )
                continue
            edits.append(
                _Edit(
                    open_idx + 1,
                    close_idx,
                    _branch_wrapper(method.name, "do", branch_id, line, cond),
                )
            )
            continue

        raise TraceBuildError(f"Unsupported branch kind '{kind}'.")

    edits.sort(key=lambda edit: (edit.start, edit.end))
    prev_end = -1
    for edit in edits:
        if edit.start < prev_end:
            raise TraceBuildError("Overlapping instrumentation edits detected.")
        prev_end = max(prev_end, edit.end)

    out = java_code
    for edit in sorted(edits, key=lambda item: (item.start, item.end), reverse=True):
        out = out[: edit.start] + edit.text + out[edit.end :]
    return out


def _extract_trace_json(text: str) -> Optional[Dict[str, object]]:
    if not text:
        return None
    pattern = re.compile(
        rf"{TRACE_JSON_BEGIN}\s*(\{{[\s\S]*?\}})\s*{TRACE_JSON_END}",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _summarize_events(events: Sequence[Dict[str, object]]) -> Tuple[List[str], List[Dict[str, object]]]:
    called_methods: List[str] = []
    method_seen = set()
    branches_seen: List[Dict[str, object]] = []
    branch_seen = set()

    for event in events:
        if event.get("event_type") == "method_enter":
            method_name = str(event.get("method_name", "")).strip()
            if method_name and method_name not in method_seen:
                method_seen.add(method_name)
                called_methods.append(method_name)
        if event.get("event_type") == "branch_eval":
            key = (
                str(event.get("branch_id", "")),
                str(event.get("branch_kind", "")),
                int(event.get("line", -1)),
            )
            if key in branch_seen:
                continue
            branch_seen.add(key)
            branches_seen.append(
                {
                    "branch_id": key[0],
                    "branch_kind": key[1],
                    "line": key[2],
                }
            )
    return called_methods, branches_seen


def _full_line_sequence(events: Sequence[Dict[str, object]]) -> List[int]:
    out: List[int] = []
    for event in events:
        if str(event.get("method_name", "")) == "main":
            continue
        if event.get("event_type") not in {"line_exec", "branch_eval", "return"}:
            continue
        out.append(int(event.get("line", -1)))
    return out


def _build_trace_result(
    *,
    exec_result: Dict[str, object],
    dataset: str,
    snippet: str,
    variant: str,
    variant_path: Optional[Path],
    class_name: str,
    case_id: str,
    case_expression: str,
    case_origin: str,
    mutation_type: str,
    expected_bool: bool,
    case_pack_source_hash: str = "",
) -> Dict[str, object]:
    parsed_trace = _extract_trace_json(str(exec_result.get("stdout", "")) + "\n" + str(exec_result.get("stderr", "")))
    events = list(parsed_trace.get("events", [])) if isinstance(parsed_trace, dict) else []
    called_methods, branches_seen = _summarize_events(events)
    case_events = [e for e in events if e.get("event_type") == "case_result"]
    case_outcome = None
    if case_events:
        case_outcome = bool(case_events[-1].get("outcome"))

    if not exec_result.get("compiled", False):
        status = "compile_error"
    elif not exec_result.get("success", False) and case_outcome is None:
        status = "runtime_error"
    elif case_outcome is None:
        status = "trace_missing"
    elif bool(case_outcome) != expected_bool:
        status = "mismatch"
    else:
        status = "ok"

    return {
        "dataset": dataset,
        "snippet": snippet,
        "variant": variant,
        "variant_path": str(variant_path) if variant_path else "",
        "class_name": class_name,
        "case_id": case_id,
        "case_expression": case_expression,
        "case_origin": case_origin,
        "mutation_type": mutation_type,
        "expected_bool": expected_bool,
        "trace_status": status,
        "unsupported_reason": "",
        "event_count": len(events),
        "called_methods": called_methods,
        "branches_seen": branches_seen,
        "case_result_matches_expected": (case_outcome == expected_bool) if case_outcome is not None else False,
        "case_result_observed": case_outcome,
        "executed_line_sequence": _full_line_sequence(events),
        "events": events,
        "exec_result": exec_result,
        "case_pack_source_hash": case_pack_source_hash,
    }


def _execute_trace_source(
    *,
    dataset: str,
    snippet: str,
    variant: str,
    variant_path: Optional[Path],
    class_name: str,
    case_id: str,
    case_expression: str,
    case_origin: str,
    mutation_type: str,
    expected_bool: bool,
    trace_source: str,
    case_pack_source_hash: str = "",
) -> Dict[str, object]:
    try:
        instrumented_source = _instrument_java_source(trace_source)
    except TraceBuildError as exc:
        return {
            "dataset": dataset,
            "snippet": snippet,
            "variant": variant,
            "variant_path": str(variant_path) if variant_path else "",
            "class_name": class_name,
            "case_id": case_id,
            "case_expression": case_expression,
            "case_origin": case_origin,
            "mutation_type": mutation_type,
            "expected_bool": expected_bool,
            "trace_status": "unsupported",
            "unsupported_reason": str(exc),
            "event_count": 0,
            "called_methods": [],
            "branches_seen": [],
            "events": [],
        }

    exec_result = utity.run_java_program_with_result(instrumented_source, class_name, enable_assertions=True)
    return _build_trace_result(
        exec_result=exec_result,
        dataset=dataset,
        snippet=snippet,
        variant=variant,
        variant_path=variant_path,
        class_name=class_name,
        case_id=case_id,
        case_expression=case_expression,
        case_origin=case_origin,
        mutation_type=mutation_type,
        expected_bool=expected_bool,
        case_pack_source_hash=case_pack_source_hash,
    )


def trace_java_case(
    *,
    project_root: Path,
    dataset: str,
    snippet: str,
    java_code: str,
    class_name: str,
    case_id: Optional[str] = None,
    pick_first: bool = False,
    cache_dir: Optional[Path | str] = None,
    rebuild_case_pack: bool = False,
    min_cases: int = 8,
    target_cases: int = 16,
    variant: str = "original",
    variant_path: Optional[Path] = None,
) -> Dict[str, object]:
    case_pack = build_case_pack(
        java_code=java_code,
        class_name=class_name,
        dataset=dataset,
        snippet=snippet,
        min_cases=min_cases,
        target_cases=target_cases,
        cache_dir=cache_dir,
        rebuild=rebuild_case_pack,
    )
    cases = case_pack.get("cases", [])
    if not cases:
        raise TraceBuildError("Case pack is empty; cannot build execution trace.")

    selected_case_id = case_id or (str(cases[0].get("case_id")) if pick_first or not case_id else "")
    if not selected_case_id:
        raise TraceBuildError("Specify --case-id or use --pick-first.")

    selected = _resolve_trace_case(java_code, dataset, case_pack, selected_case_id)
    trace_source = _replace_main_body(java_code, _build_trace_main_body(selected))
    return _execute_trace_source(
        dataset=dataset,
        snippet=snippet,
        variant=variant,
        variant_path=variant_path,
        class_name=class_name,
        case_id=selected.case_id,
        case_expression=selected.expr,
        case_origin=selected.origin,
        mutation_type=selected.mutation_type,
        expected_bool=selected.expected_bool,
        trace_source=trace_source,
        case_pack_source_hash=str(case_pack.get("source_hash", "")),
    )


def trace_java_source_case(
    *,
    project_root: Path,
    dataset: str,
    snippet: str,
    java_code: str,
    class_name: str,
    case_id: str,
    case_expression: str,
    case_origin: str,
    expected_bool: bool,
    trace_mode: str = "expression",
    prelude: str = "",
    variant: str = "original",
    variant_path: Optional[Path] = None,
) -> Dict[str, object]:
    if trace_mode == "expression":
        selected = TraceCase(
            case_id=case_id,
            expr=case_expression.strip(),
            expected_bool=expected_bool,
            origin=case_origin,
            mutation_type="source_case",
            prelude=prelude.strip(),
        )
        trace_source = _replace_main_body(java_code, _build_trace_main_body(selected))
    elif trace_mode == "program_success":
        bounds = _extract_main_body(java_code)
        if not bounds:
            raise TraceBuildError("Could not locate main method body for program-success trace.")
        start, end = bounds
        original_body = java_code[start:end]
        trace_source = _replace_main_body(java_code, _build_program_success_trace_main_body(case_id, original_body))
    else:
        raise TraceBuildError(f"Unsupported trace mode '{trace_mode}'.")

    return _execute_trace_source(
        dataset=dataset,
        snippet=snippet,
        variant=variant,
        variant_path=variant_path,
        class_name=class_name,
        case_id=case_id,
        case_expression=case_expression.strip(),
        case_origin=case_origin,
        mutation_type="source_case",
        expected_bool=expected_bool,
        trace_source=trace_source,
        case_pack_source_hash="",
    )


def resolve_original_java_path(project_root: Path, dataset: str, snippet: str) -> Path:
    root = resolve_dataset_source_root(project_root, dataset)
    candidates = [
        root / "java" / f"{snippet}.java",
        root / f"{snippet}.java",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"Could not find source snippet {snippet}.java for dataset '{dataset}'.")


def default_trace_output_path(
    *,
    project_root: Path,
    dataset: str,
    snippet: str,
    case_id: str,
    variant: str,
    variant_path: Optional[Path] = None,
    output_dir: Optional[Path | str] = None,
) -> Path:
    base = resolve_artifact_path(project_root, output_dir or "logs/execution_traces")
    if variant == "original":
        return base / dataset / snippet / "original" / f"{case_id}.json"

    label_parts = ["obf"]
    if variant_path is not None:
        parts = list(variant_path.parts)
        if snippet in parts:
            idx = parts.index(snippet)
            tail = parts[idx + 1 :]
            if len(tail) >= 3:
                label_parts.extend(tail[:2])
    return base / dataset / snippet / Path(*label_parts) / f"{case_id}.json"


def load_trace_target(
    *,
    project_root: Path,
    dataset: str,
    snippet: str,
    variant: str,
    variant_path: Optional[Path] = None,
) -> Tuple[Path, str, str]:
    if variant == "original":
        source_path = resolve_original_java_path(project_root, dataset, snippet)
    else:
        if variant_path is None:
            raise FileNotFoundError("Obfuscated trace runs require --variant-path.")
        source_path = variant_path
        if not source_path.is_file():
            raise FileNotFoundError(f"Variant path not found: {source_path}")
    java_code = source_path.read_text(encoding="utf-8")
    return source_path, java_code, source_path.stem
