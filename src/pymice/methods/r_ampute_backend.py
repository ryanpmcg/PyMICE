"""Optional R ``mice::ampute`` backend for vignette parity."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from pymice.ampute import AmputeResult

_R_SCRIPT = Path(__file__).with_name("r_ampute.R")


def use_r_ampute_backend(explicit: bool | None = None) -> bool:
    """Return whether to call R ``ampute`` (auto when R+mice available)."""
    env = os.environ.get("PYMICE_R_AMPUTE", "").strip().lower()
    if env in {"0", "false", "no"}:
        return False
    if explicit is False:
        return False
    if explicit is True or env in {"1", "true", "yes"}:
        return r_ampute_available()
    return r_ampute_available()


@lru_cache(maxsize=1)
def r_ampute_available() -> bool:
    rscript = shutil.which("Rscript")
    if rscript is None or not _R_SCRIPT.is_file():
        return False
    try:
        proc = subprocess.run(
            [
                rscript,
                "-e",
                'suppressPackageStartupMessages(requireNamespace("mice", quietly=TRUE)); '
                'suppressPackageStartupMessages(requireNamespace("jsonlite", quietly=TRUE))',
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def _default_testdata_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "ampute_testdata.csv"


def run_ampute_chain_r(
    chain: list[dict[str, object]],
    *,
    testdata_path: Path | None = None,
    seed: int = 2016,
) -> list[AmputeResult]:
    """Run a sequence of ``ampute`` calls on one R RNG stream (V07 workflow)."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError("Rscript not found")
    data_path = testdata_path or _default_testdata_path()
    if not data_path.is_file():
        raise FileNotFoundError(f"ampute testdata not found: {data_path}")

    payload = {
        "seed": int(seed),
        "testdata_path": str(data_path.resolve()),
        "chain": chain,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        payload_path = fh.name

    try:
        proc = subprocess.run(
            [rscript, str(_R_SCRIPT), payload_path],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    finally:
        Path(payload_path).unlink(missing_ok=True)

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "R ampute failed")

    raw = json.loads(proc.stdout)
    out: list[AmputeResult] = []
    for item in raw["results"]:
        amp = None
        if item.get("amp") is not None:
            amp = np.asarray(item["amp"], dtype=object)
            amp = np.where(amp == "NA", np.nan, amp).astype(np.float64)
        patterns = np.asarray(item["patterns"], dtype=np.int_)
        freq = np.asarray(item["freq"], dtype=np.float64)
        weights = item.get("weights")
        weights_arr = np.asarray(weights, dtype=np.float64) if weights is not None else None
        out.append(
            AmputeResult(
                amp=amp,
                patterns=patterns,
                freq=freq,
                mech=str(item.get("mech", "MCAR")),
                prop=float(item["prop"]),
                bycases=bool(item.get("bycases", True)),
                weights=weights_arr,
            )
        )
    return out


def ampute_r(
    data: NDArray[np.floating],
    *,
    prop: float = 0.5,
    patterns: NDArray[np.int_] | None = None,
    freq: NDArray[np.floating] | None = None,
    mech: str = "MCAR",
    weights: NDArray[np.floating] | None = None,
    cont: bool = True,
    type: str | list[str] | None = None,
    bycases: bool = True,
    run: bool = True,
    seed: int = 2016,
    testdata_path: Path | None = None,
) -> AmputeResult:
    """Single ``ampute`` call via R (uses bundled testdata + vignette RNG warmup)."""
    spec: dict[str, object] = {
        "prop": float(prop),
        "bycases": bool(bycases),
        "mech": mech.upper(),
        "cont": bool(cont),
        "run": bool(run),
    }
    if patterns is not None:
        spec["patterns"] = np.asarray(patterns, dtype=np.int_).tolist()
    if freq is not None:
        spec["freq"] = np.asarray(freq, dtype=np.float64).tolist()
    if weights is not None:
        spec["weights"] = np.asarray(weights, dtype=np.float64).tolist()
    if type is not None:
        spec["type"] = type if isinstance(type, list) else [type]
    return run_ampute_chain_r(
        [spec],
        testdata_path=testdata_path,
        seed=seed,
    )[0]
