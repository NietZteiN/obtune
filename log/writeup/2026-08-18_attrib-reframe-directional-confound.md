### Target Date: 2026-08-18 (ATTRIB draft v4 — reframed from refutation to attribution confound)

- **Hypotheses / what we're testing:** Not an experiment. No number changed. The question was
  whether the paper is arguing for the right thing. Through v3 it read as *"CFT does not work,
  and here is an attribution lesson"*. The contribution is the reverse — a confound class, of
  which the CFT replication is one measured instance. ATTRIB is an attribution workshop, so the
  general claim is the part that belongs there and it was the part buried in future work.

- **Setup:** No GPU. `paper_bidirectional/main.tex`, `README.md`, `NUMBERS.md`. Built with
  tectonic; body verified at 6 pp after every pass.

- **The claim, as now stated.** When training pairs read both ways — obfuscate/deobfuscate,
  compile/decompile, minify/beautify, translate either way — every example is already an example
  of the opposite direction. So **any intervention that adds instances also changes which
  directions the model sees**, and direction travels with the method. It is easy to miss because
  the controls a careful reader asks for do not catch it: instance counts, token counts, optimizer
  steps and compute can all be matched exactly while directional content differs. That is the
  confound. CFT-on-obfuscation is where we measured it, and there it accounts for the published
  effect entirely (objective −0.2 pp [−0.7,+0.3], direction +30.9).

- **Results — what changed:**
  1. **Title** → *The Free Flip: When Training Pairs Read Both Ways, Direction Confounds
     Attribution*. Handle kept for continuity with the drafts, logs and repo.
  2. **Abstract** leads with the class and why it hides, then the instance, then the test.
  3. **§1** restructured: *A confound that paired data carries* → the obfuscation instance → the
     phenomenon → CFT as "the confound in its natural habitat" → **the general test**, which
     replaced the old contributions paragraph.
  4. **The general test**, now the contribution rather than a summary: *for any method that adds
     instances to paired training data, train the arm that supplies the same directional content
     and none of the method.* What makes it more than advice is that the ablation arm is also the
     remedy, so running it pays for itself either way.
  5. **Section headers** reframed from verdicts to mechanisms ("With direction held fixed, the
     objective contributes nothing and the direction everything"; "The cheap arm is also the fix").
  6. **Conclusion** leads with the class and bounds it explicitly — we do *not* claim every
     auxiliary-task result on paired data is a directional artifact.
  7. **Tone.** Two sentences are load-bearing and deliberate: "that is not careless, it is what
     almost any auxiliary-task method looks like", and the conclusion's explicit non-claim. They
     matter both for the reframe and because Nikiema et al. may review this.

- **Observations:**
  - **The page fight was won by finding repetition, not by cutting content.** The reframe ran
    **11 lines over**. Two compression passes on the new prose recovered ~8. The last 3 came from
    noticing that "reading a pair backwards is already a reverse example" was stated **three
    times** in §1 — in the opening, the habitat paragraph and the test paragraph. That is the same
    lesson as the v3 round, where the last 11 lines came from moving a table rather than deleting
    an argument. Look for your own restatement first; it is cheaper than anything else and it
    improves the prose.
  - **The old contributions paragraph was replaced, not cut.** Worth recording, because the page
    budget pre-authorisation for cutting it was thereby spent on new content rather than banked.
  - **Three prose colons slipped in** with the new text, two in the body and one in an appendix
    framing sentence added the same day. The house rule at `main.tex:4` bans them outside the
    title. A `grep -cE '^[^%]*[a-z]: [a-z]'` catches them and is worth keeping in the pre-submit
    sweep alongside the non-ASCII check.
  - Final layout is the tidiest it has been: body fills p1–6 exactly, references begin at the top
    of p7, appendices A–O to p13. 0 errors, 0 undefined refs, 0 non-ASCII, 0 overfull hboxes.

- **Next steps:**
  - Submission mechanics remain the only substantive item: venue style, anonymisation, OpenReview.
  - Still unresolved and worth one email: whether ATTRIB counts references toward the 6 pages.
    The call is silent; we assume the NeurIPS convention that they are excluded.
  - The reframe raises the value of a second instance. Any invertible pair with a published
    auxiliary-task result would do, and none is in scope before the freeze.
