### Target Date: 2026-09-09 (the quota is shared and two agents are managing it blind to each other — my cleanup shows up in the other project's log as an unexplained event)
- **Hypotheses / what we're testing:** none; an operational finding recorded because the next person
  to plan a large batch on juno needs it and it is not in `CLAUDE.md`.
- **Setup:** found while answering "what can we delete outside obtune and transcoders" —
  `/work/jvl210002/migration/transcoders/log/nla-harness/2026-09-09_quota-exhaustion-l18.md`, written
  by the other sub-project on this account the same day.
- **Results:**
  - **`/work/jvl210002` carries a per-user quota of 1,000 GB soft / 1,100 GB hard that is shared by
    every project on this account, and `df` does not show it.** The other project's own debug pass
    recorded "Disk fine: `/work` has 101 T free" from `df` and missed the binding constraint
    entirely; its rule going forward is `mfsgetquota <project root>`, never `df`. obtune's charter
    has the same gap — `CLAUDE.md` §2 describes the storage layout and says nothing about a quota.
  - **The other project hit the hard quota today.** Array `384655` tasks 18/19/20 died with
    `SafetensorError: ... Disk quota exceeded (os error 122)` after 68 minutes of training each,
    at 99.97 % of 1.1 TB with ~380 MB of headroom.
  - **Two of the events its log lists as unexplained were mine.**
    It records `models--Qwen--Qwen2.5-Coder-1.5B-Instruct` present at ~20:25Z and gone at ~20:35Z,
    and the held obtune job `dl_sc2` "released by something other than me", concluding that
    `hf_home` is "a shared cache mutated by other sub-projects concurrently — treat its contents as
    not exclusively ours". Both were this session: the barred-model deletion in
    `2026-09-09_quota-cleanup-for-the-panel.md` and the `scontrol release` of the download chain.
    Neither was wrong, and both were human-approved on this side; the point is that **approval
    inside one project is invisible to the other**.
  - Independent convergence worth noting: that project's recovery list and mine named the *same*
    six Qwen/DeepSeek caches (47.4 GB) as unreferenced dead weight, from opposite directions. It
    has since executed that deletion plus 34 GB of `acts/` and 34 GB of `results/sweeps`; the
    counter moved 998 → 948 GB while this session was writing.
  - **What is left outside obtune and transcoders is now ~19 GB:** `migration/envs/obtune` (15 GB —
    verified `torch 2.11.0+cu130`, `cuda available: False`, the env `CLAUDE.md` §2 records as
    working on no GPU node here, rebuildable by `env/setup_env.sh` replaying the committed lock) and
    `tmp_pip` (3.4 GB). All 16 models remaining in `hf_home` are referenced by some project's
    configs or source; all three `conda_envs` are referenced by transcoders (18/6/3 hits).
- **What worked / hypothesis verdict:** n/a.
- **Observations:**
  - The arithmetic that matters is not the deletion list. The other project has **~122 GB of
    committed work** (9 layers × ~13.6 GB, with L27–L33 deliberately held so a second hit cannot
    happen) against **~152 GB free**, and obtune's five-model panel needs ~25 GB of adapters. The
    two fit only if nothing else lands. **A quota increase is the only action that changes this;
    every deletion available to either side is now small relative to the demand.**
  - A cross-project convention would be cheap and is not proposed lightly: neither agent can see the
    other's approvals, so a shared note — who is writing, how much is committed, what was deleted —
    is the only thing that would have made either of today's "unexplained" events legible. Recording
    the need; not inventing the mechanism unilaterally, since it would bind a project this charter
    does not govern.
- **New questions / new hypotheses:** none.
- **Next Steps:** ask the user about the 19 GB and about requesting a quota increase. Add a quota
  line to `scripts/preflight_panel.py` so the constraint is visible before a batch is submitted
  rather than after it fails — the check that would have caught this on both sides.
