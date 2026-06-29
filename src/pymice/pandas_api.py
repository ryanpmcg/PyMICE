"""Pandas-facing API."""

from __future__ import annotations

from typing import Any

from pymice.engine import mice
from pymice.imputation_frame import ImputationFrame
from pymice.types import Mids


def mice_df(df, **kwargs: Any) -> Mids:
    """Run ``mice()`` on a pandas DataFrame."""
    frame = ImputationFrame.from_pandas(df)
    return mice(
        frame.data,
        column_names=frame.column_names,
        variable_specs=frame.variable_specs,
        **kwargs,
    )
