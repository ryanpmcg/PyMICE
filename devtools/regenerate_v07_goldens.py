#!/usr/bin/env python3
"""Refresh V07 golden outputs from the R ampute chain (seed 2016)."""

from __future__ import annotations

import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS))

from lib.golden_store import update_golden_key  # noqa: E402

TESTDATA_CSV = ROOT / "src" / "pymice" / "data" / "ampute_testdata.csv"


def _capture_r_head() -> str:
    """Exact ``head(result$amp)`` from current R ``mice`` + bundled CSV."""
    script = f"""
suppressPackageStartupMessages({{library(mice); library(MASS)}})
set.seed(2016)
invisible(mvrnorm(10000, c(10, 5, 0), matrix(c(1, 0.2, 0.2, 0.2, 1, 0.2, 0.2, 0.2, 1), 3, 3, byrow = TRUE)))
testdata <- read.csv({json.dumps(str(TESTDATA_CSV))}, check.names = FALSE)
result <- ampute(testdata)
capture.output(print(head(result$amp), digits = 7)) |> cat(sep = "\\n")
"""
    out = subprocess.run(
        ["Rscript", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return out.stdout.strip()


def _update(vignette_dir: str, key: str, r_output: str) -> None:
    update_golden_key(vignette_dir, key, r_output)


def main() -> int:
    from lib.data import load_ampute_testdata
    from lib.r_style import (
        format_ampute_summary_r,
        format_md_pattern_r,
        format_patterns_matrix_r,
    )
    from lib.vignette_rng import ensure_vignette_r_prerequisites

    from pymice import md_pattern
    from pymice.methods.r_ampute_backend import run_ampute_chain_r, use_r_ampute_backend

    ensure_vignette_r_prerequisites()
    if not use_r_ampute_backend():
        raise RuntimeError("R ampute backend required to refresh V07 goldens")

    testdata, names = load_ampute_testdata()
    mypatterns = np.array([[0, 1, 1], [0, 0, 1], [1, 1, 0], [0, 1, 0]], dtype=np.int_)
    myfreq = np.array([0.7, 0.1, 0.1, 0.1], dtype=np.float64)
    chain = [
        {"prop": 0.5},
        {"prop": 0.2, "bycases": False},
        {"freq": myfreq.tolist(), "patterns": mypatterns.tolist(), "mech": "MAR"},
        {"freq": myfreq.tolist(), "patterns": mypatterns.tolist(), "mech": "MNAR"},
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result, result2, _, result_mnar = run_ampute_chain_r(chain, seed=2016)

    _update("07_ampute", "2.1", format_ampute_summary_r(testdata, names))
    _update("07_ampute", "3.3", _capture_r_head())
    _update("07_ampute", "5.5", format_md_pattern_r(md_pattern(result.amp, names)))
    _update("07_ampute", "10.7", format_md_pattern_r(md_pattern(result2.amp, names)))
    _update("07_ampute", "11.19", format_patterns_matrix_r(result_mnar.patterns, names, max_rows=4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
