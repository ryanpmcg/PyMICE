"""Design matrix construction for univariate imputation models."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.types import VariableKind, VariableSpec


def _factor_encode(spec: VariableSpec, type_flag: int | None) -> bool:
    """Whether to dummy-expand a predictor (R ``predictorMatrix`` type semantics)."""
    if type_flag is None:
        return spec.kind not in {VariableKind.NUMERIC, VariableKind.BINARY}
    if type_flag == 1:
        return False
    if type_flag >= 2:
        return True
    return False


def expand_predictors(
    data: NDArray[np.float64],
    predictor_idx: list[int],
    specs: list[VariableSpec],
    *,
    predictor_types: list[int] | None = None,
) -> NDArray[np.float64]:
    """Expand predictors with dummy coding for categorical columns."""
    if not predictor_idx:
        return np.empty((data.shape[0], 0), dtype=np.float64)

    columns: list[NDArray[np.float64]] = []
    for local, j in enumerate(predictor_idx):
        spec = specs[j]
        col = data[:, j]
        type_flag = None if predictor_types is None else int(predictor_types[local])
        if not _factor_encode(spec, type_flag):
            columns.append(col)
            continue
        levels = spec.levels if spec.levels else tuple(np.unique(col[~np.isnan(col)]))
        for level in levels[1:]:
            columns.append((col == level).astype(np.float64))

    return np.column_stack(columns)


def obtain_design(
    data: NDArray[np.float64],
    target_idx: int,
    predictor_idx: list[int],
    specs: list[VariableSpec] | None = None,
    *,
    predictor_types: list[int] | None = None,
) -> NDArray[np.float64]:
    """Build predictor matrix (no intercept) for target ~ predictors."""
    del target_idx
    if specs is None:
        if not predictor_idx:
            return np.empty((data.shape[0], 0), dtype=np.float64)
        return data[:, predictor_idx]
    return expand_predictors(
        data,
        predictor_idx,
        specs,
        predictor_types=predictor_types,
    )


def predictor_indices(pred_row: NDArray[np.int_], target_idx: int) -> list[int]:
    """Column indices used as predictors for a target (excluding self)."""
    return [j for j, flag in enumerate(pred_row) if flag != 0 and j != target_idx]


def predictor_labels(
    predictor_idx: list[int],
    specs: list[VariableSpec],
    column_names: list[str],
    *,
    predictor_types: list[int] | None = None,
) -> list[str]:
    """One label per expanded design column (matches ``expand_predictors`` order)."""
    labels: list[str] = []
    for local, j in enumerate(predictor_idx):
        spec = specs[j]
        name = column_names[j]
        type_flag = None if predictor_types is None else int(predictor_types[local])
        if not _factor_encode(spec, type_flag):
            labels.append(name)
            continue
        levels = spec.levels if spec.levels else ()
        if not levels:
            labels.append(name)
            continue
        for level in levels[1:]:
            labels.append(f"{name}{level}")
    return labels
