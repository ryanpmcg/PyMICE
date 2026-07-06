"""Level-2 class mean imputation (2lonly.mean)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method
from pymice.types import VariableKind


def _class_lookup(
    class_mis: NDArray[np.int_],
    class_levels: NDArray[np.int_],
    values: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Map missing rows to aggregated class values (R ``aggregate`` + ``apply``)."""
    lookup = {int(c): float(v) for c, v in zip(class_levels, values, strict=True)}
    out = np.array([lookup.get(int(c), np.nan) for c in class_mis], dtype=np.float64)
    out[np.isnan(out) & np.isin(class_mis, class_levels)] = np.nan
    return out


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
    if not np.any(wy):
        return np.array([], dtype=np.float64)

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

    all_classes = np.unique(classes)
    observed_classes = np.unique(class_obs)
    empty_classes = np.setdiff1d(all_classes, observed_classes, assume_unique=True)

    agg_classes = np.concatenate([class_obs, empty_classes])
    agg_y = np.concatenate([y_obs, np.full(empty_classes.size, np.nan, dtype=np.float64)])

    if kind != VariableKind.NUMERIC and levels:
        # R uses median on factor integer codes, then maps back to levels.
        modes: list[float] = []
        for c in agg_classes:
            vals = agg_y[agg_classes == c]
            vals = vals[np.isfinite(vals)]
            if vals.size == 0:
                modes.append(np.nan)
                continue
            codes, counts = np.unique(vals, return_counts=True)
            modes.append(float(codes[int(np.argmax(counts))]))
        return _class_lookup(class_mis, agg_classes, np.asarray(modes, dtype=np.float64))

    means = np.array(
        [np.nanmean(agg_y[agg_classes == c]) for c in agg_classes],
        dtype=np.float64,
    )
    return _class_lookup(class_mis, agg_classes, means)


register_method("2lonly.mean", impute_2lonly_mean)
