### Target Date: 2026-09-09 (second cleanup sweep: ~10 GB from four targets, one of which had to be split rather than deleted whole)
- **Hypotheses / what we're testing:** housekeeping. The user approved deleting the four remaining
  candidates named in the storage audit.
- **Setup:** blast radius stated and approved per CLAUDE.md; each target deleted in its own narrow
  operation with its own justification, and the reference scan established in
  `2026-09-09_quota-cleanup-for-the-panel.md` re-run first.
- **Results — 10.1 GB freed; quota 965.4 → 955.2 GB, 144.8 GB free (95.5 % of soft):**

  | target | freed | note |
  |---|---:|---|
  | `migration/envs/obtune` | **7.75 GB** | the CUDA-13 venv. Verified this session: `torch 2.11.0+cu130`, `cuda available: False` on every GPU node here; `OBTUNE_ENV` defaults to `obtune-cu129`; no queued job references it; `env/setup_env.sh` replays it from a 222-pin lock |
  | `tmp_pip` | **2.16 GB** | pip cache |
  | `results/attn` raw arrays | **185 MB** | 3,600 `.npz`/`.npy`; regenerable by HF-eager extraction on a stratified subset (~4 GPU-h) |
  | `allocation_replication` | **38 MB** | preserved first (below) |

  The `du` figures quoted before the deletion (15 GB / 3.4 GB / 131 MB) were **MooseFS block
  allocation**, not bytes; the real total was ~10 GB against the ~19 GB advertised. Direction right,
  magnitude optimistic — worth remembering the next time a cleanup is costed from `du`.
- **What worked / hypothesis verdict:** n/a. Two departures from a literal "delete all", both
  deliberate:
  1. **`results/attn` was split, not removed.** `scripts/pipeline/plan.yaml` pins five files under
     `results/attn/knockout/codellama-7b/X1/*.json` as `done_when` markers for the `ko_x1_*` stages.
     Deleting them would have made `run.py` believe the knockout extractions were unrun and
     resubmit five GPU jobs — the same class of trap as the `adapters_overtrain` config pins found
     in the first sweep. Only the array dumps went; `run.py --status` still reports all five stages
     `done, outputs present`.
  2. **`allocation_replication` was preserved before deletion.** It carried uncommitted work (a
     modified `artifact/obfuscation/main.py` plus two untracked `.bak`/`.orig` files). Full history
     bundled to `~/allocation_replication_HEAD_2026-09-09.bundle` (12 MB), the diff saved as
     `~/allocation_replication_uncommitted_2026-09-09.patch`, the loose files tarred, and `HEAD`
     verified contained in `origin/main` before anything was removed. Restore: clone the bundle,
     `git apply` the patch.
- **Observations:**
  - The deletions ran while `tr_gemma3_L0` (388536) was training and nothing broke — no target was
    on a path any running job reads, which is what the reference scan is for.
  - Verified after: `obtune-cu129` still imports (`torch 2.11.0+cu129`), so removing the sibling env
    touched nothing live.
  - Everything above ~1 GB that can be deleted without a scope decision is now gone from this
    account. What remains is committed work: the other project's ~122 GB and this panel's ~25 GB
    against 144.8 GB. The next lever is a quota increase, not a deletion.
- **New questions / new hypotheses:** none.
- **Next Steps:** `scripts/preflight_panel.py` should grow a quota line (already noted in
  `2026-09-09_one-quota-two-agents.md`); the constraint is invisible to `df` and has now bitten
  once on each side of the account.
