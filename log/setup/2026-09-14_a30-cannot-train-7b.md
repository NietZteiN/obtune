# 2026-09-14 — a30 cannot train CodeLlama-7B at the panel batch shape: four of four OOMs

**Thread:** setup · **Corrects:** the standing note that "a30 trains CodeLlama-7B and nothing else" (CLAUDE.md §1, drain comments)

Four CodeLlama-7B trainings were sent to a30 today because it was idle and the standing rule said
7B fits there. All four died at their first optimizer step with CUDA OOM on the 23.49 GB card:

| job | short by | when |
|---|---|---|
| `tr_S3_codellama-7b_s42` | 322 MiB | step 1/222 |
| `tr_S4_codellama-7b_s42` | 570 MiB | step 0/219 |
| `tr_X1_codellama-7b_s42` | 752 MiB | step 0/162 |
| `tr_inverse_breadth_codellama-7b` | 872 MiB | step 0/1260 |

The recipe is the panel's own — `per_device_batch` from `configs/models.yaml`, 2048-token context,
gradient checkpointing on — and it is what the seed-17 twins were trained with on h100/h200. The
standing note dates from a smaller batch. A smaller batch on a30 would fit, and would make the
second seed incomparable with the first, which is the one thing a second seed must not be.

All four are requeued to h100 at the lowest priorities, behind every evaluation grid. The a30
partition is now unused by this project; its note in the drain says why. About twelve minutes of
a30 time and four submissions were spent learning this, which is cheap, and it should not be
learned a fifth time.
