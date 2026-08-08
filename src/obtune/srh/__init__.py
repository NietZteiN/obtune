"""Experiment 1 of the Shared Representation Hypothesis (SRH) follow-up.

    Does bidirectional training build SHARED representations for a transformation `T`
    and its inverse `T-inverse`, or two disjoint one-way circuits?

This package is a **follow-up to**, not a part of, the `nikiema2025contrastive`
replication in `obtune.cft`. The replication answers the paper's question on our corpus;
this asks the question the paper leaves open, and the two must stay separable.

The question Experiment 1 settles
---------------------------------
The paper attributes reverse-direction capability to the *contrastive objective*. But
reverse training data is free here — every `(original, obfuscated)` pair is also an
`(obfuscated, original)` pair — and the paper never ran that baseline. So:

    FWD     forward obfuscation only            (= the replication's `sft` arm)
    REV     reverse deobfuscation only          reverse ceiling; the kill-gate
    FLIP    both directions                     the missing baseline
    MIX50   50/50 by program, matched budget    the arm the experiment turns on
    FWD2x   forward only, 6 epochs              rules out "FLIP just trained longer"
    CFT     contrastive triplets                (= the replication's `cft` arm)

Why MIX50 is the decisive arm
-----------------------------
"Same data budget" is not one quantity, and measuring it inverts the paper's framing.
Per epoch on the Python corpus, relative to FWD:

    arm       instances   supervised tok   sequence tok (FLOPs)   steps
    FLIP        2.00x         1.52x              2.00x            2.00x
    CFT         2.52x         1.02x              2.60x            2.53x
    MIX50       1.00x         0.76x              1.00x            1.00x

CFT already costs more than FLIP on every axis a practitioner pays for while adding
almost no supervised signal (a `pos`/`neg` example carries two whole programs in its
prompt but supervises the single token YES or NO). So the honest comparison is not
budget-matching but **dominance**. MIX50 then supplies the one arm matched to FWD on
instances, steps, FLOPs and wall-clock simultaneously — with *strictly less* supervision.
If MIX50 shows reverse capability where FWD shows none, bidirectional exposure produces
it at negative budget cost, and the contrastive objective is not the mechanism.

What this package must never do
-------------------------------
`obtune.cft.prompts.completion_for` raises for the reverse direction, and
`cft.dataset.load_mixture` rejects it. That is not an oversight — it is the replication's
central guarantee that its reverse direction is never supervised, and two tests lock it
(`test_cft_prompts.py::test_reverse_direction_has_no_training_target`,
`test_cft_dataset.py::test_load_mixture_rejects_the_reverse_task`). The reverse
*training* task therefore lives here, in `srh.prompts`, and `cft.prompts.template_sha256()`
stays frozen at the value already recorded in every `pool_report.json`.

Scope limit inherited from the corpus
-------------------------------------
The source paper's hardest transformation is string encryption, which maps onto obtune's
`H1` — quarantined, never trainable (`../CLAUDE.md` §3.2). `S1` (control-flow flattening)
is the primary transformation instead, and is a better one: it preserves identifier
names, so its inverse is purely structural, well-posed, and execution-verifiable. `S2` is
the easy sanity check; the renaming conditions keep the ill-posed-inverse caveat.
"""

from obtune.srh import prompts  # noqa: F401

__all__ = ["prompts"]
