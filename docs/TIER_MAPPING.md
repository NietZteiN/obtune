# TIER_MAPPING.md — the legacy ICSE tiers vs the obtune conditions

*Last updated: 2026-08-04*

This project carries **two orthogonal namespaces** on its test set. Mixing them would
silently invalidate either the human comparison or the cross-language claim, so every
row carries exactly one of them and they are never averaged together.

| Field | Values | Rows | What it is for |
|---|---|---|---|
| `tier_icse` | `L0 L1 L1b L2 L3` | 350, **byte-identical** to the ICSE artifacts | The only rows comparable to the human baselines (Papers 1–3) |
| `condition` | `L0 L1b L1r L2 S1 S2 H1` | regenerated from the 70 L0 parents | The transfer matrix; identical semantics in both languages |

## Why the legacy tiers could not simply be reused

The legacy tier codes denote **different transforms depending on language, and on
generation vintage**. Verified against the artifacts:

| Tier | Python meaning | JavaScript meaning |
|---|---|---|
| `L0` | original | original |
| `L1` | random-hex identifier rename (`var_68f8`) | hex *numeric literals* + member-string rewrite (`e['push']`, `0x2`) |
| `L1b` | adversarial rename | adversarial rename (a *different* generation round than the archived mapping parquets) |
| `L2` | sequential `state_N` while-machine (control flow!) | object-dispatch table + dead code + string table |
| `L3` | `L1` + `L2` stacked | `L2` + single-letter minification |

Reusing `L2` for "full identifier obfuscation" would have produced a transfer matrix in
which one label denotes four different transforms depending on language and vintage —
exactly the drift that makes a cross-language claim unfalsifiable. Hence two
namespaces and this crosswalk.

## Crosswalk

| Legacy tier | Nearest obtune condition | Reused? | Note |
|---|---|---|---|
| `L0` | **`L0`** | shared parent | The new conditions are generated from a whitespace-normalized copy of this code; the legacy row keeps the exact original bytes. |
| `L1` | py ≈ `L1r`, js ≈ none | no | Python L1 left the entry function's name intact; `L1r` renames every binding including the entry point. JS L1 is not an identifier transform at all. |
| `L1b` | `L1b` (concept only) | no — regenerated | The study's L1b generator was never recovered. Even the archived `L1b_mapping` parquets are from a different round (`fibfib→rns` there vs `fibfib→smoothArea` in the shipped stimuli, ~0/10 match), so mappings are derived cross-tier from the stimuli themselves. |
| `L2` | py ≈ `S1` (degenerate), js ≈ `S2` **+ H1-family** | no | Python L2 is flattening with *ordered, monotone* state ids — a degenerate special case of `S1`, which randomizes and shuffles them. |
| `L3` | stacked; js minify ≈ `L2` | no | obtune conditions are never stacked. |

## ⚠️ Legacy JavaScript L2/L3 contain H1-family features

The ICSE JS L2/L3 rows use **string-keyed dispatch tables** (`mkAvEl['xqLrF'](i,0x2)`),
which is an H1-family feature (string encoding). Consequences, both enforced rather
than merely documented:

1. They must **never** enter training. `scripts/check_manifest.py`'s H1-marker content
   scan matches on their string-table pattern, so a leak fails `make check`.
2. They must **never** back an "unseen transform" claim — they are not unseen relative
   to H1.

They remain valid for the human comparison, which is what they exist for.

## What the new conditions guarantee that the legacy tiers do not

* **Single-transform.** Each condition applies exactly one transform to the L0 parent;
  nothing is stacked, which removes the composition-bug class the L3 tier had.
* **Language-identical semantics.** `S1` is a randomized dispatch loop in both
  languages; `L2` is sequential minification in both; and an identifier condition
  changes *only identifiers* — `tests/test_condition_purity.py` asserts that masking
  identifiers makes a variant textually identical to its parent, which is what caught
  the JS transforms printing at a different indentation than L0 normalization.
* **Execution-gated.** Every variant reproduces its parent's canonical output on all
  stored cases plus fuzzed gate inputs, comparing exceptions by type only.

## Measured coverage on the 70 test parents

Produced by `scripts/05_build_variants.py --target testset`
(`data/manifests/coverage_matrix_testset.json`):

| Language | n | L0 | L1b | L1r | L2 | S1 | S2 | all-six subset |
|---|---|---|---|---|---|---|---|---|
| Python | 40 | 40 | 40 | 40 | 40 | **33** | 40 | **33/40** |
| JavaScript | 30 | 30 | 30 | 30 | 30 | 30 | 30 | **30/30** |

All 7 Python `S1` declines are the `min_states=3` guard on functions whose bodies are
too short to form a dispatch loop — a genuine structural limit, not a defect.

H1 (quarantined, generated separately): **Python 27/40, JavaScript 24/30 = 51/70**.
Thirteen Python programs fall below the 3-site bar and six of those contain no
strings, no integer literals and no MBA-able operators at all — there is nothing for
the transform family to act on. The Invariance Index is therefore computed on the
H1-eligible subset, with the other conditions restricted to that same subset when
compared against it.

## Headline-number rule

Transfer-matrix headline numbers use the **all-conditions-succeeded common subset**,
because `S1`/`S2` decline on different programs than the identifier conditions and a
per-condition full set would confound the family contrast with differing program sets.
Per-condition full sets are reported as a secondary analysis, and
`coverage_matrix_testset.json` is published alongside.
