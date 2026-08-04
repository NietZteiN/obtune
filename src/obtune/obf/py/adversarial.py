"""L1b vocabulary — adversarial/misleading renaming (the `fibfib -> smoothArea` trap).

L1b is the condition that separates "the model reads the code" from "the model reads
the names". Its power comes entirely from the *vocabulary*: a random name (L1r) merely
removes a cue, while a wrong name actively supplies a false one, and the literature on
identifier-driven comprehension says the false cue is the expensive one.

Two vocabularies, three strengths
---------------------------------
`INVERSIONS` is harvested from ../dataset/generate_adversarial_variants.py
(KEYWORD_REPLACEMENTS + DESCRIPTION_MISDIRECTIONS, merged and de-duplicated). It maps a
concept word to its semantic *opposite*, so `find_max` becomes `find_min`: the name is
still about the right domain and is therefore read, but it asserts the inverse of what
the code does. That is strength 3.

`DOMAIN_VOCAB` is new here: plausible-but-unrelated names from domains the corpus never
contains (graphics, audio, telemetry, billing). `fibfib -> smooth_area` reads as
competent code from another file — the reader has nothing to invert, only a wrong prior.
That is strength 2.

`FILLER` covers names with no semantic content at all (`i`, `tmp`), where the only
available misdirection is to make them *look* meaningful. Strength 1.

Only the mechanism differs from the harvested script: it renamed one function by regex,
which cannot tell an identifier from the same text in a string. Here every name goes
through the scope-aware renamer in rename.py, and the strongest available misdirection
is reserved for the entry function.
"""
from __future__ import annotations

import random
from typing import Any

from obtune.obf.base import Bail, SnippetCtx, TransformResult, split_words
from obtune.obf.py.rename import binding_plan, rename

#: concept -> semantic opposite. Harvested from dataset/generate_adversarial_variants.py
#: (KEYWORD_REPLACEMENTS ∪ DESCRIPTION_MISDIRECTIONS), then made symmetric where the
#: source tables were one-directional so that the substitution is stable regardless of
#: which side of a pair a corpus program happens to use.
INVERSIONS: dict[str, str] = {
    "add": "subtract",
    "subtract": "add",
    "addition": "subtraction",
    "subtraction": "addition",
    "sum": "difference",
    "difference": "sum",
    "plus": "minus",
    "minus": "plus",
    "increment": "decrement",
    "decrement": "increment",
    "max": "min",
    "min": "max",
    "maximum": "minimum",
    "minimum": "maximum",
    "largest": "smallest",
    "smallest": "largest",
    "greatest": "least",
    "least": "greatest",
    "longest": "shortest",
    "shortest": "longest",
    "first": "last",
    "last": "first",
    "head": "tail",
    "tail": "head",
    "push": "pop",
    "pop": "push",
    "prime": "composite",
    "composite": "prime",
    "odd": "even",
    "even": "odd",
    "positive": "negative",
    "negative": "positive",
    "ascending": "descending",
    "descending": "ascending",
    "sort": "shuffle",
    "shuffle": "sort",
    "sorted": "shuffled",
    "reverse": "preserve",
    "search": "delete",
    "find": "lose",
    "count": "ignore",
    "filter": "duplicate",
    "unique": "repeated",
    "palindrome": "anagram",
    "anagram": "palindrome",
    "fibonacci": "factorial",
    "factorial": "fibonacci",
    "fib": "fact",
    "fact": "fib",
    "gcd": "lcm",
    "lcm": "gcd",
    "path": "wall",
    "graph": "maze",
    "subset": "superset",
    "superset": "subset",
    "permutation": "combination",
    "combination": "permutation",
    "coin": "bill",
    "knapsack": "knockout",
    "encode": "decode",
    "decode": "encode",
    "encrypt": "decrypt",
    "decrypt": "encrypt",
    "valid": "invalid",
    "invalid": "valid",
    "empty": "full",
    "full": "empty",
    "open": "close",
    "close": "open",
    "start": "end",
    "end": "start",
    "begin": "finish",
    "upper": "lower",
    "lower": "upper",
    "left": "right",
    "right": "left",
    "insert": "remove",
    "remove": "insert",
    "merge": "split",
    "split": "merge",
    "join": "separate",
    "flatten": "nest",
    "compress": "expand",
    "expand": "compress",
    "double": "halve",
    "half": "twice",
    "square": "root",
    "root": "leaf",
    "leaf": "root",
    "child": "parent",
    "parent": "child",
    "depth": "breadth",
    "breadth": "depth",
    "total": "remainder",
    "product": "quotient",
    "quotient": "product",
    "multiply": "divide",
    "divide": "multiply",
    "input": "output",
    "output": "input",
    "source": "target",
    "target": "source",
    "true": "false",
    "success": "failure",
    "enable": "disable",
}

