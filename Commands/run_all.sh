#!/usr/bin/env bash
# Set up venv, run all vignette demos, run pytest, and write HTML/MD reports.
set -euo pipefail

COMMANDS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$COMMANDS_DIR"

bash setup_venv.sh
# shellcheck source=/dev/null
source .venv/bin/activate

python run_vignettes.py
EXIT=$?

echo ""
echo "Open Commands/output/index.html in a browser to review vignette output."
exit $EXIT