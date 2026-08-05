# 03 — RQ1: the transfer matrix, Transfer Ratio, and the Invariance Index.
#
# TR(i->j) = (acc_j(tuned_i) - acc_j(base)) / (acc_j(tuned_j) - acc_j(base))
#
# The denominator is the self-tuned gain. When it is small the ratio explodes, so TR is
# reported ONLY where that gain clears TR_MIN_SELF_GAIN_PTS with a bootstrap CI
# excluding zero; otherwise the cell is `undefined` and excluded from averages rather
# than plotted as a large, meaningless number. Raw delta-accuracy accompanies every TR.

source(file.path("stats", "R", "02_backbone.R"))

cell_table <- function(core, restrict_common = TRUE) {
  d <- core
  if (restrict_common) d <- common_subset(d)
  d %>% cell_accuracy(base_model, language, adapter_arch, train_cond, eval_cond)
}

#' Per (model, language, eval_cond): base accuracy and each tuned system's accuracy.
transfer_matrix <- function(core, restrict_common = TRUE) {
  cells <- cell_table(core, restrict_common)
  base <- cells %>%
    filter(adapter_arch == "none") %>%
    select(base_model, language, eval_cond, acc_base = estimate, n_base = n, k_base = k)
  tuned <- cells %>%
    filter(adapter_arch == "per_type", train_cond != "none") %>%
    select(base_model, language, train_cond, eval_cond,
           acc_tuned = estimate, n_tuned = n, k_tuned = k)
  tuned %>%
    left_join(base, by = c("base_model", "language", "eval_cond")) %>%
    mutate(delta_pts = 100 * (acc_tuned - acc_base))
}

#' Self-gain per (model, language, condition) — the TR denominator — with a cluster
#' bootstrap CI over programs.
self_gains <- function(core, restrict_common = TRUE) {
  d <- if (restrict_common) common_subset(core) else core
  keys <- d %>%
    filter(adapter_arch == "per_type", as.character(train_cond) == as.character(eval_cond)) %>%
    distinct(base_model, language, eval_cond)

  purrr_rows <- lapply(seq_len(nrow(keys)), function(i) {
    k <- keys[i, ]
    sub <- d %>% filter(base_model == k$base_model, language == k$language,
                        eval_cond == k$eval_cond,
                        (adapter_arch == "none") |
                          (adapter_arch == "per_type" & as.character(train_cond) == as.character(k$eval_cond)))
    if (dplyr::n_distinct(sub$adapter_arch) < 2) return(NULL)
    stat <- function(df) {
      a <- df %>% filter(adapter_arch == "per_type") %>% pull(correct)
      b <- df %>% filter(adapter_arch == "none") %>% pull(correct)
      if (!length(a) || !length(b)) return(NA_real_)
      100 * (mean(a) - mean(b))
    }
    bs <- cluster_bootstrap(sub, stat)
    tibble(base_model = k$base_model, language = k$language, eval_cond = k$eval_cond,
           self_gain_pts = bs$estimate, self_lo = bs$lower, self_hi = bs$upper,
           bootstrap_R = bs$R)
  })
  bind_rows(Filter(Negate(is.null), purrr_rows)) %>%
    mutate(denominator_ok = is.finite(self_gain_pts) &
             self_gain_pts >= TR_MIN_SELF_GAIN_PTS &
             is.finite(self_lo) & self_lo > 0)
}

transfer_ratios <- function(core, restrict_common = TRUE) {
  tm <- transfer_matrix(core, restrict_common)
  sg <- self_gains(core, restrict_common) %>%
    select(base_model, language, eval_cond, self_gain_pts, self_lo, self_hi, denominator_ok)
  tm %>%
    left_join(sg, by = c("base_model", "language", "eval_cond")) %>%
    mutate(
      transfer_ratio = ifelse(denominator_ok %in% TRUE, delta_pts / self_gain_pts, NA_real_),
      tr_status = case_when(
        is.na(denominator_ok) ~ "no_self_tuned_cell",
        !denominator_ok ~ "undefined_small_denominator",
        TRUE ~ "defined"
      )
    )
}

