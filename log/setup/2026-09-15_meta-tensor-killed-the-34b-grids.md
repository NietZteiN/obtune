# 2026-09-15 — The 34B mixture grids died in 60 seconds on a meta tensor, and two other submission faults

**Thread:** setup · All three found in one sweep after the queue emptied unexpectedly.

## 1. The expert bank was registered on the meta device (the real bug)

`ev_mole_codellama-34b` and `ev_moleinv_codellama-34b` both failed ~60 s in:

```
File "src/obtune/mole/mixture.py", line 106, in forward
    a = self.A_cat.to(device=x.device, dtype=x.dtype)
NotImplementedError: Cannot copy out of meta tensor; no data!
```

`MoLELinear.__init__` placed the expert bank on `base.weight.device`, with a comment explaining
(correctly) that under `device_map="auto"` the base weights are already on a GPU. What that comment
missed: when accelerate must **offload** part of a model, the offloaded layers' weights sit on the
**meta** device and are materialised by a hook immediately before the layer runs.
`bank.A_cat.to(device=meta)` therefore produced a tensor with no data — silently, at attach time —
and the job survived model loading, expert loading and the first minute of generation before dying on
the first forward through an offloaded layer.

Only the 34B is large enough for accelerate to offload here, which is why seven models never showed
it and why it appeared now: these grids had previously been killed by WALLTIME before reaching a
node where the model did not fit outright.

**Fixed** in `mixture.py`: when the base weight is on meta, resolve the layer's real device from
accelerate's hook (`_hf_hook.execution_device`) and fall back to CPU, which the forward's own
`.to(x.device)` then handles. A guard raises at attach if the bank would ever be meta again — at
attach, not an hour into a 24-hour job. Regression-tested three ways: a meta base layer, a meta base
layer with a hook, and the ordinary path unchanged.

## 2. `--argv bash script.sh` ran `python bash`

The two seed-42 checkpoint-selection jobs failed in one second with exit 2:

```
python: can't open file '/work/jvl210002/migration/obtune/bash': [Errno 2] No such file or directory
```

`--argv` runs the project python and prefixes `python` to the tokens, which is right for a module and
wrong for a shell script. SLURM reports it as a one-second FAILED, which reads like a cluster problem.
`submit.py` now omits the prefix when the first token is `bash`/`sh` or ends in `.sh`.

## 3. A cancelled grid and a batch of walltimes

`ev_moleinv_gemma3-12b` was CANCELLED by SIGTERM at 1:20:25 (not by us; no cancel was issued in this
session). Three others hit walltime again. All requeued with walltimes from their own measured rates.

## Where the panel stands

**Forward is complete on seven of eight models** and backward on four. What remains is mixture cells
only: 34B forward 10 and backward 6, Gemma-3 backward 9, CodeGemma backward 7, CodeLlama-13B
backward 4.
