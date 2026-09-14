# 2026-09-14 — The router, backwards, on its first complete model: H-router-locks REFUTED

**Thread:** modularity · **Status:** one model of five (Llama-3.1-8B); the other grids are running · **Registered rule:** `CLAUDE_SCRATCHPAD.md`, "Sharpened prediction for the mixture-backwards read", written before any mixture backward cell existed

## The rule, and the number

CONFIRMED iff `mole_router`'s collapse rate is above 0.05 and inside the single-adapter band; REFUTED
iff below 0.01, at the merge floor. **Prediction: CONFIRMED, 0.10–0.20.**

Llama-3.1-8B, 23 backward conditions, forward-collapse rate:

| `base` | `tuned_L0` | `mono_all` | `cons_lam3` | `tuned_X1` | `merge_dare_ties` | `merge_ties` | **`mole_router`** |
|---|---|---|---|---|---|---|---|
| 0.000 | 0.001 | 0.021 | 0.025 | 0.001 | 0.000 | 0.000 | **0.001** |

**REFUTED.** The router is at the merge floor, a hundred times below where I put it. My reasoning —
a saturated gate makes the router effectively one per-type adapter, so it should inherit that
adapter's locking — was wrong about what causes the locking: the per-type adapters on this model
barely lock either (`tuned_L0` 0.001, `tuned_X1` 0.001), and the arms that do are the ones trained
on the *breadth* mixture (`mono_all` 0.021, `cons_lam3` 0.025). Locking follows what the adapter
was trained on, not how many adapters are combined.

The sharper discriminator I registered — `mole_uniform` at the floor while `mole_router` is not
would mean "averaging removes the lock" — is uninformative here: **both are at the floor**
(uniform 0.000, random 0.000, router 0.001, hardened 0.001).

## Backward accuracy, the nine stacks, exact arguments, paired (n = 557 programs)

| contrast | points |
|---|---|
| router − untuned | **+0.96** [+0.09, +1.89] \* |
| uniform − untuned | **+0.89** [+0.06, +1.70] \* |
| router − uniform | +0.07 [−0.43, +0.58] |
| router − breadth | **+1.86** [+1.20, +2.53] \* |
| merge − router | **+1.16** [+0.47, +1.86] \* |

Levels: untuned 0.079, breadth 0.070, router 0.088, uniform 0.088, merge 0.100. Seen→unseen drop:
router −17.5 % against untuned −15.1 % and breadth −42.2 % — **no brittleness tax**.

## What this says, on one model

The mixture behaves like the merge and not like breadth in every backward respect: no
forward-locking, no tax on the unseen family, above the untuned model, above breadth. It is also
**below the merge** by about a point on exact arguments and six by execution, and the learned gate
is indistinguishable from a fixed uniform one (+0.07) — the same "mixing, not dispatch" result the
forward direction gave on CodeLlama-7B's held-out family this morning.

So the picture the paper has to carry is now three-way: single-adapter arms trained on the breadth
mixture lock and pay; the merge and the mixture do neither, and the merge collects more. One model.
Four grids are still running; the registered rule is applied to each as it lands, and the panel
verdict is the count.
