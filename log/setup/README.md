# setup — scaffold, environment, data layer, obfuscation pipeline

*Last updated: 2026-08-04*
**Status:** active

## Hypotheses — open
- (the scientific ledger lives in [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md); this thread tracks engineering correctness)
- **S1/S2 coverage:** the flattener/dead-code passes apply to >=90% of real programs. CONFIRM if `coverage_matrix.json` shows >=0.90 per condition; REFUTE below that, in which case headline numbers must use the all-conditions-succeeded common subset and the shortfall is reported.
- **Span->token resolution >= 0.98 on Qwen2.5-Coder tokenizers** (the prior 1.0 validation was on Llama-3.1-8B / Qwen3-0.6B). REFUTE below 0.98 — RQ3 hard-fails there.

## Hypotheses — resolved
- ✓ **Cross-language canonicalization**: Python and JavaScript canonicalizers produce byte-identical strings for equivalent values — 9/9 fixture groups, plus matching rejection behavior. Resolved by [`2026-08-04_scaffold-and-pipeline.md`](2026-08-04_scaffold-and-pipeline.md), after fixing two real defects (integral-float formatting; vm-context intrinsics breaking object type checks).

## What worked
- Testing the canonicalizers against each other rather than assuming agreement — it found the float-format divergence that would have made the JS arm of RQ1 incomparable.
- Confining `javascript-obfuscator` to the H1 generator architecturally, instead of configuring it carefully per condition.
- Four independent quarantine layers; the content-marker scan caught a planted `atob(` in a row labeled `S1`, which label checks alone cannot.

## What didn't
- Resolving `node` from the child's restricted PATH — every JS execution failed silently as `crash` until the binary was resolved once at import via `shutil.which`.
- Mapping an `RLIMIT_CPU` kill to `crash`; `crash` must mean the harness broke, `timeout` that the program was unsuitable.

## Open ideas
- Run the determinism filter with more than 3 repeats on programs whose outputs contain dict/object keys — hash-order dependence is the failure mode most likely to survive a small repeat count.
- Consider recording per-condition transform wall-time in the coverage manifest; a condition that is slow to generate is usually one that is bailing and retrying.

## Entries
- [`2026-08-04_scaffold-and-pipeline.md`](2026-08-04_scaffold-and-pipeline.md) — project created; contracts verified in both languages; RQ1–RQ3 stack built

## Doc / results links
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md) (§9 records deviations from the v0.1 brief)
- [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md)
- [`../../data/DATA_SOURCES.md`](../../data/DATA_SOURCES.md)
