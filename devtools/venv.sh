#!/usr/bin/env bash
# Shared venv resolution for PyMICE scripts — source from repo root or devtools/.
# Venv lives OUTSIDE Brain/Drive (~/.venvs/brain-pymice); override with PYMICE_VENV.
set -euo pipefail

VENV_DIR="${PYMICE_VENV:-$HOME/.venvs/brain-pymice}"
PYMICE_PYTHON="${VENV_DIR}/bin/python"

run_pymice_python() {
  if [[ -x "${PYMICE_PYTHON}" ]]; then
    "${PYMICE_PYTHON}" "$@"
  else
    echo "Missing venv at ${VENV_DIR}. Run: bash devtools/setup_venv.sh" >&2
    exit 1
  fi
}