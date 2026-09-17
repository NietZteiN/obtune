# 2026-09-17 — Proactive debug pass: four chains checked before they could fail, one design choice made visible

**Thread:** setup · **Prompted by:** user, "debug and keep running, do a proactive debug pass".

The pattern of the last three days: a chain stops silently — a bad exit code, a missing `best/`, an
adapter that was never trained — and nobody sees it until they look. This pass looked first.

## Found and fixed

| what | how it would have failed | fix |
|---|---|---|
| Llama seed-42 evals name `cons_lam3_s42`, never trained for Llama | `FileNotFoundError` 3 min in (it already had, twice) | anchored s42 training submitted (409819); evals re-chained behind it |
| Granite seed-42 has selection + merges but **no eval configs** and no evals queued | the chain would have ended silently at the merges | `seed42_granite31-8b.yaml` + inverse written, listing only arms Granite has at s42; both evals submitted |
| invtrained selections at "Priority" on congested h100 while the h200 pool sat at 0 of 4 | hours of avoidable wait | moved to h200 |
| `ckpt_select_batch.sh` never covered `runs/adapters_inverse/` | already failed once; would again on Llama | script now covers that root |

## The tool this pass produced

`scripts/ops/preflight_eval.py` resolves every `adapter:` an eval config names and checks that
`adapter_model.safetensors` exists — distinguishing "directory missing", "has checkpoints but no
best/, run ckpt-select", and "no weights". It touches no GPU. Run across every `seed42_*` and
`invtrained_*` config it reported exactly the two live faults above and nothing else. **It should run
before every eval submission**; four allocations this week were spent discovering what it reports in
a second.

## A design choice that was implicit and is now stated

The seed-42 anchored arm uses the **seed-17 clean-code teacher**. `obj_cons_*_py.yaml` hardcodes
`teacher_adapter: .../L0_r32_s17/best`, `objectives.py` has no `--teacher` override, and the
CodeLlama-7B s42 run's manifest confirms it used the s17 teacher. The Llama s42 run submitted today
does the same. This is **consistent across the two models**, which is what the comparison needs, and it
is defensible — the second seed varies the student's initialisation and data order while the teacher
is a fixed reference — but it is a choice a reviewer will ask about and it must be in the method, not
in a manifest. Registered in `CLAUDE_SCRATCHPAD.md` under H-seed42.

## Verified clean

Granite s42 merges at the path the evals read; `/work` at 41 %; no orphaned training processes on the
login node; the one `DependencyNeverSatisfied` in the queue belongs to the sibling project; CodeLlama-7B
seed-42 landed complete in both directions (161 + 161 cells).

## Not done, deliberately

`runs/probe/drain_queue.sh` still says "share of 2" in a comment; the enforced value is
`compute.yaml`'s 4. It is a running `while true` loop that never re-reads itself, and editing a script
under a live shell is how yesterday's batch died. Fix it at the next restart, not now.