#' Invariance Index = mean over training conditions of transfer onto H1.
#' Reported BOTH as raw delta-H1 points (primary — H1 has no self-tuned denominator,
#' so a normalized TR would need a proxy) and normalized by the monolithic H1 gain.
invariance_index <- function(core, restrict_common = TRUE) {
  d <- if (restrict_common) common_subset(core) else core
  h1 <- d %>% filter(eval_cond == HELDOUT_CONDITION)
  if (!nrow(h1)) return(tibble())

  base_acc <- h1 %>% filter(adapter_arch == "none") %>%
    group_by(base_model, language) %>% summarise(acc_base = mean(correct), .groups = "drop")
  mono_acc <- h1 %>% filter(adapter_arch == "mono") %>%
    group_by(base_model, language) %>% summarise(acc_mono = mean(correct), .groups = "drop")

  per_cond <- h1 %>%
    filter(adapter_arch == "per_type") %>%
    group_by(base_model, language, train_cond) %>%
    summarise(acc_tuned = mean(correct), n = n(), .groups = "drop") %>%
    left_join(base_acc, by = c("base_model", "language")) %>%
    mutate(delta_h1_pts = 100 * (acc_tuned - acc_base))

  stat <- function(df) {
    a <- df %>% filter(adapter_arch == "per_type") %>% pull(correct)
    b <- df %>% filter(adapter_arch == "none") %>% pull(correct)
    if (!length(a) || !length(b)) return(NA_real_)
    100 * (mean(a) - mean(b))
  }
  boots <- lapply(split(h1, list(h1$base_model, h1$language), drop = TRUE), function(sub) {
    bs <- cluster_bootstrap(sub, stat)
    tibble(base_model = sub$base_model[1], language = sub$language[1],
           mean_delta_h1_pts = bs$estimate, lo = bs$lower, hi = bs$upper, bootstrap_R = bs$R)
  })

  per_cond %>%
    group_by(base_model, language) %>%
    summarise(invariance_index_pts = mean(delta_h1_pts, na.rm = TRUE),
              n_train_conditions = n(), .groups = "drop") %>%
    left_join(bind_rows(boots), by = c("base_model", "language")) %>%
    left_join(mono_acc, by = c("base_model", "language")) %>%
    left_join(base_acc, by = c("base_model", "language")) %>%
    mutate(mono_gain_pts = 100 * (acc_mono - acc_base),
           invariance_index_normalized = ifelse(is.finite(mono_gain_pts) & mono_gain_pts > 0,
                                                invariance_index_pts / mono_gain_pts, NA_real_))
}

#' Item-level test of each transfer cell against base, BH-corrected across the whole
#' matrix as ONE family (design doc 5.2).
transfer_tests <- function(core, restrict_common = TRUE) {
  d <- if (restrict_common) common_subset(core) else core
  keys <- d %>% filter(adapter_arch == "per_type") %>%
    distinct(base_model, language, train_cond, eval_cond)
  rows <- lapply(seq_len(nrow(keys)), function(i) {
    k <- keys[i, ]
    tuned <- d %>% filter(base_model == k$base_model, language == k$language,
                          adapter_arch == "per_type", train_cond == k$train_cond,
                          eval_cond == k$eval_cond) %>% arrange(item_id)
    base <- d %>% filter(base_model == k$base_model, language == k$language,
                         adapter_arch == "none", eval_cond == k$eval_cond) %>% arrange(item_id)
    shared <- intersect(tuned$item_id, base$item_id)
    if (length(shared) < 5) return(NULL)
    a <- tuned$correct[match(shared, tuned$item_id)]
    b <- base$correct[match(shared, base$item_id)]
    mc <- mcnemar_paired(a, b)
    tibble(base_model = k$base_model, language = k$language, train_cond = k$train_cond,
           eval_cond = k$eval_cond, n_items = length(shared),
           gained = mc$b, lost = mc$c, p_value = mc$p)
  })
  out <- bind_rows(Filter(Negate(is.null), rows))
  if (nrow(out)) out <- add_fdr(out)
  out
}

if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  trials <- load_trials()
  core <- analysis_set(trials)

  emit(cell_table(core), "03_cell_accuracy", "03_rq1_transfer.R",
       "accuracy per model x language x system x eval condition (common subset, Wilson CIs)")
  emit(transfer_ratios(core), "03_transfer_matrix", "03_rq1_transfer.R",
       "transfer matrix with TR and its denominator-guard status")
  emit(self_gains(core), "03_self_gains", "03_rq1_transfer.R",
       "self-tuned gains (the TR denominator) with cluster-bootstrap CIs")
  emit(invariance_index(core), "03_invariance_index", "03_rq1_transfer.R",
       "Invariance Index: mean transfer onto the held-out obfuscator")
  emit(transfer_tests(core), "03_transfer_tests", "03_rq1_transfer.R",
       "paired McNemar per transfer cell, BH-FDR across the matrix as one family")
  message("RQ1 complete")
}
