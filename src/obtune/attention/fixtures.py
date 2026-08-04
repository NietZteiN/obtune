"""Real programs from the ICSE stimuli, embedded for offline validation + tests.

WHY embedded: `data/eval/testset/` is materialized by a peer module (testset/ingest.py)
and is empty until that runs, but `attention/validate.py` has to be able to prove the
span->token resolution rate on REAL obfuscated code before anything downstream is built.
These are byte-identical copies of rows from the Dataset-A source named in
configs/data.yaml (`full_human_experiment_v2.json`) — the same programs the test set is
drawn from, and the only programs with a human baseline.

`condition` carries the NEW-ladder label the legacy tier maps to (docs/TIER_MAPPING.md);
`tier_icse` keeps the original so the provenance is not lost. validate.py prefers the
real test set when it exists and falls back to this list.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixtureProgram:
    program_id: str
    condition: str
    tier_icse: str
    language: str
    entry_point: str
    code: str

    @property
    def item_id(self) -> str:
        return f"{self.program_id}::{self.condition}::0"


FIXTURES: tuple[FixtureProgram, ...] = (
    FixtureProgram(
        program_id='JavaScript/63',
        condition='L0',
        tier_icse='L0',
        language='javascript',
        entry_point='fibfib',
        code='\nconst fibfib = (n) => {\n  if (n == 0 || n == 1)\n    return 0;\n  if (n == 2)\n    return 1;\n  return fibfib(n - 1) + fibfib(n - 2) + fibfib(n - 3);\n}\n\n',
    ),
    FixtureProgram(
        program_id='JavaScript/63',
        condition='L1b',
        tier_icse='L1b',
        language='javascript',
        entry_point='fibfib',
        code='\nconst smoothArea = (_lastNSecs) => {\n  if (_lastNSecs == 0 || _lastNSecs == 1)\n    return 0;\n  if (_lastNSecs == 2)\n    return 1;\n  return smoothArea(_lastNSecs - 1) + smoothArea(_lastNSecs - 2) + smoothArea(_lastNSecs - 3);\n}\n\n',
    ),
    FixtureProgram(
        program_id='JavaScript/63',
        condition='L2',
        tier_icse='L2',
        language='javascript',
        entry_point='fibfib',
        code="const fibfib = n => {\n    const EnHOIf = {\n        'hszwT': function (x, y) {\n            return x == y;\n        },\n        'zlfVA': function (x, y) {\n            return x == y;\n        },\n        'mFypV': function (x, y) {\n            return x == y;\n        },\n        'rAgqn': function (x, y) {\n            return x + y;\n        },\n        'feewe': function (x, y) {\n            return x + y;\n        },\n        'JHrvY': function (callee, param1) {\n            return callee(param1);\n        },\n        'KOqQU': function (x, y) {\n            return x - y;\n        },\n        'ojDHb': function (x, y) {\n            return x - y;\n        }\n    };\n    if (EnHOIf['hszwT'](n, 0x0) || EnHOIf['zlfVA'](n, 0x1))\n        return 0x0;\n    if (EnHOIf['mFypV'](n, 0x2))\n        return 0x1;\n    return EnHOIf['rAgqn'](EnHOIf['feewe'](EnHOIf['JHrvY'](fibfib, EnHOIf['KOqQU'](n, 0x1)), EnHOIf['JHrvY'](fibfib, EnHOIf['KOqQU'](n, 0x2))), fibfib(EnHOIf['ojDHb'](n, 0x3)));\n};",
    ),
    FixtureProgram(
        program_id='Python/36',
        condition='L0',
        tier_icse='L0',
        language='python',
        entry_point='myFunct',
        code="def myFunct(n: int):\n    ns = []\n    for i in range(n):\n        if i % 11 == 0 or i % 13 == 0:\n            ns.append(i)\n    s = ''.join(list(map(str, ns)))\n    ans = 0\n    for c in s:\n        ans += c == '7'\n    return ans",
    ),
    FixtureProgram(
        program_id='Python/36',
        condition='L1b',
        tier_icse='L1b',
        language='python',
        entry_point='initAttrs',
        code="def initAttrs(stride: int):\n\n    input_def = []\n\n    for blob_freq_start in range(stride):\n\n        if blob_freq_start % 11 == 0 or blob_freq_start % 13 == 0:\n\n            input_def.append(blob_freq_start)\n\n    vmaxs = ''.join(list(map(str, input_def)))\n\n    cleanIsolatedTriangles = 0\n\n    for sigparG2Vmax in vmaxs:\n\n        cleanIsolatedTriangles += sigparG2Vmax == '7'\n\n    return cleanIsolatedTriangles",
    ),
    FixtureProgram(
        program_id='Python/36',
        condition='L2',
        tier_icse='L2',
        language='python',
        entry_point='myFunct',
        code="def myFunct(n: int):\n\n    state_2848 = 0\n\n    while state_2848 < 6:\n\n        if state_2848 == 0:\n\n            ns = []\n\n            state_2848 += 1\n\n        if state_2848 == 1:\n\n            for i in range(n):\n\n                if i % 11 == 0 or i % 13 == 0:\n\n                    ns.append(i)\n\n            state_2848 += 1\n\n        if state_2848 == 2:\n\n            s = ''.join(list(map(str, ns)))\n\n            state_2848 += 1\n\n        if state_2848 == 3:\n\n            ans = 0\n\n            state_2848 += 1\n\n        if state_2848 == 4:\n\n            for c in s:\n\n                ans += c == '7'\n\n            state_2848 += 1\n\n        if state_2848 == 5:\n\n            return ans\n\n            state_2848 += 1",
    ),
    FixtureProgram(
        program_id='Python/104',
        condition='L0',
        tier_icse='L0',
        language='python',
        entry_point='myFunct',
        code='def myFunct(x):\n\n    odd_digit_elements = []\n\n    for i in x:\n\n        if all((int(c) % 2 == 1 for c in str(i))):\n\n            odd_digit_elements.append(i)\n\n    return sorted(odd_digit_elements)',
    ),
    FixtureProgram(
        program_id='JavaScript/58',
        condition='L0',
        tier_icse='L0',
        language='javascript',
        entry_point='common',
        code='\nconst common = (l1, l2) => {\n  var ret = new Set();\n  for (const e1 of l1)\n    for (const e2 of l2)\n      if (e1 == e2)\n        ret.add(e1);\n  return [...ret].sort();\n}\n\n',
    ),
    FixtureProgram(
        program_id='Python/74',
        condition='L2',
        tier_icse='L2',
        language='python',
        entry_point='myFunct',
        code='def myFunct(lst1, lst2):\n\n    state_6306 = 0\n\n    while state_6306 < 5:\n\n        if state_6306 == 0:\n\n            l1 = 0\n\n            state_6306 += 1\n\n        if state_6306 == 1:\n\n            for st in lst1:\n\n                l1 += len(st)\n\n            state_6306 += 1\n\n        if state_6306 == 2:\n\n            l2 = 0\n\n            state_6306 += 1\n\n        if state_6306 == 3:\n\n            for st in lst2:\n\n                l2 += len(st)\n\n            state_6306 += 1\n\n        if state_6306 == 4:\n\n            if l1 <= l2:\n\n                return lst1\n\n            else:\n\n                return lst2\n\n            state_6306 += 1',
    ),
    FixtureProgram(
        program_id='JavaScript/163',
        condition='L1b',
        tier_icse='L1b',
        language='javascript',
        entry_point='generateIntegers',
        code='\nconst nonEmptyObject = (tr, _headers) => {\n  if (tr > _headers) {\n    let dynamicTasks = tr;\n    tr = _headers;\n    _headers = dynamicTasks;\n  }\n  let attrVal = []\n  for (let nextNode = tr; nextNode <= _headers; nextNode++) {\n    if (nextNode == 2 || nextNode == 4 || nextNode == 6 || nextNode == 8) { attrVal.push(nextNode) }\n  }\n  return attrVal\n}\n\n',
    ),
)


def by_language(language: str) -> list[FixtureProgram]:
    return [f for f in FIXTURES if f.language == language]
