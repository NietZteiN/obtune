### Target Date: 2026-09-13 (the backward task's one-shot template is CodeLlama-7B-specific: 20 of 35 backward cells on the new panel models fail the format gate, so the panel-wide "backward cost" is format collapse, not lost competence)
- **What the batch showed.** `evb_inv` ran the reverse task (input prediction, one-shot template
  `inverse_1shot_v1`, graded by execution) on seven further models. Read naively, the tuned arms lose
  **20–41 points backwards** on clean code — Granite anchored −41.0, CodeLlama-13B breadth −39.6 —
  where CodeLlama-7B's arms move by ±4.
- **Why it is not a competence result.** The design pre-registered a format gate: pooled
  `format_fail_rate` above **0.25** makes a cell NOT INTERPRETABLE. On CodeLlama-7B every arm
  passes (max 0.192). On the new models:

  | model | base | tuned_L0 | mono_all | cons_lam3 | tuned_X1 |
  |---|---:|---:|---:|---:|---:|
  | codellama-13b | 0.039 | 0.068 | **0.942** | **0.643** | **0.637** |
  | codellama-34b | 0.036 | **0.480** | **0.293** | **0.678** | **0.254** |
  | llama31-8b | 0.108 | 0.090 | **0.532** | **0.531** | 0.084 |
  | starcoder2-15b | **1.000** | **0.725** | **0.656** | **0.752** | **0.603** |
  | gemma3-12b | 0.023 | **0.258** | 0.048 | **0.672** | 0.017 |
  | codegemma-7b | 0.172 | **0.581** | **0.843** | **0.989** | **0.766** |

  **20 of 35 cells are over the bar.** A −40 point delta on a base of 0.42 puts the arm near zero,
  and the format column says why: it is not producing a parsable `name(args)` line at all.
- **This is the in-context result again, in the other direction.** The one-shot ICL read on the
  same day had 5 of 8 models over the same threshold, worst on CodeLlama-34B (0.737). Both tasks
  put a demonstration in front of the model with a template written and validated on CodeLlama-7B.
  The tuned arms of other models respond to that demonstration by leaving the output contract. It is
  the same class of fault as the system-role rejection that needed `prompts.py`'s adaptation layer
  before training could start — a template that is model-specific wearing a model-neutral name.
- **What stands.** The direction-ratio result in the paper is **CodeLlama-7B only** and every one
  of its cells passes the gate; Threats already says the reversal test is one model deep. It is not
  extended. The master table now renders any gated cell as `fmt` and excludes it from every mean.
- **What may NOT be said:** anything about backward competence on the seven new models from these
  cells. The corrected cross-model summary drops from n=8 to the cells that pass, and the "anchored
  costs 20 points backwards" figure that a naive read produced is withdrawn before it was ever used.
- **Next Steps:** a per-model adaptation of the inverse template (the same treatment `prompts.py`
  gave the forward template), validated on format rate before any backward number from these
  models is read. Until then the backward columns for those models are `fmt`.
