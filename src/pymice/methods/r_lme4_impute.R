#!/usr/bin/env Rscript
# Call mice::mice.impute.2l.lmer / mice.impute.2l.bin via lme4 (optional PyMICE backend).
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("usage: r_lme4_impute.R <workdir>")
}
workdir <- args[[1]]
read_vec <- function(name) as.numeric(readLines(file.path(workdir, name)))
read_mat <- function(name) as.matrix(read.csv(file.path(workdir, name), header = FALSE))

y <- read_vec("y.txt")
ry <- as.logical(read_vec("ry.txt"))
wy <- as.logical(read_vec("wy.txt"))
x <- read_mat("x.txt")
type <- as.integer(read_vec("type.txt"))
method <- trimws(readLines(file.path(workdir, "method.txt"))[1L])
seed <- as.integer(read_vec("seed.txt"))
random_effects <- trimws(readLines(file.path(workdir, "random_effects.txt"))[1L])

suppressPackageStartupMessages({
  library(mice)
  library(lme4)
  library(MASS)
})

set.seed(seed)
colnames(x) <- paste0("V", seq_len(ncol(x)))
names(type) <- colnames(x)

if (method == "lmer") {
  out <- mice.impute.2l.lmer(y, ry, x, type, wy, intercept = TRUE)
} else if (method == "bin") {
  out <- mice.impute.2l.bin(
    y,
    ry,
    x,
    type,
    wy,
    intercept = TRUE,
    random.effects = random_effects
  )
} else {
  stop("unknown method: ", method)
}

writeLines(as.character(out), file.path(workdir, "out.txt"))