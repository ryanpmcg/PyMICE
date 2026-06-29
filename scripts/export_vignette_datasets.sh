#!/usr/bin/env bash
# Export R vignette datasets to tests/data/ (requires R + mice).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/tests/data"
mkdir -p "$OUT"

Rscript -e "
library(mice)
for (d in c('boys', 'mammalsleep', 'nhanes', 'nhanes2')) {
  write.csv(get(d), file.path('$OUT', paste0(d, '.csv')), row.names = FALSE)
  cat('wrote', d, '\n')
}
con <- url('https://www.gerkovink.com/mimp/leiden.RData')
load(con)
write.csv(leiden, file.path('$OUT', 'leiden.csv'), row.names = FALSE)
cat('wrote leiden\n')
con2 <- url('https://www.gerkovink.com/mimp/popular.RData')
load(con2)
write.csv(popNCR, file.path('$OUT', 'popNCR.csv'), row.names = FALSE)
cat('wrote popNCR\n')
"

echo "Datasets exported to $OUT"