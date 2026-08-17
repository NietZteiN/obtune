# 2026-08-09 — CFT does not reproduce at 7 B, and the scheduler was killing its own jobs

*Thread: `cft-replication`. Previous: [`2026-08-08_srh-exp1-plumbing.md`](2026-08-08_srh-exp1-plumbing.md).*

## Goal / hypothesis

Two things, one scientific and one operational.

1. **Scientific.** The 1.5 B kill-gate (yesterday) found CFT indistinguishable from
   forward-only SFT and both *below* the untouched base model, while the free
   direction-swap (`flip`/`mix50`) reached ~31 %. The obvious objection is scale: the paper
   used 7–15 B and says its method only works at the larger sizes. So: run the paper's own
   model, **Qwen2.5-Coder-7B**, which it reports at 39.00 % (Fig. 4). Does CFT recover?
2. **Operational.** Make the whole remaining programme run unattended, and — after three
   separate "is it running smoothly" checks each surfaced a real defect — audit what is
   about to run rather than assume it is correct.

## Setup

- Host `csr-94608`, 4 × A6000. GPUs 0–3, all four in use.
- Seed 17 throughout. Env `/data/jvl210002/conda_envs/obtune`.
- 7 B eval: `python -m obtune.cft.evaluate --config srh/eval/e1_qwen7b.yaml`
  → `results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b/`
  (300 test-split programs × 5 conditions × 4 strategies × 2 directions = 22,500 generations).
- Report: `python scripts/cft/12_report.py <that dir>`.
- Unattended stack: `scripts/pipeline.sh` (5 stages, markers under
  `runs/manifest/.pipeline/`), `scripts/supervise.sh`, `scripts/launch_workers.sh`.
- New: `scripts/preflight.py`, wired as a gate at pipeline start and before each stage that
  enqueues work.

## Results

### Reverse success, paper's own criterion, Qwen2.5-Coder-7B

| system | `simple` | `few_shot` | `cot` | `augmented` |
|---|---|---|---|---|
| `base` — untouched | 23.6 % | 32.7 % | 34.7 % | **38.7 %** [35.9, 41.5] |
| `sft` — forward only | 0.3 % [0.1, 0.7] | 6.8 % | 11.0 % | 12.5 % |
| `cft` — contrastive | 0.2 % | 1.9 % | 3.0 % | 2.6 % |

Pooled over strategies, **`cft` − `sft` = −5.7 pts [−6.4, −5.0]**.

Forward direction is healthy in both tuned arms — `sft` 97.2 % exec-parity, `cft` 97.5 %,
`base` 92.6 % — so this is not a broken adapter. `assert_adapters_effective` reports 1.7–1.8 %
identical-to-base outputs for both.

### By condition (reverse, paper criterion)

| system | `L1b` | `L1r` | `L2` | `S1` | `S2` |
|---|---|---|---|---|---|
| `base` | 10.5 % | 28.7 % | 29.2 % | 71.8 % | 21.8 % |
| `sft` | 0.1 % | 3.5 % | 4.1 % | 25.1 % | 5.5 % |
| `cft` | 0.0 % | 1.3 % | 0.8 % | 7.2 % | 0.3 % |

## Observations

**1. The refutation holds at the paper's own scale.** CFT never exceeds 3.0 % against a
reported 39.00 %, and is *significantly worse* than the SFT it is meant to repair. The 1.5 B
result was not a small-model artifact.

**2. The paper's "0 %" is substantially a prompt effect.** The same `sft` adapter scores
0.3 % under `simple` and 12.5 % under `augmented` — a 40× swing from instruction wording
alone. Reporting the `simple` number as a property of the model overstates the phenomenon.

**3. The untouched base model matches the paper's headline.** `base` scores 38.7 % under
`augmented`, indistinguishable from the 39.00 % attributed to CFT. **The paper reports no
untouched baseline.** Without one there is no way to tell a number the method produced from
a number the model already had. This is now the strongest single criticism in the writeup —
stronger than the budget argument, because it needs no accounting, only the missing row.

