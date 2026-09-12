### Target Date: 2026-09-12 (a fifth quarantine layer: H1's spent budget is now enforced, not merely declared — and testing it against the real quarantine put a row in the access log)
- **The hole.** CLAUDE.md §3.2 rule 3 allows exactly two H1 passes and the changelog records both as
  spent (pilot 09-02, repaired 09-04; final 09-05). The gate in `data.load_h1_items` enforced only
  that `purpose` is one of the two sanctioned values — **not that the budget behind them is gone**.
  **Twelve committed configs still carry `h1_access_purpose: final_eval`.** Queueing any of them
  would have read H1, appended a log row, and spent a third pass, and **every enforcement layer
  would have reported success** — the failure would have been invisible.
- **The fence.** `load_h1_items` now refuses any read after `_BUDGET_SPENT_UTC = "2026-09-05"`
  unless the caller passes `allow_after_budget_spent=True` explicitly. That keeps a genuinely
  authorised future pass possible (re-register, then pass the flag, so the decision appears in the
  diff) and makes an accidental one impossible.
- **Why a date and not a counter.** The log records **one row per CELL, not per pass** — 135 rows
  are two passes plus the generator's own writes. A counter would misread the file's granularity and
  either fire immediately or never.
- **THE MISTAKE, and it is the part worth keeping.** I verified the fence by calling it twice: once
  expecting refusal (it refused) and once with the override to prove that path still works. **The
  second call read 115 items and appended a row to `ACCESS_LOG.md`.** No model ran, no cell was
  written, no accuracy was computed, nothing selected or ranked anything — the items were loaded and
  discarded. But the row exists, and read cold it looks like a third `final_eval`.
  - The row is **annotated in place, not deleted.** The log's own header says rows are never
    deleted, and deleting it would be exactly the behaviour the log exists to prevent.
  - **I tested a quarantine gate against the real quarantine.** The refusal path was safe to
    exercise; the override path was not, and I exercised it anyway to be thorough. The test now
    asserts the refusal only and checks the override by reading the source.
  - The general form: **a safety mechanism's "allow" path must be verified without using the thing
    it protects.** That is what a fixture or an injected path is for, and neither was used here
    because the check felt small.
- **Not claimed:** that this read cost anything. It did not. What it cost is the log's readability,
  which is the artefact the whole discipline rests on, and that is why it is written up rather than
  quietly left.
- **Next Steps:** none. The four original layers are untouched; this is a fifth in front of them.
