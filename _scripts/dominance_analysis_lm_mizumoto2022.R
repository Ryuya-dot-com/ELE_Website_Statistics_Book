#!/usr/bin/env Rscript

# Dominance analysis script (multiple regression version)
# Reference:
# Mizumoto, A. (2022). Language Learning, 73(1), 161-196.
# OSF supplementary code: https://osf.io/uxdwh/

required_pkgs <- c("MASS", "dominanceanalysis", "dplyr", "tidyr", "tibble", "ggplot2")
missing_pkgs <- required_pkgs[!vapply(required_pkgs, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_pkgs) > 0) {
  stop(
    "Missing packages: ", paste(missing_pkgs, collapse = ", "),
    "\nInstall them first, e.g. install.packages(c(",
    paste(sprintf('"%s"', missing_pkgs), collapse = ", "),
    "))"
  )
}

suppressPackageStartupMessages({
  library(MASS)
  library(dominanceanalysis)
  library(dplyr)
  library(tidyr)
  library(tibble)
  library(ggplot2)
})


# ---- Data generator (Table 1 style in Mizumoto, 2022) ---------------------

simulate_mizumoto_table1_data <- function(n = 100, seed = 88, empirical = TRUE) {
  correl <- matrix(
    c(
      1, 0.62, 0.43, 0.56, 0.61,
      0.62, 1, 0.67, 0.55, 0.72,
      0.43, 0.67, 1, 0.67, 0.65,
      0.56, 0.55, 0.67, 1, 0.79,
      0.61, 0.72, 0.65, 0.79, 1
    ),
    nrow = 5,
    dimnames = list(
      c("Speaking", "Vocabulary", "Grammar", "Writing", "Reading"),
      c("Speaking", "Vocabulary", "Grammar", "Writing", "Reading")
    )
  )

  set.seed(seed)
  sim <- MASS::mvrnorm(
    n = n,
    mu = rep(0, ncol(correl)),
    Sigma = correl,
    empirical = empirical
  )

  tibble::as_tibble(sim) |>
    setNames(colnames(correl))
}


# ---- Dominance analysis pipeline ------------------------------------------

run_dominance_lm <- function(
    data,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading")
) {
  data <- as.data.frame(data)

  needed <- c(outcome, predictors)
  missing_cols <- setdiff(needed, names(data))
  if (length(missing_cols) > 0) {
    stop("Columns not found in `data`: ", paste(missing_cols, collapse = ", "))
  }

  fml <- stats::reformulate(predictors, response = outcome)
  # dominanceanalysis uses model call inspection to retrieve original data.
  # To avoid getData() failures inside user-defined functions, place data
  # temporarily in .GlobalEnv with a symbol name.
  tmp_data_name <- paste0(".da_data_", as.integer(Sys.time()), "_", sample.int(1e6, 1))
  assign(tmp_data_name, data, envir = .GlobalEnv)
  on.exit(rm(list = tmp_data_name, envir = .GlobalEnv), add = TRUE)

  lm_fit <- eval(bquote(stats::lm(.(fml), data = .(as.name(tmp_data_name)))))

  da_fit <- dominanceanalysis::dominanceAnalysis(lm_fit)

  # General dominance weights
  avg <- dominanceanalysis::averageContribution(da_fit)$r2
  weights_tbl <- tibble(
    predictor = names(avg),
    general_dominance = as.numeric(avg)
  ) |>
    arrange(desc(general_dominance))

  # Contribution by level
  by_level_tbl <- dominanceanalysis::contributionByLevel(da_fit)$r2 |>
    as_tibble() |>
    pivot_longer(
      cols = -level,
      names_to = "predictor",
      values_to = "contribution"
    )

  list(
    formula = fml,
    lm_fit = lm_fit,
    dominance_fit = da_fit,
    weights_tbl = weights_tbl,
    by_level_tbl = by_level_tbl
  )
}


# ---- Plot helpers ----------------------------------------------------------

plot_dominance_weights <- function(weights_tbl, base_size = 12) {
  ggplot(weights_tbl, aes(x = reorder(predictor, general_dominance), y = general_dominance)) +
    geom_col(fill = "#2C7FB8", alpha = 0.9) +
    geom_text(aes(label = round(general_dominance, 3)), hjust = -0.1, size = 3.3) +
    coord_flip() +
    expand_limits(y = max(weights_tbl$general_dominance) * 1.12) +
    labs(
      title = "General Dominance Weights (LM)",
      subtitle = "Mizumoto (2022)-style variable-importance summary",
      x = "Predictor",
      y = "Dominance weight"
    ) +
    theme_bw(base_size = base_size)
}

plot_dominance_by_level <- function(by_level_tbl, base_size = 12) {
  ggplot(by_level_tbl, aes(x = factor(level), y = contribution, fill = predictor)) +
    geom_col(position = "dodge", width = 0.8) +
    labs(
      title = "Dominance Contribution by Model Size",
      subtitle = "How each predictor contributes across subset levels",
      x = "Model level (number of predictors in subset)",
      y = "Contribution"
    ) +
    theme_bw(base_size = base_size) +
    theme(legend.position = "bottom")
}


# ---- Example run -----------------------------------------------------------

if (sys.nframe() == 0) {
  dat <- simulate_mizumoto_table1_data(n = 100, seed = 88)

  res <- run_dominance_lm(
    data = dat,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading")
  )

  cat("\n[LM summary]\n")
  print(summary(res$lm_fit))

  cat("\n[General dominance weights]\n")
  print(res$weights_tbl)

  dir.create("output", showWarnings = FALSE, recursive = TRUE)

  write.csv(res$weights_tbl, "output/dominance_lm_weights.csv", row.names = FALSE)
  write.csv(res$by_level_tbl, "output/dominance_lm_by_level.csv", row.names = FALSE)

  p_weights <- plot_dominance_weights(res$weights_tbl)
  p_levels <- plot_dominance_by_level(res$by_level_tbl)

  ggplot2::ggsave("output/dominance_lm_weights.png", p_weights, width = 8, height = 5, dpi = 150)
  ggplot2::ggsave("output/dominance_lm_by_level.png", p_levels, width = 9, height = 5.5, dpi = 150)

  cat("\nSaved:\n")
  cat("- output/dominance_lm_weights.csv\n")
  cat("- output/dominance_lm_by_level.csv\n")
  cat("- output/dominance_lm_weights.png\n")
  cat("- output/dominance_lm_by_level.png\n")
}