**4. `exec` alone inverts the ranking, exactly as designed for.** `cft` is the *best* system
by execution equivalence (91.7 % vs base 80.9 %) and the worst by everything requiring the
output to be deobfuscated. Identity rate reaches 43–90 % in `cft`'s `cot`/`simple` reverse
cells: it echoes its input, which is trivially execution-equivalent and is not a
deobfuscation. Same failure the paper describes for SFT (§4.3.3) — but CFT shows it *more*.
Retaining `strict = exec AND paper` as the headline was load-bearing; `exec` alone would
have produced the opposite conclusion.

**5. `S1` is where all the reverse signal lives** (base 71.8 %, vs 10.5 % on `L1b`).
Control-flow flattening is mechanically invertible; adversarial renaming destroys
information that cannot be recovered. Consistent with the ill-posed-inverse caveat in the
plan, and it means a single pooled reverse number is dominated by transformation mix.

### Operational — four defects found, three of them ours breaking our own jobs

**a. The supervisor was SIGTERMing workers that were mid-job.** `gpu_alloc.survey` decided
GPU ownership from the process command line. vLLM calls `setproctitle`, so the engine-core
process holding the GPU during *our own* evaluation is titled `VLLM::EngineCore_DP0` with no
obtune marker — the card read as `theirs`, and the supervisor "retired our idle worker
there". Confirmed in `vllm/utils/system_utils.py:198` and in the 17:16 supervisor log line
against the gpu0 worker log showing an eval in flight. Fixed: ownership now resolves by
**process ancestry** plus `/proc/<pid>/exe`, with `VLLM::` accepted only under our own uid.

A second, independent weakness surfaced while testing: `argv[0]` is whatever was typed, so a
process launched as bare `python -m pytest` carries no marker at all. `/proc/<pid>/exe`
resolves to the conda prefix regardless of invocation and is now the load-bearing check.

**b. A killed worker's claim was unrecoverable.** The claim stayed in `running/<tag>/`, and
the sweeper requeued only when *no* worker held the tag — but a replacement worker had been
started on gpu0, so the claim was stranded permanently. `queue_busy` counts `running/`, so
`drain` would have waited **forever**: the pipeline would have hung silently rather than
failed. `os.rename` preserves mtime, so there was no timestamp to fall back on either.
Fixed: `_claim` now stamps `_owner` (pid, tag, host, time) and `worker.is_orphaned` requeues
only claims whose owning process is provably dead. The one stranded job was requeued by hand
after verifying no process was running it.

**c. `--requeue-stale` ignored `--gpu-tag`** — introduced by me while fixing (b), and it
would have requeued all four live claims and double-launched three training jobs onto busy
GPUs. Caught before it ran; now scoped, with a test.

**d. Two eval configs resolved to one results directory**, and the 7 B run destroyed the
1.5 B `trials.jsonl` (21,000 rows). The 1.5 B summary survives, so §5 of the report stands,
but it is not currently re-derivable from raw trials; the eval is re-queued. Output paths now
carry model and run tag, and preflight fails any collision.

**Editing a running bash script is itself a hazard** — bash reads by byte offset, and the
orchestrators were live while I changed them. Both were restarted cleanly; workers are
`setsid` sessions and kept their jobs.

## Next steps

- Land the 7 B `rev`/`flip` arms (training on gpu1) and re-run the 7 B eval, so the positive
  half of the argument — the free swap supplies what CFT does not — is established at the
  paper's scale and not only at 1.5 B.
- Re-run the 1.5 B evaluation (queued) to restore reproducible per-trial data for §5.
- Seed 42 replicates for `rev`/`flip`/`mix50` before any effect claim goes in the writeup.
- Add the untouched-baseline argument to `docs/RELATED_WORK.md` — it is the sharpest
  criticism and currently lives only in the report.
- Finish the S3/S4 adapters (pipeline stage 3) and extend the transfer matrix.
