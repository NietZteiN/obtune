### Target Date: 2026-09-12 (Granite's training loss is 2.6× the panel median and it does NOT explain its three refutations — a correction to my own flag of two hours earlier)
- **The flag, and it was wrong.** On seeing Granite's first specialist adapter train to
  `train_loss` 1.377 against a panel median near 0.48, I wrote that this was *"a plausible common
  cause rather than three independent failures"* for its refutations of R2, R3 and the divergence
  advantage, and that it *"deserves checking before the paper treats Granite's three results as
  independent evidence."* **The checks refute that.**
- **The anomaly is real and systematic.** Median `train_loss` across every arm each model has:

  | model | n arms | median | range |
  |---|---:|---:|---|
  | starcoder2-15b | 4 | 0.3844 | 0.131–0.546 |
  | codellama-34b | 4 | 0.4165 | 0.108–0.583 |
  | gemma3-12b | 4 | 0.4254 | 0.124–0.641 |
  | codellama-13b | 4 | 0.4791 | 0.134–0.712 |
  | codellama-7b | 41 | 0.5170 | 0.150–1.235 |
  | llama31-8b | 5 | 0.5350 | 0.141–0.758 |
  | codegemma-7b | 4 | 0.7874 | 0.195–0.991 |
  | **granite31-8b** | 5 | **1.3770** | 0.395–2.718 |

- **Ruled out — vocabulary size.** Cross-entropy scales with the number of classes, so this was the
  easy answer. It is not available: **Granite's vocabulary is 49,155 and StarCoder2's is 49,152**,
  essentially identical, and their median losses are **1.377 and 0.384**. Gemma-3, at 262k tokens —
  five times the vocabulary — sits at 0.425.
- **Ruled out — loss-mask breakage** (CLAUDE.md §4, silent failure #4). `scripts/inspect_batch.py`
  on a real batch, run on a compute node:

  | model | mask verdict | supervised / total tokens | supervised text |
  |---|---|---:|---|
  | granite31-8b | **ok** | 39 / 2,822 | `0.33<\|end_of_text\|>\n` |
  | starcoder2-15b | **ok** | 71 / 3,022 | `0.33<\|endoftext\|>\n\n### Response\n` |
  | codellama-7b | **ok** | 45 / 3,149 | `0.33</s>` |

  Granite's prompt is correctly masked (296 of 302 tokens on row 0) and only the answer is
  supervised. If anything it supervises **fewer** trailing template tokens than StarCoder2 — and
  StarCoder2 has the panel's *lowest* loss, so trailing-token count does not order the losses either.
- **Refuted — that the anomaly explains the results.** Granite's accuracy is **entirely normal**:

  | | Granite | panel range |
  |---|---:|---|
  | clean-code adapter @L0 | **0.430** | 0.427 – 0.542 |
  | untuned @L0 | **0.285** | 0.000 – 0.334 (2nd highest) |
  | gain from tuning | **+14.5 pts** | — |

  A model whose training had gone wrong would show it here. It does not. **Granite's refutations of
  R2, R3 and the divergence advantage stand on their own and are not an artefact of bad training.**
- **What remains open, and it is a curiosity rather than a blocker.** Granite reaches panel-normal
  accuracy while assigning the gold answer lower probability — exact-match argmax can be right while
  P(gold) is low. That is the same axis E14's log-probability instrument measures, and it would be
  the instrument to use if anyone wants the mechanism. Nothing in the paper depends on it.
- **The process point.** I raised the concern on one number and a plausible story, and said so as a
  concern rather than a finding — which was right — but the story was wrong, and three cheap checks
  (a vocabulary comparison, a mask inspection, an accuracy lookup) settled it in under an hour.
  **Two of the three used data already on disk.** The order should have been: check the cheap
  refutations first, then raise the concern if they survive.
- **Next Steps:** none. Granite's pre-registered watch item may be closed on the training-health
  question; its status as the panel's outlier on *results* is unchanged and unexplained.
