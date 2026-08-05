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
COND_LEVELS <- c("L0", "L1r", "L1b", "L2", "S1", "S2", "H1")
TRAINABLE_CONDITIONS <- setdiff(COND_LEVELS, "H1")
IDENTIFIER_FAMILY <- c("L1r", "L1b", "L2")
STRUCTURAL_FAMILY <- c("S1", "S2")
HELDOUT_CONDITION <- "H1"

LANGUAGES <- c("python", "javascript")
ARCHS <- c("none", "oracle_prompt", "mono", "per_type", "router",
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
