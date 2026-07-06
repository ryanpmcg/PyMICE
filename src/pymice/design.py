"""Design matrix construction for univariate imputation models."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.types import VariableKind, VariableSpec


def expand_predictors(
    data: NDArray[np.float64],
    predictor_idx: list[int],
    specs: list[VariableSpec],
) -> NDArray[np.float64]:
    """Expand predictors with dummy coding for categorical columns."""
    if not predictor_idx:
        return np.empty((data.shape[0], 0), dtype=np.float64)

    columns: list[NDArray[np.float64]] = []
    for j in predictor_idx:
        spec = specs[j]
        col = data[:, j]
        if spec.kind == VariableKind.NUMERIC:
            columns.append(col)
        elif spec.kind == VariableKind.BINARY:
            columns.append(col)
        else:
            levels = spec.levels if spec.levels else tuple(np.unique(col[~np.isnan(col)]))
            for level in levels[1:]:
                columns.append((col == level).astype(np.float64))

    return np.column_stack(columns)


def obtain_design(
    data: NDArray[np.float64],
    target_idx: int,
    predictor_idx: list[int],
    specs: list[VariableSpec] | None = None,
) -> NDArray[np.float64]:
    """Build predictor matrix (no intercept) for target ~ predictors."""
    if specs is None:
        if not predictor_idx:
            return np.empty((data.shape[0], 0), dtype=np.float64)
        return data[:, predictor_idx]
    return expand_predictors(data, predictor_idx, specs)


def predictor_indices(pred_row: NDArray[np.int_], target_idx: int) -> list[int]:
    """Column indices used as predictors for a target (excluding self)."""
    return [j for j, flag in enumerate(pred_row) if flag != 0 and j != target_idx]


def predictor_labels(
    predictor_idx: list[int],
    specs: list[VariableSpec],
    column_names: list[str],
) -> list[str]:
    """One label per expanded design column (matches ``expand_predictors`` order)."""
    labels: list[str] = []
    for j in predictor_idx:
        spec = specs[j]
        name = column_names[j]
        if spec.kind in {VariableKind.NUMERIC, VariableKind.BINARY}:
            labels.append(name)
            continue
        levels = spec.levels if spec.levels else ()
        if not levels:
            labels.append(name)
            continue
        for level in levels[1:]:
            labels.append(f"{name}{level}")
    return labels
