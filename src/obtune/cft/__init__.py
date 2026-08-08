"""Contrastive Fine-Tuning (CFT) — replication of `nikiema2025contrastive` on the
obtune corpus.

    Nikiema, Samhi, Moumoula, Djire, Kabore, Klein, Bissyande (2025).
    "Using Contrastive Learning to Improve Two-Way Reasoning in Large Language
    Models: The Obfuscation Task as a Case Study." arXiv:2509.05553.
    PDF: papers/nikiema2025contrastive.pdf

Why this lives in obtune
------------------------
`papers/RELATED_WORK.md` §2.1 registers this as the *nearest prior work* to obtune's
pilot finding: it names the same disease ("cognitive specialization" — fine-tuning on
a forward transform destroys the reverse direction) on a different axis. obtune's axis
is transform identity (a held-out obfuscator family); theirs is direction (forward vs
reverse). §7 names CFT as the candidate intervention if obtune's RQ1 grid confirms the
pilot. This package answers the prerequisite question: *does their result reproduce on
our corpus at all?*

What is replicated, and what is not
-----------------------------------
Replicated: the three-task contrastive objective (§5.0.2), the LoRA setup, the SFT
baseline, the forward/reverse evaluation protocol (§4.1, §4.3), and CodeBLEU as the
primary syntactic metric.

Deliberately NOT replicated, with reasons recorded at each site:
  * **Java/CodeNet → Python/JavaScript on the obtune corpus.** Their transformations
    come from a Java GUI obfuscator; ours from `src/obtune/obf/` under a semantic gate.
  * **Their "string encryption" arm maps onto our `H1`, which is quarantined**
    (CLAUDE.md §3.2) — it is never trained on and is read only under the two sanctioned
    eval passes. So this replication covers renaming (`L1b`/`L1r`/`L2`) and dead code
    (`S2`), and *adds* control-flow flattening (`S1`), which the paper does not have.
  * **Negative construction.** The paper pairs a clean original against *clean* code
    with different semantics, while every positive pairs clean against *obfuscated*
    code (§5.0.2). Under that design "is B obfuscated?" predicts the label perfectly,
    so a model can score well without any semantic comparison. `dataset.py` defaults to
    `negative_style="obfuscated_mutant"`, which obfuscates the mutated program with the
    same transform as the positive, making surface obfuscation-ness uninformative. The
    paper-literal `clean_mutant` style is kept as a config option so the confound can
    be measured rather than argued about.
  * **Readability.** They score with Scalabrino et al.'s Java readability model, which
    has no Python/JS equivalent; `metrics.readability_proxy` is an explicitly-labelled
    substitute and is never presented as the same instrument.
  * **Execution.** The paper's reverse criterion is purely syntactic (CodeBLEU +
    readability). obtune has a sandboxed executor and canonical outputs, so
    `metrics.exec_equivalence` reports whether recovered code *actually still computes
    the original's outputs*. Both criteria are reported; the paper's is what supports a
    replication claim, ours is what we would believe.

Quarantine
----------
Everything under this package reads training data through `paths.load_training_jsonl`
and writes only under `data/train/cft/`. H1 has no entry point here at all.
"""

from obtune.cft import prompts  # noqa: F401

__all__ = ["prompts"]
