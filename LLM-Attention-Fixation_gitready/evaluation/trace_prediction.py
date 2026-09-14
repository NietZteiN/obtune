from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


TRACE_EVENT_TYPES = {"line_exec", "branch_eval", "return"}
LOOP_LINE_PATTERN = re.compile(r"^\s*(?:}\s*)?(?:for\b|while\b|do\b)")
METHOD_DECL_PATTERN = re.compile(
    r"^L(\d+)\s+"
    r"(?!(?:if|for|while|switch|catch|return|new)\b)"
    r".*\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{"
)


@dataclass(frozen=True)
class TracePredictionTarget:
    dataset: str
    snippet: str
    case_id: str
    case_expression: str
    prompt_source: str
    prompt_source_path: Path
    trace_path: Path
    gold_prompt_lines: List[int]
    target_method_name: str
    target_method_prompt_line_start: int
    target_method_prompt_line_end: int
    allowed_prompt_lines: List[int]
    loop_prompt_lines: List[int]


@dataclass(frozen=True)
class TraceParseResult:
    parsed_lines: List[int]
    parse_mode: str
    parse_valid: bool
    failure_reason: str = ""


def _ordered_unique(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        key = str(value)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _method_spans_from_prompt_lines(prompt_lines: Sequence[str]) -> Dict[str, tuple[int, int]]:
    spans: Dict[str, tuple[int, int]] = {}
    active_name = ""
    active_start = -1
    brace_depth = 0
    for line in prompt_lines:
        lm = re.match(r"^L(\d+)\s+(.*)$", line)
        if not lm:
            continue
        line_no = int(lm.group(1))
        code = lm.group(2)
        if not active_name:
            decl = METHOD_DECL_PATTERN.match(line)
            if not decl:
                continue
            active_name = str(decl.group(2))
            active_start = int(decl.group(1))
            brace_depth = code.count("{") - code.count("}")
            if brace_depth <= 0:
                spans[active_name] = (active_start, active_start)
                active_name = ""
                active_start = -1
            continue
        brace_depth += code.count("{") - code.count("}")
        if brace_depth <= 0:
            spans[active_name] = (active_start, line_no)
            active_name = ""
            active_start = -1
    return spans


def _infer_target_method_name(
    *,
    trace_obj: Dict[str, object],
    prompt_lines: Sequence[str],
    case_expression: str,
) -> str:
    called_methods = _ordered_unique(
        str(m) for m in (trace_obj.get("called_methods", []) or []) if str(m) != "main"
    )
    if called_methods:
        return called_methods[0]

    event_methods = _ordered_unique(
        str(event.get("method_name", ""))
        for event in (trace_obj.get("events", []) or [])
        if str(event.get("method_name", "")) and str(event.get("method_name", "")) != "main"
    )
    if event_methods:
        return event_methods[0]

    method_spans = _method_spans_from_prompt_lines(prompt_lines)
    declared_methods = [name for name in method_spans if name != "main"]
    if len(declared_methods) == 1:
        return declared_methods[0]

    case_methods = _ordered_unique(re.findall(r"\b([A-Za-z_]\w*)\s*\(", case_expression))
    matching_case_methods = [name for name in case_methods if name in method_spans and name != "main"]
    if len(matching_case_methods) == 1:
        return matching_case_methods[0]

    if "f" in method_spans and "main" in method_spans and len(declared_methods) <= 2:
        return "f"

    return ""


def _build_target_from_paths(
    *,
    dataset: str,
    snippet: str,
    case_id: str,
    case_expression: str,
    prompt_source_path: Path,
    trace_path: Path,
) -> TracePredictionTarget:
    trace_obj = json.loads(trace_path.read_text(encoding="utf-8"))
    prompt_source = prompt_source_path.read_text(encoding="utf-8")
    prompt_lines = prompt_source.splitlines()

    gold_prompt_lines: List[int] = []
    target_method_name = _infer_target_method_name(
        trace_obj=trace_obj,
        prompt_lines=prompt_lines,
        case_expression=case_expression,
    )
    if not target_method_name:
        raise RuntimeError(f"Could not infer target method for {snippet}/{case_id}.")
    for event in trace_obj.get("events", []) or []:
        if event.get("event_type") not in TRACE_EVENT_TYPES:
            continue
        if str(event.get("method_name", "")) == "main":
            continue
        if "prompt_line" not in event:
            continue
        gold_prompt_lines.append(int(event["prompt_line"]))

    method_spans = _method_spans_from_prompt_lines(prompt_lines)
    method_start = -1
    method_end = -1
    if target_method_name in method_spans:
        method_start, method_end = method_spans[target_method_name]
    if method_start < 0 or method_end < 0:
        raise RuntimeError(f"Could not determine prompt line span for method {target_method_name}.")

    allowed_prompt_lines: List[int] = []
    loop_prompt_lines: List[int] = []
    for line in prompt_lines:
        lm = re.match(r"^L(\d+)\s+(.*)$", line)
        if not lm:
            continue
        line_no = int(lm.group(1))
        if line_no < method_start or line_no > method_end:
            continue
        code = lm.group(2)
        if code.strip() in {"", "{", "}"}:
            continue
        if re.search(rf"\b{re.escape(target_method_name)}\s*\(", code):
            continue
        if code.strip() == "}":
            continue
        if code.strip().startswith("@"):
            continue
        if code.strip().startswith("class "):
            continue
        if code.strip().startswith("public class "):
            continue
        if code.strip().startswith("private class "):
            continue
        if code.strip().startswith("protected class "):
            continue
        if code.strip().startswith("static class "):
            continue
        if code.strip().endswith("{") and re.search(
            r"\b(if|else\s+if|for|while|do|switch|try|catch|finally|synchronized)\b",
            code,
        ) is None:
            continue
        if code.strip() == "}":
            continue
        allowed_prompt_lines.append(line_no)
        if LOOP_LINE_PATTERN.match(code):
            loop_prompt_lines.append(line_no)

    return TracePredictionTarget(
        dataset=dataset,
        snippet=snippet,
        case_id=case_id,
        case_expression=case_expression,
        prompt_source=prompt_source,
        prompt_source_path=prompt_source_path,
        trace_path=trace_path,
        gold_prompt_lines=gold_prompt_lines,
        target_method_name=target_method_name,
        target_method_prompt_line_start=method_start,
        target_method_prompt_line_end=method_end,
        allowed_prompt_lines=allowed_prompt_lines,
        loop_prompt_lines=loop_prompt_lines,
    )


def load_trace_prediction_target(
    *,
    dataset_root: Path,
    snippet: str,
    case_id: str,
) -> TracePredictionTarget:
    snippet_dir = dataset_root / snippet
    manifest = json.loads((snippet_dir / "snippet_manifest.json").read_text(encoding="utf-8"))
    case_entry = None
    for item in manifest.get("cases", []):
        if str(item.get("case_id")) == case_id:
            case_entry = item
            break
    if case_entry is None:
        raise FileNotFoundError(f"Case {snippet}/{case_id} not found in snippet manifest.")

    return _build_target_from_paths(
        dataset="humaneval",
        snippet=snippet,
        case_id=case_id,
        case_expression=str(case_entry["case_expression"]),
        prompt_source_path=snippet_dir / "canonical_source_numbered.txt",
        trace_path=Path(str(case_entry["trace_original_path"])),
    )


def load_trace_prediction_target_from_entry(entry: Dict[str, object]) -> TracePredictionTarget:
    return _build_target_from_paths(
        dataset=str(entry.get("dataset", "humaneval")),
        snippet=str(entry["snippet"]),
        case_id=str(entry["case_id"]),
        case_expression=str(entry["case_expression"]),
        prompt_source_path=Path(str(entry["prompt_source_path"])),
        trace_path=Path(str(entry["trace_path"])),
    )


def build_trace_prediction_instruction(
    target: TracePredictionTarget,
    *,
    prompt_style: str = "plain_numbers",
) -> str:
    base = (
        "You are given a numbered Java source file with comments removed and one test case.\n"
        "Simulate the execution of the case.\n"
        "Output the executed line numbers inside the target method, in execution order.\n"
        "Include repeated line numbers when the same line executes multiple times.\n"
        "Do not output any main-harness or setup-code lines.\n"
        f"Case: {target.case_expression}\n"
    )
    if prompt_style == "plain_numbers":
        return (
            base
            + "Use the source line labels shown in the file, but output only the integer parts.\n"
            + "Return one line of integers separated by single spaces.\n"
            + "Do not output any words, commas, brackets, quotes, explanations, or code fences.\n"
            + "Example format: 1 1 2 3 5"
        )
    if prompt_style == "json_array":
        return (
            base
            + "Return ONLY a JSON array of integers.\n"
            + "Do not output any explanation or extra text.\n"
            + "Example format: [1, 1, 2, 3, 5]"
        )
    if prompt_style == "json_array_method_scoped":
        return (
            base
            + f"The traced method is {target.target_method_name}.\n"
            + f"Only output lines executed inside {target.target_method_name}, from "
            + f"L{target.target_method_prompt_line_start:03d} to L{target.target_method_prompt_line_end:03d}.\n"
            + "Never output any line from main or setup code.\n"
            + "Return ONLY a JSON array of integers.\n"
            + "Do not output any explanation or extra text.\n"
            + "Example format: [1, 1, 2, 3, 5]"
        )
    if prompt_style == "json_array_loop_semantics":
        allowed_str = ", ".join(str(v) for v in target.allowed_prompt_lines)
        loop_str = ", ".join(str(v) for v in target.loop_prompt_lines) if target.loop_prompt_lines else "none"
        return (
            base
            + f"The traced method is {target.target_method_name}.\n"
            + f"Only output lines executed inside {target.target_method_name}, from "
            + f"L{target.target_method_prompt_line_start:03d} to L{target.target_method_prompt_line_end:03d}.\n"
            + f"The only valid output line numbers are: [{allowed_str}].\n"
            + f"Loop-condition lines in this method are: [{loop_str}].\n"
            + "Loop lines must be repeated once for every condition check.\n"
            + "If a loop body runs N times, output that loop line N+1 times: once before each iteration and once for the final failed check.\n"
            + "If a loop body runs zero times, still output the loop line once for the failed initial check.\n"
            + "Return lines appear once when they execute.\n"
            + "Never output any line from main or setup code.\n"
            + "Return ONLY a JSON array of integers.\n"
            + "Do not output any explanation or extra text.\n"
            + "Example format: [1, 1, 2, 3, 5]"
        )
    raise ValueError(f"Unsupported prompt_style '{prompt_style}'.")


def parse_predicted_line_sequence_with_meta(text: str) -> TraceParseResult:
    stripped = text.strip()
    if not stripped:
        return TraceParseResult(parsed_lines=[], parse_mode="empty", parse_valid=False, failure_reason="empty_output")

    array_match = re.search(r"\[(?:\s*\d+\s*(?:,\s*\d+\s*)*)?]", stripped, re.S)
    if array_match:
        payload = array_match.group(0)
        try:
            data = json.loads(payload)
        except Exception as exc:
            return TraceParseResult(
                parsed_lines=[],
                parse_mode="json_array_invalid",
                parse_valid=False,
                failure_reason=f"json_load_failed:{type(exc).__name__}",
            )
        if isinstance(data, list):
            out: List[int] = []
            for item in data:
                if isinstance(item, int):
                    out.append(item)
                elif isinstance(item, str) and item.strip().isdigit():
                    out.append(int(item.strip()))
                else:
                    return TraceParseResult(
                        parsed_lines=[],
                        parse_mode="json_array_invalid_item",
                        parse_valid=False,
                        failure_reason="non_integer_item",
                    )
            return TraceParseResult(parsed_lines=out, parse_mode="json_array", parse_valid=True)

    if "[" in stripped or "]" in stripped:
        recovered = [int(tok) for tok in re.findall(r"\d+", stripped)]
        return TraceParseResult(
            parsed_lines=recovered,
            parse_mode="json_array_truncated",
            parse_valid=False,
            failure_reason="unbalanced_or_truncated_array",
        )

    if re.fullmatch(r"[\s\d,]+", stripped):
        out = [int(tok) for tok in re.findall(r"\d+", stripped)]
        return TraceParseResult(parsed_lines=out, parse_mode="plain_numbers", parse_valid=bool(out), failure_reason="" if out else "no_digits")

    recovered = [int(tok) for tok in re.findall(r"\d+", stripped)]
    return TraceParseResult(
        parsed_lines=recovered,
        parse_mode="regex_recovery",
        parse_valid=False,
        failure_reason="unexpected_text_wrapper",
    )


def parse_predicted_line_sequence(text: str) -> List[int]:
    return parse_predicted_line_sequence_with_meta(text).parsed_lines


def _lcs_len(a: Sequence[int], b: Sequence[int]) -> int:
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        prev = 0
        for j in range(1, len(b) + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    return dp[-1]


def evaluate_trace_prediction(
    *,
    predicted: Sequence[int],
    gold: Sequence[int],
) -> Dict[str, float | int | bool]:
    pred = list(predicted)
    target = list(gold)
    lcs = _lcs_len(pred, target)
    ordered_precision = float(lcs / len(pred)) if pred else 0.0
    ordered_recall = float(lcs / len(target)) if target else 0.0
    ordered_f1 = (
        2.0 * ordered_precision * ordered_recall / (ordered_precision + ordered_recall)
        if (ordered_precision + ordered_recall) > 0
        else 0.0
    )
    prefix_matches = 0
    for left, right in zip(pred, target):
        if left != right:
            break
        prefix_matches += 1
    position_matches = sum(1 for left, right in zip(pred, target) if left == right)
    return {
        "exact_match": pred == target,
        "gold_length": len(target),
        "predicted_length": len(pred),
        "lcs_length": lcs,
        "ordered_precision": ordered_precision,
        "ordered_recall": ordered_recall,
        "ordered_f1": ordered_f1,
        "prefix_match_length": prefix_matches,
        "prefix_recall": float(prefix_matches / len(target)) if target else 0.0,
        "position_accuracy": float(position_matches / len(target)) if target else 0.0,
    }
