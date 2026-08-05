# 00 — load results/trials.parquet and coerce it to the analysis schema.
# Every downstream script starts from `trials`, so all factor levels and derived
# columns are established exactly once, here.

source(file.path("stats", "R", "config.R"))
source(file.path("stats", "R", "helpers.R"))

suppressMessages(library(arrow))

load_trials <- function(path = PATHS$trials) {
  if (!file.exists(path)) {
    stop("no trial table at ", path, " — run `python -m obtune.trial_table` first")
  }
  trials <- arrow::read_parquet(path) %>%
    mutate(
      eval_cond  = factor(eval_cond, levels = COND_LEVELS),
      train_cond = factor(ifelse(is.na(train_cond), "none", train_cond),
                          levels = c("none", TRAINABLE_CONDITIONS, "mix")),
      language   = factor(language, levels = LANGUAGES),
      adapter_arch = factor(adapter_arch, levels = ARCHS),
      base_model = factor(base_model),
      snippet_id = factor(snippet_id),
      family = case_when(
        eval_cond %in% IDENTIFIER_FAMILY ~ "identifier",
        eval_cond %in% STRUCTURAL_FAMILY ~ "structural",
        eval_cond == HELDOUT_CONDITION   ~ "heldout",
        TRUE ~ "none"
      ),
      correct = as.integer(correct)
    )
  trials
}

analysis_set <- function(trials) {
  # is_core marks the rows the design intends to analyse; anything else (debug cells,
  # re-runs) stays in the table for provenance but out of the models.
  out <- trials %>% filter(is_core == 1)
  # H1 rows are only admissible when they carry the access purpose that logged them.
  bad_h1 <- out %>% filter(eval_cond == HELDOUT_CONDITION, is.na(h1_access_purpose))
  if (nrow(bad_h1) > 0) {
    stop(nrow(bad_h1), " H1 trials lack h1_access_purpose — refusing to analyse ",
         "unlogged held-out evaluations (CLAUDE.md 3.2)")
  }
  out
}

if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  trials <- load_trials()
  core <- analysis_set(trials)
  message(sprintf("ingested %d trials (%d core) | %d models | %d programs",
                  nrow(trials), nrow(core),
                  dplyr::n_distinct(core$base_model), dplyr::n_distinct(core$snippet_id)))
  emit(core %>% count(base_model, language, train_cond, eval_cond, name = "n"),
       "00_cell_counts", "00_ingest.R", "trial counts per analysis cell")
}
