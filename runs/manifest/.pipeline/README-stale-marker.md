# p3_mole_train.skipped — stale, renamed 2026-08-13

Written 06:26:25 when the mole dry-run hit a device mismatch in `mole/mixture.py`
("cuda:1 and cuda:0", the `device_map="auto"` sharding hazard). That bug was fixed at
06:29:02 — three minutes later — and the gate then trained successfully at 12:18:03
(11 MB, 2,766,876 gate params, 196 modules attached, see
`runs/mole/qwen25c-1.5b/python/routerlora_v1_s17/summary.json`).

The stage therefore SUCCEEDED. The `.skipped` marker survived only because nothing clears
it, and it made `pipeline.sh --status` report a completed experiment as having produced
nothing. Renamed rather than deleted so the failure stays auditable.
