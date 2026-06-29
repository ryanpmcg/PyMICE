"""Tabular wrapper for MICE inputs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pymice.data_form import as_data_matrix
from pymice.types import VariableSpec


@dataclass
class ImputationFrame:
    """Numeric matrix plus column metadata for ``mice()``."""

    data: NDArray[np.float64]
    column_names: list[str]
    variable_specs: list[VariableSpec]

    @classmethod
    def from_array(
        cls,
        data: NDArray[np.float64],
        *,
        column_names: list[str] | None = None,
        variable_specs: list[VariableSpec] | None = None,
    ) -> ImputationFrame:
        matrix, names, specs = as_data_matrix(
            data,
            column_names=column_names,
            variable_specs=variable_specs,
        )
        return cls(data=matrix, column_names=names, variable_specs=specs)

    @classmethod
    def from_pandas(cls, df) -> ImputationFrame:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for ImputationFrame.from_pandas") from exc
        if not isinstance(df, pd.DataFrame):
            raise TypeError("expected pandas DataFrame")
        names = list(df.columns.astype(str))
        matrix = df.to_numpy(dtype=np.float64, copy=True)
        matrix[df.isna().to_numpy()] = np.nan
        _, _, specs = as_data_matrix(matrix, column_names=names)
        return cls(data=matrix, column_names=names, variable_specs=specs)

    def to_numpy(self) -> NDArray[np.float64]:
        return self.data
