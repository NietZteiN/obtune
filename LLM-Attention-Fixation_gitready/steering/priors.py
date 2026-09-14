from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Sequence, List, Optional

import numpy as np
import re


@dataclass
class PriorContext:
    prompt_tokens: Sequence[str]
    code_text: str
    vocab_tokens: Sequence[dict]
    prompt_text: str = ""


class PriorProvider:
    def __init__(self, context: PriorContext) -> None:
        self.context = context

    def _normalize(self, vec: np.ndarray) -> np.ndarray:
        s = vec.sum()
        if s <= 0:
            return np.full_like(vec, 1.0 / len(vec))
        return vec / s

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        raise NotImplementedError


class Semantic(PriorProvider):
    def __init__(self, context):
        super().__init__(context)
        pass
    """ To Do:
        Maybe we can make use of PDG. Let model focus on semantic preserving element through
        Control- or Data- flow 
    """


@dataclass
class _SliceNode:
    id: int
    kind: str  # stmt | predicate | return_expr | param
    ast_node: Any
    token_indices: List[int]
    defs: set[str]
    uses: set[str]
    depth: int
    stmt_id: Optional[int] = None


class HumanPrior(PriorProvider):
    def __init__(self, context: PriorContext, human_file: Path) -> None:
        super().__init__(context)
        self.vectors = self._load(human_file)

    def _load(self, file_path: Path) -> Sequence[np.ndarray]:
        if file_path.is_dir():
            return [self._aggregate_directory(file_path)]
        if file_path.suffix == ".json":
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return self._vectors_from_payload(data, file_path)
        rows = []
        with file_path.open("r", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if row:
                    rows.append([float(x) for x in row])
        if not rows:
            raise ValueError(f"No data in human prior file {file_path}")
        return [np.asarray(row, dtype=float) for row in rows]

    def _aggregate_directory(self, folder: Path) -> np.ndarray:
        vocab = list(self.context.vocab_tokens)
        if not vocab:
            vocab_path = folder / "vocabulary.json"
            if vocab_path.is_file():
                try:
                    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
                except Exception:
                    vocab = []
        vocab_len = len(vocab)
        if vocab_len == 0:
            vocab_len = len(self.context.prompt_tokens) or 1

        accumulator = np.zeros(vocab_len, dtype=float)
        participant_files = sorted(folder.glob("participant_*.json"))
        for participant in participant_files:
            try:
                payload = json.loads(participant.read_text(encoding="utf-8"))
            except Exception:
                continue
            scores = payload.get("total_scores")
            if not isinstance(scores, list):
                continue
            vec = np.asarray(
                [float(entry.get("score", 0.0)) for entry in scores],
                dtype=float,
            )
            if vec.size < vocab_len:
                padded = np.zeros(vocab_len, dtype=float)
                padded[: vec.size] = vec
                vec = padded
            elif vec.size > vocab_len:
                vec = vec[:vocab_len]
            accumulator += vec

        if accumulator.sum() == 0:
            accumulator += 1.0
        return accumulator

    def _vectors_from_payload(self, payload: Any, source: Path) -> Sequence[np.ndarray]:
        if isinstance(payload, dict):
            if "bins" in payload:
                return [np.asarray(vec, dtype=float) for vec in payload["bins"]]
            if "vector" in payload:
                return [np.asarray(payload["vector"], dtype=float)]
            if "total_scores" in payload:
                return [
                    np.asarray(
                        [float(entry.get("score", 0.0)) for entry in payload["total_scores"]],
                        dtype=float,
                    )
                ]
        if isinstance(payload, list):
            if payload and isinstance(payload[0], dict) and "score" in payload[0]:
                return [
                    np.asarray([float(entry.get("score", 0.0)) for entry in payload], dtype=float)
                ]
            length = len(payload) or 1
            return [np.ones(length, dtype=float)]
        raise ValueError(f"Unsupported human prior format in {source}")

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        vec = self.vectors[min(bin_idx, len(self.vectors) - 1)]
        if vec.size != len(self.context.prompt_tokens):
            vec = np.resize(vec, len(self.context.prompt_tokens))
        return self._normalize(vec)


class LexPrior(PriorProvider):
    def __init__(self, context: PriorContext, window: int) -> None:
        super().__init__(context)
        self.window = max(1, window)

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        total = len(self.context.prompt_tokens)
        stride = max(1, total // n_bins)
        start = min(bin_idx * stride, total - 1)
        end = min(start + self.window, total)
        vec = np.zeros(total, dtype=float)
        vec[start:end] = 1.0
        return self._normalize(vec)


class RandPrior(PriorProvider):
    def __init__(self, context: PriorContext, seed: int | None) -> None:
        super().__init__(context)
        self.rng = np.random.default_rng(seed)

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        vec = self.rng.random(len(self.context.prompt_tokens))
        return self._normalize(vec)


class UniformPrior(PriorProvider):
    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        vec = np.ones(len(self.context.prompt_tokens), dtype=float)
        return self._normalize(vec)


class ASTPrior(PriorProvider):
    """
    AST-aware prior using javalang. Falls back to a simple chunk heuristic if parsing fails.
    """

    tier_weights = {
        "tier1": 3.0,  # signatures and control
        "tier2": 2.0,  # calls / data flow
        "tier3": 1.0,  # literals / secondary
    }
    node_names = {
        "tier1": {
            "ClassDeclaration",
            "ConstructorDeclaration",
            "MethodDeclaration",
            "IfStatement",
            "WhileStatement",
            "ForStatement",
            "SwitchStatement",
            "TryStatement",
        },
        "tier2": {
            "MethodInvocation",
            "SuperMethodInvocation",
            "MemberReference",
            "Assignment",
            "ReturnStatement",
            "BinaryOperation",
            "UnaryOperation",
            "Cast",
            "InstanceOf",
        },
        "tier3": {
            "Literal",
            "ElementArrayValue",
            "ArraySelector",
            "This",
            "SuperConstructorInvocation",
            "ClassCreator",
            "ArrayCreator",
        },
    }

    def _try_import(self):
        try:
            import javalang  # type: ignore
            return javalang
        except Exception:
            return None

    def _tokenize(self, javalang_mod, code: str):
        try:
            return list(javalang_mod.tokenizer.tokenize(code))
        except Exception:
            return []

    def _sanitize_java_for_javalang(self, java_code: str) -> str:
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
        sanitized = re.sub(
            r"\b[A-Za-z_$][A-Za-z0-9_$.\[\]]*\s*::\s*[A-Za-z_$][A-Za-z0-9_$]*",
            "null",
            sanitized,
        )
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

    def _prepare_parse_artifacts(self, javalang_mod):
        raw_code = str(self.context.code_text or "")
        if not raw_code.strip():
            return None, [], None
        candidates: List[str] = [raw_code]
        sanitized_code = self._sanitize_java_for_javalang(raw_code)
        if sanitized_code != raw_code:
            candidates.append(sanitized_code)
        for candidate in candidates:
            tokens = self._tokenize(javalang_mod, candidate)
            if not tokens:
                continue
            try:
                tree = javalang_mod.parse.parse(candidate)
            except Exception:
                continue
            return candidate, tokens, tree
        return None, [], None

    def _select_target_method(self, tree, javalang_mod):
        methods = [node for _, node in tree.filter(javalang_mod.tree.MethodDeclaration)]
        if not methods:
            return None
        main = next((m for m in methods if m.name == "main"), None)
        non_main = [m for m in methods if m.name != "main"]
        if not non_main:
            return None

        def is_wrapper_like(method) -> bool:
            name = str(getattr(method, "name", "") or "")
            if not name:
                return False
            return name.startswith("_obf_") or re.match(r"^_+obf", name, flags=re.IGNORECASE) is not None

        def filter_wrappers(candidates):
            filtered = [m for m in candidates if not is_wrapper_like(m)]
            return filtered or list(candidates)

        if main:
            called = set()
            for _, inv in main.filter(javalang_mod.tree.MethodInvocation):
                if getattr(inv, "member", None):
                    called.add(inv.member)
            called_candidates = [m for m in non_main if m.name in called]
            if called_candidates:
                called_candidates = filter_wrappers(called_candidates)
                return max(called_candidates, key=lambda m: len(getattr(m, "body", []) or []))

        def nonvoid_params(method):
            ret = getattr(method, "return_type", None)
            params = getattr(method, "parameters", []) or []
            return ret is not None and len(params) > 0

        non_main = filter_wrappers(non_main)
        candidates = [m for m in non_main if nonvoid_params(m)]
        if candidates:
            return max(candidates, key=lambda m: len(getattr(m, "body", []) or []))
        return max(non_main, key=lambda m: len(getattr(m, "body", []) or []))

    def _position_index(self, tokens) -> Dict[tuple, int]:
        pos_map = {}
        for idx, tok in enumerate(tokens):
            if getattr(tok, "position", None):
                pos_map[tok.position] = idx
        return pos_map

    def _add_pos(self, node, weight: float, pos_map: Dict[tuple, int], scores: Dict[int, float]):
        if not node:
            return
        pos = getattr(node, "position", None)
        if pos and pos in pos_map:
            idx = pos_map[pos]
            scores[idx] = scores.get(idx, 0.0) + weight

    def _collect_scores(self, tree, tokens, javalang_mod) -> Dict[int, float]:
        pos_map = self._position_index(tokens)
        scores: Dict[int, float] = {}

        def walk(node, accumulated: float) -> None:
            if node is None:
                return
            ntype = type(node).__name__
            w_self = self._node_weight(ntype)
            total_w = accumulated + w_self
            if total_w > 0:
                self._add_pos(node, total_w, pos_map, scores)
                # for declarations, also tag their name/type positions if present
                if ntype in self.node_names["tier1"]:
                    if hasattr(node, "name"):
                        name_obj = getattr(node, "name", None)
                        if hasattr(name_obj, "position"):
                            self._add_pos(name_obj, total_w, pos_map, scores)
                    if hasattr(node, "parameters"):
                        for p in getattr(node, "parameters", []):
                            walk(p, total_w)
                    if hasattr(node, "type"):
                        walk(getattr(node, "type", None), total_w)
            # Recurse children to inherit this node's emphasis (accumulate)
            for child in getattr(node, "children", ()):
                if child is None:
                    continue
                if isinstance(child, (list, tuple)):
                    for c in child:
                        walk(c, total_w)
                else:
                    walk(child, total_w)

        # walk the parsed tree root
        walk(tree, 0.0)
        return scores

    @staticmethod
    def _normalize_prompt_piece(text: str) -> str:
        return (
            str(text)
            .replace("▁", "")
            .replace("Ġ", "")
            .replace("Ċ", "")
            .replace("ĉ", "")
            .replace("`", "")
            .strip()
            .lower()
        )

    def _is_skippable_prompt_piece(self, piece: str) -> bool:
        if not piece:
            return True
        return re.fullmatch(r"l?\d+", piece) is not None

    def _old_map_scores_to_prompt(self, token_scores: Dict[int, float], tokens, prompt_tokens: Sequence[str]) -> np.ndarray:
        total_len = len(prompt_tokens)
        vec = np.zeros(total_len, dtype=float)
        if not token_scores:
            return vec

        idx_to_text = {i: str(tok.value) for i, tok in enumerate(tokens)}
        lexemes = [(idx, idx_to_text[idx], score) for idx, score in token_scores.items()]
        lexemes.sort(key=lambda x: x[0], reverse=True)
        pt_idx = len(prompt_tokens) - 1
        for _, lex, score in lexemes:
            lex_clean = lex.strip()
            if not lex_clean:
                continue
            while pt_idx >= 0:
                token_text = prompt_tokens[pt_idx].replace("▁", "").strip()
                if token_text == "":
                    pt_idx -= 1
                    continue
                if token_text.lower().startswith(lex_clean.lower()):
                    vec[pt_idx] += score
                    pt_idx -= 1
                    break
                pt_idx -= 1
            if pt_idx < 0:
                    break
        return vec

    def _locate_lexeme_indices(
        self,
        lexeme: str,
        prompt_norms: Sequence[str],
        start_idx: int,
        *,
        skip_line_markers: bool = True,
    ) -> tuple[List[int], int]:
        lex_norm = self._normalize_prompt_piece(lexeme)
        if not lex_norm:
            return [], start_idx
        for start in range(start_idx, len(prompt_norms)):
            first_piece = prompt_norms[start]
            if first_piece == "":
                continue
            if skip_line_markers and self._is_skippable_prompt_piece(first_piece):
                continue
            built = ""
            indices: List[int] = []
            for idx in range(start, len(prompt_norms)):
                piece = prompt_norms[idx]
                if piece == "":
                    continue
                if skip_line_markers and self._is_skippable_prompt_piece(piece):
                    continue
                candidate = built + piece
                if candidate == lex_norm or lex_norm.startswith(candidate):
                    built = candidate
                    indices.append(idx)
                    if built == lex_norm:
                        return indices, idx + 1
                    continue
                break
        return [], start_idx

    def _build_prompt_alignment(self, tokens, prompt_tokens: Sequence[str]) -> Dict[int, List[int]]:
        prompt_norms = [self._normalize_prompt_piece(tok) for tok in prompt_tokens]
        alignment: Dict[int, List[int]] = {}
        cursor = 0
        for token_idx, tok in enumerate(tokens):
            indices, next_cursor = self._locate_lexeme_indices(str(tok.value), prompt_norms, cursor)
            if indices:
                alignment[token_idx] = indices
                cursor = next_cursor
        return alignment

    def _build_prompt_line_spans(self, prompt_tokens: Sequence[str]) -> Dict[int, List[int]]:
        prompt_text = str(getattr(self.context, "prompt_text", "") or "")
        if not prompt_text:
            return {}
        prompt_lines = []
        for line in prompt_text.splitlines():
            match = re.match(r"^\s*L(\d+)\s+", line)
            if match:
                prompt_lines.append(int(match.group(1)))
        if not prompt_lines:
            return {}

        prompt_norms = [self._normalize_prompt_piece(tok) for tok in prompt_tokens]
        starts: Dict[int, int] = {}
        marker_indices_by_line: Dict[int, set[int]] = {}
        cursor = 0
        for line_no in prompt_lines:
            marker = f"l{line_no:03d}"
            indices, next_cursor = self._locate_lexeme_indices(
                marker,
                prompt_norms,
                cursor,
                skip_line_markers=False,
            )
            if not indices:
                continue
            starts[line_no] = indices[0]
            marker_indices_by_line[line_no] = set(indices)
            cursor = next_cursor
        if not starts:
            return {}

        json_block_start = None
        for idx in range(cursor, len(prompt_norms) - 1):
            if prompt_norms[idx] == "json" and prompt_norms[idx + 1] == "array":
                json_block_start = idx
                break

        line_spans: Dict[int, List[int]] = {}
        ordered = [line_no for line_no in prompt_lines if line_no in starts]
        for pos, line_no in enumerate(ordered):
            start = starts[line_no]
            if pos + 1 < len(ordered):
                end = starts[ordered[pos + 1]]
            else:
                end = json_block_start if json_block_start is not None else len(prompt_tokens)
            indices = [
                idx
                for idx in range(start, max(start, end))
                if prompt_norms[idx]
                and idx not in marker_indices_by_line.get(line_no, set())
                and not self._is_skippable_prompt_piece(prompt_norms[idx])
            ]
            if indices:
                line_spans[line_no] = indices
        return line_spans

    def _source_line_lexemes(self, line: str) -> List[str]:
        return re.findall(
            r"[A-Za-z_$][A-Za-z0-9_$]*"
            r"|-?\d+(?:\.\d+)?(?:e[+-]?\d+)?"
            r"|<=|>=|==|!=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|%=|->"
            r"|[{}()\[\];,.:<>+\-*/=%!?]",
            str(line),
            flags=re.IGNORECASE,
        )

    def _build_prompt_source_line_spans(self, prompt_tokens: Sequence[str]) -> Dict[int, List[int]]:
        prompt_text = str(getattr(self.context, "prompt_text", "") or "")
        source_text = str(getattr(self.context, "code_text", "") or "")
        if not prompt_text or not source_text:
            return {}

        prompt_norms = [self._normalize_prompt_piece(tok) for tok in prompt_tokens]
        source_lines = source_text.splitlines()
        anchor_line_no: Optional[int] = None
        anchor_indices: List[int] = []
        cursor = 0

        for line_no, raw_line in enumerate(source_lines, start=1):
            lexemes = self._source_line_lexemes(raw_line)
            if not lexemes:
                continue
            matched: List[int] = []
            probe_cursor = cursor
            for lexeme in lexemes:
                indices, next_cursor = self._locate_lexeme_indices(
                    lexeme,
                    prompt_norms,
                    probe_cursor,
                    skip_line_markers=False,
                )
                if not indices:
                    continue
                matched.extend(indices)
                probe_cursor = next_cursor
            if matched:
                anchor_line_no = line_no
                anchor_indices = sorted(set(matched))
                cursor = probe_cursor
                break

        if anchor_line_no is None or not anchor_indices:
            return {}

        def newline_count(token: str) -> int:
            return str(token).count("Ċ") + str(token).count("\n")

        line_spans: Dict[int, List[int]] = {}
        current_line = int(anchor_line_no)
        current_indices: List[int] = []
        started = False
        start_idx = anchor_indices[0]
        last_line = len(source_lines)

        for idx in range(start_idx, len(prompt_tokens)):
            raw_tok = str(prompt_tokens[idx])
            if not started and idx < start_idx:
                continue
            started = True
            current_indices.append(idx)
            nl_count = newline_count(raw_tok)
            if nl_count <= 0:
                continue
            filtered = [
                i
                for i in current_indices
                if str(prompt_tokens[i]).strip()
                and str(prompt_tokens[i]).replace("Ċ", "").strip()
            ]
            line_spans[current_line] = filtered
            current_indices = []
            current_line += 1
            for _ in range(nl_count - 1):
                if current_line > last_line:
                    break
                line_spans.setdefault(current_line, [])
                current_line += 1
            if current_line > last_line:
                break

        if current_indices and current_line <= last_line:
            filtered = [
                i
                for i in current_indices
                if str(prompt_tokens[i]).strip()
                and str(prompt_tokens[i]).replace("Ċ", "").strip()
            ]
            line_spans[current_line] = filtered
        return line_spans

    def _map_scores_to_prompt(self, token_scores: Dict[int, float], tokens, prompt_tokens: Sequence[str]) -> np.ndarray:
        total_len = len(prompt_tokens)
        vec = np.zeros(total_len, dtype=float)
        if not token_scores:
            return vec

        line_spans = self._build_prompt_line_spans(prompt_tokens)
        if not line_spans:
            line_spans = self._build_prompt_source_line_spans(prompt_tokens)
        if line_spans:
            for token_idx, score in token_scores.items():
                pos = getattr(tokens[token_idx], "position", None)
                if not pos:
                    continue
                indices = line_spans.get(int(pos[0])) or []
                if not indices:
                    continue
                weight = float(score) / float(len(indices))
                for prompt_idx in indices:
                    vec[prompt_idx] += weight
            if vec.sum() > 0:
                return vec

        alignment = self._build_prompt_alignment(tokens, prompt_tokens)
        for token_idx, score in token_scores.items():
            for prompt_idx in alignment.get(token_idx, []):
                vec[prompt_idx] += score

        if vec.sum() > 0:
            return vec
        return self._old_map_scores_to_prompt(token_scores, tokens, prompt_tokens)

    def _fallback_chunk(self, bin_idx: int, n_bins: int) -> np.ndarray:
        total = len(self.context.prompt_tokens)
        if total == 0:
            return np.asarray([])
        chunk = max(1, total // n_bins)
        start = min(bin_idx * chunk, total - 1)
        vec = np.zeros(total, dtype=float)
        vec[start : start + chunk] = 1.0
        return vec

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        javalang_mod = self._try_import()
        if javalang_mod is None:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))
        _, tokens, tree = self._prepare_parse_artifacts(javalang_mod)
        if not tokens or tree is None:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        focus_node = self._select_target_method(tree, javalang_mod) or tree
        scores = self._collect_scores(focus_node, tokens, javalang_mod)
        vec = self._map_scores_to_prompt(scores, tokens, self.context.prompt_tokens)
        if vec.sum() == 0:
            vec = self._fallback_chunk(bin_idx, n_bins)
        return self._normalize(vec)

    def _node_weight(self, ntype: str) -> float:
        if ntype in self.node_names["tier1"]:
            return self.tier_weights["tier1"]
        if ntype in self.node_names["tier2"]:
            return self.tier_weights["tier2"]
        if ntype in self.node_names["tier3"]:
            return self.tier_weights["tier3"]
        # small default to avoid over-amplifying deep nesting of unlisted nodes
        return 0.0


class CFGPrior(ASTPrior):
    """
    Control-flow prior: emphasize control structures and their condition expressions.
    """

    control_weights = {
        "IfStatement": 3.0,
        "WhileStatement": 3.0,
        "ForStatement": 3.0,
        "DoStatement": 3.0,
        "DoWhileStatement": 3.0,
        "SwitchStatement": 3.0,
        "TryStatement": 2.0,
        "CatchClause": 2.0,
        "ReturnStatement": 2.0,
        "BreakStatement": 2.0,
        "ContinueStatement": 2.0,
        "ThrowStatement": 2.0,
        "AssertStatement": 2.0,
    }

    control_attrs = {
        "IfStatement": ["condition"],
        "WhileStatement": ["condition"],
        "DoStatement": ["condition"],
        "DoWhileStatement": ["condition"],
        "ForStatement": ["condition", "init", "update"],
        "SwitchStatement": ["expression"],
        "ReturnStatement": ["expression"],
        "ThrowStatement": ["expression"],
        "AssertStatement": ["condition"],
        "TryStatement": [],
        "CatchClause": ["parameter"],
    }

    def _collect_scores(self, tree, tokens, javalang_mod) -> Dict[int, float]:
        pos_map = self._position_index(tokens)
        scores: Dict[int, float] = {}

        def add_subtree(node, weight: float) -> None:
            if node is None:
                return
            self._add_pos(node, weight, pos_map, scores)
            for child in getattr(node, "children", ()):
                if child is None:
                    continue
                if isinstance(child, (list, tuple)):
                    for c in child:
                        add_subtree(c, weight)
                else:
                    add_subtree(child, weight)

        def pick_branch(node):
            ntype = type(node).__name__
            if ntype == "IfStatement":
                return getattr(node, "then_statement", None) or getattr(node, "else_statement", None)
            if ntype in ("WhileStatement", "ForStatement", "DoStatement", "DoWhileStatement"):
                return getattr(node, "body", None)
            if ntype == "SwitchStatement":
                cases = getattr(node, "cases", []) or []
                if cases:
                    first_case = cases[0]
                    return getattr(first_case, "statements", None)
                return None
            if ntype == "TryStatement":
                return getattr(node, "block", None) or getattr(node, "finally_block", None)
            if ntype == "CatchClause":
                return getattr(node, "block", None)
            return None

        def visit(node, depth: int) -> None:
            if node is None:
                return
            ntype = type(node).__name__
            base_weight = self.control_weights.get(ntype, 0.0)
            if base_weight > 0:
                # depth-weighting: deeper control-flow nodes get down-weighted
                weight = base_weight * (0.85 ** depth)
                self._add_pos(node, weight, pos_map, scores)
                for attr in self.control_attrs.get(ntype, []):
                    add_subtree(getattr(node, attr, None), weight)
                # branch-local focus: traverse only one branch for nested control flow
                branch = pick_branch(node)
                if branch is not None:
                    if isinstance(branch, (list, tuple)):
                        for b in branch:
                            visit(b, depth + 1)
                    else:
                        visit(branch, depth + 1)
                return

            for child in getattr(node, "children", ()):
                if child is None:
                    continue
                if isinstance(child, (list, tuple)):
                    for c in child:
                        visit(c, depth)
                else:
                    visit(child, depth)

        visit(tree, 0)
        return scores


class SlicingPrior(ASTPrior):
    """
    Intra-procedural slicing/chop prior focused on the algorithm method (non-main).
    """

    type_weights = {
        "predicate": 1.0,
        "return_expr": 1.0,
        "param": 0.9,
        "MethodInvocation": 0.7,
        "SuperMethodInvocation": 0.7,
        "Assignment": 0.6,
        "LocalVariableDeclaration": 0.6,
        "StatementExpression": 0.6,
        "ReturnStatement": 0.7,
        "Literal": 0.3,
    }
    slice_baseline = 1.0
    slice_boost = 1.0
    slice_gamma = 0.7

    def _is_meaningful_token(self, tok) -> bool:
        val = str(getattr(tok, "value", "")).strip()
        if not val:
            return False
        if re.fullmatch(r"[{}\[\]();,]", val):
            return False
        if re.search(r"[A-Za-z0-9_]", val):
            return True
        if val in {"==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "&&", "||", "!", "=", "+=", "-=", "*=", "/="}:
            return True
        return False

    def _pos_leq(self, a: tuple, b: tuple) -> bool:
        return (a[0], a[1]) <= (b[0], b[1])

    def _max_position(self, node) -> Optional[tuple]:
        if node is None:
            return None
        pos = getattr(node, "position", None)
        max_pos = pos
        for child in getattr(node, "children", ()):
            if child is None:
                continue
            if isinstance(child, (list, tuple)):
                for c in child:
                    cpos = self._max_position(c)
                    if cpos and (max_pos is None or self._pos_leq(max_pos, cpos)):
                        max_pos = cpos
            else:
                cpos = self._max_position(child)
                if cpos and (max_pos is None or self._pos_leq(max_pos, cpos)):
                    max_pos = cpos
        return max_pos

    def _min_position(self, node) -> Optional[tuple]:
        if node is None:
            return None
        pos = getattr(node, "position", None)
        min_pos = pos
        for child in getattr(node, "children", ()):
            if child is None:
                continue
            if isinstance(child, (list, tuple)):
                for c in child:
                    cpos = self._min_position(c)
                    if cpos and (min_pos is None or self._pos_leq(cpos, min_pos)):
                        min_pos = cpos
            else:
                cpos = self._min_position(child)
                if cpos and (min_pos is None or self._pos_leq(cpos, min_pos)):
                    min_pos = cpos
        return min_pos

    def _node_span(self, node) -> Optional[Tuple[tuple, tuple]]:
        start = getattr(node, "position", None)
        end = self._max_position(node)
        if start is None:
            start = self._min_position(node)
        if end is None:
            end = start
        if start is None:
            return None
        return (start, end)

    def _token_indices_in_span(self, span: Tuple[tuple, tuple], tokens) -> List[int]:
        start, end = span
        indices = []
        for idx, tok in enumerate(tokens):
            pos = getattr(tok, "position", None)
            if not pos:
                continue
            if self._pos_leq(start, pos) and self._pos_leq(pos, end):
                if self._is_meaningful_token(tok):
                    indices.append(idx)
        return indices

    def _select_target_method(self, tree, javalang_mod):
        methods = [node for _, node in tree.filter(javalang_mod.tree.MethodDeclaration)]
        if not methods:
            return None
        main = next((m for m in methods if m.name == "main"), None)
        non_main = [m for m in methods if m.name != "main"]
        if not non_main:
            return None
        if main:
            called = set()
            for _, inv in main.filter(javalang_mod.tree.MethodInvocation):
                if getattr(inv, "member", None):
                    called.add(inv.member)
            called_candidates = [m for m in non_main if m.name in called]
            if called_candidates:
                return max(called_candidates, key=lambda m: len(getattr(m, "body", []) or []))
        def nonvoid_params(m):
            ret = getattr(m, "return_type", None)
            params = getattr(m, "parameters", []) or []
            return ret is not None and len(params) > 0
        candidates = [m for m in non_main if nonvoid_params(m)]
        if candidates:
            return max(candidates, key=lambda m: len(getattr(m, "body", []) or []))
        return max(non_main, key=lambda m: len(getattr(m, "body", []) or []))

    def _collect_uses(self, node, javalang_mod) -> set[str]:
        names: set[str] = set()
        if node is None:
            return names
        if isinstance(node, javalang_mod.tree.MemberReference):
            if getattr(node, "member", None):
                names.add(node.member)
            qual = getattr(node, "qualifier", None)
            if isinstance(qual, str) and qual.isidentifier():
                names.add(qual)
            return names
        if isinstance(node, javalang_mod.tree.MethodInvocation):
            qual = getattr(node, "qualifier", None)
            if isinstance(qual, str) and qual.isidentifier():
                names.add(qual)
            for arg in getattr(node, "arguments", []) or []:
                names |= self._collect_uses(arg, javalang_mod)
            return names
        if isinstance(node, javalang_mod.tree.SuperMethodInvocation):
            for arg in getattr(node, "arguments", []) or []:
                names |= self._collect_uses(arg, javalang_mod)
            return names
        if isinstance(node, javalang_mod.tree.Literal):
            return names
        for child in getattr(node, "children", ()):
            if child is None:
                continue
            if isinstance(child, (list, tuple)):
                for c in child:
                    names |= self._collect_uses(c, javalang_mod)
            else:
                names |= self._collect_uses(child, javalang_mod)
        return names

    def _def_name(self, node, javalang_mod) -> Optional[str]:
        if node is None:
            return None
        if isinstance(node, javalang_mod.tree.MemberReference):
            return getattr(node, "member", None)
        return None

    def _statement_defs_uses(self, stmt, javalang_mod) -> Tuple[set[str], set[str]]:
        defs: set[str] = set()
        uses: set[str] = set()
        if stmt is None:
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.LocalVariableDeclaration):
            for decl in getattr(stmt, "declarators", []) or []:
                if getattr(decl, "name", None):
                    defs.add(decl.name)
                uses |= self._collect_uses(getattr(decl, "initializer", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.StatementExpression):
            expr = getattr(stmt, "expression", None)
            return self._statement_defs_uses(expr, javalang_mod)
        if isinstance(stmt, javalang_mod.tree.Assignment):
            left = getattr(stmt, "expressionl", None) or getattr(stmt, "expression", None)
            right = getattr(stmt, "value", None)
            def_name = self._def_name(left, javalang_mod)
            if def_name:
                defs.add(def_name)
            uses |= self._collect_uses(right, javalang_mod)
            if getattr(stmt, "type", "=") not in ("=", None):
                uses |= self._collect_uses(left, javalang_mod)
            return defs, uses
        unary_cls = getattr(javalang_mod.tree, "UnaryOperation", None)
        if unary_cls is not None and isinstance(stmt, unary_cls):
            op = getattr(stmt, "operator", "")
            expr = getattr(stmt, "expression", None)
            if op in ("++", "--"):
                def_name = self._def_name(expr, javalang_mod)
                if def_name:
                    defs.add(def_name)
                    uses.add(def_name)
            else:
                uses |= self._collect_uses(expr, javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.MemberReference):
            post_ops = getattr(stmt, "postfix_operators", []) or []
            pre_ops = getattr(stmt, "prefix_operators", []) or []
            if any(op in ("++", "--") for op in post_ops + pre_ops):
                name = getattr(stmt, "member", None)
                if name:
                    defs.add(name)
                    uses.add(name)
                return defs, uses
        if isinstance(stmt, javalang_mod.tree.ReturnStatement):
            uses |= self._collect_uses(getattr(stmt, "expression", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.IfStatement):
            uses |= self._collect_uses(getattr(stmt, "condition", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.WhileStatement):
            uses |= self._collect_uses(getattr(stmt, "condition", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.DoStatement):
            uses |= self._collect_uses(getattr(stmt, "condition", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.ForStatement):
            control = getattr(stmt, "control", None)
            if isinstance(control, javalang_mod.tree.ForControl):
                for init in getattr(control, "init", []) or []:
                    d, u = self._statement_defs_uses(init, javalang_mod)
                    defs |= d
                    uses |= u
                uses |= self._collect_uses(getattr(control, "condition", None), javalang_mod)
                for upd in getattr(control, "update", []) or []:
                    d, u = self._statement_defs_uses(upd, javalang_mod)
                    defs |= d
                    uses |= u
            if isinstance(control, javalang_mod.tree.EnhancedForControl):
                var = getattr(control, "var", None)
                if getattr(var, "name", None):
                    defs.add(var.name)
                uses |= self._collect_uses(getattr(control, "iterable", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.SwitchStatement):
            uses |= self._collect_uses(getattr(stmt, "expression", None), javalang_mod)
            return defs, uses
        if isinstance(stmt, javalang_mod.tree.ThrowStatement):
            uses |= self._collect_uses(getattr(stmt, "expression", None), javalang_mod)
            return defs, uses
        # fallback: collect uses within the statement
        uses |= self._collect_uses(stmt, javalang_mod)
        return defs, uses

    def _block_statements(self, block) -> List[Any]:
        if block is None:
            return []
        if isinstance(block, list):
            return block
        if hasattr(block, "statements"):
            return list(getattr(block, "statements") or [])
        if hasattr(block, "body"):
            return self._block_statements(getattr(block, "body"))
        # treat a single statement node as a 1-item block
        return [block]

    def _build_nodes_and_cfg(self, method, tokens, javalang_mod, id_base: int = 0):
        stmt_id_by_node: Dict[int, int] = {}
        pred_id_by_stmt: Dict[int, int] = {}
        ret_expr_id_by_stmt: Dict[int, int] = {}
        nodes: Dict[int, _SliceNode] = {}
        next_id = id_base

        method_span = self._node_span(method)
        method_token_indices = set(self._token_indices_in_span(method_span, tokens)) if method_span else set()

        def alloc_id() -> int:
            nonlocal next_id
            nid = next_id
            next_id += 1
            return nid

        def stmt_tokens(node) -> List[int]:
            span = self._node_span(node)
            if not span:
                return []
            indices = self._token_indices_in_span(span, tokens)
            if method_token_indices:
                indices = [i for i in indices if i in method_token_indices]
            return indices

        def register_stmt(node, depth: int) -> int:
            key = id(node)
            if key in stmt_id_by_node:
                return stmt_id_by_node[key]
            stmt_id = alloc_id()
            stmt_id_by_node[key] = stmt_id
            defs, uses = self._statement_defs_uses(node, javalang_mod)
            nodes[stmt_id] = _SliceNode(
                id=stmt_id,
                kind="stmt",
                ast_node=node,
                token_indices=stmt_tokens(node),
                defs=defs,
                uses=uses,
                depth=depth,
            )
            return stmt_id

        def register_predicate(stmt_id: int, expr_node, depth: int) -> int:
            pred_id = alloc_id()
            pred_id_by_stmt[stmt_id] = pred_id
            token_indices = stmt_tokens(expr_node)
            stmt_node = nodes.get(stmt_id).ast_node if stmt_id in nodes else None
            if stmt_node is not None:
                span = self._node_span(stmt_node)
                if span:
                    start, end = span
                    keyword_candidates: List[Tuple[int, int]] = []
                    for idx, tok in enumerate(tokens):
                        if method_token_indices and idx not in method_token_indices:
                            continue
                        pos = getattr(tok, "position", None)
                        if not pos:
                            continue
                        if not (self._pos_leq(start, pos) and self._pos_leq(pos, end)):
                            continue
                        val = str(getattr(tok, "value", ""))
                        if val in {"if", "for", "while", "do", "switch"}:
                            keyword_candidates.append((pos[1], idx))
                    if keyword_candidates:
                        _, kw_idx = min(keyword_candidates)
                        token_indices.append(kw_idx)
            token_indices = sorted(set(token_indices))
            nodes[pred_id] = _SliceNode(
                id=pred_id,
                kind="predicate",
                ast_node=expr_node,
                token_indices=token_indices,
                defs=set(),
                uses=self._collect_uses(expr_node, javalang_mod),
                depth=depth,
                stmt_id=stmt_id,
            )
            return pred_id

        def register_return_expr(stmt_id: int, expr_node, depth: int) -> int:
            ret_id = alloc_id()
            ret_expr_id_by_stmt[stmt_id] = ret_id
            nodes[ret_id] = _SliceNode(
                id=ret_id,
                kind="return_expr",
                ast_node=expr_node,
                token_indices=stmt_tokens(expr_node),
                defs=set(),
                uses=self._collect_uses(expr_node, javalang_mod),
                depth=depth,
                stmt_id=stmt_id,
            )
            return ret_id

        def register_param(param_node, depth: int) -> int:
            param_id = alloc_id()
            pname = getattr(param_node, "name", None)
            token_indices = stmt_tokens(param_node)
            if pname:
                pos = getattr(param_node, "position", None)
                candidates: List[Tuple[int, int]] = []
                for idx, tok in enumerate(tokens):
                    if method_token_indices and idx not in method_token_indices:
                        continue
                    tpos = getattr(tok, "position", None)
                    if not tpos:
                        continue
                    if pos and tpos[0] != pos[0]:
                        continue
                    if pos and tpos[1] < pos[1]:
                        continue
                    if str(getattr(tok, "value", "")) == pname:
                        candidates.append((tpos[1], idx))
                if candidates:
                    _, name_idx = min(candidates)
                    token_indices.append(name_idx)
            token_indices = sorted(set(token_indices))
            nodes[param_id] = _SliceNode(
                id=param_id,
                kind="param",
                ast_node=param_node,
                token_indices=token_indices,
                defs={pname} if pname else set(),
                uses=set(),
                depth=depth,
            )
            return param_id

        cfg_edges: List[Tuple[int, int]] = []

        def connect(prev_exits: List[int], next_entry: int) -> None:
            for e in prev_exits:
                cfg_edges.append((e, next_entry))

        def build_block(statements: List[Any], depth: int) -> Tuple[List[int], List[int]]:
            entries: List[int] = []
            prev_exits: List[int] = []
            first = True
            for stmt in statements:
                stmt_entry, stmt_exits = build_stmt(stmt, depth)
                if first:
                    entries.extend(stmt_entry)
                    first = False
                else:
                    connect(prev_exits, stmt_entry[0])
                prev_exits = stmt_exits
                if not prev_exits:
                    # return or terminal; subsequent statements are unreachable
                    prev_exits = []
            return entries, prev_exits

        def build_stmt(stmt, depth: int) -> Tuple[List[int], List[int]]:
            stmt_id = register_stmt(stmt, depth)
            entry = [stmt_id]
            if isinstance(stmt, javalang_mod.tree.ReturnStatement):
                expr = getattr(stmt, "expression", None)
                if expr is not None:
                    register_return_expr(stmt_id, expr, depth)
                return entry, []
            if isinstance(stmt, javalang_mod.tree.IfStatement):
                cond = getattr(stmt, "condition", None)
                if cond is not None:
                    register_predicate(stmt_id, cond, depth)
                then_block = self._block_statements(getattr(stmt, "then_statement", None))
                else_block = self._block_statements(getattr(stmt, "else_statement", None))
                then_entries, then_exits = build_block(then_block, depth + 1) if then_block else ([], [stmt_id])
                else_entries, else_exits = build_block(else_block, depth + 1) if else_block else ([], [stmt_id])
                for te in then_entries:
                    cfg_edges.append((stmt_id, te))
                for ee in else_entries:
                    cfg_edges.append((stmt_id, ee))
                exits = then_exits + else_exits
                return entry, exits
            if isinstance(stmt, (javalang_mod.tree.WhileStatement, javalang_mod.tree.ForStatement, javalang_mod.tree.DoStatement)):
                cond = getattr(stmt, "condition", None)
                if cond is not None:
                    register_predicate(stmt_id, cond, depth)
                body = self._block_statements(getattr(stmt, "body", None))
                body_entries, body_exits = build_block(body, depth + 1) if body else ([], [])
                for be in body_entries:
                    cfg_edges.append((stmt_id, be))
                for bx in body_exits:
                    cfg_edges.append((bx, stmt_id))
                return entry, [stmt_id]
            if isinstance(stmt, javalang_mod.tree.SwitchStatement):
                cond = getattr(stmt, "expression", None)
                if cond is not None:
                    register_predicate(stmt_id, cond, depth)
                case_exits: List[int] = []
                cases = getattr(stmt, "cases", []) or []
                for case in cases:
                    case_block = self._block_statements(getattr(case, "statements", None))
                    ce, cx = build_block(case_block, depth + 1) if case_block else ([], [stmt_id])
                    for c_entry in ce:
                        cfg_edges.append((stmt_id, c_entry))
                    case_exits.extend(cx)
                return entry, case_exits or [stmt_id]
            if isinstance(stmt, javalang_mod.tree.TryStatement):
                block = self._block_statements(getattr(stmt, "block", None))
                catches = getattr(stmt, "catches", []) or []
                finally_block = self._block_statements(getattr(stmt, "finally_block", None))
                block_entries, block_exits = build_block(block, depth + 1) if block else ([], [stmt_id])
                for be in block_entries:
                    cfg_edges.append((stmt_id, be))
                catch_exits: List[int] = []
                for catch in catches:
                    catch_block = self._block_statements(getattr(catch, "block", None))
                    ce, cx = build_block(catch_block, depth + 1) if catch_block else ([], [stmt_id])
                    for c_entry in ce:
                        cfg_edges.append((stmt_id, c_entry))
                    catch_exits.extend(cx)
                fin_entries, fin_exits = build_block(finally_block, depth + 1) if finally_block else ([], [])
                for fe in fin_entries:
                    cfg_edges.append((stmt_id, fe))
                exits = (block_exits + catch_exits + fin_exits) or [stmt_id]
                return entry, exits
            return entry, [stmt_id]

        method_body = self._block_statements(getattr(method, "body", None))
        entries, exits = build_block(method_body, 0)

        # parameter pseudo-nodes
        param_ids = []
        for param in getattr(method, "parameters", []) or []:
            param_ids.append(register_param(param, 0))

        return (
            nodes,
            cfg_edges,
            entries,
            exits,
            param_ids,
            pred_id_by_stmt,
            ret_expr_id_by_stmt,
            stmt_id_by_node,
            next_id,
        )

    def _build_control_edges(self, nodes: Dict[int, _SliceNode], method, javalang_mod, stmt_id_by_node, pred_id_by_stmt, ret_expr_id_by_stmt) -> List[Tuple[int, int]]:
        control_edges: List[Tuple[int, int]] = []

        def collect_stmt_ids(block) -> List[int]:
            ids: List[int] = []
            for stmt in self._block_statements(block):
                sid = stmt_id_by_node.get(id(stmt))
                if sid is not None:
                    ids.append(sid)
                    if sid in ret_expr_id_by_stmt:
                        ids.append(ret_expr_id_by_stmt[sid])
                # include nested statements
                ids.extend(collect_stmt_ids(getattr(stmt, "then_statement", None)))
                ids.extend(collect_stmt_ids(getattr(stmt, "else_statement", None)))
                ids.extend(collect_stmt_ids(getattr(stmt, "body", None)))
            return ids

        for _, node in method.filter(javalang_mod.tree.IfStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for tid in collect_stmt_ids(getattr(node, "then_statement", None)):
                control_edges.append((pid, tid))
            for tid in collect_stmt_ids(getattr(node, "else_statement", None)):
                control_edges.append((pid, tid))
        for _, node in method.filter(javalang_mod.tree.WhileStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for tid in collect_stmt_ids(getattr(node, "body", None)):
                control_edges.append((pid, tid))
        for _, node in method.filter(javalang_mod.tree.ForStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for tid in collect_stmt_ids(getattr(node, "body", None)):
                control_edges.append((pid, tid))
        for _, node in method.filter(javalang_mod.tree.DoStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for tid in collect_stmt_ids(getattr(node, "body", None)):
                control_edges.append((pid, tid))
        for _, node in method.filter(javalang_mod.tree.SwitchStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for case in getattr(node, "cases", []) or []:
                for tid in collect_stmt_ids(getattr(case, "statements", None)):
                    control_edges.append((pid, tid))
        for _, node in method.filter(javalang_mod.tree.TryStatement):
            sid = stmt_id_by_node.get(id(node))
            pid = pred_id_by_stmt.get(sid)
            if pid is None:
                continue
            for tid in collect_stmt_ids(getattr(node, "block", None)):
                control_edges.append((pid, tid))
            for catch in getattr(node, "catches", []) or []:
                for tid in collect_stmt_ids(getattr(catch, "block", None)):
                    control_edges.append((pid, tid))
        return control_edges

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        javalang_mod = self._try_import()
        if javalang_mod is None:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))
        _, tokens, tree = self._prepare_parse_artifacts(javalang_mod)
        if not tokens or tree is None:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        methods = [node for _, node in tree.filter(javalang_mod.tree.MethodDeclaration)]
        if not methods:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        class_name = None
        for _, cls in tree.filter(javalang_mod.tree.ClassDeclaration):
            class_name = getattr(cls, "name", None)
            if class_name:
                break

        target_method = self._select_target_method(tree, javalang_mod)
        if target_method is None:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        main_method = next((m for m in methods if getattr(m, "name", None) == "main"), None)

        method_by_name = {getattr(m, "name", None): m for m in methods if getattr(m, "name", None)}

        def is_local_invocation(inv) -> bool:
            member = getattr(inv, "member", None)
            if not member or member not in method_by_name:
                return False
            qual = getattr(inv, "qualifier", None)
            if qual is None or qual in ("this", class_name):
                return True
            return False

        roots = [target_method]
        if main_method is not None and main_method is not target_method:
            roots.append(main_method)

        included = set(roots)
        stack = list(roots)
        while stack:
            cur = stack.pop()
            for _, inv in cur.filter(javalang_mod.tree.MethodInvocation):
                if not is_local_invocation(inv):
                    continue
                callee = method_by_name.get(inv.member)
                if callee and callee not in included:
                    included.add(callee)
                    stack.append(callee)

        nodes: Dict[int, _SliceNode] = {}
        cfg_edges: List[Tuple[int, int]] = []
        control_edges: List[Tuple[int, int]] = []
        method_infos: Dict[str, Dict[str, Any]] = {}
        id_cursor = 0
        all_method_token_indices: List[int] = []

        for method in included:
            (
                method_nodes,
                method_cfg,
                entries,
                exits,
                param_ids,
                pred_map,
                ret_expr_map,
                stmt_id_by_node,
                id_cursor,
            ) = self._build_nodes_and_cfg(method, tokens, javalang_mod, id_base=id_cursor)
            nodes.update(method_nodes)
            cfg_edges.extend(method_cfg)
            control_edges.extend(
                self._build_control_edges(method_nodes, method, javalang_mod, stmt_id_by_node, pred_map, ret_expr_map)
            )
            method_name = getattr(method, "name", None) or f"anon_{id(method)}"
            method_infos[method_name] = {
                "method": method,
                "entries": entries,
                "exits": exits,
                "param_ids": param_ids,
                "pred_map": pred_map,
                "ret_expr_map": ret_expr_map,
                "ret_expr_ids": list(ret_expr_map.values()),
                "stmt_id_by_node": stmt_id_by_node,
            }
            span = self._node_span(method)
            if span:
                all_method_token_indices.extend(self._token_indices_in_span(span, tokens))

        if not nodes:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        # build reaching defs + PDG per method (intra-procedural)
        pdg_edges: List[Tuple[int, int]] = []
        for info in method_infos.values():
            stmt_ids = list(info["stmt_id_by_node"].values())
            if not stmt_ids:
                continue
            preds: Dict[int, List[int]] = {sid: [] for sid in stmt_ids}
            for src, dst in cfg_edges:
                if dst in preds:
                    preds[dst].append(src)

            def_entries = {(pname, pid) for pid in info["param_ids"] for pname in nodes[pid].defs}
            in_defs: Dict[int, set] = {sid: set() for sid in stmt_ids}
            out_defs: Dict[int, set] = {sid: set() for sid in stmt_ids}
            entry_set = set(info["entries"])
            changed = True
            while changed:
                changed = False
                for sid in stmt_ids:
                    incoming = set()
                    for p in preds.get(sid, []):
                        incoming |= out_defs.get(p, set())
                    if sid in entry_set:
                        incoming |= def_entries
                    defs = {(d, sid) for d in nodes[sid].defs}
                    kill = {d for d in incoming if d[0] in nodes[sid].defs}
                    new_in = incoming
                    new_out = defs | (incoming - kill)
                    if new_in != in_defs[sid] or new_out != out_defs[sid]:
                        in_defs[sid] = new_in
                        out_defs[sid] = new_out
                        changed = True

            # data edges to statements
            for sid in stmt_ids:
                for use in nodes[sid].uses:
                    for var, def_id in in_defs.get(sid, set()):
                        if var == use:
                            pdg_edges.append((def_id, sid))
            # data edges to predicate/return expr nodes
            for node in nodes.values():
                if node.kind in ("predicate", "return_expr") and node.stmt_id in stmt_ids:
                    anchor = node.stmt_id
                    for use in node.uses:
                        for var, def_id in in_defs.get(anchor, set()):
                            if var == use:
                                pdg_edges.append((def_id, node.id))
            # return expr -> return stmt
            for stmt_id, expr_id in info["ret_expr_map"].items():
                pdg_edges.append((expr_id, stmt_id))

        pdg_edges.extend(control_edges)

        # connect call sites to local callees (lightweight inter-procedural links)
        for method_name, info in method_infos.items():
            method = info["method"]
            for stmt_id in info["stmt_id_by_node"].values():
                stmt_node = None
                for obj in nodes.values():
                    if obj.id == stmt_id:
                        stmt_node = obj.ast_node
                        break
                if stmt_node is None:
                    continue
                for _, inv in stmt_node.filter(javalang_mod.tree.MethodInvocation):
                    if not is_local_invocation(inv):
                        continue
                    callee = method_by_name.get(inv.member)
                    if callee is None:
                        continue
                    callee_name = getattr(callee, "name", None)
                    if callee_name not in method_infos:
                        continue
                    callee_info = method_infos[callee_name]
                    for pid in callee_info["param_ids"]:
                        pdg_edges.append((stmt_id, pid))
                    for rid in callee_info["ret_expr_ids"]:
                        pdg_edges.append((rid, stmt_id))
                    for entry_id in callee_info["entries"]:
                        pdg_edges.append((stmt_id, entry_id))

        # sources and sinks
        source_ids = []
        for root in roots:
            rname = getattr(root, "name", None)
            if rname in method_infos:
                source_ids.extend(method_infos[rname]["param_ids"])
        if not source_ids:
            source_ids = list(method_infos.get(getattr(target_method, "name", ""), {}).get("param_ids", []))
        sink_ids = []
        target_name = getattr(target_method, "name", None)
        if target_name in method_infos:
            target_stmt_ids = set(method_infos[target_name]["stmt_id_by_node"].values())
            for node in nodes.values():
                if node.id in target_stmt_ids and isinstance(node.ast_node, javalang_mod.tree.ReturnStatement):
                    sink_ids.append(node.id)
        if not sink_ids:
            sink_ids = [
                node.id
                for node in nodes.values()
                if node.kind == "stmt" and isinstance(node.ast_node, javalang_mod.tree.ReturnStatement)
            ]

        # reachability
        forward_adj: Dict[int, List[int]] = {}
        reverse_adj: Dict[int, List[int]] = {}
        for src, dst in pdg_edges:
            forward_adj.setdefault(src, []).append(dst)
            reverse_adj.setdefault(dst, []).append(src)

        def reachable(start_ids: List[int], adj: Dict[int, List[int]]) -> Dict[int, set]:
            result = {}
            for sid in start_ids:
                seen = set([sid])
                stack = [sid]
                while stack:
                    cur = stack.pop()
                    for nxt in adj.get(cur, []):
                        if nxt not in seen:
                            seen.add(nxt)
                            stack.append(nxt)
                result[sid] = seen
            return result

        forward_sets = reachable(source_ids, forward_adj)
        backward_sets = reachable(sink_ids, reverse_adj)

        reverse_control: Dict[int, List[int]] = {}
        for src, dst in control_edges:
            if nodes.get(src) and nodes[src].kind == "predicate":
                reverse_control.setdefault(dst, []).append(src)

        sharedness: Dict[int, int] = {}
        for s in source_ids:
            fset = forward_sets.get(s, set())
            for t in sink_ids:
                bset = backward_sets.get(t, set())
                chop = set(fset & bset)
                if chop:
                    stack = list(chop)
                    while stack:
                        cur = stack.pop()
                        for pred in reverse_control.get(cur, []):
                            if pred not in chop:
                                chop.add(pred)
                                stack.append(pred)
                for n in chop:
                    sharedness[n] = sharedness.get(n, 0) + 1

        if not sharedness:
            return self._normalize(self._fallback_chunk(bin_idx, n_bins))

        # distance to sink (shortest path)
        dist = {nid: math.inf for nid in nodes.keys()}
        queue = list(sink_ids)
        for s in sink_ids:
            dist[s] = 0
        while queue:
            cur = queue.pop(0)
            for prev in reverse_adj.get(cur, []):
                if dist[prev] > dist[cur] + 1:
                    dist[prev] = dist[cur] + 1
                    queue.append(prev)

        max_shared = max(sharedness.values()) if sharedness else 1

        token_scores: Dict[int, float] = {}
        for nid, node in nodes.items():
            if nid not in sharedness:
                continue
            if not node.token_indices:
                continue
            w_type = self.type_weights.get(node.kind, self.type_weights.get(type(node.ast_node).__name__, 0.5))
            w_shared = sharedness[nid] / float(max_shared)
            dval = dist.get(nid, math.inf)
            if dval == math.inf:
                w_dist = 0.0
            else:
                w_dist = 1.0 / (1.0 + dval)
            w_depth = 1.0 / (1.0 + max(node.depth, 0))
            weight = w_type * w_shared * w_dist * w_depth
            for idx in node.token_indices:
                token_scores[idx] = max(token_scores.get(idx, 0.0), weight)

        method_tokens = list(dict.fromkeys(all_method_token_indices))
        baseline_scores = {idx: float(self.slice_baseline) for idx in method_tokens}

        slice_vec = self._map_scores_to_prompt(token_scores, tokens, self.context.prompt_tokens)
        if self.slice_gamma and self.slice_gamma != 1.0:
            slice_vec = np.power(np.clip(slice_vec, 0.0, None), self.slice_gamma)
        baseline_vec = self._map_scores_to_prompt(baseline_scores, tokens, self.context.prompt_tokens)

        combined = baseline_vec + (float(self.slice_boost) * slice_vec)
        if combined.sum() == 0:
            combined = self._fallback_chunk(bin_idx, n_bins)
        return self._normalize(combined)


class SlicingHybridPrior(SlicingPrior):
    """
    Hybrid slicing prior:
    - algorithm signal from SlicingPrior
    - case-block signal from prompt markers (### CASES_BEGIN ... ### CASES_END)
    """

    alg_weight = 0.7
    case_weight = 0.3
    baseline_weight = 1.0

    def __init__(self, context: PriorContext) -> None:
        super().__init__(context)
        self._case_vectors, self._case_ids = self._build_case_vectors()

    @staticmethod
    def _norm_token(token: str) -> str:
        return str(token).replace("▁", "").replace("Ġ", "").strip().lower()

    def _extract_case_specs(self) -> List[tuple[str, str]]:
        prompt_text = str(getattr(self.context, "prompt_text", "") or "")
        if not prompt_text:
            return []
        start = prompt_text.find("### CASES_BEGIN")
        end = prompt_text.find("### CASES_END")
        if start < 0 or end < 0 or end <= start:
            return []
        block = prompt_text[start:end]
        specs: List[tuple[str, str]] = []
        for line in block.splitlines():
            m = re.match(r"\s*(c\d{3})\s*:\s*(.+?)\s*$", line, flags=re.IGNORECASE)
            if not m:
                continue
            specs.append((m.group(1).lower(), m.group(2).strip()))
        return specs

    def _expr_terms(self, expr: str) -> List[str]:
        terms: List[str] = []
        for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr):
            tl = t.lower()
            if tl in {
                "true",
                "false",
                "null",
                "new",
                "return",
                "if",
                "else",
                "for",
                "while",
                "assert",
                "math",
            }:
                continue
            terms.append(tl)
        for n in re.findall(r"-?\d+(?:\.\d+)?(?:e[+-]?\d+)?", expr, flags=re.IGNORECASE):
            terms.append(n.lower())
        for op in re.findall(r"<=|>=|==|!=|&&|\|\||<|>|\+|-|\*|/|%|!", expr):
            terms.append(op)
        # Keep deterministic order and uniqueness.
        uniq = list(dict.fromkeys(terms))
        return uniq

    def _build_case_vectors(self) -> tuple[List[np.ndarray], List[str]]:
        toks = list(self.context.prompt_tokens)
        total = len(toks)
        if total == 0:
            return [], []

        specs = self._extract_case_specs()
        if not specs:
            return [], []

        norm_tokens = [self._norm_token(t) for t in toks]
        marker_start: Optional[int] = None
        marker_end: Optional[int] = None
        for i, tok in enumerate(norm_tokens):
            if marker_start is None and "cases_begin" in tok:
                marker_start = i
            if "cases_end" in tok:
                marker_end = i
        vectors: List[np.ndarray] = []
        case_ids: List[str] = []

        for case_id, expr in specs:
            terms = self._expr_terms(expr)
            vec = np.zeros(total, dtype=float)
            for i, raw_tok in enumerate(toks):
                tok = norm_tokens[i]
                if not tok:
                    continue
                score = 0.0
                if case_id in tok:
                    score += 4.0
                in_case_block = (
                    marker_start is not None
                    and marker_end is not None
                    and marker_start <= i <= marker_end
                )
                if in_case_block:
                    score += 0.2
                for term in terms:
                    if tok == term:
                        score += 2.5
                    elif len(tok) > 1 and len(term) > 1 and (tok in term or term in tok):
                        score += 1.2
                tok_plain = str(raw_tok).replace("▁", "").replace("Ġ", "")
                if tok_plain in {"(", ")", ":", "<", ">", "==", "!=", "<=", ">="}:
                    score += 0.2
                if score > 0.0:
                    vec[i] = score
            if vec.sum() > 0:
                vectors.append(self._normalize(vec))
                case_ids.append(case_id)
        return vectors, case_ids

    def _select_case_vector(self, bin_idx: int, n_bins: int, size: int) -> np.ndarray:
        if not self._case_vectors:
            return np.zeros(size, dtype=float)
        if n_bins <= 1:
            idx = 0
        else:
            # Spread bins across available cases deterministically.
            pos = float(bin_idx) / float(max(n_bins - 1, 1))
            idx = int(round(pos * float(len(self._case_vectors) - 1)))
        idx = max(0, min(idx, len(self._case_vectors) - 1))
        vec = self._case_vectors[idx]
        if vec.size != size:
            vec = np.resize(vec, size)
            s = float(vec.sum())
            if s > 0:
                vec = vec / s
        return vec

    def _case_block_vector(self) -> np.ndarray:
        toks = list(self.context.prompt_tokens)
        total = len(toks)
        if total == 0:
            return np.ones(1, dtype=float)

        start_idx: Optional[int] = None
        end_idx: Optional[int] = None
        for i, tok in enumerate(toks):
            low = str(tok).lower()
            if start_idx is None and "cases_begin" in low:
                start_idx = i
            if "cases_end" in low:
                end_idx = i

        vec = np.zeros(total, dtype=float)
        if start_idx is None or end_idx is None or end_idx < start_idx:
            return vec

        for i in range(start_idx, end_idx + 1):
            tok = str(toks[i])
            tok_plain = tok.replace("▁", "").replace("Ġ", "")
            weight = 1.0
            if re.search(r"[A-Za-z0-9_]", tok_plain):
                weight = 1.5
            if ":" in tok_plain or "(" in tok_plain or ")" in tok_plain:
                weight = 2.0
            vec[i] = weight
        return self._normalize(vec)

    def vector(self, bin_idx: int, n_bins: int) -> np.ndarray:
        alg_vec = super().vector(bin_idx, n_bins)
        if self._case_vectors:
            case_vec = self._select_case_vector(bin_idx, n_bins, alg_vec.size)
        else:
            case_vec = self._case_block_vector()
        if case_vec.size != alg_vec.size:
            case_vec = np.resize(case_vec, alg_vec.size)
        baseline = np.ones_like(alg_vec, dtype=float) * float(self.baseline_weight)
        combined = baseline + float(self.alg_weight) * alg_vec + float(self.case_weight) * case_vec
        if combined.sum() == 0:
            combined = self._fallback_chunk(bin_idx, n_bins)
        return self._normalize(combined)


PRIOR_REGISTRY = {
    "human": HumanPrior,
    "lex": LexPrior,
    "rand": RandPrior,
    "uniform": UniformPrior,
    "ast": ASTPrior,
    "cfg": CFGPrior,
    "slice": SlicingPrior,
    "slice_hybrid": SlicingHybridPrior,
}
