### Target Date: 2026-09-05 (lever 3b — span-pooled alignment, submitted)
- **Hypotheses / what we're testing:** W5 refuted H-align for the *answer-position* form
  ([`2026-09-04_invariance-arm-at-7b.md`](2026-09-04_invariance-arm-at-7b.md): matched −
  mismatched +0.18 [−0.82, +1.16]). The user's original ask was "make the hidden states match the
  unobfuscated code"; the answer-position variant aligns four states that predict the answer, not
  the code representation. **H-align-span:** aligning the mean-pooled per-layer representation of
  the *code span* (student on obfuscated code, frozen `tuned_L0` on the clean parent) does what the
  answer-slot version did not. CONFIRM if matched > mismatched **and** matched − `mono_all` excludes
  0 on ≥ 1 non-L0 condition with no L0 tax; REFUTE if matched ≈ mismatched (regularizer again) or
  the dose-response is monotone negative as before.
- **Setup:** `src/obtune/align.py` gained `align.mode: span` — `resolve_span_mask` re-assembles the
  sentencepiece pieces of each row's `input_ids` (`▁`→space, `<0x0A>`→newline) and locates the
  frozen prompt markers `Program:\n` … `\n\nCall:`; `pool_states` mean-pools the masked positions
  per layer, so n ≠ m never arises and S1/S2 need no rename map. Gate `scripts/check_span_mask.py`
  (dev 377863): recall = precision = 1.000 on 40 rows × six conditions, span 125 (L2) – 701 (S1)
  tokens. Cache `runs/align_cache/codellama-7b/python/L0-L1b-L1r-L2-S1-S2_s17__best__span.npz`
  holds `[N, 6, 4096]` pooled teacher states. Config `configs/train/align_span_codellama7b_py_mono.yaml`
  is the W5 config + `mode: span` (six conditions, train_size 30000, seed 17, r32, 16×4, teacher
  `tuned_L0`, layers 4-10-16-21-25-30). Arms: λ = 1 matched, λ = 1 mismatched (permuted teacher
  index, as in W5), λ = 3 matched. Chain `al_span_cache` 377864 → `al_span_lam1` 377865 /
  `al_span_lam1_mm` 377866 / `al_span_lam3` 377867 → `ck_span_*` 377868–377870 (held-in val) →
  `ev_span` 377871 (`eval/align_span_codellama7b.yaml`, rq2_generic, no H1). Commit `745a0f9`.
- **Results:** pending.
- **What worked / hypothesis verdict:** pending.
- **Observations:** The per-token `rename_map` pairing was dropped: it exists only for the
  identifier family, and L2 strips annotations so even there the correspondence is not 1:1. The
  pooled MSE has a different raw scale from the k = 4 form, so λ is not comparable across modes —
  λ = 3 brackets it; `align_loss` is logged separately, as before, so a flat term is visible. The λ = 0
  plumbing gate is not re-run: λ = 0 skips the alignment path entirely and is identical in both modes.
- **New questions / new hypotheses:** if pooled matched ≈ mismatched too, the whole L_align family
  is closed at 7B on this corpus and the writeup should say that alignment-as-objective is not
  where invariance comes from.
- **Next Steps:** read 377871 against `mono_all` (s17/s42/s101 band) and `tuned_L0`; update H-align
  in the README either way.
