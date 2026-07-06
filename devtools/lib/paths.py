"""Repository path constants for devtools and R reference snapshots."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVTOOLS_DIR = REPO_ROOT / "devtools"
REFERENCE_DIR = REPO_ROOT / "reference"
RUNNERS_DIR = DEVTOOLS_DIR / "runners"

# Local-only audit artifacts (not published)
DEVTOOLS_OUTPUT = DEVTOOLS_DIR / "output"

# Published vignette walkthroughs (copied into MkDocs site → GitHub Pages)
VIGNETTES_PUBLISH_DIR = REPO_ROOT / "docs" / "vignettes"

# Outside Google Drive — see devtools/setup_venv.sh
DEFAULT_VENV_DIR = Path.home() / ".venvs" / "brain-pymice"


def venv_dir() -> Path:
    return Path(os.environ.get("PYMICE_VENV", str(DEFAULT_VENV_DIR)))


def venv_python() -> Path:
    return venv_dir() / "bin" / "python"
