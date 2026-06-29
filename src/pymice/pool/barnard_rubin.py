"""Barnard–Rubin degrees of freedom adjustment for small samples."""

from __future__ import annotations


def barnard_rubin(m: int, b: float, t: float, dfcom: float) -> float:
    """Adjusted df for MI inference (Barnard & Rubin, 1999; R ``barnard.rubin``)."""
    if m < 2:
        return float(dfcom)
    lam = (1.0 + 1.0 / m) * b / t
    if lam == 0.0 or t == 0.0:
        dfold = float("inf")
    else:
        dfold = (m - 1.0) / (lam**2)
    if dfcom == float("inf") or dfcom > 1e6:
        return dfold
    tmp = (1.0 - lam) * (1.0 + dfcom) * dfcom
    return (m - 1.0) * tmp / ((dfcom + 3.0) * (m - 1.0) + (lam**2) * tmp)
