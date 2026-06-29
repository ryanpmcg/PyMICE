"""Convert user input into the internal numeric matrix representation."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pymice.types import VariableKind, VariableSpec


def as_data_matrix(
    data: NDArray[Any] | dict[str, NDArray[Any]],
    column_names: list[str] | None = None,
    variable_specs: list[VariableSpec] | dict[str, VariableSpec] | None = None,
) -> tuple[NDArray[np.float64], list[str], list[VariableSpec]]:
    """Normalize input to a float matrix with column metadata."""
    if isinstance(data, dict):
        names = column_names or list(data.keys())
        if set(names) != set(data.keys()):
            raise ValueError("column_names must match dict keys")
        matrix = np.column_stack([np.asarray(data[n], dtype=np.float64) for n in names])
        specs = _resolve_specs(names, matrix, variable_specs)
        return matrix, names, specs

    arr = np.asarray(data, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("data must be a 2-D array or column dict")
    n_cols = arr.shape[1]
    names = column_names or [f"V{j + 1}" for j in range(n_cols)]
    if len(names) != n_cols:
        raise ValueError("column_names length must match number of columns")
    specs = _resolve_specs(names, arr, variable_specs)
    return arr, names, specs


def _resolve_specs(
    names: list[str],
    matrix: NDArray[np.float64],
    variable_specs: list[VariableSpec] | dict[str, VariableSpec] | None,
) -> list[VariableSpec]:
    if variable_specs is None:
        return [_infer_spec(n, matrix[:, j]) for j, n in enumerate(names)]
    if isinstance(variable_specs, dict):
        return [variable_specs[n] for n in names]
    if len(variable_specs) != len(names):
        raise ValueError("variable_specs length must match number of columns")
    return list(variable_specs)


def _infer_spec(name: str, column: NDArray[np.float64]) -> VariableSpec:
    """Infer variable kind from data (numeric columns default to NUMERIC like R)."""
    observed = column[~np.isnan(column)]
    if observed.size == 0:
        return VariableSpec(name=name, kind=VariableKind.NUMERIC)
    uniq = np.unique(observed)
    if uniq.size <= 2 and np.all(np.isin(uniq, [0.0, 1.0])):
        return VariableSpec(name=name, kind=VariableKind.BINARY, levels=(0.0, 1.0))
    return VariableSpec(name=name, kind=VariableKind.NUMERIC)
