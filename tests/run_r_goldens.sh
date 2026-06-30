#!/usr/bin/env bash
# Generate R reference outputs for vignette parity tests (requires R + mice).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/tests/goldens/r"
mkdir -p "$OUT"

OUT_DIR="$OUT" Rscript -e "
out_dir <- Sys.getenv('OUT_DIR')
if (!requireNamespace('mice', quietly = TRUE)) {
  stop('R package mice is required: install.packages(\"mice\")')
}
library(mice)
set.seed(123)
for (meth in c('mean', 'pmm', 'norm', 'norm.nob')) {
  imp <- mice(nhanes, method = meth, m = 2, maxit = 3, print = FALSE, seed = 123)
  fname <- paste0('nhanes_', gsub('\\\\.', '_', meth, fixed = TRUE), '_m2_maxit3_complete1.csv')
  write.csv(complete(imp, 1), file.path(out_dir, fname), row.names = FALSE)
}
data(nhanes2, package = 'mice')
imp2 <- mice(nhanes2, m = 2, maxit = 3, print = FALSE, seed = 123)
write.csv(complete(imp2, 1), file.path(out_dir, 'nhanes2_default_m2_maxit3_complete1.csv'), row.names = FALSE)
cat('Golden outputs written to', out_dir, '\n')
"