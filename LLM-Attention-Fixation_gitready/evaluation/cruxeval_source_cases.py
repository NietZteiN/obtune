from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


def _load_humaneval_module():
    module_path = Path(__file__).resolve().with_name("humaneval_source_cases.py")
    spec = importlib.util.spec_from_file_location("_cruxeval_humaneval_source_cases", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module from {module_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_HUMANEVAL_MOD = _load_humaneval_module()

SourceCaseBuildError = _HUMANEVAL_MOD.SourceCaseBuildError
_display_line = _HUMANEVAL_MOD._display_line
_extract_main_body_bounds = _HUMANEVAL_MOD._extract_main_body_bounds
_line_number_for_index = _HUMANEVAL_MOD._line_number_for_index
_line_starts = _HUMANEVAL_MOD._line_starts
_scan_matching = _HUMANEVAL_MOD._scan_matching
apply_prompt_line_mapping = _HUMANEVAL_MOD.apply_prompt_line_mapping
build_prompt_source_view = _HUMANEVAL_MOD.build_prompt_source_view
render_numbered_source = _HUMANEVAL_MOD.render_numbered_source
summary_for_cases = _HUMANEVAL_MOD.summary_for_cases
write_json = _HUMANEVAL_MOD.write_json


@dataclass(frozen=True)
class CruxevalSourceCase:
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


def extract_cruxeval_source_cases(java_code: str) -> List[CruxevalSourceCase]:
    bounds = _extract_main_body_bounds(java_code)
    if not bounds:
        return []

    body_start, body_end = bounds
    body = java_code[body_start:body_end]
    starts = _line_starts(java_code)
    cases: List[CruxevalSourceCase] = []
    cursor = 0
    case_idx = 1

    while True:
        match = re.search(r"\bassert\s*\(", body[cursor:])
        if not match:
            break

        open_idx = body_start + cursor + match.end() - 1
        close_idx = _scan_matching(java_code, open_idx, "(", ")")
        expr_block = java_code[open_idx + 1 : close_idx]
        expr = expr_block.strip()
        if expr:
            abs_start = open_idx + 1 + (len(expr_block) - len(expr_block.lstrip()))
            abs_end = open_idx + 1 + len(expr_block.rstrip())
            line_start = _line_number_for_index(starts, abs_start)
            line_end = _line_number_for_index(starts, max(abs_end - 1, abs_start))
            cases.append(
                CruxevalSourceCase(
                    case_id=f"c{case_idx:03d}",
                    expr=expr,
                    origin="assert",
                    expected_bool=True,
                    trace_mode="expression",
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
            case_idx += 1

        cursor = (close_idx - body_start) + 1

    return cases


__all__ = [
    "CruxevalSourceCase",
    "SourceCaseBuildError",
    "apply_prompt_line_mapping",
    "build_prompt_source_view",
    "extract_cruxeval_source_cases",
    "render_numbered_source",
    "summary_for_cases",
    "write_json",
]
