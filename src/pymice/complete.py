"""Extract completed datasets from a ``Mids`` object."""

from __future__ import annotations

from typing import Any, Literal, overload

import numpy as np
from numpy.typing import NDArray

from pymice.types import Mids

Action = int | Literal["all", "long", "broad", "repeated", "stacked"]


@overload
def complete(
    mids: Mids,
    action: int = 1,
    include: bool = False,
    *,
    draw: int | None = None,
    as_dataframe: bool = False,
) -> NDArray[np.float64]: ...


@overload
def complete(
    mids: Mids,
    action: Literal["all"],
    include: bool = False,
    *,
    draw: int | None = None,
    as_dataframe: bool = False,
) -> dict[str, NDArray[np.float64]]: ...


@overload
def complete(
    mids: Mids,
    action: Literal["long", "stacked", "broad", "repeated"],
    include: bool = False,
    *,
    draw: int | None = None,
    as_dataframe: Literal[True] = True,
) -> Any: ...


def complete(
    mids: Mids,
    action: Action = 1,
    include: bool = False,
    *,
    draw: int | None = None,
    as_dataframe: bool = True,
) -> NDArray[np.float64] | list[NDArray[np.float64]] | dict[str, NDArray[np.float64]] | Any:
    """
    Fill in missing values from imputations and return completed data.

    Draw indices are **0-based**: ``0`` = original incomplete data,
    ``1..m`` = imputation draws (R-compatible numbering).

    ``"long"`` / ``"stacked"`` and ``"broad"`` / ``"repeated"`` return a
    pandas ``DataFrame`` by default (R ``complete(imp, "long")`` layout with
    ``.imp`` / ``.id`` or ``var.N`` columns). Pass ``as_dataframe=False`` for
    the legacy ndarray layout.
    """
    if draw is not None:
        action = draw
    if isinstance(action, int):
        if action < 0 or action > mids.m:
            raise ValueError(f"action must be between 0 and {mids.m}")
        idx = [action]
        if include and action != 0:
            idx = [0, action]
        return _single_complete(mids, idx[0] if len(idx) == 1 else idx)

    if action == "all":
        indices = list(range(0 if include else 1, mids.m + 1))
        return {str(i): _single_complete(mids, i) for i in indices}

    if action in ("long", "stacked"):
        indices = list(range(1, mids.m + 1))
        if include:
            indices = [0, *indices]
        if as_dataframe:
            return _complete_long_dataframe(mids, indices)
        stacks = [_single_complete(mids, i) for i in indices]
        return np.vstack(stacks)

    if action in ("broad", "repeated"):
        indices = list(range(1, mids.m + 1))
        if include:
            indices = [0, *indices]
        if as_dataframe:
            return _complete_broad_dataframe(mids, indices)
        parts = [_single_complete(mids, i) for i in indices]
        return np.hstack(parts)

    raise ValueError(f"Unrecognized action: {action!r}")


def _single_complete(mids: Mids, draw: int) -> NDArray[np.float64]:
    if draw == 0:
        return mids.data.copy()

    if draw < 1 or draw > mids.m:
        raise ValueError(f"draw must be between 0 and {mids.m}")

    out = mids.data.copy()
    col_idx = 0
    for name in mids.column_names:
        if name not in mids.imp:
            col_idx += 1
            continue
        wy = mids.where[:, col_idx]
        missing = np.isnan(mids.data[:, col_idx])
        mask = wy & missing
        if np.any(mask):
            out[mask, col_idx] = mids.imp[name][mask[wy], draw - 1]
        # Cells outside ``where`` remain NA even if imputations exist.
        out[~wy & missing, col_idx] = np.nan
        col_idx += 1
    return out


def _require_pandas():
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for complete(..., as_dataframe=True). "
            "Install pandas or pass as_dataframe=False."
        ) from exc
    return pd


def _complete_long_dataframe(mids: Mids, indices: list[int]) -> Any:
    """Stack imputations with R ``.imp`` and ``.id`` columns."""
    pd = _require_pandas()
    frames = []
    for imp_no in indices:
        arr = _single_complete(mids, imp_no)
        frame = pd.DataFrame(arr, columns=mids.column_names)
        frame.insert(0, ".id", np.arange(1, mids.n_obs + 1))
        frame.insert(0, ".imp", imp_no)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _complete_broad_dataframe(mids: Mids, indices: list[int]) -> Any:
    """Side-by-side imputations with R ``var.N`` column names."""
    pd = _require_pandas()
    parts = []
    for imp_no in indices:
        arr = _single_complete(mids, imp_no)
        suffix = str(imp_no)
        cols = [f"{name}.{suffix}" for name in mids.column_names]
        parts.append(pd.DataFrame(arr, columns=cols))
    return pd.concat(parts, axis=1)
