### Target Date: 2026-08-05 (register the deobfuscation / fine-tuning literature)

- **Hypotheses / what we're testing:** None — this is an **organizational entry**. The question it
  answers is a positioning one, not an empirical one: *does the claim in [`../../CLAUDE.md`](../../CLAUDE.md)
  §3 — "we never train or evaluate on recovery/deobfuscation, that is the clean separation from the DOBF
  lineage" — actually hold against what the field has published?* Prior to today that claim was asserted
  against a five-bullet stub in [`../../papers/REFERENCES.md`](../../papers/REFERENCES.md) with no
  citations behind it. Secondary question: is the 2026-08-05 pilot's memorization finding
  ([`../pilot/2026-08-05_l0-control-refutes-invariance.md`](../pilot/2026-08-05_l0-control-refutes-invariance.md))
  novel, or has it been measured before?

- **Setup:** No GPU, no seed, no compute. Source material was a supplied AI-generated survey
  (`../../../LLM Obfuscated Code Fine-Tuning.md`, ~39 references). Method: take no number on trust —
  fetch the primary source for every load-bearing claim, then record a per-claim verification mark.
  Primary sources pulled: arXiv abstract/HTML pages, ACL Anthology, `eisenhofer.me` (CISPA preprint),
  `promon.io/hubfs` (threat report PDF), and direct PDF reads for the four documents whose text layer
  defeated the HTML-to-markdown path (Promon, Beste, Chisel, gMBA-ACL). 20 open-access PDFs fetched into
  [`../../papers/`](../../papers/); MDPI and IEEE sources are unfetchable (bot-blocked / paywalled) and
  are recorded as such rather than guessed at. Working files:
  `git rev-parse HEAD` = `dc86206` at start of the entry.

  ⚠️ **Two sessions touched `papers/` today.** An earlier pass wrote
  [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) and fetched the PDFs but stopped before
  the bibliography; this pass found and repaired the gap (see Results). Unrelated in-flight edits to
  `configs/data.yaml`, `scripts/02_build_corpus.py` and `src/obtune/data.py` were present in the working
  tree throughout and were **not touched**.

- **Results:**
  - **26 works registered** (20 with local PDFs in `papers/`); `references.bib` grown **3 → 29 entries**.
    The 6 without a PDF: `llm4dobf2026` and `taskin2026paradigms` (paywalled / bot-blocked), and the
    RQ2 machinery citations `hu2022lora`, `yadav2023ties`, `yu2024dare`, `rong2026codesteer`.
  - **Integrity gap found and closed:** the first pass cited **18 BibTeX keys that did not exist** in
    `references.bib` (every one dangling). 22 entries added; cited-key set minus bib-key set is now empty.
  - **7 PDFs renamed** to the repo's `<firstauthorlastname><year><keyword>` convention, citations
    repointed: `hexacoder2024`→`hajipour2024hexacoder`, `nanjing2025obfvuln`→`li2025obfvuln`,
    `poisoned2026identifiers`→`guzman2026poisoned`, `klee2025recover`→`feng2025recover`,
    `oasif2026`→`wang2026oasif`, `deconstructing2025obfuscation`→`tkachenko2025deconstructing`,
    `debinvul2024`→`manuel2024debinvul`.
  - **2 invented author names corrected.** `assaf2024malware` → the paper is Patsakis, Casino & Lykousas
    (`patsakis2024assessing`) and its PDF *is* present, though the first pass listed it as paywalled.
    `benmoussa2026paradigms` → Taşkın & Doğru (`taskin2026paradigms`).
  - **2 pre-existing broken `file = {…}` pointers repaired** in `references.bib`: the two foundational
    entries carried the `transcoders/` filenames (with the arXiv id) rather than the local symlink names.
  - **7 errors in the source survey corrected**, tabulated in `RELATED_WORK.md` §8. The two that change a
    conclusion rather than a digit: BinDeObfBench's dataset pipeline was quoted **backwards** (2,092 is
    the *input* count of filtered source programs, from which 2,108,736 obfuscated programs were
    generated — not a filtering-down of 2.1 M); and **Chisel uses no LLM at all** (OOPSLA 2024, pure
    trace-informed program synthesis), where the survey grouped it as a neural/hybrid system.
  - **1 claim remains unverified** (⚠️): LLM4DOBF's SacreBLEU **54.66**. Framework confirmed to exist;
    the number was not locatable in any accessible source.
  - **1 of my own review flags was wrong:** I flagged "Qwen3.5-27B / AndroZoo 0.982 F1" as implausible.
    It is real — MDPI *Appl. Sci.* 16(11):5600, 12,000 APKs, RF baseline 0.975. Recorded in §8 row 7 so
    the correction is not silently dropped.
  - Deliverables: [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) (living doc),
    [`../../reports/2026-08-05_deobfuscation-litreview/00_numbers.md`](../../reports/2026-08-05_deobfuscation-litreview/00_numbers.md)
    (point-in-time report), and a published web version of the report.

