#!/usr/bin/env Rscript
# Univariate pan::pan call matching mice.impute.2l.pan internals.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("usage: r_pan_impute.R <workdir>")
}
workdir <- args[[1]]
read_vec <- function(name) as.numeric(readLines(file.path(workdir, name)))
read_mat <- function(name) as.matrix(read.csv(file.path(workdir, name), header = FALSE))

y <- read_vec("y.txt")
subj <- as.integer(read_vec("subj.txt"))
pred <- read_mat("pred.txt")
zcol <- as.integer(read_vec("zcol.txt")) + 1L
n_iter <- as.integer(read_vec("n_iter.txt"))
pan_seed <- as.integer(read_vec("pan_seed.txt"))

suppressPackageStartupMessages(library(pan))

y1 <- matrix(y, ncol = 1)
miss <- !is.finite(y1[, 1])
y1[miss, 1] <- NA

xcol <- seq_len(ncol(pred))
q <- length(zcol)
prior <- list(
  a = 1L,
  Binv = diag(1, 1),
  c = q,
  Dinv = diag(rep(1, q))
)

imput <- pan(y1, subj, pred, xcol, zcol, prior, seed = pan_seed, iter = n_iter)
out <- imput$y
if (any(!is.finite(out[miss]))) {
  stop("pan left missing imputations")
}
writeLines(as.character(out), file.path(workdir, "out.txt"))