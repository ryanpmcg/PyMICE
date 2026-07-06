"""V01 draw-order parity: PyMICE session RNG chain vs R subprocess."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import numpy as np
import pytest

from pymice import data
from pymice.rng import RSession

ROOT = Path(__file__).resolve().parents[2]
DEVTOOLS = ROOT / "devtools"


def _r_v01_chain() -> dict[str, np.ndarray]:
    script = textwrap.dedent(
        """
        suppressPackageStartupMessages(library(mice))
        suppressPackageStartupMessages(library(lattice))
        set.seed(123)
        nhanes <- mice::nhanes
        imp <- mice(nhanes, method = "mean", m = 1, maxit = 1)
        densityplot(nhanes$bmi, xlab = "nhanes$bmi")
        imp <- mice(nhanes, method = "norm.predict", m = 1, maxit = 1)
        imp <- mice(nhanes, method = "norm.nob", m = 1, maxit = 1)
        nob <- as.matrix(complete(imp, 1)[, c("age", "bmi", "hyp", "chl")])
        imp <- mice(nhanes, method = "norm.nob", m = 1, maxit = 1, seed = 123)
        imp <- mice(nhanes)
        imp_bmi <- as.matrix(imp$imp$bmi)
        imp_hyp <- as.matrix(imp$imp$hyp)
        imp_chl <- as.matrix(imp$imp$chl)
        cat("NOB", paste(as.vector(t(nob)), collapse = " "), "\\n")
        cat("BMI", paste(as.vector(t(imp_bmi)), collapse = " "), "\\n")
        cat("HYP", paste(as.vector(t(imp_hyp)), collapse = " "), "\\n")
        cat("CHL", paste(as.vector(t(imp_chl)), collapse = " "), "\\n")
        """
    )
    proc = subprocess.run(
        ["Rscript", "-e", script],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    out: dict[str, list[float]] = {}
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        key, *vals = line.split()
        if key not in {"NOB", "BMI", "HYP", "CHL"}:
            continue
        out[key] = [float(v) for v in vals]
    return {k: np.array(v, dtype=np.float64) for k, v in out.items()}


from tests.r_support import r_backend_available, r_backend_skip_reason  # noqa: E402


@pytest.mark.r_backend
@pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason())
def test_v01_draw_order_matches_r_subprocess():
    import sys

    commands = DEVTOOLS
    sys.path.insert(0, str(commands))
    sys.path.insert(0, str(ROOT / "src"))

    from lib.vignette_rng import run_v01_mice_chain

    RSession.close()
    from lib.vignette_rng import start_vignette_rng_session

    start_vignette_rng_session(123)
    nhanes = data("nhanes")
    _, _, imp_nob, _, imp_pmm = run_v01_mice_chain(nhanes)

    from pymice import complete

    py_nob = complete(imp_nob, 1)
    r = _r_v01_chain()

    np.testing.assert_allclose(py_nob.ravel(), r["NOB"], rtol=0, atol=1e-5)
    np.testing.assert_allclose(imp_pmm.imp["bmi"].ravel(), r["BMI"], rtol=0, atol=1e-5)
    np.testing.assert_allclose(imp_pmm.imp["hyp"].ravel(), r["HYP"], rtol=0, atol=1e-5)
    np.testing.assert_allclose(imp_pmm.imp["chl"].ravel(), r["CHL"], rtol=0, atol=1e-5)
