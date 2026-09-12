# Reorganising the paper: from a method survey to a diagnosis

*Written 2026-09-12, in response to: "other methods that don't work are baselines that don't work
because not robust… I don't want it to be like 'here are methods we tried, this one works' and more
motivation leading to it."*

## The problem with the current shape

RQ1 asks *does composition work*, RQ2 asks *what is learned*, RQ3 introduces the objective, RQ4 asks
*is it robust*. Read in order that is a survey: three things fail, a fourth is proposed, then it is
stress-tested. The objective arrives because it is next, not because anything demanded it.

## The proposed shape: one diagnosis, two tests, applied twice

**The spine is memorisation versus generalisation**, and it is measured the same way in both halves
of the paper. Two tests, both asking *does the competence survive leaving the distribution it was
fit to?*

1. **Composition.** Does it survive being stacked with a transform family the model has never seen?
2. **Reversal.** Does it survive the task being run backwards — given a return value, produce a call
   that yields it?

§3 runs both tests on **the field's existing answers**, which fail both. §6 runs **the same two
tests** on the anchored model. The symmetry is what turns a survey into an argument: the method is
not "the one that worked", it is the one that changes the outcome of a diagnostic we had already
committed to.

| section | question | role |
|---|---|---|
| §1 | Adaptation gains 18 points. Understanding, or memorisation? | the hook |
| §2 | Setup, the condition ladder, the held-out family | |
| **§3 (RQ1)** | **Do existing adaptation methods generalise?** | **diagnosis — routing, merging and breadth are BASELINES, not attempts** |
| **§4 (RQ2)** | **What exactly is memorised?** | **mechanism — and it names what to anchor to** |
| **§5 (RQ3)** | **Anchoring to clean-code behaviour** | **the method, derived from §4 rather than proposed** |
| **§6 (RQ4)** | **Does the anchored model generalise?** | **the same two tests from §3, re-run** |
| §7–8 | Threats, related work | |

## What goes where

### §3 — the baselines fail, and they fail the same way

Routing, weight merging and training breadth are the field's existing answers, and the section
treats them as such rather than as things we tried.

- **Composition test.** Breadth's advantage is **+2.7 to +5.3 points larger** on stacks built from
  seen transforms than on stacks containing an unseen family — significant on **6 of 6 models across
  four lineages** (`tables/rq1_dissociation`). Routing beats a *random* gate by **+0.0000**; merging
  lands at or below the clean-code control.
- **Reversal test.** Every one of them buys forward accuracy with backward loss. The direction
  ratio — inverse gain over forward gain, both against the untuned model — is **negative for every
  SFT arm**:

  | arm | forward gain | backward gain | direction ratio |
  |---|---:|---:|---:|
  | format-only control | $+1.8$ | $-0.5$ | $-0.24$ |
  | clean-code tuning | $+18.2$ | $-1.9$ | $-0.09$ |
  | breadth | $+18.9$ | $-1.3$ | $-0.07$ |

- **Verdict.** What is acquired is competence at *this task on these surfaces*, not at reading the
  program. Both tests agree, and they share no machinery.

### §4 — what is memorised, and therefore what to anchor to

The mechanism section, and it must end by *naming the fix*:

- gains track **identifier surface**: breadth's stack advantage is **+3.39** larger when the stack
  contains an identifier transform, and **+5.85** out of sample on a rule fixed beforehand
  (`tables/rq2_identifier`);
- the held-out family splits into two mechanisms that **do not transfer to each other**, yet either
  alone recovers ~90 % of the family gain — not additive, so not two skills;
- breadth **polarises rather than degrades**: more confident when right, twice as far when wrong.

**The pointed close:** adaptation anchors on the surface a transform leaves behind. So anchor it to
something the transform *cannot change* — the model's own behaviour on the unobfuscated parent of
the same program. §5 is then a consequence, not a proposal.

### §5 — the method

Unchanged in content. One framing change: it opens by *deriving* the objective from §4's last
sentence, and the teacher ablation moves up, because "the unseen-family number is distilled from a
clean-code-tuned teacher" is the claim that makes the mechanism story concrete.

Panel results go here (`tables/rq3_panel`), **with the qualifier**: the repair holds on 6 of 8 models
and reverses on one.

### §6 — the same two tests, re-run

- **Composition.** On stacks containing an unseen family, anchoring is **above** the clean-code
  control ($+2.13$ at d2, $+3.26$ at d3) and **above breadth** ($+3.84$, $+3.60$) — where on *seen*
  stacks it merely matches breadth (`tables/rq4_ladder`, `tables/rq4_by_model`). Its advantage
  appears only once the input leaves what breadth was trained on.
- **Reversal.** Anchoring's direction ratio is **$+0.03$** against every SFT arm's negative, and it
  is the only arm in the SFT family not damaged backwards.
- **The bound, stated here rather than extracted by a reviewer.**

## Two places the proposed narrative outruns the evidence

**1. "This new method has bidirectional reasoning" is not supported.** Anchoring backwards is
$+0.49$ [$-1.38$, $+2.30$] against the untuned model — **undamaged, not improved**. Its direction
ratio is $+0.03$, which is zero, not positive. The defensible claim is: *every existing adaptation
method pays backward competence for forward accuracy, and anchoring is the first that does not.*
That is still a strong, novel claim, and it is the one the data carries.

**2. "This new method leads to generalisation" needs its scope.** It generalises on **composed**
novel input — above the clean-code control on stacks containing an unseen family. On the unseen
family **alone** it merely equals that control. And the repair itself is model-dependent: 6 of 8,
reversed on one. The honest headline is *composition-level generalisation, conditional on the model*.

**A finding the reorganisation surfaces that the current draft buries.** The arm trained on the
held-out family's sibling has the **only positive direction ratio in the panel** ($+0.10$), and is
the only forward training that beats the untuned model backwards ($+3.37$ on its own family).
Exposure to a *family* transfers in a way exposure to *transforms* does not. That is direct support
for the memorisation story and it currently appears nowhere in the argument.

## What this costs

No new experiments. Every number above exists. The work is:

1. rewrite §3 to lead with the two tests and demote routing/merging/breadth to baselines;
2. add the direction-ratio table (new, from existing cells) — it is the spine of both §3 and §6;
3. move the teacher ablation up within §5 and add the panel qualifier;
4. rewrite §6 as a re-run of §3's tests rather than a stress-test list;
5. add the family-training direction-ratio result to §4.
