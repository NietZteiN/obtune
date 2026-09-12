### Target Date: 2026-09-11 (verifying the "no published cell is affected" claim — the config scan was the wrong instrument; the cell scan is the right one, and it says zero of 3,062)
- **Corrects the method, not the conclusion, of**
  [`2026-09-11_missing-adapter-was-silent.md`](2026-09-11_missing-adapter-was-silent.md), which
  closed with *"every committed config was checked after the fix and all adapter paths resolve."*
  Per CLAUDE.md §6 that entry stands unaltered; this one carries the corrected account.
- **What was wrong with the check.** Scanning `configs/eval/*.yaml` and expanding `{model}` against
  the models on disk **invents failures**. A generic config is valid only for the model it is
  *invoked with*, and several configs share a phase, so pairing a config with every model under its
  phase directory produced 122 "unresolved" paths — none of which is a real defect. For example it
  paired `align_codellama7b.yaml` with `starcoder2-15b`, a combination that has never been run and
  never will be.
- **The authoritative instrument.** Every run cell writes `cell_meta.json` carrying
  `adapter_sha256`, a map from the adapter path actually used to the hash computed **at run time**,
  with the literal string `"missing"` when the path did not resolve. That is a record of what
  happened, not a guess about what could.
- **Result: `results/cells` holds 3,895 cells, 3,062 of them with a named adapter, and ZERO ran
  with a missing one.** The silent path is confirmed never to have fired on a kept result.
- **The lesson, which is the reason this is a separate entry rather than a footnote.** The thing
  that made the original bug dangerous — a silent failure leaving only a metadata note no analysis
  reads — is also what makes it *auditable after the fact*. The note nobody read is the record that
  settles the question. Reaching for the config scan first was reaching for the plausible check
  instead of the true one, and it would have reported 122 problems that do not exist.
- **Next Steps:** none. The `adapter_sha256 == "missing"` scan is ~2 seconds over the whole cell
  tree and is worth folding into `scripts/preflight_panel.py` as a standing audit.
