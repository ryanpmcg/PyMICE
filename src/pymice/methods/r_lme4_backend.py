"""Optional R ``lme4`` backend for ``2l.lmer`` and ``2l.bin`` imputation."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

_R_SCRIPT = Path(__file__).with_name("r_lme4_impute.R")


def use_r_lme4_backend(explicit: bool | None = None) -> bool:
    """Return whether to call R ``lme4`` (auto when R+lme4+mice available)."""
    env = os.environ.get("PYMICE_R_LMER", "").strip().lower()
    if env in {"0", "false", "no"}:
        return False
    if explicit is False:
        return False
    if explicit is True or env in {"1", "true", "yes"}:
        return r_lme4_available()
    return r_lme4_available()


@lru_cache(maxsize=1)
def r_lme4_available() -> bool:
    rscript = shutil.which("Rscript")
    if rscript is None or not _R_SCRIPT.is_file():
        return False
    code = (
        'suppressPackageStartupMessages(requireNamespace("lme4", quietly=TRUE)); '
        'suppressPackageStartupMessages(requireNamespace("mice", quietly=TRUE)); '
        'suppressPackageStartupMessages(requireNamespace("MASS", quietly=TRUE))'
    )
    try:
        proc = subprocess.run(
            [rscript, "-e", code],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def lme4_impute_r(
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
    x: NDArray[np.float64],
    type_vec: NDArray[np.int_],
    wy: NDArray[np.bool_],
    *,
    method: str,
    seed: int,
    random_effects: str = "laplace",
) -> NDArray[np.float64]:
    """Run ``mice.impute.2l.lmer`` or ``mice.impute.2l.bin`` via ``Rscript``."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError("Rscript not found")

    y_vec = np.asarray(y, dtype=np.float64).ravel()
    ry_arr = np.asarray(ry, dtype=np.bool_)
    wy_arr = np.asarray(wy, dtype=np.bool_)
    x_arr = np.asarray(x, dtype=np.float64)
    type_arr = np.asarray(type_vec, dtype=np.int_)

    if method not in ("lmer", "bin"):
        raise ValueError(f"unknown lme4 method: {method}")

    with tempfile.TemporaryDirectory(prefix="pymice_lme4_") as tmp:
        work = Path(tmp)
        np.savetxt(work / "y.txt", y_vec)
        np.savetxt(work / "ry.txt", ry_arr.astype(np.int_), fmt="%d")
        np.savetxt(work / "wy.txt", wy_arr.astype(np.int_), fmt="%d")
        np.savetxt(work / "x.txt", x_arr, delimiter=",")
        np.savetxt(work / "type.txt", type_arr, fmt="%d")
        (work / "method.txt").write_text(method + "\n")
        np.savetxt(work / "seed.txt", [int(seed)], fmt="%d")
        (work / "random_effects.txt").write_text(random_effects + "\n")

        proc = subprocess.run(
            [rscript, str(_R_SCRIPT), str(work)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            msg = proc.stderr.strip() or proc.stdout.strip() or "R lme4 impute failed"
            raise RuntimeError(msg)

        out = np.loadtxt(work / "out.txt", dtype=np.float64)
        if out.shape != (int(np.sum(wy_arr)),):
            raise RuntimeError(f"R lme4 returned shape {out.shape}, expected ({np.sum(wy_arr)},)")
        return out
