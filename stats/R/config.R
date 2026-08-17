# Shared configuration for the obtune GLMM stack.
# Adapted from model_understanding_dualsystem/stats/R/config.R (Papers 2-3), so that
# obtune results enter the same analytical frame as the behavioural work they extend.

SEED <- 42
set.seed(SEED)

PROJECT_ROOT <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), "..", ".."),
                              mustWork = FALSE)
if (!dir.exists(file.path(PROJECT_ROOT, "src"))) {
  PROJECT_ROOT <- normalizePath(".", mustWork = FALSE)
}

PATHS <- list(
  trials      = file.path(PROJECT_ROOT, "results", "trials.parquet"),
  attention   = file.path(PROJECT_ROOT, "results", "attn", "attention_metrics.parquet"),
  human_p2    = file.path(PROJECT_ROOT, "data", "human", "paper2_graded.csv"),
  human_p3    = file.path(PROJECT_ROOT, "data", "human", "paper3_graded.csv"),
  coverage    = file.path(PROJECT_ROOT, "data", "manifests", "coverage_matrix_testset.json"),
  outputs     = file.path(PROJECT_ROOT, "stats", "outputs"),
  figures     = file.path(PROJECT_ROOT, "stats", "outputs", "figures"),
  tables      = file.path(PROJECT_ROOT, "stats", "outputs", "tables")
)

# The condition ladder. Order matters: it sets the factor levels used in every model
# and figure, and L0 is the reference level (the untransformed control).
# S3/S4 are the two halves of S2, split out on 2026-08-09 (paths.TRAINABLE_CONDITIONS
# went 6 -> 8). This list did not follow, so 01_schema_validate.R would have rejected
# EVERY S3/S4 trial with "unknown eval_cond" the first time the R stack was run over
# the new cells. Keep in sync with src/obtune/paths.py::TRAINABLE_CONDITIONS.
COND_LEVELS <- c("L0", "L1r", "L1b", "L2", "S1", "S2", "S3", "S4", "H1")
TRAINABLE_CONDITIONS <- setdiff(COND_LEVELS, "H1")
IDENTIFIER_FAMILY <- c("L1r", "L1b", "L2")
STRUCTURAL_FAMILY <- c("S1", "S2")
HELDOUT_CONDITION <- "H1"

LANGUAGES <- c("python", "javascript")
# `oracle_route` is deliberately its OWN level, not `per_type`: 03_rq1_transfer.R selects
# the transfer matrix with `adapter_arch == "per_type"`, so labelling the oracle-routed
# system per_type would sweep an RQ2 upper-bound system into the RQ1 headline result.
ARCHS <- c("none", "oracle_prompt", "mono", "per_type", "router", "oracle_route",
           "merge_linear", "merge_ties", "merge_dare_ties", "merge_dare_linear", "knockout")

# Multiplicity policy: BH-FDR *within* each research question, treating the whole
# transfer matrix as one family (design doc 5.2). Correcting per-row would understate
# the multiplicity; correcting across RQs would overstate it.
FDR_METHOD <- "BH"
ALPHA <- 0.05

# Transfer Ratio is unstable when the denominator (the self-tuned gain) is small, so it
# is reported only above this gain with a CI excluding zero; otherwise the cell is
# undefined and excluded from averages rather than plotted as a large number.
TR_MIN_SELF_GAIN_PTS <- 3
BOOTSTRAP_R <- 2000       # cluster bootstrap over program_id
PERMUTATIONS <- 5000      # RQ3: n(base models) is small, asymptotic p is not trustworthy

`%||%` <- function(a, b) if (is.null(a)) b else a
