"""MICE sampler convergence diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pymice.types import Mids


@dataclass
class ConvergenceRow:
    iteration: int
    variable: str
    autocorrelation: float | None = None
    psrf: float | None = None


def convergence(
    data: Mids,
    diagnostic: str = "all",
    parameter: str = "mean",
) -> list[ConvergenceRow]:
    """Compute convergence diagnostics (R ``convergence()``).

    Parameters
    ----------
    diagnostic
        ``"all"``, ``"ac"``, ``"psrf"``, or ``"gr"`` (alias for psrf).
    parameter
        ``"mean"`` (chain means) or ``"sd"`` (chain standard deviations).
    """
    if data.m < 2:
        raise ValueError("m must be at least 2 for convergence diagnostics")
    if data.iteration < 3:
        raise ValueError("maxit must be at least 3 for convergence diagnostics")
    if not data.chain_mean:
        raise ValueError("no convergence diagnostics found on Mids object")

    diagnostic = diagnostic.lower()
    if diagnostic == "gr":
        diagnostic = "psrf"
    if diagnostic not in ("all", "ac", "psrf"):
        raise ValueError("diagnostic must be 'all', 'ac', 'psrf', or 'gr'")
    if parameter not in ("mean", "sd"):
        raise ValueError("parameter must be 'mean' or 'sd'")

    rows: list[ConvergenceRow] = []
    for name in data.column_names:
        if name not in data.chain_mean:
            continue
        if parameter == "mean":
            chains = np.asarray(data.chain_mean[name], dtype=np.float64)
        else:
            chains = np.sqrt(np.asarray(data.chain_var[name], dtype=np.float64))

        if chains.ndim != 2:
            continue

        for it in range(1, data.iteration + 1):
            ac_val: float | None = None
            psrf_val: float | None = None

            if diagnostic in ("all", "ac") and it >= 2:
                prev = chains[it - 2, :]
                curr = chains[it - 1, :]
                ac_val = _lag1_autocorrelation(prev, curr)

            if diagnostic in ("all", "psrf"):
                cumulative = chains[:it, :]
                psrf_val = _gelman_rubin_rhat(cumulative)

            rows.append(
                ConvergenceRow(
                    iteration=it,
                    variable=name,
                    autocorrelation=ac_val,
                    psrf=psrf_val,
                )
            )

    return rows


def _lag1_autocorrelation(prev: NDArray[np.float64], curr: NDArray[np.float64]) -> float | None:
    mask = np.isfinite(prev) & np.isfinite(curr)
    if int(np.sum(mask)) < 2:
        return None
    c = np.corrcoef(prev[mask], curr[mask])
    return float(c[0, 1])


def _gelman_rubin_rhat(chains: NDArray[np.float64]) -> float | None:
    """Potential scale reduction factor (Gelman–Rubin R-hat)."""
    if chains.ndim != 2:
        return None
    n, m = chains.shape
    if m < 2 or n < 2:
        return None

    chain_means = np.mean(chains, axis=0)
    chain_vars = np.var(chains, axis=0, ddof=1)
    W = float(np.mean(chain_vars))
    B = float(n / (m - 1) * np.sum((chain_means - np.mean(chain_means)) ** 2))
    if float(np.ptp(chain_means)) < 1e-9:
        return 1.0
    if W <= 0:
        return None
    var_hat = ((n - 1) / n) * W + B / n
    return float(np.sqrt(var_hat / W))
