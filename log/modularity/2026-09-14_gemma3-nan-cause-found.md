# 2026-09-14 — Cause found: one non-finite gradient, and the gradient clipper spreads it to every parameter

**Thread:** modularity · **Status:** cause identified and fixed; Gemma-3 gate not yet retrained · **Follows:** [`2026-09-14_gemma3-gate-nan.md`](2026-09-14_gemma3-gate-nan.md)

## What the probe saw

`--nan-probe 140` on the real training loop, `routerlora_gemma3-12b`:

```
[nan-probe] step 82 loss 0.0701 finite=True tau[min=9.222e-01 max=1.005e+00]
[nan-probe] step 83 loss 0.0747 finite=True tau[min=nan max=nan]
[nan-probe] GATE OUTPUT non-finite at layer 0 from a FINITE input; tau=nan.
```

Three facts in two lines. The **loss was still finite**. The gate's **input hidden states were
finite**, so the base model did not overflow. And `log_tau` — a gate *parameter* — had become NaN
between one optimizer step and the next. The parameters were corrupted by the update, not by the
forward pass. That is why the loss only went visibly `nan` at step 90 in the original run: the
damage happened earlier and the printout is every ten steps.

## The mechanism, which is `clip_grad_norm_`

`torch.nn.utils.clip_grad_norm_` computes the total norm, forms
`clamp(max_norm / (total_norm + eps), max=1.0)`, and multiplies **every** gradient by it. Two steps,
both reproduced on CPU in a few lines:

| gradients | returned norm | effect |
|---|---|---|
| one `inf` among four | `inf` | coefficient is 0, so `inf × 0 = nan` — **that parameter alone** becomes NaN |
| one `nan` in any parameter | `nan` | coefficient is NaN, so **every unrelated parameter's gradient** becomes NaN |

So one bad batch produces one non-finite gradient; the clipper turns it into a NaN parameter; on the
very next step that NaN makes the total norm NaN and the clipper multiplies *all 50 gate tensors* by
it. Which is exactly what the cancelled run's checkpoint contained: all 50, not some.

**The component that is supposed to protect training from a bad batch is the one that propagates
it.** That is worth stating plainly, because `max_grad_norm: 1.0` reads like a safety net and is not
one.

## The fix

`clip_grad_norm_` returns the norm it computed, so the test costs nothing:

- if the returned norm is not finite, **zero the gradients and skip the step**. A step with a
  non-finite gradient carries no information, so nothing is lost; this is what AMP's `GradScaler`
  does, for this reason.
- skips are counted and the first three are logged, so a run that is quietly dropping steps says so.
- **50 consecutive** skips abort the run: that is divergence rather than a bad batch, and grinding to
  walltime helps no one.

Paired with the guard added earlier — three consecutive non-finite *losses* abort — a run can now
neither corrupt itself silently nor burn a card after it has.

## Scope

This is not Gemma-3-specific. Every gate on the panel trains through the same clipper; Gemma-3 is
simply the model that produced a non-finite gradient first, being the largest vocabulary at 12 B in
bf16 with gradient checkpointing. **The seven gates already trained are unaffected** — a poisoned run
would have shown NaN in its checkpoint, and CodeLlama-13B's, checked today, has zero NaN tensors of
42 with `tau` between 0.448 and 0.927.

## Verified, then released

The fix was checked before spending another twelve-hour slot, on the same deterministic step that
killed the first run (same seed, same data order, so step 83 is step 83):

```
[nan-probe] step 82 loss 0.0702 finite=True tau[min=9.250e-01 max=9.782e-01]
[mole.train] SKIPPED step 83: gradient norm nan is not finite (1 skipped so far).
[nan-probe] step 83 loss 0.1061 finite=True tau[min=9.240e-01 max=9.777e-01]
[nan-probe] step 90 loss 0.0598 finite=True tau[min=9.171e-01 max=9.759e-01]
```

**One skipped step in ninety, and training continues normally through it.** `tau` keeps its ordinary
downward drift instead of becoming NaN. The manifest is released.
