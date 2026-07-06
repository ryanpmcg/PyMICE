#!/usr/bin/env bash
# Create an isolated virtual environment for PyMICE — OUTSIDE Brain (Drive-safe).
set -euo pipefail

DEVTOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DEVTOOLS_DIR/.." && pwd)"
VENV_DIR="${PYMICE_VENV:-$HOME/.venvs/brain-pymice}"

if [[ -d "$DEVTOOLS_DIR/.venv" ]]; then
  echo "WARNING: Remove legacy devtools/.venv from Drive (sync hazard)."
  echo "  Delete Brain/Research/Projects/PyMICE/devtools/.venv on drive.google.com if present."
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

python -m pip install -U pip wheel
python -m pip install -e "$ROOT[dev,plot,pandas,ml,survival,docs]"

echo "Virtual environment ready: $VENV_DIR"
echo "Activate with: source $VENV_DIR/bin/activate"
echo "Override path: PYMICE_VENV=/path/to/venv bash devtools/setup_venv.sh"