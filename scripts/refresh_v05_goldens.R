#!/usr/bin/env Rscript
# Refresh V05 goldens for steps 9.24, 9.25, 16.37 using bundled CSV + factor class.
suppressPackageStartupMessages(library(mice))

capture_block <- function(expr) {
  out <- capture.output(expr)
  cat(paste(out, collapse = "\n"), "\n", sep = "")
  invisible(out)
}

popNCR <- read.csv("tests/data/popNCR.csv")
popNCR$class <- as.factor(popNCR$class)
popNCR$sex <- factor(popNCR$sex, levels = c(0, 1))

set.seed(123)
ini <- mice(popNCR, maxit = 0)
meth <- ini$meth
meth[c(3, 5, 6, 7)] <- "norm"
pred <- ini$pred
pred[, "class"] <- 0
pred[, "pupil"] <- 0
imp1 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)
pred <- ini$pred
pred[, "pupil"] <- 0
imp2 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)

cat("=== 9.24 ===\n")
capture_block(summary(complete(imp1)))
cat("=== 9.25 ===\n")
capture_block(summary(popNCR))
cat("=== 16.37 ===\n")
capture_block(head(complete(imp2, 1), n = 15))