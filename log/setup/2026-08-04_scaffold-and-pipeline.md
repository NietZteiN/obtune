### Target Date: 2026-08-04 (Project created — contracts, pipeline, and stack)

- **Hypotheses / what we're testing:** Setup day — no scientific hypothesis under test. The engineering
  question is whether the frozen contracts (canonical output, sandboxed execution, quarantine guard) hold
  well enough that everything built on top of them is trustworthy. Falsifiable version: *the Python and
  JavaScript canonicalizers produce byte-identical strings for equivalent values* — if they do not, the
  cross-language transfer claim in RQ1 is not comparable and the whole JS arm is compromised. The
  pre-registered hypothesis ledger for the actual science is in
  [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md) (H1a–H3, HA1); none are resolved yet.

- **Setup:**
  - Repo created at `/data/jvl210002/my_downloads/obtune/`, `git init -b main`, first commit `49864d1`.
  - Env built by [`../../env/setup_env.sh`](../../env/setup_env.sh) → `/data/jvl210002/conda_envs/obtune`
    (Python 3.12.12, torch 2.11.0+cu130, transformers 5.14.1, trl 1.9.2, peft 0.20.0, vllm 0.26.0);
    frozen to `env/lock-obtune.txt`. Node workspace `js/node_modules` via `npm install` (168 packages;
    @babel/* 7.29.x, javascript-obfuscator 5.5.0).
  - `Qwen/Qwen2.5-Coder-1.5B-Instruct` downloaded into `HF_HOME=/data/jvl210002/my_downloads/.cache/huggingface`
    (the 7B Coder and Llama-3.1-8B were already cached).
  - Seed: `GLOBAL_SEED = 17` in `src/obtune/config.py`; obfuscation retry stride 7919 in `configs/conditions.yaml`.
  - Commands run for verification: `pytest tests/`, `python scripts/00_env_check.py`,
    `python scripts/check_manifest.py`, plus direct executor smoke tests (recorded below).
  - GPUs: none used today — everything on this list is CPU-only. (Noted for later: `gpu1` became busy with
    another user's job at ~15:00, which is exactly the case `sched/worker.py`'s idle check exists for.)

- **Results:**
  - **canon parity Python ↔ JavaScript: 9/9 fixture groups byte-identical.** Rejected-value behavior matches
    on both sides (NaN, ±Infinity, set/frozenset, `undefined`, complex, bytes, >40-deep nesting).
  - **Executor, both languages:** 12/12 Python and 10/10 JavaScript fixture programs execute all cases
    successfully. Status mapping verified end-to-end: `ok`, `raised` (exception **type** only),
    `unserializable`, `timeout`. Infinite loops terminate — Python via `RLIMIT_CPU`, JavaScript via the
    `vm` watchdog.
  - **Cross-language spot check on parallel fixtures:** `fib_like(10)` → `55` in both;
    `count_chars("hello")` → `{"e":1,"h":1,"l":2,"o":1}` in both, byte-identical.
  - **Quarantine lint: 5/5.** Loader guard rejects quarantine paths, eval paths, and paths outside the
    training tree; H1-labeled rows are rejected even inside a legal training path; no `obf/h1` import exists
    outside the generator; `javascript-obfuscator` appears in no trainable-condition source file.
  - **H1-marker content scan:** a planted `atob(` in a row labeled `S1` was caught
    (`manifest verify: FAILED — 1 training row(s) containing H1 markers`), which is the case labels alone
    cannot catch.
  - **Preflight `scripts/00_env_check.py`: 45 checks, PASS.** Two warnings, neither blocking: `gpu1` busy
    (another user), and `broom.mixed` absent from the `r_analysis` R env.

- **What worked / hypothesis verdict:** The cross-language canonicalization hypothesis is **SUPPORTED** —
  but only after two real defects were found and fixed, which is the reason to have tested it rather than
  assumed it:
  1. **Float formatting diverged.** Python printed `2.0` where JavaScript printed `2`, and Python zero-padded
     exponents (`1e-07` vs `1e-7`). JS has a single number type and physically cannot make the int/float
     distinction, so the same program would have scored differently by language. Resolved by collapsing
     integral floats to plain integers in *both* canonicalizers and normalizing exponent padding. The
     int/float distinction is not load-bearing for output prediction, and `scoring.py` compares numerics
     with a tolerance anyway.
  2. **`vm`-context intrinsics broke type checks.** Object literals created inside the sandbox have that
     context's `Object`, so `value.constructor !== Object` was true for ordinary objects and every JS
     program returning a plain object was wrongly rejected as unserializable. Switched to constructor-name
     and `Object.prototype.toString` tag checks.

- **Observations:**
  - The `node` binary is not on the restricted child PATH (`/usr/bin:/bin`); it lives in miniconda. Resolving
    it once at import via `shutil.which` was necessary — without it every JS execution silently failed as
    `crash`, which would have looked like a JS-corpus problem rather than a harness bug. Any new subprocess
    path in this project needs the same treatment.
  - A spinning program killed by `RLIMIT_CPU` initially reported `crash`; now a negative return code maps to
    `timeout`. Worth keeping distinct: `crash` should mean *our harness broke*, `timeout` means *the program
    was unsuitable*, and conflating them would hide real defects behind expected corpus attrition.
  - Two design ambiguities in the v0.1 brief had to be resolved before any code could be written, and both
    are recorded in `docs/design_doc_v0.1.md` §9: what `L2` means (no legacy tier was purely
    identifier-based), and whether legacy tiers could be reused as condition codes (they could not — their
    semantics differ per language *and* per generation vintage).
  - `javascript-obfuscator`'s `deadCodeInjection` forcibly enables `stringArray`, and `stringArray` is
    default-on. Configuring it carefully per condition would have been a silent-leak generator; confining it
    architecturally to the H1 path is the only safe use.

- **New questions / new hypotheses:**
  - What is the real S1/S2 **coverage** on non-fixture programs? The flattener bails on `try`/`with`/`yield`/
    `match` by design ("correctness beats coverage"). If coverage falls below ~90 % the headline transfer
    numbers must come from the all-conditions-succeeded common subset — already the plan, but the shortfall
    has to be reported rather than smoothed.
  - Does span→token resolution still hit ~1.0 on the **Qwen2.5-Coder** tokenizers? The transcoders validation
    was on Llama-3.1-8B and Qwen3-0.6B. RQ3 hard-fails below 0.98.
  - Dataset A's Python rows carry human-formatted I/O (`outputs: "FALSE"`) and double-spaced code. Re-deriving
    canonical outputs by execution will produce disagreements; anything beyond `FALSE` vs `False` is a
    finding about the human answer key, not a formatting artifact.

- **Next Steps:**
  1. Finish the integration review of the generated modules; get the full suite green.
  2. Run the data layer end to end (test-set ingest → corpus → variants → quarantined H1), then `make check`.
  3. Pre-register H1a–H3 before the main grid; the pilot stays labeled `phase=pilot` as exploratory.
  4. Week-1 kill-switch pilot on an idle GPU; fill in the verdict box in `docs/CHECKLIST.md` §5.
