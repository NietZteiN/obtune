# 2026-09-20 — Results restructured to RQ1–RQ3, and the clean-code recovery claim verified before it was made

**Thread:** writeup · **Prompted by:** user — three RQs supplied verbatim, results to be rewritten
against them with takeaway boxes, discussion removed, and "the fact obfuscation generally brings us
back to L0 clean code" promoted to an RQ1 subsection and emphasised throughout.

## The claim was checked first, because it is the largest one in the paper

Reference: the untuned model's accuracy on `L0`, unobfuscated source — the performance obfuscation
removes. Question: do adapted arms, reading *obfuscated* programs, reach 100 % of it?

**Forward.** Yes, and beyond it. Untuned models retain 75–92 % of clean-code accuracy on single
transforms, 61–83 % at depth 2, 47–63 % on the held-out family. Adapted arms reach 132–195 %,
110–180 % and 82–132 % on the same groups. **78 of 84 arm × model × group cells are at or above
100 % — 93 %.**

**Backward.** No: 29 of 78, and the merge is the closest. Recovery is a property of the trained
direction.

So the claim is real and larger than "adaptation helps": a model fine-tuned on obfuscated code reads
obfuscated programs better than the original model reads clean ones, including on an obfuscator
family it never saw. It is stated with its exception attached, because the exception is the rest of
the paper.

## Structure

`sections/rqs.tex` is new and carries the three questions as given. `results.tex` is rewritten
one-for-one against them, each closing with a `takeaway` box (the environment already existed in the
preamble). `discussion.tex` is retired to `sections/retired/` — its cross-view argument moved into
RQ1, its "what to use" into RQ3, its breadth material into RQ2.

Two tables now serve the results: CodeLlama-7B's complete per-condition grid, moved out of
Appendix A because it is the one model on which every arm exists, and the panel summary
`tab:main`. Appendix A keeps the other seven.

## What RQ1 argues, and what it does not

RQ1 asks what merging composes. The evidence that it is a general capability rather than a union of
transform-specific ones is negative as much as positive: the merge is *not* the best arm on the
transforms its specialists were built from — the KL and router arms beat it there by three to six
points — and is strongest where the surface is unfamiliar. If it were recombining surface knowledge,
the seen stacks are where it should win.

That argument is a reading of the pattern, not a measurement of internal structure. It is stated in
the paper as an inference from where the advantage appears, and no mechanism beyond that is claimed.
