#!/usr/bin/env Rscript
# One-shot ampute chain for V07 parity (stdin: JSON path, stdout: JSON result).

`%||%` <- function(x, y) if (is.null(x)) y else x

suppressPackageStartupMessages({
  library(mice)
  library(MASS)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("usage: r_ampute.R <payload.json>")
}

payload <- fromJSON(args[1], simplifyVector = FALSE)
seed <- as.integer(payload$seed %||% 2016L)
testdata_path <- payload$testdata_path
chain <- payload$chain

set.seed(seed)
invisible(
  mvrnorm(
    n = 10000,
    mu = c(10, 5, 0),
    Sigma = matrix(c(1.0, 0.2, 0.2, 0.2, 1.0, 0.2, 0.2, 0.2, 1.0), nrow = 3, byrow = TRUE)
  )
)
testdata <- as.data.frame(read.csv(testdata_path, check.names = FALSE))

as_args <- function(spec) {
  out <- list()
  if (!is.null(spec$prop)) out$prop <- as.numeric(spec$prop)
  if (!is.null(spec$bycases)) out$bycases <- as.logical(spec$bycases)
  if (!is.null(spec$mech)) out$mech <- spec$mech
  if (!is.null(spec$cont)) out$cont <- as.logical(spec$cont)
  if (!is.null(spec$run)) out$run <- as.logical(spec$run)
  if (!is.null(spec$type)) out$type <- unlist(spec$type)
  if (!is.null(spec$freq)) out$freq <- as.numeric(unlist(spec$freq))
  if (!is.null(spec$patterns)) {
    pat <- spec$patterns
    if (is.list(pat[[1]])) {
      out$patterns <- do.call(rbind, lapply(pat, function(row) as.integer(unlist(row))))
    } else {
      out$patterns <- matrix(as.integer(unlist(pat)), nrow = 1)
    }
  }
  if (!is.null(spec$weights)) {
    w <- spec$weights
    if (is.list(w[[1]])) {
      out$weights <- do.call(rbind, lapply(w, function(row) as.numeric(unlist(row))))
    } else {
      out$weights <- matrix(as.numeric(unlist(w)), nrow = 1)
    }
  }
  out
}

run_one <- function(spec) {
  call_args <- as_args(spec)
  run_flag <- call_args$run %||% TRUE
  if (identical(run_flag, FALSE)) {
    res <- do.call(ampute, c(list(data = testdata, run = FALSE), call_args))
    return(list(
      amp = NULL,
      prop = res$prop,
      mech = res$mech,
      patterns = as.matrix(res$patterns),
      freq = as.numeric(res$freq),
      bycases = res$bycases
    ))
  }
  res <- do.call(ampute, c(list(data = testdata), call_args))
  list(
    amp = as.matrix(res$amp),
    prop = res$prop,
    mech = res$mech,
    patterns = as.matrix(res$patterns),
    freq = as.numeric(res$freq),
    bycases = res$bycases,
    weights = if (!is.null(res$weights)) as.matrix(res$weights) else NULL
  )
}

results <- lapply(chain, run_one)
cat(toJSON(list(results = results), auto_unbox = TRUE, digits = 10))