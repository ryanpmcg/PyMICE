"""Level-2 class mean imputation (2lonly.mean)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method
from pymice.types import VariableKind


def impute_2lonly_mean(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    levels: tuple[float, ...] | None = None,
    kind: VariableKind = VariableKind.NUMERIC,
    **_: object,
) -> NDArray[np.floating]:
    """Replicate class mean / mode within cluster (R ``mice.impute.2lonly.mean``)."""
    del rng
    if type is None:
        raise ValueError("2lonly.mean requires predictor type codes (include -2 for cluster)")
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)
    cluster_mask = type_vec == -2
    if not np.any(cluster_mask):
        raise ValueError("2lonly.mean requires a cluster indicator (type=-2)")

    classes = x_arr[:, cluster_mask].astype(np.int64).ravel()
    y_obs = y_arr[ry]
    class_obs = classes[ry]
    class_mis = classes[wy]

    if kind != VariableKind.NUMERIC and levels:
        modes: dict[int, float] = {}
        for c in np.unique(class_obs):
            vals = y_obs[class_obs == c]
            if vals.size == 0:
                continue
            codes, counts = np.unique(vals, return_counts=True)
            modes[int(c)] = float(codes[int(np.argmax(counts))])
        out = np.array([modes.get(int(c), np.nan) for c in class_mis], dtype=np.float64)
        return out

    means: dict[int, float] = {}
    for c in np.unique(class_obs):
        vals = y_obs[class_obs == c]
        if vals.size:
            means[int(c)] = float(np.mean(vals))
    return np.array([means.get(int(c), np.nan) for c in class_mis], dtype=np.float64)


register_method("2lonly.mean", impute_2lonly_mean)
