from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from util import utity


GENERATOR_VERSION = "cf-v2"
CASES_BEGIN = "### CASES_BEGIN"
CASES_END = "### CASES_END"


def resolve_task_profile(dataset: str, requested: str) -> str:
    ds = dataset.strip().lower()
    # Hard-switch policy: humaneval/cruxeval always use counterfactual T/F.
    if ds in {"humaneval", "cruxeval"}:
        return "counterfactual_tf"
    if requested == "auto":
        return "stdout"
    return requested


def _stable_hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8", errors="ignore"))
        h.update(b"\x00")
    return h.hexdigest()


def _extract_main_body(java_code: str) -> Optional[Tuple[int, int, str]]:
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
                return body_start, idx, java_code[body_start:idx]
        idx += 1
    return None


def _replace_main_body(java_code: str, new_body: str) -> str:
    located = _extract_main_body(java_code)
    if not located:
        return java_code
    start, end, _ = located
    return java_code[:start] + "\n" + new_body + "\n" + java_code[end:]


def _split_top_level_csv(exprs: str) -> List[str]:
    out: List[str] = []
    cur: List[str] = []
    depth = 0
    in_str = False
    escape = False
    for ch in exprs:
        if in_str:
            cur.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            cur.append(ch)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            token = "".join(cur).strip()
            if token:
                out.append(token)
            cur = []
            continue
        cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        out.append(tail)
    return out


@dataclass
class SeedExpr:
    expr: str
    origin: str
    prelude: str = ""


