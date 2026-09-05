### Target Date: 2026-09-05 (THE FINAL H1 READ — every pre-registered test confirms; the H1 budget is now fully spent)

The second and last H1 access CLAUDE.md §3.2 rule 3 allows (jobs 378518, 378519; pilot spent
2026-09-02, repaired 2026-09-04). **There is no third read. No H1 number in this entry may be
used to select, tune, rank or choose anything from here on.** Authorised by the user on
2026-09-05 against a concrete five-arm manifest; hypotheses committed as `361d354` **before**
submission. Grid A heldout, 1,214 items / 405 programs; program-clustered bootstraps, 2,000
resamples.

- **Integrity checks run before any number was interpreted.** The pilot's `tuned_L0` row was
  once silently decoded on another adapter's cached prefill
  ([`2026-09-03_prefix-cache-collision.md`](2026-09-03_prefix-cache-collision.md)), so
  distinctness was verified rather than assumed: `base` shares **0.0000** identical outputs with
  every tuned arm, and no pair of arms exceeds 0.44. Every adapter was genuinely applied.
  `format_fail` 0.014–0.026 on tuned arms against 0.159 on the 34b base.
- **The final panel** (7B rows other than the X1 arms are the spent pilot, shown for context):

  | system | H1 |
  |---|---|
  | `base` (7b) | 0.1285 |
  | `base` (34b) | 0.1433 |
  | `mono_all` (7b) | 0.2323 |
  | `tuned_L0` (7b) | 0.2735 |
  | `tuned_S1` (7b) | 0.2776 |
  | `tuned_S2` (7b) — *the old leader* | 0.2834 |
  | **`mono_all` (34b)** | **0.2965** |
  | **`mono_allX` (7b)** | **0.3089** |
  | **`tuned_X1` (7b)** | **0.3180** |
  | **`tuned_L0` (34b)** — *the new leader* | **0.3213** |

- **Every pre-registered test confirms.**

  | test | Δ pts [95 % CI] |
  |---|---|
  | **H-34b-h1**: 34b `tuned_L0` vs the 7B H1 leader `tuned_S2` | **+3.79 [+1.56, +6.10]** |
  | **H-rq2-at-scale** (decisive): `tuned_L0 − mono_all` @ 34b | **+2.47 [+0.41, +4.78]** |
  |   *7B reference from the pilot* | *+4.12 [+1.81, +6.75]* |
  | **H-X1-family**, 2nd conjunct: `tuned_X1` vs `tuned_S2` | **+3.46 [+1.32, +5.51]** |
  | **H-mono-X** on H1: `mono_allX − mono_all` | **+7.66 [+5.35, +10.04]** |
  | 34b tuning gap on H1 (`tuned_L0 − base`) | **+17.79 [+14.81, +20.94]** |

- **RQ2's headline survives the top of the ladder — this is the paper's central claim.** At 7B,
  `tuned_L0` — trained on *clean code only*, having never seen an obfuscator — beat the
  six-condition `mono_all` on the held-out obfuscator by +4.12. The obvious objection was that
  this is a small-model artefact: a 7B model cannot exploit breadth, so breadth looks useless.
  **It is not an artefact.** At 34B, with 8.6 pts more headroom on the trainable grid and a
  +17.79 tuning gap on H1 itself, `tuned_L0` still beats `mono_all` by **+2.47 [+0.41, +4.78]**.
  Training on more transform families does not buy generalisation to an unseen one; training on
  clean code does. Fine-tuning here teaches something closer to semantic invariance than to
  transform memorisation, and scale does not change which of the two you get.
- **The result I did not expect: family training at 7B matches scale at 34B.** `tuned_X1` (a 7B
  adapter) against `tuned_L0` (34B, the campaign winner) on H1 is **−0.33 [−2.88, +2.06]** —
  statistically indistinguishable. A 7B model trained on a *sibling of the held-out family*
  equals a 34B model at roughly a fifth of the parameters. Read with
  [`2026-09-05_scale-is-the-only-lever-that-works.md`](2026-09-05_scale-is-the-only-lever-that-works.md),
  where every algorithmic lever at 7B fit inside 1.8 pts while scale bought 8.6, the qualifier is
  now sharper: **no lever that keeps the training distribution fixed beat scale; changing the
  training distribution to the right family did.**
- **An honest surprise, recorded as such.** The pre-registration stated plainly that the X1
  diagonal carries *no* information about H1 for arms trained on X1, and that the r = 0.9992
  X1↔H1 correspondence explicitly does not extend to them
  ([`2026-09-05_x1-is-a-trainable-proxy-for-h1.md`](2026-09-05_x1-is-a-trainable-proxy-for-h1.md)).
  That was the right inferential stance and I would write it again. Empirically the transfer
  turned out to be **essentially lossless**:

  | arm | X1 (diagonal) | H1 (transfer) | Δ |
  |---|---|---|---|
  | `tuned_X1` | 0.3188 | 0.3180 | **0.08 pts** |
  | `mono_allX` | 0.3097 | 0.3089 | **0.08 pts** |

  Training on X1 yields the same accuracy on H1 as on X1 itself. Combined with the r = 0.9992
  correspondence on untrained arms, **X1 and H1 are the same problem to this model** — which is
  the strongest available evidence that H1's difficulty is its *mechanism family* (XOR-keyed
  string encoding + guarded MBA), not its particular surface form. That was H-X1-family's whole
  premise and it is now confirmed on both conjuncts. The caveat stands for future work: this was
  learned *from* the final read, and cannot be assumed for a new held-out family.
- **What this closes.** The H1 budget is fully spent. `tuned_L0` (34b) is the campaign's H1
  leader at 0.3213, against the pilot's 0.2834 and a 0.1285 base. Every remaining question about
  the held-out obfuscator must be answered on X1, which the correspondence above licenses.
- **Provenance:** cells `results/cells/h1_codellama/codellama-{7b,34b}/python/*__H1`; configs
  `configs/eval/h1_final_{codellama34b,x1_codellama7b}.yaml` (hypotheses in headers, committed
  `361d354` pre-submission); ACCESS_LOG narrative at `data/quarantine/h1/ACCESS_LOG.md`
  (that tree is gitignored so quarantined stimuli can never be committed); quarantine layers
  re-run immediately before submission — `test_quarantine_lint` 5 passed, `check_manifest.py` OK.
