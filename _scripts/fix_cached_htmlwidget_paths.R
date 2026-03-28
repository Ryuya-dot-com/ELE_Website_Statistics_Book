#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
project_root <- if (length(args) >= 1) args[[1]] else "."

dt_lib_root <- system.file("htmlwidgets/lib", package = "DT")
if (!nzchar(dt_lib_root)) {
  stop("DT htmlwidgets lib path not found.", call. = FALSE)
}
dt_lib_root <- normalizePath(dt_lib_root, winslash = "/", mustWork = TRUE)

rdata_files <- Sys.glob(file.path(project_root, "*_cache", "html", "*.RData"))
patched_files <- 0L
patched_dependencies <- 0L

for (rdata_file in rdata_files) {
  cache_env <- new.env(parent = emptyenv())
  loaded <- try(load(rdata_file, envir = cache_env), silent = TRUE)
  if (inherits(loaded, "try-error")) {
    next
  }

  changed <- FALSE
  for (name in ls(cache_env, all.names = TRUE)) {
    obj <- get(name, envir = cache_env)
    if (!is.list(obj) || !length(obj) || !all(vapply(obj, is.list, logical(1)))) {
      next
    }

    for (i in seq_along(obj)) {
      dep <- obj[[i]]
      src_file <- dep$src$file
      if (is.null(src_file) || !is.character(src_file) || length(src_file) != 1) {
        next
      }
      match <- regexec("DT/htmlwidgets/lib/([^/]+)$", src_file)
      captures <- regmatches(src_file, match)[[1]]
      if (length(captures) != 2) {
        next
      }

      dep_dir <- captures[[2]]
      dt_dep_path <- system.file(file.path("htmlwidgets/lib", dep_dir), package = "DT")
      if (!nzchar(dt_dep_path)) {
        next
      }
      dt_dep_path <- normalizePath(dt_dep_path, winslash = "/", mustWork = TRUE)
      if (identical(src_file, dt_dep_path)) {
        next
      }

      obj[[i]]$src$file <- dt_dep_path
      patched_dependencies <- patched_dependencies + 1L
      changed <- TRUE
    }

    if (changed) {
      assign(name, obj, envir = cache_env)
    }
  }

  if (!changed) {
    next
  }

  save(list = ls(cache_env, all.names = TRUE), file = rdata_file, envir = cache_env, compress = TRUE)
  patched_files <- patched_files + 1L
  cat(sprintf("[fix_cached_htmlwidget_paths] Patched %s\n", rdata_file))
}

cat(
  sprintf(
    "[fix_cached_htmlwidget_paths] Patched %d dependency entries across %d cache file(s).\n",
    patched_dependencies,
    patched_files
  )
)
