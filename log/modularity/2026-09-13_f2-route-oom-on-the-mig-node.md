# 2026-09-13 — H-F2-route: first attempt ran a MIG slice out of memory

**Thread:** modularity · **Status:** resubmitted as 392996 · **Related:** [`2026-09-13_f1-routing-and-merging-on-stacks.md`](2026-09-13_f1-routing-and-merging-on-stacks.md)

`ev_f2_mole` 392884 landed on `g-06-01` (a 47 GB `nvidia_h100_nvl_3g` MIG slice) and died 17 min in
with `torch.OutOfMemoryError` in the first cell's forward pass (45.6 GB in use, 966 MB requested).
The seen-stack routing run (392638) had used the same `engine.batch_size: 32` on a full 95 GB card.
The X1-containing composites are the long prompts — medians 515–1130 tokens, `C_S2_X1` up to ~1800
(the calibration note in `conditions_composite.yaml`) — so batch 32 of those on half a card does not fit.

No cell was written (0 `mole_*` cells on any X1 composite, checked), so the pre-registration in
`CLAUDE_SCRATCHPAD.md` stands unchanged and nothing was read.

Resubmitted with `engine.batch_size: 16` in `configs/eval/mole_f2_codellama-7b.yaml` and
`--exclude g-06-01`. Batch size does not change a greedy result. `obtune.eval_vllm` already
auto-excludes that node; `eval_mole` submissions go through `--argv` and do not, which is the trap.