- **What worked / hypothesis verdict:** Organizational entry — no hypothesis to grade. On the two
  questions posed:
  - **The positioning claim holds.** Of the 26 works registered, **every** fine-tuning system optimises
    *obfuscated → clean*. None evaluates on still-obfuscated code, and none holds out an entire
    obfuscator family. The closest neighbour, `wang2026oasif` (OASIF), tunes for comprehension rather
    than recovery but works on assembly and has no held-out family. The `../CLAUDE.md` §3 sentence is
    defensible as written.
  - **The pilot finding is NOT novel, and that is good news.** `nikiema2025contrastive` (Nikiema et al.,
    Univ. Luxembourg, arXiv:2509.05553) names the same phenomenon **"cognitive specialization"** and
    measures it: standard SFT yields **0 %** reverse success; their Contrastive Fine-Tuning fix recovers
    **39–52 %** — but on **variable renaming only**, with dead-code insertion and string encryption still
    failing outright. Different axis (forward/reverse direction) from ours (held-out obfuscator family),
    same disease. This makes our pilot *expected* rather than anomalous, and hands us a named candidate
    intervention if the RQ1 grid confirms it.

- **Observations:**
  - The AI-generated survey was **~82 % accurate on numbers but unreliable on framing** — the two errors
    that mattered were both categorical (a pipeline direction, a system's whole method class), not
    numerical. Verifying digits alone would have caught neither. Worth remembering for the next sweep.
  - **A literature document with dangling citation keys is worse than no document**, because it reads as
    grounded. The check that caught it is cheap and should be routine: diff the backticked-key set in the
    prose against the `^@type{key,` set in the bib. Note the naive regex misses keys containing digits
    (`gong2024astt5`, `llm4dobf2026`) — the pattern must allow trailing digits or it reports false gaps.
  - `guzman2026poisoned` is a direct, unlooked-for hit on **`L1b`**: misleading identifiers survived
    deobfuscation in **every** baseline run (8/8, 5/5), and in **15/17** runs the model wrote the wrong
    variable name *while correctly describing the operation in a comment*. Reframing the prompt from
    "deobfuscate" to "write a fresh implementation" cut propagation **100 % → 0–20 %** with no weight
    update. That is an existing-literature datapoint for the RQ2 oracle-prompt arm being a live
    hypothesis rather than a formality.
  - `promon2026atr` supplies the strongest external warrant for a decision already taken: ten frontier
    models average only **63.7 %** on *clean* ARM assembly. Obfuscation degrades from ~64 %, not from
    100 %. That is exactly the argument for the `L0` control adapter being a required cell — which the
    pilot independently discovered by having it falsify H1c.
  - `hu2026bindeobf`'s in-context-learning divergence (few-shot lifts CodeLlama to 72.92 % but plateaus
    DeepSeek-R1 at 70.29 %) is a concrete warning for `oracle_prompt_1shot`: **report it per model family,
    never pooled.** It also independently echoes Paper 2's reasoning-vs-coder alignment split.

- **New questions / new hypotheses:**
  - Should CFT (`nikiema2025contrastive`) enter the design as an RQ1 follow-up arm? Their result implies
    it works where a consistent inverse mapping exists (renaming) and fails where it does not — which
    predicts it would help `L1b`/`L1r`/`L2` and not `S1`/`S2`/`H1`. That is a falsifiable prediction our
    ladder is unusually well-suited to test.
  - `li2025obfvuln`'s "upgrade" effect (some transforms *improve* model performance by stripping
    misleading surface cues) predicts a **non-monotonic** tier ordering. Our pilot is already consistent
    with it: base scores `.242` on `L1b` but `.202` on both `L1r` and `L2`, and the `L1b`-tuned adapter
    scores *higher* on `L1r` (`.576`) than on `L1b` itself (`.515`). Worth stating as a hypothesis rather
    than discovering it again in the grid.
  - Read `wang2026oasif` properly before the RQ1 writeup — it is the nearest competitor to the framing
    and I have only read its abstract and first page.

- **Next Steps:**
  1. Read `wang2026oasif` and `feng2025recover` in full; promote them out of `RELATED_WORK.md` §3.4
     ("registered but not yet load-bearing") if they bear on the framing.
  2. Fold the `nikiema2025contrastive` comparison into [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md)
     §1 as prior work, and decide whether CFT becomes a design arm.
  3. Add the non-monotonic-ordering hypothesis to [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md).
  4. Register "Attention is not explanation" + rebuttals — still the one un-cited item in the adjacent-work
     list, and RQ3's framing depends on it.
