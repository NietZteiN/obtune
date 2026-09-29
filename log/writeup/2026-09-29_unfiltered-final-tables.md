## 2026-09-29 — Recover unfiltered Tables 6–9

- Request: fill all values and remove format filtering in paper/final Tables 6–9; four local GPUs authorized for reruns if needed.
- Hardware: four idle RTX A6000 48 GB; no GPU jobs launched. Original evaluation results were accessible on Juno.
- Source: jvl210002@juno.utdallas.edu:/work/jvl210002/migration/obtune/results/cells/, retrieved with rsync (directories, cell_meta*.json and trials*.parquet only). Local checkout 081a3d014103be86225ab727b066da224d49a81b. Existing trials use seed 17; no new inference or training.
- Commands: `/data/jvl210002/conda_envs/obtune/bin/python scripts/analysis/76_merge_ablation.py --unfiltered`; `python scripts/paper/unfiltered_final_tables.py`; `/data/jvl210002/conda_envs/tex/bin/tectonic -X compile paper/final/fse27.tex --keep-logs`.
- Results: Table 7 backward entries recovered: CodeLlama-7B struct/depth-3 = 45; CodeLlama-13B struct/L0 = 35, ident/L0 = 84, struct/depth-3 = 36 (percent of base L0). Tables 6/8/9 recomputed using all cells and unchanged condition groups; reverse block averages all 23 conditions. Prefer v2 backward grades. Updated the directly affected reverse-gain range to 3.0–17.1 pp.
- Validation: all four missing values present; 2,208 source cells recorded for Tables 6/8/9; generator repeatability, brace/marker checks and git diff --check passed. PDF compiled successfully; Table 7 visually inspected. Existing font/layout and bibliography warnings remain.
- Artifacts: paper/final/fse27.pdf; results/analysis/pipeline/final_tables_unfiltered.json; results/analysis/pipeline/merge_ablation_unfiltered.json.
