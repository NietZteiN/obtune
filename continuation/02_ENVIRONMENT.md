# 02 — What breaks on a new cluster, and how to fix it

Everything in this file was verified on the **old** cluster (`csr-94608.utdallas.edu`) on
2026-08-27. Work through it in order; nothing else will run until this is done.

---

## 1. Hardcoded absolute paths — 18 references across 9 files

All of the form `/data/jvl210002/...`. Find them with:

```bash
grep -rn "/data/jvl210002" configs/ src/ scripts/ Makefile
```

| file | what it points at | note |
|---|---|---|
| `configs/compute.yaml` | conda env, its `bin/python`, `HF_HOME`, `TMPDIR` | **fix first** — the scheduler reads this |
| `scripts/env.sh` | project root, conda env, `HF_HOME`, `TMPDIR` | sourced by most entry points |
| `Makefile` | conda env `bin/python` | |
| `src/obtune/gpu_alloc.py` | conda env `bin/python3.12` | used to identify this project's own processes |
| `configs/data.yaml` | **4 paths OUTSIDE `obtune/`** — `model_understanding/`, `transcoders/` | see §2 |
| `configs/sources.yaml`, `src/obtune/corpus/sources/humaneval.py` | `dataset/humaneval_js/...` | see §2 |
| `scripts/attn/run_steer_{grid,alllayers}.sh` | project root | RQ3 steering only |

**Do not blanket sed.** Two categories need different treatment: the conda/cache paths are pure
relocation, while the four `configs/data.yaml` entries are cross-project dependencies (§2).

## 2. Cross-project data dependencies — these live OUTSIDE the repo

`obtune` reads stimuli from sibling projects under `/data/jvl210002/my_downloads/`:

| needed by | path on old cluster |
|---|---|
| `configs/data.yaml` | `model_understanding/base/data/corpus/experiment_tasks/full_human_experiment_v2.json` |
| `configs/data.yaml` | `model_understanding/base/data/corpus/paper_sets/tasks_unified_50.json` |
| `configs/data.yaml` | `transcoders/data/stimuli/dataset_a/dataset_a.jsonl` |
| `configs/data.yaml` | `transcoders/data/stimuli/dataset_b/dataset_b.jsonl` |
| `configs/sources.yaml`, `corpus/sources/humaneval.py` | `dataset/humaneval_js/humaneval_x_js_full.json` |

**Copy these five files across too**, or the corpus cannot be rebuilt. They are small. If the
corpus under `data/` is transferred intact you will not need them immediately — but you will the
first time anything is regenerated, and the failure will look like a missing-source error rather
than a migration problem.

## 3. Python environment

