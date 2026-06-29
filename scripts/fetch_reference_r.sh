#!/usr/bin/env bash
# Fetch read-only R mice source snapshots for behavioral reference (GPL, dev-only).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/Reference"
TAG="v3.19.0"
BASE="https://raw.githubusercontent.com/amices/mice/${TAG}/R"

FILES=(
  mice.R
  sampler.R
  initialize.imp.R
  mids.R
  complete.R
  pool.R
  md.pattern.R
  mice.impute.pmm.R
  mice.impute.norm.R
  mice.impute.norm.boot.R
  mice.impute.norm.predict.R
  mice.impute.logreg.R
  mice.impute.polyreg.R
  mice.impute.cart.R
  mice.impute.jomoImpute.R
  mice.impute.panImpute.R
  blocks.R
  auxiliary.R
)

mkdir -p "$REF"
for f in "${FILES[@]}"; do
  dest="$REF/${f}"
  echo "Fetching $f ..."
  curl -fsSL "$BASE/$f" -o "$dest"
  if [[ ! -s "$dest" ]] || grep -q "404: Not Found" "$dest" 2>/dev/null; then
    echo "ERROR: failed to fetch $f" >&2
    exit 1
  fi
done

echo "Reference snapshots updated in $REF"