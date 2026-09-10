# setup — scaffold, environment, data layer, obfuscation pipeline

*Last updated: 2026-09-07*
**Status:** active

## Hypotheses — open
- (the scientific ledger lives in [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md); this thread tracks engineering correctness)
- **S1/S2 coverage:** the flattener/dead-code passes apply to >=90% of real programs. CONFIRM if `coverage_matrix.json` shows >=0.90 per condition; REFUTE below that, in which case headline numbers must use the all-conditions-succeeded common subset and the shortfall is reported.
- **Span->token resolution >= 0.98 on Qwen2.5-Coder tokenizers** (the prior 1.0 validation was on Llama-3.1-8B / Qwen3-0.6B). REFUTE below 0.98 — RQ3 hard-fails there.

## Hypotheses — resolved
- ✓ **Cross-language canonicalization**: Python and JavaScript canonicalizers produce byte-identical strings for equivalent values — 9/9 fixture groups, plus matching rejection behavior. Resolved by [`2026-08-04_scaffold-and-pipeline.md`](2026-08-04_scaffold-and-pipeline.md), after fixing two real defects (integral-float formatting; vm-context intrinsics breaking object type checks).

## What worked
- Diffing the backticked-citation-key set in a literature document against the `@type{key,` set in the bib. It caught 18 dangling keys in `papers/RELATED_WORK.md` that made the file *look* grounded while citing nothing. Cheap; should be routine. (Caveat: the naive regex misses keys containing digits — `gong2024astt5`, `llm4dobf2026` — so the pattern must allow trailing digits or it reports false gaps.)
- Testing the canonicalizers against each other rather than assuming agreement — it found the float-format divergence that would have made the JS arm of RQ1 incomparable.
- Confining `javascript-obfuscator` to the H1 generator architecturally, instead of configuring it carefully per condition.
- Four independent quarantine layers; the content-marker scan caught a planted `atob(` in a row labeled `S1`, which label checks alone cannot.

## What didn't
- Trusting an AI-generated literature survey on *framing* rather than digits. Its numbers were ~82% right, but it quoted BinDeObfBench's dataset pipeline backwards and classified Chisel (pure program synthesis, no LLM) as a neural hybrid. Verifying figures alone would have caught neither.
- Resolving `node` from the child's restricted PATH — every JS execution failed silently as `crash` until the binary was resolved once at import via `shutil.which`.
- Mapping an `RLIMIT_CPU` kill to `crash`; `crash` must mean the harness broke, `timeout` that the program was unsuitable.

## Open ideas
- Run the determinism filter with more than 3 repeats on programs whose outputs contain dict/object keys — hash-order dependence is the failure mode most likely to survive a small repeat count.
- Consider recording per-condition transform wall-time in the coverage manifest; a condition that is slow to generate is usually one that is bailing and retrying.

