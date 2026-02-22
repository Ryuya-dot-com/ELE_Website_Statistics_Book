#!/usr/bin/env Rscript

# Random-forest variable-importance script (Mizumoto, 2022 inspired)
# Reference:
# Mizumoto, A. (2022). Language Learning, 73(1), 161-196.
# OSF supplementary code: https://osf.io/uxdwh/

required_pkgs <- c("MASS", "randomForest", "dplyr", "tidyr", "tibble", "ggplot2")
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
  library(randomForest)
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


# ---- Random forest importance pipeline ------------------------------------

run_rf_importance <- function(
    data,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading"),
    ntree = 1000,
    mtry = NULL,
    seed = 88
) {
  needed <- c(outcome, predictors)
  missing_cols <- setdiff(needed, names(data))
  if (length(missing_cols) > 0) {
    stop("Columns not found in `data`: ", paste(missing_cols, collapse = ", "))
  }

  if (is.null(mtry)) {
    mtry <- max(1, floor(sqrt(length(predictors))))
  }

  set.seed(seed)
  fml <- stats::reformulate(predictors, response = outcome)
  rf_fit <- randomForest::randomForest(
    formula = fml,
    data = data,
    ntree = ntree,
    mtry = mtry,
    importance = TRUE
  )

  raw_imp <- randomForest::importance(rf_fit) |>
    as.data.frame(check.names = FALSE) |>
    tibble::rownames_to_column("predictor")

  acc_col <- intersect(c("%IncMSE", "MeanDecreaseAccuracy"), names(raw_imp))[1]
  purity_col <- intersect(c("IncNodePurity", "MeanDecreaseGini"), names(raw_imp))[1]

  if (is.na(acc_col) || is.na(purity_col)) {
    stop(
      "Could not find expected importance columns in randomForest output.\n",
      "Available columns: ", paste(names(raw_imp), collapse = ", ")
    )
  }

  imp_tbl <- raw_imp |>
    transmute(
      predictor = predictor,
      importance_accuracy = .data[[acc_col]],
      importance_purity = .data[[purity_col]]
    ) |>
    arrange(desc(importance_accuracy))

  oob_tbl <- tibble(
    tree = seq_along(rf_fit$mse),
    oob_mse = rf_fit$mse
  )

  list(
    formula = fml,
    rf_fit = rf_fit,
    importance_tbl = imp_tbl,
    oob_tbl = oob_tbl
  )
}


run_rf_importance_repeated <- function(
    data,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading"),
    ntree = 1000,
    mtry = NULL,
    n_repeats = 50,
    seed_start = 88
) {
  all_runs <- lapply(seq_len(n_repeats), function(i) {
    one <- run_rf_importance(
      data = data,
      outcome = outcome,
      predictors = predictors,
      ntree = ntree,
      mtry = mtry,
      seed = seed_start + i - 1
    )
    one$importance_tbl |>
      mutate(repeat_id = i)
  })

  bind_rows(all_runs) |>
    group_by(predictor) |>
    summarise(
      mean_importance_accuracy = mean(importance_accuracy),
      sd_importance_accuracy = stats::sd(importance_accuracy),
      mean_importance_purity = mean(importance_purity),
      sd_importance_purity = stats::sd(importance_purity),
      .groups = "drop"
    ) |>
    arrange(desc(mean_importance_accuracy))
}


# ---- Plot helpers ----------------------------------------------------------

plot_rf_importance <- function(importance_tbl, metric = c("accuracy", "purity"), base_size = 12) {
  metric <- match.arg(metric)
  col_name <- if (metric == "accuracy") "importance_accuracy" else "importance_purity"
  y_label <- if (metric == "accuracy") "%IncMSE / Accuracy-based importance" else "Node-purity importance"

  ggplot(importance_tbl, aes(x = reorder(predictor, .data[[col_name]]), y = .data[[col_name]])) +
    geom_col(fill = "#1B9E77", alpha = 0.9) +
    geom_text(aes(label = round(.data[[col_name]], 3)), hjust = -0.1, size = 3.3) +
    coord_flip() +
    expand_limits(y = max(importance_tbl[[col_name]]) * 1.12) +
    labs(
      title = "Random Forest Variable Importance",
      subtitle = paste0("Metric: ", col_name),
      x = "Predictor",
      y = y_label
    ) +
    theme_bw(base_size = base_size)
}

plot_oob_curve <- function(oob_tbl, base_size = 12) {
  ggplot(oob_tbl, aes(x = tree, y = oob_mse)) +
    geom_line(color = "#2C7FB8", linewidth = 0.8) +
    labs(
      title = "OOB Error Curve (Random Forest Regression)",
      x = "Number of trees",
      y = "OOB MSE"
    ) +
    theme_bw(base_size = base_size)
}


# ---- Example run -----------------------------------------------------------

if (sys.nframe() == 0) {
  dat <- simulate_mizumoto_table1_data(n = 100, seed = 88)

  rf_res <- run_rf_importance(
    data = dat,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading"),
    ntree = 1000,
    seed = 88
  )

  cat("\n[Random forest fit]\n")
  print(rf_res$rf_fit)

  cat("\n[Single-run variable importance]\n")
  print(rf_res$importance_tbl)

  rf_rep <- run_rf_importance_repeated(
    data = dat,
    outcome = "Speaking",
    predictors = c("Vocabulary", "Grammar", "Writing", "Reading"),
    ntree = 1000,
    n_repeats = 50,
    seed_start = 88
  )

  cat("\n[Repeated-run stability summary]\n")
  print(rf_rep)

  dir.create("output", showWarnings = FALSE, recursive = TRUE)

  write.csv(rf_res$importance_tbl, "output/rf_importance_single_run.csv", row.names = FALSE)
  write.csv(rf_rep, "output/rf_importance_repeated_summary.csv", row.names = FALSE)

  p_imp_acc <- plot_rf_importance(rf_res$importance_tbl, metric = "accuracy")
  p_imp_purity <- plot_rf_importance(rf_res$importance_tbl, metric = "purity")
  p_oob <- plot_oob_curve(rf_res$oob_tbl)

  ggplot2::ggsave("output/rf_importance_accuracy.png", p_imp_acc, width = 8, height = 5, dpi = 150)
  ggplot2::ggsave("output/rf_importance_purity.png", p_imp_purity, width = 8, height = 5, dpi = 150)
  ggplot2::ggsave("output/rf_oob_curve.png", p_oob, width = 8, height = 5, dpi = 150)

  cat("\nSaved:\n")
  cat("- output/rf_importance_single_run.csv\n")
  cat("- output/rf_importance_repeated_summary.csv\n")
  cat("- output/rf_importance_accuracy.png\n")
  cat("- output/rf_importance_purity.png\n")
  cat("- output/rf_oob_curve.png\n")
}

