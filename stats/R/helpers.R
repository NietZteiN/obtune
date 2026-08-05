# Shared helpers: the emit() provenance protocol, Wilson intervals, and the cluster
# bootstrap. Ported from the Papers-2/3 stack; emit() is the reproducibility backbone
# and is deliberately kept identical so outputs are comparable across projects.

suppressMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
  library(jsonlite)
})

MANIFEST_ENV <- new.env(parent = emptyenv())
MANIFEST_ENV$entries <- list()

#' Write a result and record it in the run manifest.
#' Every number that reaches the paper goes through here, so `manifest.json` is a
#' complete index of what was produced, by which script, with which row count.
emit <- function(obj, name, script, description = "") {
  dir.create(PATHS$tables, recursive = TRUE, showWarnings = FALSE)
  path <- file.path(PATHS$tables, paste0(name, ".csv"))
  readr::write_csv(obj, path)
  MANIFEST_ENV$entries[[name]] <- list(
    name = name, script = script, description = description,
    path = path, rows = nrow(obj), cols = ncol(obj),
    written_utc = format(Sys.time(), tz = "UTC", usetz = TRUE)
  )
  message(sprintf("  emit %-32s %5d rows  -> %s", name, nrow(obj), basename(path)))
  invisible(obj)
}

write_manifest <- function() {
  dir.create(PATHS$outputs, recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(MANIFEST_ENV$entries,
                       file.path(PATHS$outputs, "manifest.json"),
                       auto_unbox = TRUE, pretty = TRUE)
}

#' Wilson score interval — the cell-level accuracy CI used throughout.
#' Chosen over Wald because cells near 0 or 1 accuracy are common under obfuscation
#' and Wald intervals there are badly behaved (and can leave [0,1]).
wilson_ci <- function(successes, n, conf = 0.95) {
  if (length(n) == 0) return(tibble(estimate = numeric(), lower = numeric(), upper = numeric()))
  z <- stats::qnorm(1 - (1 - conf) / 2)
  phat <- ifelse(n > 0, successes / n, NA_real_)
  denom <- 1 + z^2 / n
  centre <- (phat + z^2 / (2 * n)) / denom
  half <- z * sqrt(phat * (1 - phat) / n + z^2 / (4 * n^2)) / denom
  tibble(estimate = phat,
         lower = pmax(0, centre - half),
         upper = pmin(1, centre + half))
}

#' Cluster bootstrap resampling PROGRAMS, not items.
#' Several input cases share a program and are strongly correlated, so resampling items
#' would understate the interval. Returns percentile bounds of `stat_fn` over resamples.
cluster_bootstrap <- function(df, stat_fn, cluster = "snippet_id", R = BOOTSTRAP_R, conf = 0.95) {
  clusters <- unique(df[[cluster]])
  n <- length(clusters)
  if (n < 2) return(list(estimate = stat_fn(df), lower = NA_real_, upper = NA_real_, R = 0))
  stats <- vapply(seq_len(R), function(i) {
    drawn <- sample(clusters, n, replace = TRUE)
    idx <- unlist(lapply(drawn, function(cl) which(df[[cluster]] == cl)), use.names = FALSE)
    out <- suppressWarnings(stat_fn(df[idx, , drop = FALSE]))
    if (length(out) != 1 || !is.finite(out)) NA_real_ else out
  }, numeric(1))
  stats <- stats[is.finite(stats)]
  a <- (1 - conf) / 2
  list(estimate = stat_fn(df),
       lower = unname(stats::quantile(stats, a, na.rm = TRUE)),
       upper = unname(stats::quantile(stats, 1 - a, na.rm = TRUE)),
       R = length(stats))
}

#' Paired McNemar test for tuned-vs-base on the same items.
mcnemar_paired <- function(correct_a, correct_b) {
  b <- sum(correct_a == 1 & correct_b == 0)
  c <- sum(correct_a == 0 & correct_b == 1)
  if (b + c == 0) return(list(b = b, c = c, p = NA_real_))
  list(b = b, c = c, p = stats::binom.test(b, b + c, 0.5)$p.value)
}

#' BH-FDR over a whole family of tests (see config.R FDR_METHOD).
add_fdr <- function(df, p_col = "p_value", out_col = "q_value") {
  df[[out_col]] <- stats::p.adjust(df[[p_col]], method = FDR_METHOD)
  df
}

#' Restrict a trial table to programs where every listed condition succeeded.
#' Headline transfer numbers use this subset: S1/S2 decline on different programs than
#' the identifier conditions, so a per-condition full set would confound the family
#' contrast with differing program sets.
common_subset <- function(trials, conditions = TRAINABLE_CONDITIONS) {
  have <- trials %>%
    filter(eval_cond %in% conditions) %>%
    distinct(snippet_id, eval_cond) %>%
    count(snippet_id, name = "n_conditions")
  keep <- have$snippet_id[have$n_conditions == length(conditions)]
  trials %>% filter(snippet_id %in% keep)
}

cell_accuracy <- function(trials, ...) {
  trials %>%
    group_by(...) %>%
    summarise(n = n(), k = sum(correct), .groups = "drop") %>%
    bind_cols(wilson_ci(.$k, .$n))
}