- Env lives at `/data/jvl210002/conda_envs/obtune` (**not** in `$HOME` — small NFS on the old
  cluster; check the new cluster's quota policy before choosing a location).
- Rebuild: `env/setup_env.sh`, pinned by `env/lock-obtune.txt` (222 packages).
- Key versions: **torch 2.11 / transformers 5.14.1 / trl 1.9.2 / peft 0.20.0 / vllm 0.26.0**.
- Node: `js/node_modules` via `npm ci` from the committed lockfile. `javascript-obfuscator` is
  installed **for the `H1` generator only**.
- R analysis reuses a separate `r_analysis` env (`stats/`), currently
  `~/miniconda3/envs/r_analysis/bin/Rscript`.
- LaTeX: **tectonic**, not texlive (`/data/jvl210002/conda_envs/tex/bin/tectonic`). conda-forge
  `texlive-core` ships an empty `texmf-dist/tex/latex` and a broken `tlmgr` — this was learned the
  hard way; do not retry it. Set `XDG_CACHE_HOME` off `$HOME`.

Environment variables that must be set (old cluster had these in `~/.bashrc`, set **before** conda
init so pip/conda inherit them):

```bash
export TMPDIR=/data/.../tmp_pip
export HF_HOME=/data/.../.cache/huggingface
export TORCHINDUCTOR_CACHE_DIR=/data/.../.cache/inductor
export TRITON_CACHE_DIR=/data/.../.cache/triton
```

## 4. Compute policy — **re-read `CLAUDE.md` §1, it is cluster-specific and will be wrong**

The old cluster: single host, **4 × RTX A6000 (48 GB)**, 96 cores, ~250 GB RAM, **no SLURM**, shared
with another group. That produced a custom scheduler under `src/obtune/sched/` plus
`configs/compute.yaml`'s `scheduler_policy.allowed_gpus` / `gpu_budget`, and a set of rules that are
specific to having no scheduler:

- GPUs are selected by polling `nvidia-smi` for idle cards, pinned with `CUDA_VISIBLE_DEVICES`
  **before** importing torch.
- The worker refuses any GPU with >2 GB used or >5 % util.
- A borrower **shares the same Unix account**, so `uid` is not an ownership test — see
  `gpu_alloc.stranded_engines`, which additionally checks `ppid == 1` and process name.
- Cards were lent by editing `allowed_gpus`, never by hand-killing workers (the supervisor reclaims
  within one 300 s poll).

**If the new cluster has SLURM, most of `src/obtune/sched/` should be bypassed rather than ported.**
Decide this explicitly and record the decision in `log/setup/`. Update `CLAUDE.md` §1 and its
changelog to describe the new hardware — the charter is meant to be authoritative, and a stale §1 is
worse than none.

Feasibility numbers to re-derive on new hardware: LoRA SFT at 1.5B ≈ 2–3 h/adapter; at 7–8B, bf16 +
gradient checkpointing peaks ≈ 25–28 GB, so **one GPU per adapter**, ≈ 8–11 h each, no DeepSpeed and
no model parallelism.

## 5. Known infrastructure defects — carried over, still unfixed

From master report §7 / §8.13, all diagnosed, none blocking:

- **No orphan recovery while `pipeline.sh` is not running.** `--requeue-stale` is only invoked by
  `supervise.sh`, so a worker that dies mid-run leaves its claim in `runs/manifest/running/` forever
  and nothing notices.
- **Training loss unobservable for the first ~hour.** `worker.py` launches jobs with `stdout`
  block-buffered to file and no `PYTHONUNBUFFERED`; first loss lines appear clumped at step 200. Use
  `trainer_state.json` as the liveness check. Both are one-line fixes.
- **`build_manifest.py --eval` silently drops any system whose `arch` starts with `merge`.** A config
  mixing merge and non-merge systems queues some and drops the rest without saying so. `--rq2` is
  **not** the workaround — it *rebuilds* the standard merges and would overwrite
  `runs/adapters/.../merge_*`. Use a hand-written queue entry.
- **`train_size: 30000` never binds in the LOTO configs** (§8.12) — folds ran 22,152–23,373 rows
  against `mono_all`'s 26,841. Correction owed in its own commit.

## 6. First-run smoke test, in this order

```bash
source scripts/env.sh
python scripts/smoke_env.py                       # the gate; do this before anything else
make check                                        # manifest SHA + H1 content scan
pytest tests/test_quarantine_lint.py              # quarantine enforcement intact
python scripts/preflight.py                       # config validation
```

Then confirm the data layer survived the move by recomputing a published number from cells — pick
the RQ2 headline, which should reproduce to ≤0.02 pts:

```
merge_dare_ties − tuned_L0  on Grid A H1 (n=1214)  =  −0.66  [−1.89, +0.66]
```

Paired cluster bootstrap by `program_id`, 2,000 resamples, seed 17. If that number does not come
back, something about the transfer is wrong and nothing downstream can be trusted.

## 7. A determinism caveat that will confuse you otherwise

Re-running an *identical* eval does **not** reproduce exactly. Verified: `tuned_L0` on Grid B `H1`
with the same adapter path, prompt sha, 115 items, engine (vllm-0.26.0), sampling (T=0), commit and
GPU reads **34.8** and **33.9** on two passes, differing on 12 of 115 generations. Across a commit
boundary the spread reached **6.1 points**. Expect ~1 pt of movement on Grid B, less on Grid A
(n=1,214). **Do not treat a small mismatch after migration as a transfer failure** — check against
this band first. A determinism note is owed in `CLAUDE.md` §4 (see `03_OPEN_CORRECTIONS.md`).
