# 2026-09-13 — The mixture guard refused the mixture engine

**Thread:** modularity · **Status:** fixed, chain resubmitted · **Related:** [`2026-09-12_routing-cells-were-the-base-model.md`](2026-09-12_routing-cells-were-the-base-model.md)

## What happened

`ev_f1_mole` (job 392173, the resubmission of the F1 routing/merging evaluation through
`obtune.mole.eval_mole` after the 09-12 finding that vLLM had written the base model under the
routing arms' names) failed 84 s in, after writing one cell (`base__C_L1b_S1`, acc 0.141):

```
ValueError: system 'mole_uniform': arch='mole_uniform' is a mixture architecture and this
engine (vLLM) does not implement one ... Use `python -m obtune.mole.eval_mole` instead.
```

That is the guard I added on 09-12 — raised from inside `eval_mole`, the entry point the message
recommends. `eval_mole` reuses `eval_vllm.run_cell` with its own `HFEngine`, and the guard keyed
on the **arch alone**, so it refused every engine, including the one engine that implements
mixtures. The chained `an_f1` (392174) went to `DependencyNeverSatisfied` and sat in the queue;
the monitor's status line reported it as pending.

## Fix

The check is on the engine. `eval_vllm.Engine.supports_mixture = False`,
`eval_mole.HFEngine.supports_mixture = True`, and `run_cell` calls
`assert_engine_implements(engine, system)`, which raises only for a `mole_*` arch on an engine
without the attribute. `tests/test_mixture_guard.py` pins both directions (vLLM refuses, HFEngine
is allowed, HFEngine declares the path, non-mixture arches pass everywhere).

The 09-12 protection is intact: a `mole_*` system submitted through `obtune.eval_vllm` still
raises before generation.

## Resubmission

`ev_f1_mole` → 392638 (h100, resume on, the one written cell is kept). The chained `an_f1` was
refused on `dev` with "Requested node configuration is not available" (8 cpu / 64 GB, which the
same partition accepted on 09-12) and went to `normal` instead. Two mis-named `adhoc` submissions
in between were cancelled unstarted: `submit.py --argv` is `REMAINDER`, so `--name` must precede it.

## Not affected

No result. The one cell written before the failure is the untuned model on `C_L1b_S1` and matches
the `composite_generic` cell (0.141).