## Entries
- [`2026-09-10_correction-the-cap-is-real.md`](2026-09-10_correction-the-cap-is-real.md) — **corrects the entry below**: h200 imposes `QoS=juno`, `MaxJobsPU=4`, and it is binding (4 running / 10 cap-blocked). Packing was right; converting to singles halved throughput. A cap is invisible until you are against it — check `scontrol show partition`, not pending reasons.
- [`2026-09-10_the-qos-that-did-not-exist.md`](2026-09-10_the-qos-that-did-not-exist.md) — **the QOS every job has requested since the migration is not on this cluster**; jobs holding it are throttled while H200s idle. Control job proves it. `CLAUDE.md` §1's queue-wait constraint is partly self-inflicted. Packing is the wrong tool once the cap lifts. HF cache moved to 30 TB scratch.
- [`2026-09-10_four-probes-the-gate-was-wrong.md`](2026-09-10_four-probes-the-gate-was-wrong.md) — **three of five models rejected by the gate, all wrongly.** StarCoder2 0.5401 (best in panel), Gemma-3 0.5180, CodeGemma 0.4647, pretrained Llama measurable one-shot. Three unrelated causes, none of them the model. Untuned `format_fail` diagnoses the prompt contract, not the model.
- [`2026-09-10_gate-format-confirmed.md`](2026-09-10_gate-format-confirmed.md) — **H-gate-format CONFIRMED.** Gemma-3-12B tuned reads **0.5180** on L0 (threshold 0.4275), ties CodeLlama-34B at a third the parameters, and its format_fail falls 29× in one epoch. The registered gate would have discarded it. Proposed two-part gate; CodeGemma probe opened as H-gate-format-lineage.
- [`2026-09-09_final-cleanup-sweep.md`](2026-09-09_final-cleanup-sweep.md) — **second sweep, 10.1 GB.** `results/attn` split (five pipeline `done_when` markers kept), `allocation_replication` bundled + patched before deletion. `du` overstated the yield ~2x: block allocation, not bytes.
- [`2026-09-09_panel-gates-read.md`](2026-09-09_panel-gates-read.md) — **five gates read: Granite PASSES, Gemma-3/CodeGemma blocked by one shared quoting convention, StarCoder2 by its template's own persona under merged mode, and the pretrained-Llama read INVALIDATED by a `render_plain` bug from this session** (trailing newline into the `\n\n` stop → 92.9 % empty). Fixed and re-running. New H-merged-persona.
- [`2026-09-09_one-quota-two-agents.md`](2026-09-09_one-quota-two-agents.md) — **one 1.1 TB quota, two agents, no shared view.** The other sub-project lost three trained layers to `Disk quota exceeded` today; two events it logged as unexplained were this session's cleanup and job release. `df` does not show the quota — use `mfsgetquota`. ~19 GB left outside obtune/transcoders against ~122 GB of committed work elsewhere.
- [`2026-09-09_panel-downloads-and-first-gate.md`](2026-09-09_panel-downloads-and-first-gate.md) — **all five panel models downloaded and verified; Gemma-3-12B gate is NO-GO by the rule** (ff 0.2796 > 0.15) **but its floor is a quoting convention**: L0 0.3335 beats CodeLlama-7b base 0.2569, and 34.8 % of its failures are the gold value unquoted (9.8 pts). Decision on the reduced probe left to the human. New hypothesis H-gate-format.
- [`2026-09-09_quota-cleanup-for-the-panel.md`](2026-09-09_quota-cleanup-for-the-panel.md) — **125 GB freed** (218 non-selected checkpoints, 23.8 GB of orphaned download scratch, the barred Qwen-1.5B) so the five-model panel fits; 1,074.6 → 965.4 GB, back under the soft quota. `best/` is a symlink into a checkpoint dir — a blanket delete would have destroyed every selected adapter. Two dangling symlinks are 2026-08-28 migration damage, not this cleanup.
- [`2026-09-09_five-model-panel.md`](2026-09-09_five-model-panel.md) — **five-model panel adopted; three of the five reject the system role.** StarCoder2 and CodeGemma raise `TemplateError`, the pretrained Llama-3.1 has no chat template — `prompts.py` gained one verified adaptation layer used by every path (identity in `system` mode, 30 tests). PEFT-on-the-vision-tower disarmed for Gemma-3. Downloads and the first two gates submitted.
- [`2026-09-07_autonomous-pipeline.md`](2026-09-07_autonomous-pipeline.md) — RQ1′–RQ4′ adopted; `scripts/pipeline/plan.yaml` (47 stages) + `report.py` run everything planned as SLURM chains; rules pre-registered; E5b/E10 disabled with reasons
- [`2026-09-06_quota-cleanup.md`](2026-09-06_quota-cleanup.md) — 685 `optimizer.pt` (~346 GB) + uv cache dropped after the quota incident; `/work` 99.7 % → 66.2 %; nothing under `runs/` is resumable now.
- [`2026-09-01_model-agnostic-and-an-inherited-pin.md`](2026-09-01_model-agnostic-and-an-inherited-pin.md) — model-agnostic refactor + lint; the inherited `_base_lora.yaml` model pin that doomed 17 jobs
- [`2026-08-30_vllm-unblocked.md`](2026-08-30_vllm-unblocked.md) — vLLM was never blocked by CUDA; corrects the 08-28 verdict. Real fault was flashinfer needing `nvcc`; the rest was a harness with no `__main__` guard and node-local `/tmp`
- [`2026-08-05_register-deobfuscation-literature.md`](2026-08-05_register-deobfuscation-literature.md) — 20 papers registered; the DOBF-separation claim holds, and the pilot's memorization finding has prior measurement
- [`2026-08-04_scaffold-and-pipeline.md`](2026-08-04_scaffold-and-pipeline.md) — project created; contracts verified in both languages; RQ1–RQ3 stack built

## Doc / results links
- [`../../papers/RELATED_WORK.md`](../../papers/RELATED_WORK.md) — the deobfuscation/fine-tuning literature map, per-claim verification marks
- [`../../reports/2026-08-05_deobfuscation-litreview/00_numbers.md`](../../reports/2026-08-05_deobfuscation-litreview/00_numbers.md) — numbers-first summary of the same sweep
- [`../../docs/design_doc_v0.1.md`](../../docs/design_doc_v0.1.md) (§9 records deviations from the v0.1 brief)
- [`../../docs/CHECKLIST.md`](../../docs/CHECKLIST.md)
- [`../../data/DATA_SOURCES.md`](../../data/DATA_SOURCES.md)