#: Plausible names from domains the corpus never contains — the `fibfib -> smooth_area`
#: trap. Grouped so one program draws from one coherent domain and therefore reads as
#: real code rather than as a bag of random words.
DOMAIN_VOCAB: dict[str, list[str]] = {
    "graphics": [
        "smooth area", "bezier span", "viewport scale", "pixel gutter", "raster tile",
        "shader slot", "gamma ramp", "vertex batch", "clip bounds", "mip level",
        "sprite atlas", "alpha mask", "depth buffer", "tessellation step", "texel width",
    ],
    "audio": [
        "sample gate", "reverb tail", "envelope decay", "filter cutoff", "chorus depth",
        "bit crush", "pan spread", "gain stage", "waveform bucket", "transient snap",
        "noise floor", "voice steal", "loop point", "sidechain duck", "harmonic drift",
    ],
    "telemetry": [
        "heartbeat lag", "packet jitter", "sensor drift", "uptime slice", "sample window",
        "trace span", "beacon skew", "queue backlog", "retry budget", "latency bucket",
        "shard weight", "probe timeout", "rollup bin", "drop ratio", "warm pool",
    ],
    "billing": [
        "invoice float", "ledger offset", "tax bracket", "refund window", "coupon tier",
        "settlement lag", "chargeback pool", "accrual bucket", "billing anchor",
        "proration step", "dunning cycle", "credit memo", "fee schedule", "payout batch",
        "escrow hold",
    ],
    "logistics": [
        "pallet slot", "dock window", "route detour", "manifest gap", "carrier lane",
        "freight tier", "loading dwell", "customs hold", "yard buffer", "hub transfer",
        "trailer fill", "wave pick", "cutoff shift", "backhaul leg", "cross dock",
    ],
}

#: Names that carry no semantic signal of their own (`i`, `tmp`, `x`): the only
#: available misdirection is to make them look load-bearing.
FILLER: list[str] = [
    "cached weight", "pending flag", "checksum seed", "retry count", "lookup handle",
    "session token", "dirty bit", "scratch cursor", "pool index", "frame budget",
    "sync epoch", "quota left", "stale mark", "spill slot", "warm hint",
]

#: Strength of the misdirection actually applied to a name.
STRENGTH_INVERSION = 3
STRENGTH_DOMAIN = 2
STRENGTH_FILLER = 1


#: Verbs that describe *what the function does with* a concept rather than the concept
#: itself. Inverting `find` in `find_max_prime` yields `lose_max_prime`, which reads as
#: nonsense and is therefore discounted; inverting `prime` yields `find_max_composite`,
#: which reads as competent code that asserts the wrong thing. Concept words win.
_WEAK_VERBS = frozenset(
    {"find", "search", "count", "get", "make", "build", "check", "compute", "calc",
     "calculate", "return", "apply", "run", "do", "is", "has"}
)


def _invert(name: str) -> str | None:
    """Substitute the most semantically central invertible word of `name`.

    Word-level rather than substring-level: the harvested script matched `"min" in
    "administrator"`, which produced nonsense names. Splitting on snake/camel
    boundaries keeps `find_max_value -> find_min_value` and leaves `admin` alone.
    """
    words = split_words(name)
    if not words:
        return None
    candidates = [i for i, w in enumerate(words) if w.lower() in INVERSIONS]
    if not candidates:
        return None
    strong = [i for i in candidates if words[i].lower() not in _WEAK_VERBS]
    pick = (strong or candidates)[-1]  # trailing word is the noun in `verb_noun` names
    out = list(words)
    out[pick] = INVERSIONS[words[pick].lower()]
    return " ".join(out)


def choose_hints(
    rng: random.Random, names: list[tuple[str, str]], entry_point: str
) -> tuple[dict[str, str], dict[str, int]]:
    """Pick a misleading stem for every name; return (hints, strength-per-name).

    The entry function is resolved first and gets the strongest misdirection available
    to it (conditions.yaml: `strength: strongest_on_entry`): an inversion when its own
    name carries an invertible concept, otherwise a domain word. Inversion beats a
    domain word at equal availability because it actively asserts the opposite of what
    the code does, whereas a domain word only supplies an unrelated prior.
    """
    domain = rng.choice(sorted(DOMAIN_VOCAB))
    pool = list(DOMAIN_VOCAB[domain])
    rng.shuffle(pool)
    filler = list(FILLER)
    rng.shuffle(filler)

    hints: dict[str, str] = {}
    strength: dict[str, int] = {}
    ordered = sorted(names, key=lambda nk: (nk[0] != entry_point,))  # entry first

    def take(seq: list[str], fallback: list[str]) -> str:
        if seq:
            return seq.pop()
        if fallback:
            return fallback.pop()
        return f"{domain}_{rng.randrange(1000):03d}"

    for name, _kind in ordered:
        inverted = _invert(name)
        if inverted is not None:
            hints[name] = inverted
            strength[name] = STRENGTH_INVERSION
        elif len(name) <= 2 or name.lower() in ("tmp", "temp", "val", "res", "ret", "buf"):
            hints[name] = take(filler, pool)
            strength[name] = STRENGTH_FILLER
        else:
            hints[name] = take(pool, filler)
            strength[name] = STRENGTH_DOMAIN
    return hints, strength


def transform(ctx: SnippetCtx) -> TransformResult:
    """L1b — adversarial renaming of all bindings, strongest misdirection on the entry."""
    names = binding_plan(ctx.src)
    if not names:
        return TransformResult(ctx.src, False, notes=["no renamable bindings"])
    if ctx.entry_point and ctx.entry_point not in {n for n, _ in names}:
        raise Bail(f"entry point {ctx.entry_point!r} is not a renamable binding")

    hints, strength = choose_hints(ctx.rng, names, ctx.entry_point)
    result = rename(ctx, "adversarial", hints=hints)

    entry_strength = strength.get(ctx.entry_point, 0)
    meta: dict[str, Any] = {
        "misdirection_strength": strength,
        "entry_misdirection_strength": entry_strength,
        "mean_misdirection_strength": (
            sum(strength.values()) / len(strength) if strength else 0.0
        ),
        "n_inverted": sum(1 for v in strength.values() if v == STRENGTH_INVERSION),
    }
    result.extra.update(meta)
    result.notes.append(
        f"entry misdirection strength {entry_strength} "
        f"({ctx.entry_point!r} -> {result.extra.get('entry_point_new')!r})"
    )
    return result
