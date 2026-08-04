"""Canonical output serialization — Python side.

"Exact match" must mean the SAME thing for Python and JavaScript programs, or the
cross-language claim is not comparable. This module and `canon.mjs` implement one
spec; tests/test_canon_parity.py runs a shared fixture list through both and
requires byte-identical strings.

Spec
----
* JSON-ish text, object keys sorted, no insignificant whitespace: `[1,2]`, `{"a":1}`.
* int  -> exact decimal (Python bignums are printed in full).
* float -> shortest round-trip repr with the exponent zero-padding stripped
  (`1e-07` -> `1e-7`). `-0.0` normalizes to `0`. A float with an exact integral
  value prints as a plain integer (`2.0` -> `2`), because JavaScript has a single
  number type and cannot distinguish the two — collapsing here is what makes the
  cross-language claim comparable. The int/float distinction is not load-bearing
  for output prediction, and scoring.py compares numerics with a tolerance anyway.
* bool -> `true` / `false`; None/null -> `null`.
* str  -> JSON-escaped double-quoted.
* list / tuple -> array. JS Array -> array.
* dict / Map -> object with sorted keys (keys must be str/int/bool; other key types
  are rejected).
* REJECTED (raise Unserializable, program is dropped from the corpus):
  NaN, +/-Infinity, set/frozenset (iteration order not stable across processes),
  complex, bytes, undefined, functions, cyclic structures, and any object that is
  not one of the types above.
"""
from __future__ import annotations

import math
import re
from typing import Any


class Unserializable(ValueError):
    """The value cannot be canonicalized — the program is unsuitable for the corpus."""


_EXP_ZEROS = re.compile(r"e([+-])0+(\d)")


def _fmt_float(x: float) -> str:
    if math.isnan(x) or math.isinf(x):
        raise Unserializable(f"non-finite float: {x!r}")
    if x == 0.0:
        return "0"  # also normalizes -0.0
    # Integral floats collapse to plain integers: JS cannot distinguish 2.0 from 2,
    # so keeping the distinction would make the same program score differently by
    # language. Only collapse when the value is exactly representable as an int.
    if x.is_integer() and abs(x) < 2**53:
        return str(int(x))
    r = repr(float(x))
    return _EXP_ZEROS.sub(r"e\1\2", r)


def _escape(s: str) -> str:
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif o < 0x20:
            out.append(f"\\u{o:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _key(k: Any) -> str:
    if isinstance(k, str):
        return k
    if isinstance(k, bool):
        return "true" if k else "false"
    if isinstance(k, int):
        return str(k)
    raise Unserializable(f"unsupported dict key type: {type(k).__name__}")


def canon(value: Any, _depth: int = 0) -> str:
    """Canonical string for `value`. Raises Unserializable on anything out of spec."""
    if _depth > 40:
        raise Unserializable("value nested too deeply (possible cycle)")
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _fmt_float(value)
    if isinstance(value, str):
        return _escape(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(canon(v, _depth + 1) for v in value) + "]"
    if isinstance(value, dict):
        items = sorted((_key(k), v) for k, v in value.items())
        return "{" + ",".join(f"{_escape(k)}:{canon(v, _depth + 1)}" for k, v in items) + "}"
    if isinstance(value, (set, frozenset)):
        raise Unserializable("set/frozenset in output position: iteration order is not stable")
    raise Unserializable(f"unsupported type: {type(value).__name__}")


def canon_or_none(value: Any) -> str | None:
    try:
        return canon(value)
    except Unserializable:
        return None
