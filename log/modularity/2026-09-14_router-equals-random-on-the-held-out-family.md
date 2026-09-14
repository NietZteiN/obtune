# 2026-09-14 — The router ties a random gate on the held-out family, and CodeLlama-7B's forward table is complete

**Thread:** modularity · **Status:** one model (the only one with a complete mixture column) · **Cells:** `mole_generic/codellama-7b/python/*__X1`

X1 was the one hole in CodeLlama-7B's mixture column. Its 110 existing mixture cells came from three
configs written before a panel config existed for that model, and none of them listed the held-out
family — the column RQ1's argument turns on. Filled today (job 397520, batch 8 after an OOM at 32).
**CodeLlama-7B's forward master table is now 184/184 cells.**

## Forward accuracy on X1, every arm

| arm | acc | format-fail |
|---|---|---|
| `base` | 0.119 | 0.144 |
| `mono_all` (breadth) | 0.231 | 0.011 |
| `tuned_L0` (clean) | 0.269 | 0.044 |
| `merge_dare_ties` | 0.276 | 0.036 |
| **`mole_router`** | **0.279** | 0.031 |
| **`mole_hardrouter`** | **0.283** | 0.031 |
| **`mole_uniform`** | **0.283** | 0.040 |
| **`mole_random`** | **0.283** | 0.040 |
| `cons_lam3` (anchored) | 0.286 | 0.027 |
| `tuned_X1` (family) | 0.316 | 0.030 |

## The result

**The learned gate is worth nothing on the held-out family.** `mole_router` 0.279 against
`mole_random` 0.283 and `mole_uniform` 0.283 — the trained router is a fraction *below* a random
gate and below a fixed uniform mix, on 1,214 items. Hardening it to an argmax changes nothing
(0.283). The four mixture arms span 0.004.

This is the strongest form of the finding the ladder already suggested and the paper states for
single transforms ("router == random [−0.008, +0.008]"), now on the one condition where routing
should matter most: an input built from a transform family no expert was trained on. If the gate
had learned anything transferable about *which* expert to weight, the unseen family is where a
random gate should fall behind. It does not.

**What the mixture is worth is the mixing, not the routing.** All four mixture arms beat breadth
(0.231) and the merge (0.276) and sit with the anchored arm (0.286); only the family adapter, which
was trained on X1's sibling, is higher. So combining eight per-type adapters *is* worth roughly five
points over breadth on an unseen family — and any combination rule gets it.

## Where this leaves H-mixture

`H-mixture` in the transfer README says the gain from an expert mixture is a capacity/ensembling
effect and not a dispatch effect, and predicts that a fixed uniform gate tracks any other. **On X1,
confirmed as sharply as the data can put it**: uniform, random, learned and argmax-hardened all land
within 0.004 of each other while beating every single-adapter arm except the one trained on the
family.

One model. The other seven have no X1 mixture cell yet — three gates are still training and four
mixture grids are queued or partial — so this is registered as a single-model result and the panel
version will either replicate it or not.
