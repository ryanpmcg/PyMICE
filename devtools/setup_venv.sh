#!/usr/bin/env bash
# Create an isolated virtual environment for PyMICE — OUTSIDE Brain (Drive-safe).
set -euo pipefail

DEVTOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DEVTOOLS_DIR/.." && pwd)"
VENV_DIR="${PYMICE_VENV:-$HOME/.venvs/brain-pymice}"

LEGACY_VENV="$DEVTOOLS_DIR/.venv"
if [[ -d "$LEGACY_VENV" ]]; then
  echo "Removing legacy devtools/.venv (Drive sync hazard; venv belongs at $VENV_DIR)."
  rm -rf "$LEGACY_VENV"
  echo "  If devtools/.venv still appears on drive.google.com, delete it there too."
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
