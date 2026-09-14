#!/usr/bin/env python
"""Inline the generated tables into the paper's .tex files, idempotently.

    python scripts/paper/inline_tables.py paper/router_merger

The tables are GENERATED from the cells (59_master_tables.py, gen_fse_tables.py) and were carried by
`\\input{tables/NAME}`. The user asked for them built into the .tex instead, so a reader or a
co-author opening the source sees the table rather than a reference to a file they have to go and
find, and the sources compile on their own.

The regeneration workflow still has to work, so an inlined table is wrapped in markers:

    % >>> GENERATED TABLE NAME -- from tables/NAME.tex; regenerate, then re-run inline_tables.py
    ...table body...
    % <<< GENERATED TABLE NAME

On every run this replaces either a bare `\\input{tables/NAME}` or an existing marked block with the
current contents of `tables/NAME.tex`. Running it twice changes nothing; running it after
regenerating the tables refreshes every inlined copy. `tables/` is kept as the generators' output and
as the provenance trail -- each file's header names the JSON it came from.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

BEGIN = "% >>> GENERATED TABLE {name} -- from tables/{name}.tex; regenerate, then re-run inline_tables.py"
END = "% <<< GENERATED TABLE {name}"

def block(name: str, body: str) -> str:
    return BEGIN.format(name=name) + "\n" + body.rstrip("\n") + "\n" + END.format(name=name)

def main(argv):
    root = Path(argv[1] if len(argv) > 1 else "paper/router_merger")
    tdir = root / "tables"
    files = [root / "fse27.tex"] + sorted((root / "sections").glob("*.tex"))
    n_in = n_re = 0
    for f in files:
        if not f.exists(): continue
        s = orig = f.read_text()
        # refresh blocks already inlined
        def refresh(m):
            nonlocal n_re
            name = m.group(1); p = tdir / f"{name}.tex"
            if not p.exists(): return m.group(0)
            n_re += 1; return block(name, p.read_text())
        s = re.sub(r"% >>> GENERATED TABLE (\S+) --.*?\n.*?% <<< GENERATED TABLE \1",
                   refresh, s, flags=re.S)
        # expand any remaining \input{tables/NAME}
        def expand(m):
            nonlocal n_in
            name = m.group(1); p = tdir / f"{name}.tex"
            if not p.exists():
                print(f"  MISSING tables/{name}.tex -- left as \\input", file=sys.stderr)
                return m.group(0)
            n_in += 1; return block(name, p.read_text())
        s = re.sub(r"\\input\{tables/([^}]+)\}", expand, s)
        if s != orig:
            f.write_text(s); print(f"  {f.relative_to(root)}")
    print(f"inlined {n_in} table(s), refreshed {n_re}")
    left = sum(len(re.findall(r"\\input\{tables/", (root/p).read_text()))
               for p in ["fse27.tex"] + [str(x.relative_to(root)) for x in (root/"sections").glob("*.tex")])
    print("remaining \\input{tables/...}:", left)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
