#!/usr/bin/env bash
# Create an isolated virtual environment for PyMICE vignette commands.
set -euo pipefail

COMMANDS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$COMMANDS_DIR/.." && pwd)"
VENV="$COMMANDS_DIR/.venv"

if [[ ! -d "$VENV" ]]; then
  echo "Creating virtual environment at $VENV"
  python3 -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

python -m pip install -U pip wheel
python -m pip install -e "$ROOT[dev,plot,pandas,ml]"

echo "Virtual environment ready: $VENV"
echo "Activate with: source Commands/.venv/bin/activate"