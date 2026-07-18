"""Shared pytest configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Stable BLAS for parity / remove_lindep (avoids multi-thread GEMM drift).
for _blas_var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_blas_var, "1")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS_DIR = REPO_ROOT / "devtools"

# A third-party PyPI package named ``tests`` can shadow this repo's test tree.
_tests_mod = sys.modules.get("tests")
if _tests_mod is not None:
    mod_file = getattr(_tests_mod, "__file__", "") or ""
    if not mod_file.startswith(str(REPO_ROOT)):
        del sys.modules["tests"]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(DEVTOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(DEVTOOLS_DIR))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "parity: R alignment / golden parity checks")
    config.addinivalue_line("markers", "r_backend: requires Rscript and CRAN mice")
    config.addinivalue_line("markers", "slow: long-running chain parity")
