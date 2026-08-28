### Target Date: 2026-08-17 (MBPP+ as a held-out probe — and it overturns two claims)

- **Hypotheses / what we're testing:** **H-M1 — is the paper's selectivity claim an artifact of
  benchmark contamination?** The abstract said forward-only fine-tuning destroys the reverse
  direction "while the same model's score on a general coding benchmark does not fall at all."
  That rested on HumanEval+, and HumanEval is one of the corpus's three sources. §8 also claimed
  a *grouping*: single-direction arms within 1.2 pts of base, bidirectional arms down 6–7.
  **Verdict: H-M1 CONFIRMED. Both claims were contamination artifacts.** Companion writeup entry:
  [`../writeup/2026-08-17_attrib-reviewer-hardening.md`](../writeup/2026-08-17_attrib-reviewer-hardening.md).

- **Setup:** 7 cells, `qwen25c-7b` × {base, sft, fwd2x, cft, rev, flip, mix50}, MBPP+ 399 tasks,
  greedy, seed 17, enqueued at the default priority 59 via a new
  `26_enqueue_forgetting.py --preset mbpp-7b --suite mbpp --write`. All four A6000s idle, queue
  empty, ~5 min/cell. Every adapter path is byte-identical to the one its published HumanEval+
  cell used, checked against each `humanevalplus_qwen25c-7b_*.json`'s `adapter` field, so the two
  probes measure the same weights. Results: `results/forgetting/mbppplus_qwen25c-7b_7b_*.json`,
  each carrying an inline `provenance` block and a 399-entry `per_task` dict.

- **Is MBPP actually held out? Yes, verified rather than assumed.**
  `data/manifests/corpus_python.json` records `tiers: ['tier1']`; MBPP/MBPPPlus are declared only
  under `tier2` in `configs/sources.yaml` and were never built. Provenance histogram over the
  2231 rows of `data/train/base/python.jsonl`: **apps 1584 / cruxeval 543 / humaneval 104 /
  mbpp 0.** Nothing under `data/train/` mentions mbpp and the dataset was never in the HF cache.
  `src/obtune/corpus/sources/mbpp.py` is an unexercised loader.

- **A correction that fell out of the same check.** The paper said "104 of the 164 HumanEval+
  problems ... so every trained arm saw them." 104 is the **corpus** count; the arms train on the
  train split, and `data/splits/python.json` puts those 104 at **74 train / 25 test / 5 val**. The
  defensible number is **74/164**, and it is the stronger contrast against MBPP+'s 0/399.

- **Results** (paired bootstrap over the 399 tasks, 10,000 resamples, seed 17; sign confirmed by
  exact McNemar on discordant pairs). Base MBPP+ `plus` = .714.

  | arm | MBPP+ Δ vs base | 95% CI | McNemar p | HumanEval+ Δ |
  |---|---|---|---|---|
  | `sft` | **−5.3** | [−9.0, −1.5] | 8.6e−3 | **+1.2** |
  | `fwd2x` | −2.5 | [−6.3, +1.3] | 0.23 | +0.0 |
  | `cft` | −5.0 | [−8.8, −1.3] | 1.2e−2 | −0.6 |
  | `rev` | −6.0 | [−10.0, −2.0] | 5.6e−3 | −0.6 |
  | `flip` | −6.3 | [−10.3, −2.3] | 3.5e−3 | −6.1 |
  | `mix50` | −5.5 | [−9.3, −1.8] | 5.4e−3 | −7.3 |

  - Pooled, any trained arm − base = **−5.1 pp [−8.0, −2.1]**.
  - **The grouping is dead.** both-directions − one-direction = **−1.2 pp [−3.8, +1.5]**, where
    HumanEval+ gives −6 to −7. Every arm-vs-arm contrast is null: `mix50`−`sft` −0.3
    [−4.0,+3.5] p=1.00; `mix50`−`rev` +0.5 [−3.3,+4.3]; `flip`−`sft` −1.0 [−5.0,+3.0].
  - Data quality: 0 scorer errors, 0.0 format-fail, **0 entry-point mismatches** in all 7 cells.
    Adapter-applied check (CLAUDE.md §4.2) off `per_task`: 69–84 of 399 tasks discordant vs base
    in every tuned cell, so no adapter silently failed to load.

