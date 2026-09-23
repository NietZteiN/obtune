# INVALID — CodeLlama-34B MBPP+ retention, 2026-09-22

Four arms from the first (cancelled) run of `obtune.bench_retention`. **Do not quote these.**

Every adapted arm reads `pass@1 = 0.0000` here, and that is an extraction artefact, not
forgetting. `forgetting._extract_code` returns the completion verbatim when it contains a `def`
and no code fence; the chat template's first generated token is a space, so a bare-code reply
becomes `" def f(...)"` and raises `IndentationError` on line 1 for every task. The untuned model
fences its answers, so it is unaffected and scored 0.5313 — which is exactly what makes the
comparison look like catastrophic forgetting.

`tuned_L0` emitted `" def kth_element(arr, k):\n    return sorted(arr)[k-1] "` — the same correct
function the untuned model got credit for — and scored zero on all 399 tasks at a format-failure
rate of 0.0075.

Superseded by the rerun with `bench_retention.extract_code`, an arm-blind dedent repair reported
beside the strict rate. Kept as the evidence for that fix.
