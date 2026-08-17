# 2026-08-13 — `mole_random` is inert: the RouterLoRA control never randomised

*Thread: modularity (RQ2). Found while writing `paper_modularity/main.tex` from result files.
Companion entry: [`../writeup/2026-08-13_fse-modularity-draft-v0.1.md`](../writeup/2026-08-13_fse-modularity-draft-v0.1.md).*

## Goal / hypothesis

Not an experiment. The task was to draft the RQ2 paper from result files rather than from
`docs/MASTER_REPORT_2026-08-12.md`, per the convention that caught three discrepancies in the
ATTRIB draft. The first pass over the mixture ladder's numbers surfaced this.

`mole_random` is the arm designated — in `configs/eval/mole_ladder_qwen1.5b.yaml`, in
`src/obtune/mole/gate.py`'s docstring, and in this thread's own next-steps — as **the control
that decides what the headline may say**: if `mole_router ≈ mole_random`, the gain is
rank-256 residency rather than routing.

## Setup

Commit: working tree at time of writing. **No GPU consumed** — the diagnosis is CPU-only and
reads existing cells. Env `/data/jvl210002/conda_envs/obtune`.

Cells examined: the 30 cells of `experiment_id == rq2_mole_ladder`
(`results/cells/main/qwen25c-1.5b/python/mole_*`, written 2026-08-13T17:22–17:26 UTC).

## Results

**1. `mole_random` and `mole_uniform` are bit-identical.** Over all 1,299 shared items across
the eight evaluated conditions: **0 disagreements** in the `correct` vector, identical
`format_fail` rates, and identical raw generated strings on inspection.

| condition | `mole_uniform` | `mole_random` | `mole_router` |
|---|---|---|---|
| `C_L1r_S1` | .367 | .367 | .407 |
| `C_S1_L1r` | .413 | .413 | .420 |
| `C_L1b_S1` | .393 | .393 | .420 |
| `C_L2_S4`  | .466 | .466 | .540 |
| `C_L1r_S3` | .443 | .443 | .460 |
| `C_S4_S3`  | .449 | .449 | .477 |
| `L1r`      | .506 | .506 | .511 |
| `S1`       | .441 | .441 | .476 |

This is not near-uniform softmax at random init. It is the same gate.

**2. Root cause — an ordering dependency in `_load_gate`.** `eval_mole._load_gate` implements
the arm as

```python
elif mode == "mole_random":
    torch.manual_seed(seed)
    for p_ in holder.gate.parameters():
        if p_.dim() > 1:
            torch.nn.init.normal_(p_, std=0.02)
```

The ladder's `systems:` list runs `base → mole_uniform → mole_random → mole_router`.
`mole_uniform` **replaces** `holder.gate` with a `ConstantGate`, whose routing vector `w` is a
registered *buffer*, not a parameter. So by the time `mole_random` runs, `holder.gate` is a
`ConstantGate`, `.parameters()` yields nothing, the loop body never executes, and the uniform
gate survives into the arm meant to randomise it.

Confirmed directly, no GPU:

```
ConstantGate n_parameters: 0
buffers: ['w']
weights after the mole_random re-init loop: [0.125]*8
```

**3. The neighbouring branch already guards against this.** `mode == "mole_router"` restores
`holder._router_gate` before loading, with a comment stating that arms must not depend on the
order they run in — written after that exact failure. The control branch was not given the
same guard.

**4. What this does and does not invalidate.** `mole_router` vs `mole_uniform` is a valid
contrast and is unaffected: +0.6 to +7.4 points, positive on 8/8 conditions, pooled
**+3.3 [−0.4, +7.5]** over the six composites and **+2.9 [−0.0, +6.2]**, p=0.059, over all
eight (cluster bootstrap by program, 2000 draws, seed 17; no cell survives BH-FDR). What is
lost is the **residency question** — routing versus simply having eight experts resident at
effective rank 256 — which is exactly what `mole_random` existed to answer.

Per the pre-registered rule, **no mixture headline is available until this is re-run.**

## Observations

- The defect is the same shape as every prior bug in this project: **a code path that does not
  encode what actually varies.** Here the arm identifier said "random" while the installed
  module was whatever the previous arm left behind.
- It is also the same shape as the two defects caught on 2026-08-11 *before* GPU time — and
  this one got through because the ladder was verified with `--stub`, which exercises the
  arms independently rather than in sequence. Mechanical verification cannot catch a component
  that works perfectly in the wrong order.
- `buffers are not parameters` is the specific trap. Any future "freeze at init" control should
  assert its own effect rather than assume the loop ran.
- Cheap to fix and cheap to re-run: one evaluation pass over 8 conditions, no retraining.

## Next steps

- **Fix:** stash the freshly-built `RouterGate` as `holder._router_gate` (already done for
  `mole_router`) and have `mole_random` restore *that* before re-initialising — or build a
  fresh `RouterGate` for the arm. Then assert non-inertness: the arm must fail loudly if its
  routing weights come out uniform.
- **Pin:** a test that runs the ladder's arms *in configured order* and asserts
  `mole_random` ≠ `mole_uniform` on a handful of items. A test that installs each arm in
  isolation would have passed throughout.
- **Re-run** `p3_mole_eval` for the `mole_random` arm only, then update
  `paper_modularity/main.tex` §7 and resolve `CLAIM_LADDER.md` Branch A vs B.
- **Audit the same hazard elsewhere:** any other place a `ConstantGate` (or another
  buffer-only module) is installed before a parameter-mutating arm.
