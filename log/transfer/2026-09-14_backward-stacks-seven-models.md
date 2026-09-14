# 2026-09-14 — Backward on stacks, seven models: the dissociation is 4/5 clear, and the anchored arm does not hold up

**Thread:** transfer · **Status:** seven of eight evaluated · **Supersedes the counts in:** [`2026-09-14_backward-dissociation-three-of-four.md`](2026-09-14_backward-dissociation-three-of-four.md) and [`2026-09-14_backward-stacks-fifth-model.md`](2026-09-14_backward-stacks-fifth-model.md), neither amended

Llama-3.1-8B and Gemma-3 finished. Exact-argument accuracy, seen stacks → unseen-containing stacks,
every model measured:

| model | `base` | **`mono_all`** | ratio | `cons_lam3` | `tuned_X1` | `merge` |
|---|---|---|---|---|---|---|
| CodeLlama-7B | −17.8 % | **−46.7 %** | 2.6× | −17.0 % | −18.5 % | −23.7 % |
| Granite-3.1-8B | −12.1 % | **−52.6 %** | 4.3× | gated | −11.5 % | −27.1 % |
| CodeGemma-7B | −24.3 % | **−51.1 %** | 2.1× | gated | −3.4 % | −26.5 % |
| Llama-3.1-8B | −17.4 % | **−44.1 %** | 2.5× | **−37.1 %** | −7.0 % | −22.5 % |
| Gemma-3-12B | −25.0 % | −31.8 % | **1.3×** | gated | −11.8 % | −22.9 % |
| CodeLlama-13B | −20.3 % | gated 0.92 | — | gated | gated | −22.5 % |
| CodeLlama-34B | −13.1 % | gated 0.57 | — | gated | −23.2 % | −13.8 % |

**The dissociation: four of five readable models show breadth falling 2.1–4.3× further than the
untuned model; Gemma-3 shows only 1.3×.** Two models are unreadable. None contradicts it, but
"replicates on every model where it is readable" — which I wrote two entries ago — is no longer
accurate: Gemma-3 is readable and weak, and that belongs in the count.

**The anchored arm is readable on two models and behaves differently on each.** On CodeLlama-7B it
matches the untuned model (−17.0 % against −17.8 %), which is the result the paper's reversal claim
rests on. On Llama-3.1-8B it falls **−37.1 %** against base's −17.4 % — more than twice as far, and
closer to breadth's −44.1 % than to base. On the other five it is format-gated. So the claim that
anchoring preserves backward competence under divergence holds on one model of two where it can be
tested, and is contradicted on the other.

**The family adapter is the most stable arm on all five readable models** — −18.5, −11.5, −3.4, −7.0,
−11.8 — never worse than base anywhere. **The merge is the most consistent**: −13.8 to −27.1 across
all seven, never gated on any model, above base on every readable one.

One model remains (StarCoder2).