def _extract_humaneval_seeds(java_code: str) -> List[SeedExpr]:
    seeds: List[SeedExpr] = []
    main_loc = _extract_main_body(java_code)
    if not main_loc:
        return seeds
    _, _, body = main_loc

    m = re.search(r"List<Boolean>\s+correct\s*=\s*Arrays\.asList\s*\(", body, re.DOTALL)
    if m:
        start = m.end()
        depth = 1
        i = start
        while i < len(body):
            ch = body[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        expr_block = body[start:i]
        prelude = body[:m.start()].strip()
        for expr in _split_top_level_csv(expr_block):
            seeds.append(SeedExpr(expr=expr, origin="humaneval.correct_list", prelude=prelude))
        return seeds

    throw_pat = re.compile(
        r"if\s*\(\s*(?P<cond>.*?)\s*\)\s*\{\s*throw\s+new\s+AssertionError\s*\(\s*\)\s*;\s*\}",
        re.DOTALL,
    )
    for tm in throw_pat.finditer(body):
        cond = tm.group("cond").strip()
        prelude = body[:tm.start()].strip()
        if cond:
            seeds.append(SeedExpr(expr=f"!({cond})", origin="humaneval.if_throw", prelude=prelude))
    return seeds


def _extract_cruxeval_seeds(java_code: str) -> List[SeedExpr]:
    seeds: List[SeedExpr] = []
    main_loc = _extract_main_body(java_code)
    if not main_loc:
        return seeds
    _, _, body = main_loc
    idx = 0
    while True:
        m = re.search(r"\bassert\s*\(", body[idx:])
        if not m:
            break
        start = idx + m.end()
        depth = 1
        i = start
        while i < len(body):
            ch = body[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        expr = body[start:i].strip()
        if expr:
            seeds.append(SeedExpr(expr=expr, origin="cruxeval.assert", prelude=""))
        idx = i + 1
    return seeds


def _extract_seed_expressions(java_code: str, dataset: str) -> List[SeedExpr]:
    ds = dataset.strip().lower()
    if ds == "humaneval":
        return _extract_humaneval_seeds(java_code)
    if ds == "cruxeval":
        return _extract_cruxeval_seeds(java_code)
    return []


def _mutate_expr_false(expr: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []

    # Prefer non-opposite mutations first so the pack is less redundant.
    comp = re.match(r"^(?P<lhs>.+?)\s*(?P<op><=|>=|==|!=|<|>)\s*(?P<rhs>.+?)\s*$", expr)
    if comp:
        lhs = comp.group("lhs").strip()
        op = comp.group("op")
        rhs = comp.group("rhs").strip()
        try:
            rhs_num = float(rhs)
        except Exception:
            rhs_num = None
        if rhs_num is not None:
            if op == "==":
                alt = rhs_num + (0.1 if abs(rhs_num) < 1 else 1.0)
                out.append((f"{lhs} == {alt}", "expected_value_mutation"))
            elif op == "<":
                out.append((f"{lhs} < 0.0", "threshold_mutation"))
            elif op == "<=":
                out.append((f"{lhs} <= -1.0", "threshold_mutation"))
            elif op == ">":
                out.append((f"{lhs} > {rhs_num + 1000.0}", "threshold_mutation"))
            elif op == ">=":
                out.append((f"{lhs} >= {rhs_num + 1000.0}", "threshold_mutation"))

    num_pat = re.search(r"(-?\d+(?:\.\d+)?)", expr)
    if num_pat:
        token = num_pat.group(1)
        try:
            if "." in token:
                val = float(token)
                repl = f"{val + 1.0:.6f}".rstrip("0").rstrip(".")
            else:
                repl = str(int(token) + 1)
            out.append((expr[:num_pat.start()] + repl + expr[num_pat.end():], "literal_perturbation"))
        except Exception:
            pass

    if ".equals(" in expr:
        out.append((f"!({expr})", "expected_value_mutation"))

    call_arg = re.search(r"\(([^()]*)\)", expr)
    if call_arg and call_arg.group(1).strip():
        parts = _split_top_level_csv(call_arg.group(1))
        if parts:
            parts[-1] = f"({parts[-1]})"
        repl = ", ".join(parts)
        out.append((expr[:call_arg.start(1)] + repl + expr[call_arg.end(1):], "argument_perturbation"))

    # Direct-opposite forms are fallback only.
    flips = [
        ("==", "!="),
        ("!=", "=="),
        (">=", "<"),
        ("<=", ">"),
        (">", "<="),
        ("<", ">="),
    ]
    for a, b in flips:
        if a in expr:
            out.append((expr.replace(a, b, 1), f"comparator_flip:{a}->{b}"))

    out.append((f"!({expr})", "negation_fallback"))
    dedup: List[Tuple[str, str]] = []
    seen = set()
    for e, k in out:
        key = e.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        dedup.append((key, k))
    return dedup


def _build_eval_body(expr: str, prelude: str) -> str:
    pre = prelude.strip()
    lines = []
    if pre:
        lines.append(pre)
    lines.append(f"boolean __cfv = ({expr});")
    lines.append('System.out.println(__cfv ? "T" : "F");')
    return "\n".join(lines)


def _eval_expr_bool(java_code: str, class_name: str, expr: str, prelude: str) -> Optional[bool]:
    patched = _replace_main_body(java_code, _build_eval_body(expr, prelude))
    result = utity.run_java_program_with_result(patched, class_name, enable_assertions=True)
    if not result.get("compiled", False) or not result.get("success", False):
        return None
    out = str(result.get("stdout", "")).strip().upper()
    if out.endswith("T"):
        return True
    if out.endswith("F"):
        return False
    return None


def _run_program_passes(java_code: str, class_name: str) -> bool:
    result = utity.run_java_program_with_result(java_code, class_name, enable_assertions=True)
    return bool(result.get("compiled", False) and result.get("success", False))


def _bool_to_tf(v: bool) -> str:
    return "T" if v else "F"


def _make_case(case_id: str, expr: str, expected: bool, origin: str, mutation_type: str) -> Dict[str, object]:
    return {
        "case_id": case_id,
        "expr": expr,
        "expected_bool": bool(expected),
        "origin": origin,
        "mutation_type": mutation_type,
    }


def _fallback_program_level_cases(snippet: str, program_passes: bool, target_cases: int) -> List[Dict[str, object]]:
    cases: List[Dict[str, object]] = []
    true_expr = "true" if program_passes else "false"
    false_expr = "false" if program_passes else "true"
    cases.append(_make_case("c001", true_expr, True, "fallback.program", "program_truth"))
    cases.append(_make_case("c002", false_expr, False, "fallback.program", "program_false"))
    return cases


def _cap_pure_literal_cases(
    cases: List[Dict[str, object]],
    *,
    max_literal_cases: int = 2,
) -> List[Dict[str, object]]:
    kept: List[Dict[str, object]] = []
    literal_count = 0
    for case in cases:
        expr = str(case.get("expr", "")).strip().lower()
        is_literal = expr in {"true", "false"}
        if is_literal:
            if literal_count >= max_literal_cases:
                continue
            literal_count += 1
        kept.append(dict(case))

    for i, case in enumerate(kept, start=1):
        case["case_id"] = f"c{i:03d}"
    return kept


def _rebalance_cases(
    cases: List[Dict[str, object]],
    *,
    min_cases: int,
    target_cases: int,
) -> List[Dict[str, object]]:
    """Rebalance T/F mix toward ~50/50 without synthesizing trivial cases."""
    total = len(cases)
    if total == 0:
        return cases

    # Keep total within configured upper bound only (no synthetic upsampling).
    total = min(total, target_cases)
    true_cases = [dict(c) for c in cases if bool(c.get("expected_bool"))]
    false_cases = [dict(c) for c in cases if not bool(c.get("expected_bool"))]

    if not true_cases or not false_cases:
        kept = (true_cases + false_cases)[:total]
        for i, case in enumerate(kept, start=1):
            case["case_id"] = f"c{i:03d}"
        return kept

    desired_true = total // 2
    desired_false = total - desired_true

    pick_true = min(desired_true, len(true_cases))
    pick_false = min(desired_false, len(false_cases))
    picked_true = true_cases[:pick_true]
    picked_false = false_cases[:pick_false]

    remaining = total - (pick_true + pick_false)
    extra_true = true_cases[pick_true:]
    extra_false = false_cases[pick_false:]
    while remaining > 0 and (extra_true or extra_false):
        if len(extra_true) >= len(extra_false) and extra_true:
            picked_true.append(extra_true.pop(0))
        elif extra_false:
            picked_false.append(extra_false.pop(0))
        remaining -= 1

    # Interleave for stable mixed ordering.
    balanced: List[Dict[str, object]] = []
    for idx in range(max(len(picked_true), len(picked_false))):
        if idx < len(picked_true):
            balanced.append(picked_true[idx])
        if idx < len(picked_false):
            balanced.append(picked_false[idx])
        if len(balanced) >= total:
            break

    # Reindex case_id deterministically after rebalance.
    for i, case in enumerate(balanced, start=1):
        case["case_id"] = f"c{i:03d}"
    return balanced


def build_case_pack(
    *,
    java_code: str,
    class_name: str,
    dataset: str,
    snippet: str,
    min_cases: int = 8,
    target_cases: int = 16,
    cache_dir: Optional[Path | str] = None,
    rebuild: bool = False,
) -> Dict[str, object]:
    ds = dataset.strip().lower()
    min_cases = max(2, int(min_cases))
    target_cases = max(min_cases, int(target_cases))
    src_hash = _stable_hash(java_code, class_name, ds, snippet, str(min_cases), str(target_cases), GENERATOR_VERSION)
    cache_path: Optional[Path] = None
    if cache_dir is not None:
        cache_dir = Path(cache_dir)
        cache_path = cache_dir / ds / f"{snippet}.json"
        if cache_path.exists() and not rebuild:
            try:
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
                if payload.get("source_hash") == src_hash and payload.get("generator_version") == GENERATOR_VERSION:
                    return payload
            except Exception:
                pass

    seeds = _extract_seed_expressions(java_code, ds)
    cases: List[Dict[str, object]] = []
    case_idx = 1
    true_count = 0
    false_count = 0

    for seed in seeds:
        t_eval = _eval_expr_bool(java_code, class_name, seed.expr, seed.prelude)
        if t_eval is not True:
            # Seed must be true-case by definition; skip unstable seed.
            continue
        cases.append(_make_case(f"c{case_idx:03d}", seed.expr, True, seed.origin, "seed_true"))
        case_idx += 1
        true_count += 1

        false_added = False
        for cand_expr, mut_kind in _mutate_expr_false(seed.expr):
            v = _eval_expr_bool(java_code, class_name, cand_expr, seed.prelude)
            if v is False:
                cases.append(_make_case(f"c{case_idx:03d}", cand_expr, False, seed.origin, mut_kind))
                case_idx += 1
                false_count += 1
                false_added = True
                break
        if not false_added:
            # Guaranteed fallback from validated seed truth.
            neg = f"!({seed.expr})"
            cases.append(_make_case(f"c{case_idx:03d}", neg, False, seed.origin, "negation_fallback"))
            case_idx += 1
            false_count += 1
        if len(cases) >= target_cases:
            break

    if not cases:
        prog_ok = _run_program_passes(java_code, class_name)
        cases = _fallback_program_level_cases(snippet, prog_ok, target_cases)
        true_count = sum(1 for c in cases if c["expected_bool"] is True)
        false_count = len(cases) - true_count

    # Enforce at least one true and one false (without trivial true/false padding).
    if true_count == 0:
        cases.append(_make_case(f"c{case_idx:03d}", "!(false)", True, "balance", "forced_true"))
        case_idx += 1
        true_count += 1
    if false_count == 0:
        cases.append(_make_case(f"c{case_idx:03d}", "!(true)", False, "balance", "forced_false"))
        case_idx += 1
        false_count += 1

    if len(cases) > target_cases:
        cases = cases[:target_cases]
    cases = _rebalance_cases(cases, min_cases=min_cases, target_cases=target_cases)
    cases = _cap_pure_literal_cases(cases, max_literal_cases=2)
    true_count = sum(1 for c in cases if c["expected_bool"] is True)
    false_count = len(cases) - true_count

    payload: Dict[str, object] = {
        "profile": "counterfactual_tf",
        "dataset": ds,
        "snippet": snippet,
        "class_name": class_name,
        "generator_version": GENERATOR_VERSION,
        "source_hash": src_hash,
        "generation_policy": "validated_nontrivial_only",
        "min_cases_config": int(min_cases),
        "target_cases_config": int(target_cases),
        "effective_case_count": int(len(cases)),
        "cases": cases,
        "balance_stats": {
            "case_total": len(cases),
            "true_count": true_count,
            "false_count": false_count,
            "true_ratio": (float(true_count) / float(len(cases))) if cases else 0.0,
        },
        "warnings": [],
    }
    if len(cases) < 4:
        payload["warnings"].append(
            f"low_effective_case_count:{len(cases)} (consider reviewing extraction/mutation coverage)"
        )
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def build_counterfactual_instruction(case_pack: Dict[str, object]) -> str:
    cases = case_pack.get("cases", [])
    lines = [
        "You are given a Java program.",
        "Predict each listed boolean case as T or F using program semantics.",
        "Evaluate each case expression directly; do not assume all tests pass.",
        "Return ONLY one JSON object from case_id to \"T\" or \"F\". No prose.",
        CASES_BEGIN,
    ]
    for c in cases:
        lines.append(f"{c['case_id']}: {c['expr']}")
    lines.append(CASES_END)
    return "\n".join(lines)


def parse_predicted_labels(
    text: str,
    case_ids: Sequence[str],
    strict_json: bool = True,
) -> Tuple[Dict[str, bool], Dict[str, object]]:
    raw = text or ""
    parsed: Dict[str, bool] = {}
    mode = "none"
    def _consume_json_obj(obj: object) -> int:
        local = 0
        if isinstance(obj, dict):
            for k, v in obj.items():
                kk = str(k).strip().strip('"').strip("'")
                if isinstance(v, str):
                    vv = v.strip().upper()
                    if vv in {"T", "TRUE"}:
                        parsed[kk] = True
                        local += 1
                    elif vv in {"F", "FALSE"}:
                        parsed[kk] = False
                        local += 1
                elif isinstance(v, bool):
                    parsed[kk] = bool(v)
                    local += 1
        return local

    # 1) Whole-text JSON parse.
    try:
        if _consume_json_obj(json.loads(raw)) > 0:
            mode = "json"
    except Exception:
        pass

    # 2) Embedded JSON object extraction for responses that prepend prose/code.
    if not parsed:
        best_obj = None
        best_hits = 0
        for m in re.finditer(r"\{[\s\S]*?\}", raw):
            candidate = m.group(0)
            try:
                obj = json.loads(candidate)
            except Exception:
                continue
            hits = 0
            if isinstance(obj, dict):
                for k in obj.keys():
                    if str(k).strip().strip('"').strip("'") in set(case_ids):
                        hits += 1
            if hits > best_hits:
                best_hits = hits
                best_obj = obj
        if best_obj is not None and _consume_json_obj(best_obj) > 0:
            mode = "embedded_json"

    if not parsed:
        rx = re.compile(r'"?([A-Za-z0-9_.-]+)"?\s*(?::|=|->)\s*"?\b(T|F|TRUE|FALSE)\b"?', re.IGNORECASE)
        for m in rx.finditer(raw):
            k = m.group(1).strip()
            v = m.group(2).strip().upper()
            parsed[k] = v in {"T", "TRUE"}
        if parsed:
            mode = "regex"

    if strict_json and mode == "none":
        # Keep empty parse; caller will count missing as wrong.
        mode = "strict_json_fail"

    present = sum(1 for cid in case_ids if cid in parsed)
    meta = {
        "parse_mode": mode,
        "provided_case_count": present,
        "requested_case_count": len(case_ids),
    }
    return parsed, meta


def score_case_predictions(
    case_pack: Dict[str, object],
    predicted: Dict[str, bool],
) -> Dict[str, object]:
    cases = case_pack.get("cases", [])
    total = len(cases)
    correct = 0
    oracle_labels: Dict[str, str] = {}
    predicted_labels: Dict[str, str] = {}
    per_case: List[Dict[str, object]] = []

    for c in cases:
        cid = str(c["case_id"])
        expected = bool(c["expected_bool"])
        oracle_labels[cid] = _bool_to_tf(expected)
        pred = predicted.get(cid, None)
        if pred is None:
            predicted_labels[cid] = "MISSING"
            is_ok = False
        else:
            predicted_labels[cid] = _bool_to_tf(bool(pred))
            is_ok = bool(pred) == expected
        if is_ok:
            correct += 1
        per_case.append(
            {
                "case_id": cid,
                "expected": oracle_labels[cid],
                "predicted": predicted_labels[cid],
                "correct": is_ok,
                "origin": c.get("origin", ""),
                "mutation_type": c.get("mutation_type", ""),
            }
        )

    accuracy = float(correct) / float(total) if total else 0.0
    return {
        "case_total": total,
        "case_correct": correct,
        "case_accuracy": accuracy,
        "all_cases_pass": (correct == total and total > 0),
        "oracle_labels": oracle_labels,
        "predicted_labels": predicted_labels,
        "per_case": per_case,
    }
