"""Shared pytest configuration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS_DIR = REPO_ROOT / "devtools"

if str(DEVTOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(DEVTOOLS_DIR))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "parity: R alignment / golden parity checks")
    config.addinivalue_line("markers", "r_backend: requires Rscript and CRAN mice")
    config.addinivalue_line("markers", "slow: long-running chain parity")
