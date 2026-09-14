# 2026-09-14 — Maximising GPU use: what the idle capacity was and what it is now doing

**Thread:** setup · **Asked for by the user:** "We should maximize GPU usage" · **Status:** every idle card that can take this project's work has work queued

## Where the headroom was

| partition | state | usable for |
|---|---|---|
| h100 | saturated — five of my mixture backward grids running, seven more of mine pending | nothing to add |
| h200 | obtune holds 1 of its agreed share of 2; the sibling project holds the rest | one slot |
| a30 | two nodes, essentially idle | **CodeLlama-7B training only** — 23.5 GB holds 6.7 B and nothing larger, and cannot serve even that |

So the question "what should the idle cards do" is "what CodeLlama-7B training is worth doing", and
the answer had been sitting in `CLAUDE.md` §4 all along: **vary seeds before claiming an effect.**
Every headline number in the paper is seed 17 only.

## Queued, and why it is the right work

**Second seed, whole panel, on the paper's named model.** CodeLlama-7B already had `_s42` replicates
of L0, L1b, L1r, L2, S1, S2, breadth and the anchored objective from earlier seed-variance work. The
missing pieces for a full second-seed panel were S3, S4, X1 (a30 398390–398392), the two merges
(CPU, from the six s42 specialists that already exist, DARE's mask re-seeded — dev 398395/398396),
the router gate (config written, runs when S3/S4 land), and any evaluation of the lot (two configs,
23 conditions forward and backward, own phases, gated by the missing-adapter guard until the
adapters exist). Rules and predictions are in `CLAUDE_SCRATCHPAD.md` under H-seed42.

**The control that was never run.** A LoRA trained *on* the backward task (a30 398428). Every other
adapter is trained forwards and asked backwards, which cannot separate "forward tuning surface-fits
the forward mapping" from "inversion is a skill forward training does not reach". The training path
could not build it until today (`build_example` had no task direction), and it would have
**overwritten the breadth adapter** — `adapter_dir()` keys outputs on (conditions, rank, seed) and
this arm shares all three with `mono_all` — had it not been given its own root. Rule in the
scratchpad under H-inv-trained.

**The 13B mixture backward grid**, queued the hour its gate finished, into the free h200 slot.

## What was deliberately not done

- **The h200 share was not raised.** It is an agreement with the other project on this account;
  submit.py enforces it and it is the user's lever, not mine.
- **No 8B model was put on a30.** Every 8B model has OOM'd there; the note in the drain records
  three attempts.
- **No second seed on other models yet.** Each needs 8–10 trainings on h100/h200, which are the
  contended partitions; 7B first, because it is the model the paper names and the only one a30 can
  train.
