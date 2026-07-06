#!/usr/bin/env bash
# Set up venv, run all vignette demos, run pytest, and write HTML/MD reports.
set -euo pipefail

DEVTOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DEVTOOLS_DIR/.." && pwd)"
cd "$ROOT"

bash devtools/setup_venv.sh
# shellcheck source=/dev/null
source "${PYMICE_VENV:-$HOME/.venvs/brain-pymice}/bin/activate"

python devtools/run_vignettes.py
VIG_EXIT=$?

echo ""
if [ "$VIG_EXIT" -ne 0 ]; then
  echo "Vignette run finished with errors (exit $VIG_EXIT)."
else
  echo "All vignettes completed successfully."
fi
echo "Open docs/vignettes/index.html locally, or https://ryanpmcg.github.io/pymice/vignettes/ after Pages deploy."
echo "For full publication gate, also run: pytest && python maintain_parity.py"
exit $VIG_EXIT