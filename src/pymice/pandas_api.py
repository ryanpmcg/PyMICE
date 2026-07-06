"""Pandas-facing API (legacy entry point)."""

from __future__ import annotations

import warnings
from typing import Any

from pymice.engine import mice
from pymice.types import Mids


def mice_df(df, **kwargs: Any) -> Mids:
    """Run ``mice()`` on a pandas DataFrame."""
    warnings.warn(
        "mice_df() is deprecated; use mice(df, ...) instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return mice(df, **kwargs)
