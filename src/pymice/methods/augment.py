"""Data augmentation for logistic / polytomous regression (White et al. 2010)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def augment(
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
    x: NDArray[np.float64],
    wy: NDArray[np.bool_],
    maxcat: int = 50,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.bool_],
    NDArray[np.float64],
    NDArray[np.bool_],
    NDArray[np.float64],
]:
    """Augment data to reduce perfect-prediction bias (R ``augment()``)."""
    icod = np.unique(y[~np.isnan(y)])
    k = icod.size
    if k > maxcat:
        raise ValueError(f"Maximum number of categories ({maxcat}) exceeded")

    n, p = x.shape if x.ndim == 2 else (y.size, 0)

    if p == 0:
        w = np.ones(n, dtype=np.float64)
        return y, ry, x, wy, w

    if int(np.sum(~ry)) == 1:
        w = np.ones(n, dtype=np.float64)
        return y, ry, x, wy, w

    mean = np.nanmean(x, axis=0)
    sd = np.sqrt(np.nanvar(x, axis=0))
    minx = np.nanmin(x, axis=0)
    maxx = np.nanmax(x, axis=0)

    nr = 2 * p * k
    a = np.tile(mean, (nr, 1))
    b = np.zeros((nr, p), dtype=np.float64)
    for col in range(p):
        pattern = np.tile(np.repeat([0.5, -0.5], k), p)
        b[:, col] = pattern[:nr]
    c = np.tile(sd, (nr, 1))
    d_aug = a + b * c
    d_aug = np.maximum(np.tile(minx, (nr, 1)), d_aug)
    d_aug = np.minimum(np.tile(maxx, (nr, 1)), d_aug)

    e = np.tile(np.repeat(icod, 2), p)

    xa = np.vstack([x, d_aug])
    ya = np.concatenate([y, e])
    rya = np.concatenate([ry, np.ones(nr, dtype=bool)])
    wya = np.concatenate([wy, np.zeros(nr, dtype=bool)])
    wa = np.concatenate([np.ones(n), np.full(nr, (p + 1) / nr)])

    return ya, rya, xa, wya, wa
