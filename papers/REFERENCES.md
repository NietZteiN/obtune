# Foundational literature

*Last updated: 2026-08-04*

The three papers this project builds on are symlinked here from `../../transcoders/papers/`
(one canonical copy in the monorepo). BibTeX keys are in [`references.bib`](references.bib).

## The lineage

| Key | Paper | What it established | What obtune takes from it |
|---|---|---|---|
| `nguyen2026obfuscation` | **The Effect of Code Obfuscation on Human Program Comprehension** (Nguyen, Le, Coronado, Nguyen — arXiv:2603.07668) | The human baseline: obfuscation tiers degrade human comprehension in a measurable, ordered way. Established the L0/L1/L1b/L2/L3 ladder and the output-prediction probe. | The task format (function + input → exact output) and the tier ladder that our `tier_icse` namespace preserves. |
| `le2026machines` | **Do Machines Struggle Where Humans Do? LLM and Human Comprehension of Obfuscated Code** (Le, Nguyen, Nguyen — arXiv:2606.31725) | Human↔LLM alignment through Schulte's Block Model. **ρ = 0.30–0.47** for reasoning-tuned models vs **≈ 0** for coder/instruct — the alignment split. L1b adversarial renaming collapses accuracy (21.25 %) where semantic displacement meets identifier spikes. Dispatcher complexity under flattening: **r = −0.196**. | The 98-cell item-level human anchor (our primary Δρ analysis), the stimuli, and the finding that identifier-level and structural obfuscation are *different failure routes* — which is why our ladder separates the identifier family (L1b/L1r/L2) from the structural family (S1/S2). |
| `dualprocess2026` | **Fast Errors or Slow Effort? Dual-Process Signatures in Human and LLM Code Understanding** (double-blind) | The n=73 human study (6 snippets × L0/L1b/L2, timed/untimed arms). Renaming produces ×3.22 "confused by names, then traced" — Stroop-like interference rather than a confident trap. ~2,048-token System-2 accuracy plateau. CoT length anticorrelates with accuracy (ρ = −0.52). | The condition-level human profiles (item-level ρ at n=6 is underpowered and we say so), and the justification for **no CoT in v1** of the SFT format. |

## How obtune extends this line

Papers 1–3 are **behavioral**: they measure *that* obfuscation breaks comprehension, for humans and
for models, and *where* the two diverge. The mechanistic follow-up ("Opening the Black Box") asks
*how*, via attention reallocation, SAE/transcoder features, and NL autoencoders.

obtune asks a third question neither line addresses: **can it be fixed by training, and if so, what
was actually learned?** The prior work never fine-tunes; the deobfuscation literature (DOBF and
descendants) fine-tunes but always toward *recovery*, so it can never distinguish a model that
learned the transform class from one that memorized specific obfuscators. Holding the evaluation on
still-obfuscated code and holding out an entire obfuscator family (H1) is what makes that
distinction measurable.

The RQ3 attention analysis connects back to the mechanistic instruments: the Anchoring Shift metric
(identifier mass → control/data-flow mass) is the tuning-time analogue of the attention-reallocation
instrument, and a positive result would say the behavioral repair has a specific, inspectable
internal signature.

## Adjacent work to cite

- **DOBF** and identifier-recovery pretraining — the lineage we are separating from.
- KLEE-augmented pair tuning (arXiv:2511.19130), OASIF (VM-obfuscated binaries) — recent deobfuscation-oriented tuning.
- **CodeSteer** (Rong, Yadavally, Nguyen, ASE '26; PDF in `../../allocation_replication/paper/`) — post-hoc attention steering for robust code understanding under obfuscation. The training-free counterpart to our RQ2 conditioning arm.
- LoRA, TIES-merging, DARE — the adapter and merging machinery of RQ2.
- "Attention is not explanation" and its rebuttals — why RQ3 claims are framed as predictive and upgrade to causal only through the knockout intervention.
