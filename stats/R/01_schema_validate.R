# 01 — schema gate. Mirrors src/obtune/schema.py::TrialRow.
# Runs before any model is fitted: a silently mis-typed column would otherwise surface
# as a strange coefficient rather than as an error, and the H1 checks here are the
# statistical-side half of the quarantine discipline.

source(file.path("stats", "R", "00_ingest.R"))

REQUIRED_COLS <- c(
  "run_id", "seed", "phase", "experiment_id", "base_model", "model_family",
  "adapter_id", "adapter_arch", "train_cond", "eval_cond", "language", "dataset",
  "snippet_id", "item_id", "is_core", "h1_access_purpose", "correct", "parse_ok",
  "grade_method"
)

validate_trials <- function(trials) {
  problems <- character()

  missing <- setdiff(REQUIRED_COLS, names(trials))
  if (length(missing)) problems <- c(problems, paste("missing columns:", paste(missing, collapse = ", ")))

  bad_cond <- setdiff(unique(as.character(trials$eval_cond)), COND_LEVELS)
  if (length(bad_cond)) problems <- c(problems, paste("unknown eval_cond:", paste(bad_cond, collapse = ", ")))

  bad_arch <- setdiff(unique(as.character(trials$adapter_arch)), ARCHS)
  if (length(bad_arch)) problems <- c(problems, paste("unknown adapter_arch:", paste(bad_arch, collapse = ", ")))

  if (any(!trials$correct %in% c(0L, 1L))) problems <- c(problems, "correct must be 0/1")

  # H1 must never appear as a TRAINING condition — the whole invariance claim rests on
  # it being unseen, and a mislabelled row here would be invisible in the results.
  if (any(as.character(trials$train_cond) == "H1", na.rm = TRUE)) {
    problems <- c(problems, "H1 appears as a train_cond — held-out condition was trained on")
  }

  h1_unlogged <- sum(trials$eval_cond == HELDOUT_CONDITION & is.na(trials$h1_access_purpose))
  if (h1_unlogged > 0) {
    problems <- c(problems, sprintf("%d H1 trials without h1_access_purpose", h1_unlogged))
  }

  # A tuned system must actually differ from the base, or the adapter never applied.
  arch_train <- trials %>%
    filter(adapter_arch %in% c("per_type", "mono")) %>%
    filter(is.na(adapter_id) | adapter_id == "")
  if (nrow(arch_train) > 0) {
    problems <- c(problems, sprintf("%d tuned rows have no adapter_id", nrow(arch_train)))
  }

  # Split hygiene: nothing from the training split may be scored.
  if ("split" %in% names(trials) && any(trials$split == "train", na.rm = TRUE)) {
    problems <- c(problems, "train-split rows present in the analysis set")
  }

  problems
}

if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  trials <- load_trials()
  core <- analysis_set(trials)
  problems <- validate_trials(core)
  if (length(problems)) {
    for (p in problems) message("  SCHEMA FAIL: ", p)
    stop("schema validation failed (", length(problems), " problem(s))")
  }
  message("schema OK: ", nrow(core), " core trials")
  emit(tibble(check = "schema", status = "ok", n_core = nrow(core),
              n_models = dplyr::n_distinct(core$base_model),
              n_programs = dplyr::n_distinct(core$snippet_id)),
       "01_schema_status", "01_schema_validate.R", "schema gate result")
}
