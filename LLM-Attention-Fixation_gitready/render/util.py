# attention_renderer.py

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from transformers import PreTrainedTokenizerBase


@dataclass
class RenderConfig:
    pool: str = "all_layers_mean"   # which pooled distribution to use
    html_bins: int = 256
    png_font_size: int = 14
    png_line_height: int = 18
    png_margin: int = 12


class AttentionRenderer:
    """
    Post-process and visualize attention over the *prompt* tokens onto the original source.
    Requires a **fast** tokenizer (offset mapping support).
    
    """
    # to do: add a vector comparsion method using attention dump
    def __init__(self, tokenizer: PreTrainedTokenizerBase, config: Optional[RenderConfig] = None):
        self.tokenizer = tokenizer
        if not getattr(self.tokenizer, "is_fast", False):
            raise RuntimeError("AttentionRenderer requires a *fast* tokenizer for offset mappings.")
        self.cfg = config or RenderConfig()

    # --------- public API ---------
    def map_attention_to_source(
        self,
        code_snippet: str,
        generation_result: Dict[str, Any],
        instruction: str = "Summarize what this Python function does. Be concise and accurate.",
        pool: Optional[str] = None,
        human_vocabulary: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Returns a dict with per-character and per-token (human) normalized scores in [0,1].
        """
        if generation_result.get("key_scope") != "prompt":
            raise ValueError("Set key_scope='prompt' during generation to align scores to the prompt.")

        pool_name = pool or self.cfg.pool

        # Rebuild the exact prompt used by llama.run_llama (default)
        prompt = f"{instruction}\n\n```java\n{code_snippet}\n```"

        input_ids, offsets = self._encode_prompt_offsets(prompt)

        pools = generation_result.get("global_pooled_attention_over_prompt") or {}
        if pool_name not in pools:
            raise KeyError(f"Pooled attention '{pool_name}' not found. Available: {list(pools.keys()) or 'none'}")

        scores: Sequence[float] = pools[pool_name]["scores"]
        if len(scores) != len(offsets):
            raise RuntimeError(
                f"Token/offset mismatch: scores={len(scores)} offsets={len(offsets)}. "
                "Ensure no special tokens and using a Fast tokenizer."
            )

        # Locate the code span inside the prompt
        code_prefix = f"{instruction}\n\n```java\n"
        code_start = len(code_prefix)
        code_end   = code_start + len(code_snippet)

        code_token_offsets, code_token_scores = self._collect_code_token_scores(
            offsets, scores, code_start, code_end
        )

        char_scores = self._project_token_scores_to_chars(
            text_len=len(code_snippet),
            token_offsets=code_token_offsets,
            token_scores=code_token_scores,
        )

        return self._assemble_attention_map(
            code_snippet=code_snippet,
            char_scores=char_scores,
            pool_name=pool_name,
            human_vocabulary=human_vocabulary,
        )

    def map_attention_from_prompt_scores(
        self,
        code_snippet: str,
        instruction: str,
        prompt_scores: Sequence[float],
        *,
        pool_name: str,
        human_vocabulary: Optional[Sequence[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        prompt = f"{instruction}\n\n```java\n{code_snippet}\n```"
        _, offsets = self._encode_prompt_offsets(prompt)

        code_prefix = f"{instruction}\n\n```java\n"
        code_start = len(code_prefix)
        code_end = code_start + len(code_snippet)

        code_token_offsets, code_token_scores = self._collect_code_token_scores(
            offsets, prompt_scores, code_start, code_end
        )

        char_scores = self._project_token_scores_to_chars(
            text_len=len(code_snippet),
            token_offsets=code_token_offsets,
            token_scores=code_token_scores,
        )

        return self._assemble_attention_map(
            code_snippet=code_snippet,
            char_scores=char_scores,
            pool_name=pool_name,
            human_vocabulary=human_vocabulary,
            annotations=metadata,
        )


    def save_text_dump(
        self,
        attn_map: Dict[str, Any],
        json_path: str,
        csv_path: Optional[str] = None,
    ) -> None:
        import csv, pathlib
        pathlib.Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(attn_map, f, ensure_ascii=False, indent=2)
        if csv_path:
            pathlib.Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["type", "index_or_span", "text", "score"])
                for c in attn_map["char_attention"]:
                    w.writerow(["char", c["index"], c["char"], f'{c["score"]:.6f}'])
                for t in attn_map["human_tokens"]:
                    span = f'{t["start"]}-{t["end"]}'
                    w.writerow(["token", span, t["text"], f'{t["score"]:.6f}'])

    def render_html(self, code_snippet: str, attn_map: Dict[str, Any], out_html_path: str) -> None:
        from html import escape
        import pathlib
        pathlib.Path(out_html_path).parent.mkdir(parents=True, exist_ok=True)

        def bucket(x: float, bins: int) -> int:
            v = max(0.0, min(1.0, float(x)))
            return int(round(v * (bins - 1)))

        chars = attn_map["char_attention"]
        html_parts: List[Tuple[int, str]] = []
        last_b = None
        buff: List[str] = []

        for c in chars:
            b = bucket(c["score"], self.cfg.html_bins)
            ch = c["char"]
            vis = ch.replace(" ", "·").replace("\t", "→").replace("\n", "⏎\n")
            if b != last_b and buff:
                html_parts.append((last_b, "".join(buff)))
                buff = []
            buff.append(escape(vis))
            last_b = b
        if buff:
            html_parts.append((last_b, "".join(buff)))

        spans = []
        for b, text in html_parts:
            alpha = b / float(self.cfg.html_bins - 1)
            light = 90 - int(alpha * 50)  # darker with higher attention
            spans.append(f'<span style="background: hsl(120, 80%, {light}%);">{text}</span>')

        html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Attention Heatmap ({attn_map["pool"]})</title>
<style>
body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
pre  {{ white-space: pre-wrap; line-height: 1.35; font-size: 13px; }}
.code {{ padding: 12px; border: 1px solid #ddd; border-radius: 8px; background: #fff; }}
.legend {{ margin: 10px 0; font-size: 12px; color: #555; }}
</style>
</head>
<body>
<div class="legend">Attention pool: <b>{attn_map["pool"]}</b> (0→light, 1→dark)</div>
<pre class="code">{''.join(spans)}</pre>
</body>
</html>"""
        with open(out_html_path, "w", encoding="utf-8") as f:
            f.write(html)

    def render_png(
        self,
        code_snippet: str,
        attn_map: Dict[str, Any],
        out_png_path: str,
        *,
        score_key: str = "char_attention",
    ) -> None:
        from PIL import Image, ImageDraw, ImageFont
        import pathlib

        lines = code_snippet.splitlines(True)
        char_scores = self._prepare_char_scores(code_snippet, attn_map, score_key)

        # try monospace font
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", self.cfg.png_font_size)
        except Exception:
            font = ImageFont.load_default()

        # approximate cell size
        w0 = font.getbbox("M")[2]
        line_h = self.cfg.png_line_height
        max_cols = max((len(line) for line in lines), default=0)
        width  = self.cfg.png_margin * 2 + max_cols * w0
        height = self.cfg.png_margin * 2 + len(lines) * line_h

        img = Image.new("RGB", (width, height), "white")
        drw = ImageDraw.Draw(img)

        idx = 0
        y = self.cfg.png_margin
        for line in lines:
            x = self.cfg.png_margin
            for ch in line:
                score = char_scores[idx]["score"] if idx < len(char_scores) else 0.0
                light = int(230 - score * 80)   # darker with higher attention
                drw.rectangle([x, y, x + w0, y + line_h], fill=(200, light, 200))
                drw.text((x, y), ch, fill=(0, 0, 0), font=font)
                x += w0
                idx += 1
            y += line_h

        pathlib.Path(out_png_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(out_png_path)

    # --------- internals ---------
    def _encode_prompt_offsets(self, prompt: str):
        enc = self.tokenizer(
            prompt,
            return_offsets_mapping=True,
            add_special_tokens=True,
            return_tensors=None,
        )
        input_ids = enc["input_ids"]
        if isinstance(input_ids[0], list):
            input_ids = input_ids[0]
            offsets = enc["offset_mapping"][0]
        else:
            offsets = enc["offset_mapping"]
        return input_ids, offsets

    @staticmethod
    def _split_human_tokens(text: str) -> List[Tuple[str, int, int]]:
        out: List[Tuple[str, int, int]] = []
        i, n = 0, len(text)
        def is_word_char(c: str) -> bool: return c.isalnum() or c == "_"
        while i < n:
            c = text[i]
            if is_word_char(c):
                j = i + 1
                while j < n and is_word_char(text[j]):
                    j += 1
                out.append((text[i:j], i, j))
                i = j
            else:
                out.append((c, i, i+1))
                i += 1
        return out


    @staticmethod
    def _project_token_scores_to_chars(
        text_len: int,
        token_offsets: Sequence[Tuple[int, int]],
        token_scores: Sequence[float],
    ) -> List[float]:
        char_scores = np.zeros(text_len, dtype=float)
        for (s, e), w in zip(token_offsets, token_scores):
            s = max(0, s); e = min(text_len, e)
            if e <= s:
                continue
            char_scores[s:e] += float(w) / max(1, (e - s))
        maxv = float(char_scores.max()) if char_scores.size else 0.0
        if maxv > 0:
            char_scores = char_scores / maxv
        return char_scores.tolist()

    @staticmethod
    def _tokenize_code_units(text: str) -> List[Tuple[str, int, int]]:
        tokens: List[Tuple[str, int, int]] = []
        i, n = 0, len(text)

        def is_identifier_char(ch: str) -> bool:
            return ch.isalnum() or ch == "_"

        while i < n:
            ch = text[i]
            if ch.isspace():
                j = i + 1
                while j < n and text[j].isspace():
                    j += 1
                tokens.append((text[i:j], i, j))
                i = j
            elif is_identifier_char(ch):
                j = i + 1
                while j < n and is_identifier_char(text[j]):
                    j += 1
                tokens.append((text[i:j], i, j))
                i = j
            else:
                tokens.append((ch, i, i + 1))
                i += 1
        return tokens

    @staticmethod
    def _collect_code_token_scores(
        offsets: Sequence[Tuple[int, int]],
        scores: Sequence[float],
        code_start: int,
        code_end: int,
    ) -> Tuple[List[Tuple[int, int]], List[float]]:
        code_token_offsets: List[Tuple[int, int]] = []
        code_token_scores: List[float] = []
        for (s, e), w in zip(offsets, scores):
            if e <= code_start or s >= code_end:
                continue
            s_clip = max(s, code_start) - code_start
            e_clip = min(e, code_end) - code_start
            if e_clip > s_clip:
                code_token_offsets.append((s_clip, e_clip))
                code_token_scores.append(float(w))
        return code_token_offsets, code_token_scores

    def _aggregate_lexical_tokens(
        self,
        text: str,
        char_scores: Sequence[float],
    ) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        total = 0.0
        token_idx = 0

        for token, start, end in self._tokenize_code_units(text):
            if token.strip() == "":
                continue  # ignore pure whitespace
            span_scores = char_scores[start:end]
            raw_score = float(sum(span_scores))
            entries.append(
                {
                    "index": token_idx,
                    "token": token,
                    "start": start,
                    "end": end,
                    "raw_score": raw_score,
                }
            )
            total += raw_score
            token_idx += 1

        if total > 0:
            for entry in entries:
                entry["score"] = entry["raw_score"] / total
        else:
            for entry in entries:
                entry["score"] = 0.0

        return entries

    @staticmethod
    def _locate_vocabulary_spans(
        text: str,
        vocabulary: Sequence[Dict[str, Any]],
    ) -> List[Tuple[str, int, int]]:
        spans: List[Tuple[str, int, int]] = []
        pos = 0
        for entry in vocabulary:
            token = str(entry.get("Token", ""))
            if token == "":
                continue
            token = token.strip("\n")
            if token == "":
                continue
            idx = text.find(token, pos)
            if idx == -1:
                spans.append((token, -1, -1))
                continue
            spans.append((token, idx, idx + len(token)))
            pos = idx + len(token)
        return spans

    def _aggregate_human_vocabulary(
        self,
        text: str,
        char_scores: Sequence[float],
        vocabulary: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not vocabulary:
            return []

        spans = self._locate_vocabulary_spans(text, vocabulary)
        entries: List[Dict[str, Any]] = []
        total = 0.0
        v_idx = 0

        for vocab_entry, (token, start, end) in zip(vocabulary, spans):
            missing = start < 0 or end <= start
            if missing:
                raw_score = 0.0
                span_start, span_end = -1, -1
            else:
                span_scores = char_scores[start:end]
                raw_score = float(sum(span_scores))
                span_start, span_end = start, end

            entries.append(
                {
                    "index": v_idx,
                    "token": token,
                    "start": span_start,
                    "end": span_end,
                    "raw_score": raw_score,
                    "token_idx": vocab_entry.get("TokenIdx"),
                    "missing": missing,
                }
            )
            if not missing:
                total += raw_score
            v_idx += 1

        if total > 0:
            for entry in entries:
                entry["score"] = entry["raw_score"] / total
        else:
            for entry in entries:
                entry["score"] = 0.0

        return entries

    def _assemble_attention_map(
        self,
        code_snippet: str,
        char_scores: Sequence[float],
        pool_name: str,
        human_vocabulary: Optional[Sequence[Dict[str, Any]]] = None,
        *,
        annotations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        char_arr = np.asarray(char_scores, dtype=float)
        if char_arr.size:
            maxv = float(char_arr.max())
            if maxv > 0:
                char_arr = char_arr / maxv
        char_list = char_arr.tolist()

        char_attention = [
            {"index": i, "char": code_snippet[i], "score": float(char_list[i])}
            for i in range(len(code_snippet))
        ]

        human_tokens = []
        for text, s, e in self._split_human_tokens(code_snippet):
            seg = float(sum(char_list[s:e]) / max(1, (e - s)))
            human_tokens.append({"text": text, "start": s, "end": e, "score": seg})

        lexical_tokens = self._aggregate_lexical_tokens(code_snippet, char_list)
        fixation_tokens = self._aggregate_human_vocabulary(
            code_snippet, char_list, human_vocabulary or []
        )

        attn_map = {
            "pool": pool_name,
            "char_attention": char_attention,
            "human_tokens": human_tokens,
            "lexical_tokens": lexical_tokens,
            "fixation_tokens": fixation_tokens,
        }
        if annotations:
            attn_map["metadata"] = annotations
        return attn_map

    def mask_attention_map(
        self,
        code_snippet: str,
        attn_map: Dict[str, Any],
        spans: Sequence[Tuple[int, int]],
        human_vocabulary: Optional[Sequence[Dict[str, Any]]] = None,
        *,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        base_scores = [entry["score"] for entry in attn_map.get("char_attention", [])]
        mask = np.zeros(len(base_scores), dtype=float)
        for span_start, span_end in spans:
            start = max(0, int(span_start))
            end = min(len(base_scores), int(span_end))
            if end > start:
                mask[start:end] = 1.0
        masked_scores = (np.asarray(base_scores, dtype=float) * mask).tolist()
        annotations: Dict[str, Any] = {
            "mask_spans": [(int(max(0, s)), int(min(len(base_scores), e))) for s, e in spans]
        }
        if note:
            annotations["note"] = note
        return self._assemble_attention_map(
            code_snippet=code_snippet,
            char_scores=masked_scores,
            pool_name=attn_map.get("pool", self.cfg.pool),
            human_vocabulary=human_vocabulary,
            annotations=annotations,
        )

    @staticmethod
    def _prepare_char_scores(
        code_snippet: str,
        attn_map: Dict[str, Any],
        score_key: str,
    ) -> List[Dict[str, Any]]:
        if score_key == "char_attention":
            return attn_map["char_attention"]
        if score_key == "lexical_tokens":
            char_entries = [
                {"index": i, "char": code_snippet[i], "score": 0.0}
                for i in range(len(code_snippet))
            ]
            for token in attn_map.get("lexical_tokens", []):
                score = float(token.get("score", 0.0))
                start = int(token["start"])
                end = int(token["end"])
                for idx in range(start, min(end, len(code_snippet))):
                    char_entries[idx]["score"] = score
            return char_entries
        if score_key == "fixation_tokens":
            char_entries = [
                {"index": i, "char": code_snippet[i], "score": 0.0}
                for i in range(len(code_snippet))
            ]
            for token in attn_map.get("fixation_tokens", []):
                score = float(token.get("score", 0.0))
                start = int(token["start"])
                end = int(token["end"])
                if start < 0 or end <= start:
                    continue
                for idx in range(start, min(end, len(code_snippet))):
                    char_entries[idx]["score"] = score
            return char_entries
        raise ValueError(f"Unknown score_key '{score_key}'")


__all__ = ["AttentionRenderer", "RenderConfig"]
