"""Extract completed datasets from a ``Mids`` object."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from pymice.types import Mids

Action = int | Literal["all", "long", "broad", "repeated", "stacked"]


def complete(
    mids: Mids,
    action: Action = 1,
    include: bool = False,
    *,
    draw: int | None = None,
) -> NDArray[np.float64] | list[NDArray[np.float64]] | dict[str, NDArray[np.float64]]:
    """
    Fill in missing values from imputations and return completed data.

    Draw indices are **0-based**: ``0`` = original incomplete data,
    ``1..m`` = imputation draws (R-compatible numbering).
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
        stacks = [_single_complete(mids, i) for i in indices]
        return np.vstack(stacks)

    if action in ("broad", "repeated"):
        indices = list(range(1, mids.m + 1))
        if include:
            indices = [0, *indices]
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
