"""Normalize tabular inputs (DataFrame or ndarray) for PyMICE APIs."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pymice.data_form import as_data_matrix
from pymice.imputation_frame import ImputationFrame
from pymice.types import VariableSpec


def is_pandas_dataframe(obj: Any) -> bool:
    try:
        import pandas as pd
    except ImportError:
        return False
    return isinstance(obj, pd.DataFrame)


def is_pandas_series(obj: Any) -> bool:
    try:
        import pandas as pd
    except ImportError:
        return False
    return isinstance(obj, pd.Series)


def prepare_mice_input(
    data: Any,
    *,
    column_names: list[str] | None = None,
    variable_specs: list[VariableSpec] | dict[str, VariableSpec] | None = None,
) -> tuple[NDArray[np.float64], list[str], list[VariableSpec]]:
    """Return matrix, names, and specs for ``mice()`` (DataFrame-aware)."""
    if is_pandas_dataframe(data):
        if column_names is not None:
            raise ValueError("column_names cannot be used when data is a pandas DataFrame")
        if variable_specs is not None:
            raise ValueError("variable_specs cannot be used when data is a pandas DataFrame")
        frame = ImputationFrame.from_pandas(data)
        return frame.data, frame.column_names, frame.variable_specs
    return as_data_matrix(data, column_names=column_names, variable_specs=variable_specs)


def prepare_tabular_input(
    data: Any,
    column_names: list[str] | None = None,
) -> tuple[NDArray[np.float64], list[str]]:
    """Return matrix and names for analysis/diagnostic functions."""
    if is_pandas_dataframe(data):
        if column_names is not None:
            raise ValueError("column_names cannot be used when data is a pandas DataFrame")
        frame = ImputationFrame.from_pandas(data)
        return frame.data, frame.column_names
    matrix, names, _specs = as_data_matrix(data, column_names=column_names)
    return matrix, names
