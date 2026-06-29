"""Scalar Rubin pooling (pool.scalar)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pymice.pool.barnard_rubin import barnard_rubin


@dataclass
class ScalarPoolResult:
    m: int
    qhat: NDArray[np.float64]
    u: NDArray[np.float64]
    qbar: float
    ubar: float
    b: float
    t: float
    df: float
    r: float
    fmi: float


def pool_scalar(
    q: NDArray[np.float64] | list[float],
    u: NDArray[np.float64] | list[float],
    n: float = float("inf"),
    k: int = 1,
    rule: str = "rubin1987",
) -> ScalarPoolResult:
    """Pool scalar estimates across imputations (Rubin 1987; R ``pool.scalar``)."""
    q_arr = np.asarray(q, dtype=np.float64)
    u_arr = np.asarray(u, dtype=np.float64)
    if q_arr.shape != u_arr.shape:
        raise ValueError("Q and U must have the same length")
    m = int(q_arr.size)
    if m < 1:
        raise ValueError("At least one imputation required")

    qbar = float(np.mean(q_arr))
    ubar = float(np.mean(u_arr))
    b = float(np.var(q_arr, ddof=1)) if m > 1 else 0.0
    r = (1.0 + 1.0 / m) * b / ubar if ubar > 0 else 0.0

    if rule == "rubin1987":
        t = ubar + (m + 1.0) * b / m
        dfcom = n - k
        df = barnard_rubin(m, b, t, dfcom)
        fmi = (r + 2.0 / (df + 3.0)) / (r + 1.0) if m > 1 else 0.0
    elif rule == "reiter2003":
        t = ubar + b / m
        df = (m - 1.0) * (1.0 + (ubar / (b / m))) ** 2 if m > 1 and b > 0 else float("inf")
        fmi = float("nan")
    else:
        raise ValueError(f"Unknown pooling rule: {rule}")

    return ScalarPoolResult(
        m=m,
        qhat=q_arr,
        u=u_arr,
        qbar=qbar,
        ubar=ubar,
        b=b,
        t=t,
        df=df,
        r=r,
        fmi=fmi,
    )
