"""Optional R ``pan::pan`` backend for ``2l.pan`` (Fortran ``mgibbs``)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

_R_SCRIPT = Path(__file__).with_name("r_pan_impute.R")


def use_r_pan_backend(explicit: bool | None = None) -> bool:
    """Return whether to call R ``pan`` (auto when R+pan available)."""
    env = os.environ.get("PYMICE_R_PAN", "").strip().lower()
    if env in {"0", "false", "no"}:
        return False
    if explicit is False:
        return False
    if explicit is True or env in {"1", "true", "yes"}:
        return r_pan_available()
    return r_pan_available()


@lru_cache(maxsize=1)
def r_pan_available() -> bool:
    rscript = shutil.which("Rscript")
    if rscript is None or not _R_SCRIPT.is_file():
        return False
    try:
        proc = subprocess.run(
            [
                rscript,
                "-e",
                'suppressPackageStartupMessages(requireNamespace("pan", quietly=TRUE))',
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def derive_pan_seed_from_mice_seed(mice_seed: int) -> int:
    """Match R ``mice.impute.2l.pan`` pan RNG seed after ``set.seed(mice_seed)``."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError("Rscript not found")
    code = f"set.seed({int(mice_seed)}); cat(as.integer(round(runif(1, 1, 10^7))), fill=TRUE)"
    proc = subprocess.run(
        [rscript, "-e", code],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return int(proc.stdout.strip())


def pan_impute_r(
    y: NDArray[np.float64],
    subj: NDArray[np.int_],
    pred: NDArray[np.float64],
    zcol: NDArray[np.int_],
    *,
    n_iter: int,
    pan_seed: int,
) -> NDArray[np.float64]:
    """Run ``pan::pan`` via ``Rscript`` and return the full imputed outcome vector."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError("Rscript not found")

    y_vec = np.asarray(y, dtype=np.float64).ravel()
    subj_arr = np.asarray(subj, dtype=np.int_)
    pred_arr = np.asarray(pred, dtype=np.float64)
    z_idx = np.asarray(zcol, dtype=np.int_)

    with tempfile.TemporaryDirectory(prefix="pymice_pan_") as tmp:
        work = Path(tmp)
        np.savetxt(work / "y.txt", y_vec)
        np.savetxt(work / "subj.txt", subj_arr, fmt="%d")
        np.savetxt(work / "pred.txt", pred_arr, delimiter=",")
        np.savetxt(work / "zcol.txt", z_idx, fmt="%d")
        np.savetxt(work / "n_iter.txt", [int(n_iter)], fmt="%d")
        np.savetxt(work / "pan_seed.txt", [int(pan_seed)], fmt="%d")

        proc = subprocess.run(
            [rscript, str(_R_SCRIPT), str(work)],
            capture_output=True,
            text=True,
            timeout=max(120, int(n_iter) // 2),
            check=False,
        )
        if proc.returncode != 0:
            msg = proc.stderr.strip() or proc.stdout.strip() or "R pan failed"
            raise RuntimeError(msg)

        out = np.loadtxt(work / "out.txt", dtype=np.float64)
        if out.shape != y_vec.shape:
            raise RuntimeError(f"R pan returned shape {out.shape}, expected {y_vec.shape}")
        return out
