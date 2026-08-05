# 02 — the backbone GLMM every research question refits or contrasts against.
#
#   correct ~ train_cond * eval_cond * language + (1 | snippet_id) + (1 | base_model)
#
# Crossed random effects for program and model: the same programs are seen by every
# model, so treating trials as independent would badly understate the intervals. This
# is the same specification as the Papers-2/3 stack, so obtune's effects are directly
# comparable to the behavioural results it extends.

source(file.path("stats", "R", "01_schema_validate.R"))

suppressMessages(library(glmmTMB))

fit_backbone <- function(core, subset_common = TRUE) {
  d <- core %>% filter(adapter_arch %in% c("none", "per_type", "mono"))
  if (subset_common) d <- common_subset(d)
  d <- droplevels(d)

  # Singular fits are common when a random-effect grouping has few levels (3 base
  # models). We fit anyway and report the variance components so the reader can see
  # it, rather than silently dropping the term.
  glmmTMB(
    correct ~ train_cond * eval_cond * language + (1 | snippet_id) + (1 | base_model),
    family = binomial(), data = d
  )
}

variance_components <- function(model) {
  vc <- glmmTMB::VarCorr(model)$cond
  tibble(
    group = names(vc),
    variance = vapply(vc, function(v) as.numeric(v[1, 1]), numeric(1)),
    sd = vapply(vc, function(v) sqrt(as.numeric(v[1, 1])), numeric(1))
  )
}

if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  trials <- load_trials()
  core <- analysis_set(trials)
  model <- fit_backbone(core)
  saveRDS(model, file.path(PATHS$outputs, "backbone.rds"))

  co <- summary(model)$coefficients$cond
  emit(tibble(term = rownames(co), estimate = co[, 1], se = co[, 2],
              z = co[, 3], p_value = co[, 4]) %>% add_fdr(),
       "02_backbone_coefficients", "02_backbone.R",
       "fixed effects of the backbone binomial GLMM")
  emit(variance_components(model), "02_variance_components", "02_backbone.R",
       "random-effect variances (snippet_id, base_model)")
  message("backbone fitted: ", nobs(model), " observations, AIC ", round(AIC(model), 1))
}
