"""Parity test configuration (devtools on path via tests/conftest.py)."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "parity: R alignment / golden parity checks")
    config.addinivalue_line("markers", "r_backend: requires Rscript and CRAN mice")
    config.addinivalue_line("markers", "slow: long-running chain parity (V05 multilevel)")
