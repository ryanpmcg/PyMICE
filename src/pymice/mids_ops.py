"""``Mids`` object utilities with R-familiar names."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.types import Mids, filter_imputations


def filter_mids(
    mids: Mids,
    imputations: int | list[int] | range | NDArray[np.int_],
) -> Mids:
    """
    Subset imputations from a ``Mids`` object (R ``filter()`` on mids).

    Indices are **1-based** like R: ``filter_mids(imp, [1, 3, 5])`` keeps
    imputations 1, 3, and 5. For 0-based Python indexing use
    ``filter_imputations()``.
    """
    if isinstance(imputations, (int, np.integer)):
        idx = [int(imputations)]
    else:
        idx = [int(i) for i in imputations]

    if not idx:
        raise ValueError("imputations must contain at least one index")

    if min(idx) < 1 or max(idx) > mids.m:
        raise IndexError(
            f"imputation indices must be between 1 and {mids.m} (R-style 1-based); got {idx}"
        )

    return filter_imputations(mids, [i - 1 for i in idx])
