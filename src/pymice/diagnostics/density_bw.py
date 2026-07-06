"""R-compatible kernel density bandwidth (``bw.nrd0``)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.stats import gaussian_kde


def bw_nrd0(x: NDArray[np.floating]) -> float:
    """Bandwidth selector matching R ``stats::bw.nrd0`` / ``density()`` default."""
    obs = np.asarray(x, dtype=np.float64)
    obs = obs[np.isfinite(obs)]
    n = obs.size
    if n < 2:
        return 1.0 if n == 0 else max(float(np.std(obs)), 1e-6)

    quant = np.quantile(obs, [0.25, 0.75])
    h = (quant[1] - quant[0]) / 1.34
    sd = float(np.std(obs, ddof=1))
    return float(4.0 * 1.06 * min(sd, h) * n ** (-0.2))


def density_limits(
    x: NDArray[np.floating],
    *,
    extend: float = 3.0,
) -> tuple[float, float]:
    """X-axis span matching R ``density()`` / lattice ``densityplot`` defaults."""
    obs = np.asarray(x, dtype=np.float64)
    obs = obs[np.isfinite(obs)]
    if obs.size == 0:
        return 0.0, 1.0
    if obs.size == 1:
        v = float(obs[0])
        return v - 1.0, v + 1.0
    bw = bw_nrd0(obs)
    return float(obs.min() - extend * bw), float(obs.max() + extend * bw)


def nrd0_kde_factor(kde: gaussian_kde) -> float:
    """``gaussian_kde`` bandwidth factor so effective ``h`` equals ``bw_nrd0``."""
    obs = kde.dataset.flatten()
    bw = bw_nrd0(obs)
    sd = float(np.std(obs, ddof=1))
    if sd <= 0:
        return 1.0
    return bw / sd
