### Target Date: 2026-09-10 (CORRECTION to today's earlier entry: the h200 job cap IS binding, so packing was right and I reversed it wrongly)
- **Corrects:** [`2026-09-10_the-qos-that-did-not-exist.md`](2026-09-10_the-qos-that-did-not-exist.md),
  whose "Observations" say *"Packing was the wrong reflex once the cap lifted"* and *"With the cap
  gone it is a liability"*. **That is wrong.** Per CLAUDE.md §6, corrections go in a new dated entry
  rather than editing the original; the original stands with this entry linked from it in the index.
- **Hypotheses / what we're testing:** none; a factual correction.
- **Setup:** `scontrol show partition h200`, `sacctmgr show qos where name=juno`, and a job count
  taken when the queue was actually deep rather than when it happened to be shallow.
- **Results:**
  - **`h200` imposes `QoS=juno`, and `juno` has `MaxJobsPU=4`.** This is a partition-level cap,
    independent of the account's own QOS (`normal`). It did not "lift" when the nonexistent
    `high-throughput` QOS was removed from our submissions; those are two different things.
  - Measured with the queue deep: **4 h200 jobs running — exactly the cap — and 10 pending with
    reason `QOSMaxJobsPerUserLimit`.**
- **What worked / hypothesis verdict:** n/a.
- **Observations — how the wrong conclusion was reached, because the mechanism matters more than
  the fact:**
  - The earlier check ran when only **3** h200 jobs were running. Nothing was blocked, so nothing
    reported a QOS reason, and I read "0 jobs blocked by the cap" as "there is no cap". A cap is
    invisible until you are against it; the one moment it cannot be observed is the moment you are
    below it. The correct test was `scontrol show partition h200` — which states the QOS outright —
    not an inference from pending reasons.
  - **The consequence was real, not cosmetic.** Under a 4-job cap, four single-GPU jobs occupy four
    slots and use four GPUs; four two-GPU packs use eight. Converting the packs to singles halved
    the throughput the panel could get, and it stayed halved until the queue grew deep enough for
    the cap to become visible again.
  - The QOS fix earlier today was still correct and necessary — jobs holding the nonexistent QOS
    pended *indefinitely* rather than queuing behind a legitimate cap. Both things are true: the
    flag was wrong, **and** the partition cap is real. The earlier entry conflated them.
  - **Third instance today of one failure mode:** a checkable claim asserted from a single
    observation. The others were `submit.py`'s comment describing a QOS that does not exist, and an
    inline validation that silently never ran. All three were confident, specific, and untested.
- **New questions / new hypotheses:** none.
- **Next Steps:** long arms (`mono_all`, `cons_lam3`; 4–7 h each) repacked two per allocation —
  jobs 389092 / 389094 / 389096, each with a packed ckpt-select chained `afterok`; granite's short
  `X1` stays a single (389098). Running and completed arms were not disturbed. `pack.py`'s docstring
  already describes the trade correctly (density vs whole-node schedulability); what was wrong was
  my reading of which side of it we were on.