- **What worked / hypothesis verdict:** CONFIRMED, and the paper is better for it.
  1. The abstract's "does not fall at all" was false on held-out data. `sft` scores **+1.2 above**
     base on the benchmark 74 of whose problems it trained on and **−5.3 below** it on the one it
     never saw. Rewritten to the disproportion, which is what actually survives: reverse goes to
     **zero**, a total loss, while general ability gives up a fourteenth of its value.
  2. §8's grouping and the elegant `rev`-vs-`mix50` isolation do not replicate. Replaced with the
     simpler true statement: fine-tuning costs ~5 pts whatever the direction mix. **This makes the
     prescription stronger** — bidirectional data costs no more than the forward-only training a
     practitioner would run anyway, so the flip is free against the baseline that matters. The
     draft-v2 "bidirectional costs 6–7 points" caveat largely dissolves.
  3. Untouched: the attribution (data direction, not objective) and the repair. Those are
     reverse-capability results and no general-capability number bears on them.

- **Observations:**
  - **A reviewer had explicitly advised not to complicate the `rev`-vs-`mix50` isolation.** Good
    advice against the evidence available then; overtaken by evidence now. Worth remembering that
    "don't touch the elegant part" and "the elegant part is an artifact" are indistinguishable
    from the outside until the held-out probe runs.
  - `fwd2x` is the only arm not significantly below base (−2.5 [−6.3,+1.3]) and `fwd2x`−`sft` is
    +2.8 [+0.0,+5.8]. Forward-only trained *twice as long* damages general ability *less*. Not
    explained; at these interval widths not worth a sentence in the paper, but it is the one
    number here that looks like it wants a mechanism.
  - Only `7b_rev` among the seven HumanEval+ cells carries `per_task`, so the HumanEval+ column
    cannot be paired-tested and supports point estimates only. All seven MBPP+ cells carry it.
  - Every 7B arm is single-seed, so none of these intervals covers training-seed variance.

- **Implementation notes:**
  - New `mbpp_plus()` in `src/obtune/forgetting.py`, parallel to `humaneval_plus()` rather than a
    `dataset=` parameter on it, so the seven published HumanEval+ numbers are untouched.
  - **The MBPP prompt is a bare docstring; the function name exists only inside its example
    `assert`.** A model that invents a name scores 0 on a correct program, uniformly across arms,
    which would read as catastrophic forgetting everywhere. The instruction names this explicitly
    and `entry_point_mismatch` is the counter that proves it worked (0 in every cell).
  - `_extract_code(text, "")` on the MBPP path, not `(text, prompt)`. That fallback fires when the
    completion has no `def`, and prepending a docstring yields a module defining nothing.
  - Three defects in `26_enqueue_forgetting.py` would each have silently blocked the sweep: the
    result-existence guard was hardcoded to the `humanevalplus_` stem (all 7 exist → all 7
    dropped), `job_id` collided with the HumanEval+ pass for `7b_rev`/`7b_fwd2x`, and
    `problems_for` could not express "no adapter" so the base cell was unenqueueable. Fixed;
    `--allow-overwrite` would have been the wrong response since it disarms the Table 5 guard.
    Also fixed a live landmine: the script offered `--suite humanevalplus`, which `forgetting.py`
    does not accept, so any job enqueued that way died on argparse after being claimed.
  - **Manual invocation needs `PYTHONPATH=src` and the conda env's `bin` on `PATH`.** vLLM's
    flashinfer sampler JIT-compiles on first use and shells out to `ninja`. Without it, startup
    fails as `RuntimeError: Engine core initialization failed` with the real cause nine frames
    down. The workers set both, so queued jobs were never affected.

- **Next steps:**
  - MBPP+ at 1.5B would say whether the "~5 pts regardless of mixture" result is scale-general;
    the 1.5B HumanEval+ column behaves completely differently (`sft` is the worst arm there).
  - Retrofit `per_task` onto the HumanEval+ path so the two probes can be paired-tested. Known
    debt, not for this deadline.
  - `forgetting.py`'s HumanEval+ path still writes no provenance; the MBPP+ path embeds it inline
    under a `provenance` key and is the pattern to copy.
