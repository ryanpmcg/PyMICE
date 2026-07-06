#!/usr/bin/env bash
# Brain-standard entry point — delegates to setup_venv.sh (venv at ~/.venvs/brain-pymice).
exec "$(cd "$(dirname "$0")" && pwd)/setup_venv.sh" "$@"
